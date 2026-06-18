import json
from pathlib import Path

FILE = Path("data/logica/ragionamento_astratto.json")
BACKUP = Path("backups/ragionamento_astratto.backup_prima_terzo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_logica_terzo_blocco_distrattori_forti.md")

PATCH = {
    "LOG-AST-FAC-0001": {
        "opzioni": [
            "Cerchio",
            "Quadrato",
            "Triangolo",
            "Rettangolo"
        ],
        "spiegazione": (
            "La sequenza alterna sempre due forme: cerchio e quadrato. "
            "L'ordine è cerchio, quadrato, cerchio, quadrato. "
            "Dopo il quadrato torna quindi il cerchio. "
            "Quadrato ripeterebbe la stessa forma appena vista. "
            "Triangolo e rettangolo introdurrebbero forme nuove che non fanno parte dell'alternanza."
        )
    },

    "LOG-AST-INT-0002": {
        "opzioni": [
            "F",
            "E",
            "G",
            "H"
        ],
        "spiegazione": (
            "La regola sposta ogni lettera avanti di due posizioni nell'alfabeto. "
            "A diventa C, B diventa D e C diventa E. "
            "Seguendo la stessa regola, D diventa F. "
            "E avanza di una sola posizione, G avanza di tre, H avanza di quattro."
        )
    },

    "LOG-AST-AV-0003": {
        "opzioni": [
            "I10K",
            "I8K",
            "J10K",
            "I10J"
        ],
        "spiegazione": (
            "La trasformazione modifica tre elementi insieme. "
            "La prima lettera avanza di una posizione, il numero raddoppia e l'ultima lettera avanza di una posizione. "
            "Quindi H diventa I, 5 diventa 10 e J diventa K. "
            "Il risultato corretto è I10K. "
            "I8K non raddoppia correttamente il numero. "
            "J10K avanza troppo la prima lettera. "
            "I10J non fa avanzare l'ultima lettera."
        )
    },

    "LOG-AST-INT-0004": {
        "opzioni": [
            "F6",
            "F5",
            "E6",
            "G6"
        ],
        "spiegazione": (
            "In ogni trasformazione la lettera avanza di una posizione e il numero aumenta di 1. "
            "A1 diventa B2, C3 diventa D4. "
            "Seguendo la stessa regola, E5 diventa F6. "
            "F5 cambia solo la lettera. "
            "E6 cambia solo il numero. "
            "G6 fa avanzare troppo la lettera."
        )
    },

    "LOG-AST-INT-0101": {
        "opzioni": [
            "ettagono",
            "esagono",
            "ottagono",
            "pentagono"
        ],
        "spiegazione": (
            "La sequenza aumenta il numero di lati di una unità alla volta. "
            "Triangolo ha 3 lati, quadrato 4, pentagono 5, esagono 6. "
            "Dopo l'esagono viene l'ettagono, che ha 7 lati. "
            "Esagono ripete la forma precedente. "
            "Ottagono salta un passaggio. "
            "Pentagono torna indietro."
        )
    },

    "LOG-AST-AV-0101": {
        "opzioni": [
            "ettagono rosso",
            "ettagono blu",
            "ottagono rosso",
            "esagono rosso"
        ],
        "spiegazione": (
            "La sequenza cambia due elementi: numero di lati e colore. "
            "I lati aumentano di uno: triangolo, quadrato, pentagono, esagono, quindi ettagono. "
            "Il colore alterna rosso, blu, rosso, blu, quindi il prossimo colore è rosso. "
            "Il risultato corretto è ettagono rosso. "
            "Ettagono blu sbaglia il colore. "
            "Ottagono rosso salta un lato. "
            "Esagono rosso non aumenta il numero di lati."
        )
    },

    "LOG-AST-AV-0102": {
        "opzioni": [
            "sinistra",
            "alto",
            "destra",
            "basso"
        ],
        "spiegazione": (
            "La freccia ruota sempre di 90 gradi in senso orario. "
            "La sequenza delle direzioni è alto, destra, basso, sinistra. "
            "Dopo basso viene quindi sinistra. "
            "Alto ricomincerebbe il ciclo troppo presto. "
            "Destra ripeterebbe una direzione già superata. "
            "Basso non applica la rotazione successiva."
        )
    },

    "LOG-AST-FAC-0103": {
        "opzioni": [
            "triangolo blu",
            "triangolo rosso",
            "cerchio blu",
            "quadrato blu"
        ],
        "spiegazione": (
            "La sequenza combina un ciclo di forme e un'alternanza di colori. "
            "Le forme seguono cerchio, quadrato, triangolo e poi ricominciano. "
            "I colori alternano rosso e blu. "
            "Dopo quadrato rosso viene quindi triangolo blu. "
            "Triangolo rosso mantiene la forma ma sbaglia il colore. "
            "Cerchio blu anticipa il ciclo successivo. "
            "Quadrato blu ripete la forma precedente."
        )
    },

    "LOG-AST-INT-0103": {
        "opzioni": [
            "esagono con 4 punti",
            "esagono con 3 punti",
            "pentagono con 4 punti",
            "ettagono con 4 punti"
        ],
        "spiegazione": (
            "La regola aumenta di 1 sia il numero dei lati sia il numero dei punti interni. "
            "Il pentagono ha 5 lati, quindi diventa un esagono con 6 lati. "
            "I punti interni passano da 3 a 4. "
            "Il risultato corretto è esagono con 4 punti. "
            "Esagono con 3 punti cambia solo i lati. "
            "Pentagono con 4 punti cambia solo i punti. "
            "Ettagono con 4 punti aumenta troppo i lati."
        )
    },

    "LOG-AST-AV-0103": {
        "opzioni": [
            "ettagono scuro con 5 punti",
            "ettagono chiaro con 5 punti",
            "ottagono scuro con 5 punti",
            "ettagono scuro con 4 punti"
        ],
        "spiegazione": (
            "La regola cambia tre elementi insieme. "
            "L'esagono ha 6 lati, quindi aumentando di 1 diventa un ettagono. "
            "Il colore alterna da chiaro a scuro. "
            "Gli oggetti interni aumentano di 2, quindi i punti passano da 3 a 5. "
            "Il risultato corretto è ettagono scuro con 5 punti. "
            "Ettagono chiaro con 5 punti sbaglia il colore. "
            "Ottagono scuro con 5 punti aumenta troppo i lati. "
            "Ettagono scuro con 4 punti aumenta i punti di 1 invece che di 2."
        )
    },

    "LOG-AST-0201": {
        "opzioni": [
            "CBA",
            "BAC",
            "ACB",
            "CAB"
        ],
        "spiegazione": (
            "La regola inverte l'ordine completo delle lettere. "
            "ABC letto da destra verso sinistra diventa CBA. "
            "BAC scambia solo le prime due lettere. "
            "ACB scambia solo le ultime due. "
            "CAB sposta l'ultima lettera davanti, ma non inverte tutto l'ordine."
        )
    },

    "LOG-AST-0202": {
        "opzioni": [
            "A A B B C C",
            "A B C A B C",
            "A B B C C",
            "A A B C C"
        ],
        "spiegazione": (
            "La regola ripete ogni simbolo una volta mantenendo lo stesso ordine. "
            "A diventa A A, B diventa B B e C diventa C C. "
            "Il risultato corretto è A A B B C C. "
            "A B C A B C ripete l'intera sequenza invece dei singoli simboli. "
            "A B B C C non duplica A. "
            "A A B C C non duplica B."
        )
    },

    "LOG-AST-0203": {
        "opzioni": [
            "765",
            "657",
            "576",
            "756"
        ],
        "spiegazione": (
            "La regola inverte l'ordine delle cifre. "
            "Se 1234 diventa 4321, allora 567 letto al contrario diventa 765. "
            "657 scambia solo le prime due cifre. "
            "576 scambia solo le ultime due. "
            "756 sposta l'ultima cifra davanti, ma non inverte tutta la sequenza."
        )
    },

    "LOG-AST-0204": {
        "opzioni": [
            "E5",
            "E4",
            "D5",
            "F5"
        ],
        "spiegazione": (
            "Nella serie aumentano insieme sia la lettera sia il numero. "
            "A1, B2, C3 e D4 mostrano che la lettera avanza di una posizione e il numero aumenta di 1. "
            "Dopo D4 viene quindi E5. "
            "E4 cambia solo la lettera. "
            "D5 cambia solo il numero. "
            "F5 fa avanzare troppo la lettera."
        )
    },

    "LOG-AST-0205": {
        "opzioni": [
            "CEG",
            "ACE",
            "CFG",
            "BEG"
        ],
        "spiegazione": (
            "Ogni lettera viene sostituita con quella successiva nell'alfabeto. "
            "B diventa C, D diventa E e F diventa G. "
            "Quindi BDF diventa CEG. "
            "ACE sposta le lettere indietro. "
            "CFG cambia correttamente B e F, ma non D. "
            "BEG lascia invariata la prima lettera."
        )
    },

    "LOG-AST-0206": {
        "opzioni": [
            "FE",
            "EF",
            "FG",
            "DE"
        ],
        "spiegazione": (
            "La regola scambia la posizione delle due lettere. "
            "AB diventa BA e CD diventa DC. "
            "Seguendo la stessa regola, EF diventa FE. "
            "EF non applica lo scambio. "
            "FG cambia una lettera. "
            "DE sposta la coppia verso lettere precedenti."
        )
    },

    "LOG-AST-0207": {
        "opzioni": [
            "Z X Y",
            "Y Z X",
            "X Z Y",
            "Z Y X"
        ],
        "spiegazione": (
            "La regola chiede l'ordine ultimo, primo, secondo. "
            "Nella sequenza X Y Z, l'ultimo elemento è Z, il primo è X e il secondo è Y. "
            "Il risultato corretto è Z X Y. "
            "Y Z X parte dal secondo elemento. "
            "X Z Y lascia il primo al suo posto. "
            "Z Y X inverte l'intera sequenza, ma non segue ultimo, primo, secondo."
        )
    },

    "LOG-AST-0208": {
        "opzioni": [
            "D8",
            "D7",
            "E8",
            "C8"
        ],
        "spiegazione": (
            "La sequenza associa ogni lettera al doppio della sua posizione alfabetica. "
            "A corrisponde a 2, B a 4, C a 6. "
            "D è la lettera successiva e corrisponde a 8. "
            "D7 usa la lettera giusta ma il numero sbagliato. "
            "E8 usa il numero giusto ma salta una lettera. "
            "C8 aumenta solo il numero, senza avanzare la lettera."
        )
    },

    "LOG-AST-0209": {
        "opzioni": [
            "DC8",
            "DC4",
            "CD8",
            "DC7"
        ],
        "spiegazione": (
            "La trasformazione applica due regole: inverte le lettere e raddoppia il numero. "
            "AB3 diventa BA6 perché AB diventa BA e 3 diventa 6. "
            "Quindi CD4 diventa DC8. "
            "DC4 inverte le lettere ma non raddoppia il numero. "
            "CD8 raddoppia il numero ma non inverte le lettere. "
            "DC7 inverte le lettere ma aumenta il numero in modo sbagliato."
        )
    },

    "LOG-AST-0210": {
        "opzioni": [
            "I10",
            "H10",
            "I9",
            "J10"
        ],
        "spiegazione": (
            "La serie fa avanzare le lettere saltando una lettera e aumenta i numeri di 2. "
            "Le lettere sono A, C, E, G, quindi dopo G viene I. "
            "I numeri sono 2, 4, 6, 8, quindi dopo 8 viene 10. "
            "Il risultato corretto è I10. "
            "H10 non salta correttamente la lettera. "
            "I9 usa il numero sbagliato. "
            "J10 avanza troppo la lettera."
        )
    }
}


