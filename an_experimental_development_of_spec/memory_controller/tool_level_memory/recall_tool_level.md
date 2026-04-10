### /recall_tool_level

Memory Controller listens for the HTTP endpoint:
```code
POST /memory/recall_tool_level
```
When this endpoint is invoked, the Memory Controller understands that the agent is requesting relevant past memories from the Tool-Level Memory layer.
The request payload must contain:
```python
payload = {
  "collection": toolname, # the name of the tool; name of collection where to search
  "tool_parameters": params,   # raw structured parameters from tool call
  "top_k": top_k # how many elements to retrieve if there is more than k elements
}
```
Preconditions (More details can be found in `Initialization of DBs / Vector Store / Tool-level Memory config` paragpaph):
- The Vector Store(Tool-Level Memory) must already exist.
- Each tool must have its own collection.
- Each collection must contain named vectors corresponding to tool parameters.

Upon receiving the request, Memory Controller:
1. Parses the incoming tool parameters.
2. Generates separate embeddings for each parameter using the configured embedding model.
3. Selects the correct collection based on toolname.
4. Performs multi-vector similarity search for each parameter vector.
5. Aggregates similarity scores using a weighted scoring mechanism.
6. Retrieves the top_k most relevant memory entries.
7. Returns them as structured JSON.

Here is how I see searching(recalling) memory thoughts:
```python
# Search (Recall) should be like this
from openai import OpenAI

client = OpenAI()

# for example, toolname = "run_cmd"
toolname = "run_cmd"

def embed(text):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

collection = client.collections.get(toolname)

query_shell = "bash"
query_command = "cat list_of_emails_by_worker.txt"
#query_timeout = embed(int(30)) -- because we save only string values

shell_results = collection.query.hybrid(
    query=query_shell,
    target_vector="shell_vector",
    alpha=0.7,
    limit=5
)
# could be embedded summarization of some tool params if param is bigger than PARAM_THRESHOLD
command_results = collection.query.hybrid(
    query=query_command,
    target_vector="command_vector",
    alpha=0.7,
    limit=5
)

scores = {}

def add_scores(results, weight):
    for obj in results.objects:
        id = obj.uuid
        sim = 1 - obj.metadata.distance
        
        if id not in scores:
            scores[id] = 0
            
        scores[id] += weight * sim

add_scores(shell_results, 0.4)
add_scores(command_results, 0.6)

best = sorted(scores.items(), key=lambda x: x[1], reverse=True)

best_id = best[0][0]

memory = collection.query.fetch_object_by_id(best_id)

print(memory.properties["what_worked"])
print(memory.properties["what_to_avoid"])
```

The weighted aggregation stage combines similarity scores from different parameter searches into a single ranking score for each memory entry.

Example scoring logic:
final_score = w1 * similarity(param1) + w2 * similarity(param2) + ...

This approach allows the system to retrieve memories that are semantically similar at the parameter level, rather than relying on a single combined embedding.

API Response Format

Memory Controller must return an HTTP JSON response:
```python
{
  "memories": [
    {
      "tool_call": "...",
      "tool_output": "...",
      "what_worked": "...",
      "what_to_avoid": "..."
    }
  ]
}
```
