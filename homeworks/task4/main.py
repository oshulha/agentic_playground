# main.py
from openai import AsyncOpenAI, OpenAI
import re
from helper import call_OpenAI_model, call_Gemini_model
import subprocess
import sys
import ast
import time

model_to_use = "gpt-4.1" #"gpt-4.1" claude-sonnet-4-20250514

client = AsyncOpenAI(api_key="ANTHROPIC_API_KEY")
# client = AsyncOpenAI(
#     api_key="ANTHROPIC_API_KEY",  # Your Anthropic API key
#     base_url="https://api.anthropic.com/v1/"  # Anthropic's API endpoint
# )


    # "Each expert will:\n" # For gpt-4.1-nano it is maybe hard to take so much system prompt
    # "1. Propose an initial plan to solve the task.\n"
    # "2. Review and suggest improvements to the plans of other experts.\n"
    # "3. Revise their own plan based on peer feedback.\n"
    # "4. Implement the most promising solution.\n"
    # "5. Review and suggest improvements to others' implementations.\n"
    # "6. Update their own implementation accordingly.\n"
    # "7. Evaluate all final implementations and select the best one.\n\n"

system_prompt_gen_experts = (
    "You are a system simulating the Delphi method to support complex decision-making. "
    "Your role is to generate a set of expert personas, each bringing a unique perspective to the given task.\n\n"
    "Each expert must be described with:\n"
    "- Full name (in Latin characters)\n"
    "- Profession\n"
    "- Thinking style\n"
    "- A brief description of their value to the discussion\n\n"
    "All experts must be professionals with a technical background—such as engineers, developers, data scientists, AI specialists, or automation experts—with great experience in developing or implementing systems using the Python programming language and the OpenAI/Gemini/Anthropic API.\n\n"
    "Format the output as a numbered list using the '№' symbol (e.g., '№1.').\n"
    "Each entry must follow this structure:\n"
    "№<number>. <Full Name>, <Profession>. <Thinking Style>. <Brief description>\n"
    "Ensure the full name appears immediately after the number and is followed by a comma for easy parsing."
)


num_experts = 1


def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Не вдалося встановити пакет '{package}'.")
        print(f"[DETAILS] Команда повернула помилку: {e}")

def eval_plan_prompt(resp):
    eval_plan_prompt = f"""Review another expert's plan: {resp}. Identify its advantages and disadvantages, and provide a rating from 0.0 to 10.0. The rating must include exactly one decimal place (tenths only — no hundredths or thousandths). 

IMPORTANT: Your response must strictly follow the format below. You MUST use the `<grade>` XML tag exactly as shown — do NOT use other tags such as <score>, <rating>, or similar.

Your response must follow this **exact** format:

Advantages:
- <list of advantages>
Disadvantages:
- <list of disadvantages>
<grade>X.X</grade>   ← Only use this tag to wrap the score, and nothing else!
"""
    return eval_plan_prompt

def eval_implmnt_prompt(resp):
    implmnt = f"""Review another expert's implementation: {resp}. Identify its advantages and disadvantages, and provide a rating from 0.0 to 10.0. The rating must include exactly one decimal place (tenths only — no hundredths or thousandths). 

    IMPORTANT: Your response must strictly follow the format below. You MUST use the `<grade>` XML tag exactly as shown — do NOT use other tags such as <score>, <rating>, or similar.

    Your response must follow this **exact** format:

    Advantages:
    - <list of advantages>
    Disadvantages:
    - <list of disadvantages>
    <grade>X.X</grade>   ← Only use this tag to wrap the score, and nothing else!
    """
    return implmnt

def eval_improv_prompt(resp):
    implmnt = f"""Review another expert's list of improvements: {resp}. Identify its advantages and disadvantages, and provide a rating from 0.0 to 10.0. The rating must include exactly one decimal place (tenths only — no hundredths or thousandths). 

    IMPORTANT: Your response must strictly follow the format below. You MUST use the `<grade>` XML tag exactly as shown — do NOT use other tags such as <score>, <rating>, or similar.

    Your response must follow this **exact** format:

    Advantages:
    - <list of advantages>
    Disadvantages:
    - <list of disadvantages>
    <grade>X.X</grade>   ← Only use this tag to wrap the score, and nothing else!
    """
    return implmnt

