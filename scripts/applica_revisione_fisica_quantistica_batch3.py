from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

FQ_JSON = ROOT / "data" / "fisica_quantistica.json"
BACKUP_TMP = Path("/tmp/fisica_quantistica_prima_revisione_batch3.json")

REVISIONI = {
    "FQ_034": {
        "opzioni": [
            "Perché gli elettroni possono passare solo tra livelli energetici permessi",
            "Perché gli elettroni hanno energie continue ma la luce viene filtrata dal gas",
            "Perché il nucleo vibra con frequenze classiche indipendenti dagli elettroni",
            "Perché lo spettroscopio divide una sorgente continua in righe senza legame con l’atomo",
        ],
        "risposta_corretta": "Perché gli elettroni possono passare solo tra livelli energetici permessi",
        "spiegazione": (
            "Gli spettri atomici hanno righe discrete perché gli elettroni negli atomi possono "
            "passare solo tra livelli energetici permessi. Ogni salto corrisponde a un fotone "
            "con energia specifica."
        ),
    },

    "FQ_035": {
        "opzioni": [
            "Che anche le particelle materiali possono essere associate a una lunghezza d’onda",
            "Che solo le particelle cariche possiedono massa quando attraversano una fenditura",
            "Che la luce perde il comportamento ondulatorio quando incontra un elettrone",
            "Che la lunghezza d’onda di una particella non dipende dalla sua quantità di moto",
        ],
        "risposta_corretta": "Che anche le particelle materiali possono essere associate a una lunghezza d’onda",
        "spiegazione": (
            "L’ipotesi di de Broglie afferma che anche le particelle materiali, come gli elettroni, "
            "possono avere proprietà ondulatorie. La loro lunghezza d’onda è collegata alla quantità di moto."
        ),
    },

    "FQ_036": {
        "opzioni": [
            "Perché mostra interferenza quantistica anche con particelle inviate una alla volta",
            "Perché dimostra che l’interferenza nasce solo da urti classici tra particelle",
            "Perché mostra che due fenditure eliminano la natura ondulatoria della luce",
            "Perché misura direttamente la massa degli elettroni osservando la gravità tra fenditure",
        ],
        "risposta_corretta": "Perché mostra interferenza quantistica anche con particelle inviate una alla volta",
        "spiegazione": (
            "L’esperimento della doppia fenditura è importante perché mostra che sistemi quantistici "
            "come fotoni o elettroni possono produrre figure di interferenza, anche quando vengono inviati singolarmente."
        ),
    },

    "FQ_037": {
        "opzioni": [
            "Che le ampiezze di probabilità si combinano, rafforzando o riducendo certi risultati",
            "Che le probabilità classiche si sommano direttamente senza effetti di fase",
            "Che due particelle fondono le loro masse formando un singolo oggetto macroscopico",
            "Che la misura cancella la possibilità di descrivere matematicamente lo stato",
        ],
        "risposta_corretta": "Che le ampiezze di probabilità si combinano, rafforzando o riducendo certi risultati",
        "spiegazione": (
            "L’interferenza quantistica riguarda le ampiezze di probabilità, non semplicemente "
            "le probabilità classiche. Le ampiezze possono combinarsi in modo costruttivo o distruttivo."
        ),
    },

    "FQ_038": {
        "opzioni": [
            "Uno stato puro è descritto da un singolo stato quantistico, uno misto da una distribuzione statistica",
            "Uno stato puro contiene una sola particella, uno misto contiene particelle di tipo diverso",
            "Uno stato misto è una sovrapposizione coerente descritta da un’unica funzione d’onda",
            "Uno stato puro è termico, mentre uno stato misto non richiede una descrizione matematica",
        ],
        "risposta_corretta": "Uno stato puro è descritto da un singolo stato quantistico, uno misto da una distribuzione statistica",
        "spiegazione": (
            "Uno stato puro è descritto da un singolo stato quantistico. Uno stato misto, invece, "
            "rappresenta una distribuzione statistica di possibili stati, spesso descritta tramite matrice densità."
        ),
    },
}


def carica_database(percorso):
    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return dati, None, dati

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "quiz", "items", "data", "database"]:
            if isinstance(dati.get(chiave), list):
                return dati[chiave], chiave, dati

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/fisica_quantistica.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive in modo preciso il concetto quantistico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio quantistico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not FQ_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {FQ_JSON}")

    shutil.copy2(FQ_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(FQ_JSON)

    domande_per_id = {
        str(domanda.get("id", "")): domanda
        for domanda in domande
        if isinstance(domanda, dict)
    }

    mancanti = [
        id_domanda
        for id_domanda in REVISIONI
        if id_domanda not in domande_per_id
    ]

    if mancanti:
        raise SystemExit(f"ERRORE: mancano queste domande nel JSON: {mancanti}")

    for id_domanda, revisione in REVISIONI.items():
        domanda = domande_per_id[id_domanda]
        domanda["opzioni"] = revisione["opzioni"]
        domanda["risposta_corretta"] = revisione["risposta_corretta"]
        domanda["spiegazione"] = revisione["spiegazione"]
        aggiorna_spiegazioni_opzioni(domanda, revisione)

    if chiave_lista is None:
        nuovo_database = domande
    else:
        dati_originali[chiave_lista] = domande
        nuovo_database = dati_originali

    FQ_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE FISICA QUANTISTICA BATCH 3 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/fisica_quantistica.json aggiornato.")


if __name__ == "__main__":
    main()
