#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

page = ROOT / "demo-rag/rag-app-aziendale-v2a8-ux.html"
previous_page = ROOT / "demo-rag/rag-app-aziendale-v2a7.html"
stable_report = ROOT / "reports/rag_documenti_lunghi_v2a6_500_stabile_riepilogo.md"
report = ROOT / "reports/rag_documenti_lunghi_v2a8_ux_aziendale.md"

for path in [page, previous_page, stable_report]:
    if not path.exists():
        print(f"ERRORE: file mancante {path.relative_to(ROOT)}")
        sys.exit(1)

text = page.read_text(encoding="utf-8")
previous_text = previous_page.read_text(encoding="utf-8")
stable_text = stable_report.read_text(encoding="utf-8")

required_tokens = [
    "rag-app-aziendale-v2a8-ux",
    "RAG App Aziendale V2A.8",
    "Pagina UX aziendale",
    "Limite consigliato attuale: fino a 500 pagine",
    "Motore",
    "RAG documenti lunghi stabile",
    "Elaborazione",
    "Locale/browser, senza API cloud obbligatorie",
    "Output attivi",
    "Riassunto, keyword, profilo, parziali",
    "Output futuri",
    "PDF, card, test, export aziendale",
    "Controllo qualità analisi",
    "Analisi completata con controlli base",
    "rag-large-document-manager-v1.js",
    "rag-large-document-progressive-summary-v2.js?v=app-aziendale-v2a8",
]

for token in required_tokens:
    if token not in text:
        print(f"ERRORE: token V2A.8 mancante: {token}")
        sys.exit(1)

forbidden_tokens = [
    "pdf-export-browser-v6.js",
    "btnScaricaPdf",
    "btnScaricaTxt",
    "btnScaricaHtml",
    "btnScaricaJson",
    "rag-graphic-intelligence",
    "rag-demo-graphic-bridge",
]

for token in forbidden_tokens:
    if token in text:
        print(f"ERRORE: token vietato in V2A.8: {token}")
        sys.exit(1)

previous_required = [
    "rag-app-aziendale-v2a7",
    "RAG App Aziendale V2A.7",
    "Pagina ponte aziendale",
]

for token in previous_required:
    if token not in previous_text:
        print(f"ERRORE: pagina V2A.7 alterata, token mancante: {token}")
        sys.exit(1)

stable_required = [
    "400 pagine: OK",
    "500 pagine: OK",
    "1000 chunk",
    "125 batch",
    "125 parziali",
]

for token in stable_required:
    if token not in stable_text:
        print(f"ERRORE: stabilità 500 pagine non confermata, token mancante: {token}")
        sys.exit(1)

report.write_text(
    """# Report RAG documenti lunghi V2A.8 — UX aziendale

- Pagina creata: `demo-rag/rag-app-aziendale-v2a8-ux.html`
- Base: V2A.7 pagina ponte aziendale
- Stabilità confermata: V2A.6 fino a 500 pagine
- Migliorie aggiunte:
  - limite consigliato 500 pagine
  - blocco stato sistema
  - chiarimento elaborazione locale/browser
  - output attivi e output futuri separati
  - controllo qualità analisi
  - messaggi utente più chiari
- Output NON aggiunti: PDF, card, test, export
- Pagina V2A.7 non alterata
- Esito: OK
""",
    encoding="utf-8",
)

print("OK: verifica UX aziendale V2A.8 superata")
print(f"Report: {report.relative_to(ROOT)}")
