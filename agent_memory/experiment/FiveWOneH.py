import os

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

MODEL = "gpt-5.4"
QUERY = "How to optimize Vector DB? Identify top-3 insights/solutions and then send it to the Ihor"


class EpisodicContext(BaseModel):
    who: str = Field(..., description="Actors or stakeholders involved")
    what: str = Field(..., description="Exact task or action performed")
    when: str = Field(..., description="Timing, condition, or trigger")
    where: str = Field(..., description="Platform, system, or environment")
    why: str = Field(..., description="Goal or motivation")
    how: str = Field(..., description="Method or implementation approach")


def build_system_prompt(query: str) -> str:
    return f"""
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
{{
  "who": "...",
  "what": "...",
  "when": "...",
  "where": "...",
  "why": "...",
  "how": "..."
}}
""".strip()


def create_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set.")
    return OpenAI(api_key=api_key)


def extract_episodic_context(client: OpenAI, query: str) -> EpisodicContext:
    input_messages = [
        {"role": "system", "content": build_system_prompt(query)},
        {
            "role": "user",
            "content": f"Extract maximum informative context using the 5W1H framework for this user_query: {query}",
        },
    ]

    try:
        response = client.responses.parse(
            model=MODEL,
            input=input_messages,
            text_format=EpisodicContext,
        )
    except TypeError:
        # Backward-compatible fallback for older SDKs that used a different
        # keyword name for structured parsing.
        response = client.responses.parse(
            model=MODEL,
            input=input_messages,
            response_format=EpisodicContext,
        )

    return response.output_parsed


def main() -> None:
    client = create_client()
    episodic_context = extract_episodic_context(client, QUERY)
    context_dict = episodic_context.model_dump()

    payload = {
        "user_query": QUERY,
        "who": context_dict["who"],
        "what": context_dict["what"],
        "when": context_dict["when"],
        "where": context_dict["where"],
        "why": context_dict["why"],
        "how": context_dict["how"],
    }

    print(payload)


if __name__ == "__main__":
    main()
