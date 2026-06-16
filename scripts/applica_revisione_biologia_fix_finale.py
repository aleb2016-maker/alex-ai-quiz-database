from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

BIOLOGIA_JSON = ROOT / "data" / "biologia.json"
BACKUP_TMP = Path("/tmp/biologia_prima_fix_finale.json")

ID_DOMANDA = "BIO_025"

NUOVA_DOMANDA = {
    "opzioni": [
        "Ribosoma, dove l’RNA messaggero viene tradotto in catene di amminoacidi",
        "Reticolo endoplasmatico rugoso, che ospita ribosomi ma non traduce direttamente l’mRNA",
        "Nucleo, dove il DNA viene conservato e trascritto prima della traduzione",
        "Apparato di Golgi, che modifica e smista proteine già sintetizzate",
    ],
    "risposta_corretta": "Ribosoma, dove l’RNA messaggero viene tradotto in catene di amminoacidi",
    "spiegazione": (
        "I ribosomi partecipano direttamente alla sintesi proteica perché traducono l’RNA messaggero "
        "in catene di amminoacidi. Il reticolo endoplasmatico rugoso è un distrattore vicino: ospita "
        "ribosomi e partecipa alla gestione delle proteine, ma la traduzione avviene sui ribosomi."
    ),
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


def main():
    if not BIOLOGIA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {BIOLOGIA_JSON}")

    shutil.copy2(BIOLOGIA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(BIOLOGIA_JSON)

    domanda_trovata = None

    for domanda in domande:
        if isinstance(domanda, dict) and domanda.get("id") == ID_DOMANDA:
            domanda_trovata = domanda
            break

    if domanda_trovata is None:
        raise SystemExit(f"ERRORE: domanda {ID_DOMANDA} non trovata")

    domanda_trovata["opzioni"] = NUOVA_DOMANDA["opzioni"]
    domanda_trovata["risposta_corretta"] = NUOVA_DOMANDA["risposta_corretta"]
    domanda_trovata["spiegazione"] = NUOVA_DOMANDA["spiegazione"]
    domanda_trovata["spiegazioni_opzioni"] = {
        NUOVA_DOMANDA["opzioni"][0]: (
            "Corretta: il ribosoma è la struttura che traduce l’RNA messaggero "
            "in una catena di amminoacidi."
        ),
        NUOVA_DOMANDA["opzioni"][1]: (
            "Errata ma vicina: il reticolo endoplasmatico rugoso ospita ribosomi "
            "e partecipa alla gestione delle proteine, ma non traduce direttamente l’mRNA."
        ),
        NUOVA_DOMANDA["opzioni"][2]: (
            "Errata: il nucleo conserva il DNA e permette la trascrizione, "
            "ma la costruzione della proteina avviene sui ribosomi."
        ),
        NUOVA_DOMANDA["opzioni"][3]: (
            "Errata: l’apparato di Golgi modifica e smista proteine già prodotte, "
            "ma non costruisce direttamente la catena proteica."
        ),
    }

    if chiave_lista is None:
        nuovo_database = domande
    else:
        dati_originali[chiave_lista] = domande
        nuovo_database = dati_originali

    BIOLOGIA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- FIX FINALE BIOLOGIA -----")
    print(f"Domanda aggiornata: {ID_DOMANDA}")
    print("OK: distrattore forte aggiunto.")


if __name__ == "__main__":
    main()
