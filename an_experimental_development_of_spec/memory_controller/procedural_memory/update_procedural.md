### /update_procedural 

After each ReAct agent execution, the system aggregates the existing what_worked and what_to_avoid entries with newly generated insights obtained during the Reflexion stage. Based on this updated information, the procedural memory is revised by updating the list of 10 instructions, which are saved into the file named `procedural_memory_instructions.txt`.

At the first invocation of a ReAct agent, the procedural memory is initialized as empty.

[To_Do][In this design, procedural memory closely resembles an agents.md-style guideline file. However, alternative approaches should be considered!!!
For example, in the LangChain [Introducing /remember](https://www.youtube.com/watch?v=6XXH5XecVp4&pp=ygUZL3JlbWVtYmVyIGxhbmdjaGFpbiB2aWRlbw%3D%3D)
video, the system incrementally updates an agents.md file and may eventually promote accumulated knowledge into an explicit “skill.” But looks like not very reliable idea at the moment.]