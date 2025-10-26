import argparse
import asyncio
import json
import os
import re
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, List, Optional, Tuple, Type
from langsmith import traceable, Client

import aiofiles
import yaml
from aiohttp import ClientSession
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field, create_model
from langsmith.run_helpers import get_current_run_tree
import time
from decimal import Decimal


system_prompt = """You are an expert AI agent specializing in analyzing logs from AI task executions. Your task is to extract and summarize key information from the provided log content, Task description, Dependencies, and Checkpoints.

**Task:**
You will be provided with log content that includes three parts:
1. Tool initialization phase: a short section at the beginning of the log where tools are created/selected.
2. Iteration of steps: multiple steps wrapped in XML tags <step_i>, each of which may contain:
    - <reasoning_summary> (optional): a brief summary of the LLM’s reasoning.
    - <tool_call call_id="id" tool_name="tool">: the tool invoked by the LLM and its input.
    - <tool_response call_id="id" tool_name="tool">: the output corresponding to the tool call with the same call_id.
    - <llm_output> (optional): the LLM’s text output, typically its final answer or a user-facing message.
3. Final decision: the agent’s final report stored in <final_response>.
You are required to analyze each step and provide a concise summary of tool usage, identify any errors, and assess whether each tool’s output met the agent’s expectations.

**Additional Info:**
    - Dependencies: a list of services included in the task (e.g., "rocketchat," "gitlab," "plane," "owncloud," or none) that describes which tools/services the agent will operate on.
    - Checkpoints: human-readable definitions of what constitutes task completion; used to evaluate the agent’s work.
    - Task description: the text of the task provided to the agent. Note: the agent saw only the task text and did not see any hints or Checkpoints.

**Possible Improvements:**
Your key role is to help improve the agent so it can complete more tasks and Checkpoints. For each step and in your final summary, provide concise, actionable suggestions:
    - Was the step necessary, or could the agent have skipped it?
    - Was the tool used correctly, or was there a mistake in the tool call? Did the agent provide incorrect input that caused an error or unexpected output?
    - Did the tool perform correctly and return the expected output? Could the tool’s output be made clearer or more useful for the agent?
    - Did the agent choose the right tool for the job? Would another tool have produced better results? Was no appropriate tool available?
    - If the task was not completed, identify the primary cause: agent reasoning/behavior, tool limitations/bugs, or external constraints.
    - Did the agent fully understand the task? Was the Task description unclear or insufficient relative to what the Checkpoints expected? Note any contradictions between the Task description and the Checkpoints.

**Output Format:**
You must answer using the Structured Output format required by the system. In that format:
    - Include per-step short summaries of the agent’s behavior and tool usage, with targeted improvement suggestions.
    - Include a final summary with your overall assessment and recommended improvements.
    
**Note:**
User will ask you twice:
    - The first call will be about everything we discussed above.
    - The second call will ask you to evaluate the agent. This is because our graders are not perfect and may contain errors (or check trace files, although this is not the case). Also, often, if an agent has completed checkpoint N, it means that it has automatically completed checkpoints K (for each K < N)."""
user_prompt_1 = """Here is your input data:
<task_description>
{task_description}
</task_description>
<dependencies>
{dependencies}
</dependencies>
<checkpoints>
{checkpoints}
</checkpoints>
<agent_results> 
{results}
</agent_results>

<log_content>
{log_content}
</log_content>
"""
user_prompt_2 = """
Thank you! Now, please evaluate the agent's performance based on your previous analysis. 

Occasions when you have to give full points for the checkpoint:

If the checkpoint asks you to check whether an answer or some computation is correct, but the checkpoint does not provide the exact correct answer to compare against, give full points for that checkpoint.

If evaluating the checkpoint requires seeing the contents of a file (for example, in OwnCloud or a local folder such as /workspace) and you have not seen the contents of that file, give full points for that checkpoint.

If the checkpoint description contradicts the task description, and according to the task description the agent completed everything correctly, give full points for that checkpoint.

Grade each checkpoint step-by-step."""
#If the agent FULLY performed the task, consider giving him a perfect score, even if some checkpoints were missed. Evaluating overall grade, focus more on the task description, not on the checkpoints. This is because our graders for the checkpoints may contain some errors, but we are not sure.
class InitAnalysis(BaseModel):
    is_success: bool = Field(
        ..., description="Were all tools created and selected successfully?"
    )
    errors: Optional[str] = Field(
        None,
        description="Describe any errors or issues during tool creation and selection.",
    )


