#agenthelper.py
from openai import OpenAI
from google import genai
from google.genai import types
import requests
from urllib.parse import urlparse, unquote
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from bs4 import BeautifulSoup  

client = OpenAI(api_key="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")

reasoning_model = "o3-mini"#do not support temperature parameter
fast_model = "gpt-4o"#$5 - input $20 - output - the most expensive model here
main_model = "gpt-4o-mini"

def agentcall_OpenAI_model(system_prompt, user_prompt, agent_name, chosen_output):
    global reasoning_model, fast_model, main_model

    if(agent_name == "planner_agent"):
        model_to_use = reasoning_model
        temperature_to_use=1

    if(agent_name == "thinking_agent"):
        model_to_use = reasoning_model
        temperature_to_use=1

    if(agent_name == "knowledge_gap_agent"):
        model_to_use = reasoning_model
        temperature_to_use=1

    if(agent_name == "tool_selector_agent"):#можливо в спрощеній версії буде можна тула і все
        model_to_use = reasoning_model
        temperature_to_use=1

    if(agent_name == "crawl_agent"):#how to name correctly
        model_to_use = fast_model
        temperature_to_use=0

    if(agent_name == "search_agent"):#how to name correctly
        model_to_use = fast_model
        temperature_to_use=0#якщо там буде філтрінг, то треба ставити більше
    
    response = client.chat.completions.create(
        model=model_to_use, #use chagpt-4o-latest for wikilibs -- usually use"gpt-4.1"
        temperature=temperature_to_use,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        output_type=chosen_output
    )
    return response.choices[0].message.content 

#To Be Fair We Have To Use Gemini-Pro-1.5-0514 Due To Paper With Results Of 0.729
# Характеристики Gemini 1.5 Pro (версія 0514)
# Дата випуску: 14 травня 2024 року.
# Контекстне вікно: До 1 мільйона токенів для користувачів Gemini Advanced.

#Порівняння з поточною версією Gemini 1.5 Pro
# Після версії 0514, Google представила оновлення, які розширили можливості моделі:
# # Контекстне вікно: Збільшено до 2 мільйонів токенів для розробників через AI Studio та Vertex AI.
# Оптимізації: Впроваджено кешування контексту, що зменшує витрати при повторному використанні інформації.

def call_Gemini_model(system_prompt, user_prompt, max_tokens):
    client = genai.Client(api_key="AIzaSyCJfra7a9AEGc9pIv-Q9DctrwxVApuZ634")

    response = client.models.generate_content(
        model="gemini-1.5-pro", 
        contents=user_prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max_tokens,
            temperature=0,
            system_instruction=system_prompt
            )
    )
    return response.text

def _clean_wiki_content(soup: BeautifulSoup) -> str:
    content_div = soup.find("div", class_="mw-content-container")
    if content_div:
        tags = content_div.find_all(["p", "h2", "h3"])
        extracted_text = "\n\n".join(tag.get_text(strip=True) for tag in tags)
    else:
        extracted_text = "Can`t find div with class 'mw-content-container'."

    return extracted_text


def fetch_wiki(url, wait_time=5):
    # Налаштування headless-режиму
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')

    # Створюємо Service об'єкт для ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Створюємо WebDriver з сервісом і опціями
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(wait_time)  # Чекаємо на завантаження JS-контенту
        html = driver.page_source
        text = html
        soup = BeautifulSoup(text, "html.parser")
        text = _clean_wiki_content(soup)
        return text
    finally:
        driver.quit()

#Wikipedia API Variant
# def extract_wiki_title(url: str) -> str:
#     path = urlparse(url).path  
#     if path.startswith("/wiki/"):
#         title = path[len("/wiki/"):]  
#         return unquote(title)  
#     return None

# def fetch_wiki(wiki_link):
#     title = extract_wiki_title(wiki_link)
#     url = "https://en.wikipedia.org/w/api.php"
#     params = {
#         "action": "query",
#         "format": "json",
#         "prop": "extracts",
#         "explaintext": True,
#         "titles": title
#     }
#     response = requests.get(url, params=params)
#     data = response.json()
#     page = next(iter(data["query"]["pages"].values()))
#     text = page.get("extract", "No data")
#     # first_10000_words = ' '.join(text.split()[:10000])
#     return text