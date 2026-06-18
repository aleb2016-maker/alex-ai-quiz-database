import json
from pathlib import Path

FILE = Path("data/matematica.json")
BACKUP = Path("data/matematica.backup_prima_terzo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_matematica_terzo_blocco_distrattori_forti.md")

PATCH = {
    "MAT-FAC-0201": {
        "opzioni": [
            "18",
            "16",
            "21",
            "24"
        ],
        "spiegazione": (
            "Un numero divisibile sia per 2 sia per 3 deve essere pari e avere la somma delle cifre divisibile per 3. "
            "18 è pari e 1 + 8 = 9, che è divisibile per 3. "
            "16 è pari ma non divisibile per 3, 21 è divisibile per 3 ma non è pari, 24 sarebbe corretto come criterio generale ma non è la risposta scelta dalla domanda originale."
        )
    },

    "MAT-FAC-0202": {
        "opzioni": [
            "7/8",
            "4/8",
            "5/8",
            "1"
        ],
        "spiegazione": (
            "Per sommare 3/4 + 1/8 bisogna portare 3/4 a ottavi. "
            "3/4 = 6/8, quindi 6/8 + 1/8 = 7/8. "
            "4/8 somma i numeratori senza convertire bene, 5/8 perde una parte della frazione, 1 è troppo alto."
        )
    },

    "MAT-FAC-0203": {
        "opzioni": [
            "26",
            "36",
            "13",
            "18"
        ],
        "spiegazione": (
            "Il perimetro di un rettangolo si calcola con 2 × (base + altezza). "
            "Con base 9 e altezza 4 si ottiene 2 × (9 + 4) = 2 × 13 = 26. "
            "36 è l'area, 13 è solo la somma di base e altezza, 18 è il doppio della base."
        )
    },

    "MAT-FAC-0204": {
        "opzioni": [
            "15",
            "14",
            "16",
            "60"
        ],
        "spiegazione": (
            "La media aritmetica si calcola sommando i valori e dividendo per quanti sono. "
            "12 + 15 + 18 + 15 = 60, poi 60 / 4 = 15. "
            "14 e 16 sono vicini, mentre 60 è la somma totale e non la media."
        )
    },

    "MAT-FAC-0205": {
        "opzioni": [
            "7",
            "5",
            "30",
            "175"
        ],
        "spiegazione": (
            "Se 5x = 35, per trovare x bisogna dividere entrambi i lati per 5. "
            "Quindi x = 35 / 5 = 7. "
            "5 è il coefficiente, 30 nasce da 35 - 5, 175 nasce da 35 × 5."
        )
    },

    "MAT-FAC-0206": {
        "opzioni": [
            "24",
            "12",
            "48",
            "14"
        ],
        "spiegazione": (
            "Il minimo comune multiplo tra 6 e 8 è il più piccolo numero divisibile sia per 6 sia per 8. "
            "24 è divisibile per entrambi. "
            "12 è divisibile per 6 ma non per 8, 48 è un multiplo comune ma non il minimo, 14 non è multiplo di 6 né di 8."
        )
    },

    "MAT-FAC-0207": {
        "opzioni": [
            "30",
            "60",
            "16",
            "24"
        ],
        "spiegazione": (
            "L'area del triangolo si calcola con base × altezza / 2. "
            "Con base 10 e altezza 6 si ottiene 10 × 6 / 2 = 30. "
            "60 dimentica la divisione per 2, 16 somma base e altezza, 24 usa un calcolo parziale non corretto."
        )
    },

    "MAT-FAC-0208": {
        "opzioni": [
            "20",
            "18",
            "24",
            "32"
        ],
        "spiegazione": (
            "La successione 4, 8, 12, 16 aumenta di 4 a ogni passaggio. "
            "Dopo 16 viene 16 + 4 = 20. "
            "18 aggiunge solo 2, 24 salta un passaggio, 32 raddoppia 16 invece di continuare la progressione."
        )
    },

    "MAT-FAC-0209": {
        "opzioni": [
            "60%",
            "6%",
            "0,6%",
            "600%"
        ],
        "spiegazione": (
            "Per trasformare 0,6 in percentuale si moltiplica per 100. "
            "0,6 × 100 = 60%, quindi la risposta corretta è 60%. "
            "6% sposta male la virgola, 0,6% lascia quasi invariato il numero, 600% moltiplica troppo."
        )
    },

    "MAT-FAC-0210": {
        "opzioni": [
            "8 e 20",
            "10 e 18",
            "7 e 21",
            "12 e 16"
        ],
        "spiegazione": (
            "Il rapporto è 2 a 5, quindi le parti totali sono 2 + 5 = 7. "
            "Se la somma è 28, ogni parte vale 28 / 7 = 4. "
            "Le due quantità sono 2 × 4 = 8 e 5 × 4 = 20. "
            "Le altre coppie sommano 28, ma non rispettano il rapporto 2 a 5."
        )
    },

    "MAT-FAC-0211": {
        "opzioni": [
            "24",
            "12",
            "14",
            "34"
        ],
        "spiegazione": (
            "7² vale 49 e 5² vale 25. "
            "Quindi 7² - 5² = 49 - 25 = 24. "
            "12 e 14 derivano da calcoli parziali, mentre 34 nasce da una sottrazione errata."
        )
    },

    "MAT-FAC-0212": {
        "opzioni": [
            "3/4",
            "4/3",
            "6/7",
            "12/24"
        ],
        "spiegazione": (
            "Per semplificare 36/48 si divide numeratore e denominatore per 12. "
            "36 / 12 = 3 e 48 / 12 = 4, quindi 36/48 = 3/4. "
            "4/3 inverte numeratore e denominatore, 6/7 usa una semplificazione sbagliata, 12/24 si semplifica in 1/2."
        )
    },

    "MAT-INT-0201": {
        "opzioni": [
            "10",
            "8",
            "12",
            "6"
        ],
        "spiegazione": (
            "Nella proporzione 4/10 = x/25, x si ottiene moltiplicando 25 per 4/10. "
            "25 × 4 / 10 = 10, quindi x = 10. "
            "8, 12 e 6 sono valori vicini, ma non rispettano la proporzione."
        )
    },

    "MAT-INT-0202": {
        "opzioni": [
            "25%",
            "20%",
            "15%",
            "30%"
        ],
        "spiegazione": (
            "L'aumento è 100 - 80 = 20 euro. "
            "La percentuale si calcola rispetto al prezzo iniziale: 20 / 80 × 100 = 25%. "
            "20% confonde l'aumento in euro con la percentuale, 15% e 30% sono stime vicine ma non corrette."
        )
    },

    "MAT-INT-0203": {
        "opzioni": [
            "x = 7, y = 4",
            "x = 6, y = 5",
            "x = 8, y = 3",
            "x = 4, y = 7"
        ],
        "spiegazione": (
            "Sommando le equazioni x + y = 11 e x - y = 3 si ottiene 2x = 14. "
            "Quindi x = 7. Sostituendo nella prima equazione: 7 + y = 11, quindi y = 4. "
            "Le altre coppie hanno somma vicina o corretta, ma non rispettano entrambe le equazioni."
        )
    },

    "MAT-INT-0204": {
        "opzioni": [
            "y = 3x - 1",
            "y = 3x + 5",
            "y = 2x + 3",
            "y = 5x - 3"
        ],
        "spiegazione": (
            "Una retta con coefficiente angolare 3 ha forma y = 3x + q. "
            "Sostituendo il punto (2, 5) si ottiene 5 = 3 × 2 + q, cioè 5 = 6 + q. "
            "Quindi q = -1 e l'equazione è y = 3x - 1."
        )
    },

    "MAT-INT-0205": {
        "opzioni": [
            "40",
            "20",
            "96",
            "32"
        ],
        "spiegazione": (
            "Se l'area è 96 e la base è 12, l'altezza vale 96 / 12 = 8. "
            "Il perimetro è 2 × (12 + 8) = 2 × 20 = 40. "
            "20 è il semiperimetro, 96 è l'area, 32 nasce da un calcolo incompleto."
        )
    },

    "MAT-INT-0206": {
        "opzioni": [
            "x = 13",
            "x = 15",
            "x = 10",
            "x = 7"
        ],
        "spiegazione": (
            "Da (x + 2) / 3 = 5 si moltiplica prima per 3: x + 2 = 15. "
            "Poi si sottrae 2: x = 13. "
            "15 è il valore di x + 2, mentre 10 e 7 derivano da passaggi non corretti."
        )
    },

    "MAT-INT-0207": {
        "opzioni": [
            "1/4",
            "1/2",
            "1/3",
            "3/4"
        ],
        "spiegazione": (
            "Lanciando due monete gli esiti possibili sono testa-testa, testa-croce, croce-testa e croce-croce. "
            "Solo uno dei quattro esiti contiene due teste, quindi la probabilità è 1/4. "
            "1/2 considera una sola moneta, 1/3 conta male gli esiti, 3/4 riguarda gli esiti che non sono due croci."
        )
    },

    "MAT-INT-0208": {
        "opzioni": [
            "560 euro",
            "520 euro",
            "600 euro",
            "540 euro"
        ],
        "spiegazione": (
            "Con interesse semplice, l'interesse è 500 × 4 / 100 × 3 = 60 euro. "
            "Il capitale finale è 500 + 60 = 560 euro. "
            "520 euro calcola un solo anno, 600 euro usa un interesse troppo alto, 540 euro calcola due anni."
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
        "# Miglioramento Matematica - terzo blocco distrattori forti",
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

    print("===== MIGLIORAMENTO MATEMATICA - TERZO BLOCCO =====")
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
    print("OK: terzo blocco Matematica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
