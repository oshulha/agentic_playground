from openai import OpenAI
from openai.types.responses import Response, ResponseCompactionItem
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, ToolMessage, HumanMessage
from langsmith import RunTree, traceable
from dotenv import load_dotenv
import json

def add_numbers(a: int, b: int) -> int:
    return a + b

tools = [
    {
        "type": "function",
        "name": "add_numbers",
        "description": "Add two integers",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "integer"},
                "b": {"type": "integer"},
            },
            "required": ["a", "b"],
        },
    }
]

load_dotenv()

# @traceable(name="expr_compact")
def openai_solve():
    last_responses = []
    client = OpenAI()

    resp1 = client.responses.create(
        model="gpt-5.2",
        input="Explain TCP/IP in 2 sentences with examples, history, layers, pros/cons.", 
        tools=tools,
        store=True
    )
    print("Resp1: ", resp1)
    print("Resp1 Input:", resp1.usage.input_tokens)
    print("Resp1 Output:", resp1.usage.output_tokens)

    last_responses.append(resp1)

    for i in range(5):
        resp2 = client.responses.create(
            model="gpt-5.2",
            previous_response_id=last_responses[-1].id,
            input=f"Add {i} + {i + 5} using a tool",
            tools=tools,
            store=True
        )

        last_responses.append(resp2)

        print("Resp2: ", resp2)
        print("Resp2 Input:", resp2.usage.input_tokens)
        print("Resp2 Output:", resp2.usage.output_tokens)
        print("\n!!!\nResp2_output: ", resp2.output)

        # ===== Перевіряємо tool call =====
        tool_call = None
        for item in resp2.output:
            if item.type == "function_call" and item.name == "add_numbers":
                tool_call = item
                break

        if tool_call is None:
            raise RuntimeError("Model did not call the tool")

        args = json.loads(tool_call.arguments)
        result = add_numbers(**args)

        # ===== Tool output (КРИТИЧНО ПРАВИЛЬНИЙ FORMAT) =====
        resp_tool = client.responses.create(
            model="gpt-5.2",
            previous_response_id=last_responses[-1].id,
            input=[
                {
                    "type": "function_call_output",
                    "call_id": tool_call.call_id,
                    "output": str(result),
                }
            ],
            store=True
        )

        last_responses.append(resp_tool)

        print("Tool result:", result)
        print("Resp from gpt-5.2 on tool output: ", resp_tool)

    # ===== Compact (НЕ на активному tool chain!) =====

    compacted = client.responses.compact(
        model="gpt-5.2",
        previous_response_id=last_responses[-3].id
    )

    print("Compacted: ", compacted)
    print("Compacted Input:", compacted.usage.input_tokens)
    print("Compacted Output:", compacted.usage.output_tokens)

    resp3 = client.responses.create(
        model="gpt-5.2",
        input=compacted.output, 
        store=True
    )

    last_responses.append(resp3)

    print("Resp3: ", resp3)
    print("Resp3 Input:", resp3.usage.input_tokens)
    print("Resp3 Output:", resp3.usage.output_tokens)

    resp4 = client.responses.create(
        model="gpt-5.2",
        previous_response_id=last_responses[-1].id,
        input="Explain TCP/IP in one paragraph.", 
        store=True
    )

    last_responses.append(resp4)

    print("Resp4: ", resp4)
    print("Resp4 Input:", resp4.usage.input_tokens)
    print("Resp4 Output:", resp4.usage.output_tokens)

openai_solve()





