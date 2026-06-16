from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

CHIMICA_JSON = ROOT / "data" / "chimica.json"
BACKUP_TMP = Path("/tmp/chimica_prima_revisione_batch1.json")

REVISIONI = {
    "CHE_005": {
        "opzioni": [
            "Nel legame ionico si trasferiscono elettroni, nel covalente si condividono elettroni",
            "Nel legame ionico si condividono elettroni, nel covalente si formano ioni opposti",
            "Nel legame ionico si condividono protoni, nel covalente si trasferiscono neutroni",
            "Nel legame ionico si rompono nuclei atomici, nel covalente si fondono elettroni",
        ],
        "risposta_corretta": "Nel legame ionico si trasferiscono elettroni, nel covalente si condividono elettroni",
        "spiegazione": (
            "Nel legame ionico uno o più elettroni vengono trasferiti, formando ioni di carica opposta. "
            "Nel legame covalente, invece, gli atomi condividono coppie di elettroni."
        ),
    },

    "CHE_012": {
        "opzioni": [
            "Offre un percorso alternativo con energia di attivazione più bassa",
            "Aumenta l’energia di attivazione ma rende più stabili i reagenti",
            "Sposta l’equilibrio producendo più prodotto finale in ogni condizione",
            "Si consuma trasformandosi nel prodotto principale della reazione",
        ],
        "risposta_corretta": "Offre un percorso alternativo con energia di attivazione più bassa",
        "spiegazione": (
            "Un catalizzatore accelera una reazione perché fornisce un percorso con energia di attivazione più bassa. "
            "Non viene consumato in modo permanente e non cambia necessariamente la quantità di prodotto all’equilibrio."
        ),
    },

    "CHE_013": {
        "opzioni": [
            "Una sostanza pura ha composizione definita, una miscela può avere composizione variabile",
            "Una sostanza pura contiene componenti separabili fisicamente, una miscela no",
            "Una miscela ha formula chimica fissa, una sostanza pura cambia composizione",
            "Una miscela contiene un solo tipo di particella, una sostanza pura più componenti",
        ],
        "risposta_corretta": "Una sostanza pura ha composizione definita, una miscela può avere composizione variabile",
        "spiegazione": (
            "Una sostanza pura ha composizione definita e proprietà caratteristiche. "
            "Una miscela contiene più componenti e può avere proporzioni variabili."
        ),
    },

    "CHE_016": {
        "opzioni": [
            "Aumenta l’energia cinetica media e si muovono più velocemente",
            "Diminuisce l’energia cinetica media e si muovono più lentamente",
            "Aumenta la massa delle particelle senza cambiare il loro movimento",
            "Diminuisce la distanza tra particelle fino a formare un solido",
        ],
        "risposta_corretta": "Aumenta l’energia cinetica media e si muovono più velocemente",
        "spiegazione": (
            "Quando la temperatura di un gas aumenta, aumenta anche l’energia cinetica media delle sue particelle. "
            "Per questo le particelle si muovono mediamente più velocemente."
        ),
    },

    "CHE_018": {
        "opzioni": [
            "Contiene molta quantità di soluto rispetto alla quantità di solvente",
            "Contiene molto solvente rispetto alla quantità di soluto disciolto",
            "Contiene soluto non disciolto separato completamente dal solvente",
            "Contiene soltanto solvente puro senza particelle di soluto",
        ],
        "risposta_corretta": "Contiene molta quantità di soluto rispetto alla quantità di solvente",
        "spiegazione": (
            "Una soluzione concentrata contiene una quantità relativamente elevata di soluto rispetto al solvente. "
            "Non significa che il soluto sia per forza solido o non disciolto."
        ),
    },

    "CHE_019": {
        "opzioni": [
            "Il sistema libera energia verso l’ambiente, spesso sotto forma di calore",
            "Il sistema assorbe energia dall’ambiente per trasformare i reagenti",
            "Il sistema elimina massa perché gli atomi vengono distrutti nella reazione",
            "Il sistema blocca il trasferimento di energia tra reagenti e ambiente",
        ],
        "risposta_corretta": "Il sistema libera energia verso l’ambiente, spesso sotto forma di calore",
        "spiegazione": (
            "In una reazione esotermica il sistema libera energia verso l’ambiente, spesso come calore. "
            "La massa non scompare: gli atomi si riorganizzano formando nuove sostanze."
        ),
    },

    "CHE_020": {
        "opzioni": [
            "Ha quattro elettroni di valenza e può formare legami covalenti stabili e catene",
            "Ha otto elettroni di valenza e forma solo legami ionici con elementi metallici",
            "Ha un solo elettrone esterno e può legarsi soltanto con atomi di idrogeno",
            "Ha un nucleo instabile e cambia elemento durante ogni reazione organica",
        ],
        "risposta_corretta": "Ha quattro elettroni di valenza e può formare legami covalenti stabili e catene",
        "spiegazione": (
            "Il carbonio può formare moltissimi composti perché ha quattro elettroni di valenza "
            "e può creare legami covalenti stabili, anche con altri atomi di carbonio, formando catene e strutture complesse."
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

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/chimica.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}
    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive in modo preciso il concetto chimico richiesto."
        else:
            spiegazioni[opzione] = (
                "Errata: è collegata allo stesso argomento, ma contiene un dettaglio chimico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not CHIMICA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {CHIMICA_JSON}")

    shutil.copy2(CHIMICA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    domande, chiave_lista, dati_originali = carica_database(CHIMICA_JSON)

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

    CHIMICA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE CHIMICA BATCH 1 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/chimica.json aggiornato.")


if __name__ == "__main__":
    main()
