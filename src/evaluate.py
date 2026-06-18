"""Harnais d'évaluation : fait tourner l'assistant simulé sur le golden set
et note chaque réponse selon les dimensions de fiabilité du cahier des
charges.

Deux familles de vérifications :
  - DÉTERMINISTES (objectives) : précision d'intention, respect du
    comportement attendu, exactitude des faits numériques/qualitatifs,
    couverture, escalade pertinente.
  - LLM-AS-JUDGE (subjectives) : ancrage, pertinence (barème 0/1/2).

Le résultat détaillé (une ligne par question) est écrit dans
`reports/resultats_detail.csv` ; c'est `report.py` qui agrège ensuite ces
lignes en KPI ventilés.
"""
from __future__ import annotations

import json
import re
import unicodedata

import pandas as pd
import yaml

from src.assistant import build_assistant
from src.judge import juger
from src.model import get_llm_client
from src.retrieval import load_kb


def _normalise(texte: str) -> str:
    texte = texte.lower()
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if not unicodedata.combining(c))


def _charger_golden_set(path: str) -> list[dict]:
    lignes = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lignes.append(json.loads(line))
    return lignes


def _verifier_exactitude(reponse: str, reponse_attendue: str) -> int | None:
    """Vérification déterministe de l'exactitude factuelle.

    - Si la réponse attendue contient un nombre (ex: "59 DH"), on compare
      le PREMIER nombre trouvé dans la réponse de l'assistant à celui
      attendu : 1 si égal, 0 sinon.
    - Sinon, on fait une comparaison textuelle normalisée (sous-chaîne) :
      1 si les mots-clés de la réponse attendue apparaissent dans la
      réponse, 0 sinon.
    Renvoie None si non applicable (pas de réponse attendue factuelle,
    ex. cas d'escalade pure).
    """
    if not reponse_attendue:
        return None

    nombre_attendu = re.search(r"\d+(?:[.,]\d+)?", reponse_attendue)
    if nombre_attendu:
        nombre_obtenu = re.search(r"\d+(?:[.,]\d+)?", reponse)
        if not nombre_obtenu:
            return 0
        return 1 if nombre_obtenu.group() == nombre_attendu.group() else 0

    r_norm = _normalise(reponse)
    attendu_norm = _normalise(reponse_attendue)
    mots_cles = [m for m in re.findall(r"[a-z0-9]{4,}", attendu_norm)]
    if not mots_cles:
        return None
    trouves = sum(1 for m in mots_cles if m in r_norm)
    return 1 if trouves / len(mots_cles) >= 0.5 else 0


def main():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    golden = _charger_golden_set(config["golden_set"]["path"])
    kb_units = {u["id"]: u for u in load_kb(config["kb"]["path"])}
    assistant = build_assistant(config)
    llm = get_llm_client(config)

    lignes = []
    for cas in golden:
        question = cas["question"]
        sortie = assistant.repondre(question)

        sources_ids = sortie.get("sources", [])
        sources_texte = " | ".join(kb_units[sid]["texte"] for sid in sources_ids if sid in kb_units)

        intention_correcte = int(sortie["intention_predite"] == cas["intention"])
        comportement_correct = int(sortie["comportement"] == cas["comportement_attendu"])

        exactitude = None
        if cas["comportement_attendu"] == "repondre":
            exactitude = _verifier_exactitude(sortie["reponse"], cas["reponse_attendue"])

        escalade_attendue = int(cas["comportement_attendu"] == "escalader")
        escalade_obtenue = int(sortie["comportement"] == "escalader")
        escalade_pertinente = None
        if escalade_attendue:
            escalade_pertinente = escalade_obtenue
        elif escalade_obtenue and not escalade_attendue:
            # Fausse escalade = couverture dégradée (cf. ci-dessous), pas
            # une "escalade pertinente" puisqu'aucune escalade n'était due.
            escalade_pertinente = 0

        couverture_ok = int(not (sortie["intention_predite"] == "hors_perimetre"
                                  and cas["intention"] != "hors_perimetre"))

        jugement_ancrage = juger(llm, question, sortie["reponse"], sources_texte, "ancrage")
        jugement_pertinence = juger(llm, question, sortie["reponse"], sources_texte, "pertinence")

        lignes.append({
            "id": cas["id"],
            "question": question,
            "orientation": cas["orientation"],
            "intention": cas["intention"],
            "palier": cas["palier"],
            "difficulte": cas["difficulte"],
            "langue": cas["langue"],
            "comportement_attendu": cas["comportement_attendu"],
            "comportement_obtenu": sortie["comportement"],
            "orientation_predite": sortie["orientation_predite"],
            "intention_predite": sortie["intention_predite"],
            "intention_correcte": intention_correcte,
            "comportement_correct": comportement_correct,
            "exactitude": exactitude,
            "couverture_ok": couverture_ok,
            "escalade_attendue": escalade_attendue,
            "escalade_obtenue": escalade_obtenue,
            "escalade_pertinente": escalade_pertinente,
            "ancrage_score": jugement_ancrage["score"],
            "ancrage_justification": jugement_ancrage["justification"],
            "pertinence_score": jugement_pertinence["score"],
            "pertinence_justification": jugement_pertinence["justification"],
            "reponse": sortie["reponse"],
            "sources_utilisees": ",".join(sources_ids),
        })

    df = pd.DataFrame(lignes)
    out_path = config["report"]["csv_detail"]
    df.to_csv(out_path, index=False)
    print(f"Évaluation terminée : {len(df)} questions notées -> {out_path}")


if __name__ == "__main__":
    main()
