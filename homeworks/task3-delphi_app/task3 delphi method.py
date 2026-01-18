from openai import OpenAI
import re
import time
import tiktoken  # For token estimation

model="gpt-4"
encoding = tiktoken.encoding_for_model(model)

global system_prompts

client = OpenAI(api_key="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")

system_prompt_gen = (
    "You are a system that simulates the Delphi method. "
    "Your task is to generate expert personas who could offer diverse perspectives on a complex question. "
    "Each expert should have a name, profession, thinking style, and a brief description of their value in the discussion. "
    "Format the output as a list, and make sure each expert entry starts with the symbol '№' followed by their number (e.g., '№1.', '№2.', etc.) "
    "Use consistent formatting for easy parsing."
)
num_experts = 5

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

if __name__ == "__main__":
    user_question = input("Input your complex question: ")
    start = time.perf_counter()

    user_prompt_gen = f"Question: {user_question}\nGenerate {num_experts} experts."

    experts = generate_experts(user_prompt_gen)

    print("\n🔍 Generated experts Delphi:\n")
    print(experts)
    
    pattern = r"(№\d\..*?)(?=\n№\d\.|\Z)"

    expert_arr = re.findall(pattern, experts, re.DOTALL)
    names = re.findall(r"№\d+\.\s+([A-Za-z\s\.]+?),", experts)
    # Зберігаємо кожного експерта в окрему змінну
    conversations = {name: [] for name in names}

    responses_r1 = []
    responses_r2 = []

    num = 1

    for expert in expert_arr:
        conversations[names[num - 1]].append({"role": "system", "content": sys_prompt(expert)})####
        conversations[names[num - 1]].append({"role": "user", "content": user_question})
        response = expert_response(expert, conversations[names[num - 1]])
        responses_r1.append("№" + str(num) + ": " + response + "\n\n")
        conversations[names[num - 1]].append({"role": "assistant", "content": response})
        #print("Round 1 Answer: №" + str(num) + ": " + response + "\n\n")
        num = num + 1
    
    strresponses = ''.join(responses_r1)
    summary = summary_experts(user_question, strresponses)
    print("SUMMARY after Round 1: " + summary)

    user_input = (
        f"Here is a summary of what other experts said:\n{summary}\n\n"
        "Would you like to revise or expand your initial answer based on this input?"
    )

    num = 1

    for expertt in expert_arr:
        conversations[names[num - 1]].append({"role": "user", "content": user_input})
        response = expert_response(expertt, conversations[names[num - 1]])
        responses_r2.append("№" + str(num) + ": " + response + "\n\n")
        conversations[names[num - 1]].append({"role": "assistant", "content": response})
        #print("Round 2 Answer: №" + str(num) + ": " + response + "\n\n")
        num = num + 1
    
    strresponses = ''.join(responses_r2)
    summary = summary_experts(user_question, strresponses)

    end = time.perf_counter()

    print("SUMMARY after Round 2: " + summary)

    elapsed = end - start

    print(f"\nExecution time: {elapsed:.4f} seconds")

    gen_input_tokens = len(encoding.encode(system_prompt_gen)) + len(encoding.encode(user_prompt_gen))
    gen_output_tokens = len(encoding.encode(experts))
    gen_cost = (gen_input_tokens / 1_000_000) * 0.10 + (gen_output_tokens / 1_000_000) * 0.40

    summary_output_tokens = len(encoding.encode(summary))####
    summary_cost = summary_input_cost(user_question, strresponses) + (summary_output_tokens / 1_000_000) * 0.40
    
    total_conv_cost = 0
    for name in names:
        total_conv_cost += count_conv_cost(conversations[name])
    
    gpt_total_cost = total_conv_cost + gen_cost + summary_cost

    print(f"Total Estimated:    ${gpt_total_cost:.6f}")