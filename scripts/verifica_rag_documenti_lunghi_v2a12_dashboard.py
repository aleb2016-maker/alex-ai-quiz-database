#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

page = ROOT / "demo-rag/rag-app-aziendale-v2a12-dashboard.html"
previous_page = ROOT / "demo-rag/rag-app-aziendale-v2a11-ux-finale.html"
stable_report = ROOT / "reports/rag_documenti_lunghi_v2a6_500_stabile_riepilogo.md"
report = ROOT / "reports/rag_documenti_lunghi_v2a12_dashboard.md"

for path in [page, previous_page, stable_report]:
    if not path.exists():
        print(f"ERRORE: file mancante {path.relative_to(ROOT)}")
        sys.exit(1)

text = page.read_text(encoding="utf-8")
previous_text = previous_page.read_text(encoding="utf-8")
stable_text = stable_report.read_text(encoding="utf-8")
text_lower = text.lower()

required_tokens = [
    "rag-app-aziendale-v2a12-dashboard",
    "RAG App Aziendale V2A.12",
    "Mini-dashboard prodotto",
    "Documenti lunghi",
    "Flusso stabile testato fino a 500 pagine reali",
    "Analisi progressiva",
    "Output aziendali",
    "Local-first",
    "Elaborazione locale/browser, senza API cloud obbligatorie",
    "manuali interni",
    "procedure",
    "policy",
    "formazione",
    "sicurezza",
    "qualità",
    "completionBox",
    "scrollIntoView",
    "buildEnterpriseOutputs",
    "rag-large-document-manager-v1.js",
    "rag-large-document-progressive-summary-v2.js?v=app-aziendale-v2a12",
]

for token in required_tokens:
    if token.lower() not in text_lower:
        print(f"ERRORE: token V2A.12 mancante: {token}")
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
        print(f"ERRORE: token vietato in V2A.12: {token}")
        sys.exit(1)

previous_required = [
    "rag-app-aziendale-v2a11-ux-finale",
    "RAG App Aziendale V2A.11",
    "scrollIntoView",
]

for token in previous_required:
    if token not in previous_text:
        print(f"ERRORE: pagina V2A.11 alterata, token mancante: {token}")
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
    """# Report RAG documenti lunghi V2A.12 — mini-dashboard prodotto

- Pagina creata: `demo-rag/rag-app-aziendale-v2a12-dashboard.html`
- Base: V2A.11 UX finale
- Stabilità confermata: V2A.6 fino a 500 pagine
- Migliorie:
  - mini-dashboard prodotto
  - posizionamento aziendale
  - box su documenti lunghi, analisi progressiva, output aziendali e local-first
  - casi d’uso aziendali esplicitati
- Output NON aggiunti: PDF, card, test, export
- Pagina V2A.11 non alterata
- Esito: OK
""",
    encoding="utf-8",
)

print("OK: verifica mini-dashboard V2A.12 superata")
print(f"Report: {report.relative_to(ROOT)}")
