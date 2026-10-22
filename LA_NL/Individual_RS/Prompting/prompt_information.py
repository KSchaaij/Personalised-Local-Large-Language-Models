import os
import json
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

"""Here the required aspects used to create the prompt are obtained """


""" Get the avg readability scores per speaker """
def get_RS(transcript_nr):
    directory = os.path.join(parent_dir, "Data")

    file_path = os.path.join(directory, transcript_nr)

    dir = os.path.join(file_path, "Lexical_profiles")
    file_p = os.path.join(dir, "10_database" + '.json')
    with open(file_p, "r", encoding = "utf-8") as file:
            profile = json.load(file)

    lix = profile["language_level"]["LIX score"]
    flesch = profile["language_level"]["Flesch score"]
    
    if lix.lower() == flesch.lower():
         level = [lix.lower()]
         print("same",level)
    else:
         level = [lix.lower(), flesch.lower()]
         print("different", level)
    return level

""" Get the interviewsnippets for the speaker """
def get_turns(transcript_nr):
    dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    directory = os.path.join(dir, "Turns_prompt_w5_75")
    dir = os.path.join(directory, transcript_nr)
    file_p = os.path.join(dir, "overview_prompts.txt")
    with open(file_p, "r", encoding="utf-8") as file:
        content = file.read()
    prompts = content.split("-- Prompt --")
    prompts = [p.strip() for p in prompts if p.strip()]
    return prompts
      
