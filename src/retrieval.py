"""Récupération (RAG) des unités de la base de connaissances pertinentes
pour une question, via TF-IDF (scikit-learn).

Le retrieval filtre d'abord les unités candidates par orientation /
intention (et palier si renseigné), puis classe les survivantes par
similarité cosinus TF-IDF avec la question. C'est volontairement simple :
le but est de pouvoir illustrer comment un mauvais retrieval (ex: il
ramène une unité périmée, ou la mauvaise version d'un tarif contradictoire)
dégrade la fiabilité mesurée en aval.
"""
from __future__ import annotations

import json

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_kb(path: str = "data/kb.jsonl") -> list[dict]:
    units = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                units.append(json.loads(line))
    return units


class Retriever:
    """Index TF-IDF construit une fois sur toute la KB."""

    def __init__(self, units: list[dict]):
        self.units = units
        self._vectorizer = TfidfVectorizer()
        textes = [u["texte"] for u in units]
        self._matrix = self._vectorizer.fit_transform(textes)

    def search(self, question: str, orientation: str | None = None,
               intention: str | None = None, palier: str | None = None,
               top_k: int = 3) -> list[dict]:
        """Renvoie jusqu'à `top_k` unités triées par pertinence décroissante.

        Filtrage préalable : si `orientation`/`intention` sont fournis, on
        ne considère que les unités correspondantes. Le `palier` filtre
        les unités spécifiques à un autre palier (mais garde les unités
        "génériques" dont palier est None).
        """
        candidats_idx = [
            i for i, u in enumerate(self.units)
            if (orientation is None or u["orientation"] == orientation)
            and (intention is None or u["intention"] == intention)
            and (palier is None or u["palier"] is None or u["palier"] == palier)
        ]
        if not candidats_idx:
            return []

        question_vec = self._vectorizer.transform([question])
        sims = cosine_similarity(question_vec, self._matrix[candidats_idx]).ravel()

        ordre = sorted(range(len(candidats_idx)), key=lambda k: sims[k], reverse=True)
        resultats = []
        for k in ordre[:top_k]:
            if sims[k] <= 0:
                continue
            resultats.append(self.units[candidats_idx[k]])
        return resultats
