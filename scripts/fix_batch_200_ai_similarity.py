import json
from pathlib import Path


PERCORSO_BATCH_200 = Path("data/espansione/batch_200.json")
PERCORSO_SCRIPT_AI = Path("scripts/add_batch_200_ai.py")


CORREZIONI = {
    "AI-INT-0101": {
        "domanda": "In un sistema RAG, perché la scelta dei chunk del documento è importante?",
        "opzioni": [
            "Perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso",
            "Perché i chunk servono solo a cambiare il colore del testo recuperato",
            "Perché ogni chunk deve contenere sempre l'intero database",
            "Perché i chunk eliminano automaticamente tutte le risposte sbagliate"
        ],
        "risposta_corretta": "Perché chunk troppo grandi o troppo piccoli possono rendere il recupero meno preciso",
        "spiegazione": (
            "Nei sistemi RAG i documenti vengono spesso divisi in parti più piccole, chiamate chunk. "
            "Se i chunk sono troppo grandi, possono contenere troppe informazioni non pertinenti. "
            "Se sono troppo piccoli, possono perdere contesto utile. "
            "La dimensione dei chunk influenza quindi la qualità del recupero."
        ),
        "tags": ["rag", "chunking", "retrieval"]
    },

    "AI-INT-0102": {
        "domanda": "Quale differenza c'è tra ricerca per parole esatte e ricerca semantica?",
        "opzioni": [
            "La ricerca semantica può trovare contenuti simili nel significato anche con parole diverse",
            "La ricerca semantica funziona solo se la frase contiene le stesse parole identiche",
            "La ricerca per parole esatte interpreta sempre il significato profondo della domanda",
            "La ricerca semantica elimina la necessità di controllare i risultati trovati"
        ],
        "risposta_corretta": "La ricerca semantica può trovare contenuti simili nel significato anche con parole diverse",
        "spiegazione": (
            "La ricerca per parole esatte cerca corrispondenze letterali. "
            "La ricerca semantica invece prova a confrontare il significato dei contenuti, "
            "quindi può trovare testi pertinenti anche se usano parole diverse dalla domanda."
        ),
        "tags": ["ricerca_semantica", "similarita", "retrieval"]
    },

    "AI-INT-0106": {
        "domanda": "Perché un agente AI può usare una fase di pianificazione prima di agire?",
        "opzioni": [
            "Per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni",
            "Per impedire sempre all'utente di modificare la richiesta",
            "Per trasformare ogni risposta in una lista casuale di operazioni",
            "Per saltare completamente il controllo del risultato finale"
        ],
        "risposta_corretta": "Per scegliere i passaggi e gli strumenti più adatti prima di eseguire azioni",
        "spiegazione": (
            "Un agente AI può pianificare prima di agire per decidere quali passaggi seguire, "
            "quali strumenti usare e in quale ordine. "
            "Questo riduce il rischio di azioni impulsive o poco coerenti con l'obiettivo."
        ),
        "tags": ["agenti", "pianificazione", "tool_use"]
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

            domanda["domanda"] = correzione["domanda"]
            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]
            domanda["tags"] = correzione["tags"]

            modifiche += 1

    return modifiche


def aggiorna_script_ai(domande_batch_200):
    domande_ai_0100 = [
        domanda
        for domanda in domande_batch_200
        if domanda.get("categoria") == "ai"
        and domanda.get("id", "").startswith("AI-")
        and "-01" in domanda.get("id", "")
    ]

    contenuto_lista = json.dumps(
        domande_ai_0100,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script aggiunge il blocco AI della seconda espansione.
# Obiettivo: portare il database da 100 a 200 domande totali.
# Questo primo blocco aggiunge 20 nuove domande AI.
#
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_ai = {contenuto_lista}


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
        for domanda in nuove_domande_ai
    }}

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_ai

    salva_domande(domande_finali)

    print("Blocco AI aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande AI:", len(nuove_domande_ai))
    print("Domande totali in batch_200:", len(domande_finali))


main()
'''

    PERCORSO_SCRIPT_AI.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    domande_batch_200 = carica_json(PERCORSO_BATCH_200)

    modifiche = aggiorna_domande(domande_batch_200)

    salva_json(PERCORSO_BATCH_200, domande_batch_200)
    aggiorna_script_ai(domande_batch_200)

    print("Correzione somiglianze AI batch 200 completata.")
    print("Domande aggiornate:", modifiche)
    print("File aggiornati:")
    print(PERCORSO_BATCH_200)
    print(PERCORSO_SCRIPT_AI)


main()