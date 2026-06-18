import json
from pathlib import Path

FILE = Path("data/logica/logica_numerica.json")
BACKUP = Path("data/logica/logica_numerica.backup_prima_primo_blocco_distrattori_forti.json")
REPORT = Path("reports/migliora_logica_primo_blocco_distrattori_forti.md")

PATCH = {
    "LOG-NUM-FAC-0001": {
        "opzioni": [
            "16",
            "15",
            "17",
            "19"
        ],
        "spiegazione": (
            "La sequenza aumenta sempre di 3. "
            "Da 4 si passa a 7, poi a 10, poi a 13. "
            "Il passaggio successivo è 13 + 3 = 16. "
            "15 aggiunge solo 2, 17 aggiunge 4, 19 salta troppo avanti."
        )
    },

    "LOG-NUM-INT-0002": {
        "opzioni": [
            "8",
            "18",
            "9",
            "16"
        ],
        "spiegazione": (
            "La serie alterna due sequenze. "
            "Nelle posizioni dispari compaiono 2, 4, 6, quindi il valore successivo in quella sotto-sequenza è 8. "
            "Nelle posizioni pari compaiono 9, 12, 15: 18 sarebbe il prossimo valore pari, ma non è la posizione richiesta. "
            "9 ripete un valore già visto, 16 segue un raddoppio che qui non c'entra."
        )
    },

    "LOG-NUM-AV-0003": {
        "opzioni": [
            "80",
            "44",
            "72",
            "76"
        ],
        "spiegazione": (
            "La sequenza alterna due operazioni: prima aggiunge 4, poi moltiplica per 2. "
            "Infatti 3 + 4 = 7, 7 × 2 = 14, 14 + 4 = 18, 18 × 2 = 36, 36 + 4 = 40. "
            "Il passo successivo è 40 × 2 = 80. "
            "44 applicherebbe di nuovo +4, 72 usa un raddoppio su 36, 76 è vicino ma non segue la regola."
        )
    },

    "LOG-NUM-AV-0004": {
        "opzioni": [
            "40",
            "42",
            "39",
            "43"
        ],
        "spiegazione": (
            "La sequenza alterna due passaggi: moltiplicare per 2 e aggiungere 1, poi sottrarre 1. "
            "5 × 2 + 1 = 11, poi 11 - 1 = 10. "
            "10 × 2 + 1 = 21, poi 21 - 1 = 20. "
            "20 × 2 + 1 = 41, quindi il passaggio successivo è 41 - 1 = 40. "
            "42, 39 e 43 sono vicini a 41, ma non rispettano il passaggio previsto."
        )
    },

    "LOG-NUM-FAC-0101": {
        "opzioni": [
            "20",
            "16",
            "24",
            "25"
        ],
        "spiegazione": (
            "La macchina produce 4 pezzi ogni minuto. "
            "In 5 minuti produce 4 × 5 = 20 pezzi. "
            "16 sarebbe il risultato per 4 minuti, 24 per 6 minuti, 25 confonde i 5 minuti con una moltiplicazione non coerente."
        )
    },

    "LOG-NUM-INT-0101": {
        "opzioni": [
            "47",
            "46",
            "45",
            "49"
        ],
        "spiegazione": (
            "Si parte da 2 e a ogni passaggio si raddoppia il valore, poi si aggiunge 1. "
            "Primo passaggio: 2 × 2 + 1 = 5. "
            "Secondo passaggio: 5 × 2 + 1 = 11. "
            "Terzo passaggio: 11 × 2 + 1 = 23. "
            "Quarto passaggio: 23 × 2 + 1 = 47. "
            "46 dimentica l'ultimo +1, 45 perde due unità, 49 aggiunge troppo."
        )
    },

    "LOG-NUM-AV-0101": {
        "opzioni": [
            "36",
            "35",
            "49",
            "30"
        ],
        "spiegazione": (
            "La sequenza contiene quadrati perfetti: 1, 4, 9, 16 e 25 corrispondono a 1², 2², 3², 4² e 5². "
            "Il valore successivo è 6² = 36. "
            "35 è vicino ma non è un quadrato perfetto, 49 sarebbe 7², 30 non segue la sequenza dei quadrati."
        )
    },

    "LOG-NUM-FAC-0102": {
        "opzioni": [
            "48",
            "24",
            "36",
            "64"
        ],
        "spiegazione": (
            "Partendo da 3, bisogna raddoppiare quattro volte. "
            "Primo raddoppio: 6. "
            "Secondo raddoppio: 12. "
            "Terzo raddoppio: 24. "
            "Quarto raddoppio: 48. "
            "24 si ferma dopo tre raddoppi, 36 aggiunge 12 invece di raddoppiare, 64 è una potenza di 2 ma non parte da 3."
        )
    },

    "LOG-NUM-INT-0102": {
        "opzioni": [
            "12",
            "13",
            "14",
            "15"
        ],
        "spiegazione": (
            "Le diminuzioni aumentano di 1 ogni volta. "
            "Da 30 a 27 si toglie 3, da 27 a 23 si toglie 4, da 23 a 18 si toglie 5. "
            "Il passaggio successivo richiede di togliere 6: 18 - 6 = 12. "
            "13, 14 e 15 derivano da sottrazioni troppo piccole."
        )
    },

    "LOG-NUM-AV-0102": {
        "opzioni": [
            "42",
            "40",
            "44",
            "48"
        ],
        "spiegazione": (
            "Le differenze tra valori consecutivi sono 4, 6, 8 e 10. "
            "Aumentano sempre di 2, quindi la differenza successiva è 12. "
            "Partendo dall'ultimo valore noto, 30 + 12 = 42. "
            "40 usa una differenza di 10, 44 usa 14, 48 esagera il salto."
        )
    },

    "LOG-NUM-0201": {
        "opzioni": [
            "63",
            "62",
            "64",
            "47"
        ],
        "spiegazione": (
            "Ogni numero si ottiene moltiplicando il precedente per 2 e aggiungendo 1. "
            "3 × 2 + 1 = 7, 7 × 2 + 1 = 15, 15 × 2 + 1 = 31. "
            "Quindi 31 × 2 + 1 = 63. "
            "62 dimentica il +1, 64 aggiunge una unità di troppo, 47 non segue il raddoppio corretto."
        )
    },

    "LOG-NUM-0202": {
        "opzioni": [
            "42",
            "40",
            "44",
            "36"
        ],
        "spiegazione": (
            "Le differenze sono 4, 6, 8 e 10. "
            "La differenza successiva deve aumentare ancora di 2, quindi diventa 12. "
            "Il prossimo numero è 30 + 12 = 42. "
            "40 continua con +10, 44 salta a +14, 36 usa una differenza troppo piccola."
        )
    },

    "LOG-NUM-0203": {
        "opzioni": [
            "1",
            "0",
            "2",
            "6"
        ],
        "spiegazione": (
            "Ogni numero viene diviso per 3. "
            "81 / 3 = 27, 27 / 3 = 9, 9 / 3 = 3. "
            "Il passaggio successivo è 3 / 3 = 1. "
            "0 non deriva da una divisione per 3, 2 dimezza quasi il valore, 6 va nella direzione opposta."
        )
    },

    "LOG-NUM-0204": {
        "opzioni": [
            "37",
            "68",
            "35",
            "41"
        ],
        "spiegazione": (
            "La regola alterna +3 e ×2. "
            "4 + 3 = 7, 7 × 2 = 14, 14 + 3 = 17, 17 × 2 = 34. "
            "Il passaggio successivo è 34 + 3 = 37. "
            "68 applica ×2 nel momento sbagliato, 35 aggiunge solo 1, 41 aggiunge 7."
        )
    },

    "LOG-NUM-0205": {
        "opzioni": [
            "14",
            "12",
            "10",
            "16"
        ],
        "spiegazione": (
            "Dalla corrispondenza data, C vale 6 e D vale 8. "
            "Quindi C più D vale 6 + 8 = 14. "
            "12 userebbe B più D oppure due valori non corretti, 10 può venire da B più C, 16 raddoppia D invece di sommare C e D."
        )
    },

    "LOG-NUM-0206": {
        "opzioni": [
            "95",
            "94",
            "96",
            "89"
        ],
        "spiegazione": (
            "Ogni numero si ottiene moltiplicando il precedente per 2 e aggiungendo 1. "
            "5 × 2 + 1 = 11, 11 × 2 + 1 = 23, 23 × 2 + 1 = 47. "
            "Il valore successivo è 47 × 2 + 1 = 95. "
            "94 dimentica il +1, 96 aggiunge una unità di troppo, 89 non segue la regola."
        )
    },

    "LOG-NUM-0207": {
        "opzioni": [
            "40",
            "44",
            "48",
            "52"
        ],
        "spiegazione": (
            "Le sottrazioni aumentano di 4 ogni volta. "
            "100 - 4 = 96, 96 - 8 = 88, 88 - 12 = 76, 76 - 16 = 60. "
            "La sottrazione successiva è 20, quindi 60 - 20 = 40. "
            "44, 48 e 52 usano sottrazioni troppo piccole."
        )
    },

    "LOG-NUM-0208": {
        "opzioni": [
            "21",
            "20",
            "18",
            "26"
        ],
        "spiegazione": (
            "Ogni termine è la somma dei due precedenti. "
            "2 + 3 = 5, 3 + 5 = 8, 5 + 8 = 13. "
            "Il passaggio successivo è 8 + 13 = 21. "
            "20 è vicino ma perde una unità, 18 somma termini non corretti, 26 raddoppia 13 invece di sommare i due precedenti."
        )
    },

    "LOG-NUM-0209": {
        "opzioni": [
            "72",
            "64",
            "56",
            "80"
        ],
        "spiegazione": (
            "La regola trasforma ogni numero n in n × (n + 1). "
            "Infatti 2 diventa 2 × 3 = 6, 4 diventa 4 × 5 = 20, 6 diventa 6 × 7 = 42. "
            "Quindi 8 diventa 8 × 9 = 72. "
            "64 usa 8 × 8, 56 usa 8 × 7, 80 usa 8 × 10."
        )
    },

    "LOG-NUM-0210": {
        "opzioni": [
            "94",
            "92",
            "88",
            "96"
        ],
        "spiegazione": (
            "Ogni termine si ottiene raddoppiando il precedente e aggiungendo 2. "
            "1 × 2 + 2 = 4, 4 × 2 + 2 = 10, 10 × 2 + 2 = 22, 22 × 2 + 2 = 46. "
            "Il valore successivo è 46 × 2 + 2 = 94. "
            "92 dimentica il +2, 88 usa un raddoppio su un valore sbagliato, 96 aggiunge 4 invece di 2."
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
        raise SystemExit("ERRORE: data/logica/logica_numerica.json non trovato.")

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
            "Ogni risposta errata deve essere numericamente vicina alla corretta, "
            "ma sbagliata per un dettaglio preciso: passo saltato, operazione anticipata, "
            "differenza sbagliata, raddoppio incompleto o sotto-sequenza confusa."
        )

        aggiornate.append(id_domanda)

    salva_json(FILE, contenuto)

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    righe = [
        "# Miglioramento Logica - primo blocco distrattori forti",
        "",
        "File aggiornato: `data/logica/logica_numerica.json`",
        "",
        "Regola applicata: 1 risposta corretta + 3 distrattori forti.",
        "",
        "Metodo: distrattori numericamente vicini, plausibili e sbagliati per un passaggio preciso.",
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

    print("===== MIGLIORAMENTO LOGICA - PRIMO BLOCCO =====")
    print("File: data/logica/logica_numerica.json")
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
    print("OK: primo blocco Logica aggiornato con tre distrattori forti.")


if __name__ == "__main__":
    main()
