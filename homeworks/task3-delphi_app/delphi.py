# delphi.py
from openai import OpenAI
import re, time
import tiktoken
#from experts import create_experts

# --- налаштування OpenAI і тікетингу ---
client = OpenAI(api_key="OPENAI_API_KEY")
encoding = tiktoken.encoding_for_model("gpt-4")

system_prompt_gen = (
    "You are a system that simulates the Delphi method. "
    "Your task is to generate expert personas who could offer diverse perspectives on a complex question. "
    "Each expert should have a name (in Latin characters), profession, thinking style, and a brief description of their value in the discussion. "
    "Format the output as a numbered list where each expert entry starts on a new line with the symbol '№' followed by their number (e.g., '№1.'). "
    "Each entry should follow this structure:\n"
    "№<number>. <Full Name>, <Profession>. <Thinking Style>. <Brief description>\n"
    "Ensure that the expert's full name is the first element after the number, followed by a comma, to allow easy parsing."
)

num_experts = 3

def generate_experts(user_prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        temperature=0.8,
        max_tokens=800,
        messages=[
            {"role": "system", "content": system_prompt_gen},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def summary_input_cost(question, strresponses):
    system_prompt = (
    f"You will soon be presented with a Delphi method discussion on the complex question: {question}. "
    "The discussion includes insights from experts across various disciplines. "
    "Your task is to analyze each perspective carefully and provide a clear and concise summary of the key points made by each expert—without revealing their identities."
)

    user_prompt = f"Here are opinions from all experts: {strresponses}\n\nDo a summary"

    sum_input_tokens = len(encoding.encode(system_prompt)) + len(encoding.encode(user_prompt))
    sum_input_cost = (sum_input_tokens / 1_000_000) * 0.10

    return sum_input_cost

def summary_experts(question, strresponses):
    system_prompt = (
    f"You will soon be presented with a Delphi method discussion on the complex question: {question}. "
    "The discussion includes insights from experts across various disciplines. "
    "Your task is to analyze each perspective carefully and provide a clear and concise summary of the key points made by each expert—without revealing their identities."
)

    user_prompt = f"Here are opinions from all experts: {strresponses}\n\nDo a summary"

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        temperature=0.8,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content


def sys_prompt(expert):
    system_prompt = (
    "You are a participant in a Delphi method discussion, where experts from other fields are also involved. "
    "Your task is to respond to a complex question by providing a reasoned, detailed answer from your professional viewpoint, reflecting your background, logic, and priorities. "
    "Ensure that your answer is well thought out, clearly expressed, and grounded in your domain of expertise."
    f"You are: {expert}"
)
    return system_prompt


def expert_response(expert, messages):
    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        temperature=0.8,
        max_tokens=500,
        messages=messages
    )
    return response.choices[0].message.content

def count_conv_cost(messages):
    input_tokens = 0
    output_tokens = 0

    for message in messages:
        tokens = 4
        for _, value in message.items():
            tokens += len(encoding.encode(value))

        role = message.get("role", "")
        if role in ["user", "system"]:
            input_tokens += tokens
        elif role == "assistant":
            output_tokens += tokens

    input_tokens += 2

    gpt_input_cost = (input_tokens / 1_000_000) * 0.10
    gpt_output_cost = (output_tokens / 1_000_000) * 0.40
    total_cost = gpt_input_cost + gpt_output_cost

    return total_cost

# --- проміжні підготовчі функції sys_prompt, expert_response, summary_experts, etc. ---
# скопіюй сюди решту допоміжних функцій зі свого скрипта, але прибери input() і print().

def run_delphi_process(user_question):
    # 1. Генерація списку експертів
    user_prompt_gen = f"Question: {user_question}\nGenerate {num_experts} experts."
    start = time.perf_counter()
    experts = generate_experts(user_prompt_gen)
    # 2. Парсинг на окремі елементи
    pattern = r"(№\d\..*?)(?=\n№\d\.|\Z)"
    expert_arr = re.findall(pattern, experts, re.DOTALL)
    #names = re.findall(r"№\d+\.\s+([A-Za-z\s\.]+?),", experts)
    
    # 3. Перший раунд
    conversations = {expertttt: [] for expertttt in expert_arr}
    responses_r1 = []
    responses_r2 = []
    num = 1

    for expert in expert_arr:
        conversations[expert].append({"role": "system", "content": sys_prompt(expert)})####
        conversations[expert].append({"role": "user", "content": user_question})
        response = expert_response(expert, conversations[expert])
        responses_r1.append("№" + str(num) + ": " + response + "\n\n")
        conversations[expert].append({"role": "assistant", "content": response})
        #print("Round 1 Answer: №" + str(num) + ": " + response + "\n\n")
        num = num + 1

    # 4. Підсумок після раунду 1
    strresponses1 = ''.join(responses_r1)
    summary1 = summary_experts(user_question, strresponses1)

    # 5. Другий раунд
    
    user_input = (
        f"Here is a summary of what other experts said:\n{summary1}\n\n"
        "Would you like to revise or expand your initial answer based on this input?"
    )

    for expertt in expert_arr:
        conversations[expertt][0]["content"] += "You've become risk-seeking"
        conversations[expertt].append({"role": "user", "content": user_input})
        response = expert_response(expertt, conversations[expertt])
        responses_r2.append("№" + str(num) + ": " + response + "\n\n")
        conversations[expertt].append({"role": "assistant", "content": response})
        #print("Round 2 Answer: №" + str(num) + ": " + response + "\n\n")
        num = num + 1

    strresponses2 = ''.join(responses_r2)
    summary2 = summary_experts(user_question, strresponses2)
    end = time.perf_counter()
    elapsed = end - start

    gen_input_tokens = len(encoding.encode(system_prompt_gen)) + len(encoding.encode(user_prompt_gen))
    gen_output_tokens = len(encoding.encode(experts))
    gen_cost = (gen_input_tokens / 1_000_000) * 0.10 + (gen_output_tokens / 1_000_000) * 0.40

    summary_output_tokens1 = len(encoding.encode(summary1))
    summary_output_tokens2 = len(encoding.encode(summary2))
    summary_cost = summary_input_cost(user_question, strresponses1) + summary_input_cost(user_question, strresponses2) + (summary_output_tokens1 / 1_000_000) * 0.40 + (summary_output_tokens2 / 1_000_000) * 0.40
    
    total_conv_cost = 0
    for experttt in expert_arr:
        total_conv_cost += count_conv_cost(conversations[experttt])
    
    gpt_total_cost = total_conv_cost + gen_cost + summary_cost

    # 6. Збираємо всі результати
    final = f"""
<strong style='font-size: 20px;'>Experts:</strong><br>{experts.replace('\n', '<br>')}<br><br>
<strong style='font-size: 20px;'>Round 1:</strong><br>{'<br>'.join(responses_r1)}<br><br>
<strong style='font-size: 20px;'>Summary 1:</strong><br>{summary1.replace('\n', '<br>')}<br><br>
<strong style='font-size: 20px;'>Round 2:</strong><br>{'<br>'.join(responses_r2)}<br><br>
<strong style='font-size: 20px;'>Summary 2:</strong><br>{summary2.replace('\n', '<br>')}<br><br>
<strong style='font-size: 20px;'>Execution Time:</strong> {elapsed:.4f} sec<br><br>
<strong style='font-size: 20px;'>Cost:</strong> ${gpt_total_cost:.6f}
"""

    return final
