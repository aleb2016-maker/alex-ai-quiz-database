from pathlib import Path
import re

engine = Path("demo-rag/universal-document-learning-engine.js")
txt = engine.read_text(encoding="utf-8", errors="ignore")

errors = []

required = [
    "function leggiTestoSicuroV2A22",
    "leggiTestoSicuroV2A22()",
    "window.__ragVersioneRuntime = \"V2A.22\"",
    "La lettura del testo parte dopo questo messaggio",
]

for r in required:
    if r not in txt:
        errors.append(f"Manca requisito V2A.22: {r}")

for fn in ["generaRiassunto", "generaCardVisive", "generaTest", "generaDomandeStudio"]:
    m = re.search(
        r"function\s+" + re.escape(fn) + r"\s*\([^)]*\)\s*\{(?P<body>.*?)(?=\n\s*function\s+[A-Za-z0-9_$]+\s*\(|\Z)",
        txt,
        flags=re.S,
    )

    if not m:
        errors.append(f"Non trovo funzione {fn}")
        continue

    body = m.group("body")
    pos_settimeout = body.find("setTimeout")
    pos_leggi = body.find("leggiTestoSicuroV2A22()")

    if pos_settimeout == -1:
        errors.append(f"{fn} non usa setTimeout")
    if pos_leggi == -1:
        errors.append(f"{fn} non usa leggiTestoSicuroV2A22")
    if pos_leggi != -1 and pos_settimeout != -1 and pos_leggi < pos_settimeout:
        errors.append(f"{fn} legge il testo prima di setTimeout: può bloccare il click")

    if "const testo = leggiTesto();" in body:
        errors.append(f"{fn} usa ancora leggiTesto() diretto nel click")

if errors:
    print("ERRORE V2A.22 LETTURA TESTO NON BLOCCANTE:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.22 LETTURA TESTO NON BLOCCANTE:")
print("- i 4 generatori mostrano stato prima di leggere il testo")
print("- leggiTesto() non viene più chiamato direttamente nel click")
print("- la lettura testo è differita dopo setTimeout")
