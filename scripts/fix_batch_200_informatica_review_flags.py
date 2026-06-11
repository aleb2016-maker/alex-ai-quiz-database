import json
from pathlib import Path


PERCORSO_BATCH_200 = Path("data/espansione/batch_200.json")
PERCORSO_SCRIPT_INFORMATICA = Path("scripts/add_batch_200_informatica.py")


CORREZIONI = {
    "INF-FAC-0101": {
        "opzioni": [
            "Eseguire istruzioni ed elaborare operazioni",
            "Conservare temporaneamente i dati usati dai programmi",
            "Archiviare file e programmi anche a computer spento",
            "Gestire principalmente l'elaborazione grafica delle immagini"
        ],
        "risposta_corretta": "Eseguire istruzioni ed elaborare operazioni",
        "spiegazione": (
            "La CPU è il processore principale del computer: esegue istruzioni, calcoli e operazioni logiche. "
            "La RAM conserva temporaneamente i dati dei programmi, SSD o hard disk archiviano i file in modo permanente, "
            "mentre la GPU gestisce soprattutto l'elaborazione grafica."
        )
    },

    "INF-FAC-0103": {
        "opzioni": [
            "Il software che gestisce risorse del computer e permette di usare programmi",
            "Un programma applicativo usato per svolgere un compito specifico",
            "Un insieme di file personali salvati in una cartella",
            "Un componente hardware che aumenta lo spazio di archiviazione"
        ],
        "risposta_corretta": "Il software che gestisce risorse del computer e permette di usare programmi",
        "spiegazione": (
            "Il sistema operativo gestisce risorse come memoria, file, periferiche e processi, "
            "e permette agli altri programmi di funzionare. "
            "Un'applicazione svolge un compito specifico, una cartella contiene file, "
            "mentre un componente hardware come un SSD aumenta lo spazio di archiviazione."
        )
    },

    "INF-FAC-0105": {
        "opzioni": [
            "Un valore che può essere vero o falso",
            "Un numero intero usato per contare elementi",
            "Una stringa di testo composta da caratteri",
            "Un valore assente o non definito"
        ],
        "risposta_corretta": "Un valore che può essere vero o falso",
        "spiegazione": (
            "Un booleano rappresenta due stati logici: vero o falso. "
            "Un intero rappresenta numeri senza decimali, una stringa rappresenta testo, "
            "mentre un valore nullo o assente indica mancanza di dato."
        )
    },

    "INF-INT-0104": {
        "opzioni": [
            "La risorsa richiesta non è stata trovata sul server",
            "La richiesta non è autenticata correttamente",
            "L'utente è autenticato ma non autorizzato",
            "Il server ha generato un errore interno"
        ],
        "risposta_corretta": "La risorsa richiesta non è stata trovata sul server",
        "spiegazione": (
            "HTTP 404 indica che la risorsa richiesta non è stata trovata. "
            "401 riguarda un problema di autenticazione, 403 indica permessi insufficienti, "
            "mentre 500 segnala un errore interno del server."
        )
    },

    "INF-INT-0106": {
        "opzioni": [
            "Per proteggere la comunicazione tra browser e server tramite cifratura",
            "Per verificare che il sito usi un certificato digitale valido",
            "Per ridurre il rischio che i dati vengano intercettati durante il trasferimento",
            "Per rendere più sicuro lo scambio di informazioni sensibili"
        ],
        "risposta_corretta": "Per proteggere la comunicazione tra browser e server tramite cifratura",
        "spiegazione": (
            "HTTPS protegge la comunicazione tra browser e server tramite cifratura. "
            "Certificati, riduzione del rischio di intercettazione e protezione dei dati sensibili "
            "sono aspetti collegati, ma la risposta corretta è quella più completa e generale."
        )
    }
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, contenuto):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            contenuto,
            file,
            ensure_ascii=False,
            indent=2
        )


def aggiorna_domande(domande):
    modifiche = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in CORREZIONI:
            correzione = CORREZIONI[id_domanda]

            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]

            modifiche += 1

    return modifiche


def aggiorna_script_informatica(domande_batch_200):
    domande_informatica_0100 = [
        domanda
        for domanda in domande_batch_200
        if domanda.get("categoria") == "informatica"
        and domanda.get("id", "").startswith("INF-")
        and "-01" in domanda.get("id", "")
    ]

    contenuto_lista = json.dumps(
        domande_informatica_0100,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script aggiunge il blocco Informatica della seconda espansione.
# Obiettivo: portare il database da 120 a 140 domande totali.
#
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_informatica = {contenuto_lista}


def carica_domande_esistenti():
    if not PERCORSO_OUTPUT.exists():
        return []

    with open(PERCORSO_OUTPUT, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_domande(domande):
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            domande,
            file,
            ensure_ascii=False,
            indent=2
        )


def main():
    domande_esistenti = carica_domande_esistenti()

    nuovi_id = {{
        domanda["id"]
        for domanda in nuove_domande_informatica
    }}

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_informatica

    salva_domande(domande_finali)

    print("Blocco Informatica aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande Informatica:", len(nuove_domande_informatica))
    print("Domande totali in batch_200:", len(domande_finali))


main()
'''

    PERCORSO_SCRIPT_INFORMATICA.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    domande_batch_200 = carica_json(PERCORSO_BATCH_200)

    modifiche = aggiorna_domande(domande_batch_200)

    salva_json(PERCORSO_BATCH_200, domande_batch_200)
    aggiorna_script_informatica(domande_batch_200)

    print("Correzione domande Informatica batch 200 completata.")
    print("Domande aggiornate:", modifiche)
    print("File aggiornati:")
    print(PERCORSO_BATCH_200)
    print(PERCORSO_SCRIPT_INFORMATICA)


main()