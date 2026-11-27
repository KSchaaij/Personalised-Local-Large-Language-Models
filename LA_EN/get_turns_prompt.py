import contractions
import json
import os
import re
import spacy

""" This script allows the extraction of interview snippets used for the prompts """

def is_hyphenated_word(token):
    return '-' in token.text and all(part.isalpha() for part in token.text.split('-'))

def full(t):
    expanded_words = []    
    for word in t.split():
        expanded_words.append(contractions.fix(word))   
        expanded_text = ' '.join(expanded_words)

    return expanded_text

def preprocess(data):
    """ Copied and adjusted from get_linguistic_features """
    text = []

    for utt in data:
        utt = full(utt)
        utt = utt.replace("&", "and")
        utt = re.sub(r"\.{3,}", " ... ", utt)
        utt = re.sub(r"\.(?=[,?!])", "", utt)  
        utt = re.sub(r"([?!]),", r"\1", utt)   
        utt = re.sub(r'\s{2,}', ' ', utt).strip()
        if not utt.strip() or utt.strip() in {".", ",", "...", "…", "***"}:
            continue
        text.append(utt)
    return text

def split_transcript(text):   
    splits = re.split(r'(?=(?:Interviewer:|Interviewee:))', text)
    lines = [p.strip() for p in splits if p.strip()]
    return lines


def main_function(lines):
    """ Note that for our current study, we have chosen to inlcude 4 turns """
    prompts = prompt_construct(lines, 4)
    directory = os.path.join("Turns_prompt_test", ID)
    os.makedirs(directory, exist_ok=True)  
    
    store_path = os.path.join(directory, "overview_prompts" + '.txt')
    with open(store_path, 'w', encoding='utf-8') as f:
        for item in prompts:
            f.write(item)
            f.write('\n-- Prompt --\n') 
    
    return (ID,len(prompts))
    

def length(sentence):
    a = re.sub(r'^\w+:', '', sentence).strip()
    words = a.split()
    return len(words)

def prompt_construct(text, window_size):
    """ Note that we have chosen to limit the minimum length to <=4 and maximum to >90 """
    prompts = []
    total_turns = len(text)

    for i in range(total_turns - window_size):
        if re.match(r"Interviewee", text[i + window_size - 1]):
            t = text[i : i + window_size]
            ign = False
            for j in t:
                if length(j) <= 4:
                    ign = True
                    break
                if length(j) > 90:
                    ign = True
                    break
            if ign:
                continue 
            if (
                any(re.match(rf"^{re.escape("Interviewer")}:", line) for line in t)
                ):
                prompt = "\n".join(t)
                prompts.append(prompt)
    
    return prompts

directory = "Data_dialogue"
len_prompts =[]

for transcript in os.listdir(directory):
    print(f"Processing: {transcript}")
    ID = transcript.strip()  
    database = {}
    database["ID"] = {"transcript number": ID}
    dir = os.path.join(directory, ID)
    file_path = os.path.join(dir, ID + '.json')
    with open(file_path, "r", encoding = "utf-8") as file:
        data = json.load(file)
    text = " ".join(data["text"].split())  # extract ONCE
    lines = split_transcript(text)
    cleaned_lines = preprocess(lines) 
    len_p = main_function(cleaned_lines)

    len_prompts.append(len_p)

print(sorted(len_prompts, key=lambda x: x[1], reverse=True))

