from pathlib import Path
import re

errors = []

vecchio = Path("demo-rag/rag-quality-summary-cards-v34a.js")

if vecchio.exists():
    errors.append("Il file vecchio demo-rag/rag-quality-summary-cards-v34a.js esiste ancora")

html_files = list(Path("demo-rag").glob("*.html"))

for html in html_files:
    txt = html.read_text(encoding="utf-8", errors="ignore")
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>', txt, flags=re.I)

    if "rag-quality-summary-cards-v34a.js" in scripts:
        errors.append(f"{html} carica ancora rag-quality-summary-cards-v34a.js")

    if "rag-quality-summary-cards-v34a.js" in txt:
        errors.append(f"{html} contiene ancora riferimento a rag-quality-summary-cards-v34a.js")

firme_demo = [
    "Riassunto: sicurezza informatica aziendale",
    "Il documento riguarda sicurezza informatica aziendale",
]

# Queste firme non devono comparire nei file caricati dalla pagina universale.
pagina = Path("demo-rag/test-documenti-universale.html")
if pagina.exists():
    txt = pagina.read_text(encoding="utf-8", errors="ignore")
    scripts = re.findall(r'<script[^>]+src=["\']([^"\']+)["\'][^>]*>', txt, flags=re.I)

    for src in scripts:
        path = pagina.parent / src
        if not path.exists():
            continue

        contenuto = path.read_text(encoding="utf-8", errors="ignore")
        trovate = [f for f in firme_demo if f in contenuto]

        if trovate:
            errors.append(f"Script caricato dalla pagina universale contiene demo riassunto: {src}")

if errors:
    print("ERRORE V2A.17 FILE VECCHIO:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.17 FILE VECCHIO:")
print("- rag-quality-summary-cards-v34a.js eliminato")
print("- nessuna pagina demo-rag lo carica")
print("- nessun riferimento al file vecchio resta negli HTML")
print("- la pagina universale non carica script con il vecchio riassunto demo")
