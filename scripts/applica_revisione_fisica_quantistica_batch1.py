from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

FQ_JSON = ROOT / "data" / "fisica_quantistica.json"
BACKUP_TMP = Path("/tmp/fisica_quantistica_prima_revisione_batch1.json")

REVISIONI = {
    "FQ_001": {
        "opzioni": [
            "Una quantità minima e discreta con cui può presentarsi una grandezza fisica",
            "Un intervallo continuo di valori che una grandezza fisica può assumere liberamente",
            "Una forza macroscopica che agisce soltanto su oggetti visibili",
            "Una traiettoria classica descritta con precisione da una particella materiale",
        ],
        "risposta_corretta": "Una quantità minima e discreta con cui può presentarsi una grandezza fisica",
        "spiegazione": (
            "In fisica quantistica, un quanto indica una quantità discreta, cioè non divisibile "
            "in valori arbitrariamente piccoli all’interno del modello considerato."
        ),
    },

    "FQ_004": {
        "opzioni": [
            "Gli oggetti microscopici possono mostrare proprietà ondulatorie e corpuscolari",
            "Gli oggetti microscopici passano da onda classica a particella solo per attrito",
            "Le onde quantistiche sono semplici vibrazioni meccaniche di un mezzo materiale",
            "Le particelle quantistiche seguono traiettorie classiche indipendenti dalla misura",
        ],
        "risposta_corretta": "Gli oggetti microscopici possono mostrare proprietà ondulatorie e corpuscolari",
        "spiegazione": (
            "Il dualismo onda-particella indica che sistemi come elettroni e fotoni possono mostrare "
            "aspetti ondulatori o corpuscolari a seconda dell’esperimento eseguito."
        ),
    },

    "FQ_007": {
        "opzioni": [
            "L’elettrone può assumere soltanto alcuni valori energetici permessi",
            "L’elettrone può assumere qualunque energia in modo continuo dentro l’atomo",
            "L’energia dell’elettrone dipende soltanto dalla temperatura dell’ambiente",
            "L’elettrone perde energia trasformandosi in una particella del nucleo",
        ],
        "risposta_corretta": "L’elettrone può assumere soltanto alcuni valori energetici permessi",
        "spiegazione": (
            "Dire che l’energia è quantizzata significa che l’elettrone in un atomo può trovarsi "
            "solo in certi livelli energetici permessi, non in qualunque valore intermedio."
        ),
    },

    "FQ_008": {
        "opzioni": [
            "Può emettere un fotone con energia pari alla differenza tra i due livelli",
            "Può assorbire un fotone per compensare la perdita di energia del passaggio",
            "Può trasformarsi in un protone perché cambia il livello energetico atomico",
            "Può uscire dal nucleo perché il livello più basso riduce la carica elettrica",
        ],
        "risposta_corretta": "Può emettere un fotone con energia pari alla differenza tra i due livelli",
        "spiegazione": (
            "Quando un elettrone passa da un livello energetico più alto a uno più basso, "
            "la differenza di energia può essere emessa sotto forma di fotone."
        ),
    },

    "FQ_009": {
        "opzioni": [
            "Il risultato di una misura può essere descritto tramite probabilità",
            "La misura rivela un valore classico già fissato senza ruolo della probabilità",
            "La misura è possibile soltanto se l’oggetto osservato è macroscopico",
            "La misura modifica la massa della particella senza influire sullo stato",
        ],
        "risposta_corretta": "Il risultato di una misura può essere descritto tramite probabilità",
        "spiegazione": (
            "Nella fisica quantistica, prima della misura il risultato non è in generale determinato "
            "come in un modello classico semplice: viene descritto tramite probabilità."
        ),
    },

    "FQ_011": {
        "opzioni": [
            "Non si possono conoscere insieme con precisione arbitraria posizione e quantità di moto",
            "Non si può misurare la posizione perché gli strumenti hanno risoluzione insufficiente",
            "Non si può misurare la massa quando la particella attraversa un campo elettrico",
            "Non si può conoscere la velocità perché la luce cambia valore durante la misura",
        ],
        "risposta_corretta": "Non si possono conoscere insieme con precisione arbitraria posizione e quantità di moto",
        "spiegazione": (
            "Il principio di indeterminazione di Heisenberg non dipende solo da limiti tecnici "
            "degli strumenti: esprime un limite fondamentale sulla precisione simultanea di posizione e quantità di moto."
        ),
    },

    "FQ_013": {
        "opzioni": [
            "Un sistema può essere descritto come combinazione di più stati possibili prima della misura",
            "Un sistema oscilla rapidamente tra stati classici già definiti e osservabili direttamente",
            "Un sistema occupa due luoghi macroscopici perché ha energia termica elevata",
            "Un sistema perde energia fino a rimanere in un unico stato meccanico visibile",
        ],
        "risposta_corretta": "Un sistema può essere descritto come combinazione di più stati possibili prima della misura",
        "spiegazione": (
            "La sovrapposizione quantistica indica che un sistema può essere descritto come combinazione "
            "di stati possibili. La misura porta poi a uno dei risultati osservabili."
        ),
    },

    "FQ_014": {
        "opzioni": [
            "Una correlazione quantistica tra sistemi, tale che lo stato di uno è legato all’altro",
            "Un urto meccanico tra corpi macroscopici che trasferisce quantità di moto",
            "Una forza di attrazione che trasforma due particelle in un unico oggetto classico",
            "Un segnale luminoso che collega due particelle dopo ogni misurazione",
        ],
        "risposta_corretta": "Una correlazione quantistica tra sistemi, tale che lo stato di uno è legato all’altro",
        "spiegazione": (
            "L’entanglement è una correlazione quantistica tra sistemi. In certi casi non è possibile "
            "descrivere completamente lo stato di una parte senza considerare anche l’altra."
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

    print("----- REVISIONE FISICA QUANTISTICA BATCH 1 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/fisica_quantistica.json aggiornato.")


if __name__ == "__main__":
    main()
