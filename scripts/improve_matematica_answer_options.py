import json
from pathlib import Path


PERCORSO_DATA = Path("data")
PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


CORREZIONI_MATEMATICA = {
    "MAT-FAC-0006": {
        "opzioni": [
            "32",
            "50",
            "25",
            "36"
        ],
        "risposta_corretta": "32",
        "spiegazione": (
            "Prima si esegue la moltiplicazione: 7 × 2 = 14. "
            "Poi si somma 18 + 14 = 32. "
            "Il risultato 50 nasce dall'errore di fare prima 18 + 7 e poi moltiplicare per 2."
        )
    },

    "MAT-FAC-0007": {
    "domanda": "Quale frazione è equivalente a 1/2?",
    "opzioni": [
        "2/4",
        "2/3",
        "3/4",
        "4/6"
    ],
    "risposta_corretta": "2/4",
    "spiegazione": (
        "Una frazione equivalente a 1/2 deve avere lo stesso valore. "
        "2/4 si semplifica dividendo numeratore e denominatore per 2, ottenendo 1/2. "
        "2/3, 3/4 e 4/6 sono frazioni vicine come forma, ma non valgono 1/2."
    )
},

    "MAT-FAC-0008": {
        "opzioni": [
            "40 cm²",
            "13 cm²",
            "26 cm²",
            "80 cm²"
        ],
        "risposta_corretta": "40 cm²",
        "spiegazione": (
            "L'area del rettangolo si calcola con base × altezza. "
            "Quindi 8 × 5 = 40 cm². "
            "13 nasce da 8 + 5, 26 dal perimetro calcolato con 2 × (8 + 5), "
            "mentre 80 è il doppio dell'area."
        )
    },

    "MAT-INT-0004": {
        "domanda": "Risolvi l'equazione: 2(x + 4) = 22.",
        "opzioni": [
            "x = 5",
            "x = 7",
            "x = 9",
            "x = 11"
        ],
        "risposta_corretta": "x = 7",
        "spiegazione": (
            "Prima dividiamo entrambi i membri per 2: x + 4 = 11. "
            "Poi sottraiamo 4 da entrambi i lati: x = 7. "
            "Questa domanda è diversa da una semplice equazione 3x + 5 = 20 perché richiede anche di gestire le parentesi."
        )
    },

    "MAT-INT-0008": {
        "opzioni": [
            "6 cm",
            "8 cm",
            "9 cm",
            "12 cm"
        ],
        "risposta_corretta": "9 cm",
        "spiegazione": (
            "Il perimetro del quadrato è formato da 4 lati uguali. "
            "Quindi il lato misura 36 / 4 = 9 cm. "
            "12 nascerebbe dividendo per 3, 8 è vicino ma non corretto, "
            "mentre 6 sarebbe una divisione errata per 6."
        )
    },

    "MAT-INT-0009": {
        "opzioni": [
            "3/10",
            "7/10",
            "3/7",
            "1/3"
        ],
        "risposta_corretta": "3/10",
        "spiegazione": (
            "La probabilità si calcola facendo casi favorevoli diviso casi totali. "
            "Le palline rosse sono 3, mentre le palline totali sono 3 + 7 = 10. "
            "Quindi la probabilità è 3/10. "
            "7/10 sarebbe la probabilità di estrarre una blu, 3/7 confronta rosse e blu ma non usa il totale, "
            "mentre 1/3 non rappresenta il rapporto corretto."
        )
    },

    "MAT-AV-0007": {
        "opzioni": [
            "8",
            "10",
            "12",
            "16"
        ],
        "risposta_corretta": "12",
        "spiegazione": (
            "Per la prima cifra ci sono 4 scelte. "
            "Per la seconda restano 3 scelte, perché non si può ripetere la cifra. "
            "Quindi 4 × 3 = 12. "
            "16 sarebbe corretto solo se la ripetizione fosse permessa."
        )
    },

    "MAT-AV-0009": {
        "opzioni": [
            "20%",
            "25%",
            "30%",
            "35%"
        ],
        "risposta_corretta": "25%",
        "spiegazione": (
            "L'aumento è 150 - 120 = 30. "
            "La percentuale di aumento si calcola rispetto al valore iniziale, quindi 30 / 120 × 100 = 25%. "
            "30% nasce dall'errore di confondere l'aumento assoluto 30 con la percentuale."
        )
    }
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, contenuto):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            contenuto,
            file,
            ensure_ascii=False,
            indent=2
        )


def aggiorna_file_json(percorso):
    domande = carica_json(percorso)
    modifiche = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in CORREZIONI_MATEMATICA:
            correzione = CORREZIONI_MATEMATICA[id_domanda]

            if "domanda" in correzione:
                domanda["domanda"] = correzione["domanda"]

            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]

            modifiche += 1

    if modifiche > 0:
        salva_json(percorso, domande)

    return modifiche


def aggiorna_script_create_batch():
    if not PERCORSO_BATCH.exists():
        return

    domande_batch = carica_json(PERCORSO_BATCH)

    contenuto_lista = json.dumps(
        domande_batch,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script crea il primo batch di espansione.
# Obiettivo: portare il database da 27 a 100 domande totali.
# Le nuove domande vengono salvate in data/espansione/batch_100.json


PERCORSO_OUTPUT = Path("data/espansione/batch_100.json")


nuove_domande = {contenuto_lista}


def main():
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            nuove_domande,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("File creato correttamente:")
    print(PERCORSO_OUTPUT)
    print(f"Domande create: {{len(nuove_domande)}}")


main()
'''

    PERCORSO_SCRIPT_BATCH.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    modifiche_totali = 0

    for percorso in sorted(PERCORSO_DATA.rglob("*.json")):
        modifiche_file = aggiorna_file_json(percorso)

        if modifiche_file > 0:
            modifiche_totali += modifiche_file
            print(f"Aggiornato {percorso}: {modifiche_file} domande")

    aggiorna_script_create_batch()

    print()
    print("Revisione Matematica completata.")
    print(f"Domande Matematica aggiornate: {modifiche_totali}")


main()
