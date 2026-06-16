from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

SCIENZE_JSON = ROOT / "data" / "scienze.json"
BACKUP_TMP = Path("/tmp/scienze_prima_revisione_batch1.json")

REVISIONI = {
    "SCI_001": {
        "opzioni": [
            "Il nucleo, perché contiene il DNA e coordina molte attività cellulari",
            "Il mitocondrio, perché produce gran parte dell’ATP usato dalla cellula",
            "Il ribosoma, perché costruisce proteine leggendo le informazioni genetiche",
            "La membrana cellulare, perché regola gli scambi con l’ambiente esterno",
        ],
        "risposta_corretta": "Il mitocondrio, perché produce gran parte dell’ATP usato dalla cellula",
        "spiegazione": (
            "Il mitocondrio è l’organulo principalmente coinvolto nella produzione di ATP, "
            "la molecola che la cellula usa come fonte immediata di energia."
        ),
    },

    "SCI_005": {
        "opzioni": [
            "Ossigeno, che viene liberato come prodotto durante la fotosintesi",
            "Azoto, che le piante usano soprattutto tramite composti presenti nel suolo",
            "Anidride carbonica, che viene assorbita per produrre zuccheri",
            "Idrogeno molecolare, che non è il gas principale assorbito dalle foglie",
        ],
        "risposta_corretta": "Anidride carbonica, che viene assorbita per produrre zuccheri",
        "spiegazione": (
            "Durante la fotosintesi le piante assorbono anidride carbonica e acqua. "
            "Usando l’energia luminosa producono zuccheri e liberano ossigeno."
        ),
    },

    "SCI_006": {
        "opzioni": [
            "pH uguale a 7, che indica una soluzione neutra",
            "pH maggiore di 7, che indica una soluzione basica",
            "pH minore di 7, che indica una soluzione acida",
            "pH vicino a 14, che indica una soluzione fortemente basica",
        ],
        "risposta_corretta": "pH minore di 7, che indica una soluzione acida",
        "spiegazione": (
            "La scala del pH distingue soluzioni acide, neutre e basiche. "
            "Un pH minore di 7 indica una soluzione acida."
        ),
    },

    "SCI_007": {
        "opzioni": [
            "L’accelerazione aumenta, perché a massa costante dipende dalla forza risultante",
            "L’accelerazione diminuisce, perché una forza maggiore riduce il moto del corpo",
            "L’accelerazione resta nulla, perché la massa impedisce qualunque variazione",
            "L’accelerazione diventa indipendente dalla forza applicata al corpo",
        ],
        "risposta_corretta": "L’accelerazione aumenta, perché a massa costante dipende dalla forza risultante",
        "spiegazione": (
            "Secondo la seconda legge di Newton, F = m · a. "
            "Se la massa resta costante e la forza aumenta, anche l’accelerazione aumenta."
        ),
    },

    "SCI_008": {
        "opzioni": [
            "ATP, che fornisce energia immediata a molte reazioni cellulari",
            "DNA, che contiene le istruzioni genetiche ereditarie",
            "Glucosio, che è uno zucchero usato come fonte energetica",
            "Emoglobina, che trasporta ossigeno nei globuli rossi",
        ],
        "risposta_corretta": "DNA, che contiene le istruzioni genetiche ereditarie",
        "spiegazione": (
            "Il DNA contiene le informazioni genetiche ereditarie degli esseri viventi. "
            "Queste istruzioni guidano molte funzioni cellulari e possono essere trasmesse alla discendenza."
        ),
    },

    "SCI_011": {
        "opzioni": [
            "La massa dipende dal luogo, mentre il peso resta uguale su ogni pianeta",
            "La massa indica quantità di materia, il peso è la forza gravitazionale sulla massa",
            "Massa e peso indicano la stessa grandezza ma con due nomi diversi",
            "Il peso si misura in chilogrammi, mentre la massa si misura in Newton",
        ],
        "risposta_corretta": "La massa indica quantità di materia, il peso è la forza gravitazionale sulla massa",
        "spiegazione": (
            "La massa descrive la quantità di materia di un corpo. "
            "Il peso, invece, è una forza e dipende dall’attrazione gravitazionale."
        ),
    },

    "SCI_013": {
        "opzioni": [
            "Delimita la cellula e regola gli scambi con l’ambiente esterno",
            "Produce la maggior parte dell’ATP usato nelle cellule eucariotiche",
            "Contiene il materiale genetico principale nelle cellule eucariotiche",
            "Costruisce proteine assemblando amminoacidi nel citoplasma",
        ],
        "risposta_corretta": "Delimita la cellula e regola gli scambi con l’ambiente esterno",
        "spiegazione": (
            "La membrana cellulare delimita la cellula e controlla il passaggio di sostanze "
            "tra interno ed esterno, contribuendo all’equilibrio cellulare."
        ),
    },

    "SCI_023": {
        "opzioni": [
            "Acida, perché ha un valore di pH inferiore a 7",
            "Basica, perché ha un valore di pH superiore a 7",
            "Neutra, perché ha un valore di pH uguale a 7",
            "Tampone, perché impedisce qualunque variazione del pH",
        ],
        "risposta_corretta": "Acida, perché ha un valore di pH inferiore a 7",
        "spiegazione": (
            "Una soluzione con pH minore di 7 è considerata acida. "
            "Una soluzione con pH uguale a 7 è neutra, mentre con pH maggiore di 7 è basica."
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

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/scienze.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive in modo preciso il concetto scientifico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio scientifico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not SCIENZE_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {SCIENZE_JSON}")

    shutil.copy2(SCIENZE_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(SCIENZE_JSON)

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

    SCIENZE_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE SCIENZE GENERALI BATCH 1 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/scienze.json aggiornato.")


if __name__ == "__main__":
    main()
