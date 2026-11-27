from collections import Counter
import re
import spacy

nlp = spacy.load("nl_core_news_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000  # Or however large the input is

""" This script contains a number of functions (that might have been somewhat modified) from the get_lexical_features file 
for easy incorporation/usage in RS scripts """


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
    # print(tokens_)
    # print(text_)
    return text_, tokens_


def get_sentence_length(sentences):
    s_length = []
    for s in sentences:
        doc = nlp(s)
        count = sum(1 for token in doc if not token.is_punct and token.text != "PAUSE" and token.text != "BREAK")
        s_length.append(count)
    mean = sum(s_length) / len(s_length)

    return mean
