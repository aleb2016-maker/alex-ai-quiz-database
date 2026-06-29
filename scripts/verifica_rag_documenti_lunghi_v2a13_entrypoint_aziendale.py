#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

page = ROOT / "demo-rag/rag-app-aziendale.html"
source_page = ROOT / "demo-rag/rag-app-aziendale-v2a12-dashboard.html"
stable_report = ROOT / "reports/rag_documenti_lunghi_v2a6_500_stabile_riepilogo.md"
report = ROOT / "reports/rag_documenti_lunghi_v2a13_entrypoint_aziendale.md"

for path in [page, source_page, stable_report]:
    if not path.exists():
        print(f"ERRORE: file mancante {path.relative_to(ROOT)}")
        sys.exit(1)

text = page.read_text(encoding="utf-8")
source_text = source_page.read_text(encoding="utf-8")
stable_text = stable_report.read_text(encoding="utf-8")
text_lower = text.lower()

required_tokens = [
    "rag-app-aziendale-stabile-v2a13",
    "RAG App Aziendale",
    "Analizza documenti aziendali lunghi fino a 500 pagine",
    "Versione stabile aziendale",
    "Versione stabile basata sul checkpoint 500 pagine",
    "Documenti lunghi",
    "Analisi progressiva",
    "Output aziendali",
    "Local-first",
    "completionBox",
    "scrollIntoView",
    "buildEnterpriseOutputs",
    "businessKeyPoints",
    "businessRisks",
    "businessActions",
    "businessGlossary",
    "rag-large-document-manager-v1.js",
    "rag-large-document-progressive-summary-v2.js?v=app-aziendale-stabile-v2a13",
]

for token in required_tokens:
    if token.lower() not in text_lower:
        print(f"ERRORE: token V2A.13 mancante: {token}")
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
        print(f"ERRORE: token vietato in V2A.13: {token}")
        sys.exit(1)

source_required = [
    "rag-app-aziendale-v2a12-dashboard",
    "RAG App Aziendale V2A.12",
    "Mini-dashboard prodotto",
]

for token in source_required:
    if token not in source_text:
        print(f"ERRORE: pagina V2A.12 alterata, token mancante: {token}")
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
    """# Report RAG documenti lunghi V2A.13 — entrypoint aziendale

- Pagina stabile creata: `demo-rag/rag-app-aziendale.html`
- Base: V2A.12 mini-dashboard prodotto
- Stabilità confermata: V2A.6 fino a 500 pagine
- Scopo:
  - avere una pagina semplice da aprire e presentare
  - evitare di usare direttamente nomi tecnici V2A.7/V2A.8/V2A.12
  - mantenere separata la pagina versione storica V2A.12
- Output NON aggiunti: PDF, card, test, export
- Pagina V2A.12 non alterata
- Esito: OK
""",
    encoding="utf-8",
)

print("OK: verifica entrypoint aziendale V2A.13 superata")
print(f"Report: {report.relative_to(ROOT)}")
