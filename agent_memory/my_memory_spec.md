# My Memory Conceptual Architecture v1

Memory subsystem is the information storage and retrieval part of our AI Agent. It consists of a single vector store that contains several collections. It directly interacts with the Brains subsystem (PlanExecutor and ReAct) and operates at multiple levels, such as storing memories from the PlanExecutor as well as memories from each ReAct worker invoked by the PlanExecutor. At the moment, our Memory subsystem is composed of four underlying memory components: working, episodic, semantic, and procedural memory.


## Explicit Memory (Conscious) && Implicit Memory (Subconscious)

As a starting point, we can categorize memory into Explicit and Implicit.
At this stage, all memory types — namely episodic, semantic, and procedural — will be both Explicit and Implicit at the same time.

Memory types categorized as Explicit expose a dedicated tool for recall (i.e., searching the memory store) based on an agent query.
Detailed description of functions you can see below in corresponding headings: Episodic Memory, Semantic Memory, Procedural Memory.
```python
recall_semantic()
recall_episodic()
recall_procedural()
```

Memory types categorized as Implicit are running in the background for the agent(ReAct/Planner) by Memory subsystem. 

Comparing Implicit and Explicit memories, the Explicit approach has the downside of introducing some extra latency before any response is delivered. It also requires combining the memory logic with the agent logic. However, memories categorized as Implicit avoids those issues - there’s no added latency, and memory logic remains separate. But running “in the background” also has its own drawbacks: the memory is not updated immediately, and extra logic is needed determine when to kick off the background process.

Another way to updating memory involves user feedback, which is particularly relevant to episodic memory. For example, If the user marks an interaction as a positive one, you can save that feedback to recall in the future.

As I mentioned before at the moment we categorize all types of memories as both Explicit and Implicit at the same time. By this I mean that every type of memory has its own tool for recall (i.e., searching the memory store) based on an agent query.

In the future, we can evaluate usage patterns and identify cases where certain memory types should be only Explicit or only Implicit, depending on how they are accessed and utilized.

## What agent needs to remember and what is not

Agent needs to know what is his purpose so that he knows what to remember, what to remember better. For ReAct it has to be his task, given by PlanExecutor and for PlanExecutor it has to be user prompt.

Maybe we have to make some special treatment to the information that somehow correlates with user prompt

{No Mechanism at the moment}

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

## Working Memory 
This paragraph is provided for context only; it does not contain any implementation ideas at the moment.

Working memory is what helps you keep track of information you are using right now and make sense of it as things change. For our Agents, it means remembering **the current conversation** and using it to respond properly in real time. 

At the moment, we can say that OpenAI provides a solution for working memory, but maintaining a consistently growing list of all user inputs, tool calls, tool outputs, and reasoning items—appended each time the agent receives inputs and produces outputs—looks like not the best solution.

There is where Context Engineering methods like compaction and summarization come into play.

