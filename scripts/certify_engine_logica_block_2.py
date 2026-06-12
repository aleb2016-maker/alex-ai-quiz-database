import json
from pathlib import Path


DATA_DIR = Path("data")


AGGIORNAMENTI = {
    "LOG-VER-INT-0102": {
        "opzioni": [
            "uovo : uccello",
            "germoglio : pianta",
            "foglia : ramo",
            "frutto : albero",
        ],
        "risposta_corretta": "uovo : uccello",
        "spiegazione": (
            "Dal seme può svilupparsi una pianta. In modo simile, dall'uovo può svilupparsi un uccello. "
            "Germoglio : pianta è vicino, ma rappresenta una fase già successiva allo sviluppo iniziale, "
            "mentre seme e uovo sono punti di origine."
        ),
        "distrattore_forte": "germoglio : pianta",
        "motivo_distrattore_forte": (
            "È vicino perché anche il germoglio può diventare una pianta, "
            "ma è sbagliato rispetto all'analogia più precisa: seme e uovo sono elementi iniziali da cui nasce lo sviluppo."
        ),
    },
    "LOG-NUM-INT-0101": {
        "opzioni": [
            "47",
            "46",
            "45",
            "49",
        ],
        "risposta_corretta": "47",
        "spiegazione": (
            "Partiamo da 2. Passaggio 1: 2 × 2 + 1 = 5. "
            "Passaggio 2: 5 × 2 + 1 = 11. "
            "Passaggio 3: 11 × 2 + 1 = 23. "
            "Passaggio 4: 23 × 2 + 1 = 47."
        ),
        "distrattore_forte": "46",
        "motivo_distrattore_forte": (
            "È vicino perché sembra derivare dal raddoppio finale di 23, "
            "ma dimentica il +1 dell'ultimo passaggio: 23 × 2 + 1 = 47."
        ),
    },
    "LOG-NUM-INT-0102": {
        "opzioni": [
            "12",
            "13",
            "14",
            "15",
        ],
        "risposta_corretta": "12",
        "spiegazione": (
            "Le diminuzioni aumentano di 1 ogni volta: -3, -4, -5. "
            "Dopo 18 bisogna togliere 6, quindi 18 - 6 = 12."
        ),
        "distrattore_forte": "13",
        "motivo_distrattore_forte": (
            "È vicino perché continua a diminuire la sequenza, "
            "ma usa una sottrazione di 5 invece della sottrazione corretta di 6."
        ),
    },
    "LOG-CRI-INT-0101": {
        "opzioni": [
            "Alcuni programmatori sanno usare variabili",
            "Tutti i programmatori sanno usare variabili",
            "Tutti quelli che sanno usare variabili conoscono Python",
            "Nessun programmatore conosce Python",
        ],
        "risposta_corretta": "Alcuni programmatori sanno usare variabili",
        "spiegazione": (
            "Alcuni programmatori conoscono Python e tutti quelli che conoscono Python sanno usare variabili. "
            "Quindi almeno alcuni programmatori sanno usare variabili. "
            "Non possiamo però concludere che tutti i programmatori sappiano usare variabili."
        ),
        "distrattore_forte": "Tutti i programmatori sanno usare variabili",
        "motivo_distrattore_forte": (
            "È vicino perché la premessa collega Python e variabili, "
            "ma è sbagliato perché sappiamo solo che alcuni programmatori conoscono Python, non tutti."
        ),
    },
    "LOG-CRI-INT-0102": {
        "opzioni": [
            "L'app non ha superato tutti i test",
            "L'app potrebbe aver superato tutti i test anche se non viene pubblicata",
            "I test non sono mai stati eseguiti",
            "Ogni app pubblicata supera i test",
        ],
        "risposta_corretta": "L'app non ha superato tutti i test",
        "spiegazione": (
            "La regola dice: se un'app supera tutti i test, allora viene pubblicata. "
            "Se l'app non viene pubblicata, possiamo concludere che non ha superato tutti i test. "
            "È un ragionamento per contrapposizione."
        ),
        "distrattore_forte": "L'app potrebbe aver superato tutti i test anche se non viene pubblicata",
        "motivo_distrattore_forte": (
            "È vicino perché nella realtà potrebbero esistere altri motivi di blocco, "
            "ma nella logica della premessa data è sbagliato: se supera tutti i test, viene pubblicata."
        ),
    },
    "LOG-AST-INT-0101": {
        "opzioni": [
            "ettagono",
            "esagono",
            "ottagono",
            "pentagono",
        ],
        "risposta_corretta": "ettagono",
        "spiegazione": (
            "Le forme aumentano di un lato alla volta: triangolo 3 lati, quadrato 4, pentagono 5, esagono 6. "
            "Dopo viene l'ettagono, che ha 7 lati."
        ),
        "distrattore_forte": "ottagono",
        "motivo_distrattore_forte": (
            "È vicino perché continua con un poligono successivo, "
            "ma salta un passaggio: dopo 6 lati viene 7, non 8."
        ),
    },
    "LOG-VER-AV-0101": {
        "opzioni": [
            "apprendimento",
            "interrogazione",
            "lezione",
            "materia",
        ],
        "risposta_corretta": "apprendimento",
        "spiegazione": (
            "L'allenamento può portare a un miglioramento. "
            "Allo stesso modo, lo studio può portare ad apprendimento. "
            "Interrogazione e lezione sono collegate allo studio, ma non rappresentano il risultato logico più diretto."
        ),
        "distrattore_forte": "interrogazione",
        "motivo_distrattore_forte": (
            "È vicino perché è collegata allo studio, "
            "ma è sbagliato perché l'interrogazione è una verifica, mentre l'apprendimento è il risultato dello studio."
        ),
    },
    "LOG-NUM-AV-0101": {
        "opzioni": [
            "36",
            "35",
            "49",
            "30",
        ],
        "risposta_corretta": "36",
        "spiegazione": (
            "La sequenza contiene quadrati perfetti: 1²=1, 2²=4, 3²=9, 4²=16, 5²=25. "
            "Il successivo è 6²=36."
        ),
        "distrattore_forte": "35",
        "motivo_distrattore_forte": (
            "È vicino perché è molto prossimo a 36, "
            "ma è sbagliato perché non è un quadrato perfetto della sequenza."
        ),
    },
    "LOG-NUM-AV-0102": {
        "opzioni": [
            "42",
            "40",
            "44",
            "48",
        ],
        "risposta_corretta": "42",
        "spiegazione": (
            "Le differenze aumentano di 2: 4, 6, 8, 10. "
            "La differenza successiva è 12. Quindi 30 + 12 = 42."
        ),
        "distrattore_forte": "40",
        "motivo_distrattore_forte": (
            "È vicino perché aggiunge ancora 10 all'ultimo valore noto, "
            "ma è sbagliato perché la differenza deve aumentare a 12."
        ),
    },
    "LOG-CRI-AV-0101": {
        "opzioni": [
            "Alcune persone che usano Git lavorano su database",
            "Alcune persone che lavorano su database sono sviluppatori del team",
            "Tutti gli sviluppatori lavorano su database",
            "Tutti quelli che usano Git sono sviluppatori",
        ],
        "risposta_corretta": "Alcune persone che usano Git lavorano su database",
        "spiegazione": (
            "La seconda premessa afferma direttamente che alcune persone che usano Git lavorano anche su database. "
            "Non possiamo però concludere che quelle persone siano sviluppatori del team, "
            "né che tutti gli sviluppatori lavorino su database."
        ),
        "distrattore_forte": "Alcune persone che lavorano su database sono sviluppatori del team",
        "motivo_distrattore_forte": (
            "È vicino perché collega database, Git e sviluppatori, "
            "ma è sbagliato perché la premessa non dice che le persone che usano Git e lavorano su database siano sviluppatori del team."
        ),
    },
    "LOG-CRI-AV-0102": {
        "opzioni": [
            "Il server potrebbe essere inattivo, ma non è certo",
            "Il server è sicuramente inattivo",
            "L'app non può mostrare errori per altri motivi",
            "Il server è sicuramente attivo",
        ],
        "risposta_corretta": "Il server potrebbe essere inattivo, ma non è certo",
        "spiegazione": (
            "La regola dice che se il server è inattivo, allora l'app mostra un errore. "
            "Ma se l'app mostra un errore, l'errore potrebbe avere anche altre cause. "
            "Concludere che il server è sicuramente inattivo sarebbe un errore logico."
        ),
        "distrattore_forte": "Il server è sicuramente inattivo",
        "motivo_distrattore_forte": (
            "È vicino perché il server inattivo è una causa possibile dell'errore, "
            "ma è sbagliato perché l'errore potrebbe dipendere anche da altre cause."
        ),
    },
    "LOG-AST-AV-0101": {
        "opzioni": [
            "ettagono rosso",
            "ettagono blu",
            "ottagono rosso",
            "esagono rosso",
        ],
        "risposta_corretta": "ettagono rosso",
        "spiegazione": (
            "Il numero di lati aumenta: 3, 4, 5, 6, quindi 7 lati, cioè ettagono. "
            "Il colore alterna rosso, blu, rosso, blu, quindi il prossimo è rosso."
        ),
        "distrattore_forte": "ettagono blu",
        "motivo_distrattore_forte": (
            "È vicino perché individua correttamente la forma con 7 lati, "
            "ma è sbagliato perché non rispetta l'alternanza dei colori: dopo blu deve tornare rosso."
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
        print("Secondo blocco Logica certificato correttamente.")


main()