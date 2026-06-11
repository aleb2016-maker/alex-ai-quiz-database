import json
from pathlib import Path


PERCORSO_BATCH_200 = Path("data/espansione/batch_200.json")
PERCORSO_SCRIPT_LOGICA = Path("scripts/add_batch_200_logica.py")

ID_DA_RIMUOVERE = "LOG-AST-FAC-0101"


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


def aggiorna_script_logica(domande_batch_200):
    domande_logica_0100 = [
        domanda
        for domanda in domande_batch_200
        if domanda.get("categoria") == "logica"
        and domanda.get("id", "").startswith("LOG-")
        and "-010" in domanda.get("id", "")
    ]

    contenuto_lista = json.dumps(
        domande_logica_0100,
        ensure_ascii=False,
        indent=4
    )

    nuovo_contenuto = f'''import json
from pathlib import Path


# Questo script aggiunge il blocco Logica della seconda espansione.
# Obiettivo: portare il database da 180 a 200 domande totali.
#
# Le nuove domande vengono salvate in:
# data/espansione/batch_200.json


PERCORSO_OUTPUT = Path("data/espansione/batch_200.json")


nuove_domande_logica = {contenuto_lista}


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
        for domanda in nuove_domande_logica
    }}

    domande_senza_vecchie_versioni = [
        domanda
        for domanda in domande_esistenti
        if domanda.get("id") not in nuovi_id
    ]

    domande_finali = domande_senza_vecchie_versioni + nuove_domande_logica

    salva_domande(domande_finali)

    print("Blocco Logica aggiunto correttamente.")
    print("File aggiornato:")
    print(PERCORSO_OUTPUT)
    print("Nuove domande Logica:", len(nuove_domande_logica))
    print("Domande totali in batch_200:", len(domande_finali))


main()
'''

    PERCORSO_SCRIPT_LOGICA.write_text(nuovo_contenuto, encoding="utf-8")


def main():
    domande_batch_200 = carica_json(PERCORSO_BATCH_200)

    numero_prima = len(domande_batch_200)

    domande_corrette = [
        domanda
        for domanda in domande_batch_200
        if domanda.get("id") != ID_DA_RIMUOVERE
    ]

    numero_dopo = len(domande_corrette)

    salva_json(PERCORSO_BATCH_200, domande_corrette)
    aggiorna_script_logica(domande_corrette)

    print("Correzione domanda extra Logica completata.")
    print("Domande prima:", numero_prima)
    print("Domande dopo:", numero_dopo)
    print("Domanda rimossa:", ID_DA_RIMUOVERE)
    print("File aggiornati:")
    print(PERCORSO_BATCH_200)
    print(PERCORSO_SCRIPT_LOGICA)


main()