import re
"""Here the prompts for the Question Generation are designed"""

"""This is done once and stored such that in each run we have the same test set"""
dev_set = ['43', '09', '03', '19', '17', '16', '10', '08', '37', '07']
test_set = ['02', '04', '05', '06', '11', '12', '13', '14', '15', '18', '20', '21', '22', '24', '25', '26', '27', '28', '29', '30', '31', '32', '33', '34', '35', '36', '38', '39', '40', '41', '42', '44', '45', '46', '47', '48', '49', '50', '51', '52']

def format_constraints(constraints):
    return '\n'.join([f"- {pos}: {', '.join(words)}" for pos, words in constraints.items()])

def format_dialoog(dialoog):
    dialoog = re.sub(r"Interviewee:", "Interviewee:", dialoog)
    
    return dialoog

def get_prompt_LA(dialoog, lexical_info):
    return f"""You are a journalistic interviewer speaking with a Holocaust survivor.
You did not experience the Holocaust yourself and speak exclusively from the perspective of the interviewer, you are not the person concerned in the events discussed.

Task:
Generate a new, original follow-up question based on the dialogue below, which the interviewer (you) might ask.

Restrictions:
- Do not use more than {lexical_info} words per sentence. 
- Use spoken language.
- Ensure grammatical correctness.
- Output only the new, original question, without explanations or extra text.
- Do not use emojis, emoticons, or symbols such as 🙂, 🤓, etc.
- Respond from the perspective of the interviewer, not the interviewee.

Output format:
Interviewer: <your follow-up question>

Dialogue:
{format_dialoog(dialoog)}
"""

def get_prompt_NA(dialoog):
    return f"""You are a journalistic interviewer speaking with a Holocaust survivor.
You did not experience the Holocaust yourself and speak exclusively from the perspective of the interviewer, you are not the person concerned in the events discussed.

Task:
Generate a new, original follow-up question based on the dialogue below, which the interviewer (you) might ask.

Restrictions:
- Use spoken language.
- Ensure grammatical correctness.
- Output only the new, original question, without explanations or extra text.
- Do not use emojis, emoticons, or symbols such as 🙂, 🤓, etc.
- Respond from the perspective of the interviewer, not the interviewee.

Output format:
Interviewer: <your follow-up question>

Dialogue:
{format_dialoog(dialoog)}


"""