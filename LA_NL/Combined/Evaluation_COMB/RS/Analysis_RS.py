import csv
import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from functions import preprocess
from Readibility_functions import get_sentences_readibility,flesch_douma_score, LIX_score


"""" In this script we analyse the readability scores per output"""
""" Manually adjust for which model and task the results need to be processed"""
var = "QG_output (raw) (raw) (raw) (raw)"
# var = "RG_output (raw) (raw) (raw) (raw)"
print(var)  # Just a reminder and check
q = "filtered_results_XXX.json"    # Adapt to model name
print(q)    # Just a reminder and check

"""A CSV file is created to store the results of the analysis"""
results_path = os.path.join("Analysis_results", var + "_analysis_results_RS.csv")
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
    "Model", "Transcript_nr", "Turn", "Condition", "[LIX, Flesch]user", "[LIX, Flesch]model", "[LIX, Flesch]deviation"])


"""The relevant information from the speaker profile is obtained"""
def get_generated(filename):
    dir = os.path.join(filename, "Speaker_profiles")

    file_path = os.path.join(dir, "10_database.json")
    with open(file_path, 'r', encoding = "utf-8") as f:
        database = json.load(f)

    RS_user_label = [
    database["language_level"]["LIX score"],
    database["language_level"]["Flesch score"]
    ]

    RS_user = [
    database["language_level"]["LIX raw"],
    database["language_level"]["Flesch raw"]
    ]
    return RS_user, RS_user_label

"""Here, the function to obtain the readability measures of the model is added """
def readability_info(model_output, RS_user, RS_user_label):
    t1 = re.sub(r'\.{3,}(?=\W)', ' PAUSE', model_output)
    t2 = re.sub(r'…(?=\W)', ' PAUSE', t1)
    t3 = t2.replace("  ", " ") #.replace(" .", ".")
    
    sentences_m = re.split(r'(?<=[.!?])\s+|(?<=BREAK)\s+|(?<=\.)', t3)
    sentences_m = [s for s in sentences_m if s and s != "BREAK"]

    # Get the scores for the generated output of LLM
    s = get_sentences_readibility(sentences_m)
    flesch = flesch_douma_score(s)
    lix = LIX_score(s)

    # Get the deviation, sings, and bools (deviation in labels yes/no)
    lix_dev = lix_deviation(lix, RS_user_label)
    flesch_dev = flesch_deviation(flesch, RS_user_label)
    RS_user = [round(score, 3) for score in RS_user]
    writer.writerow([
            model, transcript, turn, condition, RS_user, [round(lix,3), round(flesch,3)], [round(lix_dev,3), round(flesch_dev,3)]
        ])


def lix_deviation(lix, RS_user_label):
    """ A function to obtain the deviation in LIX levels of the speaker and LLM
     The mapping was based on the approximate mapping function defined in Readability_functions.py """
    target_label = RS_user_label[0]
    lix_ranges = {
        "Zeer makkelijk": (0, 20),
        "Makkelijk": (20, 30),
        "Redelijk moeilijk": (30, 40),
        "Moeilijk": (40, 50),
        "Zeer moeilijk": (50, 60),  
    }
    low, high = lix_ranges.get(target_label, (None, None))
    if low <= lix < high:
        deviation = 0
        return deviation
    elif lix < low:
        deviation = low - lix
        return deviation
    else:
        deviation = lix -high
        return deviation
    
def flesch_deviation(flesch, RS_user_label):
    """ A function to obtain the deviation in Flesch levels of the speaker and LLM
     The mapping was based on the approximate mapping function defined in Readability_functions.py """
    target_label = RS_user_label[1]
    flesch_ranges = {
        "Zeer makkelijk": (90, 1000),
        "Makkelijk": (80, 89),
        "Redelijk makkelijk": (70, 79),
        "Gemiddeld": (60, 69),
        "Redelijk moeilijk": (50, 59),
        "Moeilijk": (30, 49),
        "Zeer moeilijk": (0, 29),
    }
    
    low, high = flesch_ranges.get(target_label, (None, None))
    if low <= flesch < high:
        deviation = 0
        return deviation
    elif flesch < low:
        deviation = low - flesch
        return deviation
    else:
        deviation = flesch -high
        return deviation

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
directory = os.path.join(parent_dir, "Data")
folders = [f for f in os.listdir(directory) if f.isdigit()]

""" Loop over all transcripts """
for transcript in folders:
    print(transcript)
    file_path = os.path.join(directory, transcript)
    file_p = os.path.join("Cleaned outputs", var + "_" + q)
    
    with open(file_p, "r", encoding = "utf-8") as file:
        data = json.load(file)

    entries_transcript = [entry for entry in data if entry['transcript_id'] == int(transcript)]
    for entry in entries_transcript:
        transcript_id = entry["transcript_id"]
        turn = str(entry['turn_index'])
        model = entry['model']
        condition = entry['condition']
        checkpoint_key = (transcript_id, turn, model)
        
        # Extract the response of the model
        response = [entry['response']]
        text_model, tokens_model = preprocess(response)  
        # Get the readability measures of the user
        RS_user, RS_user_label = get_generated(file_path)
        # Run the readability info function
        readability_info(text_model, RS_user, RS_user_label)     
                
results_file.close()