class Step(BaseModel):
    reasoning_summary: str = Field(
        ...,
        description="Summary of the step and result: was the agent on the right track? Highlight only critical reasoning errors that derailed the agent",
    )
    is_justified: bool = Field(
        ..., description="Was the step necessary? False if unnecessary or harmful."
    )
    reasoning_improvements: Optional[str] = Field(
        None,
        description="Any suggestions of improvements to the agent's reasoning and behavior. Highlight only critical reasoning improvements that fixes the agent's mistakes.",
    )
    tools_summary: str = Field(
        ...,
        description="Issues/errors during tool execution. If none, state tool executed successfully.",
    )
    is_success: bool = Field(
        ..., description="Did the tools work successfully and predictably?"
    )
    tools_improvements: Optional[str] = Field(
        None,
        description="Any suggestions for improving the use of tools or effectiveness. How can we make the tools more convenient for agents?",
    )


class FinalAnalysis(BaseModel):
    is_executed_successfully: bool = Field(
        ...,
        description="Did the system work without any errors (whether tool-related or other errors)?",
    )
    is_task_completed: bool = Field(
        ...,
        description="Did the agent complete the task (in fact, as described in the task description)?",
    )
    are_all_checkpoints_completed: bool = Field(
        ..., description="Were all checkpoints completed?"
    )
    overall_summary: str = Field(
        ...,
        description="Overall summary of the agent's performance, suggested improvements, and any discrepancies between the task description and checkpoints. Include the most valuable suggestions from the step analyses.",
    )
    additional_summary: Optional[str] = Field(
        None,
        description="Any additional tools or environment aspects we should to consider?",
    )


def create_analysis_model(
    count_of_steps: int, task_metrics: Dict[str, Any]
) -> Type[BaseModel]:
    """Dynamically create a Pydantic model for structured output based on the number of steps and task metrics.

    Args:
        count_of_steps (int): The number of steps agent performed in the task.
        task_metrics (dict): The metrics dictionary for the specific task.

    Returns:
        Type[BaseModel]: A Pydantic model class for structured output.
        Fields:
        - init_analysis: InitAnalysis
        - step1, step2, ..., stepN: Step
        - final_analysis: FinalAnalysis
    """

    # Build all fields at once
    fields = {}
    fields["init_analysis"] = (
        InitAnalysis,
        Field(..., description="Initial analysis phase"),
    )

    # Add steps and grades
    for i in range(1, count_of_steps + 1):
        fields[f"step_{i}"] = (Step, Field(..., description=f"step_{i} analysis"))

    fields["final_analysis"] = (
        FinalAnalysis,
        Field(..., description="Final analysis phase"),
    )

    return create_model("CompoundAnalysis", **fields)


def create_evaluation_model(task_metrics: Dict[str, Any]) -> Type[BaseModel]:
    """Dynamically create a Pydantic model for structured output based on task metrics for evaluation.

    Args:
        task_metrics (dict): The metrics dictionary for the specific task.

    Returns:
        Type[BaseModel]: A Pydantic model class for structured output.
        Fields:
        - checkpoint1, checkpoint2, ..., checkpointM: int (grade for each checkpoint)
    """
    fields = {}
    for i, checkpoint in enumerate(
        task_metrics.get("checkpoints", [])
    ):
        tac_grader_result = checkpoint["result"]
        total = checkpoint["total"]
        if isinstance(tac_grader_result, bool):
            tac_grader_result = int(tac_grader_result)
        if isinstance(total, bool):
            total = int(total)
        
        fields[f"checkpoint_{i+1}"] = (
            int,
            Field(
                tac_grader_result,
                description=f"Your own grade for checkpoint №{i+1}. Original grade was {tac_grader_result} out of {total}. Make sure your answer is within this range otherwise whole code will break. Choose grade among those integers: {[j for j in range(tac_grader_result, total + 1)]}",
                ge=tac_grader_result,
                le=total,
            ),
        )

    return create_model("EvaluationAnalysis", **fields)

def token_and_cost_details(metrics, run_id):
    client = Client()
    run = client.read_run(run_id)
    metrics["grader_details"] = {}
    metrics["grader_details"]["total_tokens"] = run.total_tokens
    metrics["grader_details"]["total_tokens_details"] = {}
    metrics["grader_details"]["total_tokens_details"]["total_completion_tokens"] = run.completion_tokens
    metrics["grader_details"]["total_tokens_details"]["total_prompt_tokens"] = run.prompt_tokens
    metrics["grader_details"]["total_tokens_details"]["total_prompt_cache_read"] = run.prompt_token_details.get("cache_read", 0)
    metrics["grader_details"]["total_tokens_details"]["total_completion_reasoning"] = run.completion_token_details.get("reasoning", 0)

    metrics["grader_details"]["total_latency"] = float(run.latency) if isinstance(run.latency, Decimal) else run.latency
    metrics["grader_details"]["total_cost"] = float(run.total_cost) if isinstance(run.total_cost, Decimal) else run.total_cost
    metrics["grader_details"]["total_cost_details"] = {}
    metrics["grader_details"]["total_cost_details"]["total_completion_cost"] = float(run.completion_cost) if isinstance(run.completion_cost, Decimal) else run.completion_cost
    metrics["grader_details"]["total_cost_details"]["total_prompt_cost"] = float(run.prompt_cost) if isinstance(run.prompt_cost, Decimal) else run.prompt_cost


    return metrics

