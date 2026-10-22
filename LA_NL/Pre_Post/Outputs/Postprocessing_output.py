import json
import os
import re

subset = "dev_"

""" This script is to apply our rule-based postprocessing method described in the paper 
In the Overview.xlsx more information about the amount of rejected outputs can be found.
Note that matching on removed/filtered outputs was done after this."""

""" Manually adjust for which model and task the results need to be processed"""
results = "results_XXX.json"        # Adapt to model name

# """ Question generation variables """
# task = "QG"
# nr = 70    
""" Reflection generation varianles """
nr = 150   
task = "RG"



path = os.path.join(task + "_output", subset + results)
with open(path, "r", encoding = "utf-8") as file:
        data = json.load(file)

def check_output(response, nr, bool, counter):
    bool = False
    output = response.strip()
    # Empty output --> This was inserted to remove the outputs that took longer than a minute to get generated. 
    # Note that you can uncomment this in case you want to also apply this strategy.
    # if output == "":
    #     print("Empty", output)
    #     bool = True        
    # Chinese characters
    if re.search(r'[\u4e00-\u9fff]', output):
        bool = True
    # Must not start with 'interviewee:' or 'veteran':
    if output.lower().startswith('interviewee:') or output.lower().startswith('veteraan:'):
        bool = True  
    # Speaker tags
    tags = re.findall(r'(?i)(interviewer|interviewee|veteraan|veteran):', output)
    if len(tags) > 1:
        bool = True
    # Information in front of the answer
    if re.search(r'.+\binterviewer:', output, re.IGNORECASE):
        bool = True
    # Potential excessive information
    if "Let op" in output or "Let wel" in output or "Opmerking:" in output:
        bool = True
    if re.search(r'\n\n', output):
        bool = True
    # Excessive length check
    text = re.sub(r'(?i)^interviewer:\s*', '', output).strip()
    sentences = re.split(r'[.!?]', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    total_words = len(text.split())
    if total_words > nr:
        bool = True
    # Parentheses with more than 2 words inside
    if re.search(r'\((?:\s*\S+\s+){2,}\S+\s*\)', output.lower()) and not bool:
        bool = True
    if bool == True:
        counter += 1
    return counter, bool

filtered_output = []
rejected_output = []

bool = False
counter = 0
entries_transcript = [entry for entry in data]
for entry in entries_transcript:
    transcript_id = entry["transcript_id"]
    turn = str(entry['turn_index'])
    model = entry['model']
    condition = entry['condition']
    prompt = entry['prompt']
    response_text = entry['response'].strip()
    
    counter, bool = check_output(response_text, nr, bool, counter)
    if bool:
        rejected_output.append(entry)
    else:
        filtered_output.append(entry)
print("Counter: ",counter)


# Store filtered output
save_filtered = os.path.join(task + "_output", subset + f"filtered_{results}")
with open(save_filtered, "w", encoding="utf-8") as f_out:
    json.dump(filtered_output, f_out, indent=2, ensure_ascii=False)

# Store rejected output
save_rejected = os.path.join(task + "_output", subset + f"rejected_{results}")
with open(save_rejected, "w", encoding="utf-8") as f_out:
    json.dump(rejected_output, f_out, indent=2, ensure_ascii=False)
