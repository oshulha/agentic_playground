from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()

set_of_memories = """
memory_id: 1
timestamp: 06.03.2026 14:10 (ReAct id: 1)
tool_call: run_cmd(path: "/home/oleksandr", cmd: "cat config.yaml")
tool_output: "Permission denied"
what_to_avoid: Trying to read config.yaml without sudo access.
what_worked: —

memory_id: 2
timestamp: 06.03.2026 15:00 (ReAct id: 1)
tool_call: run_cmd(path: "/home/oleksandr", cmd: "ls")
tool_output: "input.txt, intermediate.txt"
what_to_avoid: Checking result files while the processing script is still running.
what_worked: —

memory_id: 3
timestamp: 06.03.2026 15:05 (ReAct id: 1)
tool_call: run_cmd(path: "/home/oleksandr", cmd: "ls")
tool_output: "input.txt, intermediate.txt"
what_to_avoid: Attempting to verify final results before the program has finished execution.
what_worked: —

memory_id: 4
timestamp: 06.03.2026 15:09 (ReAct id: 1)
tool_call: run_cmd(path: "/home/oleksandr", cmd: "ls")
tool_output: "input.txt, intermediate.txt, output.txt, config.yaml"
what_to_avoid: —
what_worked: Checking the directory after the background process finished reveals the generated output file.

memory_id: 5
timestamp: 06.03.2026 15:11 (ReAct id: 1)
tool_call: run_cmd(path: "/home/oleksandr", cmd: "cat config.yaml")
tool_output: "database_url: postgres://localhost..."
what_to_avoid: —
what_worked: Reading config.yaml directly using cat successfully returned configuration data after execution of background script.
"""

prompt_merge = f"""
You are given a group of memories describing tool usage events.

Your task is to merge memories that describe the SAME situation or observation.

A memory has the following structure:
- memory_id
- timestamp
- tool_call
- tool_output
- what_to_avoid
- what_worked

MERGING RULES

1. Merge memories if they describe the same tool call and the same situation
   but are written slightly differently.

2. When merging:
   - Keep the memory with the MOST RECENT timestamp as the base memory.
   - Transfer useful information from older memories into the base memory.

3. If multiple memories contain similar "what_to_avoid" advice,
   merge them into a single clearer sentence.

4. If multiple memories contain similar "what_worked" advice,
   merge them into one concise explanation.

5. Do NOT merge memories if they clearly describe different situations,
   different tool calls, or different environments.

6. The final merged memory must keep the structure:
memory_id
timestamp
tool_call
tool_output
what_to_avoid
what_worked

7. If several memories describe the same event progression,
   prefer the most informative tool_output (usually the latest one).

Example

Input memories:

memory_id: 2
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt"
what_to_avoid: Checking result files while the processing script is still running.

memory_id: 3
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt"
what_to_avoid: Attempting to verify final results before the program has finished execution.

memory_id: 4
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt, output.txt, config.yaml"
what_worked: Checking the directory after the background process finished reveals the generated output file.

Output:

memory_id: 4
tool_call: run_cmd(path="/home/oleksandr", cmd="ls")
tool_output: "input.txt, intermediate.txt, output.txt, config.yaml"
what_to_avoid: Checking result files while the processing script is still running.
what_worked: Checking the directory after the background process finished reveals the generated output file.

Now merge the following memories:

Input:
{set_of_memories}
"""

# ---- First LLM call ----
response1 = client.responses.create(
    model="gpt-5-nano",
    input=prompt_merge
)

set_of_memories = response1.output_text
print("\nFirst response:\n", set_of_memories)

prompt_resolve_conflicts = f"""
You are given several memories describing tool executions and observations.

Some memories may contradict each other because:
- the environment changed over time
- earlier observations were incomplete
- conditions differed between executions

Your task is to detect and resolve contradictions between memories.

IMPORTANT:
You are NOT required to produce only one memory.
You may return multiple memories.

GENERAL RULE

Only merge memories if they describe the SAME tool_call and contain
contradictory observations about the result or conclusions.

If memories describe different situations or different tool calls,
keep them as separate memories.

Each memory has the following structure:

memory_id
timestamp
tool_call
tool_output
what_to_avoid
what_worked

CONFLICT RESOLUTION RULES

1. Detect groups of memories that refer to the SAME tool_call.
2. If there is NO contradiction between them, keep them unchanged.
3. If there IS a contradiction:
   a) Prefer the memory with the MOST RECENT timestamp
      as the base memory, because it reflects the most
      up-to-date state of the environment.
   b) Earlier memories should NOT be discarded if they contain
      useful lessons.
   c) Convert earlier conclusions into contextual advice inside:
      - "what_to_avoid"
      - "what_worked"
4. If an earlier failure later becomes a success,
   reinterpret the earlier failure as a contextual limitation.
Example:
- failure before a process finished
- success after the process finished

5. When merging advice:
   - move incorrect or outdated conclusions into a contextualized warning inside "what_to_avoid"
   - keep successful strategies in "what_worked"

6. Always preserve the memory structure:

memory_id
timestamp
tool_call
tool_output
what_to_avoid
what_worked

7. The output may contain:
   - the same number of memories
   - fewer memories if some were merged

8. Do NOT remove useful information.
   Only resolve contradictions.

Example

Input memories:

memory_id: 1
timestamp: 06.03.2026 14:10
tool_call: run_cmd(path="/home/oleksandr", cmd="cat config.yaml")
tool_output: "Permission denied"
what_to_avoid: Trying to read config.yaml without sudo access.

memory_id: 5
timestamp: 06.03.2026 15:11
tool_call: run_cmd(path="/home/oleksandr", cmd="cat config.yaml")
tool_output: "database_url: postgres://localhost..."
what_worked: Reading config.yaml directly using cat successfully returned configuration data after execution of background script.

Output:

memory_id: 5
timestamp: 06.03.2026 15:11
tool_call: run_cmd(path="/home/oleksandr", cmd="cat config.yaml")
tool_output: "database_url: postgres://localhost..."
what_to_avoid: Trying to read config.yaml before or during execution of the background script.
what_worked: Reading config.yaml directly using cat successfully returned configuration data after execution of the background script.

Now resolve contradictions in the following memories:

Input:
{set_of_memories}
"""

# ---- Second LLM call ----
response2 = client.responses.create(
    model="gpt-5-nano",
    input=prompt_resolve_conflicts
)

result2 = response2.output_text
print("\nSecond response:\n", result2)