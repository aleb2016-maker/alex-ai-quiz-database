from pathlib import Path
import json
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

BIOLOGIA_JSON = ROOT / "data" / "biologia.json"
BACKUP_TMP = Path("/tmp/biologia_prima_revisione_batch1.json")

REVISIONI = {
    "BIO_004": {
        "opzioni": [
            "ATP prodotto nella respirazione cellulare",
            "NADPH prodotto soprattutto nella fotosintesi",
            "GTP usato in alcune reazioni cellulari",
            "AMP derivato dalla degradazione dell’ATP",
        ],
        "risposta_corretta": "ATP prodotto nella respirazione cellulare",
        "spiegazione": (
            "I mitocondri producono soprattutto ATP durante la respirazione cellulare. "
            "NADPH è legato soprattutto alla fotosintesi, mentre GTP e AMP hanno altri ruoli energetici."
        ),
    },

    "BIO_005": {
        "opzioni": [
            "La mitosi mantiene il numero cromosomico, la meiosi lo dimezza formando gameti",
            "La mitosi dimezza i cromosomi nei tessuti, la meiosi li mantiene nelle cellule somatiche",
            "La mitosi produce gameti ricombinati, la meiosi produce cellule somatiche identiche",
            "La mitosi separa cromosomi omologhi, la meiosi separa solo cromatidi identici",
        ],
        "risposta_corretta": "La mitosi mantiene il numero cromosomico, la meiosi lo dimezza formando gameti",
        "spiegazione": (
            "La mitosi produce cellule geneticamente molto simili mantenendo il numero cromosomico. "
            "La meiosi invece riduce il numero di cromosomi e produce gameti."
        ),
    },

    "BIO_008": {
        "opzioni": [
            "Il trasporto attivo usa energia per spostare sostanze anche contro gradiente",
            "Il trasporto attivo usa proteine ma segue soltanto il gradiente di concentrazione",
            "La diffusione semplice usa ATP quando attraversa direttamente il doppio strato lipidico",
            "La diffusione semplice usa pompe di membrana per spingere soluti contro gradiente",
        ],
        "risposta_corretta": "Il trasporto attivo usa energia per spostare sostanze anche contro gradiente",
        "spiegazione": (
            "Il trasporto attivo richiede energia, spesso ATP, perché può spostare sostanze contro gradiente. "
            "La diffusione semplice avviene invece secondo gradiente e non usa pompe alimentate da energia."
        ),
    },

    "BIO_009": {
        "opzioni": [
            "Un gene può essere trascritto in RNA messaggero, che guida la sintesi di una proteina",
            "Un gene viene tradotto direttamente in proteina senza passare da RNA messaggero",
            "L’RNA messaggero conserva il gene originale e lo replica stabilmente nel nucleo",
            "Una proteina viene trascritta in RNA messaggero e poi convertita in DNA",
        ],
        "risposta_corretta": "Un gene può essere trascritto in RNA messaggero, che guida la sintesi di una proteina",
        "spiegazione": (
            "Nel flusso classico dell’informazione genetica, un gene può essere trascritto in RNA messaggero. "
            "L’RNA messaggero viene poi tradotto dai ribosomi per sintetizzare una proteina."
        ),
    },

    "BIO_010": {
        "opzioni": [
            "Gli individui con tratti vantaggiosi tendono a lasciare più discendenti in un certo ambiente",
            "Gli individui sviluppano tratti utili durante la vita e li trasmettono ai figli",
            "Tutti gli individui cambiano nello stesso modo quando l’ambiente esercita pressione",
            "Le mutazioni compaiono perché l’ambiente richiede direttamente un certo adattamento",
        ],
        "risposta_corretta": "Gli individui con tratti vantaggiosi tendono a lasciare più discendenti in un certo ambiente",
        "spiegazione": (
            "La selezione naturale favorisce gli individui con caratteristiche ereditarie vantaggiose "
            "in un determinato ambiente, perché tendono a sopravvivere e riprodursi di più."
        ),
    },

    "BIO_012": {
        "opzioni": [
            "La cellula procariotica non possiede un nucleo delimitato da membrana",
            "La cellula procariotica possiede organelli membranosi ma non ribosomi funzionali",
            "La cellula eucariotica non contiene DNA organizzato in compartimenti cellulari",
            "La cellula eucariotica è priva di membrana plasmatica ma contiene nucleo",
        ],
        "risposta_corretta": "La cellula procariotica non possiede un nucleo delimitato da membrana",
        "spiegazione": (
            "Le cellule procariotiche non hanno un nucleo delimitato da membrana. "
            "Le cellule eucariotiche invece possiedono un nucleo e vari organelli membranosi."
        ),
    },

    "BIO_013": {
        "opzioni": [
            "Regola in modo selettivo il passaggio di sostanze tra cellula e ambiente",
            "Produce direttamente ATP tramite le reazioni principali della respirazione cellulare",
            "Conserva l’intero DNA cellulare separandolo dal citoplasma con doppia membrana",
            "Sintetizza proteine libere trasformando RNA messaggero in catene di amminoacidi",
        ],
        "risposta_corretta": "Regola in modo selettivo il passaggio di sostanze tra cellula e ambiente",
        "spiegazione": (
            "La membrana cellulare delimita la cellula e controlla in modo selettivo gli scambi "
            "con l’ambiente esterno. Non produce ATP, non conserva il DNA e non sintetizza direttamente proteine."
        ),
    },

    "BIO_016": {
        "opzioni": [
            "Assorbono acqua e sali minerali e contribuiscono ad ancorare la pianta al terreno",
            "Producono zuccheri tramite fotosintesi grazie ai pigmenti presenti nei tessuti verdi",
            "Trasportano il polline verso l’ovulo durante la riproduzione sessuata della pianta",
            "Liberano ossigeno nell’aria come prodotto diretto della respirazione cellulare",
        ],
        "risposta_corretta": "Assorbono acqua e sali minerali e contribuiscono ad ancorare la pianta al terreno",
        "spiegazione": (
            "Le radici assorbono acqua e sali minerali dal terreno e aiutano a stabilizzare la pianta. "
            "La fotosintesi avviene soprattutto nelle foglie, non nelle radici."
        ),
    },
}


