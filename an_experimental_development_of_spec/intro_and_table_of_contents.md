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

  - [**/recall_tool_level**](#recall_tool_level)
  <br/>Progress: [█████████░] 90%; Status: Done   

  - [**/update_tool_level**](#update_tool_level)
  <br/>Progress: [█████████░] 90%; Status: Done  

  - [**/forget_tool_level**](#forget_tool_level)
  <br/>Progress: [░░░░░░░░░░] 1%; Status: None   

  - [**/rewrite_tool_level**](#rewrite_tool_level)
  <br/>Progress: [████████░░] 80%; Status: Done   

- [**Episodic Memory**](#episodic-memory)
<br/>Progress: [███░░░░░░░] 30%; Status: In Progress   
Stores past experiences and task executions. Includes structured reflections such as `what_worked`, `what_to_avoid`, summaries, and context tags.

  - [**Sequence Diagram**](#sequence-diagram-1)
  <br/>Progress: [████████░░] 80%; Status: Done (small changes will be needed)  

  - [**/recall_episodic**](#recall_episodic)
  <br/>Progress: [█████░░░░░] 50%; Status: In Progress   

  - [**/update_episodic**](#update_episodic)
  <br/>Progress: [█████░░░░░] 50%; Status: In Progress  

  - [**/forget_episodic**](#forget_episodic)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None   

- [**Semantic Memory**](#semantic-memory)
<br/>Progress: [█░░░░░░░░░] 15%; Status: In Progress   
Represents structured factual knowledge and concepts. Implemented through RAG-style retrieval from vector databases or knowledge sources.

  - [**Sequence Diagram**](#sequence-diagram-2)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/recall_semantic**](#recall_semantic)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None   

  - [**/update_semantic**](#update_semantic)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/forget_semantic**](#forget_semantic)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None   

- [**Procedural Memory**](#procedural-memory)
<br/>Progress: [█░░░░░░░░░] 10%; Status: Done(v1)   
Encodes behavioral rules and execution strategies. Derived from episodic reflections and stored as concise operational instructions.

  - [**Sequence Diagram**](#sequence-diagram-3)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/recall_procedural**](#recall_procedural)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/update_procedural**](#update_procedural)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/forget_procedural**](#forget_procedural)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

- [**Autobiographical / User-Personalized Memory**](#autobiographical-memory----user-personalized-memory)
<br/>Progress: [█░░░░░░░░░] 5%; Status: To Do   
Specialized form of episodic memory focused on user-specific patterns, preferences, and long-term identity modeling.

  - [**Sequence Diagram**](#sequence-diagram-4)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/recall_user_level**](#recall_user_level)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None   

  - [**/update_user_level**](#update_user_level)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/forget_user_level**](#forget_user_level)
  <br/>Progress: [░░░░░░░░░░░] 0%; Status: None  

- [**Priming & Classical Conditioning & Non-Associative Memory**](#priming--classical-conditioning--non-associative-memory)
<br/>Progress: [█░░░░░░░░░] 5%; Status: To Do   
Exploration of cognitive-inspired mechanisms and whether they are practically needed in agent systems.

  - [**Sequence Diagram**](#sequence-diagram-5)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/recall_priming**](#recall_priming)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/update_priming**](#update_priming)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**/forget_priming**](#forget_priming)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None   

[**Brains(ReAct) Python harness**](#brainsreact-python-harness)
<br/>Progress: [█░░░░░░░░] 10-15%; Status: Done  
Section describing the Python harness built around the implemented ReAct agent (Brains microservice) and the extensions to be added.

- [**Tools**](#tools)
  <br/>Progress: [██░░░░░░░░] 20%; Status: Done  
  Tools are functions that call corresponding Memory Controller endpoints, primarily to retrieve useful information from storage, and can be invoked by the agent as needed.

  - [**recall_tool_level**](#recall_tool_level-1)
    <br/>Progress: [██████████] 99%; Status: Done  

  - [**recall_episodic**](#recall_episodic-1)
    <br/>Progress: [███░░░░░░░] 30%; Status: Started  

  - [**recall_semantic**](#recall_semantic-1)
    <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**recall_procedural**](#recall_procedural-1)
    <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**recall_user_level**](#recall_user_level-1)
    <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**recall_priming**](#recall_priming-1)
    <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

- [**Functions**](#functions)
  <br/>Progress: [██░░░░░░░░] 20%; Status: Done  
  Functions are standard Python wrappers that guide the ReAct agent’s behavior (e.g., enforcing structured output) and then call the corresponding Memory Controller endpoints.

  - [**update_tool_level**](#update_tool_level-1)
  <br/>Progress: [██████████] 99%; Status: Done  

  - [**forget_tool_level**](#forget_tool_level-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**update_episodic**](#update_episodic-1)
  <br/>Progress: [██████████] 99%; Status: Done  

  - [**forget_episodic**](#forget_episodic-1)
  <br/>Progress: [█░░░░░░░░░] 10%; Status: None  

  - [**update_semantic**](#update_semantic-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**forget_semantic**](#forget_semantic-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**update_procedural**](#update_procedural-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**forget_procedural**](#forget_procedural-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**update_user_level**](#update_user_level-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**forget_user_level**](#forget_user_level-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**update_priming**](#update_priming-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

  - [**forget_priming**](#forget_priming-1)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  

- [**Mechanisms**](#mechanisms)
  <br/>Progress: [██████████] 99%; Status: Done  
  Mechanisms paragraph describes extensions over ReAct to improve reliability, introducing control layers around tool usage

  - [**Commit Mechanism**](#commit-mechanism)
  <br/>Progress: [██████████] 99%; Status: Done  
  Wrapper over tool execution that enforces validation and reflection before any state-modifying actions.

  - [**Accept Mechanism**](#accept-mechanism)
  <br/>Progress: [██████████] 99%; Status: Done  
  Wrapper over read-access tools that validates and compresses outputs before storing them in working memory.

[**Initialization of DBs**](#initialization-of-dbs)
<br/>Progress: [██░░░░░░░░] 20%; Status: In Progress   
Initialization and configuration of all database systems (Vector and Graph Stores) that support different memory subsystems.

- [**Vector Store**](#vector-store)
<br/>Progress: [███░░░░░░░] 30?%; Status: In Progress   
Vector Store is a paragraph, which tells about vector store and its responsibilities for different memory subsystems (Tool-Level Memory, Episodic Memory).

  - [**Tool-level Memory config**](#tool-level-memory-config)
  <br/>Progress: [█████████░] 90%; Status: Done  
  Specific configuration of Vector Store collection(s) for Tool-level Memory   

  - [**Episodic Memory config**](#episodic-memory-config)
  <br/>Progress: [███░░░░░░░] 30%; Status: Done  
  Specific configuration of Vector Store collection(s) for Episodic Memory

  - [**?Procedural Memory config**](#procedural-memory-config)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  
  Specific configuration of Vector Store collection(s) for Procedural Memory

  - [**?Autobiographical / User-Personalized Memory config**](#autobiographical--user-personalized-memory-config)
  <br/>Progress: [░░░░░░░░░░░] 0%; Status: None  
  Specific configuration of Vector Store collection(s) for Autobiographical / User-Personalized Memory

  - [**?Priming & Classical Conditioning & Non-Associative Memory config**](#priming--classical-conditioning--non-associative-memory-config)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  
  Specific configuration of Vector Store collection(s) for Priming & Classical Conditioning & Non-Associative Memory

- [**Graph Store**](#vector-store)
<br/>Progress: [░░░░░░░░░░] 0%; Status: None   
Graph Store is a paragraph, which tells about graph store and its responsibilities for Semantic Memory.

  - [**Semantic Memory config**](#semantic-memory-config)
  <br/>Progress: [░░░░░░░░░░] 0%; Status: None  
  Specific configuration of Graph Store for Semantic Memory  

---

[**Other**](#other)
<br/>This section won't be in final spec. This is just ideas, resources, valuable info that can used in writing paragraphs above.

- [**What Agent Needs to Remember and What Not**](#what-agent-needs-to-remember-and-what-is-not)
<br/>Progress: [█░░░░░░░░░] 10%; Status: To Do   
Defines criteria for deciding which information is memory-worthy. Includes discussion about relevance to task, user intent, and long-term utility.

- [**Forgetting**](#forgeting)
<br/>Progress: [█░░░░░░░░░] 10%; Status: In Progress   
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
