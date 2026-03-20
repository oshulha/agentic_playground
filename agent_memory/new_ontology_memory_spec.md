# My Memory Conceptual Architecture v1.2

Memory subsystem is the information storage and retrieval part of our AI Agent. It consists of a [not_sure]vector store that contains several collections, graph store and other storages for the best possible retrieval. It directly interacts with the Brains subsystem (PlanExecutor and ReAct) and operates at multiple levels, such as storing memories from the [not_sure]PlanExecutor as well as memories from each ReAct worker invoked by the PlanExecutor. At the moment, our Memory subsystem is composed of [not_sure]six underlying memory components:  tool-level, episodic, semantic, procedural memory, user-personalized memory, priming & classical conditioning & non-associative memory.

[old?]**Memory Architecture Diagram:**
![Memory Architecture Diagram](memory_schema.png)

# Table Of Contents

[**Overall Sequence Diagram**]()

[**Brains(ReAct) Python harness**](#brainsreact-python-harness)
<br/>Progress: [██████████] 99%; Status: Done  
Short description: _TODO

- [**Tools**](#tools)
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**recall_episodic**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

  - [**recall_tool_level**]()
    <br/>Progress: [██████████] 99%; Status: Done  
    Short description: _TODO

- [**Functions**](#functions)
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_episodic**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_episodic**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**update_tool_level**]()
  <br/>Progress: [██████████] 99%; Status: Done  
  Short description: _TODO

  - [**forget_tool_level**]()
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

  - [**Sequence Diagram**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_tool_level**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_tool_level**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_tool_level**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

- [**Episodic Memory**](#episodic-memory)
<br/>Progress: [███░░░░░░░] 30%; Status: In Progress   
Stores past experiences and task executions. Includes structured reflections such as `what_worked`, `what_to_avoid`, summaries, and context tags.

  - [**Sequence Diagram**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_episodic**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_episodic**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_episodic**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

- [**Semantic Memory**](#semantic-memory)
<br/>Progress: [███░░░░░░░] 30%; Status: In Progress   
Represents structured factual knowledge and concepts. Implemented through RAG-style retrieval from vector databases or knowledge sources.

  - [**Sequence Diagram**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_semantic**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_semantic**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_semantic**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

- [**Procedural Memory**](#procedural-memory)
<br/>Progress: [██░░░░░░░░] 20%; Status: Done(v1)   
Encodes behavioral rules and execution strategies. Derived from episodic reflections and stored as concise operational instructions.

  - [**Sequence Diagram**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_procedural**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

  - [**/update_procedural**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_procedural**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

- [**Autobiographical / User-Personalized Memory**](#autobiographical-memory----user-personalized-memory)
<br/>Progress: [█░░░░░░░░░] 10%; Status: To Do   
Specialized form of episodic memory focused on user-specific patterns, preferences, and long-term identity modeling.

  - [**Sequence Diagram**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_user_level**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

  - [**/update_user_level**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_user_level**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

- [**Priming & Classical Conditioning & Non-Associative Memory**](#priming--classical-conditioning--non-associative-memory)
<br/>Progress: [█░░░░░░░░░] 10%; Status: To Do   
Exploration of cognitive-inspired mechanisms and whether they are practically needed in agent systems.

  - [**Sequence Diagram**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/recall_priming**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO

  - [**/update_priming**]()
  <br/>Progress: [█████████░] 90%; Status: Done  
  Short description: _TODO   

  - [**/forget_priming**]()
  <br/>Progress: [█████████░] 90%; Status: Done   
  Short description: _TODO

[**Initialisation of DBs**]()
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



# Brains(ReAct) Python harness

## Tools
### recall_episodic - [] - (Types Of Memory - Episodic Memory - How To Retrieve)
### recall_tool_level - [] - (Types Of Memory - Tool-level Memory - How To Retrieve)

## Functions
### update_episodic - [] - (Types Of Memory - Episodic Memory - How To Update)
### forget_episodic - [] - (Types Of Memory - Episodic Memory - How To Forget)
### update_tool_level - [] - (Types Of Memory - Tool-level Memory - How To Update)
### forget_tool_level - [] - (Types Of Memory - Tool-level Memory - How To Forget)

## Start of ReAct 
### Episodic Memory - []
### Tool-level Memory - []

## End of ReAct
### Episodic Memory - []
### Tool-level Memory - []

## Mechanisms(?)
### Commit Mechanism - [] - (Types Of Memory - Tool-level Memory - Commit Mechanism)
### Accept Mechanism - [] - (Types Of Memory - Tool-level Memory - Accept Mechanism)

# Memory Controller (code-only microservice)

## Tool-level Memory
### Intro? - (Коряво)
### Sequence Diagram - (Коряво)
### recall() - [x] - (Actors - Memory Controller - Tool-level Memory Responsibilities - recall_episodic)
### update() - [x] - (Actors - Memory Controller - Tool-level Memory Responsibilities - update_episodic)
### forget() - [x] - (Actors - Memory Controller - Tool-level Memory Responsibilities - forget_episodic)

## Episodic Memory
### Intro? - (Коряво)
### Sequence Diagram - (Коряво)
### recall() - [x] - (Actors - Memory Controller - Episodic Memory Responsibilities - recall_episodic)
### update() - [x] - (Actors - Memory Controller - Episodic Memory Responsibilities - store_episodic)
### forget() - [x] - (Actors - Memory Controller - Episodic Memory Responsibilities - forget_episodic)

## Semantic Memory
### Sequence Diagram - (Коряво)
### recall() - [x] - (Actors - Memory Controller - Semantic Memory Responsibilities - recall_semantic)
### update() - [x] - (Actors - Memory Controller - Semantic Memory Responsibilities - store_semantic)
### forget() - [x] - (Actors - Memory Controller - Semantic Memory Responsibilities - forget_semantic)

## Procedural Memory
### Sequence Diagram - (Коряво)
### recall() - [x] - (Actors - Memory Controller - Procedural Memory Responsibilities - recall_procedural)
### update() - [x] - (Actors - Memory Controller - Procedural Memory Responsibilities - store_procedural)
### forget() - [x] - (Actors - Memory Controller - Procedural Memory Responsibilities - forget_procedural)

## Autobiographical / User-Personalized Memory
### Sequence Diagram - (Коряво)
### recall() - [x] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - recall_user_level)
### update() - [x] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - update_user_level)
### forget() - [x] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - forget_user_level)

## Priming & Classical Conditioning & Non-Associative Memory
### Sequence Diagram - (Коряво)
### recall() - [] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - recall_user_level)
### update() - [] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - update_user_level)
### forget() - [] - (Actors - Memory Controller - Autobiographical / User-Personalized Memory Responsibilities - forget_user_level)

# Initialization of DBs

## Vector Store
### Tool-level Memory config - [] - (Actors - Vector Store - Episodic Memory Responsibilities - Initialization)
### Episodic Memory config - [] - (Actors - Vector Store - Tool-level Memory Responsibilities - Initialization)
### *Procedural Memory config
### *Autobiographical / User-Personalized Memory config
### *Priming & Classical Conditioning & Non-Associative Memory config

## Graph Store
### Semantic Memory config

# Other
