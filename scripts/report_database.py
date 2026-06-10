import json
from collections import defaultdict
from pathlib import Path


# File finale creato da build_database.py.
FILE_DATABASE = Path("dist/database_quiz_finale.json")


def carica_database():
    # Legge il database finale.
    with open(FILE_DATABASE, "r", encoding="utf-8") as file:
        domande = json.load(file)

    return domande


def crea_report_categorie(domande):
    # Qui contiamo quante domande ci sono per categoria.
    conteggio_categorie = defaultdict(int)

    for domanda in domande:
        categoria = domanda["categoria"]
        conteggio_categorie[categoria] += 1

    return conteggio_categorie


def crea_report_livelli(domande):
    # Qui contiamo quante domande ci sono per livello.
    conteggio_livelli = defaultdict(int)

    for domanda in domande:
        livello = domanda["livello"]
        conteggio_livelli[livello] += 1

    return conteggio_livelli


def crea_report_categoria_livello(domande):
    # Qui contiamo le domande divise per categoria e livello.
    report = defaultdict(lambda: defaultdict(int))

    for domanda in domande:
        categoria = domanda["categoria"]
        livello = domanda["livello"]

        report[categoria][livello] += 1

    return report


def stampa_report_categorie(conteggio_categorie):
    print("\n----- DOMANDE PER CATEGORIA -----")

    for categoria, quantita in sorted(conteggio_categorie.items()):
        print(f"{categoria}: {quantita}")


def stampa_report_livelli(conteggio_livelli):
    print("\n----- DOMANDE PER LIVELLO -----")

    for livello, quantita in sorted(conteggio_livelli.items()):
        print(f"{livello}: {quantita}")


def stampa_report_categoria_livello(report):
    print("\n----- DOMANDE PER CATEGORIA E LIVELLO -----")

    livelli_ordinati = [
        "facile",
        "intermedio",
        "avanzato",
    ]

    for categoria in sorted(report.keys()):
        print(f"\n{categoria}")

        for livello in livelli_ordinati:
            quantita = report[categoria].get(livello, 0)
            print(f"- {livello}: {quantita}")


def main():
    print("----- REPORT DATABASE QUIZ -----")

    if not FILE_DATABASE.exists():
        print("ERRORE: il database finale non esiste.")
        print("Prima esegui: python scripts/build_database.py")
        return

    domande = carica_database()

    conteggio_categorie = crea_report_categorie(domande)
    conteggio_livelli = crea_report_livelli(domande)
    report_categoria_livello = crea_report_categoria_livello(domande)

    print(f"Domande totali: {len(domande)}")

    stampa_report_categorie(conteggio_categorie)
    stampa_report_livelli(conteggio_livelli)
    stampa_report_categoria_livello(report_categoria_livello)


main()