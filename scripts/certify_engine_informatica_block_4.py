import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "INF-AV-0101": {
        "opzioni": [
            "Perché i dati inviati al server non devono essere considerati affidabili solo perché il frontend li controlla",
            "Perché i controlli del frontend migliorano l'esperienza utente, ma possono essere aggirati",
            "Perché la validazione lato backend sostituisce ogni test automatico",
            "Perché il frontend non può mai mostrare messaggi di errore",
        ],
        "risposta_corretta": "Perché i dati inviati al server non devono essere considerati affidabili solo perché il frontend li controlla",
        "spiegazione": (
            "Il controllo lato frontend migliora l'esperienza utente, ma può essere aggirato. "
            "Il backend deve validare i dati perché è il punto che protegge applicazione, database e regole di business."
        ),
        "distrattore_forte": "Perché i controlli del frontend migliorano l'esperienza utente, ma possono essere aggirati",
        "motivo_distrattore_forte": (
            "È molto vicino perché descrive un motivo reale per validare anche lato backend, "
            "ma è meno completo: la risposta corretta chiarisce che i dati arrivati al server non devono essere considerati affidabili."
        ),
    },
    "INF-AV-0103": {
        "opzioni": [
            "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
            "Perché conserva temporaneamente dati frequenti, ma elimina sempre la necessità del database",
            "Perché cancella automaticamente ogni bug dal codice",
            "Perché obbliga il server a ignorare tutte le richieste nuove",
        ],
        "risposta_corretta": "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
        "spiegazione": (
            "La cache conserva temporaneamente risultati o dati molto richiesti. "
            "Questo può ridurre tempi di risposta e carico su database o servizi esterni, "
            "ma non sostituisce sempre il database principale."
        ),
        "distrattore_forte": "Perché conserva temporaneamente dati frequenti, ma elimina sempre la necessità del database",
        "motivo_distrattore_forte": (
            "È vicino perché parla correttamente di dati conservati temporaneamente, "
            "ma è sbagliato perché la cache non elimina sempre la necessità del database principale."
        ),
    },
    "INF-AV-0104": {
        "opzioni": [
            "Per dividere i risultati in blocchi più piccoli e gestibili",
            "Per limitare la quantità di dati restituiti in ogni risposta senza perdere l'accesso agli altri risultati",
            "Per impedire all'API di restituire qualsiasi dato",
            "Per trasformare ogni risposta in un errore 404",
        ],
        "risposta_corretta": "Per dividere i risultati in blocchi più piccoli e gestibili",
        "spiegazione": (
            "La paginazione evita di inviare troppi dati in una sola risposta. "
            "Aiuta prestazioni, consumo di rete e usabilità, soprattutto con grandi quantità di risultati."
        ),
        "distrattore_forte": "Per limitare la quantità di dati restituiti in ogni risposta senza perdere l'accesso agli altri risultati",
        "motivo_distrattore_forte": (
            "È molto vicino perché descrive un effetto reale della paginazione, "
            "ma la risposta corretta è più generale: divide i risultati in blocchi piccoli e gestibili."
        ),
    },
    "INF-AV-0105": {
        "opzioni": [
            "Automatizza controlli, test e rilascio riducendo errori manuali ripetitivi",
            "Automatizza test e build, ma richiede comunque controllo umano e codice scritto correttamente",
            "Sostituisce completamente la necessità di scrivere codice",
            "Impedisce a più sviluppatori di collaborare sullo stesso progetto",
        ],
        "risposta_corretta": "Automatizza controlli, test e rilascio riducendo errori manuali ripetitivi",
        "spiegazione": (
            "Una pipeline CI/CD può eseguire test, build e deploy in modo automatico. "
            "Questo rende più affidabile il processo di rilascio e riduce operazioni manuali ripetitive, "
            "ma non sostituisce la scrittura del codice o la collaborazione tra sviluppatori."
        ),
        "distrattore_forte": "Automatizza test e build, ma richiede comunque controllo umano e codice scritto correttamente",
        "motivo_distrattore_forte": (
            "È vicino perché descrive una parte realistica della CI/CD, "
            "ma è meno completo: la risposta corretta include anche controlli, rilascio e riduzione degli errori manuali ripetitivi."
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
    print("Domande Informatica certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Categoria Informatica completata: tutte le domande sono ora certificate per il motore.")


main()