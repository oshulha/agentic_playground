### Accept Mechanism

**Purpose**

The Accept Mechanism is a wrapper layer over read-access tool outputs in a ReAct-based agent architecture.

It introduces a validation and compression step after a read-access tool execution, but before the tool output is written into the agent’s working memory.

**Scope**

The Accept Mechanism applies to all tools (even external MCP tools, except tool_level_memory(), episodic_memory(), semantic_memory(), commit(), accept() and other memory-related tools) and only when tool output exceeding a configurable token threshold (default: 1000 tokens).

**Accept Mechanism Behavior**

The Accept Mechanism is triggered when the tool output exceeds TOOL_OUTPUT_THRESHOLD tokens (a configurable threshold).
This condition also applies if the tool output exceeds the threshold after passing through the Commit Mechanism.

High-Level Behavior

The agent must explicitly choose one of the following options:

* accept() — keep the raw tool output unchanged.
* accept(summary="...") — provide a summary of the output. In this case, the system automatically stores the full raw output in a file and appends a reference to that file.

Execution Flow

1. The agent calls a tool.
2. The tool executes normally.
3. The Accept Mechanism intercepts the tool output.
4. If the output exceeds TOOL_OUTPUT_THRESHOLD, the agent must choose:
* accept() — keep the full output as is.
* accept(summary="...") — replace the output with a summary.
5. If the agent provides a summary, the full output is stored in: /tool_outputs/accept/{tool_name}/{timestamp}.txt
6. The agent receives the following instruction:
```python
f"""
Tool {tool_name} returned a large output.

Choose one of the following options:
- accept() — keep the raw output as is.
- accept(summary="...") — provide a summary. The system will store the full output in a file and append a reference to it.

Summary guidelines:
Include only the most important information needed for further reasoning.

If you provide a summary, the full output will be stored at:
/tool_outputs/accept/{tool_name}/{timestamp}.txt
"""
```
Final Result
- If the summary is accepted:
The original tool output in the context window is replaced with the summary and a reference to the stored file.
- If the summary is rejected:
The full tool output is inserted into the agent’s context window.

**Deletion of Files**

Full raw tool outputs stored by the **Accept Mechanism** must be deleted immediately after the ReAct agent completes the task unless the corresponding summarized tool output has been stored in Tool-Level Memory.

If the summarized tool output is stored in Tool-Level Memory, the corresponding raw output file must be preserved.

If the memory entries (thoughts) containing the summarized tool outputs are later deleted from Tool-Level Memory, the corresponding raw output file may also be deleted if no summarized version of that output remains in Tool-Level Memory.

Files created by the Accept Mechanism must follow strict access policies:
Agent:
Read access: Allowed
Write access: Not allowed
Delete access: Not allowed
