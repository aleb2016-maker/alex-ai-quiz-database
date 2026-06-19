import json
from pathlib import Path

from visual_logic_validator import validate_visual_logic_question


# Cartella dove si trovano i file JSON delle domande.
CARTELLA_DOMANDE = Path("data")


# Campi obbligatori base validi per tutte le domande.
CAMPI_OBBLIGATORI_BASE = [
    "id",
    "categoria",
    "sottocategoria",
    "livello",
    "domanda",
    "opzioni",
    "risposta_corretta",
    "spiegazione",
    "tags",
    "difficolta",
]


# Categorie accettate dal nostro sistema.
CATEGORIE_VALIDE = [
    "ai",
    "informatica",
    "logica",
    "matematica",
    "inglese",
    "scienze",
    "fisica",
    "chimica",
    "biologia",
]


# Livelli accettati dal nostro sistema.
LIVELLI_VALIDI = [
    "facile",
    "intermedio",
    "avanzato",
]


# Tipi di domanda accettati.
TIPI_DOMANDA_VALIDI = [
    "testo",
    "immagine",
]


def carica_domande_da_file(percorso_file):
    # Legge il file JSON e restituisce le domande.
    with open(percorso_file, "r", encoding="utf-8") as file:
        domande = json.load(file)

    return domande


def controlla_campi_obbligatori_base(domanda):
    # Controlla se mancano i campi base.
    errori = []

    for campo in CAMPI_OBBLIGATORI_BASE:
        if campo not in domanda:
            errori.append(f"Manca il campo: {campo}")

    return errori


def controlla_tipo_domanda(domanda):
    # Se il tipo non è specificato, assumiamo 'testo'.
    tipo_domanda = domanda.get("tipo_domanda", "testo")

    if tipo_domanda not in TIPI_DOMANDA_VALIDI:
        return [f"Tipo domanda non valido: {tipo_domanda}"]

    return []


def controlla_campi_domanda_immagine(domanda):
    # Controlla i campi extra necessari per le domande con immagini.
    errori = []

    tipo_domanda = domanda.get("tipo_domanda", "testo")

    if tipo_domanda != "immagine":
        return errori

    if "immagine_domanda" not in domanda:
        errori.append("Manca il campo: immagine_domanda")

    if "immagini_opzioni" not in domanda:
        errori.append("Manca il campo: immagini_opzioni")
        return errori

    immagini_opzioni = domanda.get("immagini_opzioni")

    if not isinstance(immagini_opzioni, list):
        errori.append("Il campo immagini_opzioni deve essere una lista")
        return errori

    if len(immagini_opzioni) != 4:
        errori.append("Il campo immagini_opzioni deve contenere 4 elementi")

    return errori


def controlla_opzioni(domanda):
    # Controlla che ci siano esattamente 4 opzioni.
    errori = []

    opzioni = domanda.get("opzioni")

    if not isinstance(opzioni, list):
        errori.append("Il campo opzioni deve essere una lista")
        return errori

    if len(opzioni) != 4:
        errori.append("La domanda deve avere esattamente 4 opzioni")

    return errori


def controlla_risposta_corretta(domanda):
    # Controlla che la risposta corretta sia dentro le opzioni.
    errori = []

    opzioni = domanda.get("opzioni", [])
    risposta_corretta = domanda.get("risposta_corretta")

    if risposta_corretta not in opzioni:
        errori.append("La risposta corretta non è presente tra le opzioni")

    return errori


def controlla_categoria(domanda):
    # Controlla che la categoria sia valida.
    errori = []

    categoria = domanda.get("categoria")

    if categoria not in CATEGORIE_VALIDE:
        errori.append(f"Categoria non valida: {categoria}")

    return errori


def controlla_livello(domanda):
    # Controlla che il livello sia valido.
    errori = []

    livello = domanda.get("livello")

    if livello not in LIVELLI_VALIDI:
        errori.append(f"Livello non valido: {livello}")

    return errori


def controlla_difficolta(domanda):
    # Controlla che la difficoltà sia un numero da 1 a 3.
    errori = []

    difficolta = domanda.get("difficolta")

    if not isinstance(difficolta, int):
        errori.append("La difficoltà deve essere un numero intero")
        return errori

    if difficolta < 1 or difficolta > 3:
        errori.append("La difficoltà deve essere compresa tra 1 e 3")

    return errori


def controlla_domanda(domanda):
    # Esegue tutti i controlli su una singola domanda.
    errori = []

    errori.extend(controlla_campi_obbligatori_base(domanda))
    errori.extend(controlla_tipo_domanda(domanda))
    errori.extend(controlla_campi_domanda_immagine(domanda))
    errori.extend(controlla_opzioni(domanda))
    errori.extend(controlla_risposta_corretta(domanda))
    errori.extend(controlla_categoria(domanda))
    errori.extend(controlla_livello(domanda))
    errori.extend(controlla_difficolta(domanda))

    if "visual_logic" in domanda:
        risultato_visivo = validate_visual_logic_question(domanda)

        if not risultato_visivo["valid"]:
            for errore in risultato_visivo["errors"]:
                errori.append(f"Logica visiva non valida: {errore}")

    return errori


def trova_file_json():
    # Cerca tutti i file JSON dentro data e sottocartelle.
    file_json = list(CARTELLA_DOMANDE.rglob("*.json"))

    return file_json


def main():
    # Cerca i file JSON da controllare.
    file_json = trova_file_json()

    # Qui salviamo gli ID già trovati.
    id_gia_trovati = set()

    # Conta tutti gli errori trovati.
    totale_errori = 0

    print("----- CONTROLLO FILE JSON -----")

    for percorso_file in file_json:
        print(f"\nControllo file: {percorso_file}")

        try:
            domande = carica_domande_da_file(percorso_file)

        except json.JSONDecodeError:
            print("ERRORE: il file non contiene JSON valido.")
            totale_errori += 1
            continue

        if not isinstance(domande, list):
            print("ERRORE: il file deve contenere una lista di domande.")
            totale_errori += 1
            continue

        for numero_domanda, domanda in enumerate(domande, start=1):
            id_domanda = domanda.get(
                "id",
                f"DOMANDA_SENZA_ID_{numero_domanda}"
            )

            errori_domanda = controlla_domanda(domanda)

            if id_domanda in id_gia_trovati:
                errori_domanda.append(f"ID duplicato: {id_domanda}")

            id_gia_trovati.add(id_domanda)

            if errori_domanda:
                totale_errori += len(errori_domanda)

                print(f"\nErrore nella domanda {numero_domanda}: {id_domanda}")

                for errore in errori_domanda:
                    print(f"- {errore}")

    print("\n----- RISULTATO FINALE -----")

    if totale_errori == 0:
        print("Tutto corretto. Nessun errore trovato.")
    else:
        print(f"Errori trovati: {totale_errori}")


main()
