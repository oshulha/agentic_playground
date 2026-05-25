import os
from dotenv import load_dotenv
from episodic_memory_thoughts import episodic_memories
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

# ------------------ PROMPTS ------------------

system_prompt = """You are a highly precise memory relevance evaluator.

Your task is to analyze episodic memories and determine how relevant each memory is to a given query.

STRICT RULES:

1. Evaluate ALL memories.
2. Assign score 0–100 based ONLY on relevance.
3. Be critical:
   - 90–100 → directly answers query
   - 70–89 → useful
   - 40–69 → weak
   - 0–39 → irrelevant
4. Keep reasoning short and specific.
5. Do NOT hallucinate.
"""

# ------------------ LLM ------------------

llm = ChatOpenAI(model="gpt-5.4", temperature=0)  # стабільна модель

# ------------------ SCHEMA ------------------

class AskLLMItem(BaseModel):
    memory_id: int = Field(..., description="Index of memory (1-based)")
    reasoning: str = Field(..., description="Short reasoning")
    memory_score: float = Field(..., description="Score 0-100")

class AnalysisResult(BaseModel):
    results: List[AskLLMItem]

# ------------------ DATA ------------------

answers_list = [
    [2, 3, 4],
    [9, 10, 8],
    [28, 29, 13],
    [27, 24, 25],
    [21, 22, 8],
    [9, 10, 30],
    [6, 11, 5],
    [27, 23, 26],
    [13, 14, 19],
    [16, 15, 14]
]

final_score = 0

# ------------------ MAIN LOOP ------------------

for ind, query_obj in enumerate(episodic_memories["queries"]):
    query = query_obj["query"]
    memories = episodic_memories["episodic_memories"]
    answers = answers_list[ind]

    # Формуємо компактний список memories
    memories_text = "\n".join([
        f"{i+1}. {mem}"
        for i, mem in enumerate(memories)
    ])

    user_prompt = f"""
You are given:

QUERY:
{query}

MEMORIES:
{memories_text}

INSTRUCTIONS:

- Evaluate ALL memories from 1 to {len(memories)}
- Return result as JSON:

{{
  "results": [
    {{
      "memory_id": 1,
      "reasoning": "...",
      "memory_score": 85
    }}
  ]
}}

IMPORTANT:
- Do NOT skip any memory
- Be strict with scoring
"""

    messages = [
        ("system", system_prompt),
        ("human", user_prompt)
    ]

    analysis_result = llm.with_structured_output(AnalysisResult).invoke(messages)

    # ------------------ PROCESS RESULTS ------------------

    scored_memories = []

    for item in analysis_result.results:
        mem = memories[item.memory_id - 1]

        scored_memories.append({
            "memory": mem,
            "score": item.memory_score,
            "reasoning": item.reasoning
        })

    # ТОП-3
    top_k = 3
    best = sorted(scored_memories, key=lambda x: x["score"], reverse=True)[:top_k]

    # ------------------ SAVE ------------------

    with open("exp1-2_results.txt", "a", encoding="utf-8") as f:
        f.write(f"Query: {query}\n")
        f.write(f"Answers: {answers}\n")

        for i, item in enumerate(best, start=1):
            f.write(f"--- Memory {i} ---\n")
            f.write(f"Memory: {item['memory']}\n")
            f.write(f"Score: {item['score']}\n")
            f.write(f"Reasoning: {item['reasoning']}\n\n")

            if item["memory"]["memory_id"] in answers:
                final_score += 1

# ------------------ FINAL SCORE ------------------

with open("exp1-2_results.txt", "a", encoding="utf-8") as f:
    f.write(f"Final Score: {final_score}/30\n")