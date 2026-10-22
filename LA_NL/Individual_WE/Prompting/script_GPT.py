from openai import OpenAI
import json
import os
import config           ## Insert keys manually
from prompt_information import get_POS, get_turns
from QG_prompt import dev_set
transcripts = dev_set

"""Here we retrieve the relevant functions needed to run the OpenAI model using API"""

"""We need to decide whether we want to run the models on the Question Generation or the Reflection Generation
Uncomment the one we want to run."""
# from QG_prompt import get_prompt_LA, get_prompt_NA
# name = "QG_output"
from RG_prompt import get_prompt_LA, get_prompt_NA
name = "RG_output"


""" Create output path"""
output_path = name + "/dev_results.json"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
existing_data = []

""" Run the model """
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
    ## Get the information for the prompts
    lexical_constraints = get_POS(transcript)       
    interview_context = get_turns(transcript)       
    nr = len(interview_context)
    results = []

    for i in range(nr):
        if condition == "LA":
            prompt = get_prompt_LA(interview_context[i], lexical_constraints)
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
            "condition": key[1],
            "turn_index": i,
            "prompt": str(prompt),
            "response": str(result)
        })
    return results

conditions = ["LA", "NA"]
all_data = []


for transcript in transcripts:    
    for condition in conditions:
        new_data = running(transcript, condition, m)
        if new_data:
            existing_data.extend(new_data)
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(existing_data, f, indent=2,ensure_ascii=False)
