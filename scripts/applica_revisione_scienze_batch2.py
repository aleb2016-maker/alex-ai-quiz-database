from pathlib import Path
import json
import shutil

ROOT = Path(__file__).resolve().parents[1]

SCIENZE_JSON = ROOT / "data" / "scienze.json"
BACKUP_TMP = Path("/tmp/scienze_prima_revisione_batch2.json")

REVISIONI = {
    "SCI_029": {
        "opzioni": [
            "Perché una terza variabile o una relazione indiretta può spiegare l’associazione",
            "Perché due dati che crescono insieme indicano già una causa diretta certa",
            "Perché una correlazione numerica elimina il bisogno di controllare altre ipotesi",
            "Perché bastano pochi esempi osservati per stabilire un rapporto causale generale",
        ],
        "risposta_corretta": "Perché una terza variabile o una relazione indiretta può spiegare l’associazione",
        "spiegazione": (
            "Una correlazione indica che due fenomeni variano insieme, ma non dimostra da sola "
            "che uno provochi l’altro. Potrebbe esserci una terza variabile o una relazione indiretta."
        ),
    },

    "SCI_031": {
        "opzioni": [
            "Verso il centro della traiettoria circolare, per cambiare la direzione della velocità",
            "Nella direzione tangente alla traiettoria, per aumentare il modulo della velocità",
            "Verso l’esterno della traiettoria, come effetto della rotazione del corpo",
            "In direzione opposta al moto, perché il corpo deve rallentare a ogni giro",
        ],
        "risposta_corretta": "Verso il centro della traiettoria circolare, per cambiare la direzione della velocità",
        "spiegazione": (
            "Nel moto circolare uniforme il modulo della velocità resta costante, ma la direzione cambia. "
            "L’accelerazione centripeta è diretta verso il centro della traiettoria."
        ),
    },

    "SCI_033": {
        "opzioni": [
            "Inizia su superfici prive di suolo sviluppato, con colonizzazione graduale",
            "Inizia in ecosistemi maturi dopo una piccola variazione stagionale",
            "Consiste nello spostamento rapido di una specie animale verso un nuovo clima",
            "Consiste nella sostituzione immediata di tutti i produttori con consumatori",
        ],
        "risposta_corretta": "Inizia su superfici prive di suolo sviluppato, con colonizzazione graduale",
        "spiegazione": (
            "La successione ecologica primaria avviene in ambienti inizialmente privi di suolo sviluppato, "
            "come rocce nude o superfici lasciate da ghiacciai. Gli organismi colonizzano l’area in modo graduale."
        ),
    },

    "SCI_035": {
        "opzioni": [
            "Esiste un limite alla precisione simultanea di posizione e quantità di moto",
            "La posizione e la quantità di moto possono essere determinate insieme senza limite",
            "La massa della particella si annulla quando viene effettuata una misura",
            "La luce interrompe la propagazione quando interagisce con un atomo isolato",
        ],
        "risposta_corretta": "Esiste un limite alla precisione simultanea di posizione e quantità di moto",
        "spiegazione": (
            "Il principio di indeterminazione di Heisenberg esprime un limite fondamentale: "
            "non si possono conoscere simultaneamente posizione e quantità di moto con precisione arbitraria."
        ),
    },

    "SCI_036": {
        "opzioni": [
            "Abbassa l’energia di attivazione e accelera la reazione senza consumarsi stabilmente",
            "Aumenta la quantità massima di prodotto oltre il limite imposto dai reagenti",
            "Trasforma una reazione chimica ordinaria in un processo nucleare",
            "Elimina la necessità dei reagenti facendo avvenire la reazione da solo",
        ],
        "risposta_corretta": "Abbassa l’energia di attivazione e accelera la reazione senza consumarsi stabilmente",
        "spiegazione": (
            "Un catalizzatore accelera una reazione abbassando l’energia di attivazione. "
            "Non viene consumato stabilmente nel processo e non aumenta il massimo teorico dei prodotti."
        ),
    },

    "SCI_038": {
        "opzioni": [
            "Un meccanismo che riduce una variazione e riporta il sistema verso l’equilibrio",
            "Un meccanismo che amplifica una variazione allontanando il sistema dall’equilibrio",
            "Una risposta casuale che non dipende dallo stato interno dell’organismo",
            "Una reazione che interrompe le funzioni vitali invece di regolarle",
        ],
        "risposta_corretta": "Un meccanismo che riduce una variazione e riporta il sistema verso l’equilibrio",
        "spiegazione": (
            "Il feedback negativo è un meccanismo di regolazione che contrasta una variazione. "
            "Serve a riportare il sistema verso condizioni di equilibrio, come avviene nell’omeostasi."
        ),
    },

    "SCI_039": {
        "opzioni": [
            "L’acqua attraversa una membrana semipermeabile verso la soluzione più concentrata",
            "I soluti attraversano liberamente la membrana verso la soluzione meno concentrata",
            "L’acqua si trasforma chimicamente in sale durante il passaggio attraverso la membrana",
            "La membrana si dissolve per permettere il passaggio indistinto di tutte le sostanze",
        ],
        "risposta_corretta": "L’acqua attraversa una membrana semipermeabile verso la soluzione più concentrata",
        "spiegazione": (
            "Durante l’osmosi l’acqua attraversa una membrana semipermeabile. "
            "Il movimento avviene verso la soluzione con maggiore concentrazione di soluti."
        ),
    },

    "SCI_040": {
        "opzioni": [
            "La massa misura la quantità di materia, il peso è una forza dovuta alla gravità",
            "La massa misura la forza gravitazionale, il peso misura la quantità di materia",
            "La massa si misura in Newton, mentre il peso si misura in chilogrammi",
            "La massa dipende dal pianeta, mentre il peso resta uguale cambiando gravità",
        ],
        "risposta_corretta": "La massa misura la quantità di materia, il peso è una forza dovuta alla gravità",
        "spiegazione": (
            "La massa indica la quantità di materia di un corpo e si misura in chilogrammi. "
            "Il peso è una forza dovuta alla gravità e si misura in Newton."
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

    print("----- REVISIONE SCIENZE GENERALI BATCH 2 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")

    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/scienze.json aggiornato.")


if __name__ == "__main__":
    main()
