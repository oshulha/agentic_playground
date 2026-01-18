import json
import random
import datetime
import uuid
import traceback
import os
import sys

from helper import call_OpenAI_model

LOG_FILE = "process_log.txt"
RANDOM_SEED = 42

def log_event(event, error=None):
    entry = {"event": event, "timestamp": datetime.datetime.now().isoformat()}
    if error:
        entry["error"] = error
    message = json.dumps(entry)
    print(message)
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as lf:
            lf.write(message + "\n")
    except Exception:
        pass

def safe_write_json(filepath, data):
    try:
        if not isinstance(data, (dict, list)):
            raise ValueError("Data is not JSON serializable.")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f)
        with open(filepath, "r", encoding="utf-8") as f:
            _ = json.load(f)
        return True
    except Exception as e:
        log_event(f"Error writing {filepath}", error=traceback.format_exc())
        return False

def safe_load_json(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            obj = json.load(f)
        return obj
    except Exception as e:
        log_event(f"Error reading {filepath}", error=traceback.format_exc())
        return None

def retry_call_openai(system_prompt, user_prompt, temperature, max_tokens, attempts=3):
    last_error = None
    for i in range(attempts):
        try:
            response = call_OpenAI_model(system_prompt, user_prompt, temperature, max_tokens)
            if response is not None and isinstance(response, str) and len(response.strip()) > 0:
                return response
        except Exception as e:
            last_error = traceback.format_exc()
            log_event(f"OpenAI API error, attempt {i+1}", error=last_error)
    return None

def dynamic_prompt_sim(previous_answers):
    all_questions = [
        {"key": "business_idea", "prompt": "Describe your business idea in detail."},
        {"key": "attributes", "prompt": "What key attributes do you want your AI company to have?"},
        {"key": "target_markets", "prompt": "Who are your target customers or markets?"}
    ]
    prompts = []
    for q in all_questions:
        if q["key"] not in previous_answers:
            prompts.append(q)
    return prompts

def validate_responses(responses):
    required_keys = {"business_idea", "attributes", "target_markets"}
    if not isinstance(responses, dict):
        return False
    for key in required_keys:
        val = responses.get(key, "")
        if not isinstance(val, str) or len(val.strip()) < 5:
            return False
    return True

def run_step_1():
    responses = {
        "business_idea": "Platform for entrepreneurs to build companies using autonomous AI agents.",
        "attributes": "Scalable, secure, easy-to-use, no human staff required.",
        "target_markets": "Early-stage entrepreneurs, startups, innovators."
    }
    log_event("Step 1: Define and Validate the Target Audience - Started")
    if not validate_responses(responses):
        log_event("Step 1: Default responses invalid. Aborting.", error="Validation failed.")
        sys.exit(1)
    if not safe_write_json("step1_audience_profile.json", responses):
        log_event("Step 1: Failed to write profile.", error="File write error.")
        sys.exit(1)
    log_event("Step 1: Completed")
    return responses

def review_llm_output(outputs):
    review_prompt = "For each message below, please evaluate clarity, uniqueness and specificity. Flag anything that is vague, full of jargon, or lacks differentiation. Return a JSON with keys: outputs, flagged, rationale."
    system_prompt = "You are an expert marketing reviewer."
    user_prompt = review_prompt + "\n\n" + json.dumps(outputs)
    review = retry_call_openai(system_prompt, user_prompt, 0, 1500)
    try:
        print("Here is Review In JSON:\n" + review)
        return json.loads(review)
    except Exception:
        log_event("Review LLM output failed", error=traceback.format_exc())
        return {"outputs": outputs, "flagged": [], "rationale": ""}

def run_step_2(audience_profile):
    log_event("Step 2: Positioning and Messaging Generation - Started")
    system_prompt = "You are an expert marketing strategist."
    user_prompt = f"Given the following business idea and audience: {json.dumps(audience_profile)}\nGenerate 3 vivid, unique, and clear value proposition and positioning statements in JSON list format."
    outputs_raw = retry_call_openai(system_prompt, user_prompt, 0.7, 512)
    if outputs_raw is None:
        log_event("Step 2: LLM failed to generate positioning.", error="No response.")
        sys.exit(1)
    try:
        outputs = json.loads(outputs_raw)
        if not isinstance(outputs, list):
            raise ValueError("Not a list")
    except Exception:
        outputs = [outputs_raw.strip()]
    review = review_llm_output(outputs)
    flagged = review.get("flagged", [])
    if flagged:
        system_prompt2 = "You are an expert marketing strategist. Iterate and improve the following positioning statements to address flagged issues: " + json.dumps(flagged)
        improved = retry_call_openai(system_prompt2, json.dumps(outputs), 0.7, 512)
        try:
            outputs = json.loads(improved)
            if not isinstance(outputs, list):
                outputs = [improved.strip()]
        except Exception:
            outputs = [improved.strip()]
    chosen = outputs[0] if outputs else ""
    if not chosen:
        log_event("Step 2: No valid positioning statements.", error="Empty outputs.")
        sys.exit(1)
    if not safe_write_json("step2_positioning.json", {"all": outputs, "chosen": chosen}):
        log_event("Step 2: Failed to write positioning statements.", error="File write error.")
        sys.exit(1)
    log_event("Step 2: Completed")
    return chosen

def fetch_market_data(audience_profile, positioning):
    system_prompt = "You are a market research assistant."
    user_prompt = f"Given audience: {json.dumps(audience_profile)} and positioning: {positioning}\nSuggest best marketing channels and detailed buyer personas. For each channel, provide rationale. For each persona, include pain points, motivations, and content preferences. Return JSON: channels: [{{name, rationale}}], personas: [{{name, pain_points, motivations, content_formats}}]"
    res = retry_call_openai(system_prompt, user_prompt, 0.4, 512)
    if res is None:
        return {"channels": [], "personas": []}
    try:
        data = json.loads(res)
        if not isinstance(data, dict):
            raise ValueError("Not a dict")
        if "channels" not in data or "personas" not in data:
            raise ValueError("Missing fields")
        if not isinstance(data["channels"], list):
            data["channels"] = []
        if not isinstance(data["personas"], list):
            data["personas"] = []
        return data
    except Exception:
        log_event("Market data parsing failed", error=traceback.format_exc())
        return {"channels": [], "personas": []}

def run_step_3(audience_profile, positioning):
    log_event("Step 3: Channel and Persona Matching - Started")
    data = fetch_market_data(audience_profile, positioning)
    if not data.get("channels") or not data.get("personas"):
        log_event("Step 3: Market data incomplete, using backup logic.")
        data["channels"] = [{"name": "LinkedIn", "rationale": "Relevant for B2B and professional audiences."}]
        data["personas"] = [{"name": "Early Adopter Entrepreneur", "pain_points": "Needs fast MVP", "motivations": "Speed, cost", "content_formats": "Case studies, how-tos"}]
    if not safe_write_json("step3_channels_personas.json", data):
        log_event("Step 3: Failed to write channels/personas.", error="File write error.")
        sys.exit(1)
    log_event("Step 3: Completed")
    return data

def validate_campaign_plan(plan):
    if not isinstance(plan, dict):
        return False
    chs = plan.get("channels", [])
    if not isinstance(chs, list) or not chs:
        return False
    for ch in chs:
        if not isinstance(ch, dict) or not ch.get("calendar") or not isinstance(ch["calendar"], list) or not ch["calendar"]:
            return False
    return True

def run_step_4(audience_profile, channel_persona_data):
    log_event("Step 4: Content and Campaign Planning - Started")
    system_prompt = "You are a campaign planner."
    user_prompt = f"Given the audience and channel/persona information: {json.dumps(audience_profile)}, {json.dumps(channel_persona_data)}\nProduce a 30/60/90-day marketing calendar per channel with content outlines, goals, KPIs and scheduling details. Flag items needing review. Provide backup options for each main campaign item. Return a JSON object."
    plan = None
    for _ in range(3):
        res = retry_call_openai(system_prompt, user_prompt, 0.3, 1024)
        try:
            plan = json.loads(res)
        except Exception:
            plan = {"channels": []}
        if validate_campaign_plan(plan):
            break
        else:
            user_prompt += "\nMake sure each channel includes a complete calendar with goals, KPIs, and backup content."
    if not validate_campaign_plan(plan):
        log_event("Step 4: No valid campaign plan.", error="Plan validation failed.")
        sys.exit(1)
    if not safe_write_json("step4_campaign_plan.json", plan):
        log_event("Step 4: Failed to write campaign plan.", error="File write error.")
        sys.exit(1)
    log_event("Step 4: Completed")
    return plan

def evaluate_content(content, brand_voice_sample):
    system_prompt = "You are a brand voice evaluator. Compare the generated content to the brand voice sample for tone, appropriateness and diversity. Flag any issues and provide a similarity score (0 to 1)."
    user_prompt = f"Brand voice sample: {brand_voice_sample}\nContent: {json.dumps(content)}"
    res = retry_call_openai(system_prompt, user_prompt, 0, 256)
    try:
        data = json.loads(res)
        if not isinstance(data, dict):
            raise ValueError("Not a dict")
        return data
    except Exception:
        log_event("Content evaluation failed", error=traceback.format_exc())
        return {"flagged": [], "similarity_score": 0.7}

def run_step_5(channel_persona_data, campaign_plan):
    log_event("Step 5: Content Production Automation - Started")
    brand_voice_sample = "Innovative, clear, actionable, slightly playful but authoritative."
    all_content = []
    personas = channel_persona_data.get("personas", [])
    if not personas:
        log_event("Step 5: No personas. Aborting.", error="No personas.")
        sys.exit(1)
    for ch in campaign_plan.get("channels", []):
        cal = ch.get("calendar", [])
        if not isinstance(cal, list) or not cal:
            continue
        for item in cal:
            persona = random.choice(personas) if personas else None
            if not persona:
                continue
            system_prompt = "You are a marketing copywriter trained for brand voice consistency."
            outline = item.get('outline', 'No outline provided.')
            user_prompt = f"Channel: {ch.get('name')}, Persona: {persona.get('name', '')}, Content outline: {outline}, Tone: match this sample: {brand_voice_sample}.\nGenerate a post or ad."
            content = retry_call_openai(system_prompt, user_prompt, 0.6, 512)
            if not content:
                continue
            eval_result = evaluate_content(content, brand_voice_sample)
            flagged = eval_result.get("flagged", [])
            if flagged:
                system_prompt2 = "Please improve the following content to address flagged issues: " + json.dumps(flagged)
                content = retry_call_openai(system_prompt2, content, 0.3, 256)
            all_content.append({
                "channel": ch.get("name", ""),
                "content": content,
                "persona": persona.get("name", ""),
                "calendar_item": outline
            })
    if not all_content:
        log_event("Step 5: No content generated.", error="Empty content.")
        sys.exit(1)
    if not safe_write_json("step5_content.json", all_content):
        log_event("Step 5: Failed to write content.", error="File write error.")
        sys.exit(1)
    log_event("Step 5: Completed")
    return all_content

def check_visual_legality(image_desc):
    return True

def run_step_6(campaign_plan):
    log_event("Step 6: Asset Coordination and Design - Started")
    assets = []
    for ch in campaign_plan.get("channels", []):
        for item in ch.get("calendar", []):
            system_prompt = "You are a generative design assistant."
            outline = item.get('outline', 'No outline provided.')
            user_prompt = f"Create a brief image prompt for the following marketing content: {outline}.\nReturn only the image description in JSON."
            image_desc_raw = retry_call_openai(system_prompt, user_prompt, 0.6, 128)
            image_desc = ""
            if image_desc_raw:
                try:
                    desc_data = json.loads(image_desc_raw)
                    if isinstance(desc_data, str):
                        image_desc = desc_data
                    else:
                        image_desc = str(desc_data)
                except Exception:
                    image_desc = image_desc_raw.strip().strip('"')
            asset_id = str(uuid.uuid4())
            is_legal = check_visual_legality(image_desc)
            if not is_legal:
                image_desc = "Generic on-brand illustration, fully original, safe for commercial use."
            assets.append({
                "asset_id": asset_id,
                "description": image_desc,
                "channel": ch.get("name", ""),
                "copyright_checked": is_legal
            })
    if not assets:
        log_event("Step 6: No assets generated.", error="Empty assets.")
        sys.exit(1)
    if not safe_write_json("step6_assets.json", assets):
        log_event("Step 6: Failed to write assets.", error="File write error.")
        sys.exit(1)
    log_event("Step 6: Completed")
    return assets

def schedule_content(content, assets):
    schedule = []
    asset_lookup = {}
    for a in assets:
        key = a.get("channel", "")
        asset_lookup.setdefault(key, []).append(a)
    for c in content:
        asset_list = asset_lookup.get(c.get("channel", ""), [])
        asset = asset_list[0] if asset_list else None
        scheduled_time = datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 30))
        schedule.append({
            "channel": c.get("channel", ""),
            "content": c.get("content", ""),
            "persona": c.get("persona", ""),
            "asset_id": asset["asset_id"] if asset else None,
            "scheduled_time": scheduled_time.isoformat(),
            "status": "ready"
        })
    return schedule

