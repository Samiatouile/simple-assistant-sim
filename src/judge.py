"""LLM-as-judge pour les critères subjectifs : ancrage et pertinence.

Barème explicite 0/1/2 :
  0 = critère non respecté
  1 = partiellement respecté
  2 = pleinement respecté

Sortie JSON stricte {"score": int, "justification": str}, température 0.
Consigne donnée au juge : ne JAMAIS utiliser de connaissances externes ;
si l'info n'est pas dans les sources fournies, la considérer comme non
sourcée (donc dégrader l'ancrage).

En mode MOCK (pas de clé API), `model.MockLLM` simule un juge déterministe
(voir `MockLLM._judge_mock`) afin que tout le pipeline tourne hors ligne.
"""
from __future__ import annotations

import json

from src.model import LLMClient

PROMPT_TEMPLATE = """Tu es un juge strict qui évalue la qualité d'une réponse d'assistant
bancaire, UNIQUEMENT par rapport aux sources fournies.

CONSIGNE IMPORTANTE : ne JAMAIS utiliser de connaissances externes. Si une
information de la réponse n'est pas présente dans les sources fournies,
considère-la comme NON SOURCÉE (cela doit faire baisser le score).

QUESTION: {question}
REPONSE_A_JUGER: {reponse}
SOURCES: {sources}
CRITERE: {critere}

Barème :
- 0 = le critère "{critere}" n'est pas respecté
- 1 = partiellement respecté
- 2 = pleinement respecté

FORMAT_JSON_JUGE : réponds STRICTEMENT avec un JSON de la forme
{{"score": <0|1|2>, "justification": "<une phrase>"}}
"""


def _construire_prompt(question: str, reponse: str, sources_texte: str, critere: str) -> str:
    return PROMPT_TEMPLATE.format(question=question, reponse=reponse,
                                   sources=sources_texte, critere=critere)


def _parser_json_juge(sortie_brute: str) -> dict:
    """Extrait le JSON du jugement, même si le LLM ajoute du texte autour."""
    debut = sortie_brute.find("{")
    fin = sortie_brute.rfind("}")
    if debut == -1 or fin == -1:
        return {"score": 0, "justification": "Réponse du juge non parsable, score par défaut 0."}
    try:
        return json.loads(sortie_brute[debut:fin + 1])
    except json.JSONDecodeError:
        return {"score": 0, "justification": "Réponse du juge non parsable, score par défaut 0."}


def juger(llm: LLMClient, question: str, reponse: str, sources_texte: str, critere: str) -> dict:
    """Renvoie {"score": 0|1|2, "justification": str} pour un critère donné
    ("ancrage" ou "pertinence")."""
    prompt = _construire_prompt(question, reponse, sources_texte, critere)
    sortie_brute = llm.complete(prompt)
    return _parser_json_juge(sortie_brute)
