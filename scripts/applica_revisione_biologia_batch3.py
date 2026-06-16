from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

BIOLOGIA_JSON = ROOT / "data" / "biologia.json"
BACKUP_TMP = Path("/tmp/biologia_prima_revisione_batch3.json")

REVISIONI = {
    "BIO_032": {
        "opzioni": [
            "Può modificare il livello o il momento di espressione di un gene",
            "Può cambiare direttamente la sequenza di amminoacidi di ogni proteina prodotta",
            "Può eliminare il ribosoma che traduce l’RNA messaggero nel citoplasma",
            "Può trasformare una sequenza regolatrice in un cromosoma indipendente",
        ],
        "risposta_corretta": "Può modificare il livello o il momento di espressione di un gene",
        "spiegazione": (
            "Una mutazione in una sequenza regolatrice non cambia necessariamente la proteina, "
            "ma può modificare quando, dove o quanto un gene viene espresso."
        ),
    },

    "BIO_037": {
        "opzioni": [
            "Si attiva una risposta cellulare specifica tramite vie di segnalazione interne",
            "Il recettore trasforma direttamente l’ormone in una nuova proteina strutturale",
            "La cellula bersaglio perde il proprio DNA e viene sostituita dall’ormone",
            "L’ormone entra nel nucleo e replica tutti i geni della cellula bersaglio",
        ],
        "risposta_corretta": "Si attiva una risposta cellulare specifica tramite vie di segnalazione interne",
        "spiegazione": (
            "Quando un ormone si lega al recettore corretto, la cellula bersaglio attiva una risposta specifica. "
            "Il legame ormone-recettore avvia segnali intracellulari o modifica l’attività di alcuni geni."
        ),
    },

    "BIO_038": {
        "opzioni": [
            "Ha meno varianti ereditarie utili su cui la selezione naturale può agire",
            "Produce più mutazioni vantaggiose quando l’ambiente cambia rapidamente",
            "Elimina la competizione interna perché tutti gli individui sono geneticamente simili",
            "Rende ogni individuo capace di adattarsi allo stesso modo a qualsiasi pressione ambientale",
        ],
        "risposta_corretta": "Ha meno varianti ereditarie utili su cui la selezione naturale può agire",
        "spiegazione": (
            "Una popolazione con bassa variabilità genetica possiede meno alternative ereditarie. "
            "Se l’ambiente cambia, è più probabile che manchino individui con caratteristiche adatte alla nuova condizione."
        ),
    },

    "BIO_039": {
        "opzioni": [
            "Una risposta che contrasta una variazione e riporta una variabile verso l’equilibrio",
            "Una risposta che amplifica una variazione finché il sistema perde ogni controllo",
            "Un segnale che elimina il recettore e impedisce alla cellula di comunicare",
            "Un processo che sostituisce tutti gli ormoni con enzimi digestivi nel sangue",
        ],
        "risposta_corretta": "Una risposta che contrasta una variazione e riporta una variabile verso l’equilibrio",
        "spiegazione": (
            "Il feedback negativo è un meccanismo di regolazione: quando una variabile si allontana "
            "dal valore corretto, il sistema attiva risposte che tendono a riportarla verso l’equilibrio."
        ),
    },

    "BIO_040": {
        "opzioni": [
            "Elimina molti batteri sensibili e favorisce la sopravvivenza di quelli resistenti",
            "Rende ogni batterio sensibile più debole senza modificare la pressione selettiva",
            "Trasforma direttamente gli antibiotici in nutrienti usati dai batteri comuni",
            "Blocca la riproduzione dei batteri resistenti e lascia crescere solo quelli sensibili",
        ],
        "risposta_corretta": "Elimina molti batteri sensibili e favorisce la sopravvivenza di quelli resistenti",
        "spiegazione": (
            "L’uso scorretto degli antibiotici può selezionare batteri resistenti: i batteri sensibili vengono eliminati, "
            "mentre quelli resistenti sopravvivono e possono moltiplicarsi."
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

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/biologia.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive in modo preciso il concetto biologico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio biologico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not BIOLOGIA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {BIOLOGIA_JSON}")

    shutil.copy2(BIOLOGIA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(BIOLOGIA_JSON)

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

    BIOLOGIA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE BIOLOGIA BATCH 3 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/biologia.json aggiornato.")


if __name__ == "__main__":
    main()
