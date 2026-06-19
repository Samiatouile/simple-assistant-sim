"""Commande `log-iteration` : automatise la partie chiffrée du journal
d'itérations (`JOURNAL.md`).

Compare `reports/kpi_ventiles.csv` (courant) à
`reports/kpi_ventiles_precedent.csv` (sauvegardé automatiquement par
`report`, voir `src/kpi_backup.py`), calcule les deltas des KPI niveau
global / orientation / palier, et ajoute une nouvelle entrée à la fin de
`JOURNAL.md` avec :
  - un titre numéroté automatiquement ;
  - la date du jour ;
  - une section "Résultat (auto)" listant les changements significatifs,
    triés par ampleur décroissante ;
  - des sections vides "Constat", "Diagnostic", "Action", "Enseignement"
    à compléter à la main.

Ne touche jamais à `reports/rapport.md`.
"""
from __future__ import annotations

import os
import re
from datetime import date

import pandas as pd
import yaml

KPI_COLONNES = [
    "intention_correcte", "comportement_correct", "exactitude",
    "couverture_ok", "ancrage", "pertinence", "escalade_pertinente",
]

NIVEAUX_COMPARES = ("global", "orientation", "palier")


def _cle(niveau: str, row: pd.Series):
    """Clé d'identification stable d'une ligne, pour matcher courant/précédent."""
    if niveau == "global":
        return ("global",)
    if niveau == "orientation":
        return ("orientation", row["orientation"])
    if niveau == "palier":
        palier = row["palier"]
        return ("palier", palier if pd.notna(palier) else "__sans_palier__")
    return (niveau,)


def _libelle(niveau: str, row: pd.Series) -> str:
    if niveau == "global":
        return "global"
    if niveau == "orientation":
        return f"orientation {row['orientation']}"
    if niveau == "palier":
        palier = row["palier"]
        return f"palier {palier}" if pd.notna(palier) else "palier (sans palier)"
    return niveau


def _indexer(df: pd.DataFrame) -> dict:
    index = {}
    for niveau in NIVEAUX_COMPARES:
        for _, row in df[df["niveau"] == niveau].iterrows():
            index[_cle(niveau, row)] = (niveau, row)
    return index


def calculer_deltas(df_courant: pd.DataFrame, df_precedent: pd.DataFrame) -> list[dict]:
    """Renvoie la liste des changements de KPI significatifs (delta non nul),
    triée par ampleur décroissante."""
    index_courant = _indexer(df_courant)
    index_precedent = _indexer(df_precedent)

    deltas = []
    for cle, (niveau, row_courant) in index_courant.items():
        if cle not in index_precedent:
            continue
        _, row_precedent = index_precedent[cle]

        for col in KPI_COLONNES:
            avant, apres = row_precedent[col], row_courant[col]
            if pd.isna(avant) or pd.isna(apres):
                continue
            delta_pts = round((apres - avant) * 100)
            if delta_pts == 0:
                continue
            deltas.append({
                "kpi": col,
                "libelle": _libelle(niveau, row_courant),
                "avant": avant,
                "apres": apres,
                "delta_pts": int(delta_pts),
            })

    deltas.sort(key=lambda d: abs(d["delta_pts"]), reverse=True)
    return deltas


def _formater_delta(d: dict) -> str:
    signe = "+" if d["delta_pts"] > 0 else ""
    return (f"- **{d['kpi']}** / {d['libelle']} : {d['avant'] * 100:.0f}% → "
            f"{d['apres'] * 100:.0f}% ({signe}{d['delta_pts']} pts)")


def _compter_iterations(journal_path: str) -> int:
    if not os.path.exists(journal_path):
        return 0
    with open(journal_path, encoding="utf-8") as f:
        contenu = f.read()
    return len(re.findall(r"^## Itération \d+", contenu, re.M))


def main():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    chemin_courant = config["report"]["csv_kpi"]
    chemin_precedent = config["report"]["csv_kpi_precedent"]
    journal_path = config["journal"]["path"]

    if not os.path.exists(chemin_courant):
        print(f"Aucun {chemin_courant} trouvé : lancez d'abord 'run-eval' puis 'report'.")
        return

    if not os.path.exists(chemin_precedent):
        lignes_resultat = [
            "Pas de comparaison possible : aucun `reports/kpi_ventiles_precedent.csv` "
            "trouvé (première itération journalisée, ou KPI jamais régénérés depuis)."
        ]
    else:
        df_courant = pd.read_csv(chemin_courant, encoding="utf-8")
        df_precedent = pd.read_csv(chemin_precedent, encoding="utf-8")
        deltas = calculer_deltas(df_courant, df_precedent)
        if deltas:
            lignes_resultat = [_formater_delta(d) for d in deltas]
        else:
            lignes_resultat = ["Aucun changement significatif détecté entre les deux mesures."]

    numero = _compter_iterations(journal_path) + 1
    aujourdhui = date.today().isoformat()

    fichier_existe = os.path.exists(journal_path)
    bloc = []
    bloc.append(f"## Itération {numero} — [À COMPLÉTER]")
    bloc.append("")
    bloc.append(f"**Date** : {aujourdhui}")
    bloc.append("")
    bloc.append("### Résultat (auto)")
    bloc.append("")
    bloc.extend(lignes_resultat)
    bloc.append("")
    bloc.append("### Constat")
    bloc.append("")
    bloc.append("### Diagnostic")
    bloc.append("")
    bloc.append("### Action")
    bloc.append("")
    bloc.append("### Enseignement")
    bloc.append("")
    bloc.append("---")
    bloc.append("")

    with open(journal_path, "a", encoding="utf-8") as f:
        if not fichier_existe:
            f.write("# Journal d'itérations — simple-assistant-sim\n\n")
            f.write(
                "Une entrée par itération : ce qui a été changé, ce que la mesure "
                "montre, et ce qu'on en retient. La section \"Résultat (auto)\" est "
                "générée par `python -m src.cli log-iteration` ; les autres sections "
                "sont à compléter à la main.\n\n"
            )
        f.write("\n".join(bloc) + "\n")

    print(f"Itération {numero} ajoutée à {journal_path} ({len(lignes_resultat)} ligne(s) de résultat).")


if __name__ == "__main__":
    main()
