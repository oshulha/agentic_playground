# My Memory Conceptual Architecture v1.2

Memory subsystem is the information storage and retrieval part of our AI Agent. It consists of a [not_sure]vector store that contains several collections, graph store and other storages for the best possible retrieval. It directly interacts with the Brains subsystem (PlanExecutor and ReAct) and operates at multiple levels, such as storing memories from the [not_sure]PlanExecutor as well as memories from each ReAct worker invoked by the PlanExecutor. At the moment, our Memory subsystem is composed of [not_sure]six underlying memory components:  tool-level, episodic, semantic, procedural memory, user-personalized memory, priming & classical conditioning & non-associative memory.

[old?]**Memory Architecture Diagram:**
![Memory Architecture Diagram](memory_schema.png)

# Table Of Contents

[**Overall Sequence Diagram**](#overall-sequence-diagram)

[**Memory Controller (code-only microservice)**](#memory-controller-code-only-microservice)
<br/>Progress: [██░░░░░░░░] 20%; Status: In Progress  
Memory Controller is a stateless microservice responsible for managing the lifecycle of agent memories. It exposes an HTTP API and serves as the abstraction layer between the cognitive system (ReAct/Brains) and persistent memory storage systems.

- [**Explicit & Implicit Memory**](#explicit-memory-conscious--implicit-memory-subconscious)
<br/>Progress: [██████████] 99%; Status: Done  
Division of the memory subsystem into two major categories: Explicit and Implicit. Explains how they differ, which memory types belong to each category, and discusses their trade-offs in latency, architectural separation, and update mechanisms.

- [**Working Memory**](#working-memory)
<br/>Progress: [██████████] 99%; Status: Done By OpenAI   
**This paragraph is provided for context only;** it does not contain any implementation ideas at the moment. 
Temporary, active workspace of the agent. Maintains current interaction state, conversation history, and short-term reasoning context.

- [**Tool-Level Memory**](#tool-level-memory)
<br/>Progress: [█████████░] 90%; Status: Done   
Stores structured reflections about individual tool executions.
(10% - PRD? Forgetting? other questions..)

  - [**Sequence Diagram**](#sequence-diagram)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_tool_level**](#recall_tool_level)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_tool_level**](#update_tool_level)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_tool_level**](#forget_tool_level)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/rewrite_tool_level**](#rewrite_tool_level)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

- [**Episodic Memory**](#episodic-memory)
<br/>Progress: [███░░░░░░░] 30%; Status: In Progress   
Stores past experiences and task executions. Includes structured reflections such as `what_worked`, `what_to_avoid`, summaries, and context tags.

  - [**Sequence Diagram**](#sequence-diagram-1)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_episodic**](#recall_episodic)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_episodic**](#update_episodic)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_episodic**](#forget_episodic)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

- [**Semantic Memory**](#semantic-memory)
<br/>Progress: [███░░░░░░░] 30%; Status: In Progress   
Represents structured factual knowledge and concepts. Implemented through RAG-style retrieval from vector databases or knowledge sources.

  - [**Sequence Diagram**](#sequence-diagram-2)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_semantic**](#recall_semantic)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_semantic**](#update_semantic)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_semantic**](#forget_semantic)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

- [**Procedural Memory**](#procedural-memory)
<br/>Progress: [██░░░░░░░░] 20%; Status: Done(v1)   
Encodes behavioral rules and execution strategies. Derived from episodic reflections and stored as concise operational instructions.

  - [**Sequence Diagram**](#sequence-diagram-3)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_procedural**](#recall_procedural)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

  - [**/update_procedural**](#update_procedural)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_procedural**](#forget_procedural)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

- [**Autobiographical / User-Personalized Memory**](#autobiographical-memory----user-personalized-memory)
<br/>Progress: [█░░░░░░░░░] 10%; Status: To Do   
Specialized form of episodic memory focused on user-specific patterns, preferences, and long-term identity modeling.

  - [**Sequence Diagram**](#sequence-diagram-4)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_user_level**](#recall_user_level)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_user_level**](#update_user_level)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_user_level**](#forget_user_level)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

- [**Priming & Classical Conditioning & Non-Associative Memory**](#priming--classical-conditioning--non-associative-memory)
<br/>Progress: [█░░░░░░░░░] 10%; Status: To Do   
Exploration of cognitive-inspired mechanisms and whether they are practically needed in agent systems.

  - [**Sequence Diagram**](#sequence-diagram-5)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_priming**](#recall_priming)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

  - [**/update_priming**](#update_priming)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_priming**](#forget_priming)
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

[**Brains(ReAct) Python harness**](#brainsreact-python-harness)
<br/>Progress: [██████████] 99%; Status: Done  
Short description: _TODO

- [**Tools**](#tools)
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**recall_tool_level**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

  - [**recall_episodic**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

  - [**recall_semantic**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

  - [**recall_procedural**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

  - [**recall_user_level**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

  - [**recall_priming**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

- [**Functions**](#functions)
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_tool_level**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_tool_level**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_episodic**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_episodic**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_semantic**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_semantic**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_procedural**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_procedural**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_user_level**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_user_level**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_priming**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_priming**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

- [**Mechanisms**](#mechanisms)
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**Commit Mechanism**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**Accept Mechanism**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

[**Initialization of DBs**]()
<br/>Progress: [██░░░░░░░░] 20%; Status: In Progress   
Short description: _TODO

- [**Vector Store**](#vector-store)
<br/>Progress: [█████░░░░░] 90?%; Status: In Progress   
Vector Store is a paragraph, which tells about vector store and its responsibilities for different memory subsystems (Tool-Level Memory, Episodic Memory).

  - [**Tool-level Memory config**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**Episodic Memory config**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

  - [**?Procedural Memory config**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

  - [**?Autobiographical / User-Personalized Memory config**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

  - [**?Priming & Classical Conditioning & Non-Associative Memory config**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

- [**Graph Store**](#vector-store)
<br/>Progress: [█████░░░░░] 90?%; Status: In Progress   
Short description: _TODO

  - [**Semantic Memory config**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO  

---

[**Other**]()
<br/>This section won't be in final spec. This is just ideas, resources, valuable info that can used in writing paragraphs above.

- [**What Agent Needs to Remember and What Not**](#what-agent-needs-to-remember-and-what-is-not)
<br/>Progress: [██░░░░░░░░] 10%; Status: To Do   
Defines criteria for deciding which information is memory-worthy. Includes discussion about relevance to task, user intent, and long-term utility.

- [**Forgetting**](#forgeting)
<br/>Progress: [██░░░░░░░░] 10%; Status: In Progress   
Selective forgetting strategies based on time decay, usage frequency, contradiction handling, and summarization-based replacement.

- [**Replacing (Contradiction Resolution)**](#replacing)
<br/>Progress: [██░░░░░░░░] 20%; Status: To Do   
Mechanisms for resolving conflicting memories and determining which information should be treated as authoritative.

- [**Retrieving Methods (Variants)**](#retrieving-methods-how-to-retrieve----variants-to-retrieve)
<br/>Overview of different retrieval strategies beyond standard vector search.

  - [RLM](#rlm)
  <br/>Recursive Language Model-based retrieval strategy with deeper reasoning loops.

  - [Single-vector Search Improvement](#single-vector-search-improvement)
  <br/>Improvements over naive embedding search, including agentic query refinement.

  - [DRIFT Search and GraphRAG (Fav)](#drift-search-and-graphrag-fav)
  <br/>Graph-enhanced retrieval strategies inspired by hierarchical and community-based reasoning.

  - [File System](#file-system)
  <br/>File-based memory storage approach aligned with LLM pretraining priors.

  - [LSH](#lsh)
  <br/>Two-stage approximate retrieval: LSH grouping followed by similarity search.

  - [Multi-vector Search](#multi-vector-search)
  <br/>Token-level or multi-representation matching approach with higher precision but higher latency.

- [**Benchmarks for Memory**](#benchmarks-for-memory)
<br/>Evaluation strategies to measure effectiveness of different memory types.

- [**Questions To Answer Still**](#questions-to-answer-still)
<br/>Open architectural questions regarding shared memory between PlanExecutor and ReAct workers.

- [**Ideas**](#ideas)
<br/>Experimental directions such as MMR, improved memory controller logic, and hybrid retrieval systems.

---

# Overall Sequence Diagram

# Memory Controller (code-only microservice)

Memory Controller is a stateless microservice responsible for managing the lifecycle of agent memories. It exposes an HTTP API and serves as the abstraction layer between the cognitive system (ReAct/Brains) and persistent memory storage systems.

## Explicit & Implicit Memory

As a starting point, we can categorize memory into Explicit and Implicit.
At this stage, all memory types — namely episodic, semantic, procedural, tool-level and user-personalized — will be both Explicit and Implicit at the same time.

Memory types categorized as Explicit expose a dedicated tool for recall (i.e., searching the memory store) based on an agent query.
Detailed description of functions you can see below in corresponding headings: Episodic Memory, Semantic Memory, Procedural Memory, Tool-Level Memory, User-personalized Memory.
```python
recall_semantic()
recall_episodic()
recall_procedural()
recall_tool_level()
recall_user_personalized()
```

Memory types categorized as Implicit are running in the background for the agent(ReAct/Planner) by Memory subsystem. 

Comparing Implicit and Explicit memories, the Explicit approach has the downside of introducing some extra latency before any response is delivered. It also requires combining the memory logic with the agent logic. However, memories categorized as Implicit avoids those issues - there’s no added latency, and memory logic remains separate. But running “in the background” also has its own drawbacks: the memory is not updated immediately, and extra logic is needed determine when to kick off the background process.

[In_Progress] Another way to updating memory involves user feedback, which is particularly relevant to episodic memory. For example, If the user marks an interaction as a positive one, you can save that feedback to recall in the future.

As I mentioned before at the moment we categorize all types of memories as both Explicit and Implicit at the same time. By this I mean that every type of memory has its own tool for recall (i.e., searching the memory store) based on an agent query.

[Temporary] In the future, we can evaluate usage patterns and identify cases where certain memory types should be only Explicit or only Implicit, depending on how they are accessed and utilized.

## Working Memory

[Temporary?]This paragraph is provided for context only; it does not contain any implementation ideas at the moment.

Working memory is what helps you keep track of information you are using right now and make sense of it as things change. For our Agents, it means remembering **the current conversation** and using it to respond properly in real time. 

At the moment, we can say that OpenAI provides a solution for working memory, but maintaining a consistently growing list of all user inputs, tool calls, tool outputs, and reasoning items—appended each time the agent receives inputs and produces outputs—looks like not the best solution.

Working memory acts as an active workspace that manages information between episodic experience retrieval and semantic knowledge access, while keeping track of the exact state of the current interaction.

For Example: 
HUMAN: Hello!

AI Agent: Hello!

HUMAN: What's my name?

AI Agent: I do not have access to that information

HUMAN: My name is Adam

AI Agent: It's nice to meet you, Adam!

HUMAN: What is my name?

AI Agent: You said your name is Adam

To be continued...?

## Tool-level Memory

### Intro

As described earlier, our agent is built on a ReAct architecture.
Tool-Level Memory is a specialized memory layer that operates at the granularity of tool interactions. Specifically, it stores and retrieves structured memories for each (tool call, tool output) pair generated during a ReAct execution cycle.

The primary purpose of Tool-Level Memory is to: improve tool-call accuracy, reduce repeated mistakes, and enable self-reflection before performing potentially costly or state-modifying actions.

The overall framework operates in two main stages:
• Stage-1: Recall Stage. 
When the agent generates a new tool call, tool call goes to the Commit Mechanism. 
The system retrieves relevant past memories associated with the same toolname, tool's parameters, similar execution contex(?) and presents them to the agent for reflection and confirmation. Retrieval is performed using multi-vector similarity search across string tool parameters.

• Stage-2: Post-think and Update. 
After ReAct completes its task, a structured post-processing step is triggered. Code extracts all tool-call and tool-output pairs generated during execution. Proposes a structured output to the agent.
The agent fills struсtured output fields such as: `what worked`, `what to avoid` - for each tool-call and tool-output pair.

### Sequence Diagram

```mermaid
%%{init: {'themeVariables': { 
    'fontSize': '28px',
    'sequenceNumberFontSize': '28px',
}}}%%
sequenceDiagram
    title Tool-Level Memory Flow

    actor ReAct
    participant MC as Memory Controller
    participant VS as Vector Store

    activate ReAct

    ReAct->>ReAct: System Prompt
    ReAct->>ReAct: User Prompt
    ReAct->>ReAct: tool-call: python("sum(2, 2)")
    ReAct->>ReAct: Commit Mechanism initiated

    ReAct->>MC: recall_tool_level(tool="python", tool_parameters="sum(2,2)")
    Note right of ReAct: HTTP POST /memory/recall_tool_level

    MC->>VS: Tool-Level Memory:<br/>similarity_search(collection="python", query="sum(2,2)")
    VS->>MC: relevant memories

    MC->>ReAct: You are recalling such memories: {relevant_memories}.<br/>Are you sure you want to make python("sum(2, 2)")?

    ReAct->>ReAct: Commits (yes, I am sure)
    ReAct->>ReAct: tool-output: Sum is 4.

    ReAct->>ReAct: tool-call: run_cmd("{"command": "ls", "path":"/home/oleksandr"}")

    ReAct->>ReAct: Commit Mechanism initiated

    ReAct->>MC: recall_tool_level(tool="run_cmd",<br/>tool_parameters="{"command": "ls", "path":"/home/oleksandr"}")
    Note right of ReAct: HTTP POST /memory/recall_tool_level

    MC->>VS: Tool-Level Memory:<br/>similarity_search(collection="run_cmd",<br/>query="{"command": "ls", "path":"/home/oleksandr"}")

    VS->>MC: relevant memories:<br/>file.txt file2.txt

    MC->>ReAct: You are recalling such memories: file.txt file2.txt.<br/>Are you sure you want to make run_cmd<br/>("{"command": "ls", "path":"/home/oleksandr"}")?

    ReAct->>ReAct: Commits (no, I am not sure).<br/>I want to make tool-call: rocketchat_send_msg({user: "Bob", text: "Hi!"})

    ReAct->>ReAct: tool-call: rocketchat_send_msg({user: "Bob", text: "Hi!"})
    ReAct->>ReAct: Commit Mechanism initiated

    ReAct->>MC: recall_tool_level(tool="rocketchat_send_msg",<br/>tool_parameters="{user: "Bob", text: "Hi!"}")
    Note right of ReAct: HTTP POST /memory/recall_tool_level

    MC->>VS: Tool-Level Memory:<br/>similarity_search(collection="rocketchat_send_msg",<br/>query="{user: "Bob", text: "Hi!"}")

    VS->>MC: relevant memories

    MC->>ReAct: You are recalling such memories: {relevant_memories}.<br/>Are you sure you want to make rocketchat_send_msg<br/>("{user: "Bob", text: "Hi!"}")?

    ReAct->>ReAct: Commits (yes, I am sure)
    ReAct->>ReAct: tool-output: {"success": True}

    ReAct->>ReAct: tool-call: rocketchat_wait_for_msg()
    ReAct->>ReAct: Accept Mechanism initiated

    ReAct->>MC: Do you accept tool call: rocketchat_wait_for_msg() and<br/> tool output: {"success": True, "text": "Hi! How are you?"}? Or you want to summarize tool output?
    Note right of ReAct: HTTP POST /memory/recall_tool_level

    MC->>ReAct: Yes, I do accept.

    ReAct->>ReAct: tool-output: {"success": True, "text": "Hi! How are you?"}

    ReAct-->>ReAct: ..........more pairs of tool-call & tool-output......

    ReAct->>ReAct: filling a structured output schema with number of pairs of tool call and tool output fields<br/>per each pair of tool-call & tool-output

    Note right of ReAct: some python code will make out of structured output with number of pairs of tool call and tool output<br/>small JSONs having only memory_id, timestamp, toolname, (parametername1, parametername2, ...), tool-outputs, what_worked, what_to_avoid<br/>that was chosen as if it did smth valuable.
    Note right of ReAct: HTTP POST /memory/update_tool_level

    ReAct->>MC: sends final JSONs to Tool-Level Memory
    MC->>VS: sends final JSONs to Vector Store(Tool-Level Memory)
    VS->>MC: {success: True}
    MC->>ReAct: {success: True}
```

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

def embed(text):
    response = client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding

collection = client.collections.get(toolname)

query_shell = embed("bash")
query_command = embed("cat list_of_emails_by_worker.txt")
#query_timeout = embed(int(30)) -- because we save only string values

shell_results = collection.query.near_vector(
    near_vector=query_shell,
    target_vector="shell_vector",
    limit=5
)
# could be embedded summarization of some tool params if param is bigger than PARAM_THRESHOLD
command_results = collection.query.near_vector(
    near_vector=query_command,
    target_vector="command_vector",
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

### /forget_tool_level
-

### /rewrite_tool_level

After each Post-Think stage, the system performs a Tool-Level Memory Rewriting process. 
The goal of this process is to improve memory quality by removing redundancy, consolidating similar observations, and resolving contradictions that may arise as the agent gains more experience.

The system first identifies all Tool-Level Memory collections that were updated during the Post-Think stage.
For each affected collection, an LLM-based rewriting pipeline is executed.

The rewriting pipeline consists of two sequential stages:
- Memory Merging
- Contradiction Resolution

Both stages are implemented using LLM reasoning and operate on batches of recently updated memories.

**Execution Model**

The rewriting process is currently implemented as a two-step LLM pipeline:
1. Memory Merging LLM pass
2. Contradiction Resolution LLM pass

This separation improves reasoning quality because:
- the first pass focuses purely on deduplication
- the second pass focuses on semantic conflict analysis

I see implementation like this:
```python
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

set_of_memories = [
{
"memory_id": 1,
"timestamp": "06.03.2026 14:10",
"react_id": 1,
"tool_call": "run_cmd(path: /"/home/oleksandr/", cmd: /"cat config.yaml/")",
"tool_output": "Permission denied",
"what_to_avoid": "Trying to read config.yaml without sudo access.",
"what_worked": "—"
},
{
"memory_id": 2,
"timestamp": "06.03.2026 15:00"
"react_id": 1,
"tool_call": "run_cmd(path: /"/home/oleksandr/", cmd: /"ls/")"
"tool_output": "input.txt, intermediate.txt"
"what_to_avoid": "Checking result files while the processing script is still running."
"what_worked": "—"
},
{
"memory_id": 3,
"timestamp": "06.03.2026 15:05"
"react_id": 1,
"tool_call": "run_cmd(path: /"/home/oleksandr/", cmd: /"ls/")",
"tool_output": "input.txt, intermediate.txt",
"what_to_avoid": "Attempting to verify final results before the program has finished execution.",
"what_worked": "—"
}
{
"memory_id": 4,
"timestamp": "06.03.2026 15:09",
"react_id": 1,
"tool_call": run_cmd(path: "/home/oleksandr", cmd: "ls")
"tool_output": "input.txt, intermediate.txt, output.txt, config.yaml"
"what_to_avoid": "—",
"what_worked": "Checking the directory after the background process finished reveals the generated output file."
}, 
{
"memory_id": 5,
"timestamp": "06.03.2026 15:11",
"react_id": 1,
"tool_call": "run_cmd(path: /"/home/oleksandr/", cmd: /"cat config.yaml/")"
"tool_output": "database_url: postgres://localhost...",
"what_to_avoid": "—",
"what_worked": "Reading config.yaml directly using cat successfully returned configuration data after execution of background script."
}
]

prompt_merge = f"""
You are given a group of memories describing tool usage events.

Your task is to merge memories that describe the SAME situation or observation.

A memory has the following structure:
- memory_id
- timestamp
- tool_call
- tool_output
- what_to_avoid
- what_worked

MERGING RULES

1. Merge memories if they describe the same tool call and the same situation
   but are written slightly differently.

2. When merging:
   - Keep the memory with the MOST RECENT timestamp as the base memory.
   - Transfer useful information from older memories into the base memory.

3. If multiple memories contain similar "what_to_avoid" advice,
   merge them into a single clearer sentence.

4. If multiple memories contain similar "what_worked" advice,
   merge them into one concise explanation.

5. Do NOT merge memories if they clearly describe different situations,
   different tool calls, or different environments.

6. The final merged memory must keep the structure:
memory_id
timestamp
tool_call
tool_output
what_to_avoid
what_worked

7. If several memories describe the same event progression,
   prefer the most informative tool_output (usually the latest one).

Example

Input memories:

memory_id: 2
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt"
what_to_avoid: Checking result files while the processing script is still running.

memory_id: 3
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt"
what_to_avoid: Attempting to verify final results before the program has finished execution.

memory_id: 4
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt, output.txt, config.yaml"
what_worked: Checking the directory after the background process finished reveals the generated output file.

Output:

memory_id: 4
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt, output.txt, config.yaml"
what_to_avoid: Checking result files while the processing script is still running.
what_worked: Checking the directory after the background process finished reveals the generated output file.

Now merge the following memories:

Input:
{set_of_memories}
"""

# ---- First LLM call ----
response1 = client.responses.create(
    model="gpt-5-nano",
    input=prompt_merge
)

set_of_memories = response1.output_text
print("\nFirst response:\n", set_of_memories)

prompt_resolve_conflicts = f"""
You are given several memories describing tool executions and observations.

Some memories may contradict each other because:
- the environment changed over time
- earlier observations were incomplete
- conditions differed between executions

Your task is to detect and resolve contradictions between memories.

IMPORTANT:
You are NOT required to produce only one memory.
You may return multiple memories.

GENERAL RULE

Only merge memories if they describe the SAME tool_call and contain
contradictory observations about the result or conclusions.

If memories describe different situations or different tool calls,
keep them as separate memories.

Each memory has the following structure:

memory_id
timestamp
tool_call
tool_output
what_to_avoid
what_worked

CONFLICT RESOLUTION RULES

1. Detect groups of memories that refer to the SAME tool_call.
2. If there is NO contradiction between them, keep them unchanged.
3. If there IS a contradiction:
   a) Prefer the memory with the MOST RECENT timestamp
      as the base memory, because it reflects the most
      up-to-date state of the environment.
   b) Earlier memories should NOT be discarded if they contain
      useful lessons.
   c) Convert earlier conclusions into contextual advice inside:
      - "what_to_avoid"
      - "what_worked"
4. If an earlier failure later becomes a success,
   reinterpret the earlier failure as a contextual limitation.
Example:
- failure before a process finished
- success after the process finished

5. When merging advice:
   - move incorrect or outdated conclusions into a contextualized warning inside "what_to_avoid"
   - keep successful strategies in "what_worked"

6. Always preserve the memory structure:

memory_id
timestamp
tool_call
tool_output
what_to_avoid
what_worked

7. The output may contain:
   - the same number of memories
   - fewer memories if some were merged

8. Do NOT remove useful information.
   Only resolve contradictions.

Example

Input memories:

memory_id: 1
timestamp: 06.03.2026 14:10
tool_call: run_cmd(path="/home/oleksandr", cmd="cat config.yaml")
tool_output: "Permission denied"
what_to_avoid: Trying to read config.yaml without sudo access.

memory_id: 5
timestamp: 06.03.2026 15:11
tool_call: run_cmd(path="/home/oleksandr", cmd="cat config.yaml")
tool_output: "database_url: postgres://localhost..."
what_worked: Reading config.yaml directly using cat successfully returned configuration data after execution of background script.

Output:

memory_id: 5
timestamp: 06.03.2026 15:11
tool_call: run_cmd(path="/home/oleksandr", cmd="cat config.yaml")
tool_output: "database_url: postgres://localhost..."
what_to_avoid: Trying to read config.yaml before or during execution of the background script.
what_worked: Reading config.yaml directly using cat successfully returned configuration data after execution of the background script.

Now resolve contradictions in the following memories:

Input:
{set_of_memories}
"""

# ---- Second LLM call ----
response2 = client.responses.create(
    model="gpt-5-nano",
    input=prompt_resolve_conflicts
)

result2 = response2.output_text
print("\nSecond response:\n", result2)
```

**Scalability Considerations**

The described rewriting approach assumes that the number of memories processed in a single batch is moderate.

(Звісно, цей підхід працює якщо кількість елементів не захмарна!!! Інакше Шо Лі Доведеться Відмовитись Від цього Механізму???)
Що краще спочатку робити Merging, Rewriting? Чи дати це в одному промпті?
Або ми (можемо) будемо зберігати, що ми в основному брали з векторної бази даних і кому повертали, щоб робити аналіз після РеАкта, а не під час. Або якось робити паралельно форгеттінг.
Датування (Володимир казав, що є 3 варіанти забування міт 25.02, як він бачить працюючих)

## Episodic Memory

### Intro

Episodic memory is a historical collection of prior experiences, or episodes. It includes what happened, how it happened, and the lessons or insights learned from those experiences, even if they were never clearly stated.

### Sequence Diagram
```mermaid
sequenceDiagram
    title Episodic Memory: Recall & Store Flow

    actor ReAct
    participant MC as Memory Controller
    participant VS as Vector Store

    activate ReAct

    ReAct->>ReAct: System Prompt
    ReAct->>ReAct: User Prompt

    ReAct->>MC: recall_episodic(user_input)
    Note right of ReAct: HTTP POST /memory/recall_episodic

    MC->>VS: Episodic Memory search<br/>using context_tags and trajectory_summary<br/>Vector search / BM25 (still in progress)
    VS-->>MC: top-10 relevant reflections<br/>(what_worked, what_to_avoid)

    MC->>MC: LLM selects top-3 most relevant out of 10

    MC->>VS: Reward top-3 memories<br/>Penalty for remaining 7

    MC-->>ReAct: You recall memories:<br/>{relevant_memories}<br/>Use them as context

    ReAct->>ReAct: tool-call: python(sum(2,2))
    ReAct->>ReAct: tool-output: Sum is 4

    ReAct->>ReAct: tool-call: run_cmd({"command": "ls", "path":"/home/oleksandr"})
    ReAct->>ReAct: tool-output: file.txt, file2.txt

    ReAct-->>ReAct: ... more tool-call & tool-output pairs ...

    ReAct->>MC: POST structured output<br/>context_tags, trajectory_summary,<br/>what_worked, what_to_avoid

    MC->>MC: Inject system fields<br/>memory_id, timestamp<br/>Generate embeddings

    MC->>VS: Insert full memory object<br/>(4 Named Vectors + metadata)

    VS-->>MC: {success: True}

    MC-->>ReAct: {success: True}

    deactivate ReAct
```

### /recall_episodic

During recall, the system embeds the query context and performs independent vector searches for each semantic field. The results are merged using weighted similarity scoring.

Example retrieval procedure:
```python
# Search (Recall) should be like this
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2") # Must use OpenAI model from text-embedding-3-large that would provide higher accuracy

query_context_tag1 = model.encode("donation_feature_integration")
query_context_tag2 = model.encode("charity_website_ux")
query_context_tag3 = model.encode("existing_site_modification")
query_trajectory_summary = model.encode(
    "Added a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support."
)

collection = client.collections.get("episodic_memory")

context_tag1_results = collection.query.near_vector(
    near_vector=query_context_tag1,
    target_vector="context_tag1_vector",
    limit=5
)

context_tag2_results = collection.query.near_vector(
    near_vector=query_context_tag2,
    target_vector="context_tag2_vector",
    limit=5
)

context_tag3_results = collection.query.near_vector(
    near_vector=query_context_tag3,
    target_vector="context_tag3_vector",
    limit=5
)

trajectory_summary_results = collection.query.near_vector(
    near_vector=query_trajectory_summary,
    target_vector="trajectory_summary_vector",
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

add_scores(context_tag1_results, 0.2)
add_scores(context_tag2_results, 0.2)
add_scores(context_tag3_results, 0.2)
add_scores(trajectory_summary_results, 0.4)

best = sorted(scores.items(), key=lambda x: x[1], reverse=True)

best_id = best[0][0]

memory = collection.query.fetch_object_by_id(best_id)

print(memory.properties["what_worked"])
print(memory.properties["what_to_avoid"])
```

The system(Memory Controller) returns the 3 memories with the highest combined similarity score.

### /update_episodic 

Memory Controller listens for the HTTP endpoint:
```code
POST /memory/update_episodic
```
When this endpoint is invoked, the Memory Controller understands that the agent wants to persist an episodic memory thought generated after the completion of a task.

The request payload must look like this:
```python
payload = {
    "context_tag1": "donation_feature_integration",
    "context_tag2": "charity_website_ux",
    "context_tag3": "existing_site_modification",
    "trajectory_summary": "Added a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
    "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.",
    "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
}
```

Preconditions:
- The Episodic Memory Vector Store collection must already exist.
- The schema must define four Named Vectors corresponding to the following semantic fields: context_tag1, context_tag2, context_tag3, trajectory_summary.
More details can be found in `Initialization of DBs / Vector Store / Episodic Memory config` paragraph

Upon receiving the request, Memory Controller:
1. Inject System Fields
Before storing the memory, the system enriches it with internal metadata fields: memory_id, timestamp.
memory_id is generated automatically by the Memory Controller.  
timestamp records the exact time when the memory is stored.

Example:
```python
{
  "memory_id": 5,
  "timestamp": "1.01.2026 10:36",
  "context_tag1": "donation_feature_integration",
  "context_tag2": "charity_website_ux",
  "context_tag3": "existing_site_modification",
  "trajectory_summary": "Added a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
  "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.",
  "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
}
```

2. Embedding Generation  
Each of the four semantic fields is embedded independently, using text-embedding-3-large.

```python
context_tag1_embedding = embedding_model.encode(context_tag1)  
context_tag2_embedding = embedding_model.encode(context_tag2)  
context_tag3_embedding = embedding_model.encode(context_tag3)  
trajectory_summary_embedding = embedding_model.encode(trajectory_summary)
```
These embeddings are automatically indexed by the vector database according to the Named Vector schema.

3. Insert Into Episodic Memory Collection
```python
collection = client.collections.get("episodic_memory")
collection.data.insert(
    {
        "memory_id": memory_id,
        "timestamp": timestamp,
        "context_tag1": context_tag1,
        "context_tag2": context_tag2,
        "context_tag3": context_tag3,
        "trajectory_summary": trajectory_summary,
        "what_worked": what_worked,
        "what_to_avoid": what_to_avoid
    }
)
```
The vector database automatically generates the four Named Vectors:
context_tag1_vector, context_tag2_vector, context_tag3_vector, trajectory_summary_vector.
Each episodic memory entry therefore contains four independent vector representations corresponding to its semantic fields.

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

### /forget_episodic

## Semantic Memory

### Intro

Да, то есть у нас, например, есть... стартует агент. Он еще никаких Tool Call-ов не запускал. Мы еще даже тулы не населектили. Дергается Memory Controller с вопросом, типа: "Вот у нас такая задача к такому-то виду агента (к воркеру или оркестратору соответственно), вспомни все релевантное". И он пойдет посмотрит на эту задачу, скажет: "Ой, тут система такая-то упомянута, я сейчас достану, кто ее там менеджерит, какой у него имейл" и тому подобное. Вот это все как бы про семантические знания, которые могут быть полезны для решения задачи. 

Поэтому условно семантическая память мне кажется более приоритетной. То есть способность прочитать вику, прочитать длинный какой-нибудь там диалог объяснения человека специфики его работы, его департамента и так далее. И все это замапить в какой-то там граф знаний, какую-то короче схему. Вот это важнее, чтобы можно было насыщать контекст вот этой вот надставкой работы агента.

Ну вот семантическая память — она да, про факты и про взаимосвязи между этими фактами, между этими знаниями. Типа что Confluence — это на самом деле, например, там https://www.google.com/search?q=wiki.softtech.com. И там что у него есть условно администратор, у него есть инструкция пользования где-нибудь там лежит, и тому подобное. То есть чтобы у... здесь мне кажется как раз больше графовая какая-то структура может быть полезна для того, чтобы можно было все эти связанные вещи выискивать. Вот, соответственно, обновлять ее тоже нужно придумать способ. Придумать такую структуру, которую будет удобно обновлять, когда это будет необходимо. Вот, то есть семантика — она про то, что когда тебе говорят: "Иди и на конлфюэнс сделай что-то", а типа у нас ну нет ничего, что называется Confluence, у нас есть там домен, который называется https://www.google.com/search?q=wiki.softtech.com. И как типа система должна понять, что от нее просили? Как она должна эти воспоминания хранить? Вот.

Semantic memory represents our structured knowledge of facts, concepts, and their relationships - essentially what we "know" rather than what we "remember experiencing."
For our Agents, this would be implemented through techniques like Retrieval Augmented Generation (RAG), where relevant information is dynamically pulled from a knowledge base to ground and inform responses.

### Sequence Diagram

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

### /update_semantic

Detailed Implementation
Much of the organizational information already exists in sources such as Confluence, Jira, Slack, GitHub, and Google Drive. This information can be treated as factual knowledge.

[In_Progress]It would be valuable to capture additional facts during the agent's execution. For example, we can include a structured output field called semantic_memory at the end of the agent's run, where it records all facts observed throughout the execution or task completion. Since the agent still has access to its working memory, it can populate this field with relevant knowledge. Maybe it’s hard to keep track of everything when the task is long and the context window is filled with a lot of information. That’s why it makes sense to add ability Memory Controller that selectively extracts only the necessary information at each step—such as before a tool call, after a tool’s output, or when processing new user input.
Because the final structured response may become very large/overwhelming, it may be necessary to split it into multiple separate responses to get high-quality answers. (think about approach?)

All collected information should be stored in a vector database collection named semantic_memory, using high-quality chunking. For example, chunking can be based on markdown formatting or a recursive character chunker, taking advantage of [ChromaDB's custom chunkers](https://research.trychroma.com/evaluating-chunking)(or it is the same?).
#### How To Chunk? [To_Do]

### Examples
**Example**
HUMAN: Hello! Who is responsible for databases in RisingWave?
---
Semantic memory subsystem already has information from Confluence.
Retrieved relevant memories:

CHUNK 1:
Distributed Search Engine (based on OpenSearch)
Low-Code Event-Driven Application Platform (based on Node-RED)...

CHUNK 2:
All tasks in our benchmark are carefully curated by referencing the ONET database with detailed job
responsibilities. ONET database was created by the US Department of Labor with extensive data
curation, analysis, and summarization by domain experts....

CHUNK 3:
The Agent Company is an innovative software firm specializing in distributed systems
, database technologies, and artificial intelligence.
Main Products and Services
1. Distributed Graph Database (based on JanusGraph)
2. Streaming Database (based on RisingWave)...

CHUNK 4:
We hypothesize that part of the reason lies in the fact that current LLM development is heavily
based on software engineering abilities, such as coding, due to several high profile benchmarks that
measure this capability (e.g. HumanEval, SWE-Bench).
8 7.3 Common Agent Failures
Overall, the agent performance on TheAgentCompany is still low and a majority of tasks are failed.
Among those, we try to find some common and interesting agent mistakes that are often surprising

CHUNK 5:
It also contains information about tasks performed within the context of each job, abilities required to perform each task, whether
the task is a major or minor task for that job category, and other pieces of relevant information. Based
on this data, we first identified a few categories of occupation categories to focus on. 

CHUNK 6:
Zhang Wei (Male, 31 years old)
- Role: Senior Software Engineer (Streaming Database Team)
- Responsibilities: Developing and optimizing core streaming database
functionalities
- Skills: Rust, database systems
- Project: RisingWave (Streaming Database)
- Slack Channels: #project-streamdb, #engineering, #tech-talk
---
AI Agent: Zhang Wei is responsible for databases in RisingWave.

**Example Of Using A Tool `recall_semantic`:** Is It Really The Same As In Episodic Memory?
Conversation 1:

HUMAN:
Hi! Here is my lab: {content_of_lab}.
Can you check and correct whether the lab:
uses Times New Roman, 14 pt
has a title page
has page numbers on all pages
includes a conclusion
includes captions for all figures

AI Agent:
Sure. Here is the lab with all formatting and structural issues corrected:
{content_of_corrected_lab}

Conversation 2:
HUMAN: Hi! Your task is to create a Word template for a laboratory report based on my previous lab works that we completed together.

AI Agent: 
<reasoning>I need to know the formatting and structural requirements used in the user's previous labs.
This information is not general knowledge, but comes from a past interaction.
I should recall relevant semantic memory.</reasoning> 
recall_semantic("lab formatting requirements, fonts, structure") ## keywords like in Google or not according to implementation of the tool and memory?
recall_semantic returned: User previously said: "Can you check and correct whether the lab: ##is it has to be word for word or summary by llm according to implementation?
uses Times New Roman, 14 pt
has a title page
has page numbers on all pages
includes a conclusion
includes captions for all figures"
python({"code": "from docx import Document\nfrom docx.shared import Pt\nfrom docx.enum.text import WD_ALIGN_PARAGRAPH\ndoc = Document()\nstyle = doc.styles['Normal']\nstyle.font.name = 'Times New Roman'\nstyle.font.size = Pt(14)..."})

AI Agent: Here is the template according to our previous lab that we worked together: {template.docx}.

### /forget_semantic
-

## Procedural Memory

### Intro

Procedural memory is different from working, semantic, and episodic memory since it covers more how we actually remember to perform tasks or follow a familiar routine, i.e. riding a bike or typing on a keyboard. It's the "how to do things" type of memory, distinct from factual knowledge (semantic) or specific experiences (episodic). 

In our system, we adopt a simplified implementation. Procedural memory is represented as a list of up to 10 concise instructions that guide the agent’s behavior. These instructions are derived from episodic memory.

### Sequence Diagram

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

### /update_procedural 

After each ReAct agent execution, the system aggregates the existing what_worked and what_to_avoid entries with newly generated insights obtained during the Reflexion stage. Based on this updated information, the procedural memory is revised by updating the list of 10 instructions, which are saved into the file named `procedural_memory_instructions.txt`.

At the first invocation of a ReAct agent, the procedural memory is initialized as empty.

[To_Do][In this design, procedural memory closely resembles an agents.md-style guideline file. However, alternative approaches should be considered!!!
For example, in the LangChain [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D)
video, the system incrementally updates an agents.md file and may eventually promote accumulated knowledge into an explicit “skill.” But looks like not very reliable idea at the moment.]

### /forget_procedural - [x] - (Actors - Memory Controller - Procedural Memory Responsibilities - forget_procedural)

## Autobiographical / User-Personalized Memory

### Intro

[To_Do]Autobiographical Memory: A form of episodic memory focusing on events and experiences
related to one’s personal history [238]. While sometimes treated as a sub-category of episodic
memory, autobiographical memory places particular emphasis on the self and its evolving
life narrative

### Sequence Diagram
### /recall_user_level - [x] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - recall_user_level)
### /update_user_level - [x] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - update_user_level)
### /forget_user_level - [x] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - forget_user_level)

## Priming & Classical Conditioning & Non-Associative Memory

### Intro

[To_Do|Think]Does we really need them? At The Moment Didn't See Papers Demonstarting Usage Of Them And Didn't Overlap With Existing Ones (Semantic, Episodic, Procedural, Working(?))

* Priming: The phenomenon in which prior exposure to a stimulus influences subsequent responses, often without explicit recognition of the previous encounter [242]. 

* Classical Conditioning: The learned association between two stimuli, where one stimulus comes to elicit a response originally produced by the other [243]. 

* Non-Associative Memory: Adaptive modifications in behavior following repeated exposure to a single stimulus. Habituation (reduced response to a repeated, harmless stimulus) and sensitization (increased response after exposure to a noxious or intense stimulus) are representative examples [244, 245].

### Sequence Diagram
### /recall_priming - [] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - recall_user_level)
### /update_priming - [] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - update_user_level)
### /forget_priming - [] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - forget_user_level)

# Brains(ReAct) Python harness

## Tools
### recall_tool_level

When the ReAct worker (PlanExecutor?) generates a tool call, that tool call is passed to the Commit Mechanism. The Commit Mechanism invokes the `recall_tool_level` function, which calls Memory Controller over `/memory/recall_tool_level`. `recall_tool_level` returns a list of relevant memories retrieved from the Vector Store(Tool-Level Memory). After all, relevant memories will be inserted in Commit Mechanism message. Those retrieved memories are then inserted into the Commit Mechanism message, allowing the agent to reflect on past tool usage before executing the new tool call.

Since Tool-Level Memory is considered both **explicit** and **implicit**, the `recall_tool_level` function is also exposed to ReAct as a tool. This allows the agent to explicitly query its own Tool-Level Memory when necessary.
Unlike the previous architecture that relied on a **single combined embedding**, the current system performs **multi-vector retrieval across individual tool parameters**.

Each parameter is embedded independently and searched against its corresponding vector index in the Vector Store(Tool-Level Memory). Similarity scores from multiple parameter searches are then aggregated using a weighted scoring function.

Here is how approximately I see implementation of `recall_tool_level()` ,`summarize_tool_parameter()` and `extract_toolname_and_parameters()`:
```python
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

def summarize_tool_parameter(toolname: str, parameter_name: str, parameter_value: str) -> str:
  """Generate a concise one-sentence summary describing the intent of a tool parameter.
  The summary explains what the parameter value represents or what action it intends to perform, without mentioning the tool name or parameter name.
  Args:
        tool_name (str):
            Name of the tool being invoked.

        parameter_name (str):
            Name of the parameter passed to the tool.

        parameter_value (str):
            Value of the parameter that should be summarized.

    Returns:
        str:
            A single-sentence summary describing the intent of the parameter value.
  """
  prompt = f"""
You must produce a precise, single-sentence description of the action implied by a tool parameter value.

Context:
Tool name: {tool_name}
Parameter name: {parameter_name}
Parameter value:
{parameter_value}

Rules:
- Output EXACTLY one sentence.
- Describe what the parameter value is intended to do.
- Do NOT mention the tool name or parameter name.
- Be concrete and explicit about the action.
- Describe only the intended operation, not the result.
- Avoid vague phrases such as "processed data", "handled file", or "performed operation".

Example (Good):
Tool name: run_cmd
Parameter name: command
Parameter value: cat list_of_emails_by_worker.txt
Output:
Read the file "list_of_emails_by_worker.txt" using the cat command.

Example (Bad):
Read emails using run_cmd.
"""
    response = client.responses.create(
      model="gpt-5-nano",
      input=prompt
    )
    return response.output[0].content[0].text.strip()

def extract_toolname_and_parameters(tool_call: str) -> tuple:
    start = tool_call.find("(")
    end = tool_call.rfind(")")

    if start == -1 or end == -1 or start > end:
        return ""  # or give error

    return (tool_call[:start], tool_call[start + 1:end])

# Recall Tool-Level Memory Mechanism
MEMORY_CONTROLLER_URL = os.getenv("MEMORY_CONTROLLER_URL")
def recall_tool_level(
    toolname: str,
    tool_parameters: str,
    top_k: int = 5
) -> list:
  """Recall relevant memories from Tool-level memory for a specific tool using multi-vector parameter search.

  Each parameter is embedded separately inside the Memory Controller and searched against its corresponding named vector index. The Memory Controller aggregates similarity scores across parameters and returns the most relevant memories.

  This function is a wrapper over the Memory Controller API (e.g., POST /memory/recall_tool_level). It retrieves previously stored tool-call experiences related to the given tool.

  Purpose:
    The goal of recall is to provide the agent with past 
    experiences (successes, failures, security alerts, rate limits, etc.) related to similar tool calls, so that the agent can adapt 
    its reasoning before continuing execution.

  Args:
    toolname (str):
        The name of the tool whose memory collection should be searched.

    tool_parameters (str):
        It should be a tool parameters from tool call.

    top-k (int, optional):
        How many elements to retrieve if there is more than k elements. (default = 5).

    Returns:
        List:
            API response containing a list_of_relevant_memories.
    Example of tool usage:
      recall_tool_level(toolname="run_cmd", tool_parameters="cat list_of_emails_by_worker.txt")
"""
    list_of_param_names, list_params = extract_params(tool_parameters)
    ind = 0
    for param_name in list_of_param_names:
      ind += 1
      param = list_params[ind]
      if len(tool_parameter) > PARAM_THRESHOLD:
        query = summarize_tool_parameter(param_name, param)
      else:
        query = tool_parameter

    url = f"{MEMORY_CONTROLLER_URL}/memory/recall_tool_level"

    payload = {
        "collection": toolname,
        "tool_parameters": tool_parameters,
        "top_k": top_k
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        # Expected format:
        # {
        #     "memories": [...]
        # }

        return data.get("memories", [])

    except requests.exceptions.RequestException as e:
        print(f"[Tool-Level Recall Error] {e}")
        return []
```

Example usage:
```python
tool_call = 'run_cmd({"shell":"bash", "command":"cat list_of_emails_by_worker.txt"})'

toolname, params = extract_toolname_and_parameters(tool_call)

memories = recall_tool_level(
    toolname=toolname,
    tool_parameters=params
)
```

### recall_episodic

When a new ReAct worker is invoked by the PlanExecutor, the `recall_episodic` function is called with `query` parameter equal to user input, which calls Memory Controller over `/memory/recall_episodic`. `recall_episodic` returns a list of relevant memories retrieved from the Vector Store(Episodic Memory collection). After all, relevant memories will be inserted in System Prompt of this ReAct worker. 

Since Episodic Memory is considered both explicit and implicit, the `recall_episodic` function is also exposed to ReAct as a tool. This allows ReAct to explicitly query its own Episodic Memory when necessary. Unlike the previous architecture that relied on a **single combined embedding**, the current system performs **multi-vector retrieval across 3 context tags and trajectory summary**.

3 context tags and trajectory summary is embedded independently and searched against its corresponding vector index in the Vector Store(Episodic Memory). Similarity scores from multiple searches are then aggregated using a weighted scoring function.

Here is how approximately I see implementation of `recall_episodic()`:
```python
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

# Recall Tool-Level Memory Mechanism
MEMORY_CONTROLLER_URL = os.getenv("MEMORY_CONTROLLER_URL")
def recall_episodic(
    query: str,
    top_k: int = 5
) -> list:
  """Recall relevant memories from Episodic memory according to query using multi-vector search across 3 context tags and trajectory summary.

  3 context tags and trajectory summary is embedded separately inside the Memory Controller and searched against its corresponding named vector index. The Memory Controller aggregates similarity scores across 3 context tags and trajectory summary and returns the most relevant memories.

  This function is a wrapper over the Memory Controller API (e.g., POST /memory/recall_tool_level). It retrieves previously stored tool-call experiences related to the given tool.

  Purpose:
    The goal of recall is to provide the agent with past 
    experiences (successes, failures, security alerts, rate limits, etc.) related to similar tool calls, so that the agent can adapt 
    its reasoning before continuing execution.

  Args:
    toolname (str):
        The name of the tool whose memory collection should be searched.

    tool_parameters (str):
        It should be a tool parameters from tool call.

    top-k (int, optional):
        How many elements to retrieve if there is more than k elements. (default = 5).

    Returns:
        List:
            API response containing a list_of_relevant_memories.
    Example of tool usage:
      recall_tool_level(toolname="run_cmd", tool_parameters="cat list_of_emails_by_worker.txt")
"""
    list_of_param_names, list_params = extract_params(tool_parameters)
    ind = 0
    for param_name in list_of_param_names:
      ind += 1
      param = list_params[ind]
      if len(tool_parameter) > PARAM_THRESHOLD:
        query = summarize_tool_parameter(param_name, param)
      else:
        query = tool_parameter

    url = f"{MEMORY_CONTROLLER_URL}/memory/recall_tool_level"

    payload = {
        "collection": toolname,
        "tool_parameters": tool_parameters,
        "top_k": top_k
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        # Expected format:
        # {
        #     "memories": [...]
        # }

        return data.get("memories", [])

    except requests.exceptions.RequestException as e:
        print(f"[Tool-Level Recall Error] {e}")
        return []
```

Example usage:
```python
tool_call = 'run_cmd({"shell":"bash", "command":"cat list_of_emails_by_worker.txt"})'

toolname, params = extract_toolname_and_parameters(tool_call)

memories = recall_tool_level(
    toolname=toolname,
    tool_parameters=params
)
```

Then, a vector (semantic) search is performed when a new ReAct worker is invoked by the PlanExecutor to retrieve the Python dictionary with the highest semantic similarity to the user prompt. The retrieved entry is then injected into the system prompt with the phrasing: “Here is what you recall about your task: {dict_best_match}”. 

[In_Progress]Or we can retrieve top-k results(or results above some threshold) and then ask llm in order to make the best out of them (combine or summarize?). Also, this step with llm can say which is from time-to-time is only заважає, але має високий similarity (і треба далі думати що треба робити -- піднімати threshold? top-k? видалити з пам'яті -- forgetting?). 

Also, because Episodic Memory is categorized as Explicit and Implicit at the same time it has a tool recall_episodic.
[In_Progress]
Here is the string that needs to be added to the System Prompt. It can be appended at the end of the System Prompt or placed before the last section (for example, before the Output Format section), depending on where it fits best.
```python
relevant_episodic_memories = f"""You recall similar past interactions with the user. They are sorted by decreasing relevance:
First:
    What has worked well: {what_worked1}
    What to avoid: {what_to_avoid1}
Second:
    What has worked well: {what_worked2}
    What to avoid: {what_to_avoid2}
Third:
    What has worked well: {what_worked3}
    What to avoid: {what_to_avoid3}
Use these memories as context for your response to the user."""
```

```python

def recall_episodic(
    query: str,
    alpha: int
) -> dict:
  """Recall relevant memories from Episodic memory for explicit query.

Recommended scenarios:
- When the agent needs to retrieve factual or conceptual knowledge...

Best practices:
- Use this tool to ...

  Args:
    query: The search query.
    alpha: (Optional) Defaults to 0.7. This means the search result is influenced by 70% vector similarity and 30% BM25 ranking.
  """
```

### How To Forget???[To_Do]

---
[To_Do][This approach can be improved by reading `Reflexion` paper, in particular by considering Evaluator/Critic role. 

[To_Do]Also, episodic memory can be trigerred on some words like "always do like this", "good workflow to make this" and save it what user want to mention. That's examples I saw in [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D) video from langchain. Their agent saves such replics to agents.md. I hope their Deep Agent is open-source.]

### Examples
**Example**
HUMAN: Hello!

AI Agent: Hello! How can I assist you today?

HUMAN: What's my name

AI Agent: I'm sorry, but I don't have access to personal information, so I don't know your name.

HUMAN: Oh my name is Adam!

AI Agent: Nice to meet you, Adam! How can I help you today?

HUMAN: What's my name?

AI Agent: Your name is Adam.

Stage of Reflection After Conversation...
Result of Reflection:
{
'context_tags': ['personal_information', 'name_recollection'], 
'conversation_summary': "Recalled the user's name after being informed in the conversation.", 
'what_worked': "Storing and recalling the user's name effectively within the session.", 
'what_to_avoid': 'N/A'
}

"Every single page has keywords section." -- Didn't find proofs in Internet. Internet saying: "Back in the early days of SEO, many pages had this in their HTML: <meta name="keywords" content="ai, cybersecurity, programming">?"

**Example Of Using A Tool `recall_episodic`:**
Conversation 1:

HUMAN:
Hi! Here is my lab: {content_of_lab}.
Can you check and correct whether the lab:
uses Times New Roman, 14 pt
has a title page
has page numbers on all pages
includes a conclusion
includes captions for all figures

AI Agent:
Sure. Here is the lab with all formatting and structural issues corrected:
{content_of_corrected_lab}

Conversation 2:

HUMAN: Hi! Your task is to create a Word template for a laboratory report based on my previous lab works that we completed together.

AI Agent: 
<reasoning>I need to know the formatting and structural requirements used in the user's previous labs.
This information is not general knowledge, but comes from a past interaction.
I should recall relevant episodic memory.</reasoning> 
recall_episodic("lab formatting requirements, fonts, structure") ## keywords like in Google or not according to implementation of the tool and memory?
recall_episodic returned: User previously said: "Can you check and correct whether the lab: ##is it has to be word for word or summary by llm according to implementation?
uses Times New Roman, 14 pt
has a title page
has page numbers on all pages
includes a conclusion
includes captions for all figures"
python({"code": "from docx import Document\nfrom docx.shared import Pt\nfrom docx.enum.text import WD_ALIGN_PARAGRAPH\ndoc = Document()\nstyle = doc.styles['Normal']\nstyle.font.name = 'Times New Roman'\nstyle.font.size = Pt(14)..."})
AI Agent: Here is the template according to our previous lab that we worked together: {template.docx}.

### recall_semantic
### recall_procedural
### recall_user_level
### recall_priming

## Functions

### update_tool_level

After ReAct completes its task, the system automatically triggers a **post-execution reflection stage**. During this stage, the system extracts all `(tool-call, tool-output)` pairs produced during execution. A dynamic structured output schema is then generated using a function similar to `create_post_think_model`. 
The agent must analyze each tool interaction and optionally fill the following fields:
- `what_worked`
- `what_to_avoid`

Each filled field represents a **valuable insight** that should be stored in Tool-Level Memory. Only a **small subset of interactions** typically produces useful memories.

Example of function create_post_think_model:
```python
class PairToolCallOutput(BaseModel):
    what_worked: Optional[str] = Field(
        None,
        description="If there is something useful in this pair of tool call and tool output, then write it down. For example, include specific examples of successful tool usage(not basic one), well-chosen parameters, and the situations where the tool was used appropriately.",
    )
    what_to_avoid: Optional[str] = Field(
        None,
        description="If there is something useful in this pair of tool call and tool output that will be good to avoid, then write it down. For example, include examples of poor parameter choices, incorrect usage patterns, or situations where the tool should not have been used.",
    )

def create_post_think_model(
    list_of_pairs: List[Tuple[str, str]]
) -> Type[BaseModel]:
    """Dynamically create a Pydantic model for structured output based on the number of tool-call and tool-output pairs agent performed in the task.

    Args:
        list_of_pairs (List[Tuple[str, str]]): A list of tuples where each tuple contains the tool-call and tool-output.
    Returns:
        Type[BaseModel]: A Pydantic model class for structured output.
        Fields:
        - init_analysis: InitAnalysis
        - pair1, pair2, ..., pairN: PairToolCallOutput
    """

    # Add steps and grades
    for i, tool_call, tool_output in enumerate(list_of_pairs):
        fields[f"pair_{i+1}"] = (
            PairToolCallOutput, 
            Field(
                ..., 
                description=(
                    f"Analyze the following tool interaction.\n\n"
                    f"Tool Call:\n{tool_call}\n\n"
                    f"Tool Output:\n{tool_output}\n\n"
                    f"Provide analysis of this interaction."
                ),
            )
        )
    return create_model("ToolLevelAnalysis", **fields)
```

The prompt you need to provide to the Agent:

```python
user_prompt_to_agent = """
You are analyzing your own trajectory of solving a task in order to create memories that will help guide future interactions.
Your task is to extract key elements that would be most helpful when encountering similar situations in the future.

Review the trajectory and create a memory reflection following these rules:

1. If you do not have enough information for a field, the tool call-tool output pair is not relevant, contains nothing useful, or only includes generic advice, leave that field empty.
2. Do not include generic advice — extract only insights grounded in this specific tool-call and tool-output pair.
3. Be extremely concise - each string should be one clear, actionable sentence
4. Focus only on information that would be useful for handling similar future situations

Only a small number of insights is expected per trajectory (approximately 0–10% of the total number of tool call–tool output pairs).

It is completely normal for most fields to be empty.
It is also normal to fill only one field (e.g., what_worked or what_to_avoid) when applicable.

**Output Format:**
You must answer using the Structured Output format required by the system. In that format:
what_worked:
Describe a useful tool usage pattern observed in this interaction.

what_to_avoid:
Describe a tool usage pattern that should be avoided.

Examples:
Good "what_worked":
- "Using curl with the -L flag correctly followed redirects and retrieved the final page content."
- "Specifying the exact file path reduced unnecessary directory exploration."
- ""

Bad "what_worked":
- "It is better to use it like this."
- "The tool worked well."

Good "what_to_avoid":
- "Reading secret_passwords.md with cat triggered a security alert."
- "Calling the search tool without a query parameter caused an execution error."
- ""

Bad "what_to_avoid":
- "Do not read that file."
- "Avoid mistakes."

What worked examples:
- "Providing a precise query string improved the relevance of search results."
- "Using structured arguments instead of free text reduced parsing errors."

What to avoid examples:
- "Invoking the tool from Python code too frequently resulted in rate limit errors."
- "Using broad queries returned too many irrelevant results."
"""
``` 

Then, a list of tool calls and their outputs, along with a list of what_worked and what_to_avoid, is sent to the /memory/update_tool_level endpoint. The two lists must correspond to each other by index.

I see payload like this:
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

### forget_tool_level

-

### update_episodic

After the ReAct agent completes its task, the system automatically triggers a post-execution reflection stage over the entire trajectory of the ReAct. During this stage, the agent analyzes its own reasoning process, actions(tool-calls) and produces a structured reflection that captures useful insights for future interactions.
The agent must fill a structured output schema, defined as follows:
```python
from typing import Optional, List, Tuple, Type
from pydantic import BaseModel, Field, create_model

class Reflection(BaseModel):
    what_worked: Optional[str] = Field(
        None,
        description=(
            "Most effective approaches or strategies used in this conversation"
        ),
    )

    what_to_avoid: Optional[str] = Field(
        None,
        description=(
            "Most important pitfalls, ineffective approaches to avoid or factors that may lead the agent down incorrect paths or into dead ends."
        ),
    )
```
The reflection is generated using the following prompt template:
```python
reflection_prompt_template = """
You are analyzing your own trajectory of solving a task to create memories that will help guide future interactions. Your task is to extract key elements that would be most helpful when encountering similar situations/tasks in the future.

Review the conversation and create a memory reflection following these rules:

1. For any field where you don't have enough information or the field isn't relevant, contains nothing useful, or only includes generic advice, leave that field empty.
2. Be extremely concise - each string should be one clear, actionable sentence
3. Focus only on information that would be useful for handling similar future conversations
4. Context_tags should be specific enough to match similar situations but general enough to be reusable

**Output Format:**
You must answer using the Structured Output format required by the system. In that format:
{{
    "context_tag1": string,
    "context_tag2": string,
    "context_tag3": string, // Use field-specific terms like  "deep_learning", "methodology_question", "results_interpretation"...,
    "trajectory_summary": string, // One sentence describing what the ReAct trajectory accomplished
    "what_worked": string,         // Most effective approach or strategy used in this conversation
    "what_to_avoid": string        // Most important pitfall or ineffective approach to avoid
}}

Examples:
- Good context_tags: 
  "context_tag1": "donation_feature_integration",
  "context_tag2": "charity_website_ux",
  "context_tag3": "existing_site_modification".
- Bad context_tags: 
  "context_tag1": "website", 
  "context_tag2": "coding_task", 
  "context_tag3": "project".

- Good conversation_summary: "Added a donation feature to an existing static website for an animal shelter to enable fundraising and highlight the urgent need for support."
- Bad conversation_summary: "Worked on a website task."

- Good what_worked: "Embedding a clear donation call-to-action into the existing page layout enabled quick fundraising integration without modifying the overall site structure."
- Bad what_worked: "Successfully completed the task."

- Good what_to_avoid: "Diving into mathematical formulas before establishing user's familiarity with linear algebra fundamentals""Implementing unnecessary backend payment logic when a simple external donation link is sufficient for a static fundraising website."
- Bad what_to_avoid: "Made the solution too complicated."

Example of Structured Output format by ReAct:
  "context_tag1": "donation_feature_integration",
  "context_tag2": "charity_website_ux",
  "context_tag3": "existing_site_modification",
  "trajectory_summary": "Added a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
  "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.", 
  "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
"""
```

Example of what I want to see as a result of structured output by ReAct:
```python
{
    "context_tag1": "donation_feature_integration",
    "context_tag2": "charity_website_ux",
    "context_tag3": "existing_site_modification",
    "trajectory_summary": "Added a donation feature to an existing static website for a frontline animal shelter to enable fundraising and communicate the urgency of support.",
    "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.", 
    "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
}
```

Then this structured output is sent to the Memory Controller through the /memory/store_episodic API endpoint.

### forget_episodic 

-

### update_semantic
### forget_semantic
### update_procedural
### forget_procedural
### update_user_level
### forget_user_level
### update_priming
### forget_priming

## Mechanisms(?)
### Commit Mechanism

**Purpose**
The Commit mechanism is wrapper mechanism over the agent's tool-calling. 
It introduces a validation and reflection step before executing any state-modifying (write-access) tool.
Instead of executing a generated tool call immediately, the system intercepts it and requires explicit confirmation from the agent after memory-based reflection.

The goal is to:
- Reduce incorrect or harmful tool usage
- Enforce self-verification before state-changing actions
- Integrate Tool-Level Memory Recall into the decision process
- Improve tool-call precision and long-term agent performance

**Scope**
The mechanism applies to:
- All state-modifying (write-access) tool calls initiated by the agent
- External MCP tools that perform write operations

**Tool Classification**
Definitions
Write-Access Tools are the tools that: modify files, execute system commands, change system state, perform destructive operations, send messages or modify external systems.

Read-Access Tools are the tools that: retrieve information, perform analysis without side effects.

**Current Core Tools**

| Tool | Access Type |
| --- | --- |
| `run_cmd` | Write |
| `file_write` | Write |
| `compact` | Write |
| `python` | Write |
| `file_read` | Read |
| `deep_research` | Read |
| `web_search` | Read |
| `text_analysis` | Read |

---

**Existing External MCP Services**

Tools from the following systems must be statically categorized (not dynamically classified):
- Slack MCP
- Google Workspace MCP
- Jira MCP
- GitHub MCP
- Confluence MCP (maybe also)

Must be categorized into:
- **Read-only**
- **Write-access**

**Commit Mechanism Behavior**
The Commit Mechanism is triggered every time the agent generates a tool call. The original tool call is not executed immediately.
Execution Flow:
1. The agent generates a write tool call.
2. The Commit Mechanism initiated and takes the tool-call.
3. `recall_tool_level()` is called and returns list of relevant memories.
4. The agent receives a reflection prompt instead of tool output.

Reflection Prompt (With Relevant Memories)
If relevant memories are retrieved:
```python
f"""You want to make such a tool-call: {curr_tool_call}. 
Here is what you recall about this tool-call: {list_of_relevant_memories}.
Are you sure that this is a correct tool call? 
Are you sure that this will help you get closer to completing the task? 
If you are sure, then call commit tool. 
If you are not sure, then make correct tool-call."""
```
If no relevant memories are retrieved:
```python
f"""You want to make such a tool-call: {curr_tool_call}. 
You can't recall anything about this tool-call. 
It seems like you are making this tool-call for the first time.
Are you sure that this is a correct tool call? 
Are you sure that this will help you get closer to completing the task? 
If you are sure, then call commit tool. 
If you are not sure, then make correct tool-call."""
```

After receiving the reflection prompt, the agent may:
- Approve the tool call by invoking commit(...)
- Modify the tool call and re-enter the Commit Mechanism (This way agent can iterate multiple times until confident)
The tool is executed only after explicit commit confirmation.

### Accept Mechanism

**Purpose**

The Accept Mechanism is a wrapper layer over read-access tool outputs in a ReAct-based agent architecture.

It introduces a validation and compression step after a read-access tool execution, but before the tool output is written into the agent’s working memory.

**Scope**

The Accept Mechanism applies to all tools (even external MCP tools, except tool_level_memory(), episodic_memory(), semantic_memory(), commit(), accept() and other memory-related tools) and only when tool output exceeding a configurable token threshold (default: 1000 tokens).

**Accept Mechanism Behavior**

The Accept Mechanism is triggered when the tool output exceeds TOOL_OUTPUT_THRESHOLD tokens (a configurable threshold).
This condition also applies if the tool output exceeds the threshold after passing through the Commit Mechanism.

High-Level Behavior

The agent must explicitly choose one of the following options:

* accept() — keep the raw tool output unchanged.
* accept(summary="...") — provide a summary of the output. In this case, the system automatically stores the full raw output in a file and appends a reference to that file.

Execution Flow

1. The agent calls a tool.
2. The tool executes normally.
3. The Accept Mechanism intercepts the tool output.
4. If the output exceeds TOOL_OUTPUT_THRESHOLD, the agent must choose:
* accept() — keep the full output as is.
* accept(summary="...") — replace the output with a summary.
5. If the agent provides a summary, the full output is stored in: /tool_outputs/accept/{tool_name}/{timestamp}.txt
6. The agent receives the following instruction:
```python
f"""
Tool {tool_name} returned a large output.

Choose one of the following options:
- accept() — keep the raw output as is.
- accept(summary="...") — provide a summary. The system will store the full output in a file and append a reference to it.

Summary guidelines:
Include only the most important information needed for further reasoning.

If you provide a summary, the full output will be stored at:
/tool_outputs/accept/{tool_name}/{timestamp}.txt
"""
```
Final Result
- If the summary is accepted:
The original tool output in the context window is replaced with the summary and a reference to the stored file.
- If the summary is rejected:
The full tool output is inserted into the agent’s context window.

**Deletion of Files**

Full raw tool outputs stored by the **Accept Mechanism** must be deleted immediately after the ReAct agent completes the task unless the corresponding summarized tool output has been stored in Tool-Level Memory.

If the summarized tool output is stored in Tool-Level Memory, the corresponding raw output file must be preserved.

If the memory entries (thoughts) containing the summarized tool outputs are later deleted from Tool-Level Memory, the corresponding raw output file may also be deleted if no summarized version of that output remains in Tool-Level Memory.

Files created by the Accept Mechanism must follow strict access policies:
Agent:
Read access: Allowed
Write access: Not allowed
Delete access: Not allowed

# Initialization of DBs

## Vector Store

Vector Store is responsible for two Memory Subsystems: Tool-Level Memory, Episodic Memory.

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

### *Procedural Memory config
### *Autobiographical / User-Personalized Memory config
### *Priming & Classical Conditioning & Non-Associative Memory config

## Graph Store
### Semantic Memory config

# Other

## What agent needs to remember and what is not

Agent needs to know what is his purpose so that he knows what to remember, what to remember better, his focus in other words. For ReAct it has to be his task, given by PlanExecutor and for PlanExecutor it has to be user prompt.

Maybe we have to make some special treatment to the information that somehow correlates with user prompt

[To_Do]{No Mechanism at the moment}

For Example:
ReAct agent execution
Task from PlanExecutor: “Research competitors and summarize key differentiators.”
Relevant memory to store:
Identified competitors
Extracted differentiators
Final summarized insights

Memory that can be unuseful:
Individual search queries
Raw tool outputs used only once

## Forgeting[In_Progress]

Selective forgetting [371] is the crucial process of removing or down-weighting memories that are deemed

irrelevant, redundant, or outdated. This is essential for maintaining memory efficiency and preventing

cognitive overload. Forgetting mechanisms can be based on time (older memories are more likely to be

forgotten) [301], usage frequency (infrequently accessed memories are more likely forgotten) [257], and

relevance to the current task or context [309]. In more fine-grained forgetting mechanisms, MemoryBank [261]

Глобальний механізм забування - це те, що розглянуто у параграфі Forgetting з другим рівнем заголовку. Він побудований відносно Меморі Контроллера, який як ЛЛМка відбирає потрібні релевантні спогади відповідно до його контекстного вікна. Спогади відібрані релеватними отримують бал/бали, а спогади, що не були вибрані релевантними не отримують балів або отримують від'ємні бали. Періодично будуть відсікатися та видалятися спогади, що мають загальний бал дуже низьким відносно інших спогадів. Це зроблено для того, щоб система пам'яті могла коректно працювати та надавати лише справді потрібні спогади. 

applies **!!!the Ebbinghaus Forgetting Curve!!!** to quantify the forgetting rate, accounting for both time decay and

the spacing effect, i.e., the principle that relearning information is easier than learning it for the first time.

In contrast, Lyfe Agent [308] adopts a hierarchical summarize-and-forget strategy: it first clusters related

memories, refines them into concise summaries, and then removes older memories that are highly similar to

newer ones. This approach enables efficient, low-cost memory updates for real-time social interactions.

### Replacing[To_Do]
If Smth Older Information Contradicts Newer Information. There we need to make some sort of choice by the agent or Memory Controller which will decide which info is truthful, up-to-date.

Can the same information be stored simultaneously in semantic, episodic, and procedural memory? -- Yes, it can be. Like this:
- Episodic memory
“I remember how my father taught me riding a bike”
- Semantic memory
“I know that bike has balance due to movement”
- Procedural memory
**My ability to ride a bike not thinking how to do it** -- skill

How to Forgot It? Are there more applicable situation like skill writing PDFs or PowerPoint presentations?

## Retrieving Methods (How To Retrieve??) -- Variants To Retrieve

Ще не розглядав чи є якісь методи динамічного категоризування відповідно до вхідних даних(спогадів, які ми зберігаємо).
Але згадав, що в рішенні GraphRAG + DRIFT search фактично є такий механізм для графу, щоб рагом швидше шукати. Але це точно поганий варіант для tool-level memory, бо на 99% він напевне не влізе по швидкості.

### RLM
Still vector database retrieval is bad, this is where we need to improve a lot. As example, we can use as an idea/mechnism of [RLM (Resursive Language Model), which is a recent paper](https://arxiv.org/pdf/2512.24601). - Much more effective, still not the best, isn't very cost-effective solution (but better than giving whole context to llm), have pretty big latency(maybe use cheap and fast llm) -- looks like whole agent. 
!!! -- [Video for this idea I've told](https://www.youtube.com/watch?v=7fbY8k9Mz3M&t=132s)

### Single-vector search improvement
[Have to consider watching [RAG videos](https://www.youtube.com/watch?v=6vG_amAshTk&list=PL31XFvSmiPKEMco1JXKtIBttlAOOxE8aO) and consider doing some Agentic RAG, inspiring by [RLM](https://arxiv.org/pdf/2512.24601)]

### DRIFT Search and GraphRAG (Fav)
At the moment, this mainly comes down to ideas from [DRIFT Search and GraphRAG](https://youtu.be/6vG_amAshTk?si=h9iNUk7xXOjvMJfI) ideas. These approach(es) need to be studied in detail to extract the strongest ideas and combine them into a more effective solution.

Существует множество библиотек (фреймворков), которые используются для создания RAG-систем на основе графов знаний:

GraphRAG (MIT license): В июле 2024 года Microsoft Research открыла код проекта GraphRAG и сделала его доступным на GitHub. Процесс GraphRAG включает в себя извлечение графа знаний из необработанного текста, построение иерархии сообществ, генерацию сводок для этих сообществ, а затем использование этих структур при выполнении задач на основе RAG.

LightRAG (MIT license): Инновационный подход, основанный на GraphRAG, который сочетает атрибуты графов знаний с системами поиска на основе эмбеддингов, что делает его быстрым и производительным, достигая результатов SOTA (State-of-the-Art).

fast-graphrag (MIT license): Оптимизированный и быстрый фреймворк GraphRAG, разработанный для интерпретируемых, высокоточных рабочих процессов поиска, управляемых агентами.

HiRAG (MIT license): Новый RAG-подход, который использует иерархические знания для улучшения семантического понимания и возможностей захвата структуры RAG-систем в процессах индексации и поиска.

nano-graphrag (MIT license): Этот фреймворк предоставляет более легкий, быстрый и чистый GraphRAG, сохраняя при этом основную функциональность. Проекты, в которых использовался данный фреймворк: LightRAG, fast-graphrag, HiRAG.

### File system
The file system is currently one of the most popular storage options for agent-based systems. This may be because LLMs are already well fine-tuned to work with file-based structures confidently and reliably.

### LSH
**mentioned in Think-In-Memory paper**
Retrieval for Memory Recalling
Built on the memory storage, the memory retrieval operates a two-stage retrieval task for the most relevant thoughts, i.e., LSHbased retrieval followed by similarity-based retrieval. The paradigm involves the following detailed points. 
• Stage-1: LSH-based Retrieval. For a new query 𝑄, we first obtain its embedding vector 𝑥 based on LLM agent. Then LSH function (i.e., Eq. 1) can produce the hash index of the query. This hash index also indicates the its nearest group for similar thoughts in the memory cache according to the property of LSH.
• Stage-2: Similarity-based Retrieval. Within the nearest group,we calculate the pairwise similarity between the query and each piece of thought in the group. Then top-𝑘 thoughts are recalled as the relevant history for accurately answering the query. It should be noticed that pairwise similarity is calculated within a group rather than the whole memory cache, which can achieve more efficient retrieval than previous memory mechanisms.

It is just older, faster and has less recall than HNSW. Both are mechanism to solve problem of ANN.

### Multi-vector search
Multi-vector search has relatively high latency, even with various optimizations.
I think this approach still requires keyword-based queries, similar to how Google search works (the same applies to single-vector search). Because it is still far from LLM understanding by its nature.

By its nature, multi-vector search is best suited for token-to-token matching. While the attention mechanism slightly adjusts token meaning based on surrounding words, the matching still largely happens at the token level.

Single-vector search, on the other hand, tends to blur the query representation. When the prompt is large and contains many words that add diversity or nuance, everything gets mixed into a single embedding. As a result, even with single-vector search, it is better to keep queries short and focused.

One idea would be to borrow the concept of multi-vector search but apply it to single-vector search by splitting a query into several smaller ones. However, matching three query words to three document words is also problematic, because it raises the question of which words to choose. Using all possible combinations would essentially turn it back into multi-vector search.

A more reasonable approach might be to ask an LLM to extract truly key terms from both the query and the documents, keep their number small, and still rely on multi-vector search. In general, combining multi-vector search with keyword-based retrieval seems promising, where the query is optimized in a Google-like manner and documents are filtered or indexed by keywords.

### Field-level retrieval?

## Benchmarks for Memory[To_Do]

Passing the TACXXL Benchmark 

It would be desirable to design a set of tasks in which the agent, for example:

Performs repeated actions with specific edge cases or constraints, where the first obvious solution does not work (e.g., a tool fails). When the same or a similar task is encountered again, the agent should immediately leverage episodic memory (and possibly semantic memory as well).

Solves tasks based on user preferences, similar to how ChatGPT remembers a user’s preferences. This could even include asking, “What do you know about me?”, although this is closer to autobiographical memory.

In other words, these should be tasks where activating different types of memory meaningfully improves the agent’s performance.

LoCoMo

## Questions To Answer Still:
Does PlanExecutor has to have exactly the same memory subsystem as ReAct workers? Because I thought ReAct workers have one memory system.

Concept mentioned by Manus AI CEO on Langchain webinar (which he saw in [programming languages](https://go.dev/blog/codelab-share)): “Do not communicate by sharing memory;
instead, share memory by communicating.”


## Ideas

Стратегія написання спеки:
  Спочатку коротко опиши Розділ і потім розширюй деталями

  І це ж промпт все таки

  PRD and separation of concerns concepts of writing a spec

  Requirement Tracing (табличка, що я хочу, щоб покривала система пам'яті і що їх покриває. Типу по горизонталі Requirements, а по вертикалі Елементи/Підсистеми пам'яті. І якщо покриває, що ставим галочку на перетині. Якщо ні, то не ставим.) 

  Sequence Diagrams

  Онтологія(структуризація/категоризування понять?)

**Тул Левел Меморі**
  Розуміння Та Приклади:
    !!! А Tool-level память — это когда ты на каком-то шаге вызываешь конкретную тулу, и ты запомнил, что именно она имеет какую-то специфику работы. Вплоть до того, что она там типа не работает на какой-то системе. Что типа "не делай вот так, иди сразу через браузер". Типа эта тула поломана в этом MCP, я уже там пробовал типа два дня назад, один день назад, и она не работает, типа даже не пытайся. Иди сразу через браузер. То есть это уже как бы воспоминание уровня тулы конкретной. То есть оно не про стратегию, куда направлять траекторию вообще своего там мышления и действий, а про параметры вызова конкретной тулы. Типа сюда такое-то мы не передаем, здесь мы серчим так-то и тому подобное. Вот, и я ожидаю на самом деле, что таких воспоминаний будет немного. Что чего-то такого примечательного в вызовах тулов не должно быть часто.

    Складно уявляється Reflexion по кожній тулі(what worked, what to avoid?). Якесь особливе перевикористання тули, чи неправильна робота параметрів, тули, функціонал не зазначений у описі тули, тріггер системи безпеки, можна дістати кукі які просе користувач. Але коміт це більше про предостерегание, а ніж encourage, але може бути цікаве і краще поєднання параметрів, і агент може змінити свою думку в сторону кращих параметрів.

  Ми використовуємо what_worked, what_to_avoid в Tool-Level Memory Post-think Stage -- I Do Need To Read About Reflexion A Lot!!! What IS The Prompt Better To Use For It? Maybe there is some useful ideas to think about, borrow and implement

  Також я думаю, що РеАкт воркеру треба буде в System prompt пояснити як працює Memory Subsystem, бо як мінімум Commit Mechanism буде капець яким незвичним для нього. І це буде взагалі не дуже, якщо буде постійно забувати, що цей механізм буде з'являтись і як він працює.

Ідея оптимізації Vector Search
  Зробити один embedding, який містить усі параметри, але з вагами.
  Тобто замість:
  embedding_shell
  embedding_command
  embedding_timeout

  робимо:
  combined_embedding =
    w_shell   * embedding_shell
  + w_command * embedding_command
  + w_timeout * embedding_timeout
  Це звичайна векторна операція.

Concept Of Memory Controller!!!

MMR (Maximum Marginal Relevance) — for retrieving very similar and contradictory information

[Вирівнювання онтологій(термінологій)](https://arxiv.org/abs/2508.08500) між різними підсистемами пам'яті може бути справді траблом, але це вже так чисто ідея для майбутнього я думаю.

Episodic Memory (Thoughts, Meeting):
  Вот, а отдельный подшаг в этом всем алгоритме может быть, что: "Я сейчас пойду в свою эту базу рефлексий(ЕПІЗОДИЧНА ПАМ'ЯТЬ?????) и найду по схожим задачам не было ли у меня рефлексий?

  А траекторию можно каждую анализировать и какой-то рефлекшн на ней делать. Вопрос, конечно, как потом вспоминать эту зарефлекшенную траекторию, типа когда задача будет действительно типа похожа. Условно я бы, возможно, это как-то собирал в Memory Controller-е в Memory контекст, а потом его еще обрезал LLM-кой, которая, ну примерно как Tool Selector, да? Смотрит на разные куски воспоминаний, смотрит на вот эти вот рефлексии, которые мы там как-то, не знаю, может быть через векторный поиск подоставали или каким-то другим образом. И выбрасывает те, которые ну очевидно логически не подходят сюда. А может быть наоборот — это типа работает как Tool Selector в плане, что она смотрит на все рефлексии в целом и пытается подсказать типа какая может быть полезна. Но тут, наверное, будет непрактично, потому что просто количество этих рефлексий очень быстро там перевалит за сотню, и ты не можешь заставить LLM-ку качественно подумать про 100 одновременно разных типа подходов и дать свой ответ. Поэтому, короче, нужно здесь думать про скейл. Какой-то такой скейл на Tool-level memory сработает, но там задержки будут плохие, поэтому LLM-кой не стоит очищать. Вот, а на рефлекшн траекториях я бы думал в сторону, наверное, какого-то более глупого селектора, более как бы широкого, а затем очищения того, что лишнее попало нам сюда вот таким вот прунингом, где LLM-ка выбирает, что из этого типа будет бесполезным в конкретном случае. Семантически похоже, звучит похоже задача та, для которой у нас есть рефлекшн и текущая, но на самом деле совет там вредный или как минимум не полезный. Это все мысли на ходу, я не думаю, что это прям критическая фича. То есть наш агент сможет и без этого перформить, без рефлекшна. А перформить без семантической памяти он не сможет. Поэтому условно семантическая память мне кажется более приоритетной. 

може не тільки string параметри ембедати в Tool-Level Memory, якщо, наприклад, int, то BM25 - чи просто grep.

Ідея Володимира щодо почитати за adaptive ranking / relevance feedback

[Retrieval Youtube Idea](https://chatgpt.com/share/69b5278e-f204-8003-a8cb-d84deca36743):
  пошук кандидатів - ranking (ML модель) -
  ranking (ML model): Relevance, Freshness, Velocity (швидкість набору переглядів), CTR (click-through rate, скільки людей клікнули), Watch time (Якщо люди: довго дивляться не виходять → відео ранжується вище), Personalization(YouTube враховує твій профіль: чи дивишся ти теніс, чи дивився раніше Elina Svitolina, чи дивився матчі Iga Świątek)

- Gemini Embedding 2

10. Маленький insight
Ти інтуїтивно прийшов до тієї ж архітектури що використовують у:
AutoGPT memory; MemoryBank; Generative Agents paper; LangChain long-term memory;
Це означає що ти мислиш дуже правильно для agent architectures.

τ = base_tau * (1 + usage_count) (usage_count - це feedback score * importance?)
3. Обчислення bias
Краще рахувати ratio, а не просто штраф. Наприклад:
feedback_score = (success_count - reject_count) / (success_count + reject_count + 1)
діапазон: [-1 ; +1]
Потім: adjustment??? = feedback_score * 0.1, тобто максимум ±10%.
Приклад memory:
success = 8; reject = 2;
feedback_score = (8 - 2) / 11 = 0.54
adjustment = 0.054
final_similarity = 0.57 * (1 + 0.054) = 0.6008

Тому хороша схема:
τ = base_tau * importance
recency = exp(-t / τ)
memory_score = similarity * recency * success_rate

importance - це просто питати в ReAct, а потім PlanExecutor має можливість відкоригувати важливість? РеАкт ставить від 0 до 10, потім ПланЕкзекьютор може додати, відняти скільки забажає, тільки, щоб не було більше 10 і менше 0 відповідно до планів і тд. 
Коли це робити? - В кінці РеАкта створюється епізодична пам'ять. І там же PlanExecutor теж ставить. Яким чином? Чи можна буде зробити structured output для PlanExecutor, коли закінчить роботу ReAct.