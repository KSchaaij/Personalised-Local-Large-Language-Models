import json
import os
import re
import spacy

nlp = spacy.load("en_core_web_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000  

""" This script serves as preprocessing step of the interview transcripts of the CORHOH corpus
Note that this script was used in addition to manual checks and replacements at the time so only provides a rough idea of preprocessing."""
   
def roles(transcript, speakers): 
    interviewee = None
    new_lines = []

    for i, line in enumerate(transcript):
        for speaker in speakers:
            if i + 1 < len(transcript):
                if "Interview" in line and speaker.lower() in line.lower():
                    interviewee = speaker
                    new_lines.append("")
                    break  
        else:
            new_lines.append(line)
    return new_lines, interviewee


def extract_interviewee_segments(transcript):
    transcript = data["text"]

    pattern = re.compile(r'(?is)Interviewee:\s*(.*?)(?=\s*(?:Interviewer:|Interviewee:|$))')
    segments = [m.group(1).strip() for m in pattern.finditer(transcript)]
    return [seg for seg in segments if seg] 

parent_dir = "../../Data/Data_dialogue"  # Adjust to correct directory manually
for folder_name in os.listdir(parent_dir):
    folder_path = os.path.join(parent_dir, folder_name)
    if os.path.isdir(folder_path):
        print(f"\nTranscript number: {folder_name}")
        for filename in os.listdir(folder_path):
            speaker_utt = []
            if filename.lower().endswith(".json"):
                file_path = os.path.join(folder_path, filename)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                data["text"] = " ".join(data["text"].split())
                interviewee_parts = extract_interviewee_segments(data)
                
                dir = os.path.join(parent_dir, folder_name)
                store_dir = os.path.join(dir, "transcript_overview" + '.json')
                with open(store_dir, "w", encoding="utf-8") as f:
                    json.dump(interviewee_parts, f, ensure_ascii=False, indent = 4)



