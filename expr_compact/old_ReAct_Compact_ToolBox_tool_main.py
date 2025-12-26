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
#from tools.rewind.parser import parse_rewind_string
from openai import OpenAI #for compact tool


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
    #TOKEN_THRESHOLD = 30000  # Global token usage threshold for reminders (was 25000)
    TOKEN_LIMIT_PER_TOOL = 100000  # Truncation limit remains
    #SINGLE_TOOL_REWIND_THRESHOLD = 10000  # Auto-rewind if single tool output exceeds this
    #REMINDER_INTERVAL = 10  # Remind every 10 steps if threshold is still exceeded
    SERVICES = ["plane", "rocketchat", "owncloud", "gitlab"]
    # SERVICES = []
    CLIENTS = []

    def __init__(self):
        load_dotenv()
        self.registry = self._setup_tools()
        self.retry_manager = RetryManager(log_dir="./retry_logs")
        self.response_checkpoints = [] # for rewind (not for compact)
        self.tool_call_history = []  # Store all tool calls for rewind summarization
        self.total_tokens_used = 0
        self.encoding = tiktoken.get_encoding("cl100k_base")  # For gpt-4 and others
        self._oai = OpenAI()
        self.last_responses = [] # Save last 10 Responses for compact tool
    
    def create_compact_tool(self):

        @tool
        def compact(): 
            """
            Perform a compaction pass over the conversation history.

            This tool must not be called as the first tool invocation and must not
            be invoked consecutively. It compacts the existing conversation context
            and prepares it for continued interaction.

            Returns:
                str: A status message indicating that the compaction was triggered.
            """

            return "Check next assistant message about result of compaction."

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

            #compact HERE
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

    # @traceable(name="router")
    # def classify_task(self, user_input: str) -> TaskCategory:
    #     """Classify the task category."""
    #     try:
    #         logger.info("Starting ROUTER stage...")
    #         llm = ChatOpenAI(model="gpt-5", temperature=0).with_structured_output(
    #             TaskClassification
    #         )
    #         system_prompt = SYSTEM_ROUTER_PROMPT.format(
    #             tools=self.registry.get_def_manifest()
    #         )
    #         response: TaskClassification = llm.invoke(
    #             [
    #                 ("system", system_prompt),
    #                 ("human", user_input),
    #             ]
    #         )
    #         logger.info(f"Task classified as: {response.category.value}")
    #         return response.category
    #     except Exception as e:
    #         logger.exception(f"Classification failed: {e}. Moving to SIMPLE_ACTION")
    #         return TaskCategory.SIMPLE_ACTION

    # @traceable(name="simple_question")
    # def handle_simple_question(self, user_input: str) -> str:
    #     """Handle simple questions with direct LLM response."""
    #     try:
    #         logger.info("Starting SIMPLE_QUESTION stage...")
    #         llm = ChatGoogleGenerativeAI(model="gemini-2.5-pro")
    #         response = llm.invoke(
    #             [
    #                 ("system", "You are a helpful assistant answering user questions."),
    #                 ("human", user_input),
    #             ]
    #         )
    #         logger.info("SIMPLE_QUESTION stage completed")
    #         return str(response.content)
    #     except Exception as e:
    #         return f"Error processing question: {e}"

    @traceable(name="react_ask")
    def handle_react_ask(self, user_input: str, retry_context: str = "") -> str:
        """Handle tasks requiring ReAct pattern with tools."""
        logger.info("Starting REACT stage...")

        #TODO
        llm = ChatOpenAI(
            model="gpt-5.2", 
            output_version="responses/v1", 
            reasoning={"effort": "xhigh",
                       "summary": "auto"}
        ).bind_tools(self.registry.get_tools())

        base_prompt = SYSTEM_REACT_PROMPT.format(
            tools=self.registry.get_def_manifest(),
        )
        prompt = base_prompt + retry_context if retry_context else base_prompt

        #TODO
        messages = [("system", prompt), ("human", user_input)]
        previous_response_id = None

        self.response_checkpoints = []
        self.last_responses = []
        final_output = "No output provided."
        self.total_tokens_used = 0
        #last_reminder_step = -1
        #flag = False

        reasoning_summaries = []
        execution_errors = []
        #rewind_occurred = False
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

                logger.info(f"<step_{step + 1}>")

                input_tokens = self._count_tokens(messages)
                self.total_tokens_used += input_tokens
                logger.info(f"Tokens used so far: {self.total_tokens_used} (+{input_tokens} input)")
                
                #TODO
                response = llm.invoke(
                    messages, previous_response_id=previous_response_id
                )

                print(f"Resp{step}: ", response)
                print(f"Resp{step} Input:", response.usage_metadata["input_tokens"])
                print(f"Resp{step} Output:", response.usage_metadata["output_tokens"])

                output_tokens = self._count_tokens([response])
                self.total_tokens_used += output_tokens
                logger.info(f"Tokens used so far: {self.total_tokens_used} (+{output_tokens} output)")

                previous_response_id = response.response_metadata["id"]
                # self.response_checkpoints.append(previous_response_id)

                self.last_responses.append(response)
                self.last_responses = self.last_responses[:10]

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
                        # result_content = result.content if hasattr(result, 'content') else str(result)
                        # tokens = self.encoding.encode(result_content)
                        # if len(tokens) > self.SINGLE_TOOL_REWIND_THRESHOLD and tool_name != "rewind":
                        #     flag = True

                        # if tool_name == "rewind":
                        #     flag = False
                        #     parsed = parse_rewind_string(result.content)
                        #     if parsed:
                        #         target_step = parsed["target_step"]
                        #         summary = parsed["summary"]
                        #         sensory_summary = parsed["sensory_summary"]
                        #         try:
                        #             if (1 <= target_step <= len(self.response_checkpoints)):
                        #                 previous_response_id = self.response_checkpoints[target_step - 1]
                        #                 self.response_checkpoints = self.response_checkpoints[:target_step]
                        #                 toolcall_step = target_step - 1

                        #                 logger.info(f"Rewound to step {target_step}. Summary length: {len(summary)} chars. Sensory length: {len(sensory_summary)}")
                        #                 self.total_tokens_used = 0
                        #                 last_reminder_step = -1
                        #                 logger.info("Token count and reminder schedule reset after rewind.")

                        #                 rewind_occurred = True

                        #                 tool_calls_from_target_step = [
                        #                     call
                        #                     for call in self.tool_call_history
                        #                     if call["step"] == target_step
                        #                     and call["call_id"]
                        #                 ]

                        #                 self.tool_call_history = [
                        #                     call
                        #                     for call in self.tool_call_history
                        #                     if call["step"] < target_step
                        #                 ]

                        #                 logger.info(
                        #                     f"REWIND: Found {len(tool_calls_from_target_step)} tool calls from target step {target_step}"
                        #                 )

                        #                 messages = []
                        #                 for call in tool_calls_from_target_step:
                        #                     call_id = call["call_id"]
                        #                     content = call["output"]

                        #                     messages.append(
                        #                         ToolMessage(
                        #                             content=content,
                        #                             tool_call_id=call_id,
                        #                         )
                        #                     )
                        #                     tool_call_entry = {
                        #                         "step": target_step,
                        #                         "tool_name": call["tool_name"],
                        #                         "arguments": call["arguments"],
                        #                         "output": content,
                        #                         "call_id": call_id,
                        #                     }
                        #                     self.tool_call_history.append(
                        #                         tool_call_entry
                        #                     )

                        #                     logger.info(
                        #                         f"REWIND: Generated ToolMessage for call_id {call_id} with {len(content)} chars"
                        #                     )

                        #                 rewind_explanation = f"""[SYSTEM NOTIFICATION] During further actions, you have executed a rewind from step {step} back to step {target_step}.
                        #                 Your execution history has been streamlined - the detailed conversation between these steps has been replaced with the consolidated summary below. All actual work remains intact (files, data, tool results).

                        #                 CONSOLIDATED SUMMARY:
                        #                 <summary>
                        #                 {summary}
                        #                 </summary>
                        #                 Here is the sensory summary:
                        #                 <sensory_summary>
                        #                 {sensory_summary}
                        #                 </sensory_summary>                 
                                    
    
                        #                 OPERATIONAL STATUS:
                        #                 • Continue from this checkpoint using the summary as your authoritative memory
                        #                 • No need to re-execute completed work - everything is already done
                        #                 • Proceed with the next action based on this summary."""
                        #                 messages.append(("user", rewind_explanation))

                        #                 break
                        #             else:
                        #                 pass
                        #         except (ValueError, IndexError):
                        #             pass

                        logger.info(
                            f'<tool_response call_id="{tool_call_id}" tool_name="{tool_name}">\n{result.content}\n</tool_response>'
                        )
                        print(f"ToolMessage after Resp{step}:", result)
                        messages.append(result)

                        if tool_name == "compact":
                            try:

                                def response_to_input_items(response):
                                    """
                                    Turn response.output into input format for responses.create
                                    """
                                    items = []
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

                                client = self._oai

                                response = client.responses.create(
                                    model="gpt-5.2",
                                    input=[{
                                        "type": "function_call_output",
                                        "call_id": tool_call_id,
                                        "output": result.content
                                    }],
                                    previous_response_id=self.last_responses[-1].response_metadata["id"]
                                )

                                self.last_responses.append(response)

                                compacted = client.responses.compact(
                                    model="gpt-5.2",
                                    previous_response_id=self.last_responses[-1].id #because last one is itself compact?
                                )
                                print("Compacted: ", compacted.output)
                                print("Compacted Input:", compacted.usage.input_tokens)
                                print("Compacted Output:", compacted.usage.output_tokens)

                                # input_items = []

                                # input_items.extend(compacted.output)

                                # for resp in self.last_responses:
                                #     input_items.extend(response_to_input_items(resp))

                                response = client.responses.create(
                                    model="gpt-5.2",
                                    input=compacted.output, #input_items #YOU Already Can Add Tools To It If OpenAI SDK, So It Will Generate Tool Call, But Problem Is Assistant Message After It Makes It Only Small Sense, It Would Be Good To Add "Successful compaction" Message To Input Of This Response Somehow
                                )
                                print("Resp after compacted: ",  response.output_text)
                                print("Resp after compacted Input:", response.usage.input_tokens)
                                print("Resp after compacted Output:", response.usage.output_tokens)

                                self.last_responses = [response]
                            except IndexError:
                                logger.error("No response checkpoints available for compaction")
                                messages.append(("assistant", "Compaction failed. IndexError: No response checkpoints available for compaction"))
                            except Exception as e:
                                logger.exception(f"Unexpected error during compaction: {e}")
                                messages.append(("assistant", f"Compaction failed due to an unexpected error. In detail: {e}"))
                            else:
                                logger.info("Compaction completed successfully.")
                                messages.append(("assistant", "Compaction completed successfully."))

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

    #python react agent???
    # @traceable(name="cognitive_do")
    # def handle_cognitive_task(self, user_input: str) -> str:
    #     logger.info("Starting COGNITIVE stage...")
    #     llm = ChatOpenAI(model="gpt-5")
    #     plan_prompt = SYSTEM_CODEACT_PLAN_PROMPT.format(
    #         tools=self.registry.get_def_manifest()
    #     )
    #     plan = llm.invoke([("system", plan_prompt), ("human", user_input)]).content
    #     logger.info(f"Received plan:\n{plan}")

    #     prompt = SYSTEM_CODEACT_PROMPT.format(
    #         input=user_input,
    #         plan=plan,
    #         tools=self.registry.get_def_manifest(),
    #     )
    #     llm = ChatOpenAI(model="gpt-5", output_version="responses/v1").bind_tools(
    #         [self.registry.get_tool("python")]
    #     )
    #     messages = [("system", prompt)]
    #     previous_response_id = None

    #     for step in range(self.MAX_STEPS):
    #         logger.info(f"{'='*10} Step {step + 1} {'='*10}")
    #         try:
    #             r: AIMessage = llm.invoke(messages, previous_response_id=previous_response_id)  # type: ignore
    #             previous_response_id = r.response_metadata["id"]
    #             tool_calls = [
    #                 block
    #                 for block in r.content
    #                 if block["type"] in ["function_call", "custom_tool_call"]
    #             ]
    #             text_blocks = [
    #                 block["text"] for block in r.content if block["type"] == "text"
    #             ]
    #             if not tool_calls:
    #                 if not text_blocks:
    #                     return "No output provided."
    #                 return text_blocks[-1]

    #             messages = [
    #                 self._execute_tool(
    #                     call["name"],
    #                     call.get("arguments") or call.get("input"),
    #                     call["call_id"],
    #                     call["type"],
    #                 )
    #                 for call in tool_calls
    #             ]
    #         except Exception as e:
    #             logger.exception(f"COGNITIVE error in step {step + 1}: {e}")
    #             break

    #     logger.warning(
    #         f"Forced exit from COGNITIVE due to recursion limits ({self.MAX_STEPS} steps)"
    #     )
    #     return "No output provided."

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

        tool_call_entry = {
            "step": step_index + 1,
            "tool_name": name,
            "arguments": arguments,
            "output": marked_result,
            "call_id": call_id,
            "original_token_count": original_token_count,
            "was_truncated": was_truncated,
        }
        self.tool_call_history.append(tool_call_entry)

        if call_id:
            print("ToolMessage was created\n")
            return ToolMessage(marked_result, type="tool", tool_call_id=call_id)
        print("!!! !!! !!! ToolMessage was NOOOT created !!! !!! !!!\n")

        return marked_result

    # def _get_discarded_tool_calls(self, target_step: int) -> List[dict]:
    #     """Get tool calls from steps that will be discarded during rewind."""
    #     discarded_calls = []
    #     for call in self.tool_call_history:
    #         if call["step"] > target_step:
    #             discarded_calls.append(call)
    #     return discarded_calls

    # def _store_execution_context(
    #     self,
    #     task: str,
    #     reasoning_summaries: List[str],
    #     final_output: str,
    #     errors: List[str],
    #     success: bool,
    # ):
    #     """Store execution context in retry manager."""
    #     try:
    #         combined_summary = (
    #             " | ".join(reasoning_summaries)
    #             if reasoning_summaries
    #             else "No reasoning summary available"
    #         )
    #         self.retry_manager.add_attempt(
    #             task=task,
    #             reasoning_summary=combined_summary,
    #             final_output=final_output,
    #             success=success,
    #             errors=errors,
    #         )
    #     except Exception as e:
    #         logger.warning(f"Failed to store execution context: {e}")

    # def _format_results(self, results: List[str], plan: Plan) -> str:
    #     """Format execution results into final answer."""
    #     if len(results) == 1 and len(plan.tasks) == 1:
    #         return results[0].split(": ", 1)[1] if ": " in results[0] else results[0]
    #     else:
    #         return f"Plan execution completed for goal: {plan.goal}\n\n" + "\n\n".join(
    #             results
    #         )

    # def _handle_plan_regeneration(
    #     self,
    #     task_result: str,
    #     plan: Plan,
    #     step_index: int,
    #     results: List[str],
    #     user_input: str,
    #     orchestrator: PlanOrchestrator,
    # ):
    #     """Handle plan regeneration based on failure type."""
    #     parts = task_result.split(":", 2)
    #     failure_type = parts[1]
    #     failure_context = parts[2] if len(parts) > 2 else ""
    #     task = plan.tasks[step_index]

    #     if failure_type == TaskOutcome.FAILED_CURRENT_STEP.value:
    #         new_step = orchestrator.regenerate_step(task, failure_context, plan.goal)
    #         plan.tasks[step_index] = new_step
    #         logger.info(f"Regenerated step {step_index + 1}, retrying...")
    #         return plan, step_index, results

    #     elif failure_type == TaskOutcome.FAILED_PARTIAL_PLAN.value:
    #         new_plan = orchestrator.regenerate_plan_from_step(
    #             plan, step_index, failure_context
    #         )
    #         logger.info(f"Regenerated plan from step {step_index + 1}, continuing...")
    #         return new_plan, step_index, results

    #     elif failure_type == TaskOutcome.FAILED_FULL_PLAN.value:
    #         new_plan = orchestrator.create_plan(
    #             user_input, failed_plan_context=failure_context
    #         )
    #         logger.info("Regenerated entire plan, restarting execution...")
    #         return new_plan, 0, []

    #     return plan, step_index + 1, results

    # def _execute_plan(
    #     self, plan: Plan, user_input: str, orchestrator: PlanOrchestrator
    # ) -> str:
    #     """Execute a plan with unified logic for any number of tasks."""
    #     logger.info(f"Executing plan with {len(plan.tasks)} task(s)")
    #     results = []
    #     i = 0

    #     while i < len(plan.tasks):
    #         task = plan.tasks[i]
    #         logger.info(f"Executing task {i+1}/{len(plan.tasks)}: {task[:100]}...")
    #         task_result = self._execute_with_retry(task, orchestrator)

    #         if task_result.startswith("PLAN_REGENERATION_NEEDED:"):
    #             plan, i, results = self._handle_plan_regeneration(
    #                 task_result, plan, i, results, user_input, orchestrator
    #             )
    #             continue

    #         results.append(f"Task {i+1}: {task_result}")
    #         logger.info(f"Task {i+1} completed")
    #         i += 1

    #     return self._format_results(results, plan)

    # def _execute_with_retry(self, task: str, orchestrator: PlanOrchestrator) -> str:
    #     """Execute a task with retry logic using accumulated context."""
    #     context = self.retry_manager.get_retry_context(task)

    #     while context.should_retry:
    #         attempt_num = context.current_attempt_number
    #         logger.info(
    #             f"Attempting task execution (attempt {attempt_num}/{context.max_retries})"
    #         )

    #         retry_context = ""
    #         if context.attempts:
    #             retry_context = self.retry_manager.generate_retry_prompt_context(task)
    #             logger.info(
    #                 f"Adding retry context from {len(context.attempts)} previous attempts"
    #             )

    #         try:
    #             result = self.handle_react_ask(task, retry_context)
    #             outcome = orchestrator.analyze_task_outcome(task, result)

    #             if outcome == TaskOutcome.SUCCESS:
    #                 logger.info(f"Task succeeded on attempt {attempt_num}")
    #                 return result
    #             elif outcome == TaskOutcome.FAILED_CURRENT_STEP:
    #                 logger.warning(
    #                     f"Task failed on attempt {attempt_num}, can retry: {result[:200]}..."
    #                 )
    #                 context = self.retry_manager.get_retry_context(
    #                     task
    #                 )
    #             elif outcome in [
    #                 TaskOutcome.FAILED_PARTIAL_PLAN,
    #                 TaskOutcome.FAILED_FULL_PLAN,
    #             ]:
    #                 logger.error(
    #                     f"Task failed requiring plan regeneration ({outcome.value}): {result[:200]}..."
    #                 )
    #                 return f"PLAN_REGENERATION_NEEDED:{outcome.value}:{result}"

    #         except Exception as e:
    #             error_msg = f"Exception during task execution: {str(e)}"
    #             logger.exception(error_msg)
    #             self.retry_manager.add_attempt(
    #                 task=task,
    #                 reasoning_summary="Task execution failed with exception",
    #                 final_output=error_msg,
    #                 success=False,
    #                 errors=[error_msg],
    #             )
    #             context = self.retry_manager.get_retry_context(task)

    #     logger.error(f"Task failed after {context.max_retries} attempts")
    #     stats = self.retry_manager.get_statistics()
    #     logger.info(f"Retry statistics: {stats}")

    #     if context.attempts:
    #         return context.attempts[-1].final_output
    #     return f"Task failed after {context.max_retries} attempts"

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
        #from tools.rewind import RewindTool

        # rewind_tool = RewindTool()
        # self.registry.register(rewind_tool, namespace="control")
        
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
