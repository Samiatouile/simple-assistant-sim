"""L'assistant simulé : 4 agents (un par orientation), avec garde-fous.

RÈGLE D'OR (ancrage) : tout fait affirmé doit provenir d'une unité de la
base de connaissances effectivement récupérée. Si rien de pertinent n'est
récupéré, l'assistant NE L'INVENTE PAS : il le dit explicitement et
propose d'orienter vers un conseiller humain (escalade).

Garde-fous obligatoires :
  - transactionnel : ne déclenche jamais une opération, demande toujours
    une confirmation explicite.
  - support : escalade selon des critères explicites (cas "graves"
    prédéfinis dans config.yaml, + critère d'escalade documenté dans la
    procédure récupérée).
"""
from __future__ import annotations

import re
import unicodedata

from src.retrieval import Retriever, load_kb
from src.router import route

MESSAGE_AUCUNE_SOURCE = (
    "Je n'ai aucune information fiable sur ce sujet dans mes sources. "
    "Je vous oriente vers un conseiller humain pour traiter votre demande."
)


def _normalise(texte: str) -> str:
    texte = texte.lower()
    texte = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in texte if not unicodedata.combining(c))


def _extraire_montant(question: str) -> str | None:
    m = re.search(r"(\d+(?:[.,]\d+)?)\s*dh", question, re.I)
    return m.group(1) if m else None


def _extraire_beneficiaire(question: str) -> str | None:
    # Cherche un nom propre après "a", "chez" ou "li" (darija : "à/pour").
    m = re.search(r"\b(?:a|chez|li)\s+([A-Zà-ÿ][\wà-ÿ'-]+)", question)
    return m.group(1) if m else None


def _extraire_action_carte(question: str) -> str:
    q = _normalise(question)
    if "debloque" in q or "débloque" in question.lower():
        return "débloquer"
    if "bloque" in q:
        return "bloquer"
    if "plafond" in q:
        return "modifier le plafond"
    return "une action sur la carte"


