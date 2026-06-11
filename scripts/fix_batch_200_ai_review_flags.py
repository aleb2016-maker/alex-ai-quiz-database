import json
from pathlib import Path


PERCORSO_BATCH_200 = Path("data/espansione/batch_200.json")
PERCORSO_SCRIPT_AI = Path("scripts/add_batch_200_ai.py")


CORREZIONI = {
    "AI-FAC-0106": {
        "opzioni": [
            "A una risposta plausibile ma falsa o non verificata",
            "A una risposta corretta ma troppo breve per essere utile",
            "A una risposta basata solo su fonti citate e controllabili",
            "A una risposta incompleta ma dichiarata come incerta"
        ],
        "risposta_corretta": "A una risposta plausibile ma falsa o non verificata",
        "spiegazione": (
            "Un'allucinazione in AI è una risposta che può sembrare credibile, "
            "ma contiene informazioni false, inventate o non verificate. "
            "Una risposta breve, incompleta o prudente può essere migliorabile, "
            "ma non è necessariamente un'allucinazione."
        )
    },

    "AI-INT-0102": {
        "opzioni": [
            "A rappresentare testi o dati come vettori confrontabili per somiglianza",
            "A trasformare testi simili in rappresentazioni numeriche vicine tra loro",
            "A permettere ricerche semantiche confrontando la distanza tra contenuti",
            "A codificare contenuti in una forma numerica utile per modelli e database vettoriali"
        ],
        "risposta_corretta": "A rappresentare testi o dati come vettori confrontabili per somiglianza",
        "spiegazione": (
            "Un embedding rappresenta testi o altri dati come vettori numerici. "
            "La risposta corretta è la più completa perché spiega sia la trasformazione in vettori "
            "sia il motivo pratico: confrontare contenuti per somiglianza. "
            "Le altre opzioni descrivono aspetti collegati, ma sono più parziali."
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

    print("Correzione domande AI batch 200 completata.")
    print("Domande aggiornate:", modifiche)
    print("File aggiornati:")
    print(PERCORSO_BATCH_200)
    print(PERCORSO_SCRIPT_AI)


main()