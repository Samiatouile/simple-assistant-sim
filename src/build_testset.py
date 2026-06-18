"""Génère le golden set : le jeu de requêtes annotées servant de vérité
terrain à la mesure de fiabilité (`src/evaluate.py`).

IMPORTANT : ce jeu est FIGÉ une fois généré. On ne le régénère pas entre
deux mesures que l'on souhaite comparer (sinon on ne compare plus la même
chose). Si l'on doit le faire évoluer, on incrémente
`config.yaml: golden_set.version` et on documente le changement.

Chaque entrée :
    id, question, orientation, intention, palier, reponse_attendue,
    source_attendue, comportement_attendu, difficulte, langue

comportement_attendu ∈ {"repondre", "escalader", "demander_confirmation"}
"""
import json
import os

GOLDEN_PATH = "data/golden_set.jsonl"

_counter = {"n": 0}


def _q(question, orientation, intention, palier, reponse_attendue,
       source_attendue, comportement_attendu, difficulte, langue):
    _counter["n"] += 1
    return {
        "id": f"Q{_counter['n']:03d}",
        "question": question,
        "orientation": orientation,
        "intention": intention,
        "palier": palier,
        "reponse_attendue": reponse_attendue,
        "source_attendue": source_attendue,
        "comportement_attendu": comportement_attendu,
        "difficulte": difficulte,
        "langue": langue,
    }


