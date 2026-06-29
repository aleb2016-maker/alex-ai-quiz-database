from pathlib import Path
import re

errors = []

for html in Path("demo-rag").glob("*.html"):
    txt = html.read_text(encoding="utf-8", errors="ignore")
    if "rag-summary-topic-aware-v2a15.js" in txt:
        errors.append(f"{html}: carica ancora V2A.15")
    if "rag-summary-long-quality-v2a14.js" in txt:
        errors.append(f"{html}: carica ancora V2A.14")

bad_files = [
    Path("demo-rag/rag-summary-topic-aware-v2a15.js"),
    Path("demo-rag/rag-summary-long-quality-v2a14.js"),
]

for p in bad_files:
    if p.exists():
        errors.append(f"{p}: file ancora presente")

engine = Path("demo-rag/universal-document-learning-engine.js")
if not engine.exists():
    errors.append("Manca demo-rag/universal-document-learning-engine.js")
else:
    txt = engine.read_text(encoding="utf-8", errors="ignore")

    forbidden = [
        "classificatore interno",
        "function classifyDocument",
        "classifyDocument(",
        "rag-summary-topic-aware-v2a15",
        "PROFILES = {",
    ]

    for item in forbidden:
        if item in txt:
            errors.append(f"Nel motore universale resta traccia vietata: {item}")

    required = [
        "profiliDocumento",
        "riconosciTema",
        "creaCards",
        "generaRiassunto",
    ]

    for item in required:
        if item not in txt:
            errors.append(f"Nel motore universale manca aggancio base: {item}")

if errors:
    print("ERRORE V2A.16:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.16:")
print("- classificatore interno V2A.15 eliminato")
print("- script isolati V2A.14/V2A.15 non caricati")
print("- il riassunto resta nel motore universale")
print("- presenti profiliDocumento, riconosciTema, creaCards, generaRiassunto")
