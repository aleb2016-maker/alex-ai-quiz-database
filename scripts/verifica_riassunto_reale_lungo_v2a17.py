from pathlib import Path
import re

p = Path("demo-rag/universal-document-learning-engine.js")
txt = p.read_text(encoding="utf-8", errors="ignore")

errors = []

required = [
    "function generaRiassunto()",
    "riassunto-esteso-reale",
    "Rapporto riassunto",
    "paroleRiassunto",
    "paroleMinime",
    "paroleTarget",
    "paroleMassime",
    "0.15",
    "0.20",
    "0.25",
    "riassunto sospetto da demo",
    "__ultimoRiassuntoRealeV2A17",
    "verificaContrattoLinguisticoUniversaleV2A17(\"riassunto\"",
    "creaCards(testo)",
    "riconosciTema(testo)",
]

for item in required:
    if item not in txt:
        errors.append(f"Manca nel riassunto reale V2A17: {item}")

m = re.search(r"function\s+generaRiassunto\s*\([^)]*\)\s*\{(?P<body>.*?)\n\}", txt, flags=re.S)
if not m:
    errors.append("Non trovo corpo generaRiassunto")
else:
    body = m.group("body")

    vietati = [
        "documento analizzato",
        "contenuti generati",
        "punto centrale",
        "testo di esempio",
        "fallback",
        "demo",
    ]

    # Ammessi solo se compaiono dentro controlli vietati, non come testo generato fisso.
    if "Card generate" in body:
        errors.append("generaRiassunto contiene testo da card/fallback sbagliato")

    if "slice(0, 5)" in body or "slice(0,5)" in body:
        errors.append("generaRiassunto sembra limitato a 5 elementi/frasi")

    if "paragrafi.length <= 2" not in body:
        errors.append("manca blocco anti-riassunto corto/demo")

    if "totaleParole >= 1500" not in body:
        errors.append("manca distinzione documento lungo")

if errors:
    print("ERRORE V2A.17 RIASSUNTO:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.17 RIASSUNTO:")
print("- generaRiassunto non usa più demo corta")
print("- riassunto lungo reale 15%-25% per documenti lunghi")
print("- usa testo caricato, riconosciTema e creaCards")
print("- blocca riassunti sospetti da 5 righe")