def carica_database(percorso):
    dati = json.loads(percorso.read_text(encoding="utf-8"))

    if isinstance(dati, list):
        return dati, None

    if isinstance(dati, dict):
        for chiave in ["domande", "questions", "quiz", "items", "data", "database"]:
            if isinstance(dati.get(chiave), list):
                return dati[chiave], chiave

    raise SystemExit("ERRORE: struttura JSON non riconosciuta per data/biologia.json")


def aggiorna_spiegazioni_opzioni(domanda, revisione):
    spiegazioni = {}

    risposta = revisione["risposta_corretta"]

    for opzione in revisione["opzioni"]:
        if opzione == risposta:
            spiegazioni[opzione] = "Corretta: descrive il concetto biologico richiesto dalla domanda."
        else:
            spiegazioni[opzione] = (
                "Errata: è un distrattore vicino al tema, ma contiene un dettaglio biologico non corretto."
            )

    domanda["spiegazioni_opzioni"] = spiegazioni


def main():
    if not BIOLOGIA_JSON.exists():
        raise SystemExit(f"ERRORE: file mancante: {BIOLOGIA_JSON}")

    shutil.copy2(BIOLOGIA_JSON, BACKUP_TMP)
    print(f"Backup locale creato: {BACKUP_TMP}")

    dati_originali = json.loads(BIOLOGIA_JSON.read_text(encoding="utf-8"))
    domande, chiave_lista = carica_database(BIOLOGIA_JSON)

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
        nuovo_database = dati_originali
        nuovo_database[chiave_lista] = domande

    BIOLOGIA_JSON.write_text(
        json.dumps(nuovo_database, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    print("----- REVISIONE BIOLOGIA BATCH 1 -----")
    print(f"Domande aggiornate: {len(REVISIONI)}")
    for id_domanda in REVISIONI:
        print(f"- {id_domanda}")

    print("")
    print("OK: data/biologia.json aggiornato.")


if __name__ == "__main__":
    main()
