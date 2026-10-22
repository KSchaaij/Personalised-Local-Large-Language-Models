import requests
import json
import os
from prompt_information import get_lexical_constraints, get_turns
from QG_prompt import test_set
transcripts = test_set

"""Here we retrieve the relevant functions needed to run the models on a separate server using vLLM"""

"""We need to decide whether we want to run the models on the Question Generation or the Reflection Generation
Uncomment the one we want to run."""
# from QG_prompt import get_prompt_LA, get_prompt_NA
# name = "QG_output"

from RG_prompt import get_prompt_LA, get_prompt_NA
name = "RG_output"


""" Create output path """
output_path = name + "/"+ "results.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
existing_data = []

""" Run the model using default settings, used across models"""
def run_vLLM(prompt):
    url = "http://localhost:8000/v1/chat/completions"
    data = {
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, json=data)
    reply = response.json()["choices"][0]["message"]["content"]
    return reply.strip()
    ## The following is an option to enforce a maximum generation time of 1 minute.
    ## In case of uncommenting this, pay attention to the way the response should be postprocessed in the corresponding script.
    #     try:
    #     response = requests.post(url, json=data, timeout=60)
    #     reply = response.json()["choices"][0]["message"]["content"]
    #     return reply.strip()
    # except (requests.exceptions.Timeout,
    #         requests.exceptions.ConnectionError):
    #     return ""

""" Run the script for response generation """
def running(transcript, condition, m):
    pos, sl, rs = get_lexical_constraints(transcript)
    interview_context = get_turns(transcript)
    nr = len(interview_context)
    results = []

    for i in range(nr):
        if condition == "LA":
            prompt = get_prompt_LA(interview_context[i], pos, sl, rs)
        elif condition == "NA":
            prompt = get_prompt_NA(interview_context[i])
        else:
            continue  # optionally handle unexpected condition

        result = run_vLLM(prompt)
        results.append({
            "transcript_id": transcript,
            "model": m,
            "condition": key[1],
            "turn_index": i,
            "prompt": str(prompt),
            "response": str(result)
        })
    return results

# Adjust to the model one wants to use
# m = "XXX"

conditions = ["LA", "NA"]
all_data = []


for transcript in transcripts:    
    for condition in conditions:
        new_data = running(transcript, condition, m)
        if new_data:
            existing_data.extend(new_data)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2,ensure_ascii=False)
