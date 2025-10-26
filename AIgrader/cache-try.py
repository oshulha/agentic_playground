import asyncio
# from langchain_core.globals import set_llm_cache
# from langchain_core.caches import InMemoryCache
from langchain_openai import ChatOpenAI
from langsmith import traceable, Client
from langsmith.run_helpers import get_current_run_tree
import time

# set_llm_cache(InMemoryCache())
@traceable()
async def call_nano(ind):
    run_tree = get_current_run_tree()
    if run_tree:
        run_tree.name = f"call_nano_{ind}"
    llm = ChatOpenAI(model="gpt-5-nano", temperature=0)
    #chars1 = "error " * 2000 + " mistake " * 500
    chars1 = ""
    res1 = await llm.ainvoke(f"Explain Caesar cipher in 1 sentence {chars1}", prompt_cache_key="res1")
    print(res1.content)
    print("=" * 30)


def token_and_cost_details(run_id):
    # Fetch the root run
    client = Client()
    run = client.read_run(run_id)

    # Access run properties
    print("=" * 30)
    print(f"Run name: {run.name}")
    print(f"Run type: {run.run_type}")
    print(f"Start time: {run.start_time}")
    print(f"Run latency:{run.latency}")
    #print(f"Run cache read details: {run.prompt_token_details["cache_read"]}")
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

@traceable(name="cache-experiments")
async def main():
    run_tree = get_current_run_tree()
    ind = 1
    await call_nano(ind)
    #await asyncio.sleep(5)
    ind += 1
    await call_nano(ind)
    #await asyncio.sleep(5)
    ind += 1
    await call_nano(ind)
    return run_tree
    #await asyncio.sleep(5)

    #get run_id - or go to langsmith ui
    # if run_tree:
    #     run_id = run_tree.id
    #     print(f"Current run ID: {run_id}")
    #     await asyncio.sleep(30)
    #     token_and_cost_details(run_id)

run_tree = asyncio.run(main())
if run_tree:
        run_id = run_tree.id
        print(f"Current run ID: {run_id}")
        time.sleep(30)
        token_and_cost_details(run_id)