from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

FQ_JSON = ROOT / "data" / "fisica_quantistica.json"
BACKUP_TMP = Path("/tmp/fisica_quantistica_prima_revisione_batch2.json")

REVISIONI = {
    "FQ_017": {
        "opzioni": [
            "Due fermioni identici non possono occupare lo stesso stato quantico completo",
            "Due fermioni identici possono condividere lo stesso stato se hanno energia simile",
            "Due bosoni identici sono esclusi dallo stesso livello energetico atomico",
            "Due particelle classiche sono obbligate ad avere spin opposto nello stesso punto",
        ],
        "risposta_corretta": "Due fermioni identici non possono occupare lo stesso stato quantico completo",
        "spiegazione": (
            "Il principio di esclusione di Pauli afferma che due fermioni identici non possono "
            "trovarsi nello stesso identico stato quantico completo. È fondamentale per spiegare "
            "la struttura elettronica degli atomi."
        ),
    },

    "FQ_019": {
        "opzioni": [
            "La descrizione probabilistica passa a uno stato compatibile con il risultato misurato",
            "La funzione d’onda diventa una traiettoria classica visibile dopo ogni osservazione",
            "La misura trasforma la particella in un oggetto macroscopico con massa maggiore",
            "Lo stato quantistico perde ogni informazione fisica e non descrive più il sistema",
        ],
        "risposta_corretta": "La descrizione probabilistica passa a uno stato compatibile con il risultato misurato",
        "spiegazione": (
            "Nell’idea del collasso, la funzione d’onda che descrive più risultati possibili "
            "viene aggiornata a uno stato compatibile con il risultato ottenuto dalla misura."
        ),
    },

    "FQ_022": {
        "opzioni": [
            "Un oggetto matematico che agisce sullo stato quantistico e rappresenta osservabili o trasformazioni",
            "Una particella materiale che trasporta energia tra due livelli atomici vicini",
            "Una grandezza classica usata solo per indicare la posizione precisa dell’elettrone",
            "Un campo macroscopico che sostituisce la funzione d’onda durante una misura",
        ],
        "risposta_corretta": "Un oggetto matematico che agisce sullo stato quantistico e rappresenta osservabili o trasformazioni",
        "spiegazione": (
            "In meccanica quantistica un operatore è un oggetto matematico che agisce sugli stati. "
            "Può rappresentare osservabili fisiche, come energia o quantità di moto, oppure trasformazioni."
        ),
    },

    "FQ_024": {
        "opzioni": [
            "Indica se due operatori sono compatibili e se l’ordine delle operazioni cambia il risultato",
            "Indica la distanza classica tra due particelle dopo una collisione elastica",
            "Misura la quantità di energia persa da un elettrone durante un salto orbitale",
            "Stabilisce la massa assoluta di una particella indipendentemente dallo stato quantico",
        ],
        "risposta_corretta": "Indica se due operatori sono compatibili e se l’ordine delle operazioni cambia il risultato",
        "spiegazione": (
            "Il commutatore misura quanto conta l’ordine con cui due operatori vengono applicati. "
            "Se il commutatore non è nullo, le osservabili associate non sono pienamente compatibili "
            "e possono essere legate a relazioni di indeterminazione."
        ),
    },

    "FQ_025": {
        "opzioni": [
            "Che certe correlazioni quantistiche non sono spiegabili con semplici variabili nascoste locali",
            "Che la meccanica quantistica coincide con un modello classico deterministico locale",
            "Che ogni misura quantistica rivela proprietà già fissate e indipendenti dal contesto",
            "Che l’entanglement è un effetto dovuto soltanto a errori sperimentali ordinari",
        ],
        "risposta_corretta": "Che certe correlazioni quantistiche non sono spiegabili con semplici variabili nascoste locali",
        "spiegazione": (
            "La violazione sperimentale delle disuguaglianze di Bell indica che alcune correlazioni "
            "quantistiche non possono essere spiegate da modelli classici basati su variabili nascoste locali semplici."
        ),
    },

    "FQ_027": {
        "opzioni": [
            "I fermioni hanno spin semi-intero e rispettano Pauli; i bosoni hanno spin intero",
            "I fermioni hanno spin intero e possono accumularsi nello stesso stato come i fotoni",
            "I bosoni hanno spin semi-intero e formano la struttura elettronica degli atomi",
            "Fermioni e bosoni differiscono solo per la massa, non per spin o comportamento statistico",
        ],
        "risposta_corretta": "I fermioni hanno spin semi-intero e rispettano Pauli; i bosoni hanno spin intero",
        "spiegazione": (
            "I fermioni hanno spin semi-intero e obbediscono al principio di esclusione di Pauli. "
            "I bosoni hanno spin intero e possono occupare collettivamente lo stesso stato quantico."
        ),
    },

    "FQ_029": {
        "opzioni": [
            "Regioni descritte da probabilità in cui è più probabile trovare l’elettrone",
            "Traiettorie circolari precise percorse dall’elettrone come un pianeta intorno al Sole",
            "Superfici materiali solide che separano elettroni di atomi diversi nello spazio",
            "Percorsi visibili che l’elettrone segue quando viene osservato con un microscopio",
        ],
        "risposta_corretta": "Regioni descritte da probabilità in cui è più probabile trovare l’elettrone",
        "spiegazione": (
            "Gli orbitali non sono orbite classiche. Descrivono distribuzioni di probabilità "
            "associate alla possibilità di trovare l’elettrone in certe regioni dello spazio."
        ),
    },

    "FQ_033": {
        "opzioni": [
            "Ha energia maggiore, perché l’energia del fotone è proporzionale alla frequenza",
            "Ha energia minore, perché frequenza ed energia del fotone sono inversamente proporzionali",
            "Ha la stessa energia, perché l’energia dipende solo dalla velocità della luce",
            "Ha massa maggiore, perché aumentando la frequenza il fotone diventa particella materiale",
        ],
        "risposta_corretta": "Ha energia maggiore, perché l’energia del fotone è proporzionale alla frequenza",
        "spiegazione": (
            "L’energia di un fotone è data dalla relazione E = h f. "
            "Quindi, se la frequenza aumenta, aumenta anche l’energia del fotone."
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

    print("----- REVISIONE FISICA QUANTISTICA BATCH 2 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/fisica_quantistica.json aggiornato.")


if __name__ == "__main__":
    main()
