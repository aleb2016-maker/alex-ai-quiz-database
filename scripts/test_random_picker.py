import json
import random
from pathlib import Path


# File finale creato dal nostro builder.
FILE_DATABASE = Path("dist/database_quiz_finale.json")


# File dove salviamo gli ID già usati.
# Per ora è solo una simulazione.
FILE_DOMANDE_USATE = Path("dist/domande_usate_demo.json")


def carica_database():
    # Legge il database finale con tutte le domande.
    with open(FILE_DATABASE, "r", encoding="utf-8") as file:
        domande = json.load(file)

    return domande


def carica_id_domande_usate():
    # Se il file non esiste, significa che non abbiamo ancora usato domande.
    if not FILE_DOMANDE_USATE.exists():
        return []

    # Legge gli ID delle domande già usate.
    with open(FILE_DOMANDE_USATE, "r", encoding="utf-8") as file:
        id_domande_usate = json.load(file)

    return id_domande_usate


def salva_id_domande_usate(id_domande_usate):
    # Salva gli ID delle domande già usate.
    with open(FILE_DOMANDE_USATE, "w", encoding="utf-8") as file:
        json.dump(
            id_domande_usate,
            file,
            ensure_ascii=False,
            indent=2
        )


def filtra_domande(domande, categoria_richiesta, livello_richiesto):
    # Tiene solo le domande della categoria e del livello richiesto.
    domande_filtrate = []

    for domanda in domande:
        stessa_categoria = domanda["categoria"] == categoria_richiesta
        stesso_livello = domanda["livello"] == livello_richiesto

        if stessa_categoria and stesso_livello:
            domande_filtrate.append(domanda)

    return domande_filtrate


def scegli_domande_senza_ripetere(domande_filtrate, numero_domande):
    # Carica le domande già usate nei test precedenti.
    id_domande_usate = carica_id_domande_usate()

    # Tiene solo le domande non ancora usate.
    domande_disponibili = []

    for domanda in domande_filtrate:
        id_domanda = domanda["id"]

        if id_domanda not in id_domande_usate:
            domande_disponibili.append(domanda)

    # Se le domande disponibili sono poche, resettiamo la memoria.
    if len(domande_disponibili) < numero_domande:
        print("Domande quasi finite: resetto la memoria delle domande usate.")

        id_domande_usate = []
        domande_disponibili = domande_filtrate.copy()

    # Mescola le domande disponibili.
    random.shuffle(domande_disponibili)

    # Prende solo il numero di domande richiesto.
    domande_scelte = domande_disponibili[:numero_domande]

    # Aggiorna la lista degli ID usati.
    for domanda in domande_scelte:
        id_domanda = domanda["id"]
        id_domande_usate.append(id_domanda)

    # Salva la memoria aggiornata.
    salva_id_domande_usate(id_domande_usate)

    return domande_scelte


def stampa_domande_scelte(domande_scelte):
    # Stampa le domande scelte per il test.
    print("\n----- DOMANDE SCELTE -----")

    for numero, domanda in enumerate(domande_scelte, start=1):
        print(f"\nDomanda {numero}")
        print(f"ID: {domanda['id']}")
        print(f"Categoria: {domanda['categoria']}")
        print(f"Livello: {domanda['livello']}")
        print(f"Testo: {domanda['domanda']}")


def main():
    # Parametri di prova.
    categoria_richiesta = "ai"
    livello_richiesto = "intermedio"
    numero_domande = 2

    # Carica tutte le domande dal database finale.
    domande = carica_database()

    # Filtra le domande per categoria e livello.
    domande_filtrate = filtra_domande(
        domande,
        categoria_richiesta,
        livello_richiesto
    )

    print("----- TEST RANDOM INTELLIGENTE -----")
    print(f"Categoria richiesta: {categoria_richiesta}")
    print(f"Livello richiesto: {livello_richiesto}")
    print(f"Domande trovate: {len(domande_filtrate)}")

    if not domande_filtrate:
        print("Nessuna domanda trovata con questi filtri.")
        return

    # Sceglie le domande senza ripetere sempre le stesse.
    domande_scelte = scegli_domande_senza_ripetere(
        domande_filtrate,
        numero_domande
    )

    stampa_domande_scelte(domande_scelte)


main()