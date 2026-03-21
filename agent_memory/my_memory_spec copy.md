# My Memory Conceptual Architecture v1

[OUTDATED]Memory subsystem is the information storage and retrieval part of our AI Agent. It consists of a [lie]single vector store that contains several collections. It directly interacts with the Brains subsystem (PlanExecutor and ReAct) and operates at multiple levels, such as storing memories from the [not_sure]PlanExecutor as well as memories from each ReAct worker invoked by the PlanExecutor. At the moment, our Memory subsystem is composed of four underlying memory components: working, tool-level, episodic, semantic, and procedural memory.

**Memory Architecture Diagram:**
![Memory Architecture Diagram](memory_schema.png)

# Table Of Contents

[**Explicit & Implicit Memory**](#explicit-memory-conscious--implicit-memory-subconscious)

`Progress: [██████████] 99%`; `Status: Done`

Division of the memory subsystem into two major categories: Explicit and Implicit.  
Explains how they differ, which memory types belong to each category, and discusses their trade-offs in latency, architectural separation, and update mechanisms.

[**Working Memory**](#working-memory)

`Progress: [██████████] 99%`; `Status: Done By OpenAI`

**This paragraph is provided for context only;** it does not contain any implementation ideas at the moment. 
Temporary, active workspace of the agent. Maintains current interaction state, conversation history, and short-term reasoning context.


[**Memory Controller**](#memory-controller)

`Progress: [██░░░░░░░░] 20%`; `Status: In Progress` 

Memory Controller is a stateless microservice responsible for managing the lifecycle of agent memories. It exposes an HTTP API and serves as the abstraction layer between the cognitive system (ReAct/Brains) and persistent memory storage systems.

[**Vector Store**](#vector-store)

`Progress: [█████░░░░░] 90?%`; `Status: In Progress` 

Vector Store is a paragraph, which tells about vector store and its responsibilities for different memory subsystems (Tool-Level Memory, Episodic Memory).

[**Tool-Level Memory**](#tool-level-memory)

`Progress: [█████████░] 90%`; `Status: Done` 

Stores structured reflections about individual tool executions.
Captures inductive thoughts extracted from each (tool_call, tool_output) pair, representing relations such as (subject, relation, object).
Organized per tool (separate collection per tool name) and used to improve future tool selection, parameterization, and execution reliability through recall, merging, and contradiction resolution mechanisms. (10% - PRD? Forgetting? other questions..)

[**Episodic Memory**](#episodic-memory)

`Progress: [███░░░░░░░] 30%`; `Status: In Progress`

Stores past experiences and task executions.  
Includes structured reflections such as `what_worked`, `what_to_avoid`, summaries, and context tags.

[**Semantic Memory**](#semantic-memory)

`Progress: [███░░░░░░░] 30%`; `Status: In Progress`

Represents structured factual knowledge and concepts.  
Implemented through RAG-style retrieval from vector databases or knowledge sources.

[**Procedural Memory**](#procedural-memory)

`Progress: [██░░░░░░░░] 20%`; `Status: Done(v1)`

Encodes behavioral rules and execution strategies.  
Derived from episodic reflections and stored as concise operational instructions.

[**Autobiographical / User-Personalized Memory**](#autobiographical-memory----user-personalized-memory)

`Progress: [█░░░░░░░░░] 10%`; `Status: To Do`

Specialized form of episodic memory focused on user-specific patterns, preferences, and long-term identity modeling.

[**What Agent Needs to Remember and What Not**](#what-agent-needs-to-remember-and-what-is-not)

`Progress: [██░░░░░░░░] 10%`; `Status: To Do`

Defines criteria for deciding which information is memory-worthy.  
Includes discussion about relevance to task, user intent, and long-term utility.

[**Forgetting**](#forgeting)

`Progress: [█░░░░░░░░░] 10%`; `Status: In Progress`

Selective forgetting strategies based on time decay, usage frequency, contradiction handling, and summarization-based replacement.

[**Replacing (Contradiction Resolution)**](#replacing)

`Progress: [██░░░░░░░░] 20%`; `Status: To Do`

Mechanisms for resolving conflicting memories and determining which information should be treated as authoritative.

[**Retrieving Methods (Variants)**](#retrieving-methods-how-to-retrieve----variants-to-retrieve)

Overview of different retrieval strategies beyond standard vector search.

[RLM](#rlm)

Recursive Language Model-based retrieval strategy with deeper reasoning loops.

[Single-vector Search Improvement](#single-vector-search-improvement)

Improvements over naive embedding search, including agentic query refinement.

[DRIFT Search and GraphRAG (Fav)](#drift-search-and-graphrag-fav)

Graph-enhanced retrieval strategies inspired by hierarchical and community-based reasoning.

[File System](#file-system)

File-based memory storage approach aligned with LLM pretraining priors.

[LSH](#lsh)

Two-stage approximate retrieval: LSH grouping followed by similarity search.

[Multi-vector Search](#multi-vector-search)

Token-level or multi-representation matching approach with higher precision but higher latency.

[**Priming & Classical Conditioning & Non-Associative Memory**](#priming--classical-conditioning--non-associative-memory)

`Progress: [█░░░░░░░░░] 10%`; `Status: To Do`

Exploration of cognitive-inspired mechanisms and whether they are practically needed in agent systems.

[**Benchmarks for Memory**](#benchmarks-for-memory)

`Progress: [█░░░░░░░░░] 10%`; `Status: To Do`

Evaluation strategies to measure effectiveness of different memory types.

[**Questions To Answer Still**](#questions-to-answer-still)

Open architectural questions regarding shared memory between PlanExecutor and ReAct workers.

[**Ideas**](#ideas)

Experimental directions such as MMR, improved memory controller logic, and hybrid retrieval systems.

---

## Explicit Memory (Conscious) && Implicit Memory (Subconscious)

## Working Memory 

## Memory Controller

### Episodic Memory Responsibilities

#### recall_episodic

#### store_episodic

### Tool-Level Memory Responsibilities

#### recall_tool_level

#### store_tool_level

## Vector Store

### Episodic Memory Responsibilities

### Tool-Level Memory Responsibilities

## Tool-Level Memory

### How To Retrieve (Recall Mechanism)

### How To Update/Save? (Post-think)

### How To Forget?

#### Classical Forgetting?[To_Do]

#### Tool-Level Memory Rewriting

### Commit Mechanism (Tool-Call Confirmation Layer)

### Accept Mechanism (Tool-Output Compression & Confirmation Layer)

## Episodic Memory

### How To Update/Save?

### How To Retrieve

### Autobiographical Memory --> User-personalized Memory?

## Semantic Memory

### How To Update/Save?

### How To Retrieve

### How To Forget

---

## Procedural Memory

### How To Update/Save

### How To Retrieve

### How To Forget???[To_Do]

---
### Examples[To_Do]
**Example**

---

## Priming && Classical Conditioning && Non-Associative Memory

# Other