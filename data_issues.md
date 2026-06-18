# Défauts volontairement injectés dans la base de connaissances

Ce fichier documente les défauts réalistes injectés dans `data/kb.jsonl`
par `src/generate_data.py`. Le but est pédagogique : le harnais
d'évaluation (`src/evaluate.py` + `src/report.py`) doit être capable de
faire ressortir ces défauts dans le rapport de fiabilité, via une
dimension dégradée (exactitude et/ou ancrage) sur l'orientation
concernée.

## 1. Tarif Prime en double, avec deux versions contradictoires

- `KB-INF-PRIME-TARIF-A` (source `fiche_tarifs_v3`, version 3) : 59 DH/mois.
- `KB-INF-PRIME-TARIF-B` (source `communique_commercial_q3`, version 1) : 65 DH/mois.

Deux unités valides en même temps, avec des montants différents pour le
même palier. C'est le cas classique de documentation commerciale et
documentation tarifaire officielle qui divergent. Le golden set contient
une question sur le tarif Prime dont la `reponse_attendue` est 59 DH (la
source la plus récente / la plus officielle). Si la récupération RAG pioche
la mauvaise unité, l'assistant répondra 65 DH : la vérification
déterministe d'exactitude des tarifs (`evaluate.py`) doit faire chuter le
KPI "exactitude" de l'orientation `informationnel` / intention
`tarif_palier`.

## 2. Procédure SAV sans critère d'escalade explicite

`KB-SUP-LITIGE-PAIEMENT` est la seule procédure de l'orientation `support`
qui ne définit aucun "CRITERE D'ESCALADE", contrairement à
`KB-SUP-CARTE-BLOQUEE`, `KB-SUP-OPPOSITION-CARTE`, `KB-SUP-FRAUDE` et
`KB-SUP-COMPTE-BLOQUE`. Cela simule une procédure mal rédigée ou oubliée
lors d'une mise à jour de la documentation SAV. Dans le golden set, les cas
limites de litige de paiement grave (montant très élevé, motif suspect)
doivent normalement être escaladés ; comme la source ne le précise pas
explicitement, l'assistant peut échouer à escalader. Cela doit faire
chuter le KPI "escalade pertinente" de l'orientation `support`.

## 3. Unité périmée toujours présente dans la base

`KB-INF-GO-PLAFOND-OLD` indique un plafond de retrait de 1500 DH pour le
palier Go, avec une `date_validite` au 1er janvier 2024 (donc périmée),
alors que `KB-INF-GO-PLAFOND` (valide jusqu'en 2026) indique 2000 DH. La
base de connaissances n'a pas été nettoyée des anciennes versions. Si le
retrieval (TF-IDF) ramène l'unité périmée plutôt que l'unité à jour,
l'assistant répond avec une information obsolète : cela doit faire chuter
le KPI "exactitude" sur l'intention `plafond_retrait`.

## Pourquoi ne pas corriger ces défauts dans `generate_data.py` ?

Ils sont injectés intentionnellement et ne doivent PAS être corrigés sans
créer une nouvelle version de la KB (`config.yaml: kb.version`). Le but du
simulateur est justement de démontrer qu'un harnais de mesure de fiabilité
bien construit permet de détecter ce type de problème de qualité de
donnée AVANT qu'il n'impacte les utilisateurs réels.
