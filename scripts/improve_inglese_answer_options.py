import json
from pathlib import Path


PERCORSO_DATA = Path("data")
PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


CORREZIONI_INGLESE = {
    "ING-AV-0004": {
        "opzioni": [
            "however",
            "therefore",
            "moreover",
            "otherwise"
        ],
        "risposta_corretta": "however",
        "spiegazione": (
            "'However' introduce un contrasto: il sistema è potente, ma richiede comunque test accurati. "
            "'Therefore' indica conseguenza, 'moreover' aggiunge un'informazione, mentre 'otherwise' indica una conseguenza alternativa."
        )
    },

    "ING-AV-0005": {
        "opzioni": [
            "The developer who fixed the bug updated the repository.",
            "The developer which fixed the bug updated the repository.",
            "The developer that fixing the bug updated the repository.",
            "The developer whose fixed the bug updated the repository."
        ],
        "risposta_corretta": "The developer who fixed the bug updated the repository.",
        "spiegazione": (
            "Per riferirsi a una persona in una frase relativa si usa normalmente 'who'. "
            "'Which' si usa più spesso per cose o animali, 'that fixing' è una struttura errata, "
            "mentre 'whose' indica possesso e non può sostituire 'who' in questa frase."
        )
    },

    "ING-AV-0006": {
        "opzioni": [
            "The report was reviewed by the team.",
            "The report has been review by the team.",
            "The report is reviewed by the team yesterday.",
            "The report was reviewing by the team."
        ],
        "risposta_corretta": "The report was reviewed by the team.",
        "spiegazione": (
            "La forma passiva corretta usa il verbo 'to be' più il participio passato: 'was reviewed'. "
            "'Has been review' è sbagliato perché manca il participio 'reviewed'. "
            "'Is reviewed yesterday' mescola presente e tempo passato preciso. "
            "'Was reviewing' è una forma attiva/progressiva, non passiva corretta."
        )
    },

    "ING-AV-0007": {
        "opzioni": [
            "You should consider updating the documentation.",
            "You should update the documentation immediately.",
            "You could update the documentation if necessary.",
            "You might want to update the documentation."
        ],
        "risposta_corretta": "You should consider updating the documentation.",
        "spiegazione": (
            "'You should consider updating...' è un consiglio formale e prudente. "
            "'You should update immediately' è più diretto e meno formale. "
            "'Could' indica possibilità, mentre 'might want to' è un suggerimento più informale."
        )
    },

    "ING-AV-0008": {
        "opzioni": [
            "He said that he was working on the project.",
            "He said that he is working on the project.",
            "He said that he had worked on the project.",
            "He said that he worked on the project."
        ],
        "risposta_corretta": "He said that he was working on the project.",
        "spiegazione": (
            "Nel discorso indiretto, 'I am working' diventa normalmente 'he was working'. "
            "'Is working' non applica il backshift, 'had worked' cambia il tempo in past perfect, "
            "mentre 'worked' perde l'idea di azione in corso."
        )
    },

    "ING-AV-0009": {
        "opzioni": [
            "La funzionalità è compatibile con versioni precedenti.",
            "La funzionalità richiede solo versioni successive.",
            "La funzionalità mantiene la stessa interfaccia ma non supporta versioni vecchie.",
            "La funzionalità è stata riscritta senza garantire compatibilità."
        ],
        "risposta_corretta": "La funzionalità è compatibile con versioni precedenti.",
        "spiegazione": (
            "'Backward compatible' significa che una funzionalità rimane compatibile con versioni precedenti del sistema o del software. "
            "Le altre opzioni sono plausibili nel contesto software, ma indicano compatibilità futura, mancato supporto o assenza di garanzie."
        )
    },

    "ING-FAC-0001": {
        "opzioni": [
            "She has a blue backpack.",
            "She have a blue backpack.",
            "She had a blue backpack.",
            "She has got blue backpack."
        ],
        "risposta_corretta": "She has a blue backpack.",
        "spiegazione": (
            "Con 'she' al presente si usa 'has'. "
            "'Have' è sbagliato con 'she', 'had' indica passato, "
            "mentre 'has got blue backpack' manca dell'articolo 'a'."
        )
    },

    "ING-FAC-0004": {
        "opzioni": [
            "They are students.",
            "They is students.",
            "They were students.",
            "They are student."
        ],
        "risposta_corretta": "They are students.",
        "spiegazione": (
            "'They are students' è corretto perché 'they' richiede 'are' e il nome al plurale 'students'. "
            "'They is' è sbagliato, 'they were' è grammaticalmente corretto ma al passato, "
            "mentre 'They are student' sbaglia il plurale del nome."
        )
    },

    "ING-INT-0005": {
        "opzioni": [
            "more difficult",
            "most difficult",
            "more difficulty",
            "difficulter"
        ],
        "risposta_corretta": "more difficult",
        "spiegazione": (
            "Dopo 'than' serve il comparativo. Con un aggettivo lungo come 'difficult' si usa 'more difficult'. "
            "'Most difficult' è superlativo, 'more difficulty' usa un nome invece dell'aggettivo, "
            "mentre 'difficulter' non è la forma corretta."
        )
    },

    "ING-INT-0007": {
        "opzioni": [
            "will stay",
            "would stay",
            "are staying",
            "stayed"
        ],
        "risposta_corretta": "will stay",
        "spiegazione": (
            "Nel first conditional si usa 'if' + present simple e poi 'will' + verbo base. "
            "Quindi: 'If it rains tomorrow, we will stay at home.' "
            "'Would stay' appartiene più al second conditional, 'are staying' indica un piano già organizzato, "
            "mentre 'stayed' è passato."
        )
    },

    "ING-INT-0008": {
        "opzioni": [
            "spegnere",
            "accendere",
            "abbassare",
            "scollegare"
        ],
        "risposta_corretta": "spegnere",
        "spiegazione": (
            "'Turn off' significa spegnere. "
            "'Turn on' significa accendere, 'turn down' può significare abbassare, "
            "mentre 'unplug' significa scollegare."
        )
    },

    "ING-INT-0009": {
        "opzioni": [
            "I am looking forward to starting the course.",
            "I am looking forward to start the course.",
            "I am looking for starting the course.",
            "I am looking after starting the course."
        ],
        "risposta_corretta": "I am looking forward to starting the course.",
        "spiegazione": (
            "'Look forward to' significa non vedere l'ora di fare qualcosa. "
            "Dopo 'to' in questa espressione si usa il verbo in -ing: 'starting'. "
            "'Looking for' significa cercare, mentre 'looking after' significa prendersi cura di."
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

        if id_domanda in CORREZIONI_INGLESE:
            correzione = CORREZIONI_INGLESE[id_domanda]

            domanda["opzioni"] = correzione["opzioni"]
            domanda["risposta_corretta"] = correzione["risposta_corretta"]
            domanda["spiegazione"] = correzione["spiegazione"]

            modifiche += 1

    if modifiche > 0:
        salva_json(percorso, domande)

    return modifiche


def aggiorna_script_create_batch():
    if not PERCORSO_BATCH.exists():
        return

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
    print("Revisione Inglese completata.")
    print(f"Domande Inglese aggiornate: {modifiche_totali}")


main()