from langsmith import Client
from dotenv import load_dotenv
from decimal import Decimal
import json

result = { "grader_details" : {
            "run_name" : "AI Grader Nano Sum Of 3 Runs",
            "run_type" : "chain",
            "start_time" : "2025-10-25 20:17:09.542205",
            "total_tokens" : 0,
            "total_tokens_details" : {
                "total_completion_tokens" : 0,
                "total_prompt_tokens" : 0,
                "total_prompt_cache_read" : 0,
                "total_completion_reasoning" : 0,
            },
            "total_latency" : 0,
            "total_cost" : 0,
            "total_cost_details": {
                "total_completion_cost" : 0,
                "total_prompt_cost" : 0
            },
        }
    }

def token_and_cost_details(run_id):
    # Fetch the root run
    client = Client()
    run = client.read_run(run_id)

    # Access run properties
    print("=" * 30)
    print(f"Run name: {run.name}")
    print(f"Run type: {run.run_type}")
    print(f"Run latency: {run.latency}")
    print(f"Start time: {run.start_time}")
    print(f"Run cache read details: {run.prompt_token_details["cache_read"]}")
    print(f"Run prompt token details: {run.prompt_token_details}")
    print(f"Run prompt tokens: {run.prompt_tokens}")
    print(f"Run completion tokens: {run.completion_tokens}")
    print(f"Run total tokens: {run.total_tokens}")
    print(f"Run completion token details: {run.completion_token_details}")
    print(f"Run total cost: {run.total_cost}")
    print(f"Run prompt cost: {run.prompt_cost}")
    print(f"Run completion cost: {run.completion_cost}")
    print(f"Run prompt cost details: {run.prompt_cost_details}")
    print(f"Run completion cost details: {run.completion_cost_details}")
    print("=" * 30)

    result["grader_details"]["total_tokens"] = run.total_tokens
    result["grader_details"]["total_tokens_details"]["total_completion_tokens"] = run.completion_tokens
    result["grader_details"]["total_tokens_details"]["total_prompt_tokens"] = run.prompt_tokens
    result["grader_details"]["total_tokens_details"]["total_prompt_cache_read"] = run.prompt_token_details.get("cache_read", 0)
    result["grader_details"]["total_tokens_details"]["total_completion_reasoning"] = run.completion_token_details.get("reasoning", 0)

    result["grader_details"]["total_latency"] = float(run.latency) if isinstance(run.latency, Decimal) else run.latency
    result["grader_details"]["total_cost"] = float(run.total_cost) if isinstance(run.total_cost, Decimal) else run.total_cost
    result["grader_details"]["total_cost_details"] = {}
    result["grader_details"]["total_cost_details"]["total_completion_cost"] = float(run.completion_cost) if isinstance(run.completion_cost, Decimal) else run.completion_cost
    result["grader_details"]["total_cost_details"]["total_prompt_cost"] = float(run.prompt_cost) if isinstance(run.prompt_cost, Decimal) else run.prompt_cost

load_dotenv()

# Replace with your specific run ID (UUID)
run_id1 = "f90574e9-e8ee-4d0d-bfda-f301be71a826" #Took It From LangSmith UI
# run_id2 = "3d053074-8d93-4d41-85e2-db1569cda2cf"
# run_id3 = "6a81659e-218e-4985-99e7-cd05937d2332"

# run_id4 = "c44f1ce3-d46e-49d0-8a5f-f0bc611f355b"

token_and_cost_details(run_id1)
# token_and_cost_details(run_id2)
# token_and_cost_details(run_id3)



for k, v in result["grader_details"].items():
    print(str(k) + " : " + str(v))

with open("/home/oleksandr/Downloads/AIgraderPrompt/token_and_cost_details.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
# token_and_cost_details(run_id4)