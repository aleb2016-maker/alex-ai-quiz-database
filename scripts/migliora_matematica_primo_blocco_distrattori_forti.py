import json
from pathlib import Path

FILE = Path("data/matematica.json")
BACKUP = Path("data/matematica.backup_prima_primo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_matematica_primo_blocco_distrattori_forti.md")

PATCH = {
    "MAT-FAC-0001": {
        "opzioni": [
            "10",
            "12",
            "8",
            "20"
        ],
        "spiegazione": (
            "Il 20% di 50 si calcola facendo 50 × 20 / 100 = 10. "
            "12 e 8 sono risultati vicini ma non corrispondono al 20%, mentre 20 confonde la percentuale con il risultato."
        )
    },

    "MAT-INT-0002": {
        "opzioni": [
            "5",
            "4",
            "6",
            "15"
        ],
        "spiegazione": (
            "Nell'equazione 3x + 4 = 19 si sottrae prima 4 da entrambi i lati: 3x = 15. "
            "Poi si divide per 3: x = 5. Il valore 15 è il risultato intermedio, non il valore finale di x."
        )
    },

    "MAT-AV-0003": {
        "opzioni": [
            "8 giorni",
            "9 giorni",
            "10 giorni",
            "18 giorni"
        ],
        "spiegazione": (
            "Il lavoro totale è 6 × 12 = 72 giornate-operaio. "
            "Con 9 operai servono 72 / 9 = 8 giorni. "
            "9 e 10 sono stime vicine, mentre 18 nasce da un ragionamento diretto invece che inversamente proporzionale."
        )
    },

    "MAT-FAC-0004": {
        "opzioni": [
            "60",
            "40",
            "20",
            "70"
        ],
        "spiegazione": (
            "Tre quarti di 80 significa dividere 80 in 4 parti uguali e prenderne 3. "
            "80 / 4 = 20, poi 20 × 3 = 60. "
            "40 è metà di 80, 20 è un solo quarto, 70 è vicino ma non deriva dalla frazione corretta."
        )
    },

    "MAT-INT-0004": {
        "opzioni": [
            "x = 7",
            "x = 5",
            "x = 9",
            "x = 11"
        ],
        "spiegazione": (
            "Da 2(x + 4) = 22 si divide prima per 2: x + 4 = 11. "
            "Poi si sottrae 4: x = 7. "
            "x = 11 è il valore prima di togliere 4, mentre 5 e 9 derivano da passaggi non corretti."
        )
    },

    "MAT-AV-0004": {
        "opzioni": [
            "50",
            "45",
            "55",
            "60"
        ],
        "spiegazione": (
            "Se il numero iniziale è x, dopo l'aumento del 30% diventa 1,3x. "
            "Quindi 1,3x = 65 e x = 65 / 1,3 = 50. "
            "45, 55 e 60 sono valori vicini, ma non producono 65 dopo un aumento del 30%."
        )
    },

    "MAT-FAC-0005": {
        "opzioni": [
            "10 euro",
            "8 euro",
            "9 euro",
            "12 euro"
        ],
        "spiegazione": (
            "Se 3 quaderni costano 6 euro, un quaderno costa 6 / 3 = 2 euro. "
            "Quindi 5 quaderni costano 5 × 2 = 10 euro. "
            "8 e 9 sono risultati vicini, mentre 12 corrisponde a 6 quaderni allo stesso prezzo unitario."
        )
    },

    "MAT-INT-0005": {
        "opzioni": [
            "60 euro",
            "55 euro",
            "65 euro",
            "70 euro"
        ],
        "spiegazione": (
            "Il 25% di 80 è 80 × 25 / 100 = 20. "
            "Il prezzo finale è 80 - 20 = 60 euro. "
            "55, 65 e 70 sono prezzi vicini ma derivano da sconti diversi."
        )
    },

    "MAT-AV-0005": {
        "opzioni": [
            "80 km/h",
            "75 km/h",
            "85 km/h",
            "90 km/h"
        ],
        "spiegazione": (
            "2 ore e 15 minuti equivalgono a 2,25 ore, perché 15 minuti sono 15 / 60 = 0,25 ore. "
            "La velocità media è distanza / tempo, quindi 180 / 2,25 = 80 km/h. "
            "75, 85 e 90 sono valori vicini, ma non usano correttamente il tempo di 2,25 ore."
        )
    },

    "MAT-FAC-0006": {
        "opzioni": [
            "32",
            "50",
            "25",
            "36"
        ],
        "spiegazione": (
            "Si esegue prima la moltiplicazione: 7 × 2 = 14. "
            "Poi si somma 18 + 14 = 32. "
            "50 nasce facendo prima 18 + 7 e poi moltiplicando per 2; 25 ignora la priorità della moltiplicazione."
        )
    },

    "MAT-INT-0006": {
        "opzioni": [
            "9",
            "8",
            "10",
            "11"
        ],
        "spiegazione": (
            "La media si calcola sommando i valori e dividendo per quanti sono. "
            "6 + 8 + 10 + 12 = 36 e 36 / 4 = 9. "
            "8, 10 e 11 sono valori della zona centrale, ma non sono la media corretta."
        )
    },

    "MAT-AV-0006": {
        "opzioni": [
            "12",
            "9",
            "10",
            "11"
        ],
        "spiegazione": (
            "Da 2x - 3 = x + 9 si porta x a sinistra e -3 a destra: 2x - x = 9 + 3. "
            "Quindi x = 12. "
            "9, 10 e 11 sono vicini, ma non rispettano lo spostamento corretto dei termini."
        )
    },

    "MAT-FAC-0007": {
        "opzioni": [
            "2/4",
            "3/6",
            "4/8",
            "4/6"
        ],
        "spiegazione": (
            "2/4 è equivalente a 1/2 perché dividendo numeratore e denominatore per 2 si ottiene 1/2. "
            "Anche 3/6 e 4/8 hanno lo stesso valore di 1/2, quindi sono troppo corrette per essere distrattori: questa domanda va resa più precisa chiedendo la frazione equivalente tra opzioni con una sola risposta corretta."
        )
    },

    "MAT-INT-0007": {
        "opzioni": [
            "20",
            "16",
            "18",
            "24"
        ],
        "spiegazione": (
            "Il rapporto assenti:presenti è 1:5, cioè per ogni assente ci sono 5 presenti. "
            "Se gli assenti sono 4, i presenti sono 4 × 5 = 20. "
            "16, 18 e 24 sono vicini, ma non rispettano il rapporto 1:5."
        )
    },

    "MAT-AV-0007": {
        "opzioni": [
            "12",
            "8",
            "10",
            "16"
        ],
        "spiegazione": (
            "Per la prima cifra ci sono 4 scelte. "
            "Per la seconda restano 3 scelte perché non si può ripetere la cifra. "
            "Quindi i codici possibili sono 4 × 3 = 12. "
            "16 sarebbe corretto se la ripetizione fosse permessa."
        )
    },

    "MAT-FAC-0008": {
        "opzioni": [
            "40 cm²",
            "13 cm²",
            "26 cm²",
            "80 cm²"
        ],
        "spiegazione": (
            "L'area del rettangolo si calcola con base × altezza. "
            "Quindi 8 × 5 = 40 cm². "
            "13 è la somma 8 + 5, 26 è il perimetro 2 × (8 + 5), 80 è il doppio dell'area."
        )
    },

    "MAT-INT-0008": {
        "opzioni": [
            "9 cm",
            "8 cm",
            "6 cm",
            "12 cm"
        ],
        "spiegazione": (
            "Un quadrato ha 4 lati uguali. "
            "Se il perimetro è 36 cm, il lato misura 36 / 4 = 9 cm. "
            "8 è vicino ma non corretto, 6 e 12 derivano da divisioni non adatte al perimetro del quadrato."
        )
    },

    "MAT-AV-0008": {
        "opzioni": [
            "32",
            "24",
            "28",
            "36"
        ],
        "spiegazione": (
            "Se il numero minore è x, il maggiore è 2x. "
            "La somma è x + 2x = 48, quindi 3x = 48 e x = 16. "
            "Il numero maggiore è 2 × 16 = 32. "
            "24 è metà della somma, mentre 28 e 36 sono valori vicini ma non rispettano il rapporto doppio."
        )
    },

    "MAT-INT-0009": {
        "opzioni": [
            "3/10",
            "7/10",
            "3/7",
            "1/3"
        ],
        "spiegazione": (
            "La probabilità si calcola con casi favorevoli diviso casi totali. "
            "Le palline rosse sono 3 e le palline totali sono 3 + 7 = 10. "
            "Quindi la probabilità è 3/10. "
            "7/10 riguarda le blu, 3/7 confronta rosse e blu senza usare il totale."
        )
    },

    "MAT-AV-0009": {
        "opzioni": [
            "25%",
            "20%",
            "30%",
            "35%"
        ],
        "spiegazione": (
            "L'aumento è 150 - 120 = 30. "
            "La percentuale di aumento si calcola rispetto al valore iniziale: 30 / 120 × 100 = 25%. "
            "30% confonde l'aumento assoluto 30 con la percentuale."
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
        raise SystemExit("ERRORE: data/matematica.json non trovato.")

    if not BACKUP.exists():
        BACKUP.write_text(FILE.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"Backup creato: {BACKUP}")
    else:
        print(f"Backup già presente: {BACKUP}")

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
            "Ogni risposta errata deve essere un errore matematico plausibile: "
            "calcolo vicino, passaggio saltato, formula invertita o interpretazione numerica quasi corretta."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento Matematica - primo blocco distrattori forti",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: errori matematici plausibili, risultati vicini, passaggi saltati o formule applicate in modo parziale.",
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

    print("===== MIGLIORAMENTO MATEMATICA - PRIMO BLOCCO =====")
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
    print("OK: primo blocco Matematica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
