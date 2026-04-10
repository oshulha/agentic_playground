### recall_tool_level

When the ReAct worker (PlanExecutor?) generates a tool call, that tool call is passed to the Commit Mechanism. The Commit Mechanism invokes the `recall_tool_level` function, which calls Memory Controller over `/memory/recall_tool_level`. `recall_tool_level` returns a list of relevant memories retrieved from the Vector Store(Tool-Level Memory). After all, relevant memories will be inserted in Commit Mechanism message. Those retrieved memories are then inserted into the Commit Mechanism message, allowing the agent to reflect on past tool usage before executing the new tool call.

Since Tool-Level Memory is considered both **explicit** and **implicit**, the `recall_tool_level` function is also exposed to ReAct as a tool. This allows the agent to explicitly query its own Tool-Level Memory when necessary.
Unlike the previous architecture that relied on a **single combined embedding**, the current system performs **multi-vector retrieval across individual tool parameters**.

Each parameter is embedded independently and searched against its corresponding vector index in the Vector Store(Tool-Level Memory). Similarity scores from multiple parameter searches are then aggregated using a weighted scoring function.

Here is how approximately I see implementation of `recall_tool_level()` ,`summarize_tool_parameter()` and `extract_toolname_and_parameters()`:
```python
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def summarize_tool_parameter(toolname: str, parameter_name: str, parameter_value: str) -> str:
  """Generate a concise one-sentence summary describing the intent of a tool parameter.
  The summary explains what the parameter value represents or what action it intends to perform, without mentioning the tool name or parameter name.
  Args:
        tool_name (str):
            Name of the tool being invoked.

        parameter_name (str):
            Name of the parameter passed to the tool.

        parameter_value (str):
            Value of the parameter that should be summarized.

    Returns:
        str:
            A single-sentence summary describing the intent of the parameter value.
  """
  prompt = f"""
You must produce a precise, single-sentence description of the action implied by a tool parameter value.

Context:
Tool name: {tool_name}
Parameter name: {parameter_name}
Parameter value:
{parameter_value}

Rules:
- Output EXACTLY one sentence.
- Describe what the parameter value is intended to do.
- Do NOT mention the tool name or parameter name.
- Be concrete and explicit about the action.
- Describe only the intended operation, not the result.
- Avoid vague phrases such as "processed data", "handled file", or "performed operation".

Example (Good):
Tool name: run_cmd
Parameter name: command
Parameter value: cat list_of_emails_by_worker.txt
Output:
Read the file "list_of_emails_by_worker.txt" using the cat command.

Example (Bad):
Read emails using run_cmd.
"""
    response = client.responses.create(
      model="gpt-5-nano",
      input=prompt
    )
    return response.output[0].content[0].text.strip()

def extract_toolname_and_parameters(tool_call: str) -> tuple:
    start = tool_call.find("(")
    end = tool_call.rfind(")")

    if start == -1 or end == -1 or start > end:
        return ""  # or give error

    return (tool_call[:start], tool_call[start + 1:end])

# Recall Tool-Level Memory Mechanism
MEMORY_CONTROLLER_URL = os.getenv("MEMORY_CONTROLLER_URL")
def recall_tool_level(
    toolname: str,
    tool_parameters: str,
    top_k: int = 5
) -> list:
  """Recall relevant memories from Tool-level memory for a specific tool using multi-vector parameter search.

  Each parameter is embedded separately inside the Memory Controller and searched against its corresponding named vector index. The Memory Controller aggregates similarity scores across parameters and returns the most relevant memories.

  This function is a wrapper over the Memory Controller API (e.g., POST /memory/recall_tool_level). It retrieves previously stored tool-call experiences related to the given tool.

  Purpose:
    The goal of recall is to provide the agent with past 
    experiences (successes, failures, security alerts, rate limits, etc.) related to similar tool calls, so that the agent can adapt 
    its reasoning before continuing execution.

  Args:
    toolname (str):
        The name of the tool whose memory collection should be searched.

    tool_parameters (str):
        It should be a tool parameters from tool call.

    top-k (int, optional):
        How many elements to retrieve if there is more than k elements. (default = 5).

    Returns:
        List:
            API response containing a list_of_relevant_memories.
    Example of tool usage:
      recall_tool_level(toolname="run_cmd", tool_parameters="cat list_of_emails_by_worker.txt")
"""
    list_of_param_names, list_params = extract_params(tool_parameters)
    ind = 0
    for param_name in list_of_param_names:
      ind += 1
      param = list_params[ind]
      if len(tool_parameter) > PARAM_THRESHOLD:
        query = summarize_tool_parameter(param_name, param)
      else:
        query = tool_parameter

    url = f"{MEMORY_CONTROLLER_URL}/memory/recall_tool_level"

    payload = {
        "collection": toolname,
        "tool_parameters": tool_parameters,
        "top_k": top_k
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        # Expected format:
        # {
        #     "memories": [...]
        # }

        return data.get("memories", [])

    except requests.exceptions.RequestException as e:
        print(f"[Tool-Level Recall Error] {e}")
        return []
```

Example usage:
```python
tool_call = 'run_cmd({"shell":"bash", "command":"cat list_of_emails_by_worker.txt"})'

toolname, params = extract_toolname_and_parameters(tool_call)

memories = recall_tool_level(
    toolname=toolname,
    tool_parameters=params
)
```
