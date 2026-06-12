import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "AI-FAC-0001": {
        "distrattore_forte": "Classificare testi in categorie fisse senza produrre nuove frasi",
        "motivo_distrattore_forte": (
            "È vicino perché anche la classificazione può essere svolta da modelli AI sul testo, "
            "ma è troppo limitato: un LLM non si limita a classificare, genera anche linguaggio naturale."
        ),
    },
    "AI-INT-0002": {
        "distrattore_forte": "Perché modifica i parametri interni del modello durante la risposta",
        "motivo_distrattore_forte": (
            "È vicino perché collega prompt e comportamento del modello, "
            "ma è sbagliato perché il prompt guida il contesto della risposta senza modificare i parametri interni."
        ),
    },
    "AI-AV-0003": {
        "distrattore_forte": "A riaddestrare il modello sui documenti recuperati prima di ogni risposta",
        "motivo_distrattore_forte": (
            "È vicino perché parla di documenti recuperati e modello, "
            "ma è sbagliato perché un sistema RAG usa i documenti come contesto, non riaddestra il modello a ogni domanda."
        ),
    },
    "AI-FAC-0004": {
        "distrattore_forte": "Esempi usati solo per verificare il modello dopo l'addestramento",
        "motivo_distrattore_forte": (
            "È vicino perché parla comunque di esempi e modello, "
            "ma confonde i dati di addestramento con i dati di test o validazione."
        ),
    },
    "AI-FAC-0005": {
        "opzioni": [
            "Riassumi questo testo in 5 righe usando un linguaggio semplice.",
            "Riassumi questo testo usando un linguaggio semplice.",
            "Riscrivi questo testo mantenendo tutti i dettagli principali.",
            "Riformula il testo senza ridurlo e senza cambiarne il significato.",
        ],
        "risposta_corretta": "Riassumi questo testo in 5 righe usando un linguaggio semplice.",
        "spiegazione": (
            "Il prompt corretto specifica chiaramente il compito, la lunghezza e lo stile: "
            "un riassunto in 5 righe con linguaggio semplice. Il distrattore B è quasi corretto, "
            "ma è meno preciso perché non indica la lunghezza. C e D chiedono una riscrittura o riformulazione, "
            "non un vero riassunto breve."
        ),
        "distrattore_forte": "Riassumi questo testo usando un linguaggio semplice.",
        "motivo_distrattore_forte": (
            "È molto vicino perché chiede comunque un riassunto semplice, "
            "ma è meno preciso perché manca il vincolo delle 5 righe."
        ),
    },
    "AI-FAC-0006": {
        "opzioni": [
            "Classificazione",
            "Clustering",
            "Regressione",
            "Stima di un valore numerico",
        ],
        "risposta_corretta": "Classificazione",
        "spiegazione": (
            "La classificazione assegna un elemento a una categoria, per esempio spam o non spam. "
            "Il clustering è vicino perché raggruppa elementi simili, ma non usa etichette già definite. "
            "La regressione e la stima numerica servono invece a prevedere valori numerici."
        ),
        "distrattore_forte": "Clustering",
        "motivo_distrattore_forte": (
            "È vicino perché anche il clustering separa elementi in gruppi, "
            "ma è sbagliato perché nello spam/non spam le categorie sono già definite."
        ),
    },
    "AI-FAC-0007": {
        "distrattore_forte": "Classifica contenuti testuali senza produrre nuove frasi",
        "motivo_distrattore_forte": (
            "È vicino perché un modello linguistico può anche classificare testi, "
            "ma è sbagliato come ruolo principale perché il modello linguistico può comprendere e generare testo."
        ),
    },
    "AI-FAC-0008": {
        "distrattore_forte": "Bias del dataset",
        "motivo_distrattore_forte": (
            "È vicino perché anche il bias può portare a risposte distorte o scorrette, "
            "ma l'allucinazione indica specificamente una risposta falsa inventata e presentata come sicura."
        ),
    },
}


def carica_json(percorso):
    with open(percorso, "r", encoding="utf-8") as file:
        return json.load(file)


def salva_json(percorso, dati):
    with open(percorso, "w", encoding="utf-8") as file:
        json.dump(
            dati,
            file,
            ensure_ascii=False,
            indent=2
        )
        file.write("\n")


def trova_liste_domande(dati):
    liste = []

    if isinstance(dati, list):
        liste.append(dati)

    elif isinstance(dati, dict):
        for valore in dati.values():
            if isinstance(valore, list):
                liste.append(valore)

    return liste


def aggiorna_file(percorso):
    dati = carica_json(percorso)
    liste_domande = trova_liste_domande(dati)

    modificato = False
    id_modificati = []

    for lista_domande in liste_domande:
        for domanda in lista_domande:
            if not isinstance(domanda, dict):
                continue

            id_domanda = domanda.get("id")

            if id_domanda in AGGIORNAMENTI:
                domanda.update(AGGIORNAMENTI[id_domanda])
                modificato = True
                id_modificati.append(id_domanda)

    if modificato:
        salva_json(percorso, dati)

    return id_modificati


def main():
    tutti_modificati = []

    for percorso in DATA_DIR.rglob("*.json"):
        id_modificati = aggiorna_file(percorso)

        if id_modificati:
            print("File aggiornato:", percorso)

            for id_domanda in id_modificati:
                print(" -", id_domanda)

            tutti_modificati.extend(id_modificati)

    mancanti = sorted(
        set(AGGIORNAMENTI.keys()) - set(tutti_modificati)
    )

    print("")
    print("Domande AI certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Primo blocco AI certificato correttamente.")


main()