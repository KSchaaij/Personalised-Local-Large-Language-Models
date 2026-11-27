import os
import re
from docx import Document

""" This script allows the extraction of interview snippets used for the prompts """

def main_function(path):
    """ Note that for our current study, we have chosen to inlcude 5 turns """
    doc = Document(path)   
    text = []
    multiple_speakers = False

    # Call function to extract metadata from the interview and save this in the overall csv file
    ID, respondent, interviewer = get_meta(doc)

    # Get all the text from the document
    for para in doc.paragraphs:
        if para.text.strip():  # skip empty lines
            text.append(para.text.strip())
    
    skip_labels = ["Z", "Y2", "Y3"]
    for label in skip_labels:
        if (
        any(re.match(rf"^{re.escape(label)}:", line) for line in text)
        ):
            multiple_speakers = True
            
    # Remove time markers like (0:02:35) (0:02:35). and 0:20 - 0:30
    text_ = []
    for i in text:
        t = re.sub(r"\(\d{1,2}:\d{2}:\d{2}\)|\d{1,2}:\d{2} - \d{1,2}:\d{2}", "", i)
        t = re.sub("\n", " ", t)   
        t = re.sub("  ", " ", t)   
        text_.append(t)

    transcript_after_10 = get_after_10min(text_)
    prompts, short, count = prompt_construct(transcript_after_10, 5, interviewer, respondent)

    # Create the directory
    directory = os.path.join("Turns_prompt", ID)
    os.makedirs(directory, exist_ok=True)  
    
    # Store the overview of transcript
    store_path = os.path.join(directory, "overview_prompts" + '.txt')
    with open(store_path, 'w', encoding='utf-8') as f:
        for item in prompts:
            f.write(item)
            f.write('\n-- Prompt --\n') 
    
    return multiple_speakers, short, (ID,len(prompts)), count
    


def get_after_10min(lines):
    time_pattern = re.compile(r'\[(\d+)\s*min\.?\]')
    speaker_pattern = re.compile(r'^([A-Za-z0-9]+:)\s*(.*)')
    text = []
    after_10 = False
    for line in lines:
        match = time_pattern.search(line)
        if match:
            time = int(match.group(1))
            if time >= 10 and not after_10:
                after_10 = True
                continue  
        if after_10:
            line = time_pattern.sub("", line).strip()
            if speaker_pattern.match(line):
                text.append(line)
            else:
                if text:
                    text[-1] += " " + line
                else:
                    text.append(line)  
    return text

def length(sentence):
    a = re.sub(r'^\w+:', '', sentence).strip()
    words = a.split()
    return len(words)

def prompt_construct(text, window_size, interviewer, respondent):
    """ Note that we have chosen to limit the minimum length to <=3 and maximum to >75 """
    skip_labels = ["Z", "Y2", "Y3"]
    prompts = []
    total_turns = len(text)
    short = []
    count = 0

    for i in range(total_turns - window_size):
        if re.match(rf"({respondent}|Y1):", text[i]):
            t = text[i : i+window_size]
            ign = False
            for j in t:
                if length(j) <= 3:
                    ign = True
                    short.append(j)
                    break
                if length(j) > 75:
                    ign = True
                    break
            for label in skip_labels:
                if (
                any(re.match(rf"^{re.escape(label)}:", line) for line in t)
                ):
                    ign = True
                    count += 1
            if ign:
                continue 
            if (
                any(re.match(rf"^{re.escape(interviewer)}:", line) for line in t)
                ):
                prompt = "\n".join(t)
                prompts.append(prompt)
    
    return prompts, short, count


def get_meta(doc):
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                if "is de respondent" in cell.text:
                    a = cell.text
                    respondent = a.replace(" is de respondent", "")
                if "is de interviewer" in cell.text:
                    b = cell.text
                    interviewer = b.replace(" is de interviewer", "")
                if ".mp3" in cell.text.lower() and "_" in cell.text:
                    s = cell.text.replace(".mp3", "").replace(".MP3", "")
                    ID = s.split("_")[0]
    return ID, respondent, interviewer
    
directory = "Transcripties"
speaker_info = []
len_prompts =[]
count_add_speaker = []

for filename in os.listdir(directory):
    print(filename)
    file_path = os.path.join(directory, filename)
    x, short, len_p, count = main_function(file_path)
    
    speaker_info.append((filename,x))
    count_add_speaker.append((filename, count))
    len_prompts.append(len_p)

print(sorted(len_prompts, key=lambda x: x[1], reverse=True))


