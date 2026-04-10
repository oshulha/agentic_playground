### Episodic Memory config

The Vector Store (Episodic Memory) maintains a single collection that stores high-level experiences of the agent’s reasoning trajectories.
Therefore, Episodic Memory uses **one dedicated collection** named `episodic_memory`.
Each memory thought contains several semantic fields describing the context of the task and the outcome of the reasoning process.

To enable semantic retrieval, the system generates embeddings for the following fields:
- "user_query": query provided by user
- "who": concrete actors, users, or stakeholders involved
- "what": exact action/task performed
- "when": the context, situation, or triggering condition (do not include date/time, as timestamps are stored separately in the format DD.MM.YYYY HH:MM)
- "where": environment, platform, or context (e.g., static website, backend system)
- "why": underlying goal, motivation, or problem being solved
- "how": concrete method, approach, or implementation strategy

The remaining fields (`memory_id`, `timestamp`, `what_worked`, `what_to_avoid`) are stored as metadata and are returned to the agent when a relevant memory is retrieved.

Since the system uses **Weaviate** as the vector database, this architecture is implemented using **Named Vectors**.

Each semantic field corresponds to its own named vector within the collection.

This allows the system to search episodic memories using **multiple semantic perspectives simultaneously**.

Example schema:

```python
import weaviate
from weaviate.classes.config import Property, DataType, Configure
import time
from episodic_memory_thoughts import episodic_memories
from dotenv import load_dotenv
import os

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

client = weaviate.connect_to_local()

client.collections.create(
    name="episodic_memory",

    vectorizer_config=[
        Configure.NamedVectors.text2vec_openai(
            name="user_query_vector",
            model="text-embedding-3-large",
            source_properties=["user_query"]
        ),
        Configure.NamedVectors.text2vec_openai(
            name="who_vector",
            model="text-embedding-3-large",
            source_properties=["who"]
        ),
        Configure.NamedVectors.text2vec_openai(
            name="what_vector",
            model="text-embedding-3-large",
            source_properties=["what"]
        ),
        Configure.NamedVectors.text2vec_openai(
            name="when_vector",
            model="text-embedding-3-large",
            source_properties=["when"]
        ),
        Configure.NamedVectors.text2vec_openai(
            name="where_vector",
            model="text-embedding-3-large",
            source_properties=["where"]
        ),
        Configure.NamedVectors.text2vec_openai(
            name="why_vector",
            model="text-embedding-3-large",
            source_properties=["why"]
        ),
        Configure.NamedVectors.text2vec_openai(
            name="what_worked_vector",
            model="text-embedding-3-large",
            source_properties=["what_worked"]
        ),
        Configure.NamedVectors.text2vec_openai(
            name="what_to_avoid_vector",
            model="text-embedding-3-large",
            source_properties=["what_to_avoid"]
        )
    ],

    properties=[
        Property(name="memory_id", data_type=DataType.INT),
        Property(name="timestamp", data_type=DataType.TEXT),

        Property(name="user_query", data_type=DataType.TEXT),
        Property(name="who", data_type=DataType.TEXT),
        Property(name="what", data_type=DataType.TEXT),
        Property(name="when", data_type=DataType.TEXT),
        Property(name="where", data_type=DataType.TEXT),
        Property(name="why", data_type=DataType.TEXT),
        Property(name="how", data_type=DataType.TEXT),

        Property(name="what_worked", data_type=DataType.TEXT),
        Property(name="what_to_avoid", data_type=DataType.TEXT)
    ]
)
```
During retrieval, the system(Memory Controller) performs independent similarity searches for each named vector and merges the results using weighted similarity scoring.

Embeddings for episodic memory fields have to be generated, using text-embedding-3-large.