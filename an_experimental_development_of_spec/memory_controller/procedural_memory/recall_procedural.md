### /recall_procedural 

Before each execution of the ReAct agent, the last 10 generated procedural memory instructions are added to its system prompt. They are taken from the file named `procedural_memory_instructions.txt`.

Also, because Procedural Memory is categorized as Explicit and Implicit at the same time it has a tool recall_procedural.
[In_Progress]
```python
def recall_procedural(
    query: str,
    alpha: int
) -> dict:
  """Recall relevant memories from procedural memory for explicit query.

Recommended scenarios:
- When the agent needs to retrieve factual or conceptual knowledge...

Best practices:
- Use this tool to ...

  Args:
    query: The search query.
    alpha: (Optional) Defaults to 0.7. This means the search result is influenced by 70% vector similarity and 30% BM25 ranking.
  """
```
