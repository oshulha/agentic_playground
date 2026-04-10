### update_tool_level

After ReAct completes its task, the system automatically triggers a **post-execution reflection stage**. During this stage, the system extracts all `(tool-call, tool-output)` pairs produced during execution. A dynamic structured output schema is then generated using a function similar to `create_post_think_model`. 
The agent must analyze each tool interaction and optionally fill the following fields:
- `what_worked`
- `what_to_avoid`

Each filled field represents a **valuable insight** that should be stored in Tool-Level Memory. Only a **small subset of interactions** typically produces useful memories.

Example of function create_post_think_model:
```python
class PairToolCallOutput(BaseModel):
    what_worked: Optional[str] = Field(
        None,
        description="If there is something useful in this pair of tool call and tool output, then write it down. For example, include specific examples of successful tool usage(not basic one), well-chosen parameters, and the situations where the tool was used appropriately.",
    )
    what_to_avoid: Optional[str] = Field(
        None,
        description="If there is something useful in this pair of tool call and tool output that will be good to avoid, then write it down. For example, include examples of poor parameter choices, incorrect usage patterns, or situations where the tool should not have been used.",
    )

def create_post_think_model(
    list_of_pairs: List[Tuple[str, str]]
) -> Type[BaseModel]:
    """Dynamically create a Pydantic model for structured output based on the number of tool-call and tool-output pairs agent performed in the task.

    Args:
        list_of_pairs (List[Tuple[str, str]]): A list of tuples where each tuple contains the tool-call and tool-output.
    Returns:
        Type[BaseModel]: A Pydantic model class for structured output.
        Fields:
        - init_analysis: InitAnalysis
        - pair1, pair2, ..., pairN: PairToolCallOutput
    """

    # Add steps and grades
    for i, tool_call, tool_output in enumerate(list_of_pairs):
        fields[f"pair_{i+1}"] = (
            PairToolCallOutput, 
            Field(
                ..., 
                description=(
                    f"Analyze the following tool interaction.\n\n"
                    f"Tool Call:\n{tool_call}\n\n"
                    f"Tool Output:\n{tool_output}\n\n"
                    f"Provide analysis of this interaction."
                ),
            )
        )
    return create_model("ToolLevelAnalysis", **fields)
```

The prompt you need to provide to the Agent:

```python
user_prompt_to_agent = """
You are analyzing your own trajectory of solving a task in order to create memories that will help guide future interactions.
Your task is to extract key elements that would be most helpful when encountering similar situations in the future.

Review the trajectory and create a memory reflection following these rules:

1. If you do not have enough information for a field, the tool call-tool output pair is not relevant, contains nothing useful, or only includes generic advice, leave that field empty.
2. Do not include generic advice — extract only insights grounded in this specific tool-call and tool-output pair.
3. Be extremely concise - each string should be one clear, actionable sentence
4. Focus only on information that would be useful for handling similar future situations

Only a small number of insights is expected per trajectory (approximately 0–10% of the total number of tool call–tool output pairs).

It is completely normal for most fields to be empty.
It is also normal to fill only one field (e.g., what_worked or what_to_avoid) when applicable.

**Output Format:**
You must answer using the Structured Output format required by the system. In that format:
what_worked:
Describe a useful tool usage pattern observed in this interaction.

what_to_avoid:
Describe a tool usage pattern that should be avoided.

Examples:
Good "what_worked":
- "Using curl with the -L flag correctly followed redirects and retrieved the final page content."
- "Specifying the exact file path reduced unnecessary directory exploration."
- ""

Bad "what_worked":
- "It is better to use it like this."
- "The tool worked well."

Good "what_to_avoid":
- "Reading secret_passwords.md with cat triggered a security alert."
- "Calling the search tool without a query parameter caused an execution error."
- ""

Bad "what_to_avoid":
- "Do not read that file."
- "Avoid mistakes."

What worked examples:
- "Providing a precise query string improved the relevance of search results."
- "Using structured arguments instead of free text reduced parsing errors."

What to avoid examples:
- "Invoking the tool from Python code too frequently resulted in rate limit errors."
- "Using broad queries returned too many irrelevant results."
"""
``` 

Then, a list of tool calls and their outputs, along with a list of what_worked and what_to_avoid, is sent to the /memory/update_tool_level endpoint. The two lists must correspond to each other by index.

I see payload like this:
```python
payload = {
  "structured_output": [
    {
      "what_worked": "I have access to list_of_emails_by_worker.txt.",
      "what_to_avoid": "Reading list_of_emails_by_worker.txt with cat triggered a security alert. Received notification after this tool-call."
    },
    {
      "what_to_avoid": "Do not try to delete file without sudo access."
    }
  ],
  "tool_calls_and_outputs": [
    {
      "tool_call": "run_cmd(\"cat list_of_emails_by_worker.txt\")",
      "tool_output": "ivan.petrenko@gmail.com ..."
    },
    {
      "tool_call": "run_cmd(\"rm -rf list_of_emails_by_worker.txt\")",
      "tool_output": "You don't have enough permissions. You need sudo for this operation."
    }
  ]
}
```
