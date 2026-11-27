import json
import os

""" This script should be applied when the speaker profiles are created, 
to filter out subsets of ngrams stored in the common used ngrams """

## Filter out subsets of ngrams
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

## Obtain the database per transcript
directory = "Data"
folders = [f for f in os.listdir(directory) if f.isdigit()]

timeframes = [10]  

## Loop over all the transcripts
for transcript in folders:
    print(transcript)
    path = os.path.join(directory, transcript)

    # Get the file of the database for the current transcript and timeframe
    dir = os.path.join(directory, transcript)
    folder_d = os.path.join(dir, "Speaker_profile")
    for timeframe in timeframes:
        file_d = os.path.join(folder_d, str(timeframe) + "_database.json")
        with open(file_d, "r", encoding = "utf-8") as file:
                database = json.load(file)
        ngrams = database["ngrams"]["common"]
        ngrams_new = filter_ngrams(ngrams)
        database['ngrams']["common"] = ngrams_new
        with open(file_d, "w", encoding="utf-8") as file:
            json.dump(database, file, ensure_ascii=False, indent=4)
