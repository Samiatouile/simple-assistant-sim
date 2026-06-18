"""Génère la base de connaissances (KB) synthétique de "Simple".

La KB est la SOURCE DE VÉRITÉ de l'assistant : chaque réponse factuelle
doit pouvoir être tracée jusqu'à une unité de cette base (règle d'or de
l'ancrage, voir assistant.py).

Toutes les données sont FICTIVES. Aucune correspondance avec une néobanque
réelle n'est recherchée ni voulue.

Conformément au cahier des charges pédagogique, on injecte VOLONTAIREMENT
quelques défauts réalistes (documentés dans data_issues.md) :
  1. un tarif en double, avec deux versions contradictoires
     (KB-INF-PRIME-TARIF-A vs KB-INF-PRIME-TARIF-B) ;
  2. une procédure SAV sans critère d'escalade explicite
     (KB-SUP-LITIGE-PAIEMENT, contrairement aux autres procédures SAV) ;
  3. une unité périmée (date_validite dans le passé) toujours présente
     dans la base (KB-INF-GO-PLAFOND-OLD).
"""
import json
import os

KB_PATH = "data/kb.jsonl"


def _unit(id_, orientation, intention, palier, texte, source, date_validite, version):
    return {
        "id": id_,
        "orientation": orientation,
        "intention": intention,
        "palier": palier,
        "texte": texte,
        "source": source,
        "date_validite": date_validite,
        "version": version,
    }


