import re

"""Here the prompts for Reflection Generation are designed"""
def format_constraints(constraints):
    return '\n'.join([f"- {pos}: {', '.join(words)}" for pos, words in constraints.items()])

def format_dialoog(dialoog):
    dialoog = re.sub(r"Interviewee:", "Interviewee:", dialoog)
    
    return dialoog

def format_level(level):
    if len(level) > 1:
        return f""" Use a {level[0]} to {level[1]} language level."""
    else:
        return f""" Use a {level[0]} language level. """


def get_prompt_LA(dialoog, RS_info):
    return f"""You are a journalistic interviewer speaking with a Holocaust survivor.
You did not experience the Holocaust yourself and speak exclusively from the perspective of the interviewer, you are not the person concerned in the events discussed.

Task:
Generate a response from the interviewer (you) with a maximum of three sentences within the dialogue below with the interviewee summarising what has been said without asking a question.

Restrictions:
- {format_level(RS_info)}
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