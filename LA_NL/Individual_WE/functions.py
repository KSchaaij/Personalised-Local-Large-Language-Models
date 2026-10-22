import re
import spacy
from collections import Counter

nlp = spacy.load("nl_core_news_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000  

""" This script contains a number of functions (that might have been somewhat modified) from the get_linguistic_features file 
for easy incorporation/usage in other IM related scripts """ 

def is_hyphenated_word(token):
    return '-' in token.text and all(part.isalpha() for part in token.text.split('-'))

def preprocess(data):
    text_ = ""
    tokens_ = []
    
    for d in data:
        if d.lower().startswith("interviewer:"):
                d = d[len("Interviewer:"):].strip()
        t1 = d.replace("\n", "")
        t2 = re.sub(r'\.{3,}(?=\W)', ' PAUSE', t1)
        t3 = re.sub(r'…(?=\W)', ' PAUSE', t2)
        t4 = t3.replace("  ", " ")
                
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

def get_ngram(data, n):
    patterns = []
    for d in data: 
        doc = nlp(d) 
        tokens = []
        for i, token in enumerate(doc):
            if token.text == ',' and i > 0:
                tokens[-1] = tokens[-1] + token.text
            else:
                tokens.append(token.text)
        ngrams = zip(*[tokens[i:] for i in range(n)])  
        patterns.extend([' '.join(ngram) for ngram in ngrams])

    pattern_counter = Counter(patterns)  
    all_patterns = [pattern for pattern in pattern_counter]
    return all_patterns

def get_token_POS(doc):
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

def frequency_term_POS(tokens, x, target_pos = None):
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
