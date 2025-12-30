import asyncio
import json
import shlex
import tiktoken
# import re  # Added for rewind parsing
from argparse import ArgumentParser
from enum import Enum
from typing import Any, List, Literal, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from langsmith import RunTree, traceable
from langsmith.run_helpers import get_current_run_tree
from pydantic import BaseModel, Field

# from utils.tool_summarizer import ToolCallSummarizer
from plan_orchestrator import Plan, PlanOrchestrator, TaskOutcome
from prompts import (
    SYSTEM_CODEACT_PLAN_PROMPT,
    SYSTEM_CODEACT_PROMPT,
    SYSTEM_REACT_PROMPT,
    SYSTEM_ROUTER_PROMPT,
)
from runtime import DockerRuntime
from task_retry_manager import RetryManager
from tools import Cmd, DeepResearch, Python, file_write, web_search
from langchain_core.tools import tool
from tools.mcp import create_service_tools
from tools.ToolRegistry import ToolRegistry
from langchain.tools import BaseTool
from tools.ToolRegistry import get_tools as get_tools_selector
from utils.log import LoggerStream, logger
from openai import OpenAI #for compact tool

import json
from typing import List

from openai.types.responses import Response, ResponseOutputItem, ResponseOutputMessage
from openai.types.responses.response_function_call_output_item_list_param import (
    ResponseFunctionCallOutputItemListParam,
    ResponseFunctionCallOutputItemParam,
)
from openai.types.responses.response_function_tool_call_param import (
    ResponseFunctionToolCallParam,
)
from openai.types.responses.response_input_file_param import ResponseInputFileParam
from openai.types.responses.response_input_image_param import ResponseInputImageParam
from openai.types.responses.response_input_message_content_list_param import (
    ResponseInputMessageContentListParam,
)
from openai.types.responses.response_input_param import (
    FunctionCallOutput,
    Message,
    ResponseInputParam,
)
from openai.types.responses.response_input_text_param import ResponseInputTextParam

def UserMessage(
    content: ResponseInputMessageContentListParam | ResponseInputParam | dict | str,
) -> Message:
    if isinstance(content, dict):
        # Not recommended, but supported for clearer object creation
        content = [content]  # type: ignore
    return Message(role="user", content=content)


def SystemMessage(
    content: ResponseInputMessageContentListParam | ResponseInputParam | dict | str,
) -> Message:
    if isinstance(content, dict):
        # Not recommended, but supported for clearer object creation
        content = [content]  # type: ignore
    return Message(role="system", content=content)

def prepare_container_env(
    runtime: "DockerRuntime",
    work_dir: str = "/workspace",
    mounted_packages_path: Optional[str] = None,
):
    logger.info(f"Setting up container environment in {work_dir}")
    runtime.exec(f"mkdir -p {work_dir}")

    # Copy project files
    runtime.copy_files_to_container(
        {
            ".env": "./.env",
            "requirements.txt": "./requirements.txt",
            "mcp.toml": "./mcp.toml",
        },
        work_dir,
    )
    runtime.copy_directory_to_container("./src", f"{work_dir}/src")
    runtime.copy_directory_to_container("./docker", f"{work_dir}/docker")

    container_specific_packages = [
        "pydantic",
        "pydantic_core",
        "langsmith",
        # "playwright",
    ]

    stream = LoggerStream(logger, raw_output=True)
    if mounted_packages_path:
        logger.info("Using mounted packages with container's Python")
        # Reinstall only problematic packages in container
        runtime.exec(
            f"python3 -m pip install {' '.join(container_specific_packages)}",
            workdir=work_dir,
            output_stream=stream,
        )
        # Only install system-level dependencies that might 1be missing
        # runtime.exec(
        #     f"PYTHONPATH={mounted_packages_path} python3 -m playwright install chromium --with-deps",
        #     workdir=work_dir,
        # )
    else:
        logger.info("Installing fresh dependencies")
        runtime.exec("python3 -m venv .venv", workdir=work_dir, output_stream=stream)
        python_cmd = ".venv/bin/python"
        # Install all requirements
        runtime.exec(
            f"{python_cmd} -m pip install -r requirements.txt",
            workdir=work_dir,
            output_stream=stream,
        )
        # runtime.exec(
        #     f"{python_cmd} -m playwright install chromium --with-deps",
        #     workdir=work_dir,
        #     output_stream=stream,
        # )

    logger.info("Container environment ready")
    stream.close()


