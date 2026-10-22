import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

"""Here the required aspects used to create the prompt are obtained"""

""" Get the information for all three features used in the combined simulation"""
def get_linguistic_constraints(transcript_nr):
    directory = os.path.join(parent_dir, "Data_profile")

    file_path = os.path.join(directory, transcript_nr)

    dir = os.path.join(file_path, "Speaker_profiles")
    file_p = os.path.join(dir, "10_database" + '.json')
    with open(file_p, "r", encoding = "utf-8") as file:
            profile = json.load(file)

    # Get the common words and expressions to be added in the prompt
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

    # Get the sentence length
    sl = profile["sentence_info"]["avg sentence length"]

    # Get the readability scores
    ari = profile["language_use"]["ARI score"]
    flesch = profile["language_use"]["Flesch score"]
    
    if ari.lower() == flesch.lower():
         level = [ari.lower()]
         print("same",level)
    else:
         level = [ari.lower(), flesch.lower()]
         print("different", level)

    return POS, sl, level

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