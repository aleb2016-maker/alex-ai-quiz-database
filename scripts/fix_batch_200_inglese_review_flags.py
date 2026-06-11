import json
from pathlib import Path


PERCORSO_BATCH_200 = Path("data/espansione/batch_200.json")
PERCORSO_SCRIPT_INGLESE = Path("scripts/add_batch_200_inglese.py")


CORREZIONI = {
    "ING-AV-0105": {
        "opzioni": [
            "He must have forgotten the password.",
            "He may have forgotten the password.",
            "He could have forgotten the password.",
            "He should have remembered the password."
        ],
        "risposta_corretta": "He must have forgotten the password.",
        "spiegazione": (
            "'Must have + participio passato' esprime una deduzione forte riferita al passato. "
            "'May have' e 'could have' indicano possibilità, quindi sono più deboli. "
            "'Should have remembered' esprime ciò che sarebbe stato opportuno fare, non una deduzione forte."
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


def aggiorna_script_inglese(domande_batch_200):
    domande_inglese_0100 = [
        domanda
        for domanda in domande_batch_200
        if domanda.get("categoria") == "inglese"
        and domanda.get("id", "").startswith("ING-")
        and "-01" in domanda.get("id", "")
    ]

    contenuto_lista = json.dumps(
        domande_inglese_0100,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script aggiunge il blocco Inglese della seconda espansione.
# Obiettivo: portare il database da 160 a 180 domande totali.
#
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_inglese = {contenuto_lista}


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
        for domanda in nuove_domande_inglese
    }}

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_inglese

    salva_domande(domande_finali)

    print("Blocco Inglese aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande Inglese:", len(nuove_domande_inglese))
    print("Domande totali in batch_200:", len(domande_finali))


main()
'''

    PERCORSO_SCRIPT_INGLESE.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    domande_batch_200 = carica_json(PERCORSO_BATCH_200)

    modifiche = aggiorna_domande(domande_batch_200)

    salva_json(PERCORSO_BATCH_200, domande_batch_200)
    aggiorna_script_inglese(domande_batch_200)

    print("Correzione domande Inglese batch 200 completata.")
    print("Domande aggiornate:", modifiche)
    print("File aggiornati:")
    print(PERCORSO_BATCH_200)
    print(PERCORSO_SCRIPT_INGLESE)


main()