import re


"""This is done once and stored such that in each run we have the same test set
This is speaker independent, each speaker appears in either one of the splits. """
dev_set = ['1063', '1299', '1026', '1487', '968', '616', '1300', '1297', '611', '349']
test_set =  ['797','1444','1445','1125','1016', '1083', '1106', '1301', '1302', '1323', '1324', '1413', '1463', '1551', '1630', '1650', '1651', '1668', '1672', '1700', '243', '436', '566', '596', '597', '602', '605', '606', '716', '750', '781', '789', '798', '804', '815', '852', '966', '967', '973']


"""Here the prompts for the question generation are designed"""
def format_dialoog(dialoog):
    dialoog = re.sub(r"(Y|Y1):", "Veteraan:", dialoog)
    dialoog = re.sub(r"X:", "Interviewer:", dialoog)

    return dialoog

def get_prompt_LA(dialoog, lexical_info):
    return f"""Je bent een journalistieke interviewer in een gesprek met een oorlogsveteraan uit Nederlands-Indië en Korea.
Je hebt de oorlog niet meegemaakt en je spreekt uitsluitend vanuit het perspectief van de interviewer, jijzelf bent niet de veteraan.

Opdracht:
Genereer een nieuwe, originele vervolgvraag gebaseerd op onderstaande dialoog zoals de interviewer (jij) zou kunnen geven.

Restricties:
- Gebruik niet meer dan {lexical_info} woorden per zin.
- Gebruik spreektaal.
- Zorg voor grammaticale correctheid.
- Geef alleen de nieuwe, originele vraag als output, zonder uitleg of extra tekst.
- Gebruik géén emoji’s, emoticons of tekens zoals 🙂, 🤓, etc.
- Reageer vanuit het perspectief van de interviewer, niet de veteraan.

Outputformaat:
Interviewer: <jouw vervolgvraag>

Dialoog:
{format_dialoog(dialoog)}

"""

def get_prompt_NA(dialoog):
    return f"""Je bent een journalistieke interviewer in een gesprek met een oorlogsveteraan uit Nederlands-Indië en Korea.
Je hebt de oorlog niet meegemaakt en je spreekt uitsluitend vanuit het perspectief van de interviewer, jijzelf bent niet de veteraan.

Opdracht:
Genereer een nieuwe, originele vervolgvraag gebaseerd op onderstaande dialoog zoals de interviewer (jij) zou kunnen geven.

Restricties:
- Gebruik spreektaal.
- Zorg voor grammaticale correctheid.
- Geef alleen de nieuwe, originele vraag als output, zonder uitleg of extra tekst.
- Gebruik géén emoji’s, emoticons of tekens zoals 🙂, 🤓, etc.
- Reageer vanuit het perspectief van de interviewer, niet de veteraan.

Outputformaat:
Interviewer: <jouw vervolgvraag>

Dialoog:
{format_dialoog(dialoog)}

"""