def carica_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def salva_json(path, contenuto):
    path.write_text(json.dumps(contenuto, ensure_ascii=False, indent=2), encoding="utf-8")


def estrai_domande(contenuto):
    if isinstance(contenuto, list):
        return contenuto

    for chiave in ["domande", "questions", "quiz", "items"]:
        if isinstance(contenuto.get(chiave), list):
            return contenuto[chiave]

    raise ValueError("Formato JSON non riconosciuto: non trovo la lista delle domande.")


def aggiorna_opzioni(domanda, nuove_opzioni):
    for chiave in ["opzioni", "options", "risposte", "answers"]:
        if chiave in domanda:
            domanda[chiave] = nuove_opzioni
            return

    domanda["opzioni"] = nuove_opzioni


def aggiorna_risposta_corretta(domanda, testo_corretta):
    for chiave in ["risposta_corretta", "correct_answer", "correct", "answer", "soluzione"]:
        if chiave in domanda:
            valore = str(domanda.get(chiave, "")).strip().upper()

            if valore in ["A", "B", "C", "D"]:
                domanda[chiave] = "A"
            else:
                domanda[chiave] = testo_corretta

            return

    domanda["risposta_corretta"] = testo_corretta


def main():
    if not FILE.exists():
        raise SystemExit("ERRORE: data/logica/ragionamento_astratto.json non trovato.")

    BACKUP.parent.mkdir(parents=True, exist_ok=True)

    if not BACKUP.exists():
        BACKUP.write_text(FILE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato fuori dai dati ufficiali: {BACKUP}")
    else:
        print(f"Backup già presente fuori dai dati ufficiali: {BACKUP}")

    contenuto = carica_json(FILE)
    domande = estrai_domande(contenuto)

    indice_per_id = {
        str(domanda.get("id", "")).strip(): domanda
        for domanda in domande
    }

    aggiornate = []
    non_trovate = []

    for id_domanda, dati in PATCH.items():
        domanda = indice_per_id.get(id_domanda)

        if domanda is None:
            non_trovate.append(id_domanda)
            continue

        nuove_opzioni = dati["opzioni"]

        aggiorna_opzioni(domanda, nuove_opzioni)
        aggiorna_risposta_corretta(domanda, nuove_opzioni[0])
        domanda["spiegazione"] = dati["spiegazione"]
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve essere vicina alla corretta per struttura astratta, "
            "ma sbagliata per un dettaglio preciso: ordine invertito solo in parte, lettera avanzata male, "
            "numero non aggiornato, colore non alternato, lati o punti modificati in modo incompleto."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento Logica - terzo blocco distrattori forti",
        "",
        "File aggiornato: `data/logica/ragionamento_astratto.json`",
        "",
        "Backup salvato fuori dai dati ufficiali: `backups/ragionamento_astratto.backup_prima_terzo_blocco_distrattori_forti.json`",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: distrattori vicini alla trasformazione astratta corretta e sbagliati per un dettaglio preciso.",
        "",
        f"Domande aggiornate: {len(aggiornate)}",
        "",
    ]

    for id_domanda in aggiornate:
        righe.append(f"- {id_domanda}")

    if non_trovate:
        righe.append("")
        righe.append("## ID non trovati")
        righe.append("")

        for id_domanda in non_trovate:
            righe.append(f"- {id_domanda}")

    REPORT.write_text("\n".join(righe), encoding="utf-8")

    print("===== MIGLIORAMENTO LOGICA - TERZO BLOCCO =====")
    print("File: data/logica/ragionamento_astratto.json")
    print(f"Domande aggiornate: {len(aggiornate)}")

    for id_domanda in aggiornate:
        print(f"- {id_domanda}")

    if non_trovate:
        print()
        print("ID non trovati:")

        for id_domanda in non_trovate:
            print(f"- {id_domanda}")

    print()
    print(f"Report creato: {REPORT}")
    print("OK: terzo blocco Logica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
