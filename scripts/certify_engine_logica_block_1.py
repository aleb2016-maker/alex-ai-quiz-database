import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "LOG-CRI-INT-0004": {
        "opzioni": [
            "Alcune persone che documentano gli errori controllano i log",
            "Tutte le persone che documentano gli errori controllano i log",
            "Tutte le persone che controllano i log documentano errori",
            "Alcuni tecnici non controllano i log",
        ],
        "risposta_corretta": "Alcune persone che documentano gli errori controllano i log",
        "spiegazione": (
            "Sappiamo che alcuni tecnici documentano gli errori e che tutti i tecnici controllano i log. "
            "Quindi almeno alcune persone che documentano errori controllano anche i log. "
            "Non possiamo però dire che tutte le persone che documentano errori controllino i log."
        ),
        "distrattore_forte": "Tutte le persone che documentano gli errori controllano i log",
        "motivo_distrattore_forte": (
            "È vicino perché riguarda persone che documentano errori e controllano log, "
            "ma è sbagliato perché dalle premesse sappiamo solo che alcuni tecnici documentano errori, non tutti quelli che documentano errori."
        ),
    },
    "LOG-CRI-AV-0005": {
        "opzioni": [
            "L'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche",
            "L'aggiornamento è la causa più probabile solo perché è avvenuto prima degli errori",
            "Gli errori sono certamente indipendenti dall'aggiornamento perché li hanno segnalati solo alcuni utenti",
            "Il numero di segnalazioni basta da solo per dimostrare la causa tecnica",
        ],
        "risposta_corretta": "L'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche",
        "spiegazione": (
            "La vicinanza temporale tra aggiornamento ed errori suggerisce una possibile relazione, "
            "ma non dimostra da sola una causa certa. Servono log, test, confronto tra versioni e verifica di altri fattori."
        ),
        "distrattore_forte": "L'aggiornamento è la causa più probabile solo perché è avvenuto prima degli errori",
        "motivo_distrattore_forte": (
            "È vicino perché considera correttamente la vicinanza temporale, "
            "ma è sbagliato perché confonde una possibile correlazione con una causa già dimostrata."
        ),
    },
    "LOG-AST-INT-0004": {
        "opzioni": [
            "F6",
            "F5",
            "E6",
            "G6",
        ],
        "risposta_corretta": "F6",
        "spiegazione": (
            "In ogni trasformazione la lettera avanza di una posizione nell'alfabeto e il numero aumenta di 1. "
            "Quindi E5 diventa F6."
        ),
        "distrattore_forte": "F5",
        "motivo_distrattore_forte": (
            "È vicino perché aggiorna correttamente la lettera da E a F, "
            "ma è sbagliato perché lascia invariato il numero invece di aumentarlo da 5 a 6."
        ),
    },
    "LOG-VER-INT-0004": {
        "opzioni": [
            "prototipo → prodotto definitivo",
            "bozza → revisione",
            "indice → documento finale",
            "idea → titolo",
        ],
        "risposta_corretta": "prototipo → prodotto definitivo",
        "spiegazione": (
            "Una bozza è una versione iniziale che può evolvere in un documento finale. "
            "Allo stesso modo, un prototipo è una versione iniziale che può evolvere in un prodotto definitivo. "
            "Bozza → revisione indica una fase intermedia, non il passaggio completo alla versione finale."
        ),
        "distrattore_forte": "bozza → revisione",
        "motivo_distrattore_forte": (
            "È vicino perché riguarda il miglioramento di una bozza, "
            "ma è sbagliato perché la revisione è una fase intermedia, non il prodotto finale equivalente."
        ),
    },
    "LOG-VER-FAC-0101": {
        "opzioni": [
            "basso",
            "piccolo",
            "lungo",
            "vicino",
        ],
        "risposta_corretta": "basso",
        "spiegazione": (
            "Caldo e freddo sono contrari. Seguendo la stessa logica, il contrario di alto è basso. "
            "Piccolo è vicino come idea generale di dimensione, ma non è il contrario diretto di alto."
        ),
        "distrattore_forte": "piccolo",
        "motivo_distrattore_forte": (
            "È vicino perché riguarda una grandezza o dimensione, "
            "ma è sbagliato perché il contrario diretto di alto è basso, non piccolo."
        ),
    },
    "LOG-NUM-FAC-0101": {
        "opzioni": [
            "20",
            "16",
            "24",
            "25",
        ],
        "risposta_corretta": "20",
        "spiegazione": (
            "La macchina produce 4 pezzi ogni minuto. In 5 minuti produce 4 × 5 = 20 pezzi. "
            "16 sarebbe corretto solo per 4 minuti, mentre 24 sarebbe corretto per 6 minuti."
        ),
        "distrattore_forte": "16",
        "motivo_distrattore_forte": (
            "È vicino perché usa lo stesso ritmo di 4 pezzi al minuto, "
            "ma calcola 4 × 4 invece di 4 × 5."
        ),
    },
    "LOG-NUM-FAC-0102": {
        "opzioni": [
            "48",
            "24",
            "36",
            "64",
        ],
        "risposta_corretta": "48",
        "spiegazione": (
            "Partiamo da 3. Primo raddoppio: 6. Secondo: 12. Terzo: 24. Quarto: 48. "
            "24 è il valore dopo tre raddoppi, quindi è vicino ma incompleto."
        ),
        "distrattore_forte": "24",
        "motivo_distrattore_forte": (
            "È vicino perché segue correttamente i raddoppi, "
            "ma si ferma al terzo raddoppio invece di arrivare al quarto."
        ),
    },
    "LOG-CRI-FAC-0101": {
        "opzioni": [
            "Fido è un animale",
            "Fido potrebbe non essere un animale anche se è un cane",
            "Tutti gli animali sono cani",
            "Alcuni cani non sono animali",
        ],
        "risposta_corretta": "Fido è un animale",
        "spiegazione": (
            "Se tutti i cani sono animali e Fido è un cane, allora Fido appartiene al gruppo degli animali. "
            "Non vale invece il contrario: non tutti gli animali sono cani."
        ),
        "distrattore_forte": "Fido potrebbe non essere un animale anche se è un cane",
        "motivo_distrattore_forte": (
            "È vicino perché parla proprio di Fido e del fatto che sia un cane, "
            "ma contraddice la premessa: se tutti i cani sono animali, Fido deve essere un animale."
        ),
    },
    "LOG-CRI-FAC-0102": {
        "opzioni": [
            "Marco prende l'ombrello",
            "Marco prende l'ombrello solo se piove molto forte",
            "Oggi non piove",
            "Marco prende sempre l'ombrello",
        ],
        "risposta_corretta": "Marco prende l'ombrello",
        "spiegazione": (
            "La regola dice che quando piove Marco prende l'ombrello. "
            "Poiché oggi piove, la conclusione corretta è che Marco prende l'ombrello. "
            "Non possiamo aggiungere condizioni non presenti, come 'solo se piove molto forte'."
        ),
        "distrattore_forte": "Marco prende l'ombrello solo se piove molto forte",
        "motivo_distrattore_forte": (
            "È vicino perché collega ombrello e pioggia, "
            "ma è sbagliato perché aggiunge una condizione non presente nella premessa."
        ),
    },
    "LOG-VER-INT-0101": {
        "opzioni": [
            "scuola",
            "classe",
            "lezione",
            "libro",
        ],
        "risposta_corretta": "scuola",
        "spiegazione": (
            "Il medico lavora tipicamente in ospedale. "
            "Allo stesso modo, l'insegnante lavora tipicamente in una scuola. "
            "Classe e lezione sono collegate all'insegnante, ma non rappresentano il luogo generale equivalente."
        ),
        "distrattore_forte": "classe",
        "motivo_distrattore_forte": (
            "È vicino perché l'insegnante lavora spesso in classe, "
            "ma la relazione più generale equivalente a medico → ospedale è insegnante → scuola."
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
    print("Domande Logica certificate:", len(tutti_modificati))

    if mancanti:
        print("ATTENZIONE: questi ID non sono stati trovati:")

        for id_domanda in mancanti:
            print(" -", id_domanda)
    else:
        print("Primo blocco Logica certificato correttamente.")


main()