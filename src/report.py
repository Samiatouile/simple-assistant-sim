"""Agrège les résultats détaillés de l'évaluation en KPI VENTILÉS
(orientation × intention × palier) et produit le rapport de fiabilité
(CSV + Markdown), comparable d'une itération à l'autre.

Le rapport ne se contente jamais d'une moyenne globale : il montre où
l'assistant échoue, et alerte explicitement sur les groupes dont un KPI
est nettement sous la moyenne (signe probable d'un défaut de donnée ou
de logique, cf. data_issues.md).
"""
from __future__ import annotations

import pandas as pd
import yaml

from src.kpi_backup import backup_kpi

SEUIL_ALERTE = 0.7  # un KPI sous ce seuil, alors que la moyenne globale est nettement au-dessus, déclenche une alerte


def _kpi_par(df: pd.DataFrame, colonnes: list[str]) -> pd.DataFrame:
    if not colonnes:
        df = df.assign(_global="toutes questions")
        colonnes = ["_global"]
    agg = df.groupby(colonnes, dropna=False).agg(
        n=("id", "count"),
        intention_correcte=("intention_correcte", "mean"),
        comportement_correct=("comportement_correct", "mean"),
        exactitude=("exactitude", "mean"),
        couverture_ok=("couverture_ok", "mean"),
        ancrage=("ancrage_score", lambda s: (s / 2).mean()),
        pertinence=("pertinence_score", lambda s: (s / 2).mean()),
        escalade_pertinente=("escalade_pertinente", "mean"),
    ).reset_index()
    return agg


def _detecter_alertes(agg_orientation_intention: pd.DataFrame) -> list[str]:
    alertes = []
    kpi_cols = ["intention_correcte", "comportement_correct", "exactitude",
                "couverture_ok", "ancrage", "pertinence", "escalade_pertinente"]
    for col in kpi_cols:
        moyenne_globale = agg_orientation_intition_safe_mean(agg_orientation_intention, col)
        for _, row in agg_orientation_intention.iterrows():
            valeur = row[col]
            if pd.isna(valeur):
                continue
            if valeur < SEUIL_ALERTE and moyenne_globale - valeur > 0.15:
                alertes.append(
                    f"- **{col}** dégradé pour orientation=`{row['orientation']}` / "
                    f"intention=`{row['intention']}` : {valeur:.0%} (moyenne globale : {moyenne_globale:.0%})"
                )
    return alertes


def agg_orientation_intition_safe_mean(df: pd.DataFrame, col: str) -> float:
    return df[col].dropna().mean() if df[col].notna().any() else float("nan")


def main():
    with open("config.yaml", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    df = pd.read_csv(config["report"]["csv_detail"], encoding="utf-8")

    global_kpi = _kpi_par(df, [])
    par_orientation = _kpi_par(df, ["orientation"])
    par_orientation_intention = _kpi_par(df, ["orientation", "intention"])
    par_palier = _kpi_par(df, ["palier"])

    # CSV unique avec toutes les ventilations, une colonne "niveau" pour les distinguer.
    global_kpi.insert(0, "niveau", "global")
    par_orientation.insert(0, "niveau", "orientation")
    par_orientation_intention.insert(0, "niveau", "orientation_intention")
    par_palier.insert(0, "niveau", "palier")
    kpi_complet = pd.concat([global_kpi, par_orientation, par_orientation_intention, par_palier],
                             ignore_index=True)

    # Avant d'écraser le KPI courant, on le sauvegarde comme "précédent" :
    # log-iteration compare alors automatiquement la mesure d'avant ce
    # `report` à celle d'après, sans copie manuelle.
    chemin_kpi = config["report"]["csv_kpi"]
    chemin_kpi_precedent = config["report"]["csv_kpi_precedent"]
    if backup_kpi(chemin_kpi, chemin_kpi_precedent):
        print(f"KPI de l'itération précédente sauvegardés -> {chemin_kpi_precedent}")
    else:
        print("Aucun KPI précédent trouvé : pas de comparaison possible pour cette itération.")

    kpi_complet.to_csv(chemin_kpi, index=False, encoding="utf-8")

    alertes = _detecter_alertes(par_orientation_intention)

    lignes_md = []
    lignes_md.append("# Rapport de fiabilité — assistant virtuel \"Simple\"\n")
    lignes_md.append(f"- KB version : `{config['kb']['version']}`")
    lignes_md.append(f"- Golden set version : `{config['golden_set']['version']}`")
    lignes_md.append(f"- Nombre de questions évaluées : **{len(df)}**\n")

    lignes_md.append("## Vue d'ensemble (KPI globaux)\n")
    lignes_md.append(_df_to_markdown(global_kpi.drop(columns=["niveau"])))

    lignes_md.append("\n## Ventilation par orientation\n")
    lignes_md.append(_df_to_markdown(par_orientation.drop(columns=["niveau"])))

    lignes_md.append("\n## Ventilation par orientation × intention\n")
    lignes_md.append(_df_to_markdown(par_orientation_intention.drop(columns=["niveau"])))

    lignes_md.append("\n## Ventilation par palier\n")
    lignes_md.append(_df_to_markdown(par_palier.drop(columns=["niveau"])))

    lignes_md.append("\n## Alertes (KPI nettement sous la moyenne)\n")
    if alertes:
        lignes_md.append(
            "Ces alertes signalent probablement les défauts de donnée documentés "
            "dans `data_issues.md` (tarif Prime contradictoire, procédure SAV sans "
            "critère d'escalade, unité périmée) :\n"
        )
        lignes_md.extend(alertes)
    else:
        lignes_md.append("Aucune alerte détectée avec le seuil actuel.")

    lignes_md.append(
        "\n## Comment lire ce rapport\n\n"
        "- `intention_correcte` : le routeur a-t-il reconnu la bonne intention ?\n"
        "- `comportement_correct` : l'assistant a-t-il fait ce qui était attendu "
        "(répondre / escalader / demander confirmation) ?\n"
        "- `exactitude` : le fait restitué (tarif, plafond, etc.) est-il correct ?\n"
        "- `couverture_ok` : l'assistant n'a-t-il pas déclaré \"hors périmètre\" à tort ?\n"
        "- `ancrage` : la réponse s'appuie-t-elle uniquement sur les sources récupérées "
        "(jugement LLM, 0 à 1) ?\n"
        "- `pertinence` : la réponse adresse-t-elle la vraie intention (jugement LLM, 0 à 1) ?\n"
        "- `escalade_pertinente` : quand une escalade était due, l'a-t-on bien déclenchée ?\n"
    )

    out_md = config["report"]["markdown"]
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("\n".join(lignes_md) + "\n")

    print(f"Rapport généré : {out_md} (+ {config['report']['csv_kpi']})")
    if alertes:
        print(f"{len(alertes)} alerte(s) détectée(s).")


def _df_to_markdown(df: pd.DataFrame) -> str:
    df_arrondi = df.copy()
    for col in df_arrondi.select_dtypes(include="float").columns:
        df_arrondi[col] = df_arrondi[col].map(lambda v: f"{v:.0%}" if pd.notna(v) else "—")
    try:
        return df_arrondi.to_markdown(index=False)
    except ImportError:
        # Fallback si "tabulate" n'est pas installé : tableau simple en texte.
        return df_arrondi.to_string(index=False)


if __name__ == "__main__":
    main()
