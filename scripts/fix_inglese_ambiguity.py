import json
from pathlib import Path


PERCORSO_DATA = Path("data")
PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


CORREZIONI = {
    "ING-FAC-0001": {
        "domanda": "Quale frase usa correttamente il presente semplice con 'she'?",
        "opzioni": [
            "She has a blue backpack.",
            "She have a blue backpack.",
            "She is have a blue backpack.",
            "She has got blue backpack."
        ],
        "risposta_corretta": "She has a blue backpack.",
        "spiegazione": (
            "Con 'she' al presente semplice si usa 'has'. "
            "'She have' è sbagliato perché 'have' non concorda con 'she'. "
            "'She is have' usa una struttura errata. "
            "'She has got blue backpack' manca dell'articolo 'a' prima di 'blue backpack'."
        )
    },

    "ING-FAC-0004": {
        "domanda": "Quale frase usa correttamente il presente con il soggetto 'they'?",
        "opzioni": [
            "They are students.",
            "They is students.",
            "They are student.",
            "They am students."
        ],
        "risposta_corretta": "They are students.",
        "spiegazione": (
            "'They are students' è corretto perché 'they' richiede 'are' e il nome deve essere al plurale: 'students'. "
            "'They is' usa il verbo sbagliato, 'They are student' sbaglia il plurale, "
            "mentre 'They am' usa una forma che si usa solo con 'I'."
        )
    },

    "ING-AV-0008": {
        "domanda": "Quale frase trasforma correttamente 'I am working on the project' nel discorso indiretto con backshift standard?",
        "opzioni": [
            "He said that he was working on the project.",
            "He said that he is working on the project.",
            "He said that he had worked on the project.",
            "He said that he worked on the project."
        ],
        "risposta_corretta": "He said that he was working on the project.",
        "spiegazione": (
            "Con il backshift standard del discorso indiretto, 'I am working' diventa 'he was working'. "
            "'Is working' non applica il backshift, 'had worked' cambia il significato verso il past perfect, "
            "mentre 'worked' perde l'idea dell'azione in corso."
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


def aggiorna_file_json(percorso):
    domande = carica_json(percorso)
    modifiche = 0

    for domanda in domande:
        id_domanda = domanda.get("id")

        if id_domanda in CORREZIONI:
            correzione = CORREZIONI[id_domanda]

            domanda["domanda"] = correzione["domanda"]
            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]

            modifiche += 1

    if modifiche > 0:
        salva_json(percorso, domande)

    return modifiche


def aggiorna_script_create_batch():
    domande_batch = carica_json(PERCORSO_BATCH)

    contenuto_lista = json.dumps(
        domande_batch,
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
    modifiche_totali = 0

    for percorso in sorted(PERCORSO_DATA.rglob("*.json")):
        modifiche_file = aggiorna_file_json(percorso)

        if modifiche_file > 0:
            modifiche_totali += modifiche_file
            print(f"Aggiornato {percorso}: {modifiche_file} domande")

    aggiorna_script_create_batch()

    print()
    print("Correzione ambiguità Inglese completata.")
    print(f"Domande aggiornate: {modifiche_totali}")


main()