def run_agent_in_container(
    runtime: "DockerRuntime",
    prompt: str,
    work_dir: str = "/workspace",
    mounted_packages_path: Optional[str] = None,  # Path to packages directory
) -> str:
    """Run agent in container.

    Args:
        runtime: DockerRuntime object, to run agent in.
        prompt: Literally the task for the agent.
        work_dir: Working directory (from which agent will be launched).
        mounted_packages_path: Path to mounted Python packages directory
                              (e.g., "/workspace/host-packages")
    """
    prepare_container_env(runtime, work_dir, mounted_packages_path)

    if mounted_packages_path:
        pythonpath = f"{mounted_packages_path}:./src:./"
        logger.info(f"Using mounted packages from: {mounted_packages_path}")
        command = f"PYTHONPATH={pythonpath} python3 src/main.py --prompt {shlex.quote(prompt)}"
    else:
        pythonpath = "./src:./"
        command = f"PYTHONPATH={pythonpath} .venv/bin/python src/main.py --prompt {shlex.quote(prompt)}"

    stream = LoggerStream(logger, raw_output=True)
    runtime.exec(command, workdir=work_dir, output_stream=stream)
    stream.close()


class TaskCategory(Enum):
    SIMPLE_QUESTION = "simple_question"
    SIMPLE_ACTION = "simple_action"
    SEQUENCE_OF_ACTIONS = "sequence_of_actions"
    COMPLICATED = "complicated"
    COMPLEX = "complex"
    CHAOTIC = "chaotic"


class TaskClassification(BaseModel):
    reasoning: str = Field(description="Reasoning for task category selection")
    category: TaskCategory = Field(description="Selected task category")


