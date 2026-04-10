## Working Memory

[Temporary?]This paragraph is provided for context only; it does not contain any implementation ideas at the moment.

Working memory is what helps you keep track of information you are using right now and make sense of it as things change. For our Agents, it means remembering **the current conversation** and using it to respond properly in real time. 

At the moment, we can say that OpenAI provides a solution for working memory, but maintaining a consistently growing list of all user inputs, tool calls, tool outputs, and reasoning items—appended each time the agent receives inputs and produces outputs—looks like not the best solution.

Working memory acts as an active workspace that manages information between episodic experience retrieval and semantic knowledge access, while keeping track of the exact state of the current interaction.

For Example: 
HUMAN: Hello!

AI Agent: Hello!

HUMAN: What's my name?

AI Agent: I do not have access to that information

HUMAN: My name is Adam

AI Agent: It's nice to meet you, Adam!

HUMAN: What is my name?

AI Agent: You said your name is Adam

To be continued...?