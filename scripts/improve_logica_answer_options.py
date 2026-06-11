import json
from pathlib import Path


PERCORSO_DATA = Path("data")
PERCORSO_BATCH = Path("data/espansione/batch_100.json")
PERCORSO_SCRIPT_BATCH = Path("scripts/create_batch_100.py")


CORREZIONI_LOGICA = {
    "LOG-NUM-AV-0004": {
        "domanda": "Completa la sequenza: 5, 11, 10, 21, 20, 41, ?",
        "opzioni": [
            "39",
            "40",
            "42",
            "82"
        ],
        "risposta_corretta": "40",
        "spiegazione": (
            "La sequenza alterna due operazioni: moltiplicare per 2 e aggiungere 1, poi sottrarre 1. "
            "Infatti 5 × 2 + 1 = 11, poi 11 - 1 = 10. "
            "Poi 10 × 2 + 1 = 21, poi 21 - 1 = 20. "
            "Poi 20 × 2 + 1 = 41, quindi il passo successivo è 41 - 1 = 40."
        )
    },

    "LOG-CRI-FAC-0001": {
        "opzioni": [
            "Il treno 25 arriva in stazione",
            "Tutti i treni che arrivano in stazione sono della linea A",
            "Solo il treno 25 della linea A arriva in stazione",
            "Il treno 25 arriva in stazione solo se è in orario"
        ],
        "risposta_corretta": "Il treno 25 arriva in stazione",
        "spiegazione": (
            "Se tutti i treni della linea A arrivano in stazione e il treno 25 è della linea A, "
            "allora il treno 25 arriva in stazione. "
            "Non possiamo però concludere che tutti i treni che arrivano siano della linea A, "
            "né che solo il treno 25 arrivi, né aggiungere condizioni non presenti come l'orario."
        )
    },

    "LOG-CRI-AV-0003": {
        "opzioni": [
            "Non è certo che il prodotto sia scontato",
            "Il prodotto è sicuramente scontato perché si trova nello scaffale rosso",
            "Tutti i prodotti nello scaffale rosso sono sicuramente scontati",
            "Nessun prodotto non scontato può trovarsi nello scaffale rosso"
        ],
        "risposta_corretta": "Non è certo che il prodotto sia scontato",
        "spiegazione": (
            "L'affermazione dice che tutti i prodotti scontati sono nello scaffale rosso. "
            "Questo non significa che tutti i prodotti nello scaffale rosso siano scontati. "
            "Trovare un prodotto nello scaffale rosso non basta quindi per concludere con certezza che sia scontato."
        )
    },

    "LOG-CRI-AV-0005": {
        "opzioni": [
            "L'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche",
            "L'aggiornamento è certamente l'unica causa perché è avvenuto prima degli errori",
            "Gli errori sono certamente indipendenti dall'aggiornamento perché li hanno segnalati solo alcuni utenti",
            "Il numero di segnalazioni basta da solo per dimostrare la causa tecnica"
        ],
        "risposta_corretta": "L'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche",
        "spiegazione": (
            "La vicinanza temporale tra aggiornamento ed errori suggerisce una possibile relazione, "
            "ma non dimostra da sola una causa certa. "
            "Per una conclusione prudente servono log, test, confronto tra versioni e verifica di altri fattori."
        )
    },

    "LOG-CRI-INT-0002": {
        "opzioni": [
            "Oggi non piove",
            "Oggi piove sicuramente",
            "Marco potrebbe non prendere l'ombrello anche se piove",
            "Non si può dedurre nulla sul tempo"
        ],
        "risposta_corretta": "Oggi non piove",
        "spiegazione": (
            "La regola dice: se piove, Marco prende l'ombrello. "
            "Se oggi Marco non prende l'ombrello, allora la condizione 'piove' non si è verificata. "
            "Questa è una deduzione per contrapposizione: se P implica Q, allora non Q implica non P."
        )
    },

    "LOG-CRI-INT-0004": {
        "opzioni": [
            "Alcune persone che documentano gli errori controllano i log",
            "Tutte le persone che controllano i log documentano errori",
            "Alcuni tecnici non controllano i log",
            "Tutti quelli che documentano errori sono tecnici"
        ],
        "risposta_corretta": "Alcune persone che documentano gli errori controllano i log",
        "spiegazione": (
            "Sappiamo che alcuni tecnici documentano gli errori e che tutti i tecnici controllano i log. "
            "Quindi quei tecnici che documentano errori controllano anche i log. "
            "Non possiamo invece dire che tutti quelli che controllano log documentino errori, "
            "né che esistano tecnici che non controllano i log."
        )
    },

    "LOG-VER-INT-0002": {
        "opzioni": [
            "tagliare",
            "incollare",
            "misurare",
            "disegnare"
        ],
        "risposta_corretta": "tagliare",
        "spiegazione": (
            "La relazione è tra uno strumento e la sua funzione principale. "
            "La penna serve principalmente per scrivere; le forbici servono principalmente per tagliare. "
            "Incollare, misurare e disegnare sono azioni possibili con altri strumenti, ma non indicano la funzione principale delle forbici."
        )
    },

    "LOG-VER-INT-0004": {
        "opzioni": [
            "prototipo → prodotto definitivo",
            "bozza → correzione",
            "indice → documento finale",
            "idea → titolo"
        ],
        "risposta_corretta": "prototipo → prodotto definitivo",
        "spiegazione": (
            "Una bozza è una versione iniziale che può evolvere in un documento finale. "
            "Allo stesso modo, un prototipo è una versione iniziale che può evolvere in un prodotto definitivo. "
            "Bozza → correzione indica una fase di revisione, indice → documento finale indica una parte rispetto al tutto, "
            "mentre idea → titolo non rappresenta chiaramente il passaggio da versione iniziale a versione finale."
        )
    },

    "LOG-VER-AV-0003": {
        "opzioni": [
            "indizio → ipotesi",
            "prova → verdetto",
            "errore → correzione",
            "causa → conseguenza"
        ],
        "risposta_corretta": "indizio → ipotesi",
        "spiegazione": (
            "Un sintomo è un segnale che aiuta a formulare una diagnosi, ma non coincide con la diagnosi. "
            "Allo stesso modo, un indizio è un elemento che aiuta a formulare un'ipotesi, ma non coincide con una conclusione certa. "
            "Le altre coppie sono relazioni logiche plausibili, ma non mantengono esattamente lo stesso rapporto di segnale interpretato."
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

        if id_domanda in CORREZIONI_LOGICA:
            correzione = CORREZIONI_LOGICA[id_domanda]

            if "domanda" in correzione:
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
    print("Revisione Logica completata.")
    print(f"Domande Logica aggiornate: {modifiche_totali}")


main()