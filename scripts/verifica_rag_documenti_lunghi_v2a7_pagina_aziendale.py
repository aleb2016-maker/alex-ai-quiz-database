#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

page = ROOT / "demo-rag/rag-app-aziendale-v2a7.html"
original_v2 = ROOT / "demo-rag/test-rag-documenti-lunghi-v2.html"
stable_script = ROOT / "scripts/verifica_rag_documenti_lunghi_v2a6_500_pagine_stabile.py"
stable_report = ROOT / "reports/rag_documenti_lunghi_v2a6_500_stabile_riepilogo.md"
report = ROOT / "reports/rag_documenti_lunghi_v2a7_pagina_aziendale.md"

required_files = [page, original_v2, stable_script, stable_report]

for path in required_files:
    if not path.exists():
        print(f"ERRORE: file mancante {path.relative_to(ROOT)}")
        sys.exit(1)

text = page.read_text(encoding="utf-8")
original_text = original_v2.read_text(encoding="utf-8")
stable_text = stable_report.read_text(encoding="utf-8")

required_tokens = [
    "rag-app-aziendale-v2a7",
    "RAG App Aziendale V2A.7",
    "Pagina ponte aziendale",
    "File PDF/TXT/MD",
    "Analizza documento aziendale",
    "rag-large-document-manager-v1.js",
    "rag-large-document-progressive-summary-v2.js?v=app-aziendale-v2a7",
    "maxCharsPerChunk",
    "chunkOverlap",
    "maxPagesPerBatch",
    "maxChunksPerBatch",
    "maxCharsPerBatch",
    "Riassunto finale aziendale",
    "Riassunti parziali per batch",
    "Profilo",
    "Debug JSON analisi aziendale",
]

for token in required_tokens:
    if token not in text:
        print(f"ERRORE: token V2A.7 mancante: {token}")
        sys.exit(1)

forbidden_tokens = [
    "pdf-export-browser-v6.js",
    "btnScaricaPdf",
    "btnScaricaTxt",
    "btnScaricaHtml",
    "btnScaricaJson",
    "rag-graphic-intelligence",
    "rag-demo-graphic-bridge",
    "demo/index.html",
]

for token in forbidden_tokens:
    if token in text:
        print(f"ERRORE: token vietato nella pagina ponte V2A.7: {token}")
        sys.exit(1)

original_required = [
    "test-rag-documenti-lunghi-v2",
    "RAG documenti lunghi V2",
    "Analizza e genera riassunto progressivo",
]

for token in original_required:
    if token not in original_text:
        print(f"ERRORE: pagina V2A originale sembra alterata, token mancante: {token}")
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
        print(f"ERRORE: report V2A.6 500 pagine non conferma stabilità, token mancante: {token}")
        sys.exit(1)

report.write_text(
    """# Report RAG documenti lunghi V2A.7 — pagina ponte aziendale

- Pagina creata: `demo-rag/rag-app-aziendale-v2a7.html`
- Motore usato: manager V1 + progressive summary V2
- Base stabile confermata: V2A.6 fino a 500 pagine
- Output abilitati: statistiche, profilo, keyword, riassunto finale, riassunti parziali, debug JSON
- Output NON abilitati: card, test, domande, PDF, export
- Pagina V2A originale non alterata
- Esito: OK

## Note

Questa pagina è un ponte aziendale: serve a rendere utilizzabile il motore stabile dei documenti lunghi
prima di collegare output avanzati, export e PDF.
""",
    encoding="utf-8",
)

print("OK: verifica pagina ponte aziendale V2A.7 superata")
print(f"Report: {report.relative_to(ROOT)}")
