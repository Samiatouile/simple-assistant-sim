"""Point d'entrée unique du simulateur.

Usage :
    python -m src.cli generate-data
    python -m src.cli build-testset
    python -m src.cli run-eval
    python -m src.cli report
"""
import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="simple-assistant-sim",
        description="Simulateur de fiabilité de l'assistant virtuel 'Simple' (neobanque fictive).",
    )
    sub = parser.add_subparsers(dest="commande", required=True)

    sub.add_parser("generate-data", help="Génère la base de connaissances synthétique (data/kb.jsonl).")
    sub.add_parser("build-testset", help="Génère le golden set de questions annotées (data/golden_set.jsonl).")
    sub.add_parser("run-eval", help="Fait tourner l'assistant simulé sur le golden set et note les réponses.")
    sub.add_parser("report", help="Agrège les KPI de fiabilité et produit le rapport (reports/).")

    args = parser.parse_args()

    if args.commande == "generate-data":
        from src.generate_data import main as run
        run()
    elif args.commande == "build-testset":
        from src.build_testset import main as run
        run()
    elif args.commande == "run-eval":
        from src.evaluate import main as run
        run()
    elif args.commande == "report":
        from src.report import main as run
        run()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
