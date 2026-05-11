# Codex Endpoint Breakdown

Цей документ фіксує першу версію маппінгу між V2 memory tools і V1 tools, а також розкладає ключові пайплайни по кроках.

## 1. V1 tools inventory

### Core workflow tools

| V1 tool | Role | Main flow | Notes |
|---|---|---|---|
| `add` | Приймає сирі дані та зберігає їх у dataset | `setup` -> `resolve_authorized_user_dataset` -> `resolve_dlt_sources` -> `reset_dataset_pipeline_run_status` -> `run_pipeline("add_pipeline")` | Лише ingestion/persistence. Не будує knowledge graph. |
| `cognify` | Перетворює вже додані дані в dataset на knowledge graph | `get_default_tasks()` або `get_temporal_tasks()` -> `run_pipeline("cognify_pipeline")` | Це основний graph-building етап. |
| `memify` | Збагачує вже існуючий граф | `get_default_memify_extraction_tasks()` + `get_default_memify_enrichment_tasks()` -> `run_pipeline("memify_pipeline")` | За замовчуванням це enrichment pipeline для існуючого графа. |
| `search` | Шукає по knowledge graph | `log_query` -> `authorized_search` -> `get_retriever_output` | Працює з `SearchType`-режимами. |
| `delete` | Deprecated wrapper для видалення data item | Делегує в `datasets.delete_data(...)` | Старий V1 entrypoint, зараз краще використовувати `datasets.delete_data`. [Більше деталей](https://docs.cognee.ai/python-api/delete)|
| `update` | Повна заміна одного data item | `datasets.delete_data(...)` -> `add(...)` -> `cognify(...)` | Це delete-then-read цикл для конкретного `data_id`, а не окремий generalized endpoint behavior. [Більше деталей](https://docs.cognee.ai/python-api/update)|

**Tool:** `add()`

**`add_pipeline` (short version)**

| Order | Task |
|---|---|
| 1 | `resolve_data_directories` |
| 2 | `ingest_data` |

**Add Pipeline: (detailed version)**
-> resolve_data_directories() # папки перетворюємо у шляхи файлів
-> ingest_data()
   -> save_data_item_to_storage(...)# зберігається оригінальні сирі дані metadata + data у файл
      -> save_data_to_file(...)
         -> classify(file) # TextData BinaryData S3BinaryData
         -> get_metadata()
         -> get_data()
         -> storage.store(...) # зберігається оригінальні сирі дані metadata + data у файл text_<content_hash>.txt
   -> data_item_to_text_file(...)  # зберігається текстові нормалізовані дані у файл text_<raw_content_hash>.txt, далі використовуються в cognify
   -> open_data_file(original_file_path)
        -> classify(file) # TextData BinaryData S3BinaryData
        -> get_metadata()   # original/raw file metadata
        -> identify(...) # створює data_id = стабільний UUID для Datarow, який є UUID5, детерміновано згенерований із content_hash + user + tenant
   -> open_data_file(cognee_storage_file_path)
       -> classify(file) # TextData BinaryData S3BinaryData
       -> get_metadata()   # normalized text file metadata
   -> create/update Data
   -> create/update Dataset
   -> DatasetData (many-to-many link between Data and Dataset)
   -> commit to RelationalDB

**What it does and Notes:**

Якщо content_hash == raw_content_hash, то не перезаписують файл, бо overwrite=False за замовчуванням. Тобто для plain text(простого тексту) data_item_to_text_file() часто просто повертає той самий шлях і нічого реально не дублює. 

Для інших типів даних уже може бути реально інша текстова репрезентація:
https://... -> спочатку зберігається HTML/raw, потім loader може витягнути чистий текст і зберегти окремий text_*.txt. Для CSV, PDF, image, audio це теж окрема нормалізована текстова форма

Кілька dataset можуть бути потрібні, щоб розділяти різні області знань, права доступу, окремий graph scope cognify(datasets=[...]) працює по вибраних dataset-ах, окреме видалення і оновлення (delete_dataset_nodes_and_edges(dataset_id, ...)).
nodes/edges мають dataset_id, тобто вони прив’язані до конкретного dataset-а. Скоріше логіка така: 
Dataset A -> свій підграф, tagged dataset_id = A
Dataset B -> свій підграф, tagged dataset_id = B
обидва живуть в одному graph DB.
Можливість створення датасетів належить лиш користувачу.

`Data` клас має такі поля:
- `id`
  - UUID запису `Data` #hash(content_hash + user_id + tenant_id)
  - стабільний ідентифікатор data item у БД
- `label`
  - необов’язкова людська мітка
  - може приходити з `DataItem.label`
- `name`
  - назва data item
  - зазвичай береться з `original_file_metadata["name"]`
- `extension`
  - розширення **normalized text file**
  - наприклад `txt`, `csv`, `pdf`
- `mime_type`
  - MIME type **normalized text file**
  - наприклад `text/plain`, `application/pdf`
- `original_extension`
  - розширення **original/raw file**
- `original_mime_type`
  - MIME type **original/raw file**
- `loader_engine`
  - назва loader-а, який перетворив raw file у text-normalized file
- `raw_data_location`
  - шлях до **normalized text file** у storage
  - назва трохи збиває з пантелику, але в коді туди кладеться `cognee_storage_file_path`
- `original_data_location`
  - шлях або URI до **original/raw file**
- `owner_id`
  - UUID користувача, якому належить data item
- `tenant_id`
  - UUID tenant-а, якщо система його використовує
  - може бути `None`
- `content_hash`
  - hash вмісту **original/raw file**
  - використовується як content fingerprint
- `raw_content_hash`
  - hash вмісту **normalized text file**
- `external_metadata`
  - додаткові метадані, які прийшли з `DataItem.external_metadata`
  - сюди також можуть додаватися інші поля, наприклад `node_set`
- `node_set`
  - JSON-serialized список node set names
  - тобто які graph node sets пов’язані з цим data item
- `pipeline_status`
  - mutable JSON-словник статусів pipeline-етапів
  - наприклад, що вже оброблено, що ні
  - для нових записів ініціалізується як `{}`
- `token_count`
  - кількість токенів
  - у ingestion зараз ставиться `-1`, якщо ще не пораховано
- `data_size`
  - розмір original/raw file у байтах
- `created_at`
  - час створення запису в БД
- `updated_at`
  - час останнього оновлення запису
- `last_accessed`
  - час останнього доступу до data item
  - може бути `None`
- `importance_weight`
  - вага важливості data item
  - використовується як пріоритет/сигнал для подальшої обробки або ранжування


Ось колонки моделі Dataset:
id
name
created_at
updated_at
owner_id
tenant_id

relationship-поля:
acls
configuration
data

### Namespace tools

#### `config`

| Tool | What it changes | Notes |
|---|---|---|
| `set_llm_provider` | LLM provider | Mutates the runtime config in memory. |
| `set_llm_model` | LLM model | Used by completion and extraction flows. |
| `set_llm_api_key` | LLM API key | Process-local override. |
| `set_llm_endpoint` | LLM endpoint URL | For custom/self-hosted endpoints. |
| `set_llm_config` | All LLM config fields at once | Bulk update with attribute validation. |
| `set_embedding_provider` | Embedding provider | Affects vectorization backend. |
| `set_embedding_model` | Embedding model | Controls embedding model selection. |
| `set_embedding_dimensions` | Embedding vector size | Validated as a positive integer. |
| `set_embedding_endpoint` | Embedding endpoint URL | For custom embedding services. |
| `set_embedding_api_key` | Embedding API key | Process-local override. |
| `set_embedding_config` | All embedding config fields at once | Bulk update with dimension coercion. |
| `set_graph_database_provider` | Graph DB provider | Selects graph backend. |
| `set_graph_db_config` | All graph DB config fields at once | Bulk update for graph storage settings. |
| `set_graph_model` | Graph extraction model | Changes graph schema/model used in cognify. |
| `set_vector_db_provider` | Vector DB provider | Selects vector store backend. |
| `set_vector_db_url` | Vector DB URL | Connection target for vector DB. |
| `set_vector_db_key` | Vector DB API key | For authenticated vector backends. |
| `set_vector_db_config` | All vector DB config fields at once | Bulk update for vector storage settings. |
| `set_chunk_size` | Chunk size | Influences text chunking in ingestion/cognify. |
| `set_chunk_overlap` | Chunk overlap | Controls overlap between chunks. |
| `set_chunk_strategy` | Chunking strategy | Selects chunking behavior. |
| `set_chunk_engine` | Chunking engine | Selects implementation backend. |
| `set_classification_model` | Classification model | Used in cognify classification step. |
| `set_summarization_model` | Summarization model | Used in summarization step. |
| `system_root_directory` | System root directory | Cascades into DB/storage paths. |
| `data_root_directory` | Data root directory | Controls raw file storage location. |
| `monitoring_tool` | Monitoring backend | Hooks observability tooling. |
| `set_translation_provider` | Translation provider | For translation features. |
| `set_translation_target_language` | Translation target language | Sets default translation target. |
| `set_translation_config` | All translation config fields at once | Bulk update for translation settings. |
| `set(key, value)` | Any recognized config key | Generic setter for CLI and programmatic use. |

[Details](https://docs.cognee.ai/python-api/config)

#### `prune`

| Tool | What it removes | Notes |
|---|---|---|
| `prune_data()` | Raw files from file storage backend | Uses `DATA_ROOT_DIRECTORY` for storage config (for example, local disk or S3). |
| `prune_system(graph=True, vector=True, metadata=False, cache=True)` | Graph DB, vector store, metadata DB, cache depending on flags | `metadata=False` by default to reduce accidental data loss. |

[Details](https://docs.cognee.ai/python-api/prune)

#### `datasets`

| Tool | What it does | Notes |
|---|---|---|
| `list_datasets` | Returns datasets accessible to the user | Uses read access checks. |
| `discover_datasets` | Lists datasets discovered in a directory | Local filesystem discovery helper. |
| `list_data` | Returns data items for a dataset | Requires dataset access. |
| `has_data` | Checks whether dataset has data | Boolean helper for dataset state. |
| `get_status` | Returns cognify pipeline status for datasets | Tracks `cognify_pipeline` state. |
| `empty_dataset` | Deletes all data and graph artifacts for a dataset | Removes dataset contents but not all user data globally. |
| `delete_data` | Deletes one data item from a dataset | Can optionally delete the dataset if it becomes empty. |
| `delete_all` | Deletes all datasets for the user | Iterates through all accessible datasets and empties them. |

[Details](https://docs.cognee.ai/python-api/datasets)

#### `session`

| Tool | What it does | Notes |
|---|---|---|
| `get_session` | Returns session QA entries from session cache | 1. User makes query. 2. Then LLM generates response according to user query and relevant context from memory system. 3. Generates QA entry and then inserts into session cache|
| `delete_feedback` | Clears feedback for a QA entry | Sets feedback fields back to `None`. Doesn't reset memify_status to False (hmm...)|

**Tool:** `add_feedback`

**What it does and Notes:** Stores `feedback_text`, `feedback_score`, and resets memify status (memify doesn't re-run automatically). 
`feedback_score` is a mark from 1 to 5, where 5 is maximum(positive feedback) and 1 is minimum(negative feedback). 

Can be called directly by the user and then `feedback_text`, `feedback_score` is set by user.

It is also invoked automatically before the LLM generates a response if the LLM determines that the user message is feedback on the previous assistant(LLM) response. 

This way LLM detects using such structured output schema: `feedback_detected: bool`, `feedback_text: str`, `feedback_score: number from 1 to 5`, `response_to_user: str`, `contains_followup_question: bool` 

Then feedback is saved to session cache to corresponding QA entry and then sets memify_metadata["feedback_weights_applied"] = False to corresponding QA entry in order to memify/improve could process this QA entry once again.

**Prompt used:** 
```python
"""You analyze user messages in a Q&A session. Only treat a message as feedback when the user is explicitly evaluating the correctness, accuracy, or quality of the previous answer (the last response they received)—i.e. they are validating or commenting on whether the answer was right, wrong, helpful, or accurate.

Set feedback_detected to true ONLY when the user is clearly commenting on the previous answer itself, for example:
- Saying the answer was wrong or right (e.g. "that was wrong", "correct", "not quite", "yes that's right")
- Correcting the answer (e.g. "the date was 2020, not 2021", "it's actually X")
- Rating or scoring the answer (e.g. "5/5", "3 stars")
- Thanks or praise directed at the answer (e.g. "thanks, that was helpful", "perfect answer")
- Short confirmation or rejection of the answer (e.g. "nope", "yes", "wrong")

Set feedback_detected to false when:
- The message is a new question or request for information (e.g. "What is the capital of France?", "How does X work?")
- The message is a follow-up question (e.g. "can you elaborate?", "what about X?")
- The message is only a reaction to the topic or subject matter, not to the correctness of the answer (e.g. "that place is nice", "oooh interesting", "I've been there")—these do not validate whether the answer was correct or wrong.

The message may contain BOTH feedback AND a follow-up question (e.g. "that was wrong, but what about X?", "thanks! Can you also explain Y?"). When feedback_detected is true, set contains_followup_question to true only if the user is asking a distinct new or follow-up question in the same message that should be answered. Otherwise set contains_followup_question to false.

When feedback_detected is true you MUST always provide feedback_text, feedback_score, response_to_user, and contains_followup_question. feedback_text must NEVER be empty.

response_to_user: Generate a brief, friendly message (one sentence) to show the user in reply—e.g. thanking them for their feedback. Simply acknowledge and accept the feedback; be kind. Do NOT ask follow-up questions (e.g. do not ask "Could you provide more details?", "What was incorrect?", "Can you elaborate?"). Just thank them or acknowledge; do not invite the user to elaborate. You may adapt tone or language to match the user's message (formal/informal, language). Examples: "Thanks for your feedback!", "We appreciate you letting us know.", "Thank you for the feedback—it helps us improve.", "I'm sorry that wasn't right—thanks for letting us know."

feedback_text: Write a short description (one or two sentences) that includes what the user said and why it counts as feedback. Incorporate the user's words either by quoting them or by summarizing. Examples:
- "User said 'that was wrong — the date was 2020': correction of the previous answer."
- "User expressed thanks: 'that was helpful, exactly what I needed.' Positive feedback."
- "User gave a rating (5/5): positive feedback on the previous response."
- "User said 'nope' or 'correct': short reactive feedback on the previous answer."
So the reader understands both what the user sent and why it was detected as feedback. Keep it concise (e.g. under 300 characters).

feedback_score: Map to a scale of 1-5 (1 = negative, 5 = positive). E.g. "5/5" -> 5, "that was wrong" -> 1, "thanks" -> 5. Use 3 (neutral) if no clear score can be inferred.

Respond with the exact JSON structure: feedback_detected (boolean), feedback_text (string, required when feedback_detected is true), feedback_score (number 1-5, required when feedback_detected is true), response_to_user (string, required when feedback_detected is true—message to show the user), contains_followup_question (boolean, required when feedback_detected is true—true if the message also asks a new or follow-up question to answer).
"""
```

**Pipeline of Auto-detected Feedback In Conversation:** <br/>
Якщо user_query2 = лише feedback: <br/>
    user_query1 -> llm_answer1 -> add_qa(QA1) (в session_cache) -> user_query2 -> generate_completion(query2) і detect_feedback(query2) ідуть паралельно -> detect_feedback=True -> add_feedback(...) (оновлює QA1 у session cache) -> система одразу повертає истема одразу повертає response_to_user (add_qa(...) для query2 не викликається)

Якщо user_query2 = feedback + follow-up question: <br/>
    detect_feedback=True -> add_feedback(...) оновлює QA1 -> потім add_qa(...) зберігає QA2 = user_query2 + llm_answer2 -> користувач отримує response_to_user + llm_answer2

#### `visualize`

| Tool | What it does | Notes |
|---|---|---|
| `visualize_graph` | Generates graph visualization for the current user graph | Returns HTML visualization output. |
| `visualize_multi_user_graph` | Generates visualization across multiple user/dataset pairs | Aggregates graphs before rendering. |

#### `start_ui`

| Tool | What it does | Notes |
|---|---|---|
| `start_ui` | Starts the frontend UI, optionally backend API and MCP server | Handles port checks, frontend discovery/download, and process spawning. |

#### `run_custom_pipeline`

| Tool | What it does | Notes |
|---|---|---|
| `run_custom_pipeline` | Runs arbitrary task pipelines over data and datasets | Lower-level pipeline entrypoint for custom workflows. |

## 2. V2 -> V1 mapping

| V2 tool | What it does | Closest V1 tool(s) | Why this mapping is accurate |
|---|---|---|---|
| `remember` |  | without `session_id`: `add` + `cognify` + (if `self_improvement=True`, then `improve` runs in background); with `session_id`: also uses session cache | `remember()` routes to two different branches. Permanent branch runs `add -> cognify -> improve`, session branch stores QA in cache and then if  spawn `improve` in background. |
| `recall` | Retrieve information; can search session cache first, then graph | `search` | `recall()` is a router over `search`, adding session-first fallback and query routing. |
| `improve` | Enrich existing knowledge graph and optionally bridge sessions | `memify` | `improve()` uses `memify()` for the enrichment stage, and adds session feedback/session sync around it. |
| `forget` | Delete data item, dataset, or everything | `delete`, `datasets.delete_data`, `datasets.empty_dataset`, `datasets.delete_all`, `prune` | `forget()` is the unified deletion facade over the older dataset/delete/prune primitives. |

`remember` 
`run_in_background=True`, тоді remember() одразу повертає RememberResult(status="running")
`run_in_background=False`, тоді remember() одразу нічого не повертає і поверне RememberResult(status="completed") лише після того, як завершаться всі кроки

- with `session_id` and self_improvement=True: 
1) перетворює data у текст через _data_to_text(...) 
2) зберігає один QA entry у session cache через _add_to_session(...) <br/>
QA entry виглядає приблизно: <br/>
question="" <br/>
context="" <br/>
answer=<текстове представлення data> <br/>
повертає одразу `status="session_stored"`
improve(...) запускається in background

- with `session_id` and self_improvement=False: 
1) перетворює data у текст через _data_to_text(...) 
2) зберігає один QA entry у session cache через _add_to_session(...) <br/>
QA entry виглядає приблизно: <br/>
question="" <br/>
context="" <br/>
answer=<текстове представлення data> <br/>
повертає одразу `status="session_stored"`
improve(...) не запускається

- without `session_id` and self_improvement=True: <br/>
`add` + `cognify` + (`improve` in background)

- without `session_id` and self_improvement=False: <br/>
`add` + `cognify`

### `recall`
`recall(query_text, ...)` behaves like this:

1. if `session_id` is provided, no `datasets` are set, and `query_type` is not passed, it first searches the session cache by keyword overlap
2. if session search returns results, it stops there
3. otherwise it falls through to graph search
4. `query_type` is chosen by:
   - explicit `query_type`, or
   - rule-based `route_query()` when `auto_route=True`, or
   - default `GRAPH_COMPLETION` when `auto_route=False`

There is no default “multi-search aggregation” over several search types. The system picks one search type per query.

### `improve`
`improve(dataset=..., session_ids=...)` has two modes:

#### Without `session_ids`
Only the enrichment stage runs:
1. `memify(...)`

#### With `session_ids`
The full session-bridge flow is:
1. apply feedback weights from session QA entries
2. persist session Q&A into the permanent graph
3. run `memify(...)` for enrichment
4. sync graph knowledge back into session cache

So `memify` is stage 3 of 4 in the session-aware branch, not the whole `improve()` story.

### `forget`
`forget(...)` is a unified deletion method:
1. `everything=True` -> delete all datasets for the user and prune session cache
2. `dataset=...` -> empty that dataset
3. `data_id + dataset` -> delete a single data item from a dataset

## 4. Available search types

`SearchType` currently includes:

- `SUMMARIES`
- `CHUNKS`
- `RAG_COMPLETION`
- `TRIPLET_COMPLETION`
- `GRAPH_COMPLETION`
- `GRAPH_COMPLETION_DECOMPOSITION`
- `GRAPH_SUMMARY_COMPLETION`
- `CYPHER`
- `NATURAL_LANGUAGE`
- `GRAPH_COMPLETION_COT`
- `GRAPH_COMPLETION_CONTEXT_EXTENSION`
- `FEELING_LUCKY`
- `TEMPORAL`
- `CODING_RULES`
- `CHUNKS_LEXICAL`

GRAPH_COMPLETION (Default - Recommended): Natural language Q&A using full graph context and LLM reasoning. Best for: Complex questions, analysis, summaries, insights. Returns: Conversational AI responses with graph-backed context.

RAG_COMPLETION: Traditional RAG using document chunks without graph structure. Best for: Direct document retrieval, specific fact-finding. Returns: LLM responses based on relevant text chunks.

CHUNKS: Raw text segments that match the query semantically. Best for: Finding specific passages, citations, exact content. Returns: Ranked list of relevant text chunks with metadata.

SUMMARIES: Pre-generated hierarchical summaries of content. Best for: Quick overviews, document abstracts, topic summaries. Returns: Multi-level summaries from detailed to high-level.

CODE: Code-specific search with syntax and semantic understanding. Best for: Finding functions, classes, implementation patterns. Returns: Structured code information with context and relationships.

CYPHER: Direct graph database queries using Cypher syntax. Best for: Advanced users, specific graph traversals, debugging. Returns: Raw graph query results.

FEELING_LUCKY: Intelligently selects and runs the most appropriate search type. Best for: General-purpose queries or when you’re unsure which search type is best. Returns: The results from the automatically selected search type.

CHUNKS_LEXICAL: Token-based lexical chunk search (e.g., Jaccard). Best for: exact-term matching, stopword-aware lookups. Returns: Ranked text chunks (optionally with scores).


`recall()` does not run all of them at once. It selects one type per request, then calls `search(...)`.

## 5. Feedback in `improve`

Feedback is not an abstract score computed on the fly. It comes from session QA entries that already store:

- `feedback_score` in the range 1..5
- `used_graph_element_ids` with `node_ids` and/or `edge_ids`
- `memify_metadata` to mark whether feedback weights were already applied

The pipeline does:

1. read eligible(доступні) QA entries from session cache
2. normalize score 1..5 into 0..1
3. update node/edge feedback weights
4. mark the QA entry as processed

Feedback can be set explicitly through session QA update methods, and it can also be captured automatically from chat feedback detection. The session manager exposes `add_feedback(...)`, `update_qa(...)`, and `delete_feedback(...)`.

Feedback can be added explicitly or captured automatically. Feedback can be deleted explicitly.

## Task-list answers

### `recall` with and without `session_id`

Yes, `recall()` also has a session-aware split.

- With `session_id` and no explicit `datasets` or `query_type`, it first searches session cache.
- Otherwise it falls back to graph search.

How search is chosen:

1. explicit `query_type` wins
2. else `route_query()` decides when `auto_route=True`
3. else default is `GRAPH_COMPLETION`

So the system does not perform parallel hybrid search by default. It chooses one search mode. The only “multi” part is that the same query can be executed across multiple datasets when access control is enabled.

### `improve` with and without `session_ids`

Yes, there is a split.

- Without `session_ids`, `improve()` is basically enrichment through `memify()`.
- With `session_ids`, it first applies feedback weights, then persists session Q&A, then runs `memify()`, then syncs graph knowledge back to session cache.

“Enrichment of an existing graph” means deriving extra structure or higher-value knowledge from already ingested data or existing graph fragments, not re-ingesting raw data from scratch.

### Feedback source

Feedback comes from session QA entries.

The important fields are:

- `feedback_score` 1..5
- `used_graph_element_ids`
- `memify_metadata`

In the session manager, `add_feedback(...)` stores feedback for a QA entry and resets the memify status so the feedback can be applied later. Auto-feedback detection can also fill these fields from chat interactions.

### 6.6 Improve stages

Your intuition is close, but the current code has **four** stages when `session_ids` are provided, not three.

1. apply feedback weights
2. persist session Q&A
3. `memify()`
4. sync graph back to sessions

So `memify()` is stage 3 of 4 in the session-aware path.

## Pipeline tables

Даний параметр задається користувачем, але за замовчуванням `temporal_cognify=False`.
(і також через remember(...), бо temporal_cognify входить у kwargs, які remember() передає в cognify())
`temporal_cognify=False` -> default flow
`temporal_cognify=True` -> temporal flow
Це не окремі бази даних чи графи у графовій БД, а різні pipeline-логіки для одного graph backend

### `cognify_pipeline` default flow

| Order | Task | Purpose |
|---|---|---|
| 1 | `classify_documents` | Classify raw items into document types |
| 2 | `extract_chunks_from_documents` | Split documents into semantic chunks |
| 3 | `extract_graph_from_data` | Extract entities and relations. Contains `extract_content_graph(...)` for every DocumentChunk and `expand_with_nodes_and_edges(...)` |
| 4 | `summarize_text` | Build hierarchical summaries |
| 5 | `add_data_points` | Persist nodes, edges, embeddings |
| 6 | `extract_dlt_fk_edges` | Add foreign-key-style structural edges |

**Опції в cognify():**

`graph_model:`
Це Pydantic-модель графа, яку LLM має заповнити під час extraction.
Користувач може задати даний параметр.

- За замовчуванням: KnowledgeGraph
- Якщо передати іншу модель, то extract_graph_from_data() буде витягувати структуру графа під твою схему, а не під загальний формат.
- Тобто це змінює форму knowledge graph, а не просто “стиль відповіді”.

`custom_prompt:`
Це додатковий prompt для LLM extraction.
Користувач може задати даний параметр.

- Йде в extract_graph_from_data(...)
- Може підказати моделі, як саме витягувати entities/relations
- Корисно, якщо тобі потрібні особливі правила для домену
наприклад: legal, medical, code, research papers
- Тобто це змінює інструкцію для extraction, а не сам pipeline. Див. extract_graph_from_data.py.

`chunks_per_batch:`
Це розмір batch-ів, якими pipeline обробляє chunks.
Користувач може задати даний параметр.

- Передається як task_config={"batch_size": chunks_per_batch}
- Впливає на те, скільки chunks/graphs обробляється за один раз
- Більше значення = менше overhead, але більше memory/latency risk
- Менше значення = повільніше, але обережніше по ресурсах. Див. cognify.py.

`triplet_embedding:`
Це не аргумент cognify() напряму, а налаштування в cognify_config. Тобто звичайний користувач не може задати цей параметр.

- Якщо True, add_data_points(...) після побудови графа ще створює і індексує triplet embeddings
- Тобто система окремо векторизує триплети source - relation - target
- Це покращує retrieval по зв’язках між вузлами. Див. cognify.py, add_data_points.py.

**Що робить `classify_documents`**
`classify_documents(...)` **перетворює `Data`-records у typed `Document`-objects** залежно від: `extension` та чи data є DLT-sourced
Тобто логіка така:
- якщо data прийшов із DLT -> `DltRowDocument`
- інакше:
  - `pdf` -> `PdfDocument`
  - `txt` -> `TextDocument`
  - `csv` -> `CsvDocument`
  - `png/jpg/...` -> `ImageDocument`
  - `mp3/wav/...` -> `AudioDocument`
  - інші типи office/docs -> `UnstructuredDocument`

`classify_documents(...)` повертає list of `Document` objects.

Кожен `Document` створюється з полями:
- `id = data_item.id`
- `title = f"{data_item.name}.{data_item.extension}"`
- `raw_data_location`
- `name`
- `mime_type`
- `external_metadata`
- `importance_weight`

**Наступний етап `extract_chunks_from_documents(...)` читає ці `Document`-об’єкти і ріже їх на chunks.**
Для кожного `Document` викликає:
   - `async for document_chunk in document.read(max_chunk_size=max_chunk_size, chunker_cls=chunker):`
`document.read(...)` уже сам вирішує, як витягнути текст з raw data.
- потім `TextChunker` ділить текст на абзаци через `chunk_by_paragraph(...)`.
- він накопичує абзаци, поки сумарний розмір не перевищить `max_chunk_size`.
- коли ліміт досягнуто, він повертає `DocumentChunk`.

Що повертається
На виході `extract_chunks_from_documents(...)` повертає або:
- потік `DocumentChunk`-ів, коли читає документ,
- і фактично `DocumentChunk`-и йдуть далі в pipeline.

Кожен `DocumentChunk` має, зокрема:
- `id`
- `text`
- `chunk_size`
- `is_part_of` = вихідний `Document`
- `chunk_index`
- `cut_type`
- `importance_weight`
- `metadata={"index_fields": ["text"]}`

Фактично межа chunk-a формуються так:
- спочатку `chunk_by_word(...)` дає низькорівневі word/paragraph markers
- потім `chunk_by_sentence(...)` перетворює це на sentence-like segments
- потім `chunk_by_paragraph(...)` збирає ці segments у більші chunk-и, поки не досягне `max_chunk_size`

**Далі `extract_graph_from_data()` приймає `list[DocumentChunk]`.**
`extract_graph_from_data()` бере chunks і перетворює їх у graph-shaped data:
- `graph_model` задає схему, під яку LLM має витягнути граф
- `custom_prompt` може змінити інструкцію для extraction
- DLT chunks обробляються окремо, без LLM extraction

### Простий flow
1. Розділяє chunks на:
   - `dlt_chunks`
   - `non_dlt_chunks`
2. Для `non_dlt_chunks`:
   - або викликає `calculate_chunk_graphs(...)`, якщо переданий кастомна функція (за замовчування не передається)
   - або паралельно запускає `extract_content_graph(chunk.text, graph_model, custom_prompt=...)` для кожного chunk
3. Якщо `graph_model == KnowledgeGraph`, додатково відфільтровує edges, щоб вони не посилались на неіснуючі nodes.
4. Вибирає ontology resolver з `config` або з env.
5. Викликає `integrate_chunk_graphs(...)`, який:
   - для кастомного `graph_model` просто ставить `chunk.contains = chunk_graph`
   - для `KnowledgeGraph` розгортає nodes/edges, дедуплікує їх, додає provenance, може кешувати embeddings
6. Повертається **список `DocumentChunk`-ів**, але вже з інтегрованою graph-структурою.

**Далі `summarize_text(...)` приймає list[DocumentChunk].**
Він:
- для non-DLT chunks викликає `extract_summary(chunk.text, summarization_model)`
- створює `TextSummary`-об’єкти
- DLT chunks пропускає без LLM summarization
- повертає список `TextSummary` + DLT chunks

Для чого? Він будує hierarchical summaries. У документації Cognee це означає, що summaries працюють як вищий рівень представлення над chunk-ами. Тобто: raw document -> chunks -> summaries. Ще використовується у для retrieval через summaries, наприклад SearchType.SUMMARIES

**Як `extract_content_graph` працює**
1. Приймає:
   - `content: str` - текст chunk-а
   - `response_model: Type[BaseModel]` - модель, у яку LLM має запакувати результат (по замовчуванню `KnowledgeGraph`)
   - `custom_prompt: Optional[str]` - опційний override prompt
2. Якщо `custom_prompt` передали:
   - він використовується як `system_prompt`
3. Якщо ні:
   - береться за замовчуванням `llm_config.graph_prompt_path`
4. Потім викликається:
   - `LLMGateway.acreate_structured_output(content, system_prompt, response_model, **kwargs)`
5. Повертається вже **parsed structured object**.

```python
class KnowledgeGraph(BaseModel):
    """Knowledge graph."""

    nodes: List[Node] = Field(..., default_factory=list)
    edges: List[Edge] = Field(..., default_factory=list)
```

Промпт у `extract_content_graph()`:
```python
"""
You are a top-tier algorithm designed for extracting information in structured formats to build a knowledge graph.
**Nodes** represent entities and concepts. They're akin to Wikipedia nodes.
**Edges** represent relationships between concepts. They're akin to Wikipedia links.

The aim is to achieve simplicity and clarity in the knowledge graph.
# 1. Labeling Nodes
**Consistency**: Ensure you use basic or elementary types for node labels.
  - For example, when you identify an entity representing a person, always label it as **"Person"**.
  - Avoid using more specific terms like "Mathematician" or "Scientist", keep those as "profession" property.
  - Don't use too generic terms like "Entity".
**Node IDs**: Never utilize integers as node IDs.
  - Node IDs should be names or human-readable identifiers found in the text.
**Node Names**: Every node MUST include a "name" field.
  - Use the most complete human-readable name for the entity (e.g., "Albert Einstein", "Python").
# 2. Handling Numerical Data and Dates
  - For example, when you identify an entity representing a date, make sure it has type **"Date"**.
  - Extract the date in the format "YYYY-MM-DD"
  - If not possible to extract the whole date, extract month or year, or both if available.
  - **Property Format**: Properties must be in a key-value format.
  - **Quotation Marks**: Never use escaped single or double quotes within property values.
  - **Naming Convention**: Use snake_case for relationship names, e.g., `acted_in`.
# 3. Coreference Resolution
  - **Maintain Entity Consistency**: When extracting entities, it's vital to ensure consistency.
  If an entity, is mentioned multiple times in the text but is referred to by different names or pronouns,
  always use the most complete identifier for that entity throughout the knowledge graph.
Remember, the knowledge graph should be coherent and easily understandable, so maintaining consistency in entity references is crucial.
# 4. Strict Compliance
Adhere to the rules strictly. Non-compliance will result in termination"""
```

**`ontology resolver` - це модуль, який намагається прив’язати витягнуті з тексту сутності до ontology**
Ontology = заздалегідь підготовлена схема/словник того домену, про який ти хочеш будувати граф(RDF / OWL файл), але ontology не є обов'язковим і за замовчуванням його немає. (RDF — стандарт для представлення даних у вигляді трійок: суб’єкт — предикат — об’єкт. Наприклад: Alice knows Bob. OWL — мова для опису онтологій поверх RDF. Дає змогу задавати класи, зв’язки, правила логіки тощо.)

**Що ontology resolver робить**
`expand_with_nodes_and_edges(...)` викликає:

- `ontology_resolver.get_subgraph(node_name=..., node_type="classes")`
- `ontology_resolver.get_subgraph(node_name=..., node_type="individuals")`

І далі:
- якщо знайдено близький ontology match, node стає `ontology_valid=True`
- додаються ontology nodes/edges
- entity/type назви можуть бути замаплені на ontology-імена

Тобто resolver допомагає:
- зв’язати extracted entity/type з ontology
- додати ontology-based ancestry / relations
- позначити, що node відповідає ontology

Але оскільки за замовчуванням немає ontology, то тоді expand_with_nodes_and_edges(...) просто:
- не замапить entity/type на ontology canonical names
- не додасть ontology-derived nodes/edges
- але все одно створить звичайні EntityType і Entity з LLM graph
- але без ontology-файлу він майже не додає ontology-specific enrichment

Якщо LLM з chunk-а витягнув щось на кшталт: 
```python
type = Person
name = Alice
description = a researcher
```
то система створює:
```python
EntityType(name="Person")
Entity(name="Alice", is_a=Person, description="a researcher")
```
Якщо chunk каже:
“Alice works at OpenAI”

то система може створити:
```python
EntityType("Person")
Entity("Alice", is_a=Person)
EntityType("Company")
Entity("OpenAI", is_a=Company)
```
І ще:
```python
DocumentChunk.contains -> (contains, Alice)
DocumentChunk.contains -> (contains, OpenAI)
```
Тобто chunk зберігає, які сутності в ньому знайдені.

**Далі `add_data_points(...)` бере вже готові `DataPoint`-об’єкти й перетворює їх у:**
- графові ноди
- графові ребра
- вектори/ембеддинги
- ще й у записи relational `nodes` / `edges` таблиць.

Спочатку з `DataPoint` дістаються nodes/edges
Для кожного вхідного `DataPoint` викликається `get_graph_from_model(...)`

`get_graph_from_model(...)` працює так:
- проходить по всіх полях об’єкта
- звичайні поля кладе як властивості ноди
- поля, які містять інші `DataPoint`-и або `Edge`-tuples, трактує як зв’язки

Наприклад:
- `Entity.is_a` -> дає ребро типу `is_a`
- `DocumentChunk.contains` -> дає ребро `contains`
- `Entity.relations` -> дає додаткові ребра між сутностями

Потім nodes/edges дедуплікуються. Після збору всіх результатів:
- `deduplicate_nodes_and_edges(...)` прибирає дублікати нод і ребер
- `ensure_default_edge_properties(...)` нормалізує властивості ребер, щоб усі мали базовий набір атрибутів

Це важливо, бо одна й та сама сутність може зустрітися в кількох chunks або кілька разів у вкладених об’єктах.

Далі дані пишуться у graph/vector backend. Потім `add_data_points(...)` бере глобальний unified engine:
- `unified.graph`
- `unified.vector`

І пише туди nodes/edges.

Тобто:
- graph backend отримує самі вузли/ребра
- vector backend отримує їх embedding representation

Далі відбувається `upsert` у relational `nodes` / `edges`.

Якщо в `ctx` є: `user`, `dataset`, `data_item`; тоді викликаються: `upsert_nodes(...)`, `upsert_edges(...)`.

Вони пишуть у relational таблиць: `nodes`, `edges`

Що саме там зберігається
Для `Node`:
- `id`
- `slug`
- `user_id`
- `data_id`
- `dataset_id`
- `label`
- `type`
- `indexed_fields`
- `attributes`

Для `Edge`:
- `id`
- `slug`
- `user_id`
- `data_id`
- `dataset_id`
- `source_node_id`
- `destination_node_id`
- `relationship_name`
- `label`
- `attributes`

Навіщо тут `dataset_id` і `data_id`
- `dataset_id` каже, до якого dataset належить нода/ребро
- `data_id` каже, з якого конкретного data item це прийшло
- `user_id` і `tenant_id` використовуються для стабільного UUID і ізоляції

Опційно створюються triplet embeddings
Якщо `embed_triplets=True`, функція:
- бере nodes/edges
- створює `Triplet`-об’єкти
- індексує їх у vector DB

Це окремий retrieval layer для запитів по триплетах `source - relation - target`.

Triplet =  
**`source node` - `relationship` - `target node`**

Наприклад:
- `Alice - works_at - OpenAI`
- `Paris - located_in - France`

Що робить `add_data_points(..., embed_triplets=True)`
Після того як nodes вже зібрані, edges вже зібрані. Функція викликає `_create_triplets_from_graph(nodes, edges)`.

`_create_triplets_from_graph(nodes, edges)` робить наступне:
1. будує `node_map` по `node.id`
2. проходить по кожному edge
3. бере:
   - source node
   - target node
   - relationship name
   - edge_text, якщо є
4. створює текстовий опис triplet-а:
   - `source_text -> relation -> target_text`
5. генерує `triplet_id`
6. створює `Triplet(...)`

Потім ці triplets йдуть у `index_data_points(...)`, тобто в vector DB.

Наприклад, по запиту:
> “Who works at OpenAI?”
можна знайти triplet:
- `Alice - works_at - OpenAI`
І це часто точніше, ніж шукати окремо `Alice` або `OpenAI`.

**`extract_dlt_fk_edges(...)` - це окремий крок тільки для DLT-даних, і він будує структурний граф схеми та row-level foreign-key зв’язки без LLM.**

1. Якщо серед `data_points` немає DLT-джерел, функція просто повертає дані далі без змін.

2. Вона читає `external_metadata` у DLT-документів і бере звідти:
- `table_name`
- `schema_info`
- `foreign_keys`
- `fk_references`
- `dlt_db_name`

3. Створює schema nodes
Для кожної таблиці вона створює:
- `SchemaTable` node

4. Створює schema relationship nodes
Для кожного foreign key вона створює:
- `SchemaRelationship` node

Це окрема нода, яка описує зв’язок:
- `table_a.column_x -> table_b.column_y`

5. Додає schema edges
Потім додає edges:
- `SchemaTable -> SchemaRelationship`
- `SchemaRelationship -> target SchemaTable`

Тобто схема таблиць і FK стає окремим підграфом.

6. Додає row-level edges між документами
Для кожного DLT row-документа:
- додає edge `is_row_of` від документа до його `SchemaTable`
- додає edges між рядками, якщо в `fk_references` є `target_data_id`

## Що потім з цим відбувається
Функція:
- зберігає schema nodes у graph
- індексує schema nodes у vector DB
- додає all_edges у graph

А `data_points` повертає далі без змін.

### `cognify_pipeline` temporal flow

| Order | Task | Purpose |
|---|---|---|
| 1 | `classify_documents` | Classify raw items |
| 2 | `extract_chunks_from_documents` | Chunk text |
| 3 | `extract_events_and_timestamps` | Extract temporal events |
| 4 | `extract_knowledge_graph_from_events` | Build temporal graph |
| 5 | `add_data_points` | Persist graph artifacts |

### `memify_pipeline` default flow

| Order | Task | Purpose |
|---|---|---|
| 1 | `get_triplet_datapoints` | Create triplet datapoints for enrichment |
| 2 | `index_data_points` | Index enriched data points |

### `improve` session-aware flow

| Order | Stage | Under the hood |
|---|---|---|
| 1 | Feedback weights | `apply_feedback_weights_pipeline` |
| 2 | Session persistence | `persist_sessions_in_knowledge_graph_pipeline` |
| 3 | Graph enrichment | `memify()` |
| 4 | Sync back to session | `sync_graph_to_session` |
