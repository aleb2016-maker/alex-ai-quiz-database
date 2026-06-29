#!/usr/bin/env python3
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]

MANAGER = ROOT / "runtime" / "web" / "rag-large-document-manager-v1.js"
TEST_PAGE = ROOT / "demo-rag" / "test-rag-documenti-lunghi-v1.html"
GENERATOR = ROOT / "scripts" / "crea_documento_lungo_test_rag_v1.py"
LONG_TEST = ROOT / "scripts" / "test_rag_documento_lungo_generato_v1.py"
REPORT = ROOT / "reports" / "rag_documenti_lunghi_v1.md"

REQUIRED_FUNCTIONS = [
    "parsePageSelection",
    "splitTxtMdIntoLogicalPages",
    "splitTextToChunks",
    "createPageChunks",
    "createBatches",
    "analyzeFile",
    "estimateCapacity",
]

FORBIDDEN_LINKS = [
    "test-documenti-universale.html",
    "universal-document-learning-engine.js",
    "pdf-export-browser-v6.js",
    "rag-quality-summary-cards-v34a.js",
    "btnScaricaPdf",
    "btnScaricaTxt",
    "btnScaricaHtml",
    "btnScaricaJson",
]

REQUIRED_HTML = [
    "fileInputLarge",
    "pageSelection",
    "progress",
    "maxCharsPerBatch",
    "Analizza documento lungo",
    "rag-large-document-manager-v1.js",
    "__RAG_LARGE_DOCUMENT_LAST_REPORT__",
]


def fail(message: str) -> None:
    print(f"ERRORE: {message}")
    sys.exit(1)


def read(path: Path) -> str:
    if not path.exists():
        fail(f"file mancante: {path.relative_to(ROOT)}")
    return path.read_text(encoding="utf-8")


def main() -> None:
    manager_text = read(MANAGER)
    page_text = read(TEST_PAGE)
    read(GENERATOR)
    read(LONG_TEST)
    read(REPORT)

    for name in REQUIRED_FUNCTIONS:
        pattern = r"\bfunction\s+" + re.escape(name) + r"\b|^\s*" + re.escape(name) + r"\s*:"
        if not re.search(pattern, manager_text, flags=re.MULTILINE):
            fail(f"funzione manager mancante: {name}")

    for token in REQUIRED_HTML:
        if token not in page_text:
            fail(f"token pagina test mancante: {token}")

    combined = "\n".join([manager_text, page_text])
    for forbidden in FORBIDDEN_LINKS:
        if forbidden in combined:
            fail(f"collegamento o riferimento vietato trovato nei file V1: {forbidden}")

    if re.search(r"<script[^>]+src=[\"'][^\"']*(pdf-export|universal-document|rag-quality-summary)", page_text, re.I):
        fail("script vietato collegato nella pagina test")

    print("OK: verifica RAG documenti lunghi V1 superata")
    print("OK: manager, pagina test, generator, validatori e report presenti")
    print("OK: nessun collegamento alla demo ufficiale o agli export vietati")


if __name__ == "__main__":
    main()
