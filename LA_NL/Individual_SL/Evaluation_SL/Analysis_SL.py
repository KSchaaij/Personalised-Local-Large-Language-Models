import csv
import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from functions import preprocess, get_sentence_length

"""" In this script we analyse the overlength per output 
(words exceeding the stored average sentence length used by the speaker)"""

""" Manually adjust for which model and task the results need to be processed"""
# var = "QG_output (raw) (raw) (raw) (raw)"
var = "RG_output (raw) (raw) (raw) (raw)"
print(var)  # Just a reminder and check
subset = "dev_"

q = "filtered_results_XXX.json"     # Adapt to model name
print(q)    # Just a reminder and check

"""A CSV file is created to store the results of the analysis"""
results_path = os.path.join("Analysis_results", subset + var + "_analysis_results.csv")
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
    "Model", "Transcript_nr", "Turn", "Condition", "SL_user", "SL_model", "SL_deviation", "SL_deviation_c"])


"""The relevant information from the speaker profile is obtained"""
def get_generated(filename):
    dir = os.path.join(filename, "Speaker_profiles")

    file_path = os.path.join(dir, "10_database.json")
    with open(file_path, 'r', encoding = "utf-8") as f:
        database = json.load(f)

    SL_user = database["sentence_length"]["avg sentence length"]

    return SL_user

"""Here the functions for sentence length is added (based on linguistic_features.py)"""
def sentence_info(model_output, SL_user):
    t1 = re.sub(r'\.{3,}(?=\W)', ' PAUSE', model_output)
    t2 = re.sub(r'…(?=\W)', ' PAUSE', t1)
    t3 = t2.replace("  ", " ") 
    
    sentences_m = re.split(r'(?<=[.!?])\s+|(?<=BREAK)\s+|(?<=\.)', t3)
    sentences_m = [s for s in sentences_m if s and s != "BREAK"]

    SL_model = round(get_sentence_length(sentences_m))

    """ We also store the direction of the deviation in order to get insights into the directional trend """
    """ Positive means that the model has a larger value and hence, did not follow the restriction """
    SL_deviation = SL_model - SL_user      
    if SL_deviation > 0:
        SL_deviation_c = SL_deviation
    else:
        SL_deviation_c = 0
    writer.writerow([
            model, transcript, turn, condition, SL_user, SL_model, SL_deviation, SL_deviation_c
        ])

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
directory = os.path.join(parent_dir, "Data")
folders = [f for f in os.listdir(directory) if f.isdigit()]

""" Loop over all transcripts """
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
        # Extract the response of the model
        response = [entry['response']]
        text_model, tokens_model = preprocess(response)  
        # Get the sentence length of the user
        SL_user = get_generated(file_path)
        # Run the function to store the sentence length info
        sentence_info(text_model, SL_user)   
            
results_file.close()


