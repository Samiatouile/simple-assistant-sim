# Rapport de fiabilité — assistant virtuel "Simple"

- KB version : `1.0.0`
- Golden set version : `1.0.0`
- Nombre de questions évaluées : **68**

## Vue d'ensemble (KPI globaux)

| _global          |   n | intention_correcte   | comportement_correct   | exactitude   | couverture_ok   | ancrage   | pertinence   | escalade_pertinente   |
|:-----------------|----:|:---------------------|:-----------------------|:-------------|:----------------|:----------|:-------------|:----------------------|
| toutes questions |  68 | 88%                  | 85%                    | 72%          | 96%             | 100%      | 100%         | 67%                   |

## Ventilation par orientation

| orientation    |   n | intention_correcte   | comportement_correct   | exactitude   | couverture_ok   | ancrage   | pertinence   | escalade_pertinente   |
|:---------------|----:|:---------------------|:-----------------------|:-------------|:----------------|:----------|:-------------|:----------------------|
| informationnel |  27 | 85%                  | 93%                    | 70%          | 100%            | 100%      | 100%         | —                     |
| onboarding     |  12 | 100%                 | 92%                    | 75%          | 100%            | 100%      | 100%         | —                     |
| support        |  19 | 84%                  | 68%                    | 71%          | 84%             | 100%      | 100%         | 67%                   |
| transactionnel |  10 | 90%                  | 90%                    | —            | 100%            | 100%      | 100%         | —                     |

## Ventilation par orientation × intention

| orientation    | intention            |   n | intention_correcte   | comportement_correct   | exactitude   | couverture_ok   | ancrage   | pertinence   | escalade_pertinente   |
|:---------------|:---------------------|----:|:---------------------|:-----------------------|:-------------|:----------------|:----------|:-------------|:----------------------|
| informationnel | changer_palier       |   3 | 100%                 | 67%                    | 67%          | 100%            | 100%      | 100%         | —                     |
| informationnel | eligibilite_palier   |   3 | 100%                 | 100%                   | 100%         | 100%            | 100%      | 100%         | —                     |
| informationnel | frais_virement       |   5 | 40%                  | 100%                   | 80%          | 100%            | 100%      | 100%         | —                     |
| informationnel | plafond_retrait      |   6 | 100%                 | 100%                   | 50%          | 100%            | 100%      | 100%         | —                     |
| informationnel | tarif_palier         |  10 | 90%                  | 90%                    | 70%          | 100%            | 100%      | 100%         | —                     |
| onboarding     | ouverture_compte     |   3 | 100%                 | 100%                   | 67%          | 100%            | 100%      | 100%         | —                     |
| onboarding     | premiere_utilisation |   3 | 100%                 | 100%                   | 100%         | 100%            | 100%      | 100%         | —                     |
| onboarding     | service_eligible     |   6 | 100%                 | 83%                    | 67%          | 100%            | 100%      | 100%         | —                     |
| support        | carte_bloquee        |   3 | 100%                 | 67%                    | 67%          | 100%            | 100%      | 100%         | —                     |
| support        | compte_bloque        |   2 | 100%                 | 0%                     | —            | 100%            | 100%      | 100%         | 0%                    |
| support        | fraude               |   3 | 100%                 | 67%                    | —            | 100%            | 100%      | 100%         | 67%                   |
| support        | hors_perimetre       |   3 | 100%                 | 100%                   | —            | 100%            | 100%      | 100%         | 100%                  |
| support        | litige_paiement      |   4 | 75%                  | 75%                    | 100%         | 75%             | 100%      | 100%         | 50%                   |
| support        | opposition_carte     |   4 | 50%                  | 75%                    | 50%          | 50%             | 100%      | 100%         | 100%                  |
| transactionnel | gestion_carte        |   3 | 67%                  | 67%                    | —            | 100%            | 100%      | 100%         | —                     |
| transactionnel | paiement             |   3 | 100%                 | 100%                   | —            | 100%            | —         | —            | —                     |
| transactionnel | virement             |   4 | 100%                 | 100%                   | —            | 100%            | —         | —            | —                     |

## Ventilation par palier

| palier   |   n | intention_correcte   | comportement_correct   | exactitude   | couverture_ok   | ancrage   | pertinence   | escalade_pertinente   |
|:---------|----:|:---------------------|:-----------------------|:-------------|:----------------|:----------|:-------------|:----------------------|
| Go       |  10 | 80%                  | 100%                   | 60%          | 100%            | 100%      | 100%         | —                     |
| Metal    |   8 | 100%                 | 88%                    | 88%          | 100%            | 100%      | 100%         | —                     |
| Plus     |   5 | 80%                  | 100%                   | 100%         | 100%            | 100%      | 100%         | —                     |
| Prime    |   7 | 86%                  | 86%                    | 43%          | 100%            | 100%      | 100%         | —                     |
| nan      |  38 | 89%                  | 79%                    | 75%          | 92%             | 100%      | 100%         | 67%                   |

## Alertes (KPI nettement sous la moyenne)

Ces alertes signalent probablement les défauts de donnée documentés dans `data_issues.md` (tarif Prime contradictoire, procédure SAV sans critère d'escalade, unité périmée) :

- **intention_correcte** dégradé pour orientation=`informationnel` / intention=`frais_virement` : 40% (moyenne globale : 90%)
- **intention_correcte** dégradé pour orientation=`support` / intention=`opposition_carte` : 50% (moyenne globale : 90%)
- **intention_correcte** dégradé pour orientation=`transactionnel` / intention=`gestion_carte` : 67% (moyenne globale : 90%)
- **comportement_correct** dégradé pour orientation=`informationnel` / intention=`changer_palier` : 67% (moyenne globale : 82%)
- **comportement_correct** dégradé pour orientation=`support` / intention=`carte_bloquee` : 67% (moyenne globale : 82%)
- **comportement_correct** dégradé pour orientation=`support` / intention=`compte_bloque` : 0% (moyenne globale : 82%)
- **comportement_correct** dégradé pour orientation=`support` / intention=`fraude` : 67% (moyenne globale : 82%)
- **comportement_correct** dégradé pour orientation=`transactionnel` / intention=`gestion_carte` : 67% (moyenne globale : 82%)
- **exactitude** dégradé pour orientation=`informationnel` / intention=`plafond_retrait` : 50% (moyenne globale : 74%)
- **exactitude** dégradé pour orientation=`support` / intention=`opposition_carte` : 50% (moyenne globale : 74%)
- **couverture_ok** dégradé pour orientation=`support` / intention=`opposition_carte` : 50% (moyenne globale : 96%)
- **escalade_pertinente** dégradé pour orientation=`support` / intention=`compte_bloque` : 0% (moyenne globale : 63%)

## Comment lire ce rapport

- `intention_correcte` : le routeur a-t-il reconnu la bonne intention ?
- `comportement_correct` : l'assistant a-t-il fait ce qui était attendu (répondre / escalader / demander confirmation) ?
- `exactitude` : le fait restitué (tarif, plafond, etc.) est-il correct ?
- `couverture_ok` : l'assistant n'a-t-il pas déclaré "hors périmètre" à tort ?
- `ancrage` : la réponse s'appuie-t-elle uniquement sur les sources récupérées (jugement LLM, 0 à 1) ?
- `pertinence` : la réponse adresse-t-elle la vraie intention (jugement LLM, 0 à 1) ?
- `escalade_pertinente` : quand une escalade était due, l'a-t-on bien déclenchée ?

