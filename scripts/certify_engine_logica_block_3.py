import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "LOG-AST-AV-0102": {
        "opzioni": [
            "sinistra",
            "alto",
            "destra",
            "basso",
        ],
        "risposta_corretta": "sinistra",
        "spiegazione": (
            "La rotazione è sempre di 90 gradi in senso orario: alto, destra, basso, sinistra. "
            "Dopo basso, continuando la rotazione oraria, la freccia punta a sinistra."
        ),
        "distrattore_forte": "alto",
        "motivo_distrattore_forte": (
            "È vicino perché appartiene allo stesso ciclo di direzioni, "
            "ma è sbagliato perché alto arriva dopo un ulteriore passaggio, non subito dopo basso."
        ),
    },
    "LOG-VIS-FAC-0001": {
        "distrattore_forte": "A",
        "motivo_distrattore_forte": (
            "È vicino perché è una delle opzioni visive proposte, "
            "ma non rispetta l'alternanza corretta cerchio-quadrato: dopo il quadrato deve tornare il cerchio indicato dall'opzione C."
        ),
    },
    "LOG-VIS-INT-0002": {
        "distrattore_forte": "A",
        "motivo_distrattore_forte": (
            "È vicino perché rappresenta una possibile rotazione della figura, "
            "ma non continua correttamente la rotazione costante di 90 gradi in senso orario indicata dalla sequenza."
        ),
    },
    "LOG-VIS-AV-0003": {
        "distrattore_forte": "C",
        "motivo_distrattore_forte": (
            "È vicino perché rispetta una parte della logica visiva della matrice, "
            "ma non combina correttamente entrambe le regole: alternanza della forma per riga e aumento del riempimento per colonna."
        ),
    },
    "LOG-VER-FAC-0001": {
        "opzioni": [
            "FE",
            "EF",
            "FG",
            "GF",
        ],
        "risposta_corretta": "FE",
        "spiegazione": (
            "In ogni coppia le due lettere vengono invertite: AB diventa BA, CD diventa DC. "
            "Seguendo la stessa regola, EF diventa FE."
        ),
        "distrattore_forte": "EF",
        "motivo_distrattore_forte": (
            "È vicino perché contiene le stesse due lettere della coppia di partenza, "
            "ma è sbagliato perché non le inverte."
        ),
    },
    "LOG-VER-INT-0002": {
        "opzioni": [
            "tagliare",
            "incollare",
            "misurare",
            "disegnare",
        ],
        "risposta_corretta": "tagliare",
        "spiegazione": (
            "La relazione è tra uno strumento e la sua funzione principale. "
            "La penna serve principalmente per scrivere; le forbici servono principalmente per tagliare."
        ),
        "distrattore_forte": "incollare",
        "motivo_distrattore_forte": (
            "È vicino perché è un'azione manuale spesso collegata a carta, forbici e lavori pratici, "
            "ma è sbagliato perché la funzione principale delle forbici è tagliare, non incollare."
        ),
    },
    "LOG-VER-AV-0003": {
        "opzioni": [
            "indizio → ipotesi",
            "prova → verdetto",
            "errore → correzione",
            "causa → conseguenza",
        ],
        "risposta_corretta": "indizio → ipotesi",
        "spiegazione": (
            "Un sintomo è un segnale che aiuta a formulare una diagnosi, ma non coincide con la diagnosi. "
            "Allo stesso modo, un indizio aiuta a formulare un'ipotesi, ma non coincide con una conclusione certa."
        ),
        "distrattore_forte": "prova → verdetto",
        "motivo_distrattore_forte": (
            "È vicino perché collega un elemento osservato a una conclusione, "
            "ma è sbagliato perché prova e verdetto indicano un rapporto più forte e conclusivo rispetto a sintomo e diagnosi."
        ),
    },
    "LOG-AST-FAC-0001": {
        "opzioni": [
            "Cerchio",
            "Quadrato",
            "Triangolo",
            "Rettangolo",
        ],
        "risposta_corretta": "Cerchio",
        "spiegazione": (
            "La sequenza alterna sempre cerchio e quadrato: cerchio, quadrato, cerchio, quadrato. "
            "Dopo il quadrato torna quindi il cerchio."
        ),
        "distrattore_forte": "Quadrato",
        "motivo_distrattore_forte": (
            "È vicino perché è l'altra forma presente nella sequenza, "
            "ma è sbagliato perché ripeterebbe il quadrato invece di rispettare l'alternanza."
        ),
    },
    "LOG-AST-INT-0002": {
        "opzioni": [
            "F",
            "E",
            "G",
            "H",
        ],
        "risposta_corretta": "F",
        "spiegazione": (
            "Ogni lettera viene spostata avanti di due posizioni nell'alfabeto: A diventa C, B diventa D, C diventa E. "
            "Seguendo la stessa regola, D diventa F."
        ),
        "distrattore_forte": "E",
        "motivo_distrattore_forte": (
            "È vicino perché è la lettera successiva a D, "
            "ma è sbagliato perché la regola non avanza di una posizione: avanza di due."
        ),
    },
    "LOG-AST-AV-0003": {
        "opzioni": [
            "I10K",
            "I8K",
            "J10K",
            "I10J",
        ],
        "risposta_corretta": "I10K",
        "spiegazione": (
            "Nelle trasformazioni la prima e l'ultima lettera avanzano di una posizione nell'alfabeto, "
            "mentre il numero viene raddoppiato. Quindi H diventa I, 5 diventa 10 e J diventa K."
        ),
        "distrattore_forte": "I8K",
        "motivo_distrattore_forte": (
            "È vicino perché aggiorna correttamente le due lettere esterne, "
            "ma è sbagliato perché il numero deve essere raddoppiato: 5 diventa 10, non 8."
        ),
    },
    "LOG-CRI-FAC-0001": {
        "opzioni": [
            "Il treno 25 arriva in stazione",
            "Il treno 25 arriva in stazione solo se è in orario",
            "Tutti i treni che arrivano in stazione sono della linea A",
            "Solo il treno 25 della linea A arriva in stazione",
        ],
        "risposta_corretta": "Il treno 25 arriva in stazione",
        "spiegazione": (
            "Se tutti i treni della linea A arrivano in stazione e il treno 25 è della linea A, "
            "allora il treno 25 arriva in stazione. Non possiamo aggiungere condizioni non presenti, come l'orario."
        ),
        "distrattore_forte": "Il treno 25 arriva in stazione solo se è in orario",
        "motivo_distrattore_forte": (
            "È vicino perché parla dello stesso treno e dell'arrivo in stazione, "
            "ma è sbagliato perché aggiunge la condizione dell'orario, che non compare nelle premesse."
        ),
    },
    "LOG-CRI-INT-0002": {
        "opzioni": [
            "Oggi non piove",
            "Non si può dedurre nulla sul tempo",
            "Oggi piove sicuramente",
            "Marco potrebbe non prendere l'ombrello anche se piove",
        ],
        "risposta_corretta": "Oggi non piove",
        "spiegazione": (
            "La regola dice: se piove, Marco prende l'ombrello. "
            "Se oggi Marco non prende l'ombrello, allora la condizione 'piove' non si è verificata. "
            "È una deduzione per contrapposizione: se P implica Q, allora non Q implica non P."
        ),
        "distrattore_forte": "Non si può dedurre nulla sul tempo",
        "motivo_distrattore_forte": (
            "È vicino perché sembra prudente non aggiungere informazioni, "
            "ma è sbagliato: con questa premessa logica possiamo dedurre per contrapposizione che oggi non piove."
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

            tutti_modificati.extend(id_domanda for id_domanda in id_modificati)

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
        print("Terzo blocco Logica certificato correttamente.")


main()