class Assistant:
    """Orchestrateur : route la question puis délègue au bon agent."""

    def __init__(self, retriever: Retriever, config: dict | None = None):
        self.retriever = retriever
        self.config = config or {}
        self.top_k = self.config.get("retrieval", {}).get("top_k", 3)
        self.motifs_critiques = [
            _normalise(m) for m in self.config.get("escalade", {}).get("motifs_critiques", [])
        ]

    def repondre(self, question: str) -> dict:
        routage = route(question)
        orientation, intention, palier = routage["orientation"], routage["intention"], routage["palier"]

        if orientation == "transactionnel":
            sortie = self._agent_transactionnel(question, intention)
        elif orientation == "informationnel":
            sortie = self._agent_informationnel(question, intention, palier)
        elif orientation == "onboarding":
            sortie = self._agent_onboarding(question, intention, palier)
        else:  # support (y compris hors_perimetre)
            sortie = self._agent_support(question, intention)

        sortie.update({
            "orientation_predite": orientation,
            "intention_predite": intention,
            "palier_predit": palier,
        })
        return sortie

    # ------------------------------------------------------------------
    # Agent informationnel / FAQ : RAG ancré
    # ------------------------------------------------------------------
    def _agent_informationnel(self, question: str, intention: str, palier: str | None) -> dict:
        unites = self.retriever.search(question, orientation="informationnel",
                                        intention=intention, palier=palier, top_k=self.top_k)
        if not unites:
            return {"reponse": MESSAGE_AUCUNE_SOURCE, "comportement": "escalader", "sources": []}

        meilleure = unites[0]
        reponse = f"{meilleure['texte']} (source : {meilleure['source']})"
        return {"reponse": reponse, "comportement": "repondre",
                "sources": [u["id"] for u in unites]}

    # ------------------------------------------------------------------
    # Agent onboarding : recommandations filtrées par éligibilité
    # ------------------------------------------------------------------
    def _agent_onboarding(self, question: str, intention: str, palier: str | None) -> dict:
        unites = self.retriever.search(question, orientation="onboarding",
                                        intention=intention, palier=palier, top_k=self.top_k)
        if not unites:
            return {"reponse": MESSAGE_AUCUNE_SOURCE, "comportement": "escalader", "sources": []}

        meilleure = unites[0]
        reponse = f"{meilleure['texte']} (source : {meilleure['source']})"
        return {"reponse": reponse, "comportement": "repondre",
                "sources": [u["id"] for u in unites]}

    # ------------------------------------------------------------------
    # Agent support / SAV : résolution guidée + escalade
    # ------------------------------------------------------------------
    def _agent_support(self, question: str, intention: str) -> dict:
        q_norm = _normalise(question)

        # Garde-fou n°1 : motifs critiques définis en config -> escalade immédiate,
        # même si une procédure existe (ex: fraude avérée).
        if any(motif in q_norm for motif in self.motifs_critiques):
            return {
                "reponse": "Votre situation nécessite l'intervention d'un conseiller humain. "
                           "Je vous transfère immédiatement.",
                "comportement": "escalader", "sources": [],
            }

        if intention == "hors_perimetre":
            return {"reponse": MESSAGE_AUCUNE_SOURCE, "comportement": "escalader", "sources": []}

        unites = self.retriever.search(question, orientation="support",
                                        intention=intention, top_k=self.top_k)
        if not unites:
            return {"reponse": MESSAGE_AUCUNE_SOURCE, "comportement": "escalader", "sources": []}

        meilleure = unites[0]
        texte = meilleure["texte"]

        # Garde-fou n°2 : si la procédure récupérée définit elle-même un
        # critère d'escalade et que la question semble correspondre à un
        # cas grave (ex: "etranger", montant élevé), on escalade.
        criteres_graves = ["etranger", "tres eleve", "enorme", "panique", "tres grave", "grave"]
        if "CRITERE D'ESCALADE" in texte and any(c in q_norm for c in criteres_graves):
            return {
                "reponse": "Votre situation nécessite l'intervention d'un conseiller humain. "
                           "Je vous transfère immédiatement.",
                "comportement": "escalader", "sources": [meilleure["id"]],
            }

        reponse = f"{texte} (source : {meilleure['source']})"
        return {"reponse": reponse, "comportement": "repondre", "sources": [u["id"] for u in unites]}

    # ------------------------------------------------------------------
    # Agent transactionnel : extraction de paramètres + confirmation
    # obligatoire. Ne déclenche JAMAIS l'opération lui-même.
    # ------------------------------------------------------------------
    def _agent_transactionnel(self, question: str, intention: str) -> dict:
        montant = _extraire_montant(question)
        beneficiaire = _extraire_beneficiaire(question)

        if intention == "gestion_carte":
            action = _extraire_action_carte(question)
            recap = f"Récapitulatif : {action} votre carte"
            if montant:
                recap += f" (nouveau plafond : {montant} DH)"
        elif intention == "paiement":
            recap = "Récapitulatif : paiement"
            if montant:
                recap += f" de {montant} DH"
            if beneficiaire:
                recap += f" chez {beneficiaire}"
        else:  # virement
            recap = "Récapitulatif : virement"
            if montant:
                recap += f" de {montant} DH"
            if beneficiaire:
                recap += f" à {beneficiaire}"

        reponse = (f"{recap}. Confirmez-vous cette opération ? Aucune opération ne sera "
                   f"exécutée sans votre confirmation explicite.")
        return {"reponse": reponse, "comportement": "demander_confirmation", "sources": []}


def build_assistant(config: dict | None = None) -> Assistant:
    """Fabrique pratique : charge la KB et construit l'assistant."""
    config = config or {}
    kb_path = config.get("kb", {}).get("path", "data/kb.jsonl")
    units = load_kb(kb_path)
    retriever = Retriever(units)
    return Assistant(retriever, config)
