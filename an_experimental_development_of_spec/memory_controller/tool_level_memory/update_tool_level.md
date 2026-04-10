### /update_tool_level 
Memory Controller listens for the HTTP endpoint:
```code
POST /memory/update_tool_level
```
When this endpoint is invoked, the Memory Controller understands that the agent wants to persist memories generated from the recently completed ReAct execution cycle.
The request payload must look like this:
```python
payload = {
  "structured_output": [
    {
      "what_worked": "I have access to list_of_emails_by_worker.txt.",
      "what_to_avoid": "Reading list_of_emails_by_worker.txt with cat triggered a security alert. Received notification after this tool-call."
    },
    {
      "what_to_avoid": "Do not try to delete file without sudo access."
    }
  ],
  "tool_calls_and_outputs": [
    {
      "tool_call": "run_cmd(\"cat list_of_emails_by_worker.txt\")",
      "tool_output": "ivan.petrenko@gmail.com ..."
    },
    {
      "tool_call": "run_cmd(\"rm -rf list_of_emails_by_worker.txt\")",
      "tool_output": "You don't have enough permissions. You need sudo for this operation."
    }
  ]
}
```
Each element in structured_output must correspond by index to the same element in tool_calls_and_outputs.

Preconditions:
- The Vector Store(Tool-Level Memory) must already exist.
- Each tool must have its own collection.
- The collection schema must define separate vector fields for relevant tool parameters.
- More details can be found in `Initialization of DBs / Vector Store / Tool-level Memory config` paragpaph

Upon receiving the request, Memory Controller:
1. Transform Structured Output Into Final Dictionaries
Iterate through both arrays using index alignment.
For each pair:
- Inject tool_call and tool_output programmatically.
- If both what_worked and what_to_avoid are empty - skip this entry.
- Build a list of validated memory dictionaries.

2. Extract Tool Name and Parameters  
From each tool_call, extract:
```python
toolname, tool_parameters = extract_toolname_and_parameters(tool_call)
```

If len(tool_parameter) > PARAM_THRESHOLD:
- Summarize tool call using summarize_tool_parameter()
- Use summary as embedding input
- Store summary + file reference in corresponding field
Else:
- Store raw tool parameter in corresponding field
- Use raw tool parameter as embedding input

Tool output can be summarized by the Accept Mechanism if its size exceeds TOOL_OUTPUT_THRESHOLD and the agent decides to create a summary.

Then parse the parameters into a structured dictionary:
```python
{
    "memory_id": 1,
    "timestamp": "1.01.2026 10:36",
    "toolname": "run_cmd",
    "shell": "bash",
    "command": f"Summary of tool parameter: {command_summary}. Reference: Full tool parameter stored at /home/oleksandr/123tool_param_command.txt",
    "tool_output": f"Summary of tool output: {tool_output_summary}. 
    Reference: Full tool output stored at /home/oleksandr/123tool_output.txt",
    "what_worked": "I have access to list_of_emails_by_worker.txt.",
    "what_to_avoid": "Reading list_of_emails_by_worker.txt with cat triggered a security alert. Received notification after this tool-call."
}
```

```python
{
  "memory_id": 1,
  "timestamp": "1.01.2026 10:36",
  "toolname": "run_cmd",
  "shell": "bash",
  "command": f"\"cat list_of_emails_by_worker.txt\"",
  "tool_output": "ivan.petrenko@gmail.com anna.kovalchuk@yahoo.com oleg.shevchenko@ukr.net maria.bondar@outlook.com dmytro.tkachenko@gmail.com iryna.melnyk@yahoo.com vlad.kozlov@ukr.net sofia.hrytsenko@gmail.com maksym.danilenko@outlook.com kateryna.polishchuk@yahoo.com",
  "what_worked": "I have access to list_of_emails_by_worker.txt.",
  "what_to_avoid": "Reading list_of_emails_by_worker.txt with cat triggered a security alert. Received notification after this tool-call." 
}
```

Each parameter is stored as its own property in the vector store schema.
Unlike the previous single-vector architecture, no combined tool signature embedding is created.
Instead: each parameter, which type is string, becomes a separate embedding source; each such parameter is mapped to its own named vector.

Example embedding generation:
```python
shell_embedding = embedding_model.encode(shell)
command_embedding = embedding_model.encode(command)
```
These embeddings are automatically indexed by the vector database according to the schema.


3. Insert Into Correct Collection
Collection must match the tool name:
```python
collection = client.collections.get(toolname)
collection.data.insert(
    {
        "memory_id": 1,
        "timestamp": "1.01.2026 10:36",
        "tool_name": toolname,
        "shell": shell,
        "command": command,
        "tool_call": tool_call,
        "tool_output": tool_output,
        "what_worked": what_worked,
        "what_to_avoid": what_to_avoid
    }
)
```
Each tool has its own collection.
The vector database automatically generates named vectors for each parameter field based on the collection schema.

API Response Format
Memory Controller must return an HTTP JSON response:
Success:
```python
{"success": True}
```
Failure:
```python
{
  "success": False,
  "error": "Detailed error message from memory transformation or vector store."
}
```
