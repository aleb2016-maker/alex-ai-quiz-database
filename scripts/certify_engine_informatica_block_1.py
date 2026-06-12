import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "INF-FAC-0001": {
        "distrattore_forte": "Archiviare stabilmente file e programmi anche a computer spento",
        "motivo_distrattore_forte": (
            "È vicino perché parla comunque di memoria e conservazione dei dati, "
            "ma è sbagliato perché la RAM è temporanea; l'archiviazione stabile è compito di SSD o hard disk."
        ),
    },
    "INF-INT-0002": {
        "distrattore_forte": "A collegare una tabella a un'altra tramite una chiave esterna",
        "motivo_distrattore_forte": (
            "È vicino perché parla sempre di chiavi nei database relazionali, "
            "ma è sbagliato perché la chiave primaria identifica un record nella stessa tabella, "
            "mentre la chiave esterna collega tabelle diverse."
        ),
    },
    "INF-AV-0003": {
        "distrattore_forte": "Permettere al frontend di leggere direttamente le tabelle del database",
        "motivo_distrattore_forte": (
            "È vicino perché riguarda il rapporto tra frontend, backend e dati, "
            "ma è sbagliato perché il frontend non dovrebbe accedere direttamente al database: "
            "deve passare da endpoint controllati del backend."
        ),
    },
    "INF-FAC-0004": {
        "distrattore_forte": "CSS",
        "motivo_distrattore_forte": (
            "È vicino perché CSS lavora sulle pagine web insieme a HTML, "
            "ma è sbagliato perché CSS gestisce lo stile grafico, mentre HTML definisce la struttura."
        ),
    },
    "INF-FAC-0005": {
        "opzioni": [
            "Un insieme organizzato di righe e colonne",
            "Una singola riga che rappresenta un record",
            "Una relazione tra due tabelle tramite chiavi",
            "Una query usata per filtrare i dati",
        ],
        "risposta_corretta": "Un insieme organizzato di righe e colonne",
        "spiegazione": (
            "Una tabella contiene dati organizzati in righe e colonne. "
            "Una singola riga è un record, una relazione collega tabelle diverse, "
            "mentre una query serve a leggere, filtrare o modificare dati."
        ),
        "distrattore_forte": "Una singola riga che rappresenta un record",
        "motivo_distrattore_forte": (
            "È vicino perché una riga fa parte di una tabella, "
            "ma è sbagliato perché la tabella è l'insieme organizzato di molte righe e colonne."
        ),
    },
    "INF-FAC-0006": {
        "opzioni": [
            "A conservare un valore che può essere usato o modificato",
            "A conservare un valore, ma senza poterlo mai cambiare durante il programma",
            "A definire una funzione riutilizzabile",
            "A ripetere un blocco di istruzioni",
        ],
        "risposta_corretta": "A conservare un valore che può essere usato o modificato",
        "spiegazione": (
            "Una variabile conserva un valore che può essere letto e, in molti casi, modificato durante l'esecuzione. "
            "Una funzione raggruppa codice riutilizzabile, mentre un ciclo ripete istruzioni."
        ),
        "distrattore_forte": "A conservare un valore, ma senza poterlo mai cambiare durante il programma",
        "motivo_distrattore_forte": (
            "È vicino perché parla di conservare un valore, "
            "ma è sbagliato perché una variabile normalmente può cambiare valore durante il programma."
        ),
    },
    "INF-FAC-0007": {
        "distrattore_forte": "Il protocollo usato per trasferire una pagina",
        "motivo_distrattore_forte": (
            "È vicino perché il protocollo può essere una parte dell'URL, per esempio http o https, "
            "ma è sbagliato perché l'URL indica l'indirizzo completo della risorsa."
        ),
    },
    "INF-FAC-0008": {
        "opzioni": [
            "JSON",
            "XML",
            "YAML",
            "CSV",
        ],
        "risposta_corretta": "JSON",
        "spiegazione": (
            "JSON è molto usato nelle API web perché rappresenta bene oggetti, liste e coppie chiave-valore. "
            "XML e YAML possono rappresentare dati strutturati, ma JSON è particolarmente comune nello scambio dati tra frontend, backend e API. "
            "CSV è più adatto a dati tabellari semplici."
        ),
        "distrattore_forte": "XML",
        "motivo_distrattore_forte": (
            "È vicino perché anche XML può rappresentare dati strutturati, "
            "ma è meno usato di JSON nelle API web moderne per oggetti e liste."
        ),
    },
    "INF-INT-0004": {
        "distrattore_forte": "POST",
        "motivo_distrattore_forte": (
            "È vicino perché POST è un metodo HTTP molto usato nelle API, "
            "ma è sbagliato perché di solito serve a inviare o creare dati, non a leggerli senza modificarli."
        ),
    },
    "INF-INT-0005": {
        "distrattore_forte": "A identificare in modo univoco ogni record della stessa tabella",
        "motivo_distrattore_forte": (
            "È vicino perché parla di chiavi nei database relazionali, "
            "ma descrive la chiave primaria; la chiave esterna invece collega record tra tabelle diverse."
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


def aggiorna_file(percorso):
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


def main():
    tutti_modificati = []

    for percorso in DATA_DIR.rglob("*.json"):
        id_modificati = aggiorna_file(percorso)

        if id_modificati:
            print("File aggiornato:", percorso)

            for id_domanda in id_modificati:
                print(" -", id_domanda)

            tutti_modificati.extend(id_modificati)

    mancanti = sorted(
        set(AGGIORNAMENTI.keys()) - set(tutti_modificati)
    )

    print("")
    print("Domande Informatica certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Primo blocco Informatica certificato correttamente.")


main()