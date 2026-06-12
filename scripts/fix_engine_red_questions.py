import json
from pathlib import Path


DATA_DIR = Path("data")
PERCORSO_REVIEW_ENGINE = Path("scripts/review_engine_quality.py")


AGGIORNAMENTI = {
    "LOG-NUM-AV-0004": {
        "opzioni": ["40", "42", "39", "43"],
        "risposta_corretta": "40",
        "distrattore_forte": "42",
        "motivo_distrattore_forte": (
            "È vicino perché sembra continuare dopo 41 aumentando ancora, "
            "ma la sequenza alterna un aumento e poi -1: dopo 41 viene 40."
        ),
    },
    "AI-INT-0101": {
        "opzioni": [
            "Perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso",
            "Perché chunk più grandi garantiscono sempre un recupero più completo e più preciso",
            "Perché i chunk servono ad addestrare nuovamente il modello prima di ogni risposta",
            "Perché i chunk modificano in modo permanente i pesi del modello",
        ],
        "risposta_corretta": "Perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso",
        "distrattore_forte": "Perché chunk più grandi garantiscono sempre un recupero più completo e più preciso",
        "motivo_distrattore_forte": (
            "È vicino perché parla davvero della dimensione dei chunk, "
            "ma è sbagliato perché chunk più grandi non garantiscono sempre maggiore precisione."
        ),
    },
    "INF-AV-0102": {
        "opzioni": [
            "L'hashing è pensato per non essere invertito facilmente, mentre la cifratura può essere decifrata con una chiave",
            "L'hashing può essere decifrato con una chiave corretta, mentre la cifratura no",
            "La cifratura serve solo a confrontare se due dati sono uguali",
            "La cifratura produce sempre una impronta fissa come un hash",
        ],
        "risposta_corretta": (
            "L'hashing è pensato per non essere invertito facilmente, mentre la cifratura può essere decifrata con una chiave"
        ),
        "distrattore_forte": "L'hashing può essere decifrato con una chiave corretta, mentre la cifratura no",
        "motivo_distrattore_forte": (
            "È vicino perché confronta hashing e cifratura, "
            "ma è sbagliato perché l'hashing non è pensato per essere decifrato."
        ),
    },
    "INF-AV-0106": {
        "opzioni": [
            "Perché include applicazione e dipendenze in un ambiente isolato e riproducibile",
            "Perché include applicazione e dipendenze e quindi garantisce sempre lo stesso risultato in qualunque ambiente",
            "Perché aggiorna automaticamente tutte le dipendenze alla versione più recente",
            "Perché installa automaticamente ogni libreria mancante a ogni avvio",
        ],
        "risposta_corretta": "Perché include applicazione e dipendenze in un ambiente isolato e riproducibile",
        "distrattore_forte": (
            "Perché include applicazione e dipendenze e quindi garantisce sempre lo stesso risultato in qualunque ambiente"
        ),
        "motivo_distrattore_forte": (
            "È vicino perché parla di applicazione, dipendenze e ambiente, "
            "ma è troppo assoluto: un container aiuta la riproducibilità, non garantisce sempre ogni risultato."
        ),
    },
    "INF-AV-0107": {
        "opzioni": [
            "Perché permette di confermare tutte le modifiche solo se l'intera operazione va a buon fine",
            "Perché conferma ogni singola modifica appena viene eseguita, anche se le operazioni successive falliscono",
            "Perché controlla automaticamente che ogni query SQL sia scritta senza errori logici",
            "Perché corregge automaticamente le query SQL quando una condizione è sbagliata",
        ],
        "risposta_corretta": (
            "Perché permette di confermare tutte le modifiche solo se l'intera operazione va a buon fine"
        ),
        "distrattore_forte": (
            "Perché conferma ogni singola modifica appena viene eseguita, anche se le operazioni successive falliscono"
        ),
        "motivo_distrattore_forte": (
            "È vicino perché parla di modifiche e conferma, "
            "ma descrive il comportamento opposto a una transazione atomica."
        ),
    },
    "LOG-VER-FAC-0102": {
        "opzioni": ["martello", "armadio", "tavolo", "sedia"],
        "risposta_corretta": "martello",
        "distrattore_forte": "armadio",
        "motivo_distrattore_forte": (
            "È vicino perché è comunque un oggetto della casa, "
            "ma è sbagliato perché appartiene al gruppo dei mobili come tavolo e sedia."
        ),
    },
    "LOG-NUM-FAC-0001": {
        "opzioni": ["16", "15", "17", "19"],
        "risposta_corretta": "16",
        "distrattore_forte": "15",
        "motivo_distrattore_forte": (
            "È vicino perché è molto vicino al valore corretto, "
            "ma sbaglia la sequenza: si aggiunge sempre 3, quindi dopo 13 viene 16."
        ),
    },
    "LOG-NUM-AV-0003": {
        "opzioni": ["80", "44", "72", "76"],
        "risposta_corretta": "80",
        "distrattore_forte": "44",
        "motivo_distrattore_forte": (
            "È vicino perché continua con +4, una regola presente nella sequenza, "
            "ma sbaglia perché la sequenza alterna +4 e ×2: dopo 40 bisogna fare ×2."
        ),
    },
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            dati,
            file,
            ensure_ascii=False,
            indent=2
        )
        file.write("\n")


