### /recall_episodic

During recall, the system embeds the query context and performs independent vector searches for each semantic field. The results are merged using weighted similarity scoring.

Example retrieval procedure:
```python
# Search (Recall) should be like this
from openai import OpenAI

client = OpenAI()

def embed(text):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

collection = client.collections.get("episodic_memory")

user_query_memories = collection.query.hybrid(
    query=query,
    alpha=0.7,
    limit=5,
    target_vector="user_query_vector",
    return_metadata=["score"]
)

who_memories = collection.query.hybrid(
    query=query,
    alpha=0.7,
    limit=5,
    target_vector="who_vector",
    return_metadata=["score"]
)

what_memories = collection.query.hybrid(
    query=query,
    alpha=0.7,
    limit=5,
    target_vector="what_vector",
    return_metadata=["score"]
)

when_memories = collection.query.hybrid(
    query=query,
    alpha=0.7,
    limit=5,
    target_vector="when_vector",
    return_metadata=["score"]
)

where_memories = collection.query.hybrid(
    query=query,
    alpha=0.7,
    limit=5,
    target_vector="where_vector",
    return_metadata=["score"]
)

why_memories = collection.query.hybrid(
    query=query,
    alpha=0.7,
    limit=5,
    target_vector="why_vector",
    return_metadata=["score"]
)

how_memories = collection.query.hybrid(
    query=query,
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

# Temporal weightening (based on number of days)
decay_hours = 720  # 30 days

for id in list(scores.keys()):
  memory = collection.query.fetch_object_by_id(id)
  
  timestamp_str = memory.properties['timestamp']
  timestamp = datetime.fromisoformat(timestamp_str)

  hours_old = (datetime.now() - timestamp).total_seconds() / 3600
  
  weight = 0.5 ** (hours_old / decay_hours)
  final_weight = max(0.25, weight) # 60 days ago: hours_old = 1440 weight = 0.5 ** (1440/720) = 0.5^2 = 0.25

  scores[id] *= final_weight

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
