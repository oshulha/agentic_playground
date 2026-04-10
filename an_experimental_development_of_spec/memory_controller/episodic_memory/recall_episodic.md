### /recall_episodic

Memory Controller listens for the HTTP endpoint:
```code
POST /memory/recall_episodic
```
When this endpoint is invoked, the Memory Controller understands that the agent wants to retrieve relevant memories from an episodic memory thought generated after the completion of a task.

The request payload must look like this:
```python
payload = {
    "user_query": "Add a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
    "who": "Visitors and potential donors of the animal shelter website",
    "what": "Integration of a donation feature into an existing static website",
    "when": "During a website update aimed at improving fundraising capability",
    "where": "On the existing static website of a frontline animal shelter",
    "why": "To enable fundraising and clearly communicate the urgency of supporting the shelter",
    "how": "By embedding a prominent call-to-action that redirects users to an external donation service without modifying backend logic"
}
```

During recall, the system embeds the query context and performs independent vector searches for each semantic field. The results are merged using weighted similarity scoring.

Example retrieval procedure:
```python
# Search (Recall) should be like this
from openai import OpenAI

client = OpenAI()

collection = client.collections.get("episodic_memory")

user_query_memories = collection.query.hybrid(
    query=payload["user_query"],
    alpha=0.7,
    limit=5,
    target_vector="user_query_vector",
    return_metadata=["score"]
)

who_memories = collection.query.hybrid(
    query=payload["who"],
    alpha=0.7,
    limit=5,
    target_vector="who_vector",
    return_metadata=["score"]
)

what_memories = collection.query.hybrid(
    query=payload["what"],
    alpha=0.7,
    limit=5,
    target_vector="what_vector",
    return_metadata=["score"]
)

when_memories = collection.query.hybrid(
    query=payload["when"],
    alpha=0.7,
    limit=5,
    target_vector="when_vector",
    return_metadata=["score"]
)

where_memories = collection.query.hybrid(
    query=payload["where"],
    alpha=0.7,
    limit=5,
    target_vector="where_vector",
    return_metadata=["score"]
)

why_memories = collection.query.hybrid(
    query=payload["why"],
    alpha=0.7,
    limit=5,
    target_vector="why_vector",
    return_metadata=["score"]
)

how_memories = collection.query.hybrid(
    query=payload["how"],
    alpha=0.7,
    limit=5,
    target_vector="how_vector",
    return_metadata=["score"]
)

scores = {}

def add_scores(results, weight):
    for obj in results.objects:
        id = obj.uuid
        sim = 1 - obj.metadata.distance
        
        if id not in scores:
            scores[id] = 0
            
        scores[id] += weight * sim

add_scores(user_query_memories, 0.25)
add_scores(who_memories, 0.125)
add_scores(what_memories, 0.125)
add_scores(when_memories, 0.125)
add_scores(where_memories, 0.125)
add_scores(why_memories, 0.125)
add_scores(how_memories, 0.125)

top_k = 10
best = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_k]

top_k_elements = ""

for memory_id, score in best:
  memory = collection.query.fetch_object_by_id(memory_id)

  top_k_elements += f"memory_id: {memory.properties['memory_id']}\n"
  top_k_elements += f"timestamp: {memory.properties['timestamp']}\n"
  top_k_elements += f"user_query: {memory.properties['user_query']}\n"
  top_k_elements += f"who: {memory.properties['who']}\n"
  top_k_elements += f"what: {memory.properties['what']}\n"
  top_k_elements += f"when: {memory.properties['when']}\n"
  top_k_elements += f"where: {memory.properties['where']}\n"
  top_k_elements += f"why: {memory.properties['why']}\n"
  top_k_elements += f"how: {memory.properties['how']}\n"
  top_k_elements += f"what_worked: {memory.properties['what_worked']}\n"
  top_k_elements += f"what_to_avoid: {memory.properties['what_to_avoid']}\n\n"
```

The system(Memory Controller) returns the 10 memories with the highest combined similarity score.

After that LLM (gpt-5.4) with structured output is asked to took out 3 most relevant memories out of 10 memories with the highest combined similarity score.

Example of how I see implementation and usage:
```python
from pydantic import BaseModel, Field

class MemorySelection(BaseModel):
    explanation: str = Field(
        description="Explain why these 3 memories were selected as the most relevant."
    )
    top_1_memory_id: int = Field(description="ID of the most relevant memory")
    top_2_memory_id: int = Field(description="ID of the second most relevant memory")
    top_3_memory_id: int = Field(description="ID of the third most relevant memory")

def select_top_memories(top_k_elements: str, user_query: str):
    prompt = f"""
Here are 10 memories with the highest combined similarity score:
{top_k_elements}

Your task is to select the 3 most relevant memories according to the user query.

Each memory has:
- memory_id
- timestamp
- user_query
- who
- what
- when
- where
- why
- how
- what_worked
- what_to_avoid

IMPORTANT:
- Only choose from the provided IDs
- Do NOT invent new IDs
- Rank them by relevance (1 = best)

User query:
{user_query}

Return the result in structured format.
"""

    response = client.responses.parse(
        model="gpt-5.4",
        input=prompt,
        response_format=MemorySelection
    )

    return response.output_parsed


result = select_top_memories(
    top_k_elements="[{memory_id:1, timestamp:'...', user_query:'...', who: '...', what: '...', when: '...', where: '...', why: '...', what_worked: '...', what_to_avoid: '...'}, {memory_id:2, timestamp:'...'}, ...]",
    user_query="How to optimize Vector DB? Identify top-3 insights/solutions and then send it to the Ihor"
)

print(result)
```

Then Memory Controller sends top-3 memories to ReAct. Then these top-3 memories are inserted into ReAct's system prompt.

Also, you need to save payload for update_episodic endpoint.