import json
import os
from openai import OpenAI

import config  ## Need to update with correct keys etc.
from QG_prompt import dev_set
from prompt_information import get_RS, get_turns

"""Here we retrieve the relevant functions needed to run the OpenAI model using API """


"""We need to decide whether we want to run the models on the Question Generation or the Reflection Generation
Uncomment the one we want to run."""
from QG_prompt import get_prompt_LA, get_prompt_NA
name = "QG_output"
# from RG_prompt import get_prompt_LA, get_prompt_NA
# name = "RG_output"

""" Create output path """
output_path = name + "/results.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
existing_data = []
""" Run the model """
# API generation for the reference model
# The long-running response check (>1 minute) was not triggered for this model and was therefore left out in the current script.
def run_OpenAI(client, prompt, m):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        model= m,
    )
    generated_answer = chat_completion.choices[0].message.content
    return generated_answer


m = "gpt-4.1-2025-04-14"

""" Run the script for response generation """
def running(transcript, condition, m):
    readability_measures = get_RS(transcript)      
    interview_context = get_turns(transcript)      
    nr = len(interview_context)
    results = []

    for i in range(nr):
        if condition == "LA":
            prompt = get_prompt_LA(interview_context[i], readability_measures)
        elif condition == "NA":
            prompt = get_prompt_NA(interview_context[i])
        else:
            continue 

        my_api_key = config.get_openai_key()
        my_organization = config.get_openai_organization()
        client = OpenAI(
            organization=my_organization,
            api_key=my_api_key,
        )
        result = run_OpenAI(client, prompt, m)
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
for transcript in dev_set:    
    for condition in conditions:
        new_data = running(transcript, condition, m)
        if new_data:
            existing_data.extend(new_data)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2,ensure_ascii=False)
