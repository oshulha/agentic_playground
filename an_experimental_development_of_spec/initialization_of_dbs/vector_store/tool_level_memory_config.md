### Tool-level Memory config

For The Vector Store(Tool-Level Memory) maintains a separate collection for each ReAct tool.
These collections must be created statically in advance for all tools registered in the ToolSelector (except tools like?: recall_tool_level, recall_episodic_memory, recall_semantic_memory, recall_procedural_memory, recall_user_level, recall_priming and other memory related tools)
Each dictionary is stored in the collection whose name matches the value stored under the "toolname" key as an example above.
Each collection schema must define:
- structured properties for tool parameters
- named vectors corresponding to those parameters

I decided to use Weaviate as the vector database.

Example schema:
```python
import weaviate
from weaviate.classes.config import Configure, Property, DataType

client = weaviate.connect_to_local()

client.collections.create(
    name="run_cmd",
    
    vectorizer_config=[
        Configure.NamedVectors.text2vec_transformers(
            name="shell_vector",
            source_properties=["shell"]
        ),
        Configure.NamedVectors.text2vec_transformers(
            name="command_vector",
            source_properties=["command"]
        )
    ],
    
    properties=[
        Property(name="memory_id", data_type=DataType.TEXT),
        Property(name="timestamp", data_type=DataType.TEXT),
        Property(name="tool_name", data_type=DataType.TEXT),
        Property(name="shell", data_type=DataType.TEXT),
        Property(name="command", data_type=DataType.TEXT),
        Property(name="tool_call", data_type=DataType.TEXT),
        Property(name="tool_output", data_type=DataType.TEXT),
        Property(name="what_worked", data_type=DataType.TEXT),
        Property(name="what_to_avoid", data_type=DataType.TEXT),
    ]
)
```
Each string parameter is vectorized independently. During retrieval the system performs independent vector searches for each parameter vector and merges the results using weighted similarity scoring.
The results are then merged using weighted similarity scoring to produce the final ranking.

Parameter embeddings have to be generated using text-embedding-3-large.
