import json
import os
import sys

"""Here the required aspects used to create the prompt are obtained"""


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

""" Get the approximations of language level for the speaker """
def get_RS(transcript_nr):
    directory = os.path.join(parent_dir, "Data_profile")

    file_path = os.path.join(directory, transcript_nr)

    dir = os.path.join(file_path, "Speaker_profiles")
    file_p = os.path.join(dir, "10_database" + '.json')
    with open(file_p, "r", encoding = "utf-8") as file:
            profile = json.load(file)

    ari = profile["language_use"]["ARI score"]
    flesch = profile["language_use"]["Flesch score"]
    
    if ari.lower() == flesch.lower():
         level = [ari.lower()]
         print("same",level)
    else:
         level = [ari.lower(), flesch.lower()]
         print("different", level)
    return level

""" Get the interviewsnippets for the speaker """
def get_turns(transcript_nr):
    directory = os.path.join(parent_dir, "Turns_prompt_w4_90")
    dir = os.path.join(directory, transcript_nr)

    file_p = os.path.join(dir, "overview_prompts.txt")
    with open(file_p, "r", encoding="utf-8") as file:
        content = file.read()

    prompts = content.split("-- Prompt --")
    prompts = [p.strip() for p in prompts if p.strip()]

    return prompts