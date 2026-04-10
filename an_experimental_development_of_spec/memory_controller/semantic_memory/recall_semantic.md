### /recall_semantic

When a new ReAct worker is invoked by the PlanExecutor, a semantic (vector) search retrieves the top 10 chunks most semantically similar to the user prompt. These chunks are then injected into the end of user prompt with a phrasing like: “Here are some facts and knowledge that may be relevant to your task and help you complete it: {dict_best_match}”

Also, because Semantic Memory is categorized as Explicit and Implicit at the same time it has a tool recall_semantic.
[In_Progress]
```python
def recall_semantic(
    query: str,
    alpha: int
) -> dict:
  """Recall relevant memories from semantic memory for explicit query.

Recommended scenarios:
- When the agent needs to retrieve factual or conceptual knowledge...

Best practices:
- Use this tool to ...

  Args:
    query: The search query.
    alpha: (Optional) Defaults to 0.7. This means the search result is influenced by 70% vector similarity and 30% BM25 ranking.
  """
```
