# simple-assistant-sim

Bac à sable pédagogique : simulateur de l'assistant virtuel d'une néobanque
fictive, **"Simple"**, conçu pour démontrer une démarche de fiabilisation :

```
préparer la donnée  →  mesurer la fiabilité  →  itérer
```

Ce n'est **pas un produit**. Toutes les données (tarifs, procédures,
questions) sont **synthétiques et fictives**. Aucune correspondance avec
une néobanque réelle n'est recherchée ni voulue.

## Contexte métier (fictif)

"Simple" propose 4 paliers freemium : **Go** (0 DH/mois), **Plus**
(19 DH/mois), **Prime** (59 DH/mois), **Metal** (159 DH/mois). Son
assistant virtuel est organisé en 4 **orientations** :

1. **transactionnel** — guide une opération (virement, paiement, carte) ;
2. **informationnel / FAQ** — répond sur offres, tarifs, conditions ;
3. **support / SAV** — traite un incident, escalade si nécessaire ;
4. **onboarding** — prise en main, recommandations selon le profil/palier.

## Installation

```bash
pip install -r requirements.txt
```

Aucune clé API n'est nécessaire pour faire tourner le projet : par défaut,
tout fonctionne en mode **MOCK** (déterministe, hors ligne).

## Commandes CLI

```bash
python -m src.cli generate-data    # génère data/kb.jsonl (base de connaissances)
python -m src.cli build-testset    # génère data/golden_set.jsonl (jeu de test figé)
python -m src.cli run-eval         # fait tourner l'assistant + note les réponses
python -m src.cli report           # produit reports/rapport.md + reports/kpi_ventiles.csv
```

Lancer les 4 commandes dans l'ordre reproduit tout le pipeline de zéro.

## Du MOCK à l'API Anthropic réelle

Par défaut (`config.yaml: model.provider: "auto"`), le projet utilise un
LLM **mock déterministe** (`src/model.py: MockLLM`) — aucune clé requise,
résultats reproductibles d'une exécution à l'autre.

Pour utiliser l'API Anthropic réelle, il suffit de définir une variable
d'environnement, sans modifier une seule ligne de code :

```bash
export ANTHROPIC_API_KEY="sk-..."
# optionnel : choisir le modèle (sinon une valeur par défaut est utilisée)
export ANTHROPIC_MODEL="claude-haiku-4-5"
python -m src.cli run-eval
```

L'abstraction `src/model.py: get_llm_client()` est utilisée à la fois pour
la génération de réponse de l'assistant et pour le LLM-as-judge
(`src/judge.py`) : aucune logique métier ne dépend du provider choisi.

## Comment lire le rapport

Le rapport (`reports/rapport.md`) ne donne jamais une seule moyenne
globale : il **ventile les KPI par orientation, par intention, et par
palier** (`pandas.groupby`), et liste explicitement les groupes dont un
KPI est nettement sous la moyenne dans la section **Alertes**.

Dimensions mesurées :

| KPI | Type de vérification | Ce qu'il mesure |
|---|---|---|
| `intention_correcte` | déterministe | le routeur a-t-il reconnu la bonne intention ? |
| `comportement_correct` | déterministe | répondre / escalader / demander confirmation, comme attendu ? |
| `exactitude` | déterministe | le fait restitué (tarif, plafond...) est-il correct ? |
| `couverture_ok` | déterministe | pas de "hors périmètre" déclaré à tort ? |
| `ancrage` | LLM-as-judge (0/1/2) | la réponse s'appuie-t-elle uniquement sur les sources récupérées ? |
| `pertinence` | LLM-as-judge (0/1/2) | la réponse adresse-t-elle la vraie intention ? |
| `escalade_pertinente` | déterministe | l'escalade a-t-elle bien lieu quand elle est due ? |

Le détail ligne par ligne (une ligne = une question du golden set, avec la
réponse produite et les justifications du juge) est dans
`reports/resultats_detail.csv`.

