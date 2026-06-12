import json
from pathlib import Path


LOGICA_VISIVA_FILE = Path("data/logica/logica_visiva.json")


DISTRACTORI_FORTI = {
    "LOG-VIS-FAC-0004": {
        "distrattore_forte": "C",
        "motivo": "C mantiene la stessa forma e lo stesso numero di punti, ma sbaglia il colore."
    },
    "LOG-VIS-FAC-0005": {
        "distrattore_forte": "C",
        "motivo": "C è una freccia della stessa sequenza di rotazione, ma rappresenta il passaggio precedente."
    },
    "LOG-VIS-FAC-0006": {
        "distrattore_forte": "B",
        "motivo": "B mantiene forma e quantità corretta di punti, ma cambia il colore."
    },
    "LOG-VIS-FAC-0007": {
        "distrattore_forte": "A",
        "motivo": "A mantiene la stessa forma, ma sbaglia l'alternanza del colore."
    },
    "LOG-VIS-FAC-0008": {
        "distrattore_forte": "B",
        "motivo": "B mantiene forma e colore corretti, ma sbaglia il numero di punti."
    },

    "LOG-VIS-INT-0004": {
        "distrattore_forte": "C",
        "motivo": "C mantiene colore e quantità interna, ma sbaglia la crescita della figura esterna."
    },
    "LOG-VIS-INT-0005": {
        "distrattore_forte": "A",
        "motivo": "A mantiene forma e numero di punti, ma sbaglia il colore richiesto dalla matrice."
    },
    "LOG-VIS-INT-0006": {
        "distrattore_forte": "C",
        "motivo": "C mantiene forma, colore e numero di punti, ma sbaglia il verso della diagonale."
    },
    "LOG-VIS-INT-0007": {
        "distrattore_forte": "D",
        "motivo": "D mantiene direzione e colore corretti, ma sbaglia il numero di punti."
    },
    "LOG-VIS-INT-0008": {
        "distrattore_forte": "A",
        "motivo": "A è simile alla figura corretta, ma non rispetta pienamente il ribaltamento speculare."
    },

    "LOG-VIS-AV-0004": {
        "distrattore_forte": "C",
        "motivo": "C mantiene forma e colore corretti, ma sbaglia il numero di linee interne."
    },
    "LOG-VIS-AV-0005": {
        "distrattore_forte": "A",
        "motivo": "A mantiene il riempimento a puntini, ma sbaglia il numero di contorni esterni."
    },
    "LOG-VIS-AV-0006": {
        "distrattore_forte": "A",
        "motivo": "A mantiene forma, colore e posizione del punto, ma sbaglia il riempimento della figura."
    },
    "LOG-VIS-AV-0007": {
        "distrattore_forte": "B",
        "motivo": "B mantiene forma e colore corretti, ma sbaglia il numero di stelle."
    },
    "LOG-VIS-AV-0008": {
        "distrattore_forte": "C",
        "motivo": "C mantiene forma e colore corretti, ma sbaglia il numero di barre diagonali."
    },
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(dati, file, ensure_ascii=False, indent=2)


def trova_lista_domande(dati):
    if isinstance(dati, list):
        return dati

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "items", "data"]:
            valore = dati.get(chiave)

            if isinstance(valore, list):
                return valore

    raise ValueError("Non riesco a trovare la lista delle domande.")


def main():
    dati = carica_json(LOGICA_VISIVA_FILE)
    lista_domande = trova_lista_domande(dati)

    domande_corrette = 0

    for domanda in lista_domande:
        if not isinstance(domanda, dict):
            continue

        id_domanda = domanda.get("id")

        if id_domanda not in DISTRACTORI_FORTI:
            continue

        dati_distrattore = DISTRACTORI_FORTI[id_domanda]

        domanda["distrattore_forte"] = dati_distrattore["distrattore_forte"]
        domanda["motivo_distrattore_forte"] = dati_distrattore["motivo"]

        domande_corrette += 1

    salva_json(LOGICA_VISIVA_FILE, dati)

    print("----- DISTRACTORI FORTI LOGICA VISIVA SISTEMATI -----")
    print("Domande aggiornate:", domande_corrette)
    print("File aggiornato:", LOGICA_VISIVA_FILE)


main()
