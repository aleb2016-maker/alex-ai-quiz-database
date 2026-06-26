#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "demo-rag/test-rag-documento-studio-v44.html").read_text(encoding="utf-8")
js = (ROOT / "demo-rag/rag-documento-studio-v44.js").read_text(encoding="utf-8")
css = (ROOT / "demo-rag/rag-documento-studio-v44.css").read_text(encoding="utf-8")
errors = []

def ok(msg): print("OK -", msg)
def err(msg):
    print("ERRORE -", msg)
    errors.append(msg)

for forbidden in ["Carica JSON", "Analizza testo", "Controlla output", "window.print", "btnLoadGenerated", "btnAnalyzeText", "btnQuality"]:
    if forbidden in html + js:
        err(f"testo/funzione vietata presente: {forbidden}")
    else:
        ok(f"assente: {forbidden}")

for required in ["Carica TXT/PDF", "Scarica TXT", "Scarica PDF", "INTERROGA IL DOCUMENTO"]:
    if required in html:
        ok(f"interfaccia contiene {required}")
    else:
        err(f"interfaccia manca {required}")

for required in ["loadFile(file)", "autoAnalyzePastedText", "extractPdfText", "downloadPdf", "downloadText", "answerQuestion"]:
    if required in js:
        ok(f"JS contiene {required}")
    else:
        err(f"JS manca {required}")

if "/demo-rag/pdf-export-browser-v6.js" in html and "AlexBrowserPdfExportV6.exportSectionsToPdf" in js:
    ok("PDF collegato al motore V6")
else:
    err("PDF V6 non collegato")

if "/runtime/web/card-graphic-engine.js" in html:
    ok("card engine runtime caricato")
else:
    err("card engine runtime non caricato")

for bad in ["þ", "ÿ", "\\n"]:
    if bad in html + css:
        err(f"simbolo/testo brutto nel markup: {bad}")

if errors:
    raise SystemExit(1)
print("Verifica UI auto completata.")
