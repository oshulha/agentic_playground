#took from https://github.com/SoftSeq/pre-PoC/commit/bfde76a5b6cf1b837b85d285491d2486a7c42d13#diff-337b7c9a6d8c9c5cd759a0b692dc1f58a5a008913b3306975a906f736acb619e
import asyncio
from tools.mcp import create_service_tools
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage, ToolMessage
import json

# Async function to run the logic
async def run_langgraph_with_rocketchat_tools():
    # === 1. Create tools ===
    tools, client = create_service_tools("rocketchat")  # or any other service
    print(f"Loaded {len(tools)} tools: {[t.name for t in tools]}")

    # === 2. Create a prompt ===
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant using Rocket.Chat tools."),
        ("user", "{task}")
    ])

    # === 3. Bind tools to LLM ===
    llm_with_tools = ChatOpenAI(model="gpt-5-mini-2025-08-07").bind_tools(
        tools, parallel_tool_calls=False  # sequential tool calls
    )

    # === 4. Create chain ===
    simple_chain = prompt | llm_with_tools 

    # === 5. Define input for the tool-assisted chain ===
    # task = "List all channels in Rocket.Chat"
    # hint = "Use the channels_list tool."
    
    task = "Read messages from channel general, then response to the last message"
    hint = ""

    # task = "Write message 'Tool node says: Hi!' in channel named general"
    # hint = ""
    # You can pass any messages or context here if needed
    state = {
        "plan": task,
        "messages": [],
        "tools": tools
    }

    # === 6. Run the chain ===
    response = await simple_chain.ainvoke({
        "task": state["plan"],
        "messages": state["messages"],
        "suffix": hint
    })

    print("🔧 Final Response:")
    print(response)

    state["messages"].append(response)

    result = await tool_node(response, state)

    state["messages"] += result["messages"]

    prompt2 = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant using Rocket.Chat tools."),
        ("user", "You can see the task: {task}. However, some steps have been already done. You can see them: {actions}")
    ])

    second_simple_chain = prompt2 | llm_with_tools

    response = await second_simple_chain.ainvoke({
        "task": state["plan"],
        "actions": state["messages"],
        "messages": state["messages"],
    })

    print("🔧 Final Response2:")
    print(response)

    result = await tool_node(response, state)

    state["messages"] += result["messages"]

    #Save state["messages"] to a file
    # with open("/home/oleksandr/Downloads/pre-PoC/messages_state.json", "w", encoding="utf-8") as f:
    #     json.dump([m.model_dump() if hasattr(m, "model_dump") else str(m) for m in state["messages"]], f, ensure_ascii=False, indent=2)



async def tool_node(response, state):
    last_ai_message = response
    if not hasattr(last_ai_message, "tool_calls") or not last_ai_message.tool_calls:
        return {}

    tool_messages = []
    tool_by_name = {f"{tool.name}": tool for tool in state["tools"]}

    async def execute_tool(tool_call):
        tool_call_name = tool_call["name"]
        if tool_call_name in tool_by_name:
            call_id = tool_call["id"]

            # Check if tool has async invoke method
            tool = tool_by_name[tool_call_name]
            if hasattr(tool, "ainvoke"):
                print("Tool call Look:", tool_call)
                result = await tool.ainvoke(tool_call["args"])
            else:
                # Run sync tool in thread pool to avoid blocking
                # Run sync tool in a separate thread to avoid blocking.
                result = await asyncio.to_thread(tool.invoke, tool_call["args"])


            return ToolMessage(content=json.dumps(result), tool_call_id=call_id)
        return None

    tasks = [execute_tool(tool_call) for tool_call in last_ai_message.tool_calls]
    results = await asyncio.gather(*tasks)

    for result in results:
        if result is None:
            continue
        if isinstance(result, ToolMessage):
            tool_messages.append(result)

    return {"messages": tool_messages}

# === 7. Actually run the async function ===
if __name__ == "__main__":
    asyncio.run(run_langgraph_with_rocketchat_tools())


# from tools.mcp import create_service_tools
# import json

# # Створюємо інструменти
# tools, client = create_service_tools("rocketchat")

# # 1) Перевіримо, що client == None для direct
# assert client is None, "Очікуємо, що для transport=direct клієнт не повертається"

# # if client is not None:
# #     print(client.channels_list().json())
# # else:
# #     print("Client is None — це очікувано для transport='direct'")

# # 2) Виведемо список імен згенерованих StructuredTool
# names = [t.name for t in tools]
# print("Інструменти:", names)

# # 3) Спробуємо викликати один інструмент – наприклад channels_list
# tool = next(t for t in tools if t.name == "channels_list")
# # Припустимо, у тебе є коректні креденти у RocketChatBase – метод поверне JSON
# result = tool.func()
# print(type(result))
# output = result.json()
# with open("/home/oleksandr/Downloads/pre-PoC/channels_list_result.json", "w", encoding="utf-8") as f:
#     f.write(result.text)
# print("channels_list():", result)

# # 4) Перевірка валідації Pydantic: викликаємо з ​неправильним​ аргументом
# try:
#     tool.func(foo="bar")
# except Exception as e:
#     print("Очікувана помилка валідації:", type(e), e)
