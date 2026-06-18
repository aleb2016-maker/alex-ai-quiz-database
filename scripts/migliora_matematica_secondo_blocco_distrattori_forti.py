import json
from pathlib import Path

FILE = Path("data/matematica.json")
BACKUP = Path("data/matematica.backup_prima_secondo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_matematica_secondo_blocco_distrattori_forti.md")

PATCH = {
    "MAT-FAC-0101": {
        "opzioni": [
            "63",
            "53",
            "61",
            "73"
        ],
        "spiegazione": (
            "Per calcolare 45 + 18 sommiamo le unità: 5 + 8 = 13, quindi scriviamo 3 e riportiamo 1. "
            "Poi sommiamo le decine: 4 + 1 + 1 di riporto = 6. Il risultato è 63. "
            "53 dimentica una decina, 61 sbaglia il riporto, 73 aggiunge una decina di troppo."
        )
    },

    "MAT-INT-0101": {
        "opzioni": [
            "10%",
            "20%",
            "15%",
            "5%"
        ],
        "spiegazione": (
            "La diminuzione è 200 - 180 = 20 euro. "
            "La percentuale di diminuzione si calcola rispetto al valore iniziale: 20 / 200 × 100 = 10%. "
            "20% confonde la diminuzione in euro con la percentuale, mentre 15% e 5% sono percentuali vicine ma non corrette."
        )
    },

    "MAT-AV-0101": {
        "opzioni": [
            "7 cm",
            "6 cm",
            "8 cm",
            "17 cm"
        ],
        "spiegazione": (
            "Il perimetro del rettangolo è 2 × (base + altezza). "
            "Quindi 34 = 2 × (10 + altezza). Dividendo per 2 si ottiene 17 = 10 + altezza. "
            "L'altezza è 17 - 10 = 7 cm. 17 cm è il semiperimetro, non l'altezza."
        )
    },

    "MAT-FAC-0102": {
        "opzioni": [
            "44",
            "46",
            "54",
            "40"
        ],
        "spiegazione": (
            "Per calcolare 72 - 28 possiamo fare 72 - 30 = 42 e poi aggiungere 2, perché abbiamo tolto 2 in più. "
            "Quindi 42 + 2 = 44. "
            "46 e 40 derivano da aggiustamenti sbagliati, mentre 54 nasce da una sottrazione incompleta."
        )
    },

    "MAT-INT-0102": {
        "opzioni": [
            "49 m²",
            "42 m²",
            "56 m²",
            "35 m²"
        ],
        "spiegazione": (
            "Prima si calcola la copertura di 1 litro: 28 / 4 = 7 m². "
            "Con 7 litri si coprono 7 × 7 = 49 m². "
            "42 e 56 usano quantità vicine di litri, mentre 35 corrisponde a 5 litri allo stesso rendimento."
        )
    },

    "MAT-AV-0102": {
        "opzioni": [
            "22",
            "21",
            "23",
            "26"
        ],
        "spiegazione": (
            "Se il numero maggiore è A e il minore è B, allora A + B = 35 e A - B = 9. "
            "Sommando le due equazioni si ottiene 2A = 44, quindi A = 22. "
            "21 e 23 sono vicini al risultato, mentre 26 nasce da un uso scorretto della differenza."
        )
    },

    "MAT-FAC-0103": {
        "opzioni": [
            "72",
            "62",
            "68",
            "78"
        ],
        "spiegazione": (
            "12 × 6 si può calcolare come 10 × 6 + 2 × 6. "
            "Quindi 60 + 12 = 72. "
            "62 usa solo una parte del calcolo, 68 e 78 sono risultati vicini ma non rispettano la moltiplicazione."
        )
    },

    "MAT-INT-0103": {
        "opzioni": [
            "5 mesi",
            "4 mesi",
            "6 mesi",
            "7 mesi"
        ],
        "spiegazione": (
            "Prima si toglie il costo fisso di attivazione: 31 - 6 = 25 euro. "
            "Ogni mese costa 5 euro, quindi 25 / 5 = 5 mesi. "
            "4, 6 e 7 mesi sono vicini, ma non separano correttamente il costo fisso dal costo mensile."
        )
    },

    "MAT-AV-0103": {
        "opzioni": [
            "2 ore",
            "1,5 ore",
            "2,5 ore",
            "3 ore"
        ],
        "spiegazione": (
            "Il tempo si calcola facendo distanza / velocità. "
            "Quindi 150 / 75 = 2 ore. "
            "1,5 ore, 2,5 ore e 3 ore sono tempi plausibili, ma non derivano dalla divisione corretta tra distanza e velocità."
        )
    },

    "MAT-FAC-0104": {
        "opzioni": [
            "7",
            "6",
            "8",
            "9"
        ],
        "spiegazione": (
            "Dividere 56 caramelle in 8 sacchetti uguali significa calcolare 56 / 8. "
            "Poiché 8 × 7 = 56, ogni sacchetto contiene 7 caramelle. "
            "6, 8 e 9 sono valori vicini, ma non moltiplicati per 8 danno 56."
        )
    },

    "MAT-INT-0104": {
        "opzioni": [
            "16",
            "15",
            "17",
            "18"
        ],
        "spiegazione": (
            "La media si calcola sommando i valori e dividendo per quanti sono. "
            "12 + 15 + 18 + 19 = 64. Dividendo per 4 numeri si ottiene 64 / 4 = 16. "
            "15, 17 e 18 sono vicini, ma non sono la media corretta."
        )
    },

    "MAT-AV-0104": {
        "opzioni": [
            "20",
            "10",
            "25",
            "15"
        ],
        "spiegazione": (
            "Per scegliere il presidente ci sono 5 possibilità. "
            "Dopo aver scelto il presidente restano 4 possibilità per il vice. "
            "Poiché i ruoli sono diversi, il totale è 5 × 4 = 20. "
            "10 conta le coppie senza distinguere i ruoli, 25 permette ripetizioni, 15 sottrae scelte in modo errato."
        )
    },

    "MAT-FAC-0105": {
        "opzioni": [
            "15",
            "10",
            "20",
            "25"
        ],
        "spiegazione": (
            "0,5 significa metà. "
            "Calcolare 0,5 di 30 significa trovare la metà di 30: 30 / 2 = 15. "
            "10, 20 e 25 sono parti di 30, ma non rappresentano la metà."
        )
    },

    "MAT-INT-0105": {
        "opzioni": [
            "3/5",
            "4/7",
            "Sono uguali",
            "Non si possono confrontare senza trasformarle"
        ],
        "spiegazione": (
            "Per confrontare 3/5 e 4/7 si può usare il prodotto incrociato: 3 × 7 = 21 e 4 × 5 = 20. "
            "Poiché 21 è maggiore di 20, 3/5 è maggiore di 4/7. "
            "Le frazioni si possono confrontare, e non sono uguali."
        )
    },

    "MAT-AV-0105": {
        "opzioni": [
            "120",
            "116",
            "100",
            "128"
        ],
        "spiegazione": (
            "Se un valore diminuisce del 20%, resta l'80% del valore iniziale. "
            "Quindi 0,8x = 96. Dividendo 96 per 0,8 si ottiene x = 120. "
            "100 sottrae 20 da 120 senza impostare l'equazione, mentre 116 e 128 sono valori vicini ma non corretti."
        )
    },

    "MAT-FAC-0106": {
        "opzioni": [
            "30 cm²",
            "60 cm²",
            "16 cm²",
            "40 cm²"
        ],
        "spiegazione": (
            "L'area del triangolo si calcola con base × altezza / 2. "
            "Quindi 10 × 6 = 60, poi 60 / 2 = 30 cm². "
            "60 cm² dimentica la divisione per 2, 16 cm² somma base e altezza, 40 cm² nasce da un calcolo parziale."
        )
    },

    "MAT-INT-0106": {
        "opzioni": [
            "31,4 cm",
            "15,7 cm",
            "78,5 cm",
            "25 cm"
        ],
        "spiegazione": (
            "La circonferenza si calcola con 2 × π × r. "
            "Usando π circa 3,14 e raggio 5 cm si ottiene 2 × 3,14 × 5 = 31,4 cm. "
            "15,7 cm usa solo π × r, 78,5 cm è il valore numerico dell'area, 25 cm non usa la formula corretta."
        )
    },

    "MAT-AV-0106": {
        "opzioni": [
            "10 litri",
            "15 litri",
            "12 litri",
            "8 litri"
        ],
        "spiegazione": (
            "Il rapporto tra succo e acqua è 2 a 3, quindi le parti totali sono 5. "
            "Se 5 parti valgono 25 litri, una parte vale 25 / 5 = 5 litri. "
            "Il succo corrisponde a 2 parti, quindi 2 × 5 = 10 litri."
        )
    },

    "MAT-INT-0107": {
        "opzioni": [
            "3/10",
            "3/8",
            "5/10",
            "2/10"
        ],
        "spiegazione": (
            "Le penne totali sono 5 + 3 + 2 = 10. "
            "Le penne blu sono 3. "
            "La probabilità è casi favorevoli diviso casi totali, quindi 3/10. "
            "3/8 esclude una parte delle penne, 5/10 riguarda le nere, 2/10 riguarda le rosse."
        )
    },

    "MAT-AV-0107": {
        "opzioni": [
            "17",
            "13",
            "25",
            "18"
        ],
        "spiegazione": (
            "2³ significa 2 × 2 × 2 = 8. "
            "3² significa 3 × 3 = 9. "
            "Sommando 8 + 9 si ottiene 17. "
            "13 deriva da una potenza calcolata male, 25 moltiplica o combina i termini in modo scorretto, 18 è vicino ma non corretto."
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
        "# Miglioramento Matematica - secondo blocco distrattori forti",
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

    print("===== MIGLIORAMENTO MATEMATICA - SECONDO BLOCCO =====")
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
    print("OK: secondo blocco Matematica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
