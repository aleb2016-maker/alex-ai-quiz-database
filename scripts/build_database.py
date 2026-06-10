import json
from pathlib import Path


# Cartella dove si trovano i file JSON divisi per categoria.
CARTELLA_DOMANDE = Path("data")


# Cartella dove salveremo il database finale.
CARTELLA_OUTPUT = Path("dist")


# File finale che passeremo poi all'app Android o a Codex.
FILE_DATABASE_FINALE = CARTELLA_OUTPUT / "database_quiz_finale.json"


def trova_file_json():
    # Cerca tutti i file JSON dentro data e nelle sue sottocartelle.
    file_json = list(CARTELLA_DOMANDE.rglob("*.json"))

    return file_json


def carica_domande_da_file(percorso_file):
    # Legge un singolo file JSON e restituisce la lista delle domande.
    with open(percorso_file, "r", encoding="utf-8") as file:
        domande = json.load(file)

    return domande


def salva_database_finale(tutte_le_domande):
    # Crea la cartella dist se non esiste.
    CARTELLA_OUTPUT.mkdir(exist_ok=True)

    # Salva tutte le domande in un unico file JSON finale.
    with open(FILE_DATABASE_FINALE, "w", encoding="utf-8") as file:
        json.dump(
            tutte_le_domande,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():
    # Cerca tutti i file JSON delle domande.
    file_json = trova_file_json()

    # Qui metteremo tutte le domande raccolte dai vari file.
    tutte_le_domande = []

    print("----- CREAZIONE DATABASE FINALE -----")

    for percorso_file in file_json:
        print(f"Leggo file: {percorso_file}")

        domande_del_file = carica_domande_da_file(percorso_file)

        tutte_le_domande.extend(domande_del_file)

    salva_database_finale(tutte_le_domande)

    print("\n----- RISULTATO FINALE -----")
    print(f"Domande totali raccolte: {len(tutte_le_domande)}")
    print(f"Database creato in: {FILE_DATABASE_FINALE}")


main()