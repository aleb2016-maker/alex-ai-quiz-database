import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path


# Cartella dove si trovano i file JSON delle domande.
CARTELLA_DOMANDE = Path("data")


# Se due domande superano questa somiglianza, vengono segnalate.
# 0.86 significa 86% circa di testo simile.
SOGLIA_SOMIGLIANZA = 0.86


def normalizza_testo(testo):
    # Trasforma il testo in minuscolo.
    testo = testo.lower()

    # Rimuove gli accenti per confrontare meglio le frasi.
    testo = unicodedata.normalize("NFD", testo)
    testo = "".join(
        carattere
        for carattere in testo
        if unicodedata.category(carattere) != "Mn"
    )

    # Tiene solo lettere, numeri e spazi.
    testo = re.sub(r"[^a-z0-9\s]", " ", testo)

    # Sostituisce spazi multipli con un solo spazio.
    testo = re.sub(r"\s+", " ", testo)

    # Toglie spazi inutili all'inizio e alla fine.
    testo = testo.strip()

    return testo


def calcola_somiglianza(testo_1, testo_2):
    # Calcola quanto due testi sono simili tra loro.
    testo_1_pulito = normalizza_testo(testo_1)
    testo_2_pulito = normalizza_testo(testo_2)

    somiglianza = SequenceMatcher(
        None,
        testo_1_pulito,
        testo_2_pulito
    ).ratio()

    return somiglianza


def trova_file_json():
    # Cerca tutti i file JSON dentro data e nelle sue sottocartelle.
    file_json = list(CARTELLA_DOMANDE.rglob("*.json"))

    return file_json


def carica_domande_da_file(percorso_file):
    # Legge un file JSON e restituisce la lista delle domande.
    with open(percorso_file, "r", encoding="utf-8") as file:
        domande = json.load(file)

    return domande


def carica_tutte_le_domande():
    # Carica tutte le domande da tutti i file JSON.
    tutte_le_domande = []

    file_json = trova_file_json()

    for percorso_file in file_json:
        domande_del_file = carica_domande_da_file(percorso_file)

        for domanda in domande_del_file:
            domanda_con_file = dict(domanda)

            # Salviamo anche da quale file arriva la domanda.
            domanda_con_file["_file_origine"] = str(percorso_file)

            tutte_le_domande.append(domanda_con_file)

    return tutte_le_domande


def controlla_opzioni_duplicate(domanda):
    # Controlla se nella stessa domanda ci sono risposte ripetute.
    opzioni = domanda.get("opzioni", [])

    opzioni_normalizzate = []

    for opzione in opzioni:
        opzione_pulita = normalizza_testo(opzione)
        opzioni_normalizzate.append(opzione_pulita)

    opzioni_uniche = set(opzioni_normalizzate)

    if len(opzioni_normalizzate) != len(opzioni_uniche):
        return True

    return False


def controlla_domande_identiche(tutte_le_domande):
    # Controlla domande completamente uguali dopo la normalizzazione.
    domande_gia_viste = {}
    duplicati = []

    for domanda in tutte_le_domande:
        testo_domanda = domanda.get("domanda", "")
        testo_pulito = normalizza_testo(testo_domanda)

        if testo_pulito in domande_gia_viste:
            duplicati.append(
                (
                    domande_gia_viste[testo_pulito],
                    domanda
                )
            )
        else:
            domande_gia_viste[testo_pulito] = domanda

    return duplicati


def controlla_domande_simili(tutte_le_domande):
    # Confronta ogni domanda con tutte le altre.
    domande_simili = []

    numero_domande = len(tutte_le_domande)

    for indice_1 in range(numero_domande):
        domanda_1 = tutte_le_domande[indice_1]

        for indice_2 in range(indice_1 + 1, numero_domande):
            domanda_2 = tutte_le_domande[indice_2]

            testo_1 = domanda_1.get("domanda", "")
            testo_2 = domanda_2.get("domanda", "")

            somiglianza = calcola_somiglianza(testo_1, testo_2)

            if somiglianza >= SOGLIA_SOMIGLIANZA:
                domande_simili.append(
                    (
                        domanda_1,
                        domanda_2,
                        somiglianza
                    )
                )

    return domande_simili


def stampa_domanda_breve(domanda):
    # Stampa le informazioni principali di una domanda.
    id_domanda = domanda.get("id", "ID_MANCANTE")
    file_origine = domanda.get("_file_origine", "FILE_SCONOSCIUTO")
    testo_domanda = domanda.get("domanda", "")

    print(f"ID: {id_domanda}")
    print(f"File: {file_origine}")
    print(f"Domanda: {testo_domanda}")


def main():
    print("----- CONTROLLO DUPLICATI E SOMIGLIANZE -----")

    tutte_le_domande = carica_tutte_le_domande()

    print(f"Domande caricate: {len(tutte_le_domande)}")

    duplicati_identici = controlla_domande_identiche(tutte_le_domande)
    domande_simili = controlla_domande_simili(tutte_le_domande)

    opzioni_duplicate_trovate = []

    for domanda in tutte_le_domande:
        if controlla_opzioni_duplicate(domanda):
            opzioni_duplicate_trovate.append(domanda)

    print("\n----- RISULTATO DOMANDE IDENTICHE -----")

    if not duplicati_identici:
        print("Nessuna domanda identica trovata.")
    else:
        print(f"Domande identiche trovate: {len(duplicati_identici)}")

        for domanda_1, domanda_2 in duplicati_identici:
            print("\nDuplicato trovato:")
            stampa_domanda_breve(domanda_1)
            print("---")
            stampa_domanda_breve(domanda_2)

    print("\n----- RISULTATO DOMANDE TROPPO SIMILI -----")

    if not domande_simili:
        print("Nessuna domanda troppo simile trovata.")
    else:
        print(f"Domande troppo simili trovate: {len(domande_simili)}")

        for domanda_1, domanda_2, somiglianza in domande_simili:
            percentuale = round(somiglianza * 100, 2)

            print(f"\nSomiglianza: {percentuale}%")
            stampa_domanda_breve(domanda_1)
            print("---")
            stampa_domanda_breve(domanda_2)

    print("\n----- RISULTATO OPZIONI DUPLICATE -----")

    if not opzioni_duplicate_trovate:
        print("Nessuna opzione duplicata trovata nella stessa domanda.")
    else:
        print(
            "Domande con opzioni duplicate trovate: "
            f"{len(opzioni_duplicate_trovate)}"
        )

        for domanda in opzioni_duplicate_trovate:
            print()
            stampa_domanda_breve(domanda)


main()