def build_kb():
    units = []

    # ------------------------------------------------------------------
    # INFORMATIONNEL — tarifs et avantages des 4 paliers
    # ------------------------------------------------------------------
    units.append(_unit(
        "KB-INF-GO-TARIF", "informationnel", "tarif_palier", "Go",
        "Le palier Go est gratuit : 0 DH/mois. Il inclut une carte virtuelle "
        "et 3 retraits gratuits par mois en distributeur Simple.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))
    units.append(_unit(
        "KB-INF-PLUS-TARIF", "informationnel", "tarif_palier", "Plus",
        "Le palier Plus coûte 19 DH/mois. Il inclut une carte physique, "
        "10 retraits gratuits par mois et l'assurance achats en ligne.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))
    # Défaut injecté n°1a : tarif Prime version A (voir data_issues.md)
    units.append(_unit(
        "KB-INF-PRIME-TARIF-A", "informationnel", "tarif_palier", "Prime",
        "Le palier Prime coûte 59 DH/mois. Il inclut des retraits illimités, "
        "une carte premium et une assurance voyage.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))
    # Défaut injecté n°1b : tarif Prime version B, contradictoire (montant différent)
    units.append(_unit(
        "KB-INF-PRIME-TARIF-B", "informationnel", "tarif_palier", "Prime",
        "Le palier Prime coûte 65 DH/mois et inclut des retraits illimités "
        "ainsi qu'une carte premium.",
        "communique_commercial_q3", "2026-12-31", "1",
    ))
    units.append(_unit(
        "KB-INF-METAL-TARIF", "informationnel", "tarif_palier", "Metal",
        "Le palier Metal coûte 159 DH/mois. Il inclut une carte en métal, "
        "des retraits illimités dans le monde entier, une assurance voyage "
        "premium et un conseiller dédié.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))

    # Plafonds et frais par palier
    units.append(_unit(
        "KB-INF-GO-PLAFOND", "informationnel", "plafond_retrait", "Go",
        "Avec le palier Go, le plafond de retrait est de 2000 DH par mois. "
        "Au-delà, des frais de 5 DH par retrait supplémentaire s'appliquent.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))
    # Défaut injecté n°3 : unité périmée toujours présente dans la base
    units.append(_unit(
        "KB-INF-GO-PLAFOND-OLD", "informationnel", "plafond_retrait", "Go",
        "Avec le palier Go, le plafond de retrait est de 1500 DH par mois.",
        "fiche_tarifs_v1", "2024-01-01", "1",
    ))
    units.append(_unit(
        "KB-INF-PLUS-PLAFOND", "informationnel", "plafond_retrait", "Plus",
        "Avec le palier Plus, le plafond de retrait est de 5000 DH par mois, "
        "sans frais supplémentaires.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))
    units.append(_unit(
        "KB-INF-PRIME-PLAFOND", "informationnel", "plafond_retrait", "Prime",
        "Avec le palier Prime, il n'y a pas de plafond de retrait mensuel.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))
    units.append(_unit(
        "KB-INF-METAL-PLAFOND", "informationnel", "plafond_retrait", "Metal",
        "Avec le palier Metal, il n'y a pas de plafond de retrait, y compris "
        "à l'étranger.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))

    # Conditions d'utilisation : frais de virement
    units.append(_unit(
        "KB-INF-GO-VIREMENT", "informationnel", "frais_virement", "Go",
        "Avec le palier Go, les virements vers un autre compte Simple sont "
        "gratuits. Les virements vers une autre banque coûtent 4 DH chacun.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))
    units.append(_unit(
        "KB-INF-PLUSPRIMEMETAL-VIREMENT", "informationnel", "frais_virement", None,
        "Avec les paliers Plus, Prime et Metal, tous les virements (Simple "
        "ou vers une autre banque) sont gratuits et illimités.",
        "fiche_tarifs_v3", "2026-12-31", "3",
    ))

    # Eligibilité et changement de palier
    units.append(_unit(
        "KB-INF-CHANGEMENT-PALIER", "informationnel", "changer_palier", None,
        "Le changement de palier est possible à tout moment depuis "
        "l'application, dans Profil > Mon abonnement. Le nouveau tarif "
        "s'applique dès le mois suivant. Aucun frais de changement.",
        "guide_abonnement_v2", "2026-12-31", "2",
    ))
    units.append(_unit(
        "KB-INF-ELIGIBILITE-METAL", "informationnel", "eligibilite_palier", "Metal",
        "Le palier Metal est réservé aux clients majeurs ayant un compte "
        "Simple actif depuis au moins 3 mois.",
        "guide_abonnement_v2", "2026-12-31", "2",
    ))

    # ------------------------------------------------------------------
    # SUPPORT / SAV — procédures avec critères d'escalade explicites
    # ------------------------------------------------------------------
    units.append(_unit(
        "KB-SUP-CARTE-BLOQUEE", "support", "carte_bloquee", None,
        "Si votre carte est bloquée après 3 codes erronés, débloquez-la "
        "depuis l'application dans Carte > Débloquer. CRITERE D'ESCALADE : "
        "si le déblocage échoue 2 fois, transférer à un conseiller humain.",
        "procedures_sav_v4", "2026-12-31", "4",
    ))
    units.append(_unit(
        "KB-SUP-OPPOSITION-CARTE", "support", "opposition_carte", None,
        "Pour faire opposition à une carte perdue ou volée, allez dans "
        "Carte > Faire opposition, disponible 24h/24. CRITERE D'ESCALADE : "
        "si le client signale une perte à l'étranger ou une fraude avérée, "
        "transférer immédiatement à un conseiller humain.",
        "procedures_sav_v4", "2026-12-31", "4",
    ))
    units.append(_unit(
        "KB-SUP-FRAUDE", "support", "fraude", None,
        "En cas de transaction suspecte non reconnue, signalez-la dans "
        "Carte > Signaler une fraude. CRITERE D'ESCALADE : tout signalement "
        "de fraude doit être transféré immédiatement à un conseiller humain, "
        "sans exception.",
        "procedures_sav_v4", "2026-12-31", "4",
    ))
    # Défaut injecté n°2 : procédure sans critère d'escalade explicite,
    # alors que toutes les autres procédures SAV en définissent un.
    units.append(_unit(
        "KB-SUP-LITIGE-PAIEMENT", "support", "litige_paiement", None,
        "En cas de paiement contesté (montant incorrect, commerçant non "
        "reconnu), ouvrez un litige dans Paiements > Contester un paiement. "
        "Le traitement prend jusqu'à 10 jours ouvrés.",
        "procedures_sav_v4", "2026-12-31", "4",
    ))
    units.append(_unit(
        "KB-SUP-COMPTE-BLOQUE", "support", "compte_bloque", None,
        "Un compte peut être bloqué suite à un contrôle de sécurité "
        "automatique. CRITERE D'ESCALADE : un compte bloqué nécessite "
        "toujours l'intervention d'un conseiller humain pour le débloquer.",
        "procedures_sav_v4", "2026-12-31", "4",
    ))

    # ------------------------------------------------------------------
    # ONBOARDING — parcours et éligibilité par profil/palier
    # ------------------------------------------------------------------
    units.append(_unit(
        "KB-ONB-OUVERTURE-COMPTE", "onboarding", "ouverture_compte", None,
        "L'ouverture d'un compte Simple se fait 100% en ligne en 3 étapes : "
        "pièce d'identité, selfie de vérification, choix du palier. Compte "
        "actif en moins de 10 minutes.",
        "guide_onboarding_v2", "2026-12-31", "2",
    ))
    units.append(_unit(
        "KB-ONB-PREMIER-VIREMENT", "onboarding", "premiere_utilisation", None,
        "Pour effectuer votre premier virement, ajoutez d'abord un "
        "bénéficiaire dans Virements > Ajouter un bénéficiaire, puis suivez "
        "le parcours de virement habituel.",
        "guide_onboarding_v2", "2026-12-31", "2",
    ))
    units.append(_unit(
        "KB-ONB-ELIGIBLE-EPARGNE", "onboarding", "service_eligible", "Plus",
        "Le service d'épargne rémunérée est proposé automatiquement aux "
        "clients des paliers Plus, Prime et Metal après 1 mois d'ancienneté.",
        "guide_onboarding_v2", "2026-12-31", "2",
    ))
    units.append(_unit(
        "KB-ONB-ELIGIBLE-CREDIT", "onboarding", "service_eligible", "Prime",
        "Le service de micro-crédit instantané est proposé aux clients des "
        "paliers Prime et Metal ayant un historique d'au moins 3 mois.",
        "guide_onboarding_v2", "2026-12-31", "2",
    ))
    units.append(_unit(
        "KB-ONB-ELIGIBLE-GO", "onboarding", "service_eligible", "Go",
        "Les clients du palier Go n'ont accès qu'aux fonctionnalités de "
        "base (compte, carte virtuelle, virements Simple). Pour débloquer "
        "l'épargne ou le crédit, il faut passer à un palier supérieur.",
        "guide_onboarding_v2", "2026-12-31", "2",
    ))

    # ------------------------------------------------------------------
    # TRANSACTIONNEL — paramètres requis pour les opérations
    # ------------------------------------------------------------------
    units.append(_unit(
        "KB-TRX-VIREMENT", "transactionnel", "virement", None,
        "Pour effectuer un virement, l'assistant a besoin : du bénéficiaire, "
        "du montant, et éventuellement d'un motif. Une confirmation explicite "
        "du client est obligatoire avant tout déclenchement.",
        "specs_transactionnel_v1", "2026-12-31", "1",
    ))
    units.append(_unit(
        "KB-TRX-PAIEMENT", "transactionnel", "paiement", None,
        "Pour effectuer un paiement, l'assistant a besoin : le bénéficiaire "
        "ou commerçant, et le montant. Une confirmation explicite du client "
        "est obligatoire avant tout déclenchement.",
        "specs_transactionnel_v1", "2026-12-31", "1",
    ))
    units.append(_unit(
        "KB-TRX-CARTE-GESTION", "transactionnel", "gestion_carte", None,
        "Pour bloquer, débloquer ou modifier les plafonds d'une carte, "
        "l'assistant a besoin : l'action souhaitée (bloquer/débloquer/"
        "modifier plafond) et, pour une modification de plafond, le nouveau "
        "montant souhaité. Une confirmation explicite est obligatoire.",
        "specs_transactionnel_v1", "2026-12-31", "1",
    ))

    return units


def main():
    units = build_kb()
    os.makedirs(os.path.dirname(KB_PATH), exist_ok=True)
    with open(KB_PATH, "w", encoding="utf-8") as f:
        for unit in units:
            f.write(json.dumps(unit, ensure_ascii=False) + "\n")
    print(f"Base de connaissances générée : {KB_PATH} ({len(units)} unités).")


if __name__ == "__main__":
    main()
