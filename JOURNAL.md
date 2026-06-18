# Journal des iterations - Fiabilisation assistant "Simple"

Carnet des iterations d'amelioration. Une entree par correction :
constat / diagnostic / action / methode / resultat / enseignement.

---

## Iteration 1 - Correction d'un tarif contradictoire (palier Prime)

- **Constat** : exactitude du palier Prime a 43%%, signalee en alerte par le harnais.
- **Diagnostic** : deux unites de connaissance contradictoires pour le tarif Prime (59 DH issu de la fiche tarifaire officielle fiche_tarifs_v3 ; 65 DH issu d'un communique commercial communique_commercial_q3, version 1).
- **Action** : suppression de l'unite non-officielle KB-INF-PRIME-TARIF-B, en conservant la source de verite - principe "une seule version par fait".
- **Methode** : golden set fige, une seule variable modifiee, re-mesure via run-eval + report.
- **Resultat** : exactitude Prime 43%% -> 71%% (+28 pts) ; tarif_palier 70%% -> 90%% ; exactitude globale 71,7%% -> 76,1%%.
- **Enseignement** : un defaut localise de qualite de donnee a un impact mesurable et corrigible. La correction manuelle est temporaire (le defaut est reinjecte par generate-data) ; une correction durable passerait par generate_data.py.
## Itération 1 — [À COMPLÉTER]

**Date** : 2026-06-18

### Résultat (auto)

Aucun changement significatif détecté entre les deux mesures.

### Constat

### Diagnostic

### Action

### Enseignement

---

