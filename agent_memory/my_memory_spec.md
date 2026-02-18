# My Memory Conceptual Architecture v1

Memory subsystem is the information storage and retrieval part of our AI Agent. It consists of a single vector store that contains several collections. It directly interacts with the Brains subsystem (PlanExecutor and ReAct) and operates at multiple levels, such as storing memories from the PlanExecutor as well as memories from each ReAct worker invoked by the PlanExecutor. At the moment, our Memory subsystem is composed of four underlying memory components: working, episodic, semantic, and procedural memory.

Memory Architecture Diagram:
![Memory Architecture Diagram](memory_schema.png)

# Table Of Contents

[**Explicit & Implicit Memory**](#explicit-memory-conscious--implicit-memory-subconscious)

`Status: Done`

Division of the memory subsystem into two major categories: Explicit and Implicit.  
Explains how they differ, which memory types belong to each category, and discusses their trade-offs in latency, architectural separation, and update mechanisms.

[**Working Memory**](#working-memory)

`Status: Done By OpenAI`

**This paragraph is provided for context only;** it does not contain any implementation ideas at the moment. 
Temporary, active workspace of the agent. Maintains current interaction state, conversation history, and short-term reasoning context.

[**Tool-Level Memory**](#tool-level-memory)

`Status: In Progress`

Stores structured reflections about individual tool executions.
Captures inductive thoughts extracted from each (tool_call, tool_output) pair, representing relations such as (subject, relation, object).
Organized per tool (separate collection per tool name) and used to improve future tool selection, parameterization, and execution reliability through recall, merging, and contradiction resolution mechanisms.

[**Episodic Memory**](#episodic-memory)

`Status: Done(v1)`

Stores past experiences and task executions.  
Includes structured reflections such as `what_worked`, `what_to_avoid`, summaries, and context tags.

[**Semantic Memory**](#semantic-memory)

`Status: Done(v1)`

Represents structured factual knowledge and concepts.  
Implemented through RAG-style retrieval from vector databases or knowledge sources.

[**Procedural Memory**](#procedural-memory)

`Status: Done(v1)`

Encodes behavioral rules and execution strategies.  
Derived from episodic reflections and stored as concise operational instructions.

[**Autobiographical / User-Personalized Memory**](#autobiographical-memory----user-personalized-memory)

`Status: To Do`

Specialized form of episodic memory focused on user-specific patterns, preferences, and long-term identity modeling.

[**What Agent Needs to Remember and What Not**](#what-agent-needs-to-remember-and-what-is-not)

`Status: To Do`

Defines criteria for deciding which information is memory-worthy.  
Includes discussion about relevance to task, user intent, and long-term utility.

[**Forgetting**](#forgeting)

`Status: In Progress`

Selective forgetting strategies based on time decay, usage frequency, contradiction handling, and summarization-based replacement.

[**Replacing (Contradiction Resolution)**](#replacing)

`Status: To Do | In Progress`

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

`Status: To Do`

Exploration of cognitive-inspired mechanisms and whether they are practically needed in agent systems.

[**Benchmarks for Memory**](#benchmarks-for-memory)

`Status: To Do`

Evaluation strategies to measure effectiveness of different memory types.

[**Questions To Answer Still**](#questions-to-answer-still)

Open architectural questions regarding shared memory between PlanExecutor and ReAct workers.

[**Ideas**](#ideas)

Experimental directions such as MMR, improved memory controller logic, and hybrid retrieval systems.

---

## Explicit Memory (Conscious) && Implicit Memory (Subconscious)

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

## Tool-Level Memory

As you remember, our agent has a ReAct architecture.
Tool-level memory is the agent’s memory that operates by retrieving and creating memories for each pair of tool call and tool output.

So, let’s start with the mechanism.
Workflow. Overall framework is divided into two stages:
• Stage-1: Recall. Generated a new tool-call by our ReAct agent, tool call goes to commit mechanism. Commit mechanism is mechanism, when agent is asked “Are you sure that this is a correct tool call that will help you get closer to completing the task?” like a AI prompt. In our case, in addition to AI prompt we will add "Here is what you recall about this tool: {relevant_memories}". So as you can understand there is a Recall mechanism is triggered.

Не Описаний Коміт механізм. Якщо після пригадування про тулу, він вирішує змінити свій вибір до іншої тули, то він перекомічує??? І тоді має згадати тепер про цю тулу ж.

After reading the AI prompt from commit mechanism, agent can change his tool-call decision or approve that he is sure that this tool-call will help him get closer to completing the task.

Retrieving relevant thoughts helps generating accurate tool-calls.

• Stage-2: Post-think and Update. After answering the question,
Memory Controller has to post-think upon tool call and tool output pair and insert the newly self-generated reasoning thoughts into memory (to vector db collection according to tool name).

### How To Update/Save? (Post-think)

In detail, the post-thinking stage happens right after each tool output. Each post-thinking stage generates one memory.

The memory thought is formed by the Memory Controller in the following way:
Memory thought will be stored as Inductive Thought. The inductive thought is defined as the text which contains the relation between two entities, i.e., satisfying a relation triple (𝐸ℎ, 𝑟𝑖, 𝐸𝑡). 𝐸ℎ is head entity connected with tail entity 𝐸𝑡 via the relation 𝑟𝑖, where 𝑖 ∈ [0, 𝑁] and 𝑁 is the relation number. Conceptually, 𝑅ℎ = {𝑟1, · · · , 𝑟𝑁 } consists of all the one-hop relations for the entity 𝐸ℎ.

Prompt for Generating Thoughts:
```python
"""
Given the following tool-call and tool-output pairs, please extract the relation (subject, relation, object) with corresponding text:
Example 1.
Input:
Tool-call: run_cmd("rm -rf valuable.txt")
Tool Output: You didn't have enough rights. You need to use sudo.
Output:
(Deletion of valuable.txt, requires, sudo rights).
Deletion of valuable.txt requires sudo rights.

Example 2.
Input:
Tool-call: deep_research("For which Ukrainian university authors of the paper `Large Language Models as Oracles for Ontology Alignment` ")
Tool Output: Ukrainian Catolic University
Output:
(Some authors of `Large Language Models as Oracles for Ontology Alignment`, are from, Ukrainian Catolic University).
Some authors of `Large Language Models as Oracles for Ontology Alignment` are from Ukrainian Catolic University.

Here is current tool-call: 
{current_tool_call}
Here is current tool output:
{current_tool_output}

Also, you need to враховувати спогади, які вже були пригадані, аби позбутися повторів. Ось вони:
{recalled_memories}
"""
```

Then this memory thought will be categorized according to tool name of called tool. This way we will have a vector database collection named as tool name. In this collection we will add this memory thought. 

### How To Retrieve (Recall Mechanism)

Using just find(or grep) function by tool name found the category(collection of vector db named by tool name) and then we need to take out the best out of this category (or all of them).

Але Тут Вмішується Локальний Механізм Забування Tool-Level Memory.
(Звісно, Якщо Кількість Елементів не Захмарна!!! Інакше Шо Лі Доведеться Відмовитись Від цього Механізму???)
Цей Механізм скаладається з двох етапів:
1. Merging Memories
2. Rewriting Contradictatory Memories

Обидва методи базуються на ЛЛМці.

Prompt for Rewriting Contradictatory Memories
```python
"""
Given the following thoughts, please remove the
counterfactual thoughts or contradictory thoughts:
Example 1.
Input:
run_cmd collection:
ls was made in Root directory.
Root directory has input.txt, intermediate.txt.(КАК ОН ДОЛЖЕН ПОНЯТЬ КОМУ ВЕРИТЬ А КОМУ НЕТ, ЕСЛИ МИ НЕБУДЕМ ПИСАТЬ ДАТУ, ВРЕМЯ,-- НУЖНО МЕНЯТЬ КОНЦЕПЦИЮ ПОСТРОЕНИЯ СПОГАДІВ, ПЕЙПЕР ЕТО НЕ ПРОДУМАЛ!!!)
ls was made in Root directory.
Root directory has input.txt, intermeadiate.txt, output.txt
Output:
ls was made in Root directory.
ls was made in Root directory.
Root directory has input.txt, intermeadiate.txt, output.txt
Example 2.
Input:
???
Output:
???
[A group of thoughts]
"""
```

Prompt for Merging Thoughts
```python
"""
Given the following thoughts, please merge the similar thoughts with the same entity:
Example 1.
Input:
ls was made in Root directory.
ls was made in Root directory.
Root directory has input.txt, intermeadiate.txt, output.txt
Output:
ls was made in Root directory.
Root directory has input.txt, intermeadiate.txt, output.txt
Example 2.
Input:
ls was made in Root directory.
ls was made in /home/oleksandr/Downloads directory. (ТРЕБА ДАТУВАННЯ)
Root directory has input.txt, intermeadiate.txt, output.txt
Output: (а чи треба робити такий мердж? а чи не зіб'є він)
ls was made in Root directory and then /home/oleksandr/Downloads directory. 
Root directory has input.txt, intermeadiate.txt, output.txt
Input:
[A group of thoughts]
"""
```

Що краще спочатку робити Merging, Rewriting? Чи дати це в одному промпті?

Навіть якщо Post-processing створить такий самий або майже такий самий спогад, що вже лежить у Tool-level Memory. У наступному етапі Recall він матиме зробити Merging + Rewriting Contradictatory Memories, що вирішує проблему.

[To_Do] Як правильно робити query до БД, яка зберігає tool-level memory?
Оскільки по сирому tool-call нічого у векторній БД фіг відкличеться, бо ми засунемо в категорію цієї тули спогади з трьох слів походу...(типу скоріш за все відповідно до параметрів робити запит...). Якщо їх мало, то можна було б вертати всі і потім відбирати ллмкою.

[To_Do](Still optional if latency will be high enough) 
Then these all retrieved memories will be given to Memory Controller. Memory Controller (which is LLM-based) will take out the only relevant ones according to his context. And Will DO Some Scoring Of Relevance Or Reward System To Memories With The Memory Thoughts He will take from the list.

Final output of Memory Controller is what will added to the AI prompt, which ReAct Agent will read after commiting the tool.

Also, because Tool-level Memory is categorized as Explicit and Implicit at the same time it has a tool recall_tool_level.
[In_Progress]
```python
def recall_tool_level(
    toolname: str,
    query: str,
    alpha: int
) -> dict:
  """Recall relevant memories from Tool-level memory for explicit query.

Recommended scenarios:
- When the agent needs to retrieve factual or conceptual knowledge...

Best practices:
- Use this tool to ...

  Args:
    toolname: Over which toolname memory thoughts you want to search.
    query: The search query in vector db collection of specific tool.
    alpha: (Optional) Defaults to 0.7. This means the search result is influenced by 70% vector similarity and 30% BM25 ranking.
  """
```
### How To Forget???[To_Do]

Тут є два механізми забування:
Локальний механізм забування,
Глобальний механізм забування.
Локальний механізм забування в Tool-Level Memory:
Кожен раз, коли відбувається коміт тули, 

Глобальний механізм забування - це те, що розглянуто у параграфі Forgetting з другим рівнем заголовку. Він побудований відносно Меморі Контроллера, який як ЛЛМка відбирає потрібні релевантні спогади відповідно до його контекстного вікна. Спогади відібрані релеватними отримують бал/бали, а спогади, що не були вибрані релевантними не отримують балів або отримують від'ємні бали. Періодично будуть відсікатися та видалятися спогади, що мають загальний бал дуже низьким відносно інших спогадів. Це зроблено для того, щоб система пам'яті могла коректно працювати та надавати лише справді потрібні спогади. 

### Examples
**Example**

## Episodic Memory

[To_Do]Change Vector Search With Graph Rag Ideas?

Episodic memory is a historical collection of prior experiences, or episodes. It includes what happened, how it happened, and the lessons or insights learned from those experiences, even if they were never clearly stated.

### How To Update/Save?

For our agents, this includes past conversations from all ReAct workers, 2-4 keywords (context tags) that would help identify similar future conversations, one-sentence summaries of what was done in the immediately preceding conversation, and structured fields such as what_worked and what_to_avoid. The what_worked field captures the most effective approaches and strategies used as well as information that can be leveraged in subsequent iterations. The what_to_avoid field records critical pitfalls, ineffective approaches, and factors that may lead the agent down incorrect paths or into dead ends.

It has to be saved in a JSON (or Python dictionary) into vector database collection named `episodic_memory`.
The creation of the JSON (or Python dictionary) is performed by the ReAct agent at the end of the its execution, not necessarily after a successful outcome.

### How To Retrieve

Then, a vector (semantic) search is performed when a new ReAct worker is invoked by the PlanExecutor to retrieve the JSON (or Python dictionary) with the highest semantic similarity to the user prompt. The retrieved entry is then injected into the system prompt with the phrasing: “Here is what you recall about your task: {json_best_match}”. 

[In_Progress]Or we can retrieve top-k results(or results above some threshold) and then ask llm in order to make the best out of them (combine or summarize?). Also, this step with llm can say which is from time-to-time is only заважає, але має високий similarity (і треба далі думати що треба робити -- піднімати threshold? top-k? видалити з пам'яті -- forgetting?). 

Also, because Episodic Memory is categorized as Explicit and Implicit at the same time it has a tool recall_episodic.
[In_Progress]
```python
def recall_episodic(
    query: str,
    alpha: int
) -> dict:
  """Recall relevant memories from episodic memory for explicit query.

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

### Autobiographical Memory --> User-personalized Memory?
[To_Do]Autobiographical Memory: A form of episodic memory focusing on events and experiences
related to one’s personal history [238]. While sometimes treated as a sub-category of episodic
memory, autobiographical memory places particular emphasis on the self and its evolving
life narrative

## Semantic Memory

Semantic memory represents our structured knowledge of facts, concepts, and their relationships - essentially what we "know" rather than what we "remember experiencing."
For our Agents, this would be implemented through techniques like Retrieval Augmented Generation (RAG), where relevant information is dynamically pulled from a knowledge base to ground and inform responses.

### How To Update/Save?
Detailed Implementation
Much of the organizational information already exists in sources such as Confluence, Jira, Slack, GitHub, and Google Drive. This information can be treated as factual knowledge.

[In_Progress]It would be valuable to capture additional facts during the agent's execution. For example, we can include a structured output field called semantic_memory at the end of the agent's run, where it records all facts observed throughout the execution or task completion. Since the agent still has access to its working memory, it can populate this field with relevant knowledge. Maybe it’s hard to keep track of everything when the task is long and the context window is filled with a lot of information. That’s why it makes sense to add ability Memory Controller that selectively extracts only the necessary information at each step—such as before a tool call, after a tool’s output, or when processing new user input.
Because the final structured response may become very large/overwhelming, it may be necessary to split it into multiple separate responses to get high-quality answers. (think about approach?)

All collected information should be stored in a vector database collection named semantic_memory, using high-quality chunking. For example, chunking can be based on markdown formatting or a recursive character chunker, taking advantage of [ChromaDB's custom chunkers](https://research.trychroma.com/evaluating-chunking)(or it is the same?).
#### How To Chunk? [To_Do]

### How To Retrieve

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

### How To Forget???[To_Do]

---
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

## Procedural Memory

Procedural memory is different from working, semantic, and episodic memory since it covers more how we actually remember to perform tasks or follow a familiar routine, i.e. riding a bike or typing on a keyboard. It's the "how to do things" type of memory, distinct from factual knowledge (semantic) or specific experiences (episodic). 

In our system, we adopt a simplified implementation. Procedural memory is represented as a list of up to 10 concise instructions that guide the agent’s behavior. These instructions are derived from episodic memory.

### How To Update/Save
After each ReAct agent execution, the system aggregates the existing what_worked and what_to_avoid entries with newly generated insights obtained during the Reflexion stage. Based on this updated information, the procedural memory is revised by updating the list of 10 instructions, which are saved into the file named `procedural_memory_instructions.txt`.

At the first invocation of a ReAct agent, the procedural memory is initialized as empty.

[To_Do][In this design, procedural memory closely resembles an agents.md-style guideline file. However, alternative approaches should be considered!!!
For example, in the LangChain [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D)
video, the system incrementally updates an agents.md file and may eventually promote accumulated knowledge into an explicit “skill.” But looks like not very reliable idea at the moment.]

### How To Retrieve
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

### How To Forget???[To_Do]

---
### Examples[To_Do]
**Example**

---

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

## Priming && Classical Conditioning && Non-Associative Memory
[To_Do|Think]Does we really need them? At The Moment Didn't See Papers Demonstarting Usage Of Them And Didn't Overlap With Existing Ones (Semantic, Episodic, Procedural, Working(?))

* Priming: The phenomenon in which prior exposure to a stimulus influences subsequent responses, often without explicit recognition of the previous encounter [242]. 

* Classical Conditioning: The learned association between two stimuli, where one stimulus comes to elicit a response originally produced by the other [243]. 

* Non-Associative Memory: Adaptive modifications in behavior following repeated exposure to a single stimulus. Habituation (reduced response to a repeated, harmless stimulus) and sensitization (increased response after exposure to a noxious or intense stimulus) are representative examples [244, 245].

## Forgeting[In_Progress]

Selective forgetting [371] is the crucial process of removing or down-weighting memories that are deemed

irrelevant, redundant, or outdated. This is essential for maintaining memory efficiency and preventing

cognitive overload. Forgetting mechanisms can be based on time (older memories are more likely to be

forgotten) [301], usage frequency (infrequently accessed memories are more likely forgotten) [257], and

relevance to the current task or context [309]. In more fine-grained forgetting mechanisms, MemoryBank [261]

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

Concept Of Memory Controller!!!

MMR (Maximum Marginal Relevance) — for retrieving very similar and contradictory information

Як Меморі Контроллер має розуміти, що треба зберігати, а що ні? -- Так, справді можуть бути релевантні думки, які можуть там суперечити, тому 

[Вирівнювання онтологій(термінологій)](https://arxiv.org/abs/2508.08500) між різними підсистемами пам'яті може бути справді траблом, але це вже так чисто ідея для майбутнього я думаю.