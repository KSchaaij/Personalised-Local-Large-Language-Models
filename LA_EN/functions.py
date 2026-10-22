import contractions
import re
import spacy
from collections import Counter

nlp = spacy.load("en_core_web_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000

""" This script contains a number of functions (that might have been somewhat modified) from the get_linguistic_features file 
for easy incorporation/usage in other scripts """ 

def full(t):
    expanded_words = []    
    for word in t.split():
        expanded_words.append(contractions.fix(word))   
        expanded_text = ' '.join(expanded_words)

    return expanded_text

def is_hyphenated_word(token):
    return '-' in token.text and all(part.isalpha() for part in token.text.split('-'))


def preprocess(data):
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


def get_sentence_length(sentences):
    s_length = []  
    for s in sentences:
        doc = nlp(s)
        count = sum(
            1 for token in doc 
            if not token.is_punct 
            and token.text != "PAUSE" 
            and token.text != "BREAK" 
            and token.text != "INDISTINCT"
            and token.text != "INTERVIEWER")
        s_length.append(count)
    mean = sum(s_length) / len(s_length)
    return mean

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
    

def frequency_term_POS(tokens, x, target_pos = None):
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
