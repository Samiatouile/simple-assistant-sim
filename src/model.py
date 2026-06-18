"""Interface unique vers un "LLM", avec deux implémentations interchangeables.

Tout le reste du projet (assistant.py et judge.py) appelle UNIQUEMENT
`get_llm_client()` et la méthode `.complete(prompt)` qui en résulte. Ainsi,
passer du mode hors-ligne (MOCK) à l'API Anthropic réelle ne change aucune
ligne de logique métier : il suffit de définir ANTHROPIC_API_KEY.
"""
from __future__ import annotations

import hashlib
import os
import re
from abc import ABC, abstractmethod


class LLMClient(ABC):
    """Interface commune : un client LLM sait juste compléter un prompt."""

    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Renvoie une réponse texte à partir d'un prompt."""
        raise NotImplementedError


class MockLLM(LLMClient):
    """Implémentation déterministe, sans aucune clé API.

    Elle ne "comprend" pas vraiment le prompt : elle applique des règles
    simples et reproductibles. Le but n'est pas la qualité de génération,
    mais de pouvoir faire tourner TOUT le pipeline (assistant + juge) hors
    ligne, de façon stable d'une exécution à l'autre (même prompt -> même
    sortie), ce qui est essentiel pour comparer deux itérations.
    """

    def complete(self, prompt: str) -> str:
        # Cas spécial utilisé par judge.py : si le prompt demande un JSON
        # de notation, on simule un jugement déterministe basé sur la
        # présence de mots clés (voir judge.py pour la construction du prompt).
        if "FORMAT_JSON_JUGE" in prompt:
            return self._judge_mock(prompt)
        # Sinon, réponse générique stable basée sur un hash du prompt
        # (utilisé seulement si l'assistant délègue du texte libre au LLM,
        # ce qui n'est pas le cas dans la version actuelle : l'assistant
        # construit ses réponses directement à partir de la KB).
        digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:8]
        return f"[réponse-mock-{digest}]"

    @staticmethod
    def _judge_mock(prompt: str) -> str:
        """Juge factice déterministe pour ancrage/pertinence.

        Règle simple et reproductible : on regarde si le texte de la
        réponse à juger contient des fragments du texte des sources
        fournies dans le prompt. Plus le recouvrement est fort, meilleur
        le score d'ancrage. Cela suffit pour démontrer le pipeline en
        mode hors-ligne ; en mode réel, c'est l'API Anthropic qui juge.
        """
        reponse_m = re.search(r"REPONSE_A_JUGER:\s*(.*?)\nSOURCES:", prompt, re.S)
        sources_m = re.search(r"SOURCES:\s*(.*?)\nCRITERE:", prompt, re.S)
        critere_m = re.search(r"CRITERE:\s*(\w+)", prompt)
        reponse = (reponse_m.group(1) if reponse_m else "").lower()
        sources = (sources_m.group(1) if sources_m else "").lower()
        critere = critere_m.group(1) if critere_m else "ancrage"

        if "aucune information disponible" in reponse or "conseiller" in reponse:
            # L'assistant a correctement refusé d'inventer -> ancrage parfait.
            score = 2
            justification = "La réponse n'affirme rien hors des sources (escalade ou refus explicite)."
        elif not sources.strip():
            score = 0
            justification = "Aucune source fournie : impossible de considérer la réponse comme ancrée."
        else:
            mots_reponse = set(re.findall(r"[a-zà-ÿ0-9]{4,}", reponse))
            mots_sources = set(re.findall(r"[a-zà-ÿ0-9]{4,}", sources))
            if not mots_reponse:
                taux = 0.0
            else:
                taux = len(mots_reponse & mots_sources) / len(mots_reponse)
            if taux >= 0.5:
                score = 2
                justification = f"Fort recouvrement lexical avec les sources ({taux:.0%})."
            elif taux >= 0.2:
                score = 1
                justification = f"Recouvrement lexical partiel avec les sources ({taux:.0%})."
            else:
                score = 0
                justification = f"Faible recouvrement lexical avec les sources ({taux:.0%}) : possible invention."

        return f'{{"score": {score}, "justification": "{justification} (critère: {critere})"}}'


class AnthropicLLM(LLMClient):
    """Implémentation réelle via l'API Anthropic.

    N'est instanciée que si ANTHROPIC_API_KEY est présent dans
    l'environnement. Le nom du modèle n'est jamais hardcodé : il est lu
    dans la variable d'environnement ANTHROPIC_MODEL, avec une valeur par
    défaut de secours si elle est absente.
    """

    def __init__(self, model_default: str = "claude-haiku-4-5", model_env: str = "ANTHROPIC_MODEL",
                 temperature: float = 0.0):
        import anthropic  # import local : dépendance optionnelle

        self._client = anthropic.Anthropic()
        self._model = os.environ.get(model_env, model_default)
        self._temperature = temperature

    def complete(self, prompt: str) -> str:
        message = self._client.messages.create(
            model=self._model,
            max_tokens=512,
            temperature=self._temperature,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in message.content if hasattr(block, "text"))


def get_llm_client(config: dict | None = None) -> LLMClient:
    """Fabrique le client LLM à utiliser, selon la configuration et l'environnement.

    - provider == "mock"      -> toujours MockLLM
    - provider == "anthropic" -> toujours AnthropicLLM (lève une erreur si pas de clé)
    - provider == "auto" (défaut) -> AnthropicLLM si ANTHROPIC_API_KEY existe, sinon MockLLM
    """
    config = config or {}
    model_cfg = config.get("model", {})
    provider = model_cfg.get("provider", "auto")
    has_key = bool(os.environ.get("ANTHROPIC_API_KEY"))

    use_anthropic = provider == "anthropic" or (provider == "auto" and has_key)

    if use_anthropic:
        return AnthropicLLM(
            model_default=model_cfg.get("anthropic_model_default", "claude-haiku-4-5"),
            model_env=model_cfg.get("anthropic_model_env", "ANTHROPIC_MODEL"),
            temperature=model_cfg.get("temperature_judge", 0.0),
        )
    return MockLLM()
