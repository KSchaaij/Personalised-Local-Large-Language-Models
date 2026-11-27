import contractions
import json
import os
import re
import spacy
from collections import Counter

""" This script is the main script used to obtain the linguistic features in our study:
words and expressions, language level, and sentence length"""

nlp = spacy.load("en_core_web_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000 
from Readability_functions import get_text_readibility,get_Flesch,get_ARI,map_scores_Flesch,map_ARI

def is_hyphenated_word(token):
    return '-' in token.text and all(part.isalpha() for part in token.text.split('-'))

def full(t):
    expanded_words = []    
    for word in t.split():
        expanded_words.append(contractions.fix(word))   
        expanded_text = ' '.join(expanded_words)

    return expanded_text

def preprocess(file_path):
    """
    This function takes one argument, the file,
    and returns the corresponding text and tokens with easy recognisable spontaneous speech markers.
    """
    with open(file_path, "r", encoding = "utf-8") as file:
          data = json.load(file)
    
    text_ = ""
    tokens_ = []

    for utt in data:
        utt = full(utt)
        utt = utt.replace("...", " PAUSE ")
        utt = utt.replace("***", " INDISTINCT ")
        utt = utt.replace("—", " BREAK ")
        utt = utt.replace("&", "and")
        utt = utt.replace(".”", "”.")
        utt = utt.replace(",”", "”,")
        utt = utt.replace("..", ".")
        utt = utt.replace(".,", ".")
        utt = utt.replace(",.", ".")
        utt = utt.replace("?.", "?")
        utt = utt.replace("!.", "!")
        utt = re.sub(r'\s{2,}', ' ', utt).strip()
        text_ += " " + utt

        doc = nlp(utt)
        tokens = [token.text.lower() for token in doc
                  if (token.is_alpha or token.text == ',' or is_hyphenated_word(token)) 
                  and token.text not in {"PAUSE", "BREAK", "INDISTINCT"}]
        tokens_.extend(tokens)

    return text_, tokens_

def get_token_POS(doc):
    """
    This function takes one argument and returns the POS category per item
    """
    FILLER_RE = re.compile(
    r'^(ehm?|u?h?m{2,})$',
    re.IGNORECASE
    )
    
    pos = []
    for token in doc:
        if token.text in {".", "!", "?", "“", "”"}: 
            continue
        elif token.text == "PAUSE":
            pos.append("PAUSE")
        elif token.text == "BREAK":
            pos.append("BREAK")
        elif token.text == "INDISTINCT":
            pos.append("INDISTINCT")
        elif token.pos_ in {"NOUN", "PROPN"}:
            pos.append("NOUN")
        elif token.pos_ in {"CONJ", "SCONJ", "CCONJ"}:
            pos.append("CONJ")
        elif token.pos_ in {"VERB", "AUX"}:
            pos.append("VERB")
        elif token.pos_ == "INTJ" or FILLER_RE.match(token.text.lower()):            
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
    Returns all sentences from a POS dictionary.
    """
    all_sentences = []
    for sentence, pos_list in pos_dict.items():
        all_sentences.extend([sentence] * len(pos_list))
    return all_sentences

def get_sentence_length(sentences):
    """
    This function takes one argument and returns the avg sentence length, where spontaneous speech markers are not counted
    """
    s_length = []  
    for s in sentences:
        doc = nlp(s)
        count = sum(1 for token in doc if not token.is_punct and token.text != "PAUSE" and token.text != "BREAK" and token.text != "INDISTINCT")
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
        if tag in {"PAUSE", "BREAK", "INDISTINCT"}:
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


directory = "Data_profile"                 
for transcript in os.listdir(directory):
    print(f"Processing: {transcript}")
    ID = transcript.strip()  
    database = {}
    database["ID"] = {
        "transcript number": ID
    }

    # Get the file of transcripts splits for this ID
    dir = os.path.join(directory, ID)
    file_path = os.path.join(dir, "transcript_overview" + '.json')
    text, tokens = preprocess(file_path)   

    # Here, common words and expressions are extracted and stored in the lexical profile (stored in the speaker profile)
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
    database["sentence_info"] = {
        "avg sentence length": round(mean),
        }
    print(mean)

    # Here, the language level approximations are obtained and stored in the speaker profile
    text = get_text_readibility(sentences)
    flesch = get_Flesch(text)
    flesch_interpretation = map_scores_Flesch(flesch)

    ari = get_ARI(text)
    ari_interpretation_ = map_ARI(ari)

    database["language_use"] = {
        "ARI score": ari_interpretation_,
        "Flesch score": flesch_interpretation,
        "ARI raw": ari,
        "Flesch raw": flesch
    }

    # Finally the database is created as a JSON file
    q = os.path.join(dir, "Speaker_profiles")
    os.makedirs(q, exist_ok=True) 
    p = os.path.join(q, str(10) + "_database" + '.json')
    with open(p, "w", encoding="utf-8") as f:
        json.dump(database, f, ensure_ascii=False, indent=4)