[Here can be explained difference between this two methods and how, when to use each and details of implementation. compaction -- compact, summarization -- rewind. This way summarization can be the way of forgeting? [link](https://drive.google.com/file/d/1QGJ-BrdiTGslS71sYH4OJoidsry3Ps9g/view)
How OpenAI Compaction works? Does OpenAI Compaction work like described in the link above?
Codex CLI is written on Rust, but it is an endpoint how I will look into OpenAI implementation of compaction?
I can look just into usage of it in codex cli written on Rust. There is more information on Anthropic's compaction((((]

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

## Episodic Memory

Change Vector Search With Graph Rag Ideas?

Episodic memory is a historical collection of prior experiences, or episodes. It includes what happened, how it happened, and the lessons or insights learned from those experiences, even if they were never clearly stated.

### How To Update (How To Save?)

For our agents, this includes past conversations from all ReAct workers, 2-4 keywords (context tags) that would help identify similar future conversations, one-sentence summaries of what was done in the immediately preceding conversation, and structured fields such as what_worked and what_to_avoid. The what_worked field captures the most effective approaches and strategies used as well as information that can be leveraged in subsequent iterations. The what_to_avoid field records critical pitfalls, ineffective approaches, and factors that may lead the agent down incorrect paths or into dead ends.

It has to be saved in a JSON (or Python dictionary) into vector database collection named `episodic_memory`.
The creation of the JSON (or Python dictionary) is performed by the ReAct agent at the end of the its execution, not necessarily after a successful outcome.

### How To Retrieve

Then, a vector (semantic) search is performed when a new ReAct worker is invoked by the PlanExecutor to retrieve the JSON (or Python dictionary) with the highest semantic similarity to the user prompt. The retrieved entry is then injected into the system prompt with the phrasing: “Here is what you recall about your task: {json_best_match}”. 

Or we can retrieve top-k results(or results above some threshold) and then ask llm in order to make the best out of them (combine or summarize?). Also, this step with llm can say which is from time-to-time is only заважає, але має високий similarity (і треба далі думати що треба робити -- піднімати threshold? top-k? видалити з пам'яті -- forgetting?). 

Also, because Episodic Memory is categorized as Explicit and Implicit at the same time it has a tool recall_episodic?
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

### How To Forget???

---
[This approach can be improved by reading `Reflexion` paper, in particular by considering Evaluator/Critic role. 

Also, episodic memory can be trigerred on some words like "always do like this", "good workflow to make this" and save it what user want ot mention. That's examples I saw in [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D) video from langchain. Their agent saves such replics to agents.md. I hope their Deep Agent is open-source.]

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
Autobiographical Memory: A form of episodic memory focusing on events and experiences
related to one’s personal history [238]. While sometimes treated as a sub-category of episodic
memory, autobiographical memory places particular emphasis on the self and its evolving
life narrative

## Semantic Memory

Semantic memory represents our structured knowledge of facts, concepts, and their relationships - essentially what we "know" rather than what we "remember experiencing."
For our Agents, this would be implemented through techniques like Retrieval Augmented Generation (RAG), where relevant information is dynamically pulled from a knowledge base to ground and inform responses.

### How To Update (How To Save?)
Detailed Implementation
Much of the organizational information already exists in sources such as Confluence, Jira, Slack, GitHub, and Google Drive. This information can be treated as factual knowledge.

It would be valuable to capture additional facts during the agent's execution. For example, we can include a structured output field called semantic_memory at the end of the agent's run, where it records all facts observed throughout the execution or task completion. Since the agent still has access to its working memory, it can populate this field with relevant knowledge. Maybe it’s hard to keep track of everything when the task is long and the context window is filled with a lot of information. That’s why it makes sense to add ability Memory Controller that selectively extracts only the necessary information at each step—such as before a tool call, after a tool’s output, or when processing new user input.

Because the final structured response may become very large/overwhelming, it may be necessary to split it into multiple separate responses to get high-quality answers. (think about approach?)

All collected information should be stored in a vector database collection named semantic_memory, using high-quality chunking. For example, chunking can be based on markdown formatting or a recursive character chunker, taking advantage of [ChromaDB's custom chunkers](https://research.trychroma.com/evaluating-chunking)(or it is the same?).

### How To Retrieve

When a new ReAct worker is invoked by the PlanExecutor, a semantic (vector) search retrieves the top 10 chunks most semantically similar to the user prompt. These chunks are then injected into the end of user prompt with a phrasing like: “Here are some facts and knowledge that may be relevant to your task and help you complete it: {dict_best_match}”

Also, because Semantic Memory is categorized as Explicit and Implicit at the same time it has a tool recall_semantic?
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

### How To Forget???

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

### How To Update (How To Save?)
After each ReAct agent execution, the system aggregates the existing what_worked and what_to_avoid entries with newly generated insights obtained during the Reflexion stage. Based on this updated information, the procedural memory is revised by updating the list of 10 instructions, which are saved into the file named `procedural_memory_instructions.txt`.

At the first invocation of a ReAct agent, the procedural memory is initialized as empty.

[In this design, procedural memory closely resembles an agents.md-style guideline file. However, alternative approaches should be considered!!!
For example, in the LangChain [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D)
video, the system incrementally updates an agents.md file and may eventually promote accumulated knowledge into an explicit “skill.” But looks like not very reliable idea at the moment.]

### How To Retrieve
Before each execution of the ReAct agent, the last 10 generated procedural memory instructions are added to its system prompt. They are taken from the file named `procedural_memory_instructions.txt`.

Also, because Procedural Memory is categorized as Explicit and Implicit at the same time it has a tool recall_procedural?
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

### How To Forget???

---
### Examples
**Example**

---

## Priming && Classical Conditioning && Non-Associative Memory
Does we really need them? At The Moment Didn't See Papers Demonstarting Usage Of Them And Didn't Overlap With Existing Ones (Semantic, Episodic, Procedural, Working(?))

* Priming: The phenomenon in which prior exposure to a stimulus influences subsequent responses, often without explicit recognition of the previous encounter [242]. 

* Classical Conditioning: The learned association between two stimuli, where one stimulus comes to elicit a response originally produced by the other [243]. 

* Non-Associative Memory: Adaptive modifications in behavior following repeated exposure to a single stimulus. Habituation (reduced response to a repeated, harmless stimulus) and sensitization (increased response after exposure to a noxious or intense stimulus) are representative examples [244, 245].

## Forgeting -- Is it the same as Selective Forgetting From MetaResearch?

### Replacing
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

### Single-vector search improvement
[Have to consider watching [RAG videos](https://www.youtube.com/watch?v=6vG_amAshTk&list=PL31XFvSmiPKEMco1JXKtIBttlAOOxE8aO) and consider doing some Agentic RAG, inspiring by [RLM](https://arxiv.org/pdf/2512.24601)]

### DRIFT Search and GraphRAG
At the moment, this mainly comes down to ideas from [DRIFT Search and GraphRAG](https://youtu.be/6vG_amAshTk?si=h9iNUk7xXOjvMJfI) ideas. These approach(es) need to be studied in detail to extract the strongest ideas and combine them into a more effective solution.

### File system
The file system is currently one of the most popular storage options for agent-based systems. This may be because LLMs are already well fine-tuned to work with file-based structures confidently and reliably.

### Multi-vector search
Multi-vector search has relatively high latency, even with various optimizations.
I think this approach still requires keyword-based queries, similar to how Google search works (the same applies to single-vector search). Because it is still far from LLM understanding by its nature.

By its nature, multi-vector search is best suited for token-to-token matching. While the attention mechanism slightly adjusts token meaning based on surrounding words, the matching still largely happens at the token level.

Single-vector search, on the other hand, tends to blur the query representation. When the prompt is large and contains many words that add diversity or nuance, everything gets mixed into a single embedding. As a result, even with single-vector search, it is better to keep queries short and focused.

One idea would be to borrow the concept of multi-vector search but apply it to single-vector search by splitting a query into several smaller ones. However, matching three query words to three document words is also problematic, because it raises the question of which words to choose. Using all possible combinations would essentially turn it back into multi-vector search.

A more reasonable approach might be to ask an LLM to extract truly key terms from both the query and the documents, keep their number small, and still rely on multi-vector search. In general, combining multi-vector search with keyword-based retrieval seems promising, where the query is optimized in a Google-like manner and documents are filtered or indexed by keywords.

## Questions To Answer Still:
Does PlanExecutor has to have exactly the same memory subsystem as ReAct workers? Because I thought ReAct workers have one memory system.

Concept mentioned by Manus AI CEO on Langchain webinar (which he saw in [programming languages](https://go.dev/blog/codelab-share)): “Do not communicate by sharing memory;
instead, share memory by communicating.”

## Benchmarks for Memory

Passing the TACXXL Benchmark 

It would be desirable to design a set of tasks in which the agent, for example:

Performs repeated actions with specific edge cases or constraints, where the first obvious solution does not work (e.g., a tool fails). When the same or a similar task is encountered again, the agent should immediately leverage episodic memory (and possibly semantic memory as well).

Solves tasks based on user preferences, similar to how ChatGPT remembers a user’s preferences. This could even include asking, “What do you know about me?”, although this is closer to autobiographical memory.

In other words, these should be tasks where activating different types of memory meaningfully improves the agent’s performance.

LoCoMo

---

## Ideas

MMR (Maximum Marginal Relevance) — for retrieving very similar and contradictory information