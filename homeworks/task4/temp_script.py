from helper import fetch_wiki, call_Gemini_model
import time

def safe_fetch_wiki(url, retries=3, delay=2):
    for attempt in range(retries):
        try:
            content = fetch_wiki(url)
            if isinstance(content, str) and content.strip():
                return content
        except Exception as e:
            pass
        time.sleep(delay)
    print(f"ERROR: Could not fetch or validate Wikipedia content from {url}")
    exit(1)

def safe_call_gemini(system_prompt, user_prompt, max_tokens, retries=3, delay=2):
    for attempt in range(retries):
        try:
            result = call_Gemini_model(system_prompt, user_prompt, max_tokens)
            if isinstance(result, str) and result.strip():
                return result.strip()
        except Exception as e:
            pass
        time.sleep(delay)
    print("ERROR: Gemini model failed or returned empty/invalid output.")
    exit(1)

def validate_list_output(output, min_items=1):
    lines = [line.strip() for line in output.split('\n') if line.strip()]
    if len(lines) < min_items:
        print("ERROR: Model output does not contain enough valid list items.")
        exit(1)
    return lines

def validate_required_fields(text, required_fields):
    for field in required_fields:
        if field.lower() not in text.lower():
            print(f"ERROR: Required field '{field}' missing in output.")
            exit(1)

fifa_url = "https://en.wikipedia.org/wiki/FIFA_World_Cup"
london_url = "https://en.wikipedia.org/wiki/London"
ucl_url = "https://en.wikipedia.org/wiki/UEFA_Champions_League"

fifa_content = safe_fetch_wiki(fifa_url)
london_content = safe_fetch_wiki(london_url)
ucl_content = safe_fetch_wiki(ucl_url)

system_prompt_2 = "You are a meticulous data extraction assistant. Extract only the list or table of UEFA Champions League winners by season from the provided article text. For each entry, include: season (or year), winning club, and any location or city information if present. Return the result as a plain text list, one entry per line, clearly structured for easy parsing."
user_prompt_2 = ucl_content
ucl_winners_list_raw = safe_call_gemini(system_prompt_2, user_prompt_2, 3500)
ucl_winners_list_lines = validate_list_output(ucl_winners_list_raw, 1)

system_prompt_2b = "You are a careful researcher. Given the following list of UEFA Champions League winners and the full text of the London Wikipedia article, identify which of the winning clubs are based in London. Return a plain text list of club names that are based in London, one per line, and nothing else."
user_prompt_2b = "Champions League winners:\n{}\n\nLondon article:\n{}".format('\n'.join(ucl_winners_list_lines), london_content)
london_clubs_list_raw = safe_call_gemini(system_prompt_2b, user_prompt_2b, 1200)
london_clubs_list_lines = validate_list_output(london_clubs_list_raw, 1)

system_prompt_3 = "You are an analytical assistant. From the list of UEFA Champions League winners and the identified London-based clubs, find the most recent (latest) season or year in which a London club won the UEFA Champions League, but not after August 1, 2024. Return the name of the club, the season/year, and the date of the final if available, in clear plain text."
user_prompt_3 = "Champions League winners:\n{}\n\nLondon clubs:\n{}".format('\n'.join(ucl_winners_list_lines), '\n'.join(london_clubs_list_lines))
latest_london_win = safe_call_gemini(system_prompt_3, user_prompt_3, 1200)
validate_required_fields(latest_london_win, ["club", "season", "year"])

system_prompt_4 = "You are a detail-oriented temporal analyst. For the most recent London club Champions League win, clarify the exact calendar year and, if possible, the exact date the final was played, based on the UEFA Champions League Wikipedia article. Return only the club name, the season/year, and the final match date in clear plain text."
user_prompt_4 = "Most recent London club win:\n{}\n\nChampions League article:\n{}".format(latest_london_win, ucl_content)
london_win_final_date = safe_call_gemini(system_prompt_4, user_prompt_4, 600)
validate_required_fields(london_win_final_date, ["club", "season", "final"])

system_prompt_5 = "You are a data extraction bot. From the provided FIFA World Cup Wikipedia article, extract the list or table of all FIFA World Cup winners, including the winning country and the year (and date, if available) the tournament concluded. Return a plain text, structured list, each entry on a new line, with country, year, and date if available."
user_prompt_5 = fifa_content
fifa_winners_timeline_raw = safe_call_gemini(system_prompt_5, user_prompt_5, 3500)
fifa_winners_timeline_lines = validate_list_output(fifa_winners_timeline_raw, 1)

system_prompt_6 = "You are a careful chronologist. Using the timeline of FIFA World Cup winners and the exact date of the most recent Champions League final won by a London club, determine which country was the reigning FIFA World Cup holder on that date (i.e., the winner of the most recent FIFA World Cup prior to the Champions League final). Return only the country name, the year they won, and the date range of their tenure as holders in clear plain text."
user_prompt_6 = "Champions League final date:\n{}\n\nFIFA World Cup timeline:\n{}".format(london_win_final_date, '\n'.join(fifa_winners_timeline_lines))
fifa_holder = safe_call_gemini(system_prompt_6, user_prompt_6, 600)
validate_required_fields(fifa_holder, ["country", "year"])

system_prompt_7 = "You are a summary assistant. Based on the previous findings, compose a clear answer to the following: As of August 1, 2024, which country were holders of the FIFA World Cup the last time the UEFA Champions League was won by a club from London? Include in your answer the name of the London club, the year/season of their Champions League win, the date of the final, and the country that was reigning FIFA World Cup holder at that time. Present the result as a short, direct, and clear paragraph."
user_prompt_7 = "London club win info:\n{}\n\nFIFA World Cup holder info:\n{}".format(london_win_final_date, fifa_holder)
final_answer = safe_call_gemini(system_prompt_7, user_prompt_7, 400)
if not (final_answer and isinstance(final_answer, str) and final_answer.strip()):
    print("ERROR: Final answer is missing or empty.")
    exit(1)
print(final_answer)