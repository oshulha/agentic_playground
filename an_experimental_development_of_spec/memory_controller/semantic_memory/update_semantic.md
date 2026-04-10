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

