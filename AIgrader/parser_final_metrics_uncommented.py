import json

with open("1_1Danylo.json", "r", encoding="UTF-8") as f:
    first = json.load(f)

with open("1_2.json", "r", encoding="UTF-8") as f:
    second = json.load(f)

with open("1_3.json", "r", encoding="UTF-8") as f:
    third = json.load(f)

with open("1_4.json", "r", encoding="UTF-8") as f:
    fourth = json.load(f)

n = 4
result = {}
#result["total_checkpoints_mismatched"] = 0
total_checkpoints_mismatched = 0
result["total_checkpoints"] = 0
total_checkpoints = 0
result["total_tasks"] = 0

total_tasks = 0
run_worst_case = 0
run_best_case = 0
run_median_case = 0

for task in first["tests"].keys():
    result[task] = {}
    cnt_checkpoints = 0
    total_checkpoints += len(first["tests"][task]["checkpoints"])
    total_tasks += 1

    task_worst_case = 0
    task_best_case = 0
    task_median_case = 0
    for i in range(len(first["tests"][task]["checkpoints"])):
        #worst_case, best_case, median
        ai_result_1 = first["tests"][task]["checkpoints"][i].get("ai_result", first["tests"][task]["checkpoints"][i]["result"])
        ai_result_2 = second["tests"][task]["checkpoints"][i].get("ai_result", second["tests"][task]["checkpoints"][i]["result"])
        ai_result_3 = third["tests"][task]["checkpoints"][i].get("ai_result", third["tests"][task]["checkpoints"][i]["result"])
        ai_result_4 = fourth["tests"][task]["checkpoints"][i].get("ai_result", fourth["tests"][task]["checkpoints"][i]["result"])
        #first["tests"][task]["checkpoints"][i]["worst_case"] = min(ai_result_1, ai_result_2, ai_result_3, ai_result_4)
        task_worst_case += min(ai_result_1, ai_result_2, ai_result_3, ai_result_4)
        #first["tests"][task]["checkpoints"][i]["best_case"] = max(ai_result_1, ai_result_2, ai_result_3, ai_result_4)
        task_best_case += max(ai_result_1, ai_result_2, ai_result_3, ai_result_4)
        #first["tests"][task]["checkpoints"][i]["median_case"] = (ai_result_1 + ai_result_2 + ai_result_3 + ai_result_4) / n
        task_median_case += (ai_result_1 + ai_result_2 + ai_result_3 + ai_result_4) / n

        # st = set()
        # assessment1 = first["tests"][task]["checkpoints"][i].get("ai_result", "-")
        # assessment2 = second["tests"][task]["checkpoints"][i].get("ai_result", "-")
        # assessment3 = third["tests"][task]["checkpoints"][i].get("ai_result", "-")
        # assessment4 = fourth["tests"][task]["checkpoints"][i].get("ai_result", "-")
        # if not assessment1 == assessment2 == assessment3 == assessment4:
        #     cnt_checkpoints += 1
        #     st.add(assessment1)
        #     st.add(assessment2)
        #     st.add(assessment3)
        #     st.add(assessment4)
        #     first_final_score = {
        #         "ai_result": first["tests"]
        #         .get(task, {})
        #         .get("final_score", {})
        #         .get("ai_result", "-"),
        #     }
        #     second_final_score = {
        #         "ai_result": second["tests"]
        #         .get(task, {})
        #         .get("final_score", {})
        #         .get("ai_result", "-"),
        #     }
        #     third_final_score = {
        #         "ai_result": third["tests"]
        #         .get(task, {})
        #         .get("final_score", {})
        #         .get("ai_result", "-"),
        #     }
        #     fourth_final_score = {
        #         "ai_result": fourth["tests"]
        #         .get(task, {})
        #         .get("final_score", {})
        #         .get("ai_result", "-"),
        #     }                
        #     result[task][f"checkpoint{i + 1}"] = f"Different assessments: {len(st)}"
        #     result[task][f"total_points"] = first["tests"].get(task, {}).get("final_score", {}).get("total", "-")

    result[task][f"total_points"] = first["tests"].get(task, {}).get("final_score", {}).get("total", "-")
    # result[task]["worst_case"] = task_worst_case
    # result[task]["best_case"] = task_best_case
    # result[task]["median_case"] = task_median_case
    run_worst_case += task_worst_case
    run_best_case += task_best_case
    run_median_case += task_median_case
    
    # total_checkpoints_mismatched += cnt_checkpoints
    # if cnt_checkpoints != 0:        
    #     result[task]["number_of_diff_checkpoints"] = cnt_checkpoints
    #     result[task]["first_final_score"] = first_final_score
    #     result[task]["second_final_score"] = second_final_score
    #     result[task]["third_final_score"] = third_final_score
    #     result[task]["fourth_final_score"] = fourth_final_score

result["run_worst_case"] = run_worst_case
result["run_best_case"] = run_best_case
result["run_median_case"] = run_median_case
# result["total_checkpoints_mismatched"] = total_checkpoints_mismatched        
result["total_checkpoints"] = total_checkpoints
result["total_tasks"] = total_tasks

with open("old-worst-best-median-cases-responses-api-without-seed.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
# with open("diff_checkpoints_across_4_analysis.json", "w", encoding="utf-8") as f:
#     json.dump(result, f, ensure_ascii=False, indent=2)
