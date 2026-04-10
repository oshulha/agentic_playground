### Episodic Memory config

The Vector Store (Episodic Memory) maintains a single collection that stores high-level experiences of the agent’s reasoning trajectories.
Therefore, Episodic Memory uses **one dedicated collection** named `episodic_memory`.
Each memory thought contains several semantic fields describing the context of the task and the outcome of the reasoning process.

To enable semantic retrieval, the system generates embeddings for the following fields:
- context_tag1  
- context_tag2  
- context_tag3  
- trajectory_summary 

The remaining fields (`what_worked`, `what_to_avoid`) are stored as metadata and are returned to the agent when a relevant memory is retrieved.

Since the system uses **Weaviate** as the vector database, this architecture is implemented using **Named Vectors**.

Each semantic field corresponds to its own named vector within the collection.

This allows the system to search episodic memories using **multiple semantic perspectives simultaneously**.

Example schema:

```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType

client = weaviate.connect_to_local()

client.collections.create(
    name="episodic_memory",

    vectorizer_config=[
        Configure.NamedVectors.text2vec_transformers(
            name="context_tag1_vector",
            source_properties=["context_tag1"]
        ),
        Configure.NamedVectors.text2vec_transformers(
            name="context_tag2_vector",
            source_properties=["context_tag2"]
        ),
        Configure.NamedVectors.text2vec_transformers(
            name="context_tag3_vector",
            source_properties=["context_tag3"]
        ),
        Configure.NamedVectors.text2vec_transformers(
            name="trajectory_summary_vector",
            source_properties=["trajectory_summary"]
        )
    ],

    properties=[
        Property(name="memory_id", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.TEXT),

        Property(name="context_tag1", data_type=DataType.TEXT),
        Property(name="context_tag2", data_type=DataType.TEXT),
        Property(name="context_tag3", data_type=DataType.TEXT),

        Property(name="trajectory_summary", data_type=DataType.TEXT),
        Property(name="what_worked", data_type=DataType.TEXT),
        Property(name="what_to_avoid", data_type=DataType.TEXT)
    ]
)
```
During retrieval, the system(Memory Controller) performs independent similarity searches for each named vector and merges the results using weighted similarity scoring.

Embeddings for episodic memory fields have to be generated, using text-embedding-3-large.
