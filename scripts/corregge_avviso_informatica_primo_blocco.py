import json
from pathlib import Path

FILE = Path("data/informatica.json")
REPORT = Path("reports/corregge_avviso_informatica_primo_blocco.md")

ID_DA_CORREGGERE = "INF-AV-0004"

NUOVE_OPZIONI = [
    "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
    "Perché il frontend può cambiare, ma solo se il backend espone direttamente le tabelle interne",
    "Perché backend e frontend hanno responsabilità distinte, ma devono essere modificati insieme a ogni rilascio",
    "Perché l'interfaccia può usare API, ma la logica applicativa viene spostata interamente nel browser"
]

NUOVA_SPIEGAZIONE = (
    "Separare frontend e backend rende un'applicazione più gestibile perché interfaccia, logica applicativa "
    "e dati possono evolvere con responsabilità più chiare. Non significa esporre tabelle interne, non obbliga "
    "a modificare entrambe le parti a ogni rilascio e non sposta tutta la logica nel browser."
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
        corretta = True
        break

if not corretta:
    raise SystemExit(f"ERRORE: domanda {ID_DA_CORREGGERE} non trovata.")

FILE.write_text(
    json.dumps(contenuto, ensure_ascii=False, indent=2),
    encoding="utf-8"
)

REPORT.write_text(
    "# Correzione avviso Informatica primo blocco\n\n"
    "- Domanda corretta: INF-AV-0004\n"
    "- Rimossa formulazione troppo assoluta con “sempre”.\n",
    encoding="utf-8"
)

print("OK: corretto avviso su INF-AV-0004.")
