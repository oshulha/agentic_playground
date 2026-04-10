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