def eval_imprv_implmnt_prompt(resp):
    implmnt = f"""Review another expert's improved implementation: {resp}. Identify its advantages and disadvantages, and provide a rating from 0.0 to 10.0. The rating must include exactly one decimal place (tenths only — no hundredths or thousandths). 

    IMPORTANT: Your response must strictly follow the format below. You MUST use the `<grade>` XML tag exactly as shown — do NOT use other tags such as <score>, <rating>, or similar.

    Your response must follow this **exact** format:

    Advantages:
    - <list of advantages>
    Disadvantages:
    - <list of disadvantages>
    <grade>X.X</grade>   ← Only use this tag to wrap the score, and nothing else!
    """
    return implmnt

async def evaluate_resp(expert_arr, responses, conversations, responses_eval, user_propmt):
    num_exp = 1
    grades = [0] * 3

    for expert in expert_arr: #Evaluate others' responses
        for i_plan in range(len(responses)):
            if(num_exp - 1 == i_plan):
                continue
            

            resp = responses[i_plan]
            
            #add smth like be objective as much as possible
            conversations[expert].append({"role": "user", "content": user_propmt(resp)
})
            
            response = await expert_response(conversations[expert])#
            match = re.search(r'<grade>([0-9]+(?:\.[0-9])?)</grade>', response)
            grade = float(match.group(1)) if match else None
            grades[i_plan] += grade
            responses_eval.append("№" + str(num_exp) + ": " + response + "\n\n")
            conversations[expert].append({"role": "assistant", "content": response}) 
        
        num_exp = num_exp + 1

    maxx = -1
    ind = -1
    for i in range(len(grades)):
        if(maxx < grades[i]):
            maxx = grades[i]
            ind = i
    
    best_plan = responses[ind]
    return best_plan

async def generate_experts(user_prompt):#
    global model_to_use
    response = await client.chat.completions.create(
        model=model_to_use,
        temperature=0.8,
        max_tokens=800,
        messages=[
            {"role": "system", "content": system_prompt_gen_experts},
            {"role": "user", "content": user_prompt}
        ]
    )
    return response.choices[0].message.content

def sys_prompt(expert):
    system_prompt = (
    "You are a participant in a Delphi method discussion, where experts from other fields are also involved. "
    "Your task is to respond to a complex question by providing a reasoned, detailed answer from your professional viewpoint, reflecting your background, logic, and priorities. "
    "Ensure that your answer is well thought out, clearly expressed, and grounded in your domain of expertise."
    "It is crucially important to fully complete all points of the task given by user prompt.\n\n"
    f"You are: {expert}"
)
    return system_prompt


async def expert_response(messages):#
    global model_to_use
    response = await client.chat.completions.create(
        model=model_to_use,
        temperature=0.7,
        messages=messages
    )
    return response.choices[0].message.content

