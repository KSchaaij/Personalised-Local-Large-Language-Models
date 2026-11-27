import re
import spacy

nlp = spacy.load("nl_core_news_lg", disable=["ner", "parser"])
nlp.max_length = 4_000_000  


""" This script contains the readability score functions for Dutch"""

def LIX_score(sentences):
    words = []
    sentence_count = len(sentences)

    if len(sentences) == 0:
        sentence_count = 1 

    for sentence in sentences:
        tokens = [w for w in re.findall(r'\b\w+\b', sentence) if w.isalpha()]
        words.extend(tokens)

    long_words = sum(1 for word in words if len(word) > 6)
    lix = (len(words) / sentence_count) + ((long_words * 100) / len(words))
    return lix

def map_LIX(score):
    """ A mapping function to obtain the approximate LIX level of the speaker """
    if score < 20:
        return "Zeer makkelijk"
    elif score < 30:
        return "Makkelijk"
    elif score < 40:
        return "Redelijk moeilijk"
    elif score < 50:
        return "Moeilijk"
    else:
        return "Zeer moeilijk"

def count_syllables(word):
    """ Rough syllable counter for Dutch"""
    word = word.lower()
    word = re.sub(r'[^a-záéíóúàèìòùäëïöüÿ]', '', word) 
    vowels = "aeiouyáéíóúàèìòùäëïöüÿ"
    syllable_count = 0
    prevowel = False
    
    for char in word:
        if char in vowels:
            if not prevowel:
                syllable_count += 1
            prevowel = True
        else:
            prevowel = False
    return max(1, syllable_count)

def flesch_douma_score(sentences):
    words = []
    for sentence in sentences:
        tokens = [w for w in re.findall(r'\b\w+\b', sentence) if w.isalpha()]
        words.extend(tokens)
    if not words or not sentences:
        return None
    asl = len(words) / len(sentences)  
    total_syllables = sum(count_syllables(w) for w in words)
    asw = total_syllables / len(words) 
    score = 206.835 - (0.93 * asl) - (77 * asw)
    return round(score, 2)

def map_scores_Flesch(score):
    """ A mapping function to obtain the approximate Flesch-Douma level of the speaker """
    if score >= 90:
        return "Zeer makkelijk"
    elif score >= 80:
        return "Makkelijk"
    elif score >= 70:
        return "Redelijk makkelijk"
    elif score >= 60:
        return "Gemiddeld"
    elif score >= 50:
        return "Redelijk moeilijk"
    elif score >= 30:
        return "Moeilijk"
    else:
        return "Zeer moeilijk"

def get_sentences_readibility(sentences):
    """ This function removes typical speech patterns from the sentences 
    to better fit the reading score functions based on the used transcripts"""
    sent = []
    for sentence in sentences:
        # Remove fillers like "eh" or "ehm"
        s = re.sub(r"\b ehm?\b", "", sentence)     
        s = re.sub(r"\s*\bPAUSE\b\s*", " ", s)
        s = re.sub(r"\s*\bBREAK\b\s*", ".", s)

        s = re.sub(r"\.+", ".", s)
        s = re.sub(r",\.", ".", s)

        sent.append(s)
    return sent
