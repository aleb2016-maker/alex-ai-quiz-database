import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "LOG-CRI-AV-0003": {
        "opzioni": [
            "Non è certo che il prodotto sia scontato",
            "Il prodotto è sicuramente scontato perché si trova nello scaffale rosso",
            "Tutti i prodotti nello scaffale rosso sono sicuramente scontati",
            "Nessun prodotto non scontato può trovarsi nello scaffale rosso",
        ],
        "risposta_corretta": "Non è certo che il prodotto sia scontato",
        "spiegazione": (
            "L'affermazione dice che tutti i prodotti scontati sono nello scaffale rosso. "
            "Questo non significa che tutti i prodotti nello scaffale rosso siano scontati. "
            "Trovare un prodotto nello scaffale rosso non basta quindi per concludere con certezza che sia scontato."
        ),
        "distrattore_forte": "Il prodotto è sicuramente scontato perché si trova nello scaffale rosso",
        "motivo_distrattore_forte": (
            "È molto vicino perché usa proprio l'informazione dello scaffale rosso, "
            "ma è sbagliato perché confonde una condizione necessaria con una condizione sufficiente: "
            "sappiamo che gli scontati stanno nello scaffale rosso, non che tutto ciò che sta nello scaffale rosso sia scontato."
        ),
    },
    "LOG-NUM-INT-0002": {
        "opzioni": [
            "8",
            "18",
            "9",
            "16",
        ],
        "risposta_corretta": "8",
        "spiegazione": (
            "La serie alterna due sequenze. "
            "Nelle posizioni dispari ci sono 2, 4, 6, quindi il numero successivo è 8. "
            "Nelle posizioni pari ci sono 9, 12, 15, che aumentano di 3: 18 sarebbe il prossimo valore della sequenza pari, "
            "ma non è il valore richiesto in questa posizione."
        ),
        "distrattore_forte": "18",
        "motivo_distrattore_forte": (
            "È vicino perché continua correttamente la sottosequenza 9, 12, 15 aggiungendo 3, "
            "ma è sbagliato perché il prossimo posto della serie appartiene alla sottosequenza dispari 2, 4, 6, quindi deve essere 8."
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
    print("Domande Logica certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Categoria Logica completata: tutte le domande sono ora certificate per il motore.")


main()