# My Memory Conceptual Architecture v1

Memory subsystem is the information storage and retrieval part of our AI Agent. It consists of a single vector store that contains several collections. It directly interacts with the Brains subsystem (PlanExecutor and ReAct) and operates at multiple levels, such as storing memories from the PlanExecutor as well as memories from each ReAct worker invoked by the PlanExecutor. At the moment, our Memory subsystem is composed of four underlying memory components: working, episodic, semantic, and procedural memory.

## Working Memory

Working memory is what helps you keep track of information you are using right now and make sense of it as things change. For our Agents, it means remembering **the current conversation** and using it to respond properly in real time. 

At the moment, we can say that OpenAI provides a solution for working memory, but maintaining a consistently growing list of all user inputs, tool calls, tool outputs, and reasoning items—appended each time the agent receives inputs and produces outputs—looks like not the best solution.

There is where Context Engineering methods like compaction and summarization come into play.

[Here can be explained difference between this two methods and how, when to use each and details of implementation. compaction -- compact, summarization -- rewind. This way summarization can be the way of forgeting? [link](https://drive.google.com/file/d/1QGJ-BrdiTGslS71sYH4OJoidsry3Ps9g/view)]

Working memory acts as an active workspace that manages information between episodic experience retrieval and semantic knowledge access, while keeping track of the exact state of the current interaction.

To be continued...?

## Episodic Memory

Episodic memory is a historical collection of prior experiences, or episodes. It includes what happened, how it happened, and the lessons or insights learned from those experiences, even if they were never clearly stated.

For our agents, this includes past conversations from all ReAct workers, one-sentence summaries of what was done in the immediately preceding conversation, and structured fields such as what_worked and what_to_avoid. The what_worked field captures the most effective approaches and strategies used (as well as information that can be leveraged in subsequent iterations?). The what_to_avoid field records critical pitfalls, ineffective approaches, and factors that may lead the agent down incorrect paths or into dead ends.
It has to be saved in smth like in a JSON/Python dictionary into vector database collection named `episodic_memory`?

The creation of the JSON (or Python dictionary / string) is performed by the ReAct agent at the end of the its execution, not necessarily after a successful outcome.

Then, a vector (semantic) search is performed when a new ReAct worker is invoked by the PlanExecutor to retrieve the JSON (or Python dictionary) with the highest semantic similarity to the user prompt. The retrieved entry is then injected into the system prompt with the phrasing: “Here is what you recall about your task: {dict_best_match}”.

[This approach can be improved by reading `Reflexion` paper, in particular by considering Evaluator/Critic role. Still vector database retrieval is bad, this is where we need to improve a lot. As example, we can use as an idea/mechnism [recent paper](https://arxiv.org/pdf/2512.24601). - Much more effective, still not the best, isn't very cost-effective solution (but better than giving whole context to llm), have pretty big latency(maybe use cheap and fast llm) -- looks like whole agent. Also, episodic memory can be trigerred on some words like "always do like this", "good workflow to make this" and save it what user want ot mention. That's examples I saw in [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D) video from langchain. Their agent saves such replics to agents.md. I hope their Deep Agent is open-source.]

## Semantic Memory

Semantic memory represents our structured knowledge of facts, concepts, and their relationships - essentially what we "know" rather than what we "remember experiencing."
For our Agents, this would be implemented through techniques like Retrieval Augmented Generation (RAG), where relevant information is dynamically pulled from a knowledge base to ground and inform responses.

Detailed Implementation
Much of the organizational information already exists in sources such as Confluence, Jira, Slack, GitHub, and Google Drive. This information can be treated as factual knowledge.

It would be valuable to capture additional facts during the agent's execution. For example, we can include a structured output field called semantic_memory at the end of the agent's run, where it records all facts observed throughout the execution or task completion. Since the agent still has access to its working memory, it can populate this field with relevant knowledge. 

Because the final structured response may become very large/overwhelming, it may be necessary to split it into multiple separate responses to get high-quality answers. (think about approach?)

All collected information should be stored in a vector database collection named semantic_memory, using high-quality chunking. For example, chunking can be based on markdown formatting or a recursive character chunker, taking advantage of [ChromaDB's custom chunkers](https://research.trychroma.com/evaluating-chunking)(or it is the same?).

When a new ReAct worker is invoked by the PlanExecutor, a semantic (vector) search retrieves the top 10 chunks most semantically similar to the user prompt. These chunks are then injected into the end of user prompt with a phrasing like:

“Here are some facts and knowledge that may be relevant to your task and help you complete it: {dict_best_match}”

[Have to consider watching [RAG videos](https://www.youtube.com/watch?v=6vG_amAshTk&list=PL31XFvSmiPKEMco1JXKtIBttlAOOxE8aO) and consider doing some Agentic RAG, inspiring by [RLM](https://arxiv.org/pdf/2512.24601)]

[Also has troubles with high-quality retrieval]

## Procedural Memory

Procedural memory is different from working, semantic, and episodic memory since it covers more how we actually remember to perform tasks or follow a familiar routine, i.e. riding a bike or typing on a keyboard. It's the "how to do things" type of memory, distinct from factual knowledge (semantic) or specific experiences (episodic). 

In our system, we adopt a simplified implementation. Procedural memory is represented as a list of up to 10 concise instructions that guide the agent’s behavior. These instructions are derived from episodic memory.

After each ReAct agent execution, the system aggregates the existing what_worked and what_to_avoid entries with newly generated insights obtained during the Reflexion stage. Based on this updated information, the procedural memory is revised by updating the list of 10 instructions.

At the first invocation of a ReAct agent, the procedural memory is initialized as empty.

[In this design, procedural memory closely resembles an agents.md-style guideline file. However, alternative approaches should be considered!!!
For example, in the LangChain [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D)
video, the system incrementally updates an agents.md file and may eventually promote accumulated knowledge into an explicit “skill.” But looks like not very reliable idea at the moment.]

---

## Questions To Answer Still:
Does PlanExecutor has to have exactly the same memory subsystem as ReAct workers? Because I thought ReAct workers have one memory system.

Concept mentioned by Manus AI CEO on Langchain webinar (which he saw in [programming languages](https://go.dev/blog/codelab-share)): “Do not communicate by sharing memory;
instead, share memory by communicating.”