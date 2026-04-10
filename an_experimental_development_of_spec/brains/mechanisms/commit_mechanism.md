### Commit Mechanism

**Purpose**
The Commit mechanism is wrapper mechanism over the agent's tool-calling. 
It introduces a validation and reflection step before executing any state-modifying (write-access) tool.
Instead of executing a generated tool call immediately, the system intercepts it and requires explicit confirmation from the agent after memory-based reflection.

The goal is to:
- Reduce incorrect or harmful tool usage
- Enforce self-verification before state-changing actions
- Integrate Tool-Level Memory Recall into the decision process
- Improve tool-call precision and long-term agent performance

**Scope**
The mechanism applies to:
- All state-modifying (write-access) tool calls initiated by the agent
- External MCP tools that perform write operations

**Tool Classification**
Definitions
Write-Access Tools are the tools that: modify files, execute system commands, change system state, perform destructive operations, send messages or modify external systems.

Read-Access Tools are the tools that: retrieve information, perform analysis without side effects.

**Current Core Tools**

| Tool | Access Type |
| --- | --- |
| `run_cmd` | Write |
| `file_write` | Write |
| `compact` | Write |
| `python` | Write |
| `file_read` | Read |
| `deep_research` | Read |
| `web_search` | Read |
| `text_analysis` | Read |

---

**Existing External MCP Services**

Tools from the following systems must be statically categorized (not dynamically classified):
- Slack MCP
- Google Workspace MCP
- Jira MCP
- GitHub MCP
- Confluence MCP (maybe also)

Must be categorized into:
- **Read-only**
- **Write-access**

**Commit Mechanism Behavior**
The Commit Mechanism is triggered every time the agent generates a tool call. The original tool call is not executed immediately.
Execution Flow:
1. The agent generates a write tool call.
2. The Commit Mechanism initiated and takes the tool-call.
3. `recall_tool_level()` is called and returns list of relevant memories.
4. The agent receives a reflection prompt instead of tool output.

Reflection Prompt (With Relevant Memories)
If relevant memories are retrieved:
```python
f"""You want to make such a tool-call: {curr_tool_call}. 
Here is what you recall about this tool-call: {list_of_relevant_memories}.
Are you sure that this is a correct tool call? 
Are you sure that this will help you get closer to completing the task? 
If you are sure, then call commit tool. 
If you are not sure, then make correct tool-call."""
```
If no relevant memories are retrieved:
```python
f"""You want to make such a tool-call: {curr_tool_call}. 
You can't recall anything about this tool-call. 
It seems like you are making this tool-call for the first time.
Are you sure that this is a correct tool call? 
Are you sure that this will help you get closer to completing the task? 
If you are sure, then call commit tool. 
If you are not sure, then make correct tool-call."""
```

After receiving the reflection prompt, the agent may:
- Approve the tool call by invoking commit(...)
- Modify the tool call and re-enter the Commit Mechanism (This way agent can iterate multiple times until confident)
The tool is executed only after explicit commit confirmation.
