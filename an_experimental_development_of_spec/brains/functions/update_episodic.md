### update_episodic

After the ReAct agent completes its task, the system automatically triggers a post-execution reflection stage over the entire trajectory of the ReAct. During this stage, the agent analyzes its own reasoning process, actions(tool-calls) and produces a structured reflection that captures useful insights for future interactions.
The agent must fill a structured output schema, defined as follows:
```python
from typing import Optional, List, Tuple, Type
from pydantic import BaseModel, Field, create_model

class Reflection(BaseModel):
    what_worked: Optional[str] = Field(
        None,
        description=(
            "Most effective approaches or strategies used in this conversation"
        ),
    )

    what_to_avoid: Optional[str] = Field(
        None,
        description=(
            "Most important pitfalls, ineffective approaches to avoid or factors that may lead the agent down incorrect paths or into dead ends."
        ),
    )
```
The reflection is generated using the following prompt template:
```python
reflection_prompt_template = """
You are analyzing your own trajectory of solving a task to create memories that will help guide future interactions. Your task is to extract key elements that would be most helpful when encountering similar situations/tasks in the future.

Review the conversation and create a memory reflection following these rules:

1. For any field where you don't have enough information or the field isn't relevant, contains nothing useful, or only includes generic advice, leave that field empty.
2. Be extremely concise - each string should be one clear, actionable sentence
3. Focus only on information that would be useful for handling similar future conversations

**Output Format:**
You must answer using the Structured Output format required by the system. In that format:
{{
    "what_worked": string,         // Most effective approach or strategy used in this conversation
    "what_to_avoid": string        // Most important pitfall or ineffective approach to avoid
}}

Examples:
- Good what_worked: "Embedding a clear donation call-to-action into the existing page layout enabled quick fundraising integration without modifying the overall site structure."
- Bad what_worked: "Successfully completed the task."

- Good what_to_avoid: "Diving into mathematical formulas before establishing user's familiarity with linear algebra fundamentals""Implementing unnecessary backend payment logic when a simple external donation link is sufficient for a static fundraising website."
- Bad what_to_avoid: "Made the solution too complicated."

Example of Structured Output format:
  "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.", 
  "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
"""
```

Example of what I want to see as a result of structured output by ReAct:
```python
{
    "what_worked": "Embedding a prominent donation call-to-action inside the existing page layout allowed the fundraising feature to be added without restructuring the site.", 
    "what_to_avoid": "Implementing custom payment logic or backend processing when an external donation link is sufficient for a static charity website."
}
```

Then this structured output is sent to the Memory Controller through the /memory/update_episodic API endpoint.