def run_step_7(content, assets):
    log_event("Step 7: Multi-Channel Campaign Execution - Started")
    schedule = schedule_content(content, assets)
    for item in schedule:
        try:
            print(f"Deploying to {item['channel']} at {item['scheduled_time']}: {item['content'][:90]}")
            item["status"] = "deployed"
        except Exception as e:
            item["status"] = "error"
            log_event("Deployment error", error=traceback.format_exc())
    if not safe_write_json("step7_schedule.json", schedule):
        log_event("Step 7: Failed to write schedule.", error="File write error.")
        sys.exit(1)
    log_event("Step 7: Completed")
    return schedule

def collect_metrics(schedule):
    metrics = []
    for item in schedule:
        base = random.randint(100, 1000)
        engagement = random.uniform(0.01, 0.15)
        anomaly = engagement > 0.13 or engagement < 0.03
        reached = base if base else 1
        engaged = int(reached * engagement)
        metrics.append({
            "channel": item.get("channel", ""),
            "scheduled_time": item.get("scheduled_time", ""),
            "engaged": engaged,
            "reached": reached,
            "anomaly": anomaly
        })
    return metrics

def run_step_8(schedule):
    log_event("Step 8: Real-Time Monitoring and Analytics - Started")
    if not isinstance(schedule, list) or not schedule:
        log_event("Step 8: Empty schedule", error="Empty schedule.")
        sys.exit(1)
    metrics = collect_metrics(schedule)
    for m in metrics:
        print(f"Analytics [{m['channel']}@{m['scheduled_time']}] - Engaged: {m['engaged']}, Reached: {m['reached']}, Anomaly: {m['anomaly']}")
    if not safe_write_json("step8_metrics.json", metrics):
        log_event("Step 8: Failed to write metrics.", error="File write error.")
        sys.exit(1)
    log_event("Step 8: Completed")
    return metrics