def build_testset():
    qs = []

    # ==================================================================
    # INFORMATIONNEL — tarif_palier
    # ==================================================================
    qs.append(_q("Combien coûte le palier Go par mois ?", "informationnel", "tarif_palier", "Go",
                 "0 DH", "KB-INF-GO-TARIF", "repondre", "facile", "fr"))
    qs.append(_q("C'est gratuit Go ou pas ?", "informationnel", "tarif_palier", "Go",
                 "0 DH", "KB-INF-GO-TARIF", "repondre", "facile", "fr"))
    qs.append(_q("Chhal taman dial Go fchhar ?", "informationnel", "tarif_palier", "Go",
                 "0 DH", "KB-INF-GO-TARIF", "repondre", "moyen", "darija_latin"))
    qs.append(_q("Quel est le tarif mensuel du palier Plus ?", "informationnel", "tarif_palier", "Plus",
                 "19 DH", "KB-INF-PLUS-TARIF", "repondre", "facile", "fr"))
    qs.append(_q("Le forfait Plus coute kombyen?", "informationnel", "tarif_palier", "Plus",
                 "19 DH", "KB-INF-PLUS-TARIF", "repondre", "moyen", "fr"))
    qs.append(_q("Quel est le prix du palier Prime ?", "informationnel", "tarif_palier", "Prime",
                 "59 DH", "KB-INF-PRIME-TARIF-A", "repondre", "moyen", "fr"))
    qs.append(_q("Combien je paye chaque mois avec Prime ?", "informationnel", "tarif_palier", "Prime",
                 "59 DH", "KB-INF-PRIME-TARIF-A", "repondre", "moyen", "fr"))
    qs.append(_q("Chhal kayji Prime fl mois ?", "informationnel", "tarif_palier", "Prime",
                 "59 DH", "KB-INF-PRIME-TARIF-A", "repondre", "difficile", "darija_latin"))
    qs.append(_q("Quel est le tarif du palier Metal ?", "informationnel", "tarif_palier", "Metal",
                 "159 DH", "KB-INF-METAL-TARIF", "repondre", "facile", "fr"))
    qs.append(_q("Le pack Metal il coute cher non? donne moi le prix exact", "informationnel", "tarif_palier", "Metal",
                 "159 DH", "KB-INF-METAL-TARIF", "repondre", "facile", "fr"))

    # ==================================================================
    # INFORMATIONNEL — plafond_retrait
    # ==================================================================
    qs.append(_q("Quel est le plafond de retrait avec le palier Go ?", "informationnel", "plafond_retrait", "Go",
                 "2000 DH", "KB-INF-GO-PLAFOND", "repondre", "moyen", "fr"))
    qs.append(_q("Combien je peux retirer max par mois en Go ?", "informationnel", "plafond_retrait", "Go",
                 "2000 DH", "KB-INF-GO-PLAFOND", "repondre", "moyen", "fr"))
    qs.append(_q("Chhal n9der nrtire flouss b Go fchhar ?", "informationnel", "plafond_retrait", "Go",
                 "2000 DH", "KB-INF-GO-PLAFOND", "repondre", "difficile", "darija_latin"))
    qs.append(_q("Quel est le plafond de retrait du palier Plus ?", "informationnel", "plafond_retrait", "Plus",
                 "5000 DH", "KB-INF-PLUS-PLAFOND", "repondre", "facile", "fr"))
    qs.append(_q("Y a-t-il un plafond de retrait avec Prime ?", "informationnel", "plafond_retrait", "Prime",
                 "pas de plafond", "KB-INF-PRIME-PLAFOND", "repondre", "facile", "fr"))
    qs.append(_q("Le plafond de retrait Metal a l'etranger c'est combien ?", "informationnel", "plafond_retrait", "Metal",
                 "pas de plafond", "KB-INF-METAL-PLAFOND", "repondre", "moyen", "fr"))

    # ==================================================================
    # INFORMATIONNEL — frais_virement
    # ==================================================================
    qs.append(_q("Un virement vers une autre banque coute combien en Go ?", "informationnel", "frais_virement", "Go",
                 "4 DH", "KB-INF-GO-VIREMENT", "repondre", "moyen", "fr"))
    qs.append(_q("Virement vers Simple gratuit en Go ?", "informationnel", "frais_virement", "Go",
                 "gratuit", "KB-INF-GO-VIREMENT", "repondre", "facile", "fr"))
    qs.append(_q("Les virements sont gratuits avec Plus ?", "informationnel", "frais_virement", "Plus",
                 "gratuit", "KB-INF-PLUSPRIMEMETAL-VIREMENT", "repondre", "facile", "fr"))
    qs.append(_q("Est-ce que je paye des frais de virement avec Prime ?", "informationnel", "frais_virement", "Prime",
                 "gratuit", "KB-INF-PLUSPRIMEMETAL-VIREMENT", "repondre", "facile", "fr"))
    qs.append(_q("Virement b Metal khass thelsi ?", "informationnel", "frais_virement", "Metal",
                 "gratuit", "KB-INF-PLUSPRIMEMETAL-VIREMENT", "repondre", "moyen", "darija_latin"))

    # ==================================================================
    # INFORMATIONNEL — changer_palier
    # ==================================================================
    qs.append(_q("Comment changer de palier ?", "informationnel", "changer_palier", None,
                 "depuis Profil > Mon abonnement", "KB-INF-CHANGEMENT-PALIER", "repondre", "facile", "fr"))
    qs.append(_q("Je veux passer de Go a Prime, comment faire ?", "informationnel", "changer_palier", None,
                 "depuis Profil > Mon abonnement", "KB-INF-CHANGEMENT-PALIER", "repondre", "moyen", "fr"))
    qs.append(_q("Kifach nbeddel min Go l Plus ?", "informationnel", "changer_palier", None,
                 "depuis Profil > Mon abonnement", "KB-INF-CHANGEMENT-PALIER", "repondre", "difficile", "darija_latin"))

    # ==================================================================
    # INFORMATIONNEL — eligibilite_palier
    # ==================================================================
    qs.append(_q("Qui peut prendre le palier Metal ?", "informationnel", "eligibilite_palier", "Metal",
                 "majeur, compte actif depuis 3 mois", "KB-INF-ELIGIBILITE-METAL", "repondre", "moyen", "fr"))
    qs.append(_q("Est-ce que je suis eligible a Metal si j'ai ouvert mon compte hier ?", "informationnel",
                 "eligibilite_palier", "Metal", "non, il faut 3 mois d'ancienneté",
                 "KB-INF-ELIGIBILITE-METAL", "repondre", "difficile", "fr"))
    qs.append(_q("Conditions pour avoir la carte Metal ?", "informationnel", "eligibilite_palier", "Metal",
                 "majeur, compte actif depuis 3 mois", "KB-INF-ELIGIBILITE-METAL", "repondre", "moyen", "fr"))

    # ==================================================================
    # SUPPORT — carte_bloquee
    # ==================================================================
    qs.append(_q("Ma carte est bloquee apres 3 mauvais codes, que faire ?", "support", "carte_bloquee", None,
                 "débloquer depuis Carte > Débloquer", "KB-SUP-CARTE-BLOQUEE", "repondre", "facile", "fr"))
    qs.append(_q("Comment debloquer ma carte ?", "support", "carte_bloquee", None,
                 "débloquer depuis Carte > Débloquer", "KB-SUP-CARTE-BLOQUEE", "repondre", "facile", "fr"))
    qs.append(_q("Carti dyali masdouda, kifach ndebloquiha ?", "support", "carte_bloquee", None,
                 "débloquer depuis Carte > Débloquer", "KB-SUP-CARTE-BLOQUEE", "repondre", "difficile", "darija_latin"))

    # ==================================================================
    # SUPPORT — opposition_carte
    # ==================================================================
    qs.append(_q("J'ai perdu ma carte, comment faire opposition ?", "support", "opposition_carte", None,
                 "Carte > Faire opposition", "KB-SUP-OPPOSITION-CARTE", "repondre", "facile", "fr"))
    qs.append(_q("Ma carte a ete volee, je fais comment ?", "support", "opposition_carte", None,
                 "Carte > Faire opposition", "KB-SUP-OPPOSITION-CARTE", "repondre", "facile", "fr"))
    qs.append(_q("J'ai perdu ma carte a l'etranger pendant un voyage, aidez moi", "support", "opposition_carte", None,
                 "escalade vers un conseiller", "KB-SUP-OPPOSITION-CARTE", "escalader", "difficile", "fr"))
    qs.append(_q("Ma carte a ete volee a l'etranger et quelqu'un l'utilise", "support", "opposition_carte", None,
                 "escalade vers un conseiller", "KB-SUP-OPPOSITION-CARTE", "escalader", "difficile", "fr"))

    # ==================================================================
    # SUPPORT — fraude
    # ==================================================================
    qs.append(_q("Je vois une transaction que je n'ai pas faite sur mon compte", "support", "fraude", None,
                 "escalade vers un conseiller", "KB-SUP-FRAUDE", "escalader", "moyen", "fr"))
    qs.append(_q("On a pirate mon compte je crois, il y a des paiements bizarres", "support", "fraude", None,
                 "escalade vers un conseiller", "KB-SUP-FRAUDE", "escalader", "difficile", "fr"))
    qs.append(_q("Chi 7ad sra9 flousi mn compte dyali", "support", "fraude", None,
                 "escalade vers un conseiller", "KB-SUP-FRAUDE", "escalader", "difficile", "darija_latin"))

    # ==================================================================
    # SUPPORT — litige_paiement
    # ==================================================================
    qs.append(_q("Un commerçant m'a facture 2 fois le meme achat, comment contester ?", "support",
                 "litige_paiement", None, "Paiements > Contester un paiement",
                 "KB-SUP-LITIGE-PAIEMENT", "repondre", "moyen", "fr"))
    qs.append(_q("Je ne reconnais pas un paiement de 30 DH, comment faire un litige ?", "support",
                 "litige_paiement", None, "Paiements > Contester un paiement",
                 "KB-SUP-LITIGE-PAIEMENT", "repondre", "moyen", "fr"))
    qs.append(_q("J'ai un paiement conteste de 15000 DH chez un commercant que je ne connais pas du tout, "
                 "je pense que c'est grave", "support", "litige_paiement", None,
                 "escalade vers un conseiller", "KB-SUP-LITIGE-PAIEMENT", "escalader", "difficile", "fr"))
    qs.append(_q("Paiement enorme et suspect sur mon compte, montant tres eleve, je panique", "support",
                 "litige_paiement", None, "escalade vers un conseiller",
                 "KB-SUP-LITIGE-PAIEMENT", "escalader", "difficile", "fr"))

    # ==================================================================
    # SUPPORT — compte_bloque
    # ==================================================================
    qs.append(_q("Mon compte est bloque depuis ce matin, que dois-je faire ?", "support", "compte_bloque", None,
                 "escalade vers un conseiller", "KB-SUP-COMPTE-BLOQUE", "escalader", "moyen", "fr"))
    qs.append(_q("Compte dyali masdoud, 3afak chnahowa lmochkil ?", "support", "compte_bloque", None,
                 "escalade vers un conseiller", "KB-SUP-COMPTE-BLOQUE", "escalader", "difficile", "darija_latin"))

    # ==================================================================
    # SUPPORT — hors périmètre
    # ==================================================================
    qs.append(_q("Pouvez-vous m'aider a declarer mes impots sur le revenu ?", "support", "hors_perimetre", None,
                 "escalade vers un conseiller", None, "escalader", "difficile", "fr"))
    qs.append(_q("Quel est le cours de l'action Simple en bourse aujourd'hui ?", "support", "hors_perimetre", None,
                 "escalade vers un conseiller", None, "escalader", "difficile", "fr"))
    qs.append(_q("Pouvez-vous me recommander un avocat pour mon divorce ?", "support", "hors_perimetre", None,
                 "escalade vers un conseiller", None, "escalader", "difficile", "fr"))

    # ==================================================================
    # ONBOARDING — ouverture_compte
    # ==================================================================
    qs.append(_q("Comment ouvrir un compte Simple ?", "onboarding", "ouverture_compte", None,
                 "100% en ligne en 3 étapes", "KB-ONB-OUVERTURE-COMPTE", "repondre", "facile", "fr"))
    qs.append(_q("C'est long pour ouvrir un compte chez vous ?", "onboarding", "ouverture_compte", None,
                 "moins de 10 minutes", "KB-ONB-OUVERTURE-COMPTE", "repondre", "facile", "fr"))
    qs.append(_q("Kifach n7el compte f Simple ?", "onboarding", "ouverture_compte", None,
                 "100% en ligne en 3 étapes", "KB-ONB-OUVERTURE-COMPTE", "repondre", "difficile", "darija_latin"))

    # ==================================================================
    # ONBOARDING — premiere_utilisation
    # ==================================================================
    qs.append(_q("Comment faire mon premier virement ?", "onboarding", "premiere_utilisation", None,
                 "ajouter un bénéficiaire puis virement", "KB-ONB-PREMIER-VIREMENT", "repondre", "facile", "fr"))
    qs.append(_q("Je viens de creer mon compte, comment envoyer de l'argent a un ami ?", "onboarding",
                 "premiere_utilisation", None, "ajouter un bénéficiaire puis virement",
                 "KB-ONB-PREMIER-VIREMENT", "repondre", "moyen", "fr"))
    qs.append(_q("Kifach ndir l virement lawal dyali ?", "onboarding", "premiere_utilisation", None,
                 "ajouter un bénéficiaire puis virement", "KB-ONB-PREMIER-VIREMENT", "repondre", "difficile", "darija_latin"))

    # ==================================================================
    # ONBOARDING — service_eligible
    # ==================================================================
    qs.append(_q("Est-ce que j'ai acces a l'epargne avec Plus ?", "onboarding", "service_eligible", "Plus",
                 "oui, après 1 mois d'ancienneté", "KB-ONB-ELIGIBLE-EPARGNE", "repondre", "moyen", "fr"))
    qs.append(_q("Je suis en Prime, je peux ouvrir une epargne remuneree ?", "onboarding", "service_eligible", "Prime",
                 "oui, après 1 mois d'ancienneté", "KB-ONB-ELIGIBLE-EPARGNE", "repondre", "moyen", "fr"))
    qs.append(_q("Le micro-credit instantane c'est pour quel palier ?", "onboarding", "service_eligible", "Prime",
                 "Prime et Metal, 3 mois d'historique", "KB-ONB-ELIGIBLE-CREDIT", "repondre", "moyen", "fr"))
    qs.append(_q("Je suis client Metal depuis 4 mois, je peux avoir un credit instantane ?", "onboarding",
                 "service_eligible", "Metal", "oui, Prime et Metal, 3 mois d'historique",
                 "KB-ONB-ELIGIBLE-CREDIT", "repondre", "difficile", "fr"))
    qs.append(_q("Je suis en Go, j'ai acces a l'epargne ?", "onboarding", "service_eligible", "Go",
                 "non, il faut un palier supérieur", "KB-ONB-ELIGIBLE-GO", "repondre", "moyen", "fr"))
    qs.append(_q("Avec Go j'ai access a quoi exactement ?", "onboarding", "service_eligible", "Go",
                 "fonctionnalités de base uniquement", "KB-ONB-ELIGIBLE-GO", "repondre", "moyen", "fr"))

    # ==================================================================
    # TRANSACTIONNEL — virement
    # ==================================================================
    qs.append(_q("Fais un virement de 500 DH a Karim", "transactionnel", "virement", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-VIREMENT", "demander_confirmation", "facile", "fr"))
    qs.append(_q("Je veux envoyer 1200 DH a ma soeur Sara", "transactionnel", "virement", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-VIREMENT", "demander_confirmation", "facile", "fr"))
    qs.append(_q("Vire 300dh chez Yassine s'il te plait", "transactionnel", "virement", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-VIREMENT", "demander_confirmation", "moyen", "fr"))
    qs.append(_q("Sift li Mehdi 250 DH daba", "transactionnel", "virement", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-VIREMENT", "demander_confirmation", "difficile", "darija_latin"))

    # ==================================================================
    # TRANSACTIONNEL — paiement
    # ==================================================================
    qs.append(_q("Paye 89 DH chez le commercant AutoMaroc", "transactionnel", "paiement", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-PAIEMENT", "demander_confirmation", "facile", "fr"))
    qs.append(_q("Je veux payer ma facture d'electricite de 220 DH", "transactionnel", "paiement", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-PAIEMENT", "demander_confirmation", "moyen", "fr"))
    qs.append(_q("Khelles li 150dh l boulangerie", "transactionnel", "paiement", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-PAIEMENT", "demander_confirmation", "difficile", "darija_latin"))

    # ==================================================================
    # TRANSACTIONNEL — gestion_carte
    # ==================================================================
    qs.append(_q("Bloque ma carte tout de suite", "transactionnel", "gestion_carte", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-CARTE-GESTION", "demander_confirmation", "facile", "fr"))
    qs.append(_q("Augmente mon plafond de carte a 8000 DH", "transactionnel", "gestion_carte", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-CARTE-GESTION", "demander_confirmation", "moyen", "fr"))
    qs.append(_q("Sdoud li carte daba 3afak", "transactionnel", "gestion_carte", None,
                 "récapitulatif + demande de confirmation", "KB-TRX-CARTE-GESTION", "demander_confirmation", "difficile", "darija_latin"))

    return qs


def main():
    qs = build_testset()
    os.makedirs(os.path.dirname(GOLDEN_PATH), exist_ok=True)
    with open(GOLDEN_PATH, "w", encoding="utf-8") as f:
        for q in qs:
            f.write(json.dumps(q, ensure_ascii=False) + "\n")
    print(f"Golden set généré : {GOLDEN_PATH} ({len(qs)} questions).")


if __name__ == "__main__":
    main()