async def run_process(user_question):
    start = time.perf_counter()

    user_prompt_gen = f"We have such a task: {user_question} For now your task is to generate {num_experts} experts. All experts must be professionals with a technical background—such as engineers, developers, data scientists, AI specialists, or automation experts—with great experience in developing or implementing systems using the Python programming language and the OpenAI API"
    experts = await generate_experts(user_prompt_gen)#

    # 2. Парсинг на окремі елементи
    pattern = r"(№\d\..*?)(?=\n№\d\.|\Z)"
    expert_arr = re.findall(pattern, experts, re.DOTALL)
    
    # 3. Перший раунд
    conversations = {expertttt: [] for expertttt in expert_arr}
    responses_r1 = []
    responses_eval1 = []
    responses_r2 = []
    responses_eval2 = []
    responses_r3 = []
    responses_eval3 = []
    responses_r4 = []
    responses_eval4 = []
    num = 1

    for expert in expert_arr: #Step-by-step plan
        conversations[expert].append({"role": "system", "content": sys_prompt(expert)})####
        conversations[expert].append({
    "role": "user",
    "content": f"""Provide a high-level, step-by-step plan for implementing the task in Python.
The plan should be thorough, well-structured, and clearly describe the necessary programmatic steps (i.e., Python-specific instructions) required to accomplish the task.

However, do not include any actual code. Instead, describe the instructions as clearly and precisely as possible—imagine you are guiding someone through the implementation using only your words.
A team of experts will use this plan to write the actual Python code, so your explanation should be detailed enough for them to follow without needing further clarification.

If this does not contradict the conditions of the problem, the implementation should output the results to the console.

The resulting implementation, if followed correctly, must fulfill the User Objective and produce the correct output.


Here is the task: {user_question}"""
})
        response = await expert_response(conversations[expert])#
        responses_r1.append(response)
        conversations[expert].append({"role": "assistant", "content": response})
        num = num + 1

    plan = await evaluate_resp(expert_arr, responses_r1, conversations, responses_eval1, eval_plan_prompt)#
    num = 1

    gpt_helper = """ Use from helper import call_OpenAI_model to make calls to OpenAI models via API.  To use the method call_OpenAI_model(), you must provide the following arguments in this exact order: system_prompt, user_prompt and max_tokens. """
    gemini_helper = """ Use from helper import call_Gemini_model to make calls to Gemini models via API.  To use the method call_Gemini_model(), you must provide the following arguments in this exact order: system_prompt, user_prompt and max_tokens.  """

    fetch_helper = """ Use from helper import fetch_wiki to import the fetch_wiki() function. To fetch content from a link, pass the URL as a string argument to fetch_wiki(). This is much more convenient and efficient than writing your own function to retrieve text from Wikipedia."""


    for expert in expert_arr: #Implementation
        conversations[expert].append({
    "role": "user",
    "content": f""" Implement the solution according to the following plan: {plan}. Write it in valid, executable Python code. Do not include explanations, comments, or any extra output — just the plain Python code. Do not write code in Markdown format.
{gemini_helper} {fetch_helper}
When sending a request to the model and asking it to return code or structured data (such as JSON), make sure the output is not wrapped in Markdown formatting. 
Markdown wrappers can cause parsing errors and lead to incorrect handling of the returned content. 
Better provide answers in plain text—use paragraphs, bullet points, or other human-readable formats.
Do not wrap the code in exec(""" """). 
Instead, provide it as plain text. Do not include any prompts asking the user to enter information, such as input(). 
Do not write any code that accesses, manipulates, or defines API keys in any way. 
This includes reading from environment variables, hardcoding keys, or creating helper functions to retrieve or validate API keys. 
If you're going to write a prompt that includes instructions or a step-by-step plan, make sure to write each step or instruction in as much detail as possible, so that everything is fully understandable and nothing important is left out or misinterpreted.
Additionally, if the prompt is intended for a model to follow, include clear guidance that the model should output a response after each step, allowing it to view the intermediate results and use them as inputs for the following steps.
That is why you should increase the number of max_tokens to ensure there is enough space for the model to return detailed responses for each step without being cut off.
Returned Python script has to print the result to the console using print()."""
})
        response = await expert_response(conversations[expert])#
        responses_r2.append(response)
        conversations[expert].append({"role": "assistant", "content": response})
        num = num + 1

    implemnt = await evaluate_resp(expert_arr, responses_r2, conversations, responses_eval2, eval_implmnt_prompt)
    
    num = 1

    for expert in expert_arr: #Improving
        conversations[expert].append({
    "role": "user",
    "content": f"""Provide a step-by-step plan for avoiding potential errors in the following implementation.
The plan should be thorough, well-structured, and should clearly describe the programmatic steps required to accomplish the task, with a focus on Python-specific instructions.

Do not include actual code—instead, explain each step clearly and precisely, as if you are guiding a developer through the process using only your words. Assume the plan will be followed by a team of experts, so your explanation should be sufficiently detailed to avoid the need for further clarification.

The final implementation, once the plan is followed, must fully achieve the User Objective and produce correct output.

Implementation to improve:
{implemnt}
"""
})
        response = await expert_response(conversations[expert])#
        responses_r3.append(response)
        conversations[expert].append({"role": "assistant", "content": response})
        num = num + 1

    improv_list = await evaluate_resp(expert_arr, responses_r3, conversations, responses_eval3, eval_improv_prompt)

    num = 1

    for expert in expert_arr: #Adding improvements
        conversations[expert].append({
    "role": "user",
    "content": f"""Apply the improvements specified in the following plan: {improv_list}. Return valid, executable Python code. Do not include explanations, comments, or any additional output — only the raw Python code.
{gemini_helper} {fetch_helper}
Ensure that the improvements are integrated directly into the existing solution so that it functions correctly after the modifications.
When sending a request to the model and asking it to return code or structured data (such as JSON), make sure the output is not wrapped in Markdown formatting. 
Markdown wrappers can cause parsing errors and lead to incorrect handling of the returned content. 
Better provide answers in plain text—use paragraphs, bullet points, or other human-readable formats.
Do not wrap the code in exec(""" """). Do not write code in Markdown format. 
Instead, provide it as plain text. Do not include any prompts asking the user to enter information, such as input(). 
Do not write any code that accesses, manipulates, or defines API keys in any way. 
This includes reading from environment variables, hardcoding keys, or creating helper functions to retrieve or validate API keys. 
Return the code as plain Python code.
Returned Python script has to print the result to the console using print()."""
})
        response = await expert_response(conversations[expert])#
        responses_r4.append(response)
        conversations[expert].append({"role": "assistant", "content": response})
        num = num + 1

    improv_implmnt = await evaluate_resp(expert_arr, responses_r4, conversations, responses_eval4, eval_imprv_implmnt_prompt)

    
    conversations[expert_arr[0]].append({
    "role": "user",
    "content": f"""Here is a code: {improv_implmnt}.
Please provide a list of all Python libraries that need to be installed to successfully execute this file.
Make sure your list includes all the necessary libraries so that the code runs correctly without errors. 
Format your answer as a pure Python list of strings, like this:
["numpy", "pandas", "matplotlib"]

Do not include any explanations or comments. Return only the list."""
})
    str_libs = await expert_response(conversations[expert_arr[0]])
    
    list_libs = []