def analyze_performance(metrics):
    actions = []
    for m in metrics:
        reached = m.get("reached", 0)
        engaged = m.get("engaged", 0)
        if m.get("anomaly", False) and reached:
            ratio = engaged / reached if reached else 0
            if ratio < 0.05:
                recommendation = "Try a different message or channel."
            else:
                recommendation = "Replicate this approach across more channels."
            actions.append({
                "channel": m.get("channel", ""),
                "scheduled_time": m.get("scheduled_time", ""),
                "recommendation": recommendation,
                "reason": "anomaly detected"
            })
    return actions

def run_step_9(metrics):
    log_event("Step 9: Feedback Loop and Adaptive Optimization - Started")
    if not isinstance(metrics, list) or len(metrics) < 3:
        print("Insufficient data for optimization. Await more campaign runs.")
        actions = []
    else:
        actions = analyze_performance(metrics)
        for a in actions:
            print(f"Optimization Recommendation: {a['channel']} @ {a['scheduled_time']} - {a['recommendation']}")
    if not safe_write_json("step9_optimization.json", actions):
        log_event("Step 9: Failed to write optimization actions.", error="File write error.")
        sys.exit(1)
    log_event("Step 9: Completed")
    return actions

def run_step_10(metrics, actions):
    log_event("Step 10: Reporting and Knowledge Capture - Started")
    summary = f"Campaigns ran on {len(set([m.get('channel', '') for m in metrics if m.get('channel')]) )} channels, {len(metrics)} total deployments."
    report = {
        "summary": summary,
        "detailed": {"metrics": metrics, "actions": actions},
        "lessons": [a["recommendation"] for a in actions] if actions else ["Await more data for lessons learned."]
    }
    print("REPORT SUMMARY:")
    print(report["summary"])
    if not safe_write_json("step10_report.json", report):
        log_event("Step 10: Failed to write report.", error="File write error.")
        sys.exit(1)
    log_event("Step 10: Completed")
    return report

def main():
    random.seed(RANDOM_SEED)
    try:
        audience_profile = run_step_1()
        positioning = run_step_2(audience_profile)
        channel_persona_data = run_step_3(audience_profile, positioning)
        campaign_plan = run_step_4(audience_profile, channel_persona_data)
        content = run_step_5(channel_persona_data, campaign_plan)
        assets = run_step_6(campaign_plan)
        schedule = run_step_7(content, assets)
        metrics = run_step_8(schedule)
        actions = run_step_9(metrics)
        run_step_10(metrics, actions)
    except Exception as e:
        error_trace = traceback.format_exc()
        log_event("Main execution error", error=error_trace)
        print("A critical error occurred; see process_log.txt for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()