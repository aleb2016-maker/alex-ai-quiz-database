import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTO = {
    "id": "INF-AV-0103",
    "opzioni": [
        "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
        "Perché conserva temporaneamente dati frequenti, ma può restituire dati vecchi se non viene gestita bene",
        "Perché sposta automaticamente ogni dato dal database alla memoria locale",
        "Perché riduce il carico dell'applicazione anche quando i dati non vengono riutilizzati",
    ],
    "risposta_corretta": "Perché evita di ricalcolare o recuperare più volte dati usati spesso",
    "spiegazione": (
        "La cache conserva temporaneamente risultati o dati molto richiesti. "
        "Questo può ridurre tempi di risposta e carico su database o servizi esterni. "
        "Va però gestita bene, perché una cache non aggiornata può restituire dati vecchi."
    ),
    "distrattore_forte": (
        "Perché conserva temporaneamente dati frequenti, ma può restituire dati vecchi se non viene gestita bene"
    ),
    "motivo_distrattore_forte": (
        "È vicino perché descrive un comportamento reale della cache, cioè conservare dati frequenti. "
        "È però sbagliato come risposta principale perché mette al centro il rischio di dati vecchi, "
        "mentre il vantaggio prestazionale nasce dal non ricalcolare o recuperare più volte gli stessi dati."
    ),
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

    for lista_domande in liste_domande:
        for domanda in lista_domande:
            if not isinstance(domanda, dict):
                continue

            if domanda.get("id") == AGGIORNAMENTO["id"]:
                domanda.update(AGGIORNAMENTO)
                modificato = True

    if modificato:
        salva_json(percorso, dati)

    return modificato


def main():
    trovato = False

    for percorso in DATA_DIR.rglob("*.json"):
        modificato = aggiorna_file(percorso)

        if modificato:
            print("File aggiornato:", percorso)
            print(" -", AGGIORNAMENTO["id"])
            trovato = True

    if trovato:
        print("")
        print("Domanda rossa corretta.")
    else:
        print("")
        print("ATTENZIONE: domanda non trovata:", AGGIORNAMENTO["id"])


main()