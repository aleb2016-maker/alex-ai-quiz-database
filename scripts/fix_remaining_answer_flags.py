import json
from pathlib import Path


PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


CORREZIONI = {
    "AI-INT-0004": {
        "opzioni": [
            "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
            "Per scegliere documenti semanticamente vicini ma non necessariamente utili",
            "Per usare il database come archivio storico senza inserirlo nel prompt",
            "Per confrontare la domanda con esempi simili senza generare una risposta"
        ],
        "risposta_corretta": (
            "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta"
        ),
        "spiegazione": (
            "Nel RAG il sistema recupera documenti rilevanti e li passa al modello come contesto. "
            "Il punto non è solo trovare testi simili, ma fornire informazioni utili su cui costruire la risposta. "
            "Se i documenti vengono trovati ma non usati nel prompt, oppure sono solo simili in apparenza, "
            "la risposta può restare generica o poco affidabile."
        )
    },

    "INF-AV-0009": {
        "opzioni": [
            "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
            "Permette di centralizzare valori di configurazione usati in ambienti diversi",
            "Permette di modificare alcuni parametri senza cambiare direttamente il codice",
            "Permette di distinguere configurazioni di sviluppo, test e produzione"
        ],
        "risposta_corretta": (
            "Permette di separare configurazioni sensibili o diverse dal codice sorgente"
        ),
        "spiegazione": (
            "La risposta più completa è che una variabile d'ambiente separa configurazioni sensibili o diverse dal codice sorgente. "
            "Le altre opzioni descrivono vantaggi collegati, ma sono più parziali: centralizzare valori, cambiare parametri "
            "o distinguere ambienti sono effetti utili, mentre il principio principale è non scrivere certe configurazioni direttamente nel codice."
        )
    },

    "LOG-VER-INT-0004": {
        "domanda": "Quale coppia mantiene meglio la relazione: bozza → documento finale?",
        "opzioni": [
            "prototipo → prodotto definitivo",
            "titolo → capitolo",
            "indice → argomento",
            "nota → parola chiave"
        ],
        "risposta_corretta": "prototipo → prodotto definitivo",
        "spiegazione": (
            "Una bozza è una versione iniziale che può essere sviluppata fino a diventare un documento finale. "
            "Allo stesso modo, un prototipo è una versione iniziale che può evolvere in un prodotto definitivo. "
            "Le altre coppie sono collegate al mondo dei testi o delle informazioni, ma non esprimono bene il passaggio da versione iniziale a versione finale."
        )
    }
}


def carica_domande():
    with open(PERCORSO_BATCH, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_domande(domande):
    with open(PERCORSO_BATCH, "w", encoding="utf-8") as file:
        json.dump(
            domande,
            file,
            ensure_ascii=False,
            indent=2
        )


def applica_correzioni(domande):
    domande_modificate = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in CORREZIONI:
            correzione = CORREZIONI[id_domanda]

            if "domanda" in correzione:
                domanda["domanda"] = correzione["domanda"]

            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]

            domande_modificate += 1

    return domande_modificate


def aggiorna_script_create_batch(domande):
    contenuto_lista = json.dumps(
        domande,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script crea il primo batch di espansione.
# Obiettivo: portare il database da 27 a 100 domande totali.
# Le nuove domande vengono salvate in data/espansione/batch_100.json


PERCORSO_OUTPUT = Path("data/espansione/batch_100.json")


nuove_domande = {contenuto_lista}


def main():
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            nuove_domande,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("File creato correttamente:")
    print(PERCORSO_OUTPUT)
    print(f"Domande create: {{len(nuove_domande)}}")


main()
'''

    PERCORSO_SCRIPT_BATCH.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    domande = carica_domande()

    domande_modificate = applica_correzioni(domande)

    salva_domande(domande)
    aggiorna_script_create_batch(domande)

    print("Correzione completata.")
    print(f"Domande modificate: {domande_modificate}")
    print("File aggiornati:")
    print(PERCORSO_BATCH)
    print(PERCORSO_SCRIPT_BATCH)


main()