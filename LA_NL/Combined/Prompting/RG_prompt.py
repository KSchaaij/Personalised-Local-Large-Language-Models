import re

"""Here the prompts for Reflection Generation are designed"""
def format_pos(constraints):
    return '\n'.join([f"- {pos}: {', '.join(words)}" for pos, words in constraints.items()])

def format_level(level):
    if len(level) > 1:
        return f"""Gebruik een {level[0]} tot {level[1]} taalniveau."""
    else:
        return f"""Gebruik een {level[0]} taalniveau """
    
def format_dialoog(dialoog):
    dialoog = re.sub(r"(Y|Y1):", "Veteraan:", dialoog)
    dialoog = re.sub(r"X:", "Interviewer:", dialoog)
    
    return dialoog

def get_prompt_LA(dialoog, pos, ls, rs):
    return f"""Je bent een journalistieke interviewer in een gesprek met een oorlogsveteraan uit Nederlands-Indië en Korea.
Je hebt de oorlog niet meegemaakt en je spreekt uitsluitend vanuit het perspectief van de interviewer, jijzelf bent niet de veteraan.

Opdracht:
Genereer een reactie van de interviewer (jij) van maximaal drie zinnen binnen de onderstaande dialoog met de veteraan die samenvat wat er gezegd is, maar geen vraag stelt.

Restricties:
- Gebruik niet meer dan {ls} woorden per zin.
- {format_level(rs)}
- Gebruik zoveel mogelijk woorden en uitdrukkingen uit de woordenlijst van de oorlogsveteraan. 
- Gebruik spreektaal.
- Zorg voor grammaticale correctheid.
- Stel nooit een vraag.
- Spreek de veteraan aan in jouw reactie.
- Gebruik nooit emoji’s, emoticons of tekens zoals 🙂, 🤓, etc.
- Reageer vanuit het perspectief van de interviewer, niet de veteraan.

Outputformaat:
Interviewer: <jouw samenvattende reactie van maximaal drie zinnen zonder vragen>

Dialoog:
{format_dialoog(dialoog)}

Woordenlijst van de oorlogsveteraan:
{format_pos(pos)}

"""

def get_prompt_NA(dialoog):
    return f"""Je bent een journalistieke interviewer in een gesprek met een oorlogsveteraan uit Nederlands-Indië en Korea.
Je hebt de oorlog niet meegemaakt en je spreekt uitsluitend vanuit het perspectief van de interviewer, jijzelf bent niet de veteraan.

Opdracht:
Genereer een reactie van de interviewer (jij) van maximaal drie zinnen binnen de onderstaande dialoog met de veteraan die samenvat wat er gezegd is, maar geen vraag stelt.

Restricties:
- Gebruik spreektaal.
- Zorg voor grammaticale correctheid.
- Stel nooit een vraag.
- Spreek de veteraan aan in jouw reactie.
- Gebruik nooit emoji’s, emoticons of tekens zoals 🙂, 🤓, etc.
- Reageer vanuit het perspectief van de interviewer, niet de veteraan.

Outputformaat:
Interviewer: <jouw samenvattende reactie van maximaal drie zinnen zonder vragen>

Dialoog:
{format_dialoog(dialoog)}
"""