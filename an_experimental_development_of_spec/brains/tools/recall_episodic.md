### recall_episodic

When a new ReAct worker is invoked by the PlanExecutor, the `recall_episodic` function is called with `query` parameter equal to user query, which calls Memory Controller over `/memory/recall_episodic`. `recall_episodic` returns a list of relevant memories retrieved from Episodic Memory (the Vector Store(Episodic Memory collection) + LLM selection). After all, relevant memories will be inserted in System Prompt of this ReAct worker.  

Fields user_query, what, who, when, where, why, how is embedded independently and searched against its corresponding vector index in the Vector Store(Episodic Memory). Similarity scores from multiple searches are then aggregated using a weighted scoring function.

Here is how approximately I see implementation of `recall_episodic()`:
```python
import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY")
)

from pydantic import BaseModel, Field

class EpisodicContext(BaseModel):
    who: str = Field(..., description="Actors or stakeholders involved")
    what: str = Field(..., description="Exact task or action performed")
    when: str = Field(..., description="Timing, condition, or trigger")
    where: str = Field(..., description="Platform, system, or environment")
    why: str = Field(..., description="Goal or motivation")
    how: str = Field(..., description="Method or implementation approach")

# Recall Tool-Level Memory Mechanism
MEMORY_CONTROLLER_URL = os.getenv("MEMORY_CONTROLLER_URL")
def recall_episodic(
    query: str
) -> list:
  """Recall relevant memories from Episodic memory according to query using multi-vector search across fields user_query, what, who, when, where, why, how.

  Fields user_query, what, who, when, where, why, how is embedded separately inside the Memory Controller and searched against its corresponding named vector index. The Memory Controller aggregates similarity scores across Fields user_query, what, who, when, where, why, how and returns the most relevant memories.

  This function is a wrapper over the Memory Controller API (e.g., POST /memory/recall_episodic).

  Purpose:
    The goal of recall is to provide the agent with past 
    experiences (reflections, successes, failures, security alerts, rate limits, etc.), so that the agent can adapt.

  Args:
    query (str):
        User query or input provided to the ReAct agent

    Returns:
        List:
            API response containing a list_of_relevant_memories.
    Example of tool usage:
      recall_episodic(user_query="How to optimize Vector DB? Identify top-3 insights/solutions and then send it to the Ihor")
"""
    structured_5w1h_system_prompt = f"""
    You are an AI system that converts a user query into a structured episodic memory representation.

    Your goal is to extract maximum informative (highly informative) context using the 5W1H framework.

    STRICT RULES:
    - Output MUST be valid JSON only (no explanations, no extra text)
    - Use ONLY English language (no Ukrainian or any other language)
    - Be concise but maximum informative (high signal, no fluff)
    - Do NOT mention "AI agent", "system", or refer to yourself
    - Write as a neutral factual memory (not narration)
    - Avoid generic phrases like "someone", "something", "various"
    - Be specific whenever possible

    FIELDS REQUIREMENTS:
    - "who": concrete actors, users, or stakeholders involved
    - "what": exact action/task performed
    - "when": the context, situation, or triggering condition (do not include date/time, as timestamps are stored separately in the format DD.MM.YYYY HH:MM)
    - "where": environment, platform, or context (e.g., static website, backend system)
    - "why": underlying goal, motivation, or problem being solved
    - "how": concrete method, approach, or implementation strategy

    INPUT:
    user_query: {query}

    OUTPUT FORMAT:
    {
      "who": "...",
      "what": "...",
      "when": "...",
      "where": "...",
      "why": "...",
      "how": "..."
    }
    """
    response = client.responses.parse(
        model="gpt-5.4",
        input=[
            {
                "role": "system",
                "content": structured_5w1h_system_prompt
            },
            {
                "role": "user",
                "content": f"Your goal is to extract maximum informative context using the 5W1H framework according to this user_query: {user_query}"
            }
        ],
        response_format=EpisodicContext
    )

    context_dict = model_dump(response.output_parsed)

    url = f"{MEMORY_CONTROLLER_URL}/memory/recall_episodic"

    payload = {
        "user_query": query,
        "who": context_dict["who"],
        "what": context_dict["what"],
        "when": context_dict["when"],
        "where": context_dict["where"],
        "why": context_dict["why"],
        "how": context_dict["how"]
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()

        data = response.json()

        # Expected format:
        # {
        #     "memories": [...]
        # }

        return data.get("memories", [])

    except requests.exceptions.RequestException as e:
        print(f"[Episodic Memory Recall Error] {e}")
        return []
```

Example usage:
```python
user_query = "How to optimize Vector DB? Identify top-3 insights/solutions and then send it to the Ihor"

memories = recall_episodic(
    query=user_query
)
```
Memories needs to be added to the System Prompt. It can be appended at the end of the System Prompt or placed before the last section (for example, before the Output Format section), depending on where it fits best.
```python
relevant_episodic_memories = f"""You recall similar past interactions with the user. They are sorted by decreasing relevance:
First:
    What has worked well: {memories[0]["what_worked"]}
    What to avoid: {memories[0]["what_to_avoid"]}
Second:
    What has worked well: {memories[1]["what_worked"]}
    What to avoid: {memories[1]["what_to_avoid"]}
Third:
    What has worked well: {memories[2]["what_worked"]}
    What to avoid: {memories[2]["what_to_avoid"]}
Use these memories as context for your response to the user."""
```

NOTES
[To_Do]Also, episodic memory can be trigerred on some words like "always do like this", "good workflow to make this" and save it what user want to mention. That's examples I saw in [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D) video from langchain. Their agent saves such replics to agents.md. I hope their Deep Agent is open-source.]