"""Routage : détecte l'orientation, l'intention et le palier d'une question.

Implémentation volontairement SIMPLE (règles + mots-clés), mais structurée
derrière une fonction unique `route(question)` afin de pouvoir la remplacer
plus tard (TF-IDF, classifieur supervisé, etc.) sans toucher au reste du
pipeline (assistant.py, evaluate.py).

Le routeur n'est pas parfait par construction : il fait partie des sources
d'erreur mesurées par le harnais (KPI "précision d'intention").
"""
from __future__ import annotations

import re
import unicodedata

PALIERS = ["Go", "Plus", "Prime", "Metal"]

# Mots-clés par intention. L'ordre compte : on teste dans cet ordre et on
# retient la première intention dont un mot-clé est trouvé.
INTENTION_KEYWORDS = {
    # informationnel
    "tarif_palier": ["tarif", "prix", "coute", "cout", "gratuit", "taman", "kayji"],
    "plafond_retrait": ["plafond", "retrait", "retirer", "rtire"],
    "frais_virement": ["frais de virement", "virement gratuit", "virement vers", "thelsi"],
    "changer_palier": ["changer de palier", "passer de", "bedel", "beddel"],
    "eligibilite_palier": ["eligible", "eligibilite", "conditions pour", "qui peut prendre"],
    # support
    "carte_bloquee": ["carte bloquee", "carte est bloquee", "debloquer ma carte", "masdouda", "carti dyali"],
    "opposition_carte": ["perdu ma carte", "carte volee", "faire opposition", "opposition"],
    "fraude": ["fraude", "pirate", "transaction que je n'ai pas faite", "sra9"],
    "litige_paiement": ["litige", "contester", "paiement conteste", "facture 2 fois", "ne reconnais pas un paiement"],
    "compte_bloque": ["compte est bloque", "compte bloque", "compte dyali masdoud"],
    # onboarding
    "ouverture_compte": ["ouvrir un compte", "ouvrir compte", "n7el compte"],
    "premiere_utilisation": ["premier virement", "virement lawal", "envoyer de l'argent a un ami"],
    "service_eligible": ["acces a l'epargne", "epargne remuneree", "micro-credit", "credit instantane", "access a quoi"],
    # transactionnel
    "virement": ["fais un virement", "envoyer", "vire ", "sift li"],
    "paiement": ["paye ", "payer", "khelles"],
    "gestion_carte": ["bloque ma carte", "augmente mon plafond", "sdoud li carte"],
}

INTENTION_TO_ORIENTATION = {
    "tarif_palier": "informationnel",
    "plafond_retrait": "informationnel",
    "frais_virement": "informationnel",
    "changer_palier": "informationnel",
    "eligibilite_palier": "informationnel",
    "carte_bloquee": "support",
    "opposition_carte": "support",
    "fraude": "support",
    "litige_paiement": "support",
    "compte_bloque": "support",
    "ouverture_compte": "onboarding",
    "premiere_utilisation": "onboarding",
    "service_eligible": "onboarding",
    "virement": "transactionnel",
    "paiement": "transactionnel",
    "gestion_carte": "transactionnel",
}


def _normalise(texte: str) -> str:
    """Minuscule + suppression des accents, pour matcher plus robustement
    fr/darija translitérée (ex: "remunérée" -> "remuneree")."""
    texte = texte.lower()
    texte = unicodedata.normalize("NFKD", texte)
    texte = "".join(c for c in texte if not unicodedata.combining(c))
    return texte


def detect_palier(question: str) -> str | None:
    q = _normalise(question)
    for palier in PALIERS:
        if re.search(rf"\b{palier.lower()}\b", q):
            return palier
    return None


def detect_intention(question: str) -> str | None:
    q = _normalise(question)
    for intention, mots in INTENTION_KEYWORDS.items():
        for mot in mots:
            if _normalise(mot) in q:
                return intention
    return None


def route(question: str) -> dict:
    """Renvoie {"orientation": ..., "intention": ..., "palier": ...}.

    Si aucune intention n'est reconnue, orientation="support" et
    intention="hors_perimetre" : c'est la convention "je ne sais pas
    traiter cette demande" -> direction par défaut vers le SAV qui pourra
    escalader (cf. règle d'or de l'ancrage : ne jamais inventer).
    """
    intention = detect_intention(question)
    palier = detect_palier(question)

    if intention is None:
        return {"orientation": "support", "intention": "hors_perimetre", "palier": palier}

    orientation = INTENTION_TO_ORIENTATION[intention]
    return {"orientation": orientation, "intention": intention, "palier": palier}
