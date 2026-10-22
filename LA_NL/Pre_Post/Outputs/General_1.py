import csv
import emoji
import json
import os
import re
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from functions import preprocess

""" This script is used to obtain some additional information about the generation behaviour of the models,
including emoji usage and number of sentences
In the Overview.xlsx more information about the amount of emojis en nr of sentences can be found."""


""" Manually adjust for which model and task the resuls need to be processed"""
var = "QG_output (raw) (raw) (raw) (raw)"
# var = "RG_output (raw) (raw) (raw) (raw)"
print(var)  # Just a reminder and check
subset = "dev_"
# q = "filtered_results_GPT_Oss.json"              #DONE QG RG
# q = 'filtered_results_Falcon.json'               #DONE QG RG
# q = 'filtered_results_Qwen2.5_7B.json'           #DONE QG RG
# q = 'filtered_results_Qwen2.5_14B.json'          #DONE QG RG
# q = 'filtered_results_mistral_small.json'        #DONE QG RG
# q = "filtered_results_GPT.json"                  #DONE QG RG
# q = "filtered_results_Mistral.json"              #DONE QG RG
# q = "filtered_results_Geitje.json"               #DONE QG RG
q = 'filtered_results_Apertus.json'              #DONE RG QG
print(q)    # Just a reminder and check

"""A CSV file is created to store the results of the analysis"""
results_path = os.path.join("General_analysis_results", subset + var + "General_analysis_results.csv")
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
    "Model", "Transcript_nr", "Turn", "Condition", "Nr_of_sentences", "Emoji_usage"])

def information(model_output):
    Emoji = False

    for char in model_output:
        if char in emoji.EMOJI_DATA:
            Emoji = True

    t1 = re.sub(r'\.{3,}(?=\W)', ' PAUSE', model_output)
    t2 = re.sub(r'…(?=\W)', ' PAUSE', t1)
    t3 = t2.replace("  ", " ") #.replace(" .", ".")
    
    sentences_m = re.split(r'(?<=[.!?])\s+|(?<=BREAK)\s+|(?<=\.)', t3)
    sentences_m = [s for s in sentences_m if s and s != "BREAK"]
    nr_sentences = len(sentences_m)

    writer.writerow([
            model, transcript, turn, condition,nr_sentences, Emoji])

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
        
        # Extract the response of the model
        response = [entry['response']]
        text_model, tokens_model = preprocess(response)  
        # Run the function to store the additional information
        information(text_model)            
results_file.close()


