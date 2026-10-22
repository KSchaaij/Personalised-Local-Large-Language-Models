import re

""" Here the prompts for Reflection Generation are designed """
def format_constraints(constraints):
    return '\n'.join([f"- {pos}: {', '.join(words)}" for pos, words in constraints.items()])

def format_dialoog(dialoog):
    dialoog = re.sub(r"Interviewee:", "Interviewee:", dialoog)
    
    return dialoog

def get_prompt_LA(dialoog, SL_info):
    return f"""You are a journalistic interviewer speaking with a Holocaust survivor.
You did not experience the Holocaust yourself and speak exclusively from the perspective of the interviewer, you are not the person concerned in the events discussed.

Task:
Generate a response from the interviewer (you) with a maximum of three sentences within the dialogue below with the interviewee summarising what has been said without asking a question.

Restrictions:
- Do not use more than {SL_info} words per sentence. 
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
- Address the user of interviewee in your response.  
- Do not use emojis, emoticons, or symbols such as 🙂, 🤓, etc.
- Respond from the perspective of the interviewer, not the user of interviewee.

Output format:
Interviewer: <your summarising response with a maximum of three sentences without questions>

Dialogue:
{format_dialoog(dialoog)}
"""