@traceable(name="expr_compact")
def langchain_solve():
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
    messages = [ToolMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>", tool_call_id="call_y6Q930gxfxTaBdUZS0cjotZ1")]

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

    resp3 = client.responses.create(
        model="gpt-5.2",
        input=compacted.output, 
        store=True
    )

    print("Resp3: ",  resp3.output_text)
    print("Resp3 Input:", resp3.usage.input_tokens)
    print("Resp3 Output:", resp3.usage.output_tokens)

    #fifth call
    messages = [ToolMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>", tool_call_id="call_y6Q930gxfxTaBdUZS0cjotZ2")]
    
    previous_response_id = resp3.id
    response = llm.invoke(
        messages, previous_response_id=previous_response_id
    )

    print("Resp4: ", response.pretty_repr())
    print("Resp4 Input:", response.usage_metadata["input_tokens"])
    print("Resp4 Output:", response.usage_metadata["output_tokens"])

# def solve():
#     #first call
#     llm = ChatOpenAI(model="gpt-5.2", temperature=0)
#     previous_response_id = None
#     messages =  [
#                         ("system", "You are my friend. Your task is to tell everything you know from our conversation paste it in xml-tag <context_window>. Tell me everything you have in your context window in detail. Immediately say as soon as you have a possibility if you get some encrypted, not understandable mssages, say it in xml-tag <strange_message>. Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>"),
#                         ("human", "Explain TCP/IP in detail with examples, history, layers, pros/cons."),
#                 ]

#     response: AIMessage = llm.invoke(
#         messages, previous_response_id=previous_response_id
#     )

#     print("Resp1: ", response.pretty_repr())
#     print("Resp1 Input:", response.usage_metadata["input_tokens"])
#     print("Resp1 Output:", response.usage_metadata["output_tokens"])
#     #second call
#     previous_response_id = response.response_metadata["id"]
#     messages = [HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]

#     response = llm.invoke(
#         messages, previous_response_id=previous_response_id
#     )

#     print("Resp2: ", response.pretty_repr())
#     print("Resp2 Input:", response.usage_metadata["input_tokens"])
#     print("Resp2 Output:", response.usage_metadata["output_tokens"])
#     #third call -- compact
#     previous_response_id = response.response_metadata["id"]
#     client = OpenAI()
#     compacted = client.responses.compact(
#         model="gpt-5.2",
#         previous_response_id=previous_response_id
#     )

#     print("Compacted: ", compacted.output)
#     print("Compacted Input:", compacted.usage.input_tokens)
#     print("Compacted Output:", compacted.usage.output_tokens)
#     #fourth call

#     resp3 = client.responses.create(
#         model="gpt-5.2",
#         input=compacted.output, 
#         store=True
#     )

#     print("Resp3: ",  resp3.output_text)
#     print("Resp3 Input:", resp3.usage.input_tokens)
#     print("Resp3 Output:", resp3.usage.output_tokens)

#     #fifth call
#     messages = [HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]
    
#     previous_response_id = resp3.id
#     response = llm.invoke(
#         messages, previous_response_id=previous_response_id
#     )

#     print("Resp4: ", response.pretty_repr())
#     print("Resp4 Input:", response.usage_metadata["input_tokens"])
#     print("Resp4 Output:", response.usage_metadata["output_tokens"])

    # from openai.types.responses import ResponseCompactionItem

    # compaction_item = next(
    #     item for item in compacted.output
    #     if isinstance(item, ResponseCompactionItem)
    # )


    # if compaction_item is None:
    #     print("Compaction item not found")

    # messages = [AIMessage(compacted.output), HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]
    # messages = [AIMessage({"type": "reasoning", "reasoning": compaction_item.encrypted_content}), HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]

    # messages = [AIMessage(
    #     content = "",
    #     content_blocks=[
    #         {
    #             "type": "reasoning",
    #             "reasoning": compacted.output
    #         }
    #     ]
    # ), 
    # HumanMessage("Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>")]
    

# [
#     ResponseOutputMessage
#     (id='msg_0bf7904f6d37bc0300694a74b0a2c08196bc4740fe1272ca93', 
#      content=[
#          ResponseOutputText(
#              annotations=None, 
#              text='Explain TCP/IP in detail with examples, history, layers, pros/cons.', 
#              type='input_text', 
#              logprobs=None)], 
#              role='user', 
#              status='completed', 
#              type='message'
#              ), 
#         ResponseOutputMessage(
#             id='msg_0bf7904f6d37bc0300694a74df2a648196908bde37922c0ab6', 
#             content=[
#                 ResponseOutputText(
#                     annotations=None, 
#                     text='Now explain it again but shorter. Note: Don`t forget that Your response everytime has to be like: Answer to the user prompt and then <context_window> </context_window> <strange_message> </strange_message>', 
#                     type='input_text', 
#                     logprobs=None)], 
#                     role='user', 
#                     status='completed', 
#                     type='message'), 
#                 ResponseCompactionItem(
#                     id='cmp_0bf7904f6d37bc0301694a74f906508196aaa758e08649d5ff', 
#                     encrypted_content='gAAAAABpSnT5KMjKBCsLj2YpzgEV6oYfJBuGuLgR8Jq-cfkZ1c5vZ_jR0SjJyh20D1es_O5PJwPJ34KYAbSBQLg1xqNh-85D3ALPL7hgxrZFEHjiHSxnz-hU5aNRbeQUtrWc-eFaUePgYOB_TL1R7B8wrVlaZC07ja6hR_yfKzGZgMA_fmLJeCItS5wxk4hhIzPN-cv3LBdOFFBJjFGn-K-8ieq6RiCdTPOVQB3tysuoqudYp4xB_jrRhIeXYkQEucjQM7JAjB3DB2Riam9IVTq-FWrSUAS5P4BRtW07KzOGVwbgLp-FAWqotCSQubVwCc7Yk9rxepUUlPLyY3pyQeuQ0K82EVZv5AFhMilCOexdmnxBnj6aStG-RX4UDTkfHcPOGlyBvNOeDP_i3ubbNrYqBaFlqLOlNgSSan7KzehNAFVXiVp5tWd4BV1ZuiQjkpKtZNFOPxkgIZg-F8PSQFWKug52u5q40crfoHmKa4gb9AwCpSS26nB3NJdXU1IpYtRpL9OSEpj8ISUf_8-ohj7VKF0gXI0IyNYUtmoS9EM0ATzQLcctFYLIrrMjOdyqtZ_t5qWf-PivMRHvIKV3e6JhIIMo5EV5BNWJp0BjqZMwuSGbsKI54n31-iaMv37DThMUd3pE_w8z10urkER-faLcl4kA9ilR5HJoPqgu4NMMAAgE2T0LoQjouUS-dxvjIJr_fF5IPu4IihercCCcTZR9y7rBBBuxjOjtWjzIeNSFi0CtBRvFOVV-wzAw1xMhmg_bfVox9N4w3SjyM1YSZFuJBAypH53JGErCgP-EA4oRkIDTfd-bNxPSvQb3GEII5YFms-dSVoTsGpitNpYkwNuK1i3Egz4BLjtlR9hWMyWkSyMVXj7m45roDpWAVQ8jSooSdeQoAMWKYMS5RV9Pve7eYYXzCM98omgvmt7CQkpxM0PY8z8ywJESdbGREoVdUvE51wC6fb1e0-GOEYe4HiHGg9SOUVdz221n5TmJlkvmAbNsCaQ-6FHdGlHcHur6pduGIJs1j9t0HPfW5WU_Gdp58mHy-Nf3hQzszLTVfNZN-9il6OoM2GLfKylEdqWHA7CqpPgYSVKRO4H4Ay8q-5o_Do6WuiG356OJXRkGxKzaw8gScTVWVjUZKWn3w_iEY-26IERLZTrxjfrN2DqRSirgJH0F6caqdY1sYEeoU9nwdZvSoRTXQZ8clISZ56A-bzMR0IZ8M9b8dtMtBJCdi8JXZsyxEjr8GERVV7jhx11-BfSDiRRFDd55-uyVxFJGVe4bAkLsqgWKYa2EeT11IbwS6rwIt30JGJv0rZjAGhlWvpNbpCACG_VorfPotY4_AC4gZT3kLmB1JuX4WhHqb2C6ku0q0XACkhKpp4eyzd02vgoB2shGX0cGooZ-Zb5m1q58kC3lL4yjpp9GibwOIFfiwK506NLjnjc-YmvkXdoPHds8NsX_cah1tWDOHsQC6LUF_9dbHOg7I8WP3NYrrrXebQPI8cesKcekhx3soEJKCTlzjVT3zZF-sLa4NMBpNSlUuswyUBUntxA1Yt7vukcnDccpmNYyOAgd-AaNBnPtLHzR8Bl0jGsqEioP2nqz_0j-MfPIxUPil4aj09yaU4Hm-rbTORuo3czKREUteUCeQbJ809wHCcFq_mSi1wG6wtZGVAp_bthhvCPH1K_JH5ISc55O-D3q33ksLkgtV9HbrM3FL8C3KGGhBnGTWfJgMlv0LZl7758W3ZmGhm29j4u5jYv0Oox1VKd2fsTBoI0G8C6j6IF5Q-gF199W5jO5Rhi8ZmY8o1ZmZSjLiCpf9dyhPlBpHkeLKU9kIWEwXOugJP6JIQiIkYnfzPcMVA7bONbJ-4rdi8UxGHHjugA92HB33oDSyTEK8jGwjd0rHnA-zlTDmGXkS5lcgK23_2flqYKSha7c1q2UkDDdkh4h2ELuxonW7eo4gyXgkdgYJC6A6Ix9afjY7twbAeeVYsKzMiQhGC6i42zEKrxruAlPFafxtaKD2jDoDZC_6bqnpJBQeg41ipI8o3y9cffDoHR2RlXPHMFrwjwUeXtbRJ33sTbrIFCsfg5Ldo579esw1lkmXQxUp_wwkoCwD9ssyowfrc2XtuQverHwqdxvT_wNwexQaiZTEeD1qKsm0mYOohG78uY8h67Revf7MQvQ9XSykM8htoRYUpCFc8EeD8syFJsPTnPPPilcU9dAlSjpt0tiRUWOzqVk6mSOpT08YmnihBTf9PrOOSrqK8opU_PGy0fMUx84qGs77QZlFHvBvFupJLa9C7dAnJbGmWwCLTcKJUtC3u12hiqy3oBFfSgkL63t7QpYyYVKTB6knuwaljs7sKFiBLRRMrIM-kOBpk4yDkGqnRxdIXkcG7dg0JnSG3osSatFOxtQ8Q_ORXwcpUTmDi5JJnYM_5ljk4tlUnYIX6qp1iU6KvXRcvrEACLx9vv40utWmojN0nPeMqMN88jF1RSl20763VrU36BKpaDNRF7sCks0cRjBmMHcJGo4lSwOfiAVX2ttp8p8RZKil2kQpHbpbsEpYhdmBfjA8N_hwV8oBmWfntfKjh4hg51fH31j7SXvMv8PFIcQAZ3d7buFrr1z1jZJCo-6ZS1XINZ3qNqvZzaSYOe-x5KYTcTx-a_6pom5VKLXTLEZmBZb8HRWhtE9vzJ9h4BRzRdZUoM-U8JtMxsz7vD8lBz1MXUhdbwbEy7XMJRT21yqbXodQpj7jPBHRDg3957ImAQI2N67hFYJdvZPsIhDG2W4cLCgSmDAVus3-yhvJ3DekoAACHPD82IqW1LFn-57DqokK_7Lsm3d8f3huU42CliDnwWq9-JTZjNR4f9bQB1-JIdSPrOhFu3muheWbT0FEbiT_pj53bRakKcBwjFtAYCZSjcjw6mRaVUIm9wgVReq6xXVC4G8K7XUyIv_6mpDDWLtsa0ndtoSTLJgUYjtfXSDNYQCjC_79kRe2aPhN-3NglJgRN-j5d4YLtlAQrz9ehVHGiH4RhsQNSzt67IVB_PICGYuUXROL1t_SXCZ9HjoORD31yRaunfxQIwiMr2-hI9ZOg9jPghiV37KvpeWvqY30HoWa1Z6VnOTPnARynwWfIby4__weYgnr9S_Joqii324f0Kf5mnU8suABL80EFKJ6j_3S7FD_nobjTWr6V6B8THRah4MDH6G025zOtRot4vvRkXkW5WD5YIKTjFBy4m4slwKtUECTAQHdAWJMTR8OKB_GgAENoRXQ75WLCaKsI4KwMe9RqPl8oZTf0oL2x_YHFNQ3XcyKCHqfpJRORoC0c3U-pn_ef7GFP8ZLMyb0EyVmfl9BnkZGYH-iH9m3G8FOoJTq-rPwJGUoZb5tP-uBhdAOVob410AsTNoC4AqTEEMt7fCRazs1Zw1XJ5aUxYOaPMW-8z4XP6vB4gce-Jm-Bw6FUEV9kfSYcW1dBJ_aCM50TdyjZXR1FD7JF-SIIgj5UuvbAiP32EH9MMAsb0TMKfpwaw_amrtzZAwveixLdj19TD0p951uQARkHKobsVSc37vszVQIPsFg_RWA7nBlOQa0f3YN1ZNEfZJlokv3ZjXhLkCHiJUd4S480ZW2ir9_uM-yKMihcHGB0RK9Rp1M1s4L1BC1qbByQKQOc1m01EJCxdysb2DaKFgS1EDpvFRZm5bdSHgSYfOeIGcCb_eMsI__flZSzhy4flBG1XC3i8gB0pE7kfRisGpngW2z85TivzDIY4VxmaukmB-S_C7aotAouTSkoDi98TyeYEmws_emMOD8f4IxmSDMan2pgp4Rs-OnjNlRuKCgus8ZfdtVdsp45igDt3amf20DQLq_874ySxAI2_Kz9dOhxPQI_TTmClb_Y-_H_4XURHfTasCN3RN3ie7N0_6EJLLqsbzWoTahtiAqLJIZqicqrpBdvwWV8IsZEFVVJuHJGTFwnbqssfNzc4zA9AX9BGcZ0Dvu2ibLjOrrJQFqdTrTYrcAGu5DLIfP9-c_0YNYAfSn253hvVRmI0ggSglPeyp1cCENiUqe3sJEOlNnH-ZWYa14XWfgUD4q090ca8lZI5gDCDycPnCVFCGPnYs4HTu_cvCDgsDuYsGrBwasELWfC762-l_uU8q5bB0DX6Y3v6_C_-b2wFhfE1oWLslWp6GSbIUKMxibFBh8VqojvjNzNEEAOKfozgmmhfIP9OGcP28F0rkwaiNVcA4yYdatByGpNSWgf2tgWLSbtbCyKCvdmPjBL6oXmOlkW8_8B9I_Xo_TRbtz5aT9XLNxatTxz8R0kL_vkZYZPVAtn_3Lcnne5dtAma9FruN_PZQ56rIEu1OGKKDHtNui7kP5nG7utPAbt8_fSutD3z-BECnwMG4poCbzdDp54IyQQCB9JR8n_LVLTq7xd18EtG3I4XrKa9L5db6XV15oG8-360WhYuEVj7qkmTlXho5HL-3AIlLx3hNdhj2pWQmubEMWYhj9Se8cRNVrJriP9k2jQq15XHEyHV2iGBslm3PPQ9IoygFJrkCLA3vIulNqV8_U60Oi__Guy_tILRLyZbGjirHH--RhCIqhAb8PsifgnT1a95ZC72cxKJPr91TkNyTpa1nKky4bOGtp0nAdvEe408HhDNnOVPgnRnn9ekmcjaL093l4QUeLqvKyi9nJL0uqKaA8p8oZgmDuuDcp18CCmmfhV9KuzmYtMj4b2VhHe6agd4up69QIpyVqZPVo8AoRzVlNH6Un4AXOdXYR-QNK0cQmuVLDC3279gn22u70NuS3nV2uiCx4uIj0GK8ElwvTgd7pClLs7XPBV3ILC-6ooEYpe7kpkhl1VwmdRZq9wlokEiI1iqfN-QpUCBK8J6V422yF3WaTJc=', 
#                     type='compaction', 
#                     created_by=None)
#                 ]

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