from pathlib import Path
import sys

REQUIRED = {
    "demo-rag/rag-knowledge-extractors-v1.js": [
        "rag-knowledge-extractors-v2-quality",
        "isNoiseSentence",
        "questionHint",
        "answerText",
    ],
    "demo-rag/rag-knowledge-linked-generator-v1.js": [
        "rag-knowledge-linked-generator-v2-quality",
        "questionForFact",
        "makeDistractors",
        "badUserText",
    ],
    "demo-rag/rag-general-validator-v1.js": [
        "rag-general-validator-v2-quality",
        "containsRawTechnicalText",
        "opzione_troppo_lunga",
        "domanda_test_debole",
    ],
}

FORBIDDEN_CENSORSHIP = [
    "testo vietato",
    "contenuto vietato",
    "FORBIDDEN_DEMO_PATTERNS",
    "findForbiddenPattern",
    "Bloccato testo demo",
]

FORBIDDEN_BAD_OUTPUT_PATTERNS = [
    "Secondo il documento, che cosa afferma #",
    "problema_soluzione →",
    "richiede →",
]

errors = []

for relative, markers in REQUIRED.items():
    path = Path(relative)
    if not path.exists():
        errors.append(f"Manca {relative}")
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for marker in markers:
        if marker not in text:
            errors.append(f"{relative}: manca marker {marker}")
    for forbidden in FORBIDDEN_CENSORSHIP:
        if forbidden in text:
            errors.append(f"{relative}: contiene ancora censura contenuto errata: {forbidden}")

for relative in ["demo-rag/rag-knowledge-linked-generator-v1.js"]:
    path = Path(relative)
    if not path.exists():
        continue
    text = path.read_text(encoding="utf-8", errors="replace")
    for forbidden in FORBIDDEN_BAD_OUTPUT_PATTERNS:
        if forbidden in text:
            errors.append(f"{relative}: contiene testo output sporco: {forbidden}")

if errors:
    print("ERRORE: verifica qualità V2 fallita")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("OK: Qualità RAG V2 installata.")
print("OK: nessuna censura contenuto.")
print("OK: generatori ripuliti per domande, relazioni e distrattori.")
print("Pagina test: http://localhost:8000/demo-rag/test-rag-pipeline-intelligente-v1.html")
