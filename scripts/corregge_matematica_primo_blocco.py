import json
from pathlib import Path

FILE = Path("data/matematica.json")
REPORT = Path("reports/corregge_matematica_primo_blocco.md")

ID_DA_CORREGGERE = "MAT-FAC-0007"

NUOVE_OPZIONI = [
    "2/4",
    "2/3",
    "3/4",
    "4/6"
]

NUOVA_SPIEGAZIONE = (
    "La frazione 2/4 è equivalente a 1/2 perché dividendo numeratore e denominatore per 2 si ottiene 1/2. "
    "2/3 e 3/4 sono frazioni maggiori di 1/2, mentre 4/6 si semplifica in 2/3 e quindi non vale 1/2."
)

contenuto = json.loads(FILE.read_text(encoding="utf-8"))

if isinstance(contenuto, list):
    domande = contenuto
else:
    domande = contenuto.get("domande", contenuto.get("questions", []))

corretta = False

for domanda in domande:
    if domanda.get("id") == ID_DA_CORREGGERE:
        domanda["opzioni"] = NUOVE_OPZIONI
        domanda["risposta_corretta"] = NUOVE_OPZIONI[0]
        domanda["spiegazione"] = NUOVA_SPIEGAZIONE
        domanda["regola_distrattori"] = "tre_distrattori_forti"
        domanda["criterio_distrattori"] = (
            "Ogni risposta errata deve essere un errore matematico plausibile: "
            "calcolo vicino, passaggio saltato, formula invertita o interpretazione numerica quasi corretta."
        )
        corretta = True
        break

if not corretta:
    raise SystemExit(f"ERRORE: domanda {ID_DA_CORREGGERE} non trovata.")

FILE.write_text(
    json.dumps(contenuto, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

REPORT.write_text(
    "# Correzione Matematica primo blocco\n\n"
    "- Domanda corretta: MAT-FAC-0007\n"
    "- Rimossa ambiguità: ora una sola opzione è equivalente a 1/2.\n"
    "- Riscritta spiegazione in modo più pulito.\n",
    encoding="utf-8"
)

print("OK: corretta MAT-FAC-0007.")