### Défauts volontairement injectés dans la base de connaissances

Pour démontrer que le harnais détecte bien les problèmes de qualité de
donnée, `data/kb.jsonl` contient 3 défauts documentés dans
`data_issues.md` :

1. un **tarif en double contradictoire** pour le palier Prime (59 DH vs
   65 DH) ;
2. une **procédure SAV sans critère d'escalade explicite** (litige de
   paiement) ;
3. une **unité périmée** toujours présente dans la base (ancien plafond
   de retrait du palier Go).

Le rapport généré fait ressortir ces défauts : par exemple, l'`exactitude`
de l'intention `tarif_palier` / palier `Prime` chute nettement sous la
moyenne globale, et apparaît dans la section Alertes.

## Garde-fous de l'assistant simulé

- **Règle d'or de l'ancrage** : tout fait affirmé doit provenir d'une
  unité de la base de connaissances effectivement récupérée. Si rien de
  pertinent n'est trouvé, l'assistant ne l'invente jamais : il le dit
  explicitement et propose d'orienter vers un conseiller humain.
- **Agent transactionnel** : ne déclenche jamais une opération ; il
  extrait les paramètres, présente un récapitulatif, et demande toujours
  une confirmation explicite.
- **Agent support/SAV** : escalade selon des critères explicites (motifs
  critiques définis dans `config.yaml`, et critères d'escalade documentés
  dans chaque procédure de la base de connaissances).

## Structure du projet

```
src/
  model.py          interface LLM pluggable (MockLLM / AnthropicLLM)
  generate_data.py  génère la base de connaissances synthétique
  build_testset.py  génère le golden set (jeu de requêtes annoté, figé)
  router.py         classifieur orientation / intention / palier (règles)
  retrieval.py       RAG TF-IDF sur la base de connaissances
  assistant.py        les 4 agents + garde-fous
  judge.py             LLM-as-judge (ancrage, pertinence)
  evaluate.py           harnais d'évaluation (vérifications + jugement)
  report.py             agrégation KPI ventilés + rapport
  cli.py                 point d'entrée des 4 commandes
data/
  kb.jsonl            base de connaissances générée
  golden_set.jsonl    golden set généré (figé, versionné)
reports/
  resultats_detail.csv  une ligne par question évaluée
  kpi_ventiles.csv       KPI agrégés (global / orientation / intention / palier)
  rapport.md              rapport de fiabilité lisible
config.yaml            paramètres versionnés (version de KB, retrieval, modèle...)
data_issues.md         documentation des défauts injectés dans la KB
```

## Philosophie : une variable à la fois, jeu de test figé

Le **golden set est figé** (`data/golden_set.jsonl`, versionné dans
`config.yaml: golden_set.version`) : on ne le régénère pas entre deux
mesures que l'on veut comparer, sinon on ne compare plus la même chose.

De la même façon, pour observer l'effet d'un changement (ex : améliorer le
retrieval, corriger un défaut de la KB, changer un prompt), on ne change
**qu'une seule variable à la fois**, on relance `run-eval` + `report`, et
on compare les deux `kpi_ventiles.csv` obtenus. C'est cette discipline qui
rend la mesure de fiabilité utile et actionnable, plutôt qu'un chiffre
isolé sans levier d'amélioration clair.

À chaque `report`, le `reports/kpi_ventiles.csv` courant est automatiquement
sauvegardé dans `reports/kpi_ventiles_precedent.csv` *avant* d'être écrasé
par la nouvelle mesure : aucune copie manuelle n'est nécessaire pour
comparer une itération à la précédente.

```
python -m src.cli log-iteration    # compare kpi_ventiles.csv (courant) à
                                    # kpi_ventiles_precedent.csv (précédent),
                                    # et journalise le delta dans JOURNAL.md
```

S'il n'existe pas encore de `reports/kpi_ventiles_precedent.csv` (toute
première mesure), `log-iteration` l'indique clairement plutôt que de
comparer du vide.