def trova_liste_domande(dati):
    liste = []

    if isinstance(dati, list):
        liste.append(dati)

    elif isinstance(dati, dict):
        for valore in dati.values():
            if isinstance(valore, list):
                liste.append(valore)

    return liste


def aggiorna_file_domande(percorso):
    dati = carica_json(percorso)
    liste_domande = trova_liste_domande(dati)

    modificato = False
    id_modificati = []

    for lista_domande in liste_domande:
        for domanda in lista_domande:
            if not isinstance(domanda, dict):
                continue

            id_domanda = domanda.get("id")

            if id_domanda in AGGIORNAMENTI:
                domanda.update(AGGIORNAMENTI[id_domanda])
                modificato = True
                id_modificati.append(id_domanda)

    if modificato:
        salva_json(percorso, dati)

    return id_modificati


def aggiorna_controllo_visuale():
    if not PERCORSO_REVIEW_ENGINE.exists():
        print("File review_engine_quality.py non trovato.")
        return False

    contenuto = PERCORSO_REVIEW_ENGINE.read_text(encoding="utf-8")

    if "domanda_visiva = str(id_domanda).startswith(\"LOG-VIS\")" in contenuto:
        print("Il controllo visuale era già stato aggiornato.")
        return True

    vecchio_blocco = '''    if opzione_a != risposta_corretta:
        problemi_rossi.append(
            "La risposta corretta non è in posizione A. "
            "Per lo standard motore, A deve essere la risposta corretta."
        )

    if opzione_b == risposta_corretta:
        problemi_rossi.append(
            "La posizione B non può essere corretta: "
            "B deve essere il distrattore forte."
        )
'''

    nuovo_blocco = '''    domanda_visiva = str(id_domanda).startswith("LOG-VIS")

    # Nelle domande visive le opzioni A/B/C/D possono essere etichette
    # collegate alle immagini. Non le spostiamo automaticamente solo
    # per mettere la risposta corretta in posizione A.
    # Le domande visive avranno un controllo dedicato quando espanderemo
    # la logica visiva.
    if not domanda_visiva:
        if opzione_a != risposta_corretta:
            problemi_rossi.append(
                "La risposta corretta non è in posizione A. "
                "Per lo standard motore, A deve essere la risposta corretta."
            )

        if opzione_b == risposta_corretta:
            problemi_rossi.append(
                "La posizione B non può essere corretta: "
                "B deve essere il distrattore forte."
            )
'''

    if vecchio_blocco not in contenuto:
        print("Blocco del controllo A/B non trovato.")
        print("Non ho modificato review_engine_quality.py.")
        return False

    nuovo_contenuto = contenuto.replace(
        vecchio_blocco,
        nuovo_blocco
    )

    PERCORSO_REVIEW_ENGINE.write_text(
        nuovo_contenuto,
        encoding="utf-8"
    )

    print("Controllo visuale aggiornato in review_engine_quality.py.")
    return True


def main():
    tutti_gli_id_modificati = []

    for percorso in DATA_DIR.rglob("*.json"):
        id_modificati = aggiorna_file_domande(percorso)

        if id_modificati:
            print("File aggiornato:", percorso)

            for id_domanda in id_modificati:
                print(" -", id_domanda)

            tutti_gli_id_modificati.extend(id_modificati)

    id_mancanti = sorted(
        set(AGGIORNAMENTI.keys()) - set(tutti_gli_id_modificati)
    )

    print("")
    print("Domande aggiornate:", len(tutti_gli_id_modificati))

    if id_mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in id_mancanti:
            print(" -", id_domanda)
    else:
        print("Tutte le domande rosse non visive sono state aggiornate.")

    print("")
    aggiorna_controllo_visuale()


main()