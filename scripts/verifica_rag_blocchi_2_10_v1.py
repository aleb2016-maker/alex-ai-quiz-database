from pathlib import Path
import sys

REQUIRED = [
    Path("demo-rag/rag-input-reale-guard.js"),
    Path("demo-rag/rag-text-cleaner-ocr-v1.js"),
    Path("demo-rag/rag-document-input-unico-v1.js"),
    Path("demo-rag/rag-knowledge-extractors-v1.js"),
    Path("demo-rag/rag-didactic-planner-v1.js"),
    Path("demo-rag/rag-knowledge-linked-generator-v1.js"),
    Path("demo-rag/rag-general-validator-v1.js"),
    Path("demo-rag/rag-smart-pipeline-v1.js"),
    Path("demo-rag/test-rag-pipeline-intelligente-v1.html"),
]

FORBIDDEN_CENSOR_LOGIC = [
    "FORBIDDEN_DEMO_PATTERNS",
    "testo vietato",
    "Bloccato testo",
    "findForbiddenPattern",
]

errors = []

for path in REQUIRED:
    if not path.exists():
        errors.append(f"Manca file richiesto: {path}")

for path in REQUIRED:
    if not path.exists() or path.suffix.lower() not in {".js", ".html"}:
        continue
    text = path.read_text(encoding="utf-8", errors="ignore")
    for forbidden in FORBIDDEN_CENSOR_LOGIC:
        if forbidden in text:
            errors.append(f"Logica censoria non ammessa in {path}: {forbidden}")

if errors:
    print("ERRORE VERIFICA BLOCCHI 2-10 V1")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("OK: Blocchi 2-10 V1 presenti.")
print("OK: nessuna logica di testo vietato/censura contenuto.")
print("Pagina test: http://localhost:8000/demo-rag/test-rag-pipeline-intelligente-v1.html")
