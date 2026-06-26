#!/usr/bin/env python3
from pathlib import Path
import sys

ROOT = Path.cwd()
html = ROOT / "demo-rag/test-rag-documento-studio-v44.html"
js = ROOT / "demo-rag/rag-documento-studio-v44-pdf-exact.js"
css = ROOT / "demo-rag/rag-documento-studio-v44-pdf-exact.css"

problemi = []

for path in [html, js, css]:
    if not path.exists():
        problemi.append(f"manca file: {path}")

if html.exists():
    text = html.read_text(encoding="utf-8")
    if "rag-documento-studio-v44-pdf-exact.js" not in text:
        problemi.append("HTML non collega il fix PDF exact")
    if "rag-documento-studio-v44-pdf-exact.css" not in text:
        problemi.append("HTML non collega il fix CSS exact")

if js.exists():
    text = js.read_text(encoding="utf-8")
    if "window.print" in text:
        problemi.append("JS contiene window.print")
    for bad in ["þ", "ÿ"]:
        if bad in text:
            problemi.append(f"simbolo corrotto nel JS: {bad}")
    if "catturaElementoEsatto" not in text:
        problemi.append("manca funzione di cattura esatta")
    if "stopImmediatePropagation" not in text:
        problemi.append("il click PDF vecchio non viene bloccato")
    if "html2canvas" not in text:
        problemi.append("manca cattura html2canvas")

if problemi:
    print("ERRORE verifica PDF exact:")
    for p in problemi:
        print("-", p)
    sys.exit(1)

print("OK verifica PDF exact:")
print("- HTML collegato")
print("- CSS collegato")
print("- niente window.print")
print("- export tramite cattura immagine")
print("- click PDF vecchio bloccato")
