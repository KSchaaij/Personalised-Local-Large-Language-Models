import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

"""Here the required aspects used to create the prompt are obtained"""

""" Get the common words and expression (lexical profile) """
def get_POS(transcript_nr):
    directory = os.path.join(parent_dir, "Data_profile")

    file_path = os.path.join(directory, transcript_nr)

    dir = os.path.join(file_path, "Lexical_profiles")
    file_p = os.path.join(dir, "10_database" + '.json')
    with open(file_p, "r", encoding = "utf-8") as file:
            profile = json.load(file)

    # Get the terms to be added in the prompt
    adj = profile["ADJ"]["common"]
    pron = profile["PRON"]["common"]
    verbs = profile["VERB"]["common"]
    adv = profile["ADV"]["common"]
    conj = profile["CONJ"]["common"]
    ngrams = profile["ngrams"]["common"]

    POS = {
    "Adjectives": adj,
    "Pronouns":pron,
    "Verbs": verbs,
    "Adverbs": adv,
    "Conjunctions":conj,
    "Fixed expressions": ngrams
    }

    pron = ["I" if p.lower() == "i" else p for p in pron]
    ngrams = [re.sub(r"(?<!\w)i(?!\w)", "I", n) for n in ngrams]

    POS = {
        "Adjectives": adj,
        "Pronouns": pron,
        "Verbs": verbs,
        "Adverbs": adv,
        "Conjunctions": conj,
        "Fixed expressions": ngrams
    }

    POS = {k: v for k, v in POS.items() if v}

    return POS

""" Get the interviewsnippets for the speaker """
def get_turns(transcript_nr):
    directory = os.path.join(parent_dir, "Turns_prompt_w4_90")
    dir = os.path.join(directory, transcript_nr)

    file_p = os.path.join(dir, "overview_prompts.txt")
    with open(file_p, "r", encoding="utf-8") as file:
        content = file.read()

    # Split the content on recognisable delimiter
    prompts = content.split("-- Prompt --")
    prompts = [p.strip() for p in prompts if p.strip()]

    return prompts