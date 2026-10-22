import json
import os
import re
import spacy
from collections import Counter

""" This script is the main script used to obtain the linguistic features in our study:
words and expressions, language level, and sentence length"""

nlp = spacy.load("nl_core_news_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000  
from Readibility_functions import flesch_douma_score,get_sentences_readibility,LIX_score,map_scores_Flesch,map_LIX

def is_hyphenated_word(token):
    return '-' in token.text and all(part.isalpha() for part in token.text.split('-'))

def preprocess(file_path, timeframe):
    """
    This function takes two arguments, one for the file and one for the amount of timeframes, 
    and returns the corresponding text and tokens.
    """
    with open(file_path, "r", encoding = "utf-8") as file:
          data = json.load(file)
    
    # Get the first integer items from the dictionary list
    # e.g., 2 means the first two timesplits (so 10 minutes of speech)
    print(int(timeframe))
    integer = int(10/5 )
    texts = list(data.values())[:integer]

    text_ = ""
    tokens_ = []

    for text in texts:    
        t1 = text.replace("\n", "")          
        t2 = re.sub(r'\.{3,}(?=\W)', ' PAUSE', t1)
        t3 = re.sub(r'…(?=\W)', ' PAUSE', t2)
        t4 = t3.replace("  ", " ") #.replace(" .", ".")
                
        t5 = re.sub(r'-\s+(?=[A-Z0-9])', ' BREAK ', t4) 
        t6 = re.sub(r'-\s+(?=[a-z0-9])', ' BREAK ', t5)
        t7 = re.sub(r'(\w+)-$', r'\1 BREAK ', t6.strip())

        text_ += t7
        doc = nlp(t7)
        tokens = [token.text.lower() for token in doc 
                  if (token.is_alpha or token.text == ',' or is_hyphenated_word(token)) 
                  and token.text not in {"PAUSE", "BREAK"}]
        tokens_.extend(tokens)
    return text_, tokens_

def get_token_POS(doc):
    """
    This function takes one argument and returns the POS category per item
    """
    pos = []
    for token in doc:
        if token.text in {".", "!", "?"}: 
            continue
        elif token.text == "PAUSE":
            pos.append("PAUSE")
        elif token.text == "BREAK":
            pos.append("BREAK")
        elif token.pos_ in {"NOUN", "PROPN"}:
            pos.append("NOUN")
        elif token.pos_ in {"CONJ", "SCONJ", "CCONJ"}:
            pos.append("CONJ")
        elif token.pos_ in {"VERB", "AUX"}:
            pos.append("VERB")
        elif token.pos_ == "INTJ" or token.text.lower() == "eh" or token.text.lower() == "ehm":            
            pos.append("INTJ")
        else:
            pos.append(token.pos_)
    
    return pos

def sentence_POS(text):
    """
    This function takes one argument and returns its dictionary with the sentence and its corresponding POS structure
    """
    sentences = re.split(r'(?<=[.!?])\s+|(?<=BREAK)\s+|(?<=\.)', text)
    pos_dict = {}
    for s in sentences:
        if s == "":
            continue
        doc = nlp(s)
        pos = get_token_POS(doc)
        s = s.strip(".!?")
        if s in pos_dict:
            pos_dict[s].append(pos)
        else:
            pos_dict[s] = [pos] 
    return pos_dict

def get_sentences_from_dict(pos_dict):
    """
    Returns all sentences from a POS dictionary, including duplicates.
    """
    all_sentences = []
    for sentence, pos_list in pos_dict.items():
        all_sentences.extend([sentence] * len(pos_list))
    return all_sentences

def get_sentence_length(sentences):
    """
    This function takes one argument and returns the avg sentence length
    """
    s_length = []  
    for s in sentences:
        doc = nlp(s)
        count = sum(1 for token in doc if not token.is_punct and token.text != "PAUSE" and token.text != "BREAK")
        s_length.append(count)
    mean = sum(s_length) / len(s_length)
    return mean


def get_ngram(data, n, x):
    """
    This function returns the amount of identical ngrams in the provided data (sentences) where n is specified as argument
    """
    patterns = []
    for d in data: 
        doc = nlp(d) 
        tokens = []
        for i, token in enumerate(doc):
            if (token.text == ',' or token.text == '.') and i > 0:
                tokens[-1] = tokens[-1] + token.text
            else:
                tokens.append(token.text)
        ngrams = zip(*[tokens[i:] for i in range(n)])  
        patterns.extend([' '.join(ngram) for ngram in ngrams])

    pattern_counter = Counter(patterns)  
    all_patterns = [pattern for pattern in pattern_counter]
    threshold = 3   # Threshold measure
    top_patterns = [pattern for pattern, count in pattern_counter.most_common(x) if count > threshold]  
    return top_patterns, all_patterns


def frequency_term_POS(tokens, x, target_pos = None):
    """
    This function returns the terms per POS category, 
    the frequency of the categories (based on the amount of terms present), 
    and the most common x (param) terms per category

    """
    pos_dict = {}
    doc = nlp(" ".join(tokens))  
    pos_ = get_token_POS(list(doc))  

    for i, t in enumerate(tokens):
        tag = pos_[i]
        if tag in {"PAUSE", "BREAK"}:
            continue
        if target_pos and tag not in target_pos:
            continue
        pos_dict.setdefault(tag, []).append(t)
    total_counts = {pos: len(terms) for pos, terms in pos_dict.items()}
    sorted_counts = sorted(total_counts.items(), key=lambda x: x[1], reverse=True)
    threshold = 5   # threshold measure for frequency of repetition
    common_terms = {
        pos: [term for term, count in Counter(terms).most_common(x) if count > threshold]
        for pos, terms in pos_dict.items()
}    
    return pos_dict, sorted_counts, common_terms


"""Loop"""
directory = "Data"
for transcript in os.listdir(directory):
    print(f"Processing: {transcript}")
    ID = transcript.strip()  
    database = {}
    database["ID"] = {
        "transcript number": ID
    }

    # Get the file of transcripts splits for this ID
    dir = os.path.join("Data", ID)
    file_path = os.path.join(dir, "splits" + '.json')

    # Preprocess the transcribed data, not that the integer here represents the used timeframes
    text, tokens = preprocess(file_path, "10")    

    # Here, the speaker-specific features are extracted and stored in the speaker profile
    pos_structure = sentence_POS(text)
    sentences = get_sentences_from_dict(pos_structure)
                                                
    POS_terms_1, _, POS_common_1 = frequency_term_POS(tokens,5, target_pos=["CONJ", "ADJ"])  
    POS_terms_2, _, POS_common_2 = frequency_term_POS(tokens, 10, target_pos=["PRON","NOUN", "VERB", "ADV"])   
    POS_terms = {**POS_terms_1, **POS_terms_2}
    POS_common = {**POS_common_1, **POS_common_2}                                                                     
    
    for pos in POS_terms:
        database[pos] = {
            "terms": list(set(POS_terms[pos])),  
            "common": POS_common.get(pos, [])
        }

    n_values = [2,3,4,5]
    ngrams_common = []
    ngrams_all = []
    for n in n_values:
        ngrams, all_ngrams = get_ngram(sentences, int(n), 3)    
        ngrams_common.extend(ngrams)
        ngrams_all.extend(all_ngrams)
    database["ngrams"] = {
        "ngrams_all": ngrams_all,
        "common": ngrams_common
    }

    # Here, the mean sentence length of the speaker is retrieved and stored in the speaker profile
    mean = get_sentence_length(sentences)
    database["sentence_length"] = {
        "avg sentence length": round(mean),
    }

    # Here, the language level approximations are obtained and stored in the speaker profile
    sentences = get_sentences_readibility(sentences)
    flesch = flesch_douma_score(sentences)
    flesch_interpretation = map_scores_Flesch(flesch)

    lix = LIX_score(sentences)
    lix_interpretation_ = map_LIX(lix)

    database["language_level"] = {
        "LIX score": lix_interpretation_,
        "Flesch score": flesch_interpretation,
        "LIX raw": lix,
        "Flesch raw": flesch
    }

    # Finally the database is created as a JSON file
    q = os.path.join(dir, "Speaker_profiles")
    os.makedirs(q, exist_ok=True) 
    p = os.path.join(q, str(10) + "_database" + '.json')
    with open(p, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