def add_best_worst_median(metrics_path, first_metric, second_metric, third_metric): 
    n = 3
    result = {}
    result["total_checkpoints_mismatched"] = 0
    result["run_worst_case"] = 0
    result["run_best_case"] = 0
    result["run_median_case"] = 0
    result = {**result, **first_metric}

    total_checkpoints_mismatched = 0
    run_worst_case = 0
    run_best_case = 0
    run_median_case = 0

    for task in first_metric["tests"].keys():
        checkpoints_mism = 0
        task_worst_case = 0
        task_best_case = 0
        task_median_case = 0
        for i in range(len(first_metric["tests"][task]["checkpoints"])):
            ai_result_1 = first_metric["tests"][task]["checkpoints"][i].get("ai_result", first_metric["tests"][task]["checkpoints"][i]["result"])
            ai_result_2 = second_metric["tests"][task]["checkpoints"][i].get("ai_result", second_metric["tests"][task]["checkpoints"][i]["result"])
            ai_result_3 = third_metric["tests"][task]["checkpoints"][i].get("ai_result", third_metric["tests"][task]["checkpoints"][i]["result"])
            task_worst_case += min(ai_result_1, ai_result_2, ai_result_3)
            task_best_case += max(ai_result_1, ai_result_2, ai_result_3)
            task_median_case += (ai_result_1 + ai_result_2 + ai_result_3) / n

            assessment1 = first_metric["tests"][task]["checkpoints"][i].get("ai_result", "-")
            assessment2 = second_metric["tests"][task]["checkpoints"][i].get("ai_result", "-")
            assessment3 = third_metric["tests"][task]["checkpoints"][i].get("ai_result", "-")
            if not assessment1 == assessment2 == assessment3:
                checkpoints_mism += 1
        run_worst_case += task_worst_case
        run_best_case += task_best_case
        run_median_case += task_median_case
        
        total_checkpoints_mismatched += checkpoints_mism

    result["run_worst_case"] = run_worst_case
    result["run_best_case"] = run_best_case
    result["run_median_case"] = run_median_case
    result["total_checkpoints_mismatched"] = total_checkpoints_mismatched        

    return result

def list_log_files(metrics: dict, logs_path: str | Path) -> List[Tuple[Path, str]]:
    """Open metrics file -> get mapping of public links to task names -> for each log file in logs_dir,
    extract the last smith.langchain.com link -> return list of log files with corresponding task name.

    Args:
        metrics (dict): The metrics dictionary loaded from the JSON file.
        logs_dir (str | Path): directory containing all the log files

    Returns:
        List[Tuple[Path, str]]: A list of tuples containing log file paths and their corresponding task names.

    Notes:
        - Ignores log files without a smith.langchain.com link.
        - If a link does not match any task, skips it.
    """
    link_to_task_name = {}
    for task_name, test in metrics.get("tests", {}).items():
        link_to_task_name[test.get("public_link")] = task_name

    pattern = re.compile(
        re.escape("https://smith.langchain.com") + r"\S*"
    )  # non-whitespace run after domain

    log_files = []
    for log_file in Path(logs_path).glob("*.log"):
        text = log_file.read_text(encoding="utf-8", errors="ignore")
        if not (matches := pattern.findall(text)):
            continue  # no smith.langchain.com link found
        m = matches[-1]  # take the last match
        link = m.rstrip(".,);\"]'")  # clean trailing punctuation
        task_name = link_to_task_name.get(link)
        if task_name:
            log_files.append((log_file.resolve(), task_name))

    return log_files

