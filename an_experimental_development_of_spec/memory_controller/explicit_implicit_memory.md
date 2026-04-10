## Explicit & Implicit Memory

As a starting point, we can categorize memory into Explicit and Implicit.
At this stage, all memory types — namely episodic, semantic, procedural, tool-level and user-personalized — will be both Explicit and Implicit at the same time.

Memory types categorized as Explicit expose a dedicated tool for recall (i.e., searching the memory store) based on an agent query.
Detailed description of functions you can see below in corresponding headings: Episodic Memory, Semantic Memory, Procedural Memory, Tool-Level Memory, User-personalized Memory.
```python
recall_semantic()
recall_episodic()
recall_procedural()
recall_tool_level()
recall_user_personalized()
```

Memory types categorized as Implicit are running in the background for the agent(ReAct/Planner) by Memory subsystem. 

Comparing Implicit and Explicit memories, the Explicit approach has the downside of introducing some extra latency before any response is delivered. It also requires combining the memory logic with the agent logic. However, memories categorized as Implicit avoids those issues - there’s no added latency, and memory logic remains separate. But running “in the background” also has its own drawbacks: the memory is not updated immediately, and extra logic is needed determine when to kick off the background process.

[In_Progress] Another way to updating memory involves user feedback, which is particularly relevant to episodic memory. For example, If the user marks an interaction as a positive one, you can save that feedback to recall in the future.

As I mentioned before at the moment we categorize all types of memories as both Explicit and Implicit at the same time. By this I mean that every type of memory has its own tool for recall (i.e., searching the memory store) based on an agent query.

[Temporary] In the future, we can evaluate usage patterns and identify cases where certain memory types should be only Explicit or only Implicit, depending on how they are accessed and utilized.
