import json
import os

""" This script should be applied when the speaker profiles are created, 
to filter out subsets of ngrams stored in the common used ngrams """

def filter_ngrams(ngrams):
    result = []
    for n in ngrams:
        sub = False
        for other in ngrams:
            if n != other and n in other:
                sub = True
                break  
        if not sub:
            result.append(n)
    return result

directory = "Data_profile"
folders = [f for f in os.listdir(directory)]

for transcript in folders:
    print(transcript)
    path = os.path.join(directory, transcript)

    dir = os.path.join(directory, transcript)
    folder_d = os.path.join(dir, "Speaker_profiles")

    file_d = os.path.join(folder_d, str(10) + "_database.json")
    with open(file_d, "r", encoding = "utf-8") as file:
            database = json.load(file)
    ngrams = database["ngrams"]["common"]
    ngrams_new = filter_ngrams(ngrams)
    database['ngrams']["common"] = ngrams_new
    with open(file_d, "w", encoding="utf-8") as file:
        json.dump(database, file, ensure_ascii=False, indent=4)