#     print("\n\nHEREEEEEE IS WHAT GPT-4o GAVE:\n" + str_libs) 
#     print(f"""\nMy user prompt:\nHere is a code: {improv_implmnt}.
# Please provide a list of all Python libraries that need to be installed to successfully execute this file.
# Make sure your list includes all the necessary libraries so that the code runs correctly without errors. 
# Format your answer as a pure Python list of strings, like this:
# ["numpy", "pandas", "matplotlib"]

# Do not include any explanations or comments. Return only the list.""")
    
    print("\n\nHello\n\n")

    list_libs = ast.literal_eval(str_libs)
    for lib in list_libs:
        install(lib)
    #result = exec(improv_implmnt)

    with open("temp_script.py", "w", encoding="utf-8") as f:
        f.write(improv_implmnt)

    # 4. Виконання коду через exec
    result = subprocess.run([sys.executable, "temp_script.py"], capture_output=True, text=True)

    #result = subprocess.run(["python", "temp_script.py"], capture_output=True, text=True)
    end = time.perf_counter()
    #print(f"Час виконання: {end - start:.4f} секунд")

    output = result.stdout
    errput = result.stderr


    # 6. Збираємо всі результати
    final = f"""
<strong style='font-size: 20px;'>Experts:</strong><br>{experts.replace('\n', '<br>')}<br><br>
<strong style='font-size: 20px;'>Round 1 (Step-by-step plan):</strong><br>{'<br>'.join(responses_r1)}<br><br>
<strong style='font-size: 20px;'>Evaluate plans:</strong><br>{'<br>'.join(responses_eval1)}<br><br>
<strong style='font-size: 20px;'>Round 2 (Implementation):</strong><br>{'<br>'.join(responses_r2)}<br><br>
<strong style='font-size: 20px;'>Evaluate implementations:</strong><br>{'<br>'.join(responses_eval2)}<br><br>
<strong style='font-size: 20px;'>Round 3 (List Of Improvements/Potential errors):</strong><br>{'<br>'.join(responses_r3)}<br><br>
<strong style='font-size: 20px;'>Evaluate implementations:</strong><br>{'<br>'.join(responses_eval3)}<br><br>
<strong style='font-size: 20px;'>Round 4 (Implementation with improvements):</strong><br>{'<br>'.join(responses_r4)}<br><br>
<strong style='font-size: 20px;'>Evaluate implementations:</strong><br>{'<br>'.join(responses_eval4)}<br><br>
<strong style='font-size: 20px;'>Resulting generated code:</strong><br>{improv_implmnt.replace('\n', '<br>')}<br><br>
<strong style='font-size: 20px;'>Result of the code:</strong><br>{output.replace('\n', '<br>')}<br><br>
<strong style='font-size: 20px;'>Stderr --> List of errors:</strong><br>{errput.replace('\n', '<br>')}<br><br>
<strong style='font-size: 20px;'>Stderr --> Total latency (time):</strong><br>{end - start:.4f}<br><br>
"""#
    
    final2 = f"""
Resulting generated code: {improv_implmnt}
Result of the code: {output}
Stderr --> List of errors:{errput}
Stderr --> Total latency (time): {end - start:.4f}
\n\n\n"""
    
    final3 = f"""
Result of the code: {output}
Stderr --> List of errors:{errput}
Stderr --> Total latency (time): {end - start:.4f}
\n\n\n"""
    return final2
