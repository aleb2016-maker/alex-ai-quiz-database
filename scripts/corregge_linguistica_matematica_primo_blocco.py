import json
from pathlib import Path

FILE = Path("data/matematica.json")
REPORT = Path("reports/corregge_linguistica_matematica_primo_blocco.md")

ID_DA_CORREGGERE = "MAT-INT-0007"

NUOVA_SPIEGAZIONE = (
    "Il rapporto tra assenti e presenti è 1 a 5, cioè per ogni assente ci sono 5 presenti. "
    "Se gli assenti sono 4, i presenti sono 4 × 5 = 20. "
    "16, 18 e 24 sono valori vicini, ma non rispettano il rapporto corretto."
)

contenuto = json.loads(FILE.read_text(encoding="utf-8"))

if isinstance(contenuto, list):
    domande = contenuto
else:
    domande = contenuto.get("domande", contenuto.get("questions", []))

corretta = False

for domanda in domande:
    if domanda.get("id") == ID_DA_CORREGGERE:
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
    "# Correzione linguistica Matematica primo blocco\n\n"
    "- Domanda corretta: MAT-INT-0007\n"
    "- Rimossa formulazione `assenti:presenti` che causava errore di spazio dopo punteggiatura.\n"
    "- Nuova formulazione: `rapporto tra assenti e presenti`.\n",
    encoding="utf-8"
)

print("OK: corretta spiegazione linguistica di MAT-INT-0007.")
