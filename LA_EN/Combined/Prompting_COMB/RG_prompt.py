import re

"""Here the prompts for the question generation are designed"""
def format_constraints(constraints):
    return '\n'.join([f"- {pos}: {', '.join(words)}" for pos, words in constraints.items()])

def format_level(level):
    if len(level) > 1:
        return f""" Use a {level[0]} to {level[1]} language level."""
    else:
        return f""" Use a {level[0]} language level. """
    
def format_dialoog(dialoog):
    dialoog = re.sub(r"Interviewee:", "Interviewee:", dialoog)
    
    return dialoog

def get_prompt_LA(dialoog, pos, ls, rs):
    return f"""You are a journalistic interviewer speaking with a Holocaust survivor.
You did not experience the Holocaust yourself and speak exclusively from the perspective of the interviewer, you are not the person concerned in the events discussed.

Task:
Generate a response from the interviewer (you) with a maximum of three sentences within the dialogue below with the interviewee summarising what has been said without asking a question.

Restrictions:
- Do not use more than {ls} words per sentence. 
- {format_level(rs)}
- Use as many words and expressions from the interviewee's vocabulary list as possible.  
- Use spoken language.
- Ensure grammatical correctness.
- Never ask a question.
- Address the interviewee in your response.  
- Do not use emojis, emoticons, or symbols such as 🙂, 🤓, etc.
- Respond from the perspective of the interviewer, not the interviewee.

Output format:
Interviewer: <your summarising response with a maximum of three sentences without questions>

Dialogue:
{format_dialoog(dialoog)}

Wordlist of the interviewee:
{format_constraints(pos)}
"""


def get_prompt_NA(dialoog):
    return f"""You are a journalistic interviewer speaking with a Holocaust survivor.
You did not experience the Holocaust yourself and speak exclusively from the perspective of the interviewer, you are not the person concerned in the events discussed.

Task:
Generate a response from the interviewer (you) with a maximum of three sentences within the dialogue below with the interviewee summarising what has been said without asking a question.

Restrictions:
- Use spoken language.
- Ensure grammatical correctness.
- Never ask a question.
- Address the interviewee in your response.  
- Do not use emojis, emoticons, or symbols such as 🙂, 🤓, etc.
- Respond from the perspective of the interviewer, not the interviewee.

Output format:
Interviewer: <your summarising response with a maximum of three sentences without questions>

Dialogue:
{format_dialoog(dialoog)}
"""