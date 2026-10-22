import re
import spacy
import textstat

""" This script contains the readability score functions for English """

def get_ARI(text):
    ari = textstat.automated_readability_index(text)
    return ari
    
def map_ARI(score):
    """ A mapping function to obtain the approximate ARI level of the speaker
     The labels were adapted to match the ones from Flesch below """
    if score <= 6:
        return "Very easy"
    elif score <= 7:
        return "Easy"
    elif score <= 8:
        return "Fairly easy"
    elif score <= 10:
        return "Standard"
    elif score <= 13:
        return "Fairly difficult"
    elif score <= 14:
        return "Difficult"
    else:
        return "Very difficult"

def get_Flesch(text):
    flesch = textstat.flesch_reading_ease(text)
    return flesch

def map_scores_Flesch(score):
    """ A mapping function to determine the approximate Flesch Reading score of the speaker """
    if score >= 90:
        return "Very easy"
    elif score >= 80:
        return "Easy"
    elif score >= 70:
        return "Fairly easy"
    elif score >= 60:
        return "Standard"
    elif score >= 50:
        return "Fairly difficult"
    elif score >= 30:
        return "Difficult"
    else:
        return "Very difficult"

def get_text_readibility(sentences):
    """ This function removes typical speech patterns from the sentences 
    to better fit the reading score functions based on the used transripts"""
    sent = []
    for s in sentences:
        s = re.sub(r'\b(eh|ehm)\b', '', s, flags=re.IGNORECASE)
        # Remove uhm / umm / hmm with 2+ m's
        s = re.sub(r'\b(u|h)m{2,}\b', '', s, flags=re.IGNORECASE)

        # Clean extra spaces
        s = re.sub(r'\s+', ' ', s).strip()
        s = re.sub(r"\s*\bPAUSE\b\s*", " ", s)
        s = re.sub(r"\s*\bBREAK\b\s*", " ", s)
        s = re.sub(r"\s*\bINDISTINCT\b\s*", " ", s)
    
        s = s.strip()
        if s:
            sent.append(s)
            
    return ". ".join(sent)


