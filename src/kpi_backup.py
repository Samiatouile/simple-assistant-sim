"""Petite fonction utilitaire : sauvegarde le KPI courant en "précédent"
avant qu'il ne soit écrasé, pour permettre la comparaison d'une itération
à l'autre (utilisée par `report` et lue par `log-iteration`).
"""
import os
import shutil


def backup_kpi(chemin_courant: str, chemin_precedent: str) -> bool:
    """Copie `chemin_courant` vers `chemin_precedent` s'il existe.

    Renvoie True si une sauvegarde a été faite, False si aucun fichier
    courant n'existait encore (donc rien à comparer pour l'instant).
    """
    if os.path.exists(chemin_courant):
        shutil.copyfile(chemin_courant, chemin_precedent)
        return True
    return False