async def analyze_run(
    session: ClientSession, log_file: Path, task_name: str, task_metrics: dict
):
    dependencies_url = f"https://raw.githubusercontent.com/TheAgentCompany/TheAgentCompany/refs/heads/main/workspaces/tasks/{task_name}/dependencies.yml"
    checkpoints_url = f"https://raw.githubusercontent.com/TheAgentCompany/TheAgentCompany/refs/heads/main/workspaces/tasks/{task_name}/checkpoints.md"
    description_url = f"https://raw.githubusercontent.com/TheAgentCompany/TheAgentCompany/refs/heads/main/workspaces/tasks/{task_name}/task.md"
    async with session.get(dependencies_url) as resp:
        dependencies = yaml.safe_load(await resp.text()) or []
    async with session.get(checkpoints_url) as resp:
        checkpoints = await resp.text() or "No checkpoints found!"
    async with session.get(description_url) as resp:
        description = await resp.text() or "No description found!"

    async with aiofiles.open(
        log_file, mode="r", encoding="utf-8", errors="ignore"
    ) as f:
        raw_log_content = await f.read()
        delimiter = "= MODELS ANALYSIS COMPLETE ="
        _before, _sep, _after = raw_log_content.partition(delimiter)
        log_content = _after.lstrip("=\n ") if _sep else raw_log_content

    step_line_pattern = re.compile(r"^<step_(\d+)>\s*$", re.MULTILINE)
    count_of_steps = len([int(n) for n in step_line_pattern.findall(log_content)])

    analysis_model = create_analysis_model(count_of_steps, task_metrics)
    evaluation_model = create_evaluation_model(task_metrics)
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0, seed=12345)

    user_prompt_filled = user_prompt_1.format(
        task_description=description,
        dependencies=", ".join(dependencies) if dependencies else "No dependencies",
        checkpoints=checkpoints,
        results=json.dumps(task_metrics["checkpoints"], indent=2),
        log_content=log_content,
    )
    try:
        cache_key = f"cache-{task_name}"
        messages = [("system", system_prompt), ("human", user_prompt_filled)]
        analysis = await llm.with_structured_output(analysis_model).ainvoke(messages, prompt_cache_key=cache_key)

        messages.extend(
            [("ai", str(analysis.model_dump(mode="json"))), ("human", user_prompt_2)]
        )
        evaluation = await llm.with_structured_output(evaluation_model).ainvoke(messages)

    except Exception as e:
        print(f"Error processing task {task_name}: {e}")
        return None, task_metrics
    try:
        ai_result = 0
        for key, value in evaluation.model_dump().items():
            if key.startswith("checkpoint_"):
                task_metrics["checkpoints"][int(key.replace("checkpoint_", "")) - 1][
                    "ai_result"
                ] = value
                ai_result += value
        task_metrics["final_score"]["ai_result"] = ai_result
    except Exception as e:
        print(f"Error updating metrics for task {task_name}: {e}")
    return analysis, task_metrics

@traceable()
async def run_of_grader(metrics_path, logs_path, ind):
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.name = f"Run{ind}"

    with open(metrics_path) as f:
        metrics = json.load(f)
    log_files = list_log_files(metrics, logs_path)

    async with ClientSession() as session:
        tasks = [
            analyze_run(session, log_file, task_name, metrics["tests"][task_name])
            for log_file, task_name in log_files
        ]
        results = await asyncio.gather(*tasks)

    analysis_list = []
    for i, task_name in enumerate([tn for _, tn in log_files]):
        try:
            analysis, updated_metrics = results[i]
            if analysis is not None:
                analysis_list.append({task_name: analysis.model_dump()})
            metrics["tests"][task_name] = updated_metrics
            metrics["total_ai_score"] = metrics["tests"][task_name].get(
                "final_score", {}
            ).get("ai_result", 0) + metrics.get("total_ai_score", 0)
        except Exception as e:
            print(f"Error processing result for task {task_name}: {e}")
            continue

    try:
        with open(logs_path + "/analysis_results.json", "w") as f:
            json.dump(analysis_list, f, indent=2)
    except Exception as e:
        print(f"Error writing analysis results file: {e}")

    try:
        base, ext = os.path.splitext(metrics_path)
        updated_metrics_file_path = base + "metric_" + str(ind) + ext

        with open(updated_metrics_file_path, "w") as f:
            json.dump(metrics, f, indent=2)
        
        return metrics
    except Exception as e:
        print(f"Error writing updated metrics file: {e}")

@traceable(name="AIGrader")
async def run_three_graders(metrics_path, logs_path):
    """Parent function that runs all 3 graders and tracks them together."""
    updated_metrics1 = await run_of_grader(metrics_path, logs_path, 1)
    updated_metrics2 = await run_of_grader(metrics_path, logs_path, 2)
    updated_metrics3 = await run_of_grader(metrics_path, logs_path, 3)
    run_tree = get_current_run_tree()
    
    updated_metrics = add_best_worst_median(metrics_path, updated_metrics1, updated_metrics2, updated_metrics3)
    return updated_metrics, run_tree


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--metrics-path",
        type=str,
        required=True,
        help="Path to the final merged metrics.json file",
    )
    parser.add_argument(
        "--logs-path",
        type=str,
        required=True,
        help="Path to the directory containing log files",
    )
    args = parser.parse_args()

    load_dotenv()
    
    metrics, run_tree = asyncio.run(run_three_graders(args.metrics_path, args.logs_path))

    if run_tree and run_tree.id:
        print(f"\nParent run ID: {run_tree.id}")
        metrics = token_and_cost_details(metrics, run_tree.id)
    else:
        print("No run_id from langsmith to get cost, token and latency details")
    
    base, ext = os.path.splitext(args.metrics_path)
    updated_metrics_file_path = base + "metric_final" + ext
        
    with open(updated_metrics_file_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)