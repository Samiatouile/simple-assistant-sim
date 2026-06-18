"""Mode interactif : boucle de chat en console pour tester l'assistant
manuellement, question par question.

Pour chaque réponse, affiche :
  - l'orientation et l'intention détectées (routage) ;
  - les unités de connaissance utilisées (id + source), pour vérifier
    l'ancrage à l'œil ;
  - si la réponse est ancrée (sources trouvées) ou si l'assistant escalade
    vers un conseiller humain ;
  - en mode transactionnel, le récapitulatif + la demande de confirmation.

Fonctionne à l'identique en mode MOCK (sans clé API) et avec l'API
Anthropic réelle (ANTHROPIC_API_KEY) : la génération de réponse de
l'assistant est basée sur la KB ancrée, indépendamment du provider LLM
utilisé pour le jugement (voir src/model.py).
"""
from __future__ import annotations

import os

import yaml

from src.assistant import build_assistant
from src.retrieval import load_kb

COMMANDES_SORTIE = {"exit", "quit", "q", ":q"}


def _afficher_entete(config: dict):
    provider = "API Anthropic réelle" if os.environ.get("ANTHROPIC_API_KEY") else "MOCK (hors ligne, déterministe)"
    print("=" * 70)
    print("Assistant virtuel 'Simple' — mode chat interactif")
    print(f"Modèle de génération : {provider}")
    print(f"KB version {config['kb']['version']} | tapez 'exit' pour quitter")
    print("=" * 70)


def _afficher_reponse(sortie: dict, kb_units: dict):
    print(f"\n[routage]      orientation = {sortie['orientation_predite']} | "
          f"intention = {sortie['intention_predite']} | palier = {sortie['palier_predit']}")

    sources = sortie.get("sources", [])
    if sources:
        print("[sources]      unités de connaissance utilisées :")
        for sid in sources:
            unite = kb_units.get(sid)
            if unite:
                print(f"               - {sid} (source : {unite['source']})")
            else:
                print(f"               - {sid}")
    else:
        print("[sources]      aucune unité de connaissance utilisée")

    comportement = sortie["comportement"]
    if comportement == "escalader":
        print("[fiabilité]    ESCALADE vers un conseiller humain (pas d'affirmation non sourcée)")
    elif comportement == "demander_confirmation":
        print("[fiabilité]    confirmation requise avant toute exécution (mode transactionnel)")
    elif sources:
        print("[fiabilité]    réponse ANCRÉE dans les sources ci-dessus")
    else:
        print("[fiabilité]    réponse SANS source identifiée (à surveiller)")

    print(f"\nAssistant > {sortie['reponse']}\n")


def main():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    kb_units = {u["id"]: u for u in load_kb(config["kb"]["path"])}
    assistant = build_assistant(config)

    _afficher_entete(config)

    while True:
        try:
            question = input("Vous > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nFin de la session.")
            break

        if not question:
            continue
        if question.lower() in COMMANDES_SORTIE:
            print("Fin de la session.")
            break

        sortie = assistant.repondre(question)
        _afficher_reponse(sortie, kb_units)


if __name__ == "__main__":
    main()
