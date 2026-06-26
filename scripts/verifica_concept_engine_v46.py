
from pathlib import Path
import subprocess

html = Path("demo-rag/test-documenti-universale.html").read_text(encoding="utf-8", errors="replace")
js_path = Path("demo-rag/rag-concept-document-engine-v46.js")
js = js_path.read_text(encoding="utf-8", errors="replace")

old_scripts = [
    "universal-document-learning-engine.js",
    "sport-training-document-engine.js",
    "browser-rag-engine.js",
    "pdf-export-cards.js",
    "export-card-pdf-playground.js",
    "scarica-pdf-solo-card-playground.js",
]

for old in old_scripts:
    if old in html:
        raise SystemExit(f"ERRORE: HTML carica ancora vecchio script: {old}")

if html.count("rag-concept-document-engine-v46.js") != 1:
    raise SystemExit("ERRORE: concept engine non collegato una sola volta")

bad_phrases = [
    "Nel blocco",
    "quale interpretazione",
    "Scopo del documento"
]

for bad in bad_phrases:
    if bad in js:
        raise SystemExit(f"ERRORE: frase vecchia nel nuovo JS: {bad}")

good_phrases = [
    "E-mail sospette",
    "Password manager",
    "Aggiornamenti controllati",
    "Sicurezza informatica aziendale"
]

for good in good_phrases:
    if good not in js:
        raise SystemExit(f"ERRORE: concetto atteso mancante: {good}")

r = subprocess.run(["node", "--check", str(js_path)], text=True, capture_output=True)
if r.returncode != 0:
    print(r.stdout)
    print(r.stderr)
    raise SystemExit("ERRORE: sintassi JS non valida")

print("OK: concept engine collegato e vecchi motori rimossi")
