import csv
import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from functions import preprocess, get_ngram, frequency_term_POS

""" This scripts calculated the recall and coverage scores per POS category for the generated outputs following prior work as discussed in the paper"""


""" function to calculate recall and coverage scores"""
def compute_recall_coverage(comparison, original):
    ## Comparison refers to the LLM output
    ## Original refers to the speaker profile of the speaker

    org = original
    # print(org)
    original = set(original)
    org_set = set(org)
    overlap = set()

    for v in comparison:
        if v in org_set:
            overlap.add(v)

    recall = len(overlap) / len(org_set) if org else 0
    coverage = len(overlap) / len(set(comparison)) if comparison else 0

    return recall, coverage

""" Manually adjust for which model and task the resuls need to be processed"""
var = "QG_output (raw) (raw) (raw) (raw)"
# var = "RG_output (raw) (raw) (raw) (raw)"
print(var)  # Just a reminder and check
subset = "dev_"
q =  "filtered_results_XXX.json" # Adapt to model name
print(q)    # Just a reminder and check


"""A CSV file is created to store the results of the analysis"""
results_path = os.path.join("Analysis_profile", subset + var + "_analysis_results.csv")
os.makedirs(os.path.dirname(results_path), exist_ok=True)
write_header = not os.path.exists(results_path)

if not write_header: 
    with open(results_path, 'rb+') as f:
        f.seek(-1, os.SEEK_END)
        last_char = f.read(1)
        if last_char != b'\n':
            f.write(b'\n')

results_file = open(results_path, mode="a", newline="", encoding="utf-8")
writer = csv.writer(results_file)
if write_header:
    writer.writerow([
    "Model", "Transcript_nr", "Turn", "Condition", "Metric", "Value", "POS", "Matchtype"
    ])


"""The relevant information from the speaker profile is obtained"""
def get_generated(filename):
    dir = os.path.join(filename, "Speaker_profiles")

    file_path = os.path.join(dir, "10_database.json")
    with open(file_path, 'r', encoding = "utf-8") as f:
        database = json.load(f)

    ngrams = database["ngrams"]["common"]

    return database, ngrams

"""Here the functions for word repetition are implemented"""
def word_based_measures(model, transcript, turn, condition, tokens_C, tokens_O, pos):
    Recall_E, Coverage_E = compute_recall_coverage(tokens_C, tokens_O)
    for metric, val in zip(
        ["Recall", "Coverage"],
        [Recall_E, Coverage_E]
    ):
        writer.writerow([
            model, transcript, turn, condition, metric, val, pos, "Exact"
        ])

""" Here the functions for ngrams repetition are implemented"""
def ngram_based_measures(model, transcript, turn, condition, text_C, ngrams_O):
    n_values = [2,3,4,5]
    ngrams_C = []
    sentences = re.split(r'(?<=[.!?])\s+|(?<=BREAK)\s+|(?<=\.)', text_C)
    for n in n_values:
        all_ngrams = get_ngram(sentences, int(n))
        ngrams_C.extend(all_ngrams)
    Recall_ngram_E, Coverage_ngram_E = compute_recall_coverage(ngrams_C, ngrams_O)
    for metric, val in zip(
        ["Recall", "Coverage"],
        [Recall_ngram_E, Coverage_ngram_E]
    ):
        writer.writerow([
            model, transcript, turn, condition, metric, val, "ngram", "Exact"
        ])

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
directory = os.path.join(parent_dir, "Data")
folders = [f for f in os.listdir(directory) if f.isdigit()]

"""Loop over transcripts"""
for transcript in folders:
    print(transcript)
    file_path = os.path.join(directory, transcript)
    file_p = os.path.join(subset + "Cleaned outputs", var + "_" + q)
    with open(file_p, "r", encoding = "utf-8") as file:
        data = json.load(file)

    entries_transcript = [entry for entry in data if entry['transcript_id'] == int(transcript)]
    for entry in entries_transcript:
        transcript_id = entry["transcript_id"]
        turn = str(entry['turn_index'])
        model = entry['model']
        condition = entry['condition']
        checkpoint_key = (transcript_id, turn, model)
        response = [entry['response']]

        ### Get the terms per POS caetgory for the generated output
        text_C, tokens_C = preprocess(response)  
        POS_terms_C, _, _ = frequency_term_POS(tokens_C, 5, target_pos=["PRON", "ADJ", "CONJ", "VERB", "ADV"]) # Number 5 is random and irrelevant for POS_terms_C

        ### Obtain the original words for the transcript/speaker (profile items)
        database, ngrams_O = get_generated(file_path)
        POS_list = ["PRON", "ADJ", "CONJ", "VERB", "ADV"]
        for i in POS_list:
            tokens_O = database.get(i, {}).get("common", [])
            tokens_C = POS_terms_C.get(i, [])
            word_based_measures(model, transcript, turn, condition, tokens_C, tokens_O, i)
        ngram_based_measures(model, transcript, turn, condition, text_C, ngrams_O)
results_file.close()


