### /update_episodic 

Memory Controller listens for the HTTP endpoint:
```code
POST /memory/update_episodic
```
When this endpoint is invoked, the Memory Controller understands that the agent wants to persist an episodic memory thought generated after the completion of a task.

Preconditions:
- The Episodic Memory Vector Store collection must already exist.
- The schema must define seven Named Vectors corresponding to the following semantic fields: user_query, who, what, when, where, why, how.
More details can be found in `Initialization of DBs / Vector Store / Episodic Memory config` paragraph.

Upon receiving the request, Memory Controller:
1. Combines payload from `recall_episodic` endpoint and payload from `update_episodic` endpoint

The request payload must look like this example:
```python
payload = {
    "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.",
    "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
}
```

Before invoking an `update_episodic` endpoint was invoked `recall_episodic` endpoint, which needed to save a `payload` for update_episodic endpoint. 
Let's call it recall_episodic_payload. It has to look like this exaample:
```python
recall_episodic_payload = {
    "user_query": "Add a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
    "who": "Visitors and potential donors of the animal shelter website",
    "what": "Integration of a donation feature into an existing static website",
    "when": "During a website update aimed at improving fundraising capability",
    "where": "On the existing static website of a frontline animal shelter",
    "why": "To enable fundraising and clearly communicate the urgency of supporting the shelter",
    "how": "By embedding a prominent call-to-action that redirects users to an external donation service without modifying backend logic",
}
``` 

So final combined dict has to look like this.
```python
payload = {
    "user_query": "Add a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
    "who": "Visitors and potential donors of the animal shelter website",
    "what": "Integration of a donation feature into an existing static website",
    "when": "During a website update aimed at improving fundraising capability",
    "where": "On the existing static website of a frontline animal shelter",
    "why": "To enable fundraising and clearly communicate the urgency of supporting the shelter",
    "how": "By embedding a prominent call-to-action that redirects users to an external donation service without modifying backend logic",
    "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.",
    "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
}
```

2. Inject System Fields
Before storing the memory, the system enriches it with internal metadata fields: memory_id, timestamp.
memory_id is generated automatically by the Memory Controller.  
timestamp records the exact time when the memory is stored.

Example:
```python
{
  "memory_id": 5,
  "timestamp": "1.01.2026 10:36",
  "user_query": "Add a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
  "who": "Visitors and potential donors of the animal shelter website",
  "what": "Integration of a donation feature into an existing static website",
  "when": "During a website update aimed at improving fundraising capability",
  "where": "On the existing static website of a frontline animal shelter",
  "why": "To enable fundraising and clearly communicate the urgency of supporting the shelter",
  "how": "By embedding a prominent call-to-action that redirects users to an external donation service without modifying backend logic",
  "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.",
  "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
}
```

3. Insert Into Episodic Memory Collection
Each of the seven semantic fields is embedded, using text-embedding-3-large. Seven semantic fields are: "user_query", "who", "what", "when", "where", "why", "how".
These embeddings are automatically indexed by the vector database according to the Named Vector schema.
```python
collection = client.collections.get("episodic_memory")
collection.data.insert(
    {
        "memory_id": memory_id,
        "timestamp": timestamp,
        "user_query": payload["user_query"],
        "who": payload["who"],
        "what": payload["what"],
        "when": payload["when"],
        "where": payload["where"],
        "why": payload["why"],
        "how": payload["how"],
        "what_worked": payload["what_worked"],
        "what_to_avoid": payload["what_to_avoid"]
    }
)
```
The vector database automatically generates the seven Named Vectors:
user_query_vector, who_vector, what_vector, when_vector, where_vector, why_vector, how_vector.
Each episodic memory entry therefore contains seven independent vector representations corresponding to its semantic fields.

API Response Format

Memory Controller must return an HTTP JSON response.

Success:
```python
{
  "success": True
}
```

Failure:
```python
{
  "success": False,
  "error": "Detailed error message from episodic memory validation or vector store insertion."
}
```
