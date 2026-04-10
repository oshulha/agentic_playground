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