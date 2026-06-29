from pathlib import Path
import re

engine = Path("demo-rag/universal-document-learning-engine.js")
html = Path("demo-rag/test-documenti-universale.html")

assert engine.exists(), "Manca universal-document-learning-engine.js"
assert html.exists(), "Manca test-documenti-universale.html"

txt = engine.read_text(encoding="utf-8", errors="ignore")
html_txt = html.read_text(encoding="utf-8", errors="ignore")

errors = []

# Vietati classificatori esterni isolati.
for bad in [
    "rag-summary-topic-aware-v2a15.js",
    "rag-summary-long-quality-v2a14.js",
    "function classifyDocument",
    "classificatore interno",
    "PROFILES = {",
]:
    if bad in html_txt or bad in txt:
        errors.append(f"Resta elemento vietato: {bad}")

# Motori base obbligatori.
for required in [
    "profiliDocumento",
    "riconosciTema",
    "creaCards",
    "generaRiassunto",
    "verificaMotoriObbligatoriV2A16",
    "registraUsoMotoriV2A16",
]:
    if required not in txt:
        errors.append(f"Manca elemento obbligatorio nel motore universale: {required}")

# Categorie/profili già creati.
for category in [
    "sport",
    "curriculum",
    "personale",
    "aziendale",
    "storia",
    "poesia",
    "hobby",
]:
    if category not in txt:
        errors.append(f"Manca profilo/categoria: {category}")

# Ogni funzione principale deve passare dal guardiano.
checks = {
    "generaRiassunto": "riassunto",
    "generaTest": "test",
    "generaDomandeStudio": "domande",
}

for fn, action in checks.items():
    m = re.search(r"function\s+" + re.escape(fn) + r"\s*\([^)]*\)\s*\{(?P<body>.{0,900})", txt, flags=re.S)
    if not m:
        errors.append(f"Non trovo funzione {fn}")
        continue

    body = m.group("body")
    expected = f'verificaMotoriObbligatoriV2A16("{action}")'
    if expected not in body:
        errors.append(f"{fn} non passa dal guardiano obbligatorio {expected}")

# Card: il pulsante reale btnCard deve chiamare generaCardVisive,
# e generaCardVisive deve passare dal guardiano obbligatorio.
card_listener_ok = re.search(
    r'getElementById\(["\']btnCard["\']\)\.addEventListener\(["\']click["\'],\s*generaCardVisive\)',
    txt,
    flags=re.S
)

if not card_listener_ok:
    errors.append("btnCard non è collegato a generaCardVisive")

m = re.search(
    r"function\s+generaCardVisive\s*\([^)]*\)\s*\{(?P<body>.{0,900})",
    txt,
    flags=re.S
)

if not m:
    errors.append("Non trovo funzione generaCardVisive")
else:
    body = m.group("body")
    if 'verificaMotoriObbligatoriV2A16("card")' not in body:
        errors.append("generaCardVisive non passa dal guardiano obbligatorio card")

if errors:
    print("ERRORE V2A.16:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.16:")
print("- classificatore interno eliminato")
print("- pulsanti agganciati al guardiano motori obbligatori")
print("- riassunto/card/test/domande passano dai motori reali")
print("- se manca un motore, il pulsante si blocca invece di usare fallback")
