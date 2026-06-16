from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

FISICA_JSON = ROOT / "data" / "fisica.json"
BACKUP_TMP = Path("/tmp/fisica_prima_revisione_batch3.json")

REVISIONI = {
    "FIS_033": {
        "opzioni": [
            "Perché interagisce con il campo magnetico terrestre e si orienta lungo le sue linee",
            "Perché viene attirato dalla forza di gravità verso il punto più basso dell’orizzonte",
            "Perché segue la rotazione apparente del Sole durante il movimento della Terra",
            "Perché reagisce alla pressione atmosferica cambiando direzione in base al vento",
        ],
        "risposta_corretta": "Perché interagisce con il campo magnetico terrestre e si orienta lungo le sue linee",
        "spiegazione": (
            "L’ago della bussola è magnetizzato e interagisce con il campo magnetico terrestre. "
            "Per questo tende ad allinearsi lungo la direzione del campo magnetico locale."
        ),
    },

    "FIS_034": {
        "opzioni": [
            "La sua energia interna può aumentare, causando aumento di temperatura o cambiamento di stato",
            "La sua massa aumenta perché il calore si trasforma direttamente in materia stabile",
            "La sua temperatura diminuisce perché il calore sottrae energia alle particelle",
            "La sua energia interna resta invariata mentre cambia soltanto il colore esterno",
        ],
        "risposta_corretta": "La sua energia interna può aumentare, causando aumento di temperatura o cambiamento di stato",
        "spiegazione": (
            "Quando un corpo riceve calore, aumenta l’energia trasferita al sistema. "
            "Questo può far crescere la temperatura oppure produrre un cambiamento di stato."
        ),
    },

    "FIS_035": {
        "opzioni": [
            "Il calore è energia trasferita, la temperatura misura lo stato termico di un corpo",
            "Il calore misura solo la velocità del corpo, la temperatura misura solo la sua massa",
            "Il calore è una proprietà fissa del materiale, la temperatura è una forza applicata",
            "Il calore indica il volume del corpo, la temperatura indica il peso del corpo",
        ],
        "risposta_corretta": "Il calore è energia trasferita, la temperatura misura lo stato termico di un corpo",
        "spiegazione": (
            "Il calore è energia che si trasferisce tra corpi a temperatura diversa. "
            "La temperatura, invece, descrive lo stato termico di un corpo ed è collegata all’agitazione delle sue particelle."
        ),
    },

    "FIS_036": {
        "opzioni": [
            "Il calore passa dal corpo più caldo a quello più freddo fino all’equilibrio termico",
            "Il calore passa dal corpo più freddo a quello più caldo senza bisogno di lavoro esterno",
            "I due corpi scambiano massa finché diventano composti dalla stessa sostanza",
            "Le temperature si allontanano perché il contatto impedisce ogni scambio energetico",
        ],
        "risposta_corretta": "Il calore passa dal corpo più caldo a quello più freddo fino all’equilibrio termico",
        "spiegazione": (
            "Quando due corpi a temperatura diversa vengono messi a contatto, il calore fluisce "
            "dal corpo più caldo a quello più freddo finché si raggiunge l’equilibrio termico."
        ),
    },

    "FIS_037": {
        "opzioni": [
            "Perché aumenta il braccio della forza e permette di ottenere lo stesso momento con forza minore",
            "Perché elimina il peso del carico trasformandolo in una forza orizzontale nulla",
            "Perché riduce la massa del carico quando il punto di appoggio viene spostato",
            "Perché annulla la gravità sul carico se la leva è abbastanza lunga",
        ],
        "risposta_corretta": "Perché aumenta il braccio della forza e permette di ottenere lo stesso momento con forza minore",
        "spiegazione": (
            "Una leva permette di ridurre la forza necessaria aumentando il braccio della forza applicata. "
            "Il vantaggio meccanico dipende dal rapporto tra i bracci della leva."
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

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/fisica.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive in modo preciso il concetto fisico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio fisico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not FISICA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {FISICA_JSON}")

    shutil.copy2(FISICA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(FISICA_JSON)

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

    FISICA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE FISICA BATCH 3 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/fisica.json aggiornato.")


if __name__ == "__main__":
    main()
