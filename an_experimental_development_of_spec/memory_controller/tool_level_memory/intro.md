### Intro

As described earlier, our agent is built on a ReAct architecture.
Tool-Level Memory is a specialized memory layer that operates at the granularity of tool interactions. Specifically, it stores and retrieves structured memories for each (tool call, tool output) pair generated during a ReAct execution cycle.

The primary purpose of Tool-Level Memory is to: improve tool-call accuracy, reduce repeated mistakes, and enable self-reflection before performing potentially costly or state-modifying actions.

The overall framework operates in two main stages:
• Stage-1: Recall Stage. 
When the agent generates a new tool call, tool call goes to the Commit Mechanism. 
The system retrieves relevant past memories associated with the same toolname, tool's parameters, similar execution contex(?) and presents them to the agent for reflection and confirmation. Retrieval is performed using multi-vector similarity search across string tool parameters.

• Stage-2: Post-think and Update. 
After ReAct completes its task, a structured post-processing step is triggered. Code extracts all tool-call and tool-output pairs generated during execution. Proposes a structured output to the agent.
The agent fills struсtured output fields such as: `what worked`, `what to avoid` - for each tool-call and tool-output pair.