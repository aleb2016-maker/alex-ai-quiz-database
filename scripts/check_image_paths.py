import json
from pathlib import Path


# Cartella dove si trovano i file JSON delle domande.
CARTELLA_DOMANDE = Path("data")


def trova_file_json():
    # Cerca tutti i file JSON dentro data e nelle sottocartelle.
    file_json = list(CARTELLA_DOMANDE.rglob("*.json"))

    return file_json


def carica_domande_da_file(percorso_file):
    # Legge un file JSON e restituisce la lista delle domande.
    with open(percorso_file, "r", encoding="utf-8") as file:
        domande = json.load(file)

    return domande


def controlla_percorso_immagine(percorso_immagine):
    # Controlla se il file immagine esiste davvero nel progetto.
    percorso_file = Path(percorso_immagine)

    return percorso_file.exists()


def raccogli_immagini_domanda(domanda):
    # Raccoglie tutti i percorsi immagine presenti in una domanda visiva.
    immagini = []

    immagine_domanda = domanda.get("immagine_domanda")

    if immagine_domanda:
        immagini.append(immagine_domanda)

    immagini_opzioni = domanda.get("immagini_opzioni", [])

    for immagine_opzione in immagini_opzioni:
        immagini.append(immagine_opzione)

    return immagini


def main():
    print("----- CONTROLLO PERCORSI IMMAGINI -----")

    file_json = trova_file_json()

    totale_domande_visive = 0
    totale_immagini_controllate = 0
    immagini_mancanti = []

    for percorso_file in file_json:
        domande = carica_domande_da_file(percorso_file)

        for domanda in domande:
            tipo_domanda = domanda.get("tipo_domanda", "testo")

            if tipo_domanda != "immagine":
                continue

            totale_domande_visive += 1

            id_domanda = domanda.get("id", "ID_MANCANTE")
            immagini = raccogli_immagini_domanda(domanda)

            for percorso_immagine in immagini:
                totale_immagini_controllate += 1

                immagine_esiste = controlla_percorso_immagine(
                    percorso_immagine
                )

                if not immagine_esiste:
                    immagini_mancanti.append(
                        {
                            "id_domanda": id_domanda,
                            "file_json": str(percorso_file),
                            "immagine": percorso_immagine,
                        }
                    )

    print(f"Domande visive trovate: {totale_domande_visive}")
    print(f"Immagini controllate: {totale_immagini_controllate}")

    print("\n----- RISULTATO CONTROLLO IMMAGINI -----")

    if not immagini_mancanti:
        print("Tutte le immagini indicate nel JSON esistono.")
        return

    print("ATTENZIONE: alcune immagini indicate nel JSON non esistono ancora.")
    print(f"Immagini mancanti: {len(immagini_mancanti)}")

    for elemento in immagini_mancanti:
        print()
        print(f"ID domanda: {elemento['id_domanda']}")
        print(f"File JSON: {elemento['file_json']}")
        print(f"Immagine mancante: {elemento['immagine']}")

    print("\nNota: per ora questo è solo un avviso.")
    print("Quando creeremo i file PNG, questo controllo dovrà diventare pulito.")


main()