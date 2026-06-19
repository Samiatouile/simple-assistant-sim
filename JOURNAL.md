# Journal des iterations - Fiabilisation assistant "Simple"

Carnet des iterations d'amelioration. Une entree par correction :
constat / diagnostic / action / methode / resultat / enseignement.

---

## Itération 1 - Correction d'un tarif contradictoire (palier Prime)

- **Constat** : exactitude du palier Prime a 43%%, signalee en alerte par le harnais.
- **Diagnostic** : deux unites de connaissance contradictoires pour le tarif Prime (59 DH issu de la fiche tarifaire officielle fiche_tarifs_v3 ; 65 DH issu d'un communique commercial communique_commercial_q3, version 1).
- **Action** : suppression de l'unite non-officielle KB-INF-PRIME-TARIF-B, en conservant la source de verite - principe "une seule version par fait".
- **Methode** : golden set fige, une seule variable modifiee, re-mesure via run-eval + report.
- **Resultat** : exactitude Prime 43%% -> 71%% (+28 pts) ; tarif_palier 70%% -> 90%% ; exactitude globale 71,7%% -> 76,1%%.
- **Enseignement** : un defaut localise de qualite de donnee a un impact mesurable et corrigible. La correction manuelle est temporaire (le defaut est reinjecte par generate-data) ; une correction durable passerait par generate_data.py.

---

## Itération 2 — Ajout d'un critère d'escalade manquant (litige de paiement)

**Date** : 2026-06-19

- **Constat** : escalade pertinente de `support / litige_paiement` à 50 % ; sur les cas graves, l'assistant n'escaladait pas vers un conseiller humain.
- **Diagnostic** : `KB-SUP-LITIGE-PAIEMENT` était la seule procédure SAV sans « CRITERE D'ESCALADE » explicite (contrairement à carte_bloquee, opposition_carte, fraude, compte_bloque). Information *manquante* (et non fausse), simulant une procédure mal mise à jour.
- **Action** : enrichissement de l'unité par un critère d'escalade explicite (montant élevé ou motif suspect → conseiller humain), sur le modèle des autres procédures. Une seule unité modifiée.
- **Méthode** : golden set figé, une seule variable modifiée, re-mesure via run-eval + report, comparaison kpi_ventiles AVANT/APRÈS.
- **Résultat** : escalade `litige_paiement` 50 % → 100 % ; comportement_correct 75 % → 100 %. Répercussion : orientation support escalade 67 % → 75 % et comportement 68 % → 74 % ; escalade globale 67 % → 75 %. Couverture inchangée (75 %).
- **Nuance / limite** : le 100 % d'escalade est en partie un artefact. Le cas Q040 (15 000 DH, commerçant inconnu) est correctement reconnu comme litige et escaladé — vraie réussite. Mais le cas Q041 (formulé de façon vague/paniquée) est escaladé non parce qu'il est reconnu comme litige grave, mais parce que le routeur le classe à tort en « hors périmètre » et que le garde-fou « je ne sais pas → conseiller humain » le rattrape. D'où l'intention restée à 75 % et la couverture à 75 % sur cette intention.
- **Enseignement** : (1) un défaut d'information *manquante* est plus sournois qu'une info fausse — rien ne semble anormal jusqu'au cas limite ; en banque l'escalade non déclenchée est le défaut le plus à risque. (2) Un bon KPI peut masquer un mécanisme défaillant : corriger la donnée (critère d'escalade) et améliorer la reconnaissance d'intention (routeur) sont deux leviers distincts à ne pas confondre.

---

