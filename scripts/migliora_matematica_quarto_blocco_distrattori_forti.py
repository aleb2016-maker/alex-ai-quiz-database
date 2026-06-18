import json
from pathlib import Path

FILE = Path("data/matematica.json")
BACKUP = Path("data/matematica.backup_prima_quarto_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_matematica_quarto_blocco_distrattori_forti.md")

PATCH = {
    "MAT-INT-0209": {
        "opzioni": [
            "10",
            "9",
            "12",
            "50"
        ],
        "spiegazione": (
            "La mediana è il valore centrale di una lista ordinata. "
            "I numeri 4, 9, 10, 12 e 15 sono già ordinati e il valore al centro è 10. "
            "9 e 12 sono vicini al centro, mentre 50 è la somma dei valori e non la mediana."
        )
    },

    "MAT-INT-0210": {
        "opzioni": [
            "Sono validi tutti i valori di x maggiori di 4.",
            "Sono validi tutti i valori di x minori di 4.",
            "Sono validi soltanto i valori di x maggiori di 12.",
            "Sono validi tutti i valori di x maggiori di 8."
        ],
        "spiegazione": (
            "La disequazione tre x meno quattro maggiore di otto diventa tre x maggiore di dodici. "
            "Dividendo per tre si ottiene x maggiore di 4. "
            "x minore di 4 inverte il verso, mentre x maggiore di 12 e x maggiore di 8 non completano correttamente la divisione finale."
        )
    },

    "MAT-INT-0211": {
        "opzioni": [
            "2",
            "4",
            "8",
            "1/2"
        ],
        "spiegazione": (
            "Il coefficiente angolare tra i punti (1, 2) e (5, 10) si calcola con la variazione di y divisa per la variazione di x. "
            "Quindi (10 - 2) / (5 - 1) = 8 / 4 = 2. "
            "4 usa solo la variazione di x, 8 usa solo la variazione di y, 1/2 inverte il rapporto."
        )
    },

    "MAT-INT-0212": {
        "opzioni": [
            "21",
            "24",
            "18",
            "27"
        ],
        "spiegazione": (
            "Nella funzione y = 4x - 3, sostituendo x = 6 si ottiene y = 4 × 6 - 3. "
            "Quindi y = 24 - 3 = 21. "
            "24 dimentica il meno 3, 18 sottrae troppo, 27 aggiunge 3 invece di sottrarlo."
        )
    },

    "MAT-INT-0213": {
        "opzioni": [
            "44",
            "22",
            "49",
            "154"
        ],
        "spiegazione": (
            "La circonferenza di un cerchio si calcola con 2 × pi greco × raggio. "
            "Usando pi greco uguale a 22/7 e raggio 7 si ottiene 2 × 22/7 × 7 = 44. "
            "22 usa solo pi greco per il diametro dimezzato, 49 confonde il calcolo con il quadrato del raggio, 154 è l'area."
        )
    },

    "MAT-INT-0214": {
        "opzioni": [
            "125",
            "25",
            "75",
            "15"
        ],
        "spiegazione": (
            "Il volume di un cubo si calcola elevando il lato alla terza potenza. "
            "Con lato 5 si ottiene 5³ = 5 × 5 × 5 = 125. "
            "25 è l'area di una faccia, 75 moltiplica 25 per 3, 15 somma tre volte il lato."
        )
    },

    "MAT-AV-0201": {
        "opzioni": [
            "La coppia corretta è formata da 2 e 3.",
            "La coppia 1 e 6 ha prodotto corretto, ma somma non coerente con il termine centrale.",
            "La coppia -2 e -3 produce segni non coerenti con il polinomio.",
            "La coppia 5 e 1 usa il coefficiente centrale, ma non annulla il polinomio."
        ],
        "spiegazione": (
            "Il polinomio x² - 5x + 6 si scompone come (x - 2)(x - 3). "
            "Le soluzioni sono quindi 2 e 3. "
            "1 e 6 hanno prodotto 6 ma somma 7, -2 e -3 cambiano i segni, 5 e 1 non rispettano la scomposizione corretta."
        )
    },

    "MAT-AV-0202": {
        "opzioni": [
            "f'(x) = 6x - 4",
            "f'(x) = 3x - 4",
            "f'(x) = 6x + 1",
            "f'(x) = x² - 4"
        ],
        "spiegazione": (
            "La derivata di 3x² è 6x, la derivata di -4x è -4 e la derivata della costante 1 è 0. "
            "Quindi f'(x) = 6x - 4. "
            "3x - 4 dimezza il coefficiente, 6x + 1 mantiene la costante, x² - 4 lascia una potenza non derivata correttamente."
        )
    },

    "MAT-AV-0203": {
        "opzioni": [
            "x² + C",
            "2x² + C",
            "x + C",
            "2 + C"
        ],
        "spiegazione": (
            "Un integrale indefinito di 2x rispetto a x è x² + C, perché la derivata di x² è 2x. "
            "2x² + C avrebbe derivata 4x, x + C avrebbe derivata 1, 2 + C avrebbe derivata 0."
        )
    },

    "MAT-AV-0204": {
        "opzioni": [
            "Tutti i numeri reali tranne x = 2.",
            "Tutti i numeri reali tranne x = 0.",
            "Solo i numeri reali maggiori di 2.",
            "Solo i numeri interi diversi da 2."
        ],
        "spiegazione": (
            "Nella funzione f(x) = 1 / (x - 2), il denominatore non può essere uguale a zero. "
            "Quindi bisogna escludere x = 2, mentre tutti gli altri numeri reali sono ammessi. "
            "Non bisogna escludere x = 0, limitarsi ai valori maggiori di 2 o usare solo numeri interi."
        )
    },

    "MAT-AV-0205": {
        "opzioni": [
            "3",
            "2",
            "10",
            "100"
        ],
        "spiegazione": (
            "Il logaritmo in base 10 di 1000 chiede a quale esponente bisogna elevare 10 per ottenere 1000. "
            "Poiché 10³ = 1000, il valore è 3. "
            "2 darebbe 100, mentre 10 e 100 confondono base o risultato con l'esponente."
        )
    },

    "MAT-AV-0206": {
        "opzioni": [
            "43",
            "47",
            "40",
            "36"
        ],
        "spiegazione": (
            "In una progressione aritmetica si usa la formula a_n = a_1 + (n - 1)d. "
            "Con primo termine 7, differenza 4 e n = 10 si ottiene a_10 = 7 + 9 × 4 = 43. "
            "47 aggiunge dieci differenze invece di nove, 40 dimentica il primo termine, 36 usa solo 9 × 4."
        )
    },

    "MAT-AV-0207": {
        "opzioni": [
            "48",
            "24",
            "32",
            "96"
        ],
        "spiegazione": (
            "In una progressione geometrica si usa la formula a_n = a_1 × r^(n - 1). "
            "Con primo termine 3, ragione 2 e n = 5 si ottiene a_5 = 3 × 2^4 = 48. "
            "24 usa una potenza in meno, 32 ignora il primo termine 3, 96 usa una potenza in più."
        )
    },

    "MAT-AV-0208": {
        "opzioni": [
            "8/3",
            "4",
            "2",
            "16/3"
        ],
        "spiegazione": (
            "Per i valori 2, 4 e 6 la media è 4. "
            "Gli scarti quadratici sono (2 - 4)² = 4, (4 - 4)² = 0 e (6 - 4)² = 4. "
            "La varianza della popolazione è (4 + 0 + 4) / 3 = 8/3. "
            "4 non divide per il numero dei valori, 2 usa gli scarti senza quadrato, 16/3 raddoppia la somma degli scarti quadratici."
        )
    },

    "MAT-AV-0209": {
        "opzioni": [
            "6",
            "3",
            "0",
            "9"
        ],
        "spiegazione": (
            "Si scompone x² - 9 come (x - 3)(x + 3). "
            "Dopo la semplificazione con x - 3 resta x + 3. "
            "Per x che tende a 3, x + 3 vale 6. "
            "3 usa solo il valore verso cui tende x, 0 sostituisce direttamente prima di semplificare, 9 confonde il limite con 3²."
        )
    },

    "MAT-AV-0210": {
        "opzioni": [
            "5",
            "11",
            "8",
            "3"
        ],
        "spiegazione": (
            "Il determinante della matrice 2x2 con righe [2, 3] e [1, 4] si calcola con 2 × 4 - 3 × 1. "
            "Quindi 8 - 3 = 5. "
            "11 somma i prodotti invece di sottrarli, 8 usa solo il primo prodotto, 3 usa solo il secondo prodotto."
        )
    },

    "MAT-AV-0211": {
        "opzioni": [
            "14",
            "10",
            "12",
            "16"
        ],
        "spiegazione": (
            "Il prodotto scalare tra (2, -1, 3) e (4, 0, 2) si calcola moltiplicando le componenti corrispondenti e sommando. "
            "Quindi 2 × 4 + (-1) × 0 + 3 × 2 = 8 + 0 + 6 = 14. "
            "10, 12 e 16 derivano da somme parziali o da errori sul termine con zero."
        )
    },

    "MAT-AV-0212": {
        "opzioni": [
            "25",
            "20",
            "16",
            "30"
        ],
        "spiegazione": (
            "Tra i rettangoli con lo stesso perimetro, l'area massima si ottiene con il quadrato. "
            "Con perimetro 20, il lato del quadrato è 20 / 4 = 5. "
            "L'area massima è quindi 5 × 5 = 25. "
            "20 è il perimetro, 16 è un'area possibile ma non massima, 30 supera il massimo consentito."
        )
    },

    "MAT-AV-0213": {
        "opzioni": [
            "3/8",
            "1/8",
            "1/2",
            "1/4"
        ],
        "spiegazione": (
            "Con 3 prove indipendenti e probabilità di successo 1/2, ogni sequenza specifica ha probabilità (1/2)^3 = 1/8. "
            "Le sequenze con esattamente 2 successi sono 3, quindi la probabilità totale è 3 × 1/8 = 3/8. "
            "1/8 conta una sola sequenza, 1/2 è troppo alto, 1/4 non considera correttamente le 3 combinazioni."
        )
    },

    "MAT-AV-0214": {
        "opzioni": [
            "16",
            "10",
            "9",
            "7"
        ],
        "spiegazione": (
            "Prima si calcola la funzione interna: g(3) = 3 + 1 = 4. "
            "Poi si applica f al risultato: f(4) = 4² = 16. "
            "10 somma passaggi non corretti, 9 calcola f(3), 7 somma 3 e 4 senza applicare il quadrato."
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
        "# Miglioramento Matematica - quarto blocco distrattori forti",
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

    print("===== MIGLIORAMENTO MATEMATICA - QUARTO BLOCCO =====")
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
    print("OK: quarto blocco Matematica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