class TaskProcessor:
    MAX_STEPS = 1000
    TOKEN_THRESHOLD = 64000  # Global token usage threshold for reminders (was 25000)
    TOKEN_LIMIT_PER_TOOL = 100000  # Truncation limit remains
    REMINDER_INTERVAL = 10  # Remind every 10 steps if threshold is still exceeded
    REMINDER_TOKEN_STEP = 32000
    SERVICES = ["plane", "rocketchat", "owncloud", "gitlab"]
    # SERVICES = []
    CLIENTS = []

    def __init__(self):
        load_dotenv()
        self.registry = self._setup_tools()
        self.retry_manager = RetryManager(log_dir="./retry_logs")
        self.response_checkpoints = []
        self.last_responses = []
        self.total_tokens_used = 0
        self.current_total_tokens_used = 0
        self.encoding = tiktoken.get_encoding("cl100k_base")  # For gpt-4 and others
        self._oai = OpenAI()
        self.compact_sensory_summary = ""
    
    def create_compact_tool(self):

        @tool
        def compact(sensory_summary: str = ""): 
            """
            Perform a compaction pass over the conversation history.
            Passing a `sensory_summary` provides a short summary or message that will be preserved verbatim after compaction.

            This tool must not be called as the first tool invocation and must not
            be invoked consecutively. It compacts the existing conversation context
            and prepares it for continued interaction.

            Use this tool for these reasons:

            *   You have completed several tasks or a major sub-goal.
            *   The complete details of that work done are no longer needed for the *next* phase of the task.

            Note: This tool cannot be invoked from within Python tool execution
            
            Passing a sensory_summary is a short summary/message you want to keep verbatim after compaction.
            This have to be a summary of discoveries, insights, that will allow you to resume work efficiently in a future context window. Be thorough and actionable.
            Mention: 
            ### What has been successfully accomplished at the moment.
            Be specific. Summary should include exact information inside it: 
            - Actions Taken: Files modified, commands run, APIs called.
            - Concrete Data Discovered: What exact file paths, URLs, configuration details, or other key data was found.

            ### Next Steps After Compaction
            - **Immediate Actions:** List the specific, concrete actions needed to complete the task.

            Args:
                str: The summary or message to preserve verbatim after compaction.

            Returns:
                str: A status message indicating that the compaction was triggered.
            """

            self.compact_sensory_summary = sensory_summary

            return f"Compaction initiated successfully. Check next assistant message about result of compaction. After compaction, continue your actions in order to complete the task."

        return compact

    def create_toolbox_tool(self):
    
        @tool
        def toolbox_tool(query: str): 
            """
            Tool for reselecting tools from the toolbox based on the query.
            
            Args:
                query (str): A text query that may contain tool names, tool descriptions, or names of services for which the tools are needed.

            Returns:
                str: Comma-separated list of selected tool names.
            """
            self.registry = self._setup_tools()

            get_tools_selector(query, self.registry, mutate_registry=True)

            self.registry.register_many(
                [Cmd(), file_write, DeepResearch(), web_search], namespace="general"
            )

            toolbox_tool = self.create_toolbox_tool()
            self.registry.register(toolbox_tool, namespace="control")

            compact_tool = self.create_compact_tool()
            self.registry.register(compact_tool, namespace="control")

            python_tool = Python()
            for tool in self.registry:

                def make_proxy(t):
                    def proxy(*args, **kwargs):
                        if kwargs and args:
                            raise ValueError("Pass either args or kwargs, not both")
                        if kwargs:
                            return t.invoke(
                                kwargs
                            )
                        elif args:
                            if len(args) == 1:
                                return t.invoke(args[0])  # Single string arg
                            return t.invoke(args)  # multiple positional args → tuple
                        else:
                            return t.invoke("")

                    return proxy

                python_tool.globals_dict[tool.name] = make_proxy(tool)
            self.registry.register(python_tool, namespace="general")

            toolname_list = ""
            keys = list(self.registry._tools.keys())

            for i, toolname in enumerate(keys):
                if i == len(keys) - 1:
                    toolname_list += toolname
                else:
                    toolname_list += toolname + ", "

            return toolname_list

        return toolbox_tool

    def _setup_tools(self) -> ToolRegistry:
        """Initialize and register all tools."""
        registry = ToolRegistry()

        # Register MCP service tools
        for service in self.SERVICES:
            try:
                tools, client = create_service_tools(service)
                registry.register_many(tools, namespace=service)
                self.CLIENTS.append(client)
                logger.info(f"Registered {len(tools)} tools for service: {service}")
            except Exception as e:
                logger.error(f"Warning: Failed to register {service} tools: {e}")

        logger.info(f"Successfully registered {len(registry)} tools")
        return registry

    def _count_tokens(self, messages: List[Any]) -> int:
        """Counts the number of tokens in a list of messages."""
        token_count = 0
        for message in messages:
            if isinstance(message, tuple):
                content = message[1]
            elif hasattr(message, 'content'):
                content = message.content
            else:
                content = str(message)

            if isinstance(content, list):  # Handle list of content blocks
                for block in content:
                    if isinstance(block, dict) and 'text' in block:
                        token_count += len(self.encoding.encode(block['text']))
            elif isinstance(content, str):
                token_count += len(self.encoding.encode(content))
        return token_count

    @traceable(name="react_ask")
    def handle_react_ask(self, user_input: str, retry_context: str = "") -> str:
        """Handle tasks requiring ReAct pattern with tools."""
        logger.info("Starting REACT stage...")

        #TODO
        # llm = ChatOpenAI(
        #     model="gpt-5.2", 
        #     output_version="responses/v1", 
        #     reasoning={"effort": "xhigh",
        #                "summary": "auto"}
        # ).bind_tools(self.registry.get_tools())

        base_prompt = SYSTEM_REACT_PROMPT.format(
            tools=self.registry.get_def_manifest(),
        )
        prompt = base_prompt + retry_context if retry_context else base_prompt

        #TODO
        #messages = [("system", prompt), ("human", user_input)]
        messages = [
            SystemMessage(prompt),
            UserMessage(user_input),
        ]
        previous_response_id = None

        self.response_checkpoints = []
        self.last_responses = []
        final_output = "No output provided."
        self.total_tokens_used = 0
        self.current_total_tokens_used = 0
        last_reminder_step = -1
        last_reminder_token_count = -1

        reasoning_summaries = []
        execution_errors = []
        toolcall_step = 0
        for step in range(self.MAX_STEPS):
            try:
                if step == self.MAX_STEPS - 1:
                    #TODO
                    messages.append(
                        (
                            "system",
                            "You've reached the maximum number of steps. Please, provide your final answer instead of calling any more tools.",
                        )
                    )

                if self.current_total_tokens_used > self.TOKEN_THRESHOLD and (
                    last_reminder_token_count == -1 or self.current_total_tokens_used >= last_reminder_token_count + self.REMINDER_TOKEN_STEP
                ):
                    #TODO
                    reminder_message = (
                        "user",
                        """[SYSTEM NOTIFICATION]: The conversation history is growing long. To optimize performance and consolidate your progress, recall what does compact tool do and consider using the compact now. You MUST output the explanation of your decision now!"""
                    )
                    logger.info(f"added reminder to compact")
                    messages.append(reminder_message)
                    if last_reminder_token_count == -1:
                        last_reminder_token_count = self.TOKEN_THRESHOLD
                    else:
                        last_reminder_token_count += self.REMINDER_TOKEN_STEP

                logger.info(f"<step_{step + 1}>")

                input_tokens = self._count_tokens(messages)
                self.total_tokens_used += input_tokens
                logger.info(f"Tokens used so far: {self.total_tokens_used} (+{input_tokens} input)")
                
                if self.response_checkpoints == []:
                    previous_response_id = None
                else:
                    previous_response_id = self.response_checkpoints[-1]
                
                #TODO
                response = client.responses.create(
                    input=messages,
                    model="gpt-5.2",
                    reasoning={
                        "effort": "xhigh"
                    },
                    tools=tools if tools else [],
                    previous_response_id=response_id,
                )
                # response = llm.invoke(
                #     messages, previous_response_id=previous_response_id
                # )

                #TODO
                self.current_total_tokens_used = response.usage_metadata["input_tokens"]
                logger.info(f"Current tokens used so far (compaction decreased): {self.current_total_tokens_used}")

                print(f"Resp{step}: ", response)
                print(f"Resp{step} Input:", response.usage_metadata["input_tokens"])
                print(f"Resp{step} Output:", response.usage_metadata["output_tokens"])

                output_tokens = self._count_tokens([response])
                self.total_tokens_used += output_tokens
                self.current_total_tokens_used += output_tokens
                logger.info(f"Tokens used so far: {self.total_tokens_used} (+{output_tokens} output)")
                logger.info(f"Current tokens used so far (compaction decreased): {self.current_total_tokens_used} (+{output_tokens} input)")

                #TODO
                self.response_checkpoints.append(response.response_metadata["id"])
                self.last_responses.append(response)
                content = response.content

                messages = []
                for c in content:
                    if type(c) != dict:
                        continue
                    if c.get("type") == "reasoning":
                        summary = c.get("summary", [])
                        if summary:
                            summary_text = "\n".join(s.get("text", "") for s in summary)
                            reasoning_summaries.append(summary_text)
                            logger.info(
                                f"<reasoning_summary>\n{summary_text}\n</reasoning_summary>"
                            )
                    if c.get("type") == "text":
                        final_output = c.get("text")
                        logger.info(f"<llm_output>\n{c.get('text')}\n</llm_output>")
                    if c.get("type") in ["function_call", "custom_tool_call"]:
                        tool_name = c.get("name")
                        tool_input = c.get("arguments") or c.get("input")
                        tool_call_id = c.get("call_id")
                        logger.info(
                            f'<tool_call call_id="{tool_call_id}" tool_name="{tool_name}">\n{tool_input}\n</tool_call>'
                        )
                        result = self._execute_tool(
                            tool_name,
                            tool_input,
                            tool_call_id,
                            c.get("type"),
                            toolcall_step,
                        )

                        # Check for large single tool call output
                        result_content = result.content if hasattr(result, 'content') else str(result)
                        tokens = self.encoding.encode(result_content)

                        logger.info(
                            f'<tool_response call_id="{tool_call_id}" tool_name="{tool_name}">\n{result.content}\n</tool_response>'
                        )
                        print(f"\nToolMessage after Resp{step}:", result)
                        messages.append(result)

                        if tool_name == "compact":
                            try:
                                messages = []
                                client = self._oai
                                
                                seen_tool_call_ids = set()

                                def response_to_input_items(response):
                                    """
                                    Turn response.output into input format for responses.create
                                    """
                                    items = []
                                    if isinstance(response, AIMessage):
                                        items.append({
                                            "type": "message",
                                            "role": "assistant",
                                            "content": [{
                                                "type": "output_text",
                                                "text": resp.content
                                            }]
                                        })

                                        for tc in response.tool_calls or []:
                                            seen_tool_call_ids.add(tc["id"])
                                            items.append({
                                                "type": "function_call",
                                                "name": tc["name"],
                                                "call_id": tc["id"],
                                                "arguments": tc["args"]
                                            })

                                    if isinstance(response, ToolMessage):
                                        if response.tool_call_id in seen_tool_call_ids:
                                            items.append({
                                                "type": "function_call_output",
                                                "call_id": response.tool_call_id,
                                                "output": response.content
                                            })
                                    
                                    if hasattr(response, "output"):
                                        for item in response.output:
                                            if item.type == "message":
                                                items.append({
                                                    "type": "message",
                                                    "role": item.role,
                                                    "content": [
                                                        {
                                                            "type": "output_text",
                                                            "text": block.text
                                                        }
                                                        for block in item.content
                                                        if block.type == "output_text"
                                                    ]
                                                })
                                    return items

                                response = client.responses.create(
                                    model="gpt-5.2",
                                    input=[{
                                        "type": "function_call_output",
                                        "call_id": tool_call_id,
                                        "output": result.content
                                    }],
                                    previous_response_id=self.response_checkpoints[-1]
                                )

                                self.response_checkpoints.append(response.id)
                                self.last_responses.append(response)

                                compacted = client.responses.compact(
                                    model="gpt-5.2",
                                    previous_response_id=self.response_checkpoints[-1]
                                )
                                print("Compacted: ", compacted.output)
                                print("Compacted Input:", compacted.usage.input_tokens)
                                print("Compacted Output:", compacted.usage.output_tokens)

                                input_items = []
                                self.last_responses = self.last_responses[:5] ##DANGEROUS
                                input_items.extend(compacted.output)

                                for resp in self.last_responses:
                                    input_items.extend(response_to_input_items(resp))

                                response = client.responses.create(
                                    model="gpt-5.2",
                                    input=input_items,
                                )
                                print("Resp after compacted: ",  response.output_text)
                                print("Resp after compacted Input:", response.usage.input_tokens)
                                print("Resp after compacted Output:", response.usage.output_tokens)

                                self.current_total_tokens_used = response.usage.input_tokens + response.usage.output_tokens
                                logger.info(f"Current tokens used so far (AFTER compaction): {self.current_total_tokens_used}")

                                self.response_checkpoints = [response.id]
                            except IndexError:
                                logger.error("No response checkpoints available for compaction")
                                messages.append(("assistant", "Compaction failed. IndexError: No response checkpoints available for compaction"))
                            except Exception as e:
                                logger.exception(f"Unexpected error during compaction: {e}")
                                messages.append(("assistant", f"Compaction failed due to an unexpected error. In detail: {e}"))
                            else:
                                logger.info("Compaction completed successfully.")
                                messages.append(("user", f"Summary of discoveries, insights, that will allow you to resume work efficiently in a future context window and agent decided to keep verbatim: {self.compact_sensory_summary}"))
                                messages.append(("assistant", "Compaction completed successfully. Continue your actions in order to complete the task"))

                if not messages: #and not rewind_occurred:
                    # self._store_execution_context(
                    #     user_input,
                    #     reasoning_summaries,
                    #     final_output,
                    #     execution_errors,
                    #     success=True,
                    # )
                    return final_output

                toolcall_step += 1
                # if rewind_occurred:
                #     rewind_occurred = False
            except Exception as e:
                error_msg = f"REACT error in step {step + 1}: {str(e)}"
                execution_errors.append(error_msg)
                logger.exception(error_msg)
                break
            finally:
                logger.info(f"</step_{step + 1}>")
        logger.warning(
            f"Forced exit from REACT due to recursion limits ({self.MAX_STEPS} steps)"
        )

        if not execution_errors:
            execution_errors.append("Reached maximum steps limit")

        # self._store_execution_context(
        #     user_input,
        #     reasoning_summaries,
        #     final_output,
        #     execution_errors,
        #     success=False,
        # )
        return (
            final_output
            if final_output != "No output provided."
            else "Task failed to complete within step limit."
        )

    def _execute_tool(
        self,
        name: str,
        arguments: str | dict,
        call_id: Optional[Any] = None,
        call_type: Literal["function_call", "custom_tool_call"] = "function_call",
        step_index: int = 0,
    ) -> str | ToolMessage:
        try:
            if call_type == "function_call":
                if type(arguments) == str:
                    arguments = json.loads(arguments)
                result = self.registry.invoke_tool(name, arguments)
            if call_type == "custom_tool_call":
                result = self.registry.invoke_tool(name, arguments)
                if isinstance(result, list):
                    result = result[0].get("output", str(result))
        except Exception as ex:
            result = str(ex)

        result_str = str(result)

        tokens = self.encoding.encode(result_str)
        original_token_count = len(tokens)
        was_truncated = False

        if len(tokens) > self.TOKEN_LIMIT_PER_TOOL:
            result_str = self.encoding.decode(tokens[:self.TOKEN_LIMIT_PER_TOOL])
            result_str += "\n[... tool output truncated ...]"
            was_truncated = True

        marked_result = f"[Tool call from step {step_index + 1}]\n" + result_str

        if call_id:
            return ToolMessage(marked_result, tool_call_id=call_id)
        return marked_result

    @traceable(name="agent")
    def process_task(self, user_input: str) -> Optional[RunTree]:
        """Main method to process user input."""
        run = get_current_run_tree()
        if not user_input.strip():
            logger.error("Please provide a valid input!")
            return run

        get_tools_selector(user_input, self.registry, mutate_registry=True)
        self.registry.register_many(
            [Cmd(), file_write, DeepResearch(), web_search], namespace="general"
        )
        self.registry.unregister("python", ignore_missing=True)

        toolbox_tool = self.create_toolbox_tool()
        self.registry.register(toolbox_tool, namespace="control")

        compact_tool = self.create_compact_tool()
        self.registry.register(compact_tool, namespace="control")
        
        python_tool = Python()
        for tool in self.registry:

            def make_proxy(t):
                def proxy(*args, **kwargs):
                    if kwargs and args:
                        raise ValueError("Pass either args or kwargs, not both")
                    if kwargs:
                        return t.invoke(
                            kwargs
                        )
                    elif args:
                        if len(args) == 1:
                            return t.invoke(args[0])  # Single string arg
                        return t.invoke(args)  # multiple positional args → tuple
                    else:
                        return t.invoke("")

                return proxy

            python_tool.globals_dict[tool.name] = make_proxy(tool)
        self.registry.register(python_tool, namespace="general")

        toolnames = [tool.name for tool in self.registry]
        logger.info(
            f"Selected {len(self.registry)} tools for current task: {', '.join(toolnames)}"
        )

        answer = self.handle_react_ask(user_input)
        logger.info(f"<final_response>\n{answer}\n</final_response>")

        for client in self.CLIENTS:
            client.close()
        return run


def main(prompt: str):
    """Main entry point."""
    try:
        processor = TaskProcessor()
        run = processor.process_task(prompt)
        if run is not None:
            from utils.process_metrics import process_langsmith_run

            asyncio.run(process_langsmith_run(run))
    except KeyboardInterrupt:
        logger.info("\nExiting...")
    except Exception as e:
        logger.exception(f"Unexpected error: {e}")


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("--prompt", help="Initial prompt for the agent.", required=True)
    parser.add_argument(
        "--no-out-models",
        action="store_false",
        dest="out_models",
        help="Disable output models (enabled by default).",
    )

    args = parser.parse_args()

    if args.out_models:
        from utils.models_out import output_models

        output_models()

    main(args.prompt)
