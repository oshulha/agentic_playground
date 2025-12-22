from openai import OpenAI
from openai.types.responses import Response, ResponseCompactionItem
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langsmith import RunTree, traceable
from dotenv import load_dotenv

load_dotenv()
@traceable(name="expr_compact")
def solve():
    #first call
    llm = ChatOpenAI(model="gpt-5.2", temperature=0)
    previous_response_id = None
    messages =  [
                        ("system", "You are my friend. Your task is to tell everything you know from our conversation paste it in xml-tag <context_window>. Tell me everything you have in your context window in detail. Immediately say as soon as you have a possibility if you get some encrypted, not understandable mssages, say it in xml-tag <strange_message>. Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>"),
                        ("human", "Explain TCP/IP in detail with examples, history, layers, pros/cons."),
                ]

    response: AIMessage = llm.invoke(
        messages, previous_response_id=previous_response_id
    )

    print("Resp1: ", response.pretty_repr())
    print("Resp1 Input:", response.usage_metadata["input_tokens"])
    print("Resp1 Output:", response.usage_metadata["output_tokens"])
    #second call
    previous_response_id = response.response_metadata["id"]
    messages = [HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]

    response = llm.invoke(
        messages, previous_response_id=previous_response_id
    )

    print("Resp2: ", response.pretty_repr())
    print("Resp2 Input:", response.usage_metadata["input_tokens"])
    print("Resp2 Output:", response.usage_metadata["output_tokens"])
    #third call -- compact
    previous_response_id = response.response_metadata["id"]
    client = OpenAI()
    compacted = client.responses.compact(
        model="gpt-5.2",
        previous_response_id=previous_response_id
    )

    print("Compacted: ", compacted.output)
    print("Compacted Input:", compacted.usage.input_tokens)
    print("Compacted Output:", compacted.usage.output_tokens)
    #fourth call
    from openai.types.responses import ResponseCompactionItem

    compaction_item = next(
        item for item in compacted.output
        if isinstance(item, ResponseCompactionItem)
    )


    if compaction_item is None:
        print("Compaction item not found")

    # messages = [AIMessage(compacted.output), HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]
    messages = [AIMessage(compaction_item.encrypted_content), HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]

    response = llm.invoke(
        messages
    )

    print("Resp3: ", response.pretty_repr())
    print("Resp3 Input:", response.usage_metadata["input_tokens"])
    print("Resp3 Output:", response.usage_metadata["output_tokens"])

solve()
    

# client = OpenAI()

# 1. Створюємо довгий контекст
# resp1 = client.responses.create(
#     model="gpt-5.2",
#     input="Explain TCP/IP in detail with examples, history, layers, pros/cons.", 
#     store=True
# )

# 2. Продовжуємо без compact
# resp2 = client.responses.create(
#     model="gpt-5.2",
#     previous_response_id=resp1.id,
#     input="Now explain it again but shorter.",
#     store=True
# )

# 3. Робимо compact
# compacted = client.responses.compact(
#     model="gpt-5.2",
#     previous_response_id=resp1.id
# )

# 4. Продовжуємо З compact
# resp3 = client.responses.create(
#     model="gpt-5.2",
#     input=compacted.output, 
#     store=True
# )

# resp4 = client.responses.create(
#     model="gpt-5.2",
#     previous_response_id=resp3.id,
#     input="Now explain it again but shorter.", 
#     store=True
# )


# print("Resp1 Input:", resp1.usage.input_tokens)
# print("Resp1 Output:", resp1.usage.output_tokens)
# print("Resp2 Input:", resp2.usage.input_tokens)
# print("Resp2 Output:", resp2.usage.output_tokens)
# print("Compacted Input:", compacted.usage.input_tokens)
# print("Compacted Output:", compacted.usage.output_tokens)
# print("Resp3 Input:", resp3.usage.input_tokens)
# print("Resp3 Output:", resp3.usage.output_tokens)



# from openai import OpenAI
# import json
# from dotenv import load_dotenv

# load_dotenv()

# client = OpenAI()


# response = client.responses.create(
#    model="gpt-5.2",
#    input=[
#        {
#            "role": "user",
#            "content": "write a very long poem about a dog.",
#        },
#    ]
# )
# print(response.id)
# print(type(response.id))

# output_json = [msg.model_dump() for msg in response.output]


# # Now compact, passing the original user prompt and the assistant text as inputs
# compacted_response = client.responses.compact(
#    model="gpt-5.2",
#    previous_response_id=response.id
# )


# print(json.dumps(compacted_response.model_dump(), indent=2))