import json
import os
from mistralai import Mistral

import config  ## Insert keys manually
from QG_prompt import test_set
from prompt_information import get_linguistic_constraints, get_turns

transcripts = test_set

"""Here we retrieve the relevant functions needed to run the models on a separate server using vLLM"""

"""We need to decide whether we want to run the models on the Question Generation or the Reflection Generation
Uncomment the one we want to run."""
# from QG_prompt import get_prompt_LA, get_prompt_NA
# name = "QG_output"
from RG_prompt import get_prompt_LA, get_prompt_NA
name = "RG_output"


""" Create output path """
output_path = name + "/results.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
existing_data = []
ss
""" Run the model """
def run_Mistral(local_client, prompt, m):  

    chat_response = local_client.chat.complete(
        model= m,
        messages=[
            {"role": "user", "content": prompt},
        ]
    )
    return chat_response.choices[0].message.content

m = "mistral-large-2512"     

""" Run the script for response generation """
def running(transcript, condition, m):
    pos, sl, rs = get_linguistic_constraints(transcript)
    interview_context = get_turns(transcript)       
    nr = len(interview_context)
    results = []

    for i in range(nr):
        if condition == "LA":
            prompt = get_prompt_LA(interview_context[i], pos, sl, rs)
        elif condition == "NA":
            prompt = get_prompt_NA(interview_context[i])
        else:
            continue  

        api_key = config.get_mistral_key()
        client = Mistral(api_key=api_key)
        result = run_Mistral(client, prompt, m)
        results.append({
            "transcript_id": transcript,
            "model": m,
            "condition": condition,
            "turn_index": i,
            "prompt": str(prompt),
            "response": str(result)
        })
    return results

conditions = ["LA", "NA"]
all_data = []

"""Loop"""
for transcript in transcripts:    
    for condition in conditions:
        new_data = running(transcript, condition, m)
        if new_data:
            existing_data.extend(new_data)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2,ensure_ascii=False)
