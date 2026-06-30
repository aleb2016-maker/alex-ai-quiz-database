from pathlib import Path
import re

p = Path("demo-rag/universal-document-learning-engine.js")
txt = p.read_text(encoding="utf-8", errors="ignore")

errors = []

required = [
    "function verificaGeneratoreRiassuntoRealeLungoV2A17",
    "BLOCCO RIASSUNTO V2A17",
    "verificaGeneratoreRiassuntoRealeLungoV2A17()",
    "riassunto-esteso-reale",
    "Rapporto riassunto",
    "paroleRiassunto",
    "paroleMinime",
    "paroleTarget",
    "paroleMassime",
    "riassunto sospetto da demo",
    "__ultimoRiassuntoRealeV2A17",
    "creaCards(testo)",
    "riconosciTema(testo)",
    "slice(0, 5)",
    "paragrafi.length <= 2",
]

for r in required:
    if r not in txt:
        errors.append(f"Manca blocco anti-demo riassunto: {r}")

m = re.search(
    r"function\s+verificaContrattoLinguisticoUniversaleV2A17\s*\([^)]*\)\s*\{(?P<body>.{0,1200})",
    txt,
    flags=re.S
)

if not m:
    errors.append("Non trovo verificaContrattoLinguisticoUniversaleV2A17")
else:
    body = m.group("body")
    if 'if (azione === "riassunto")' not in body:
        errors.append("Il contratto V2A17 non controlla subito azione riassunto")
    if "verificaGeneratoreRiassuntoRealeLungoV2A17()" not in body:
        errors.append("Il contratto V2A17 non chiama il blocco anti-riassunto demo")
    if "BLOCCO RIASSUNTO V2A17" not in body:
        errors.append("Il blocco riassunto non produce errore esplicito")

if errors:
    print("ERRORE BLOCCO RIASSUNTO V2A17:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK BLOCCO RIASSUNTO V2A17:")
print("- se generaRiassunto è vecchio/corto, il pulsante deve bloccarsi")
print("- il riassunto demo da 5 righe non deve più partire")
print("- il controllo avviene nel contratto V2A17 prima della generazione")
