from pathlib import Path
import re

engine = Path("demo-rag/universal-document-learning-engine.js")
txt = engine.read_text(encoding="utf-8", errors="ignore")

errors = []

required = [
    "function generaRiassunto()",
    "function generaCardVisive()",
    "function generaTest()",
    "function generaDomandeStudio()",
    "generaRiassuntoLungoNonBloccanteV2A20",
    "mostraStatoGeneratoreV2A20",
    "mostraStatoRiassuntoV2A20",
    "setTimeout",
    "window.mostraOutputMotoriBrowserV2A19",
    "eseguiMotoriIntelligentiUniversaliV35V2A18",
    "verificaMotoriObbligatoriV2A16",
    "verificaContrattoLinguisticoUniversaleV2A17",
]

for r in required:
    if r not in txt:
        errors.append(f"Manca requisito V2A20: {r}")

checks = {
    "generaRiassunto": [
        "generaRiassuntoLungoNonBloccanteV2A20",
        "mostraStatoRiassuntoV2A20",
        "setTimeout",
        'verificaMotoriObbligatoriV2A16("riassunto")',
        'verificaContrattoLinguisticoUniversaleV2A17("riassunto"',
    ],
    "generaCardVisive": [
        "mostraStatoGeneratoreV2A20",
        "setTimeout",
        'verificaMotoriObbligatoriV2A16("card")',
        'eseguiMotoriIntelligentiUniversaliV35V2A18("card"',
        'verificaContrattoLinguisticoUniversaleV2A17("card"',
        'window.mostraOutputMotoriBrowserV2A19("card"',
    ],
    "generaTest": [
        "mostraStatoGeneratoreV2A20",
        "setTimeout",
        'verificaMotoriObbligatoriV2A16("test")',
        'eseguiMotoriIntelligentiUniversaliV35V2A18("test"',
        'verificaContrattoLinguisticoUniversaleV2A17("test"',
        'window.mostraOutputMotoriBrowserV2A19("test"',
    ],
    "generaDomandeStudio": [
        "mostraStatoGeneratoreV2A20",
        "setTimeout",
        'verificaMotoriObbligatoriV2A16("domande")',
        'eseguiMotoriIntelligentiUniversaliV35V2A18("domande"',
        'verificaContrattoLinguisticoUniversaleV2A17("domande"',
        'window.mostraOutputMotoriBrowserV2A19("domande"',
    ],
}

for fn, markers in checks.items():
    m = re.search(
        r"function\s+" + re.escape(fn) + r"\s*\([^)]*\)\s*\{(?P<body>.*?)(?=\n\s*function\s+[A-Za-z0-9_$]+\s*\(|\Z)",
        txt,
        flags=re.S,
    )

    if not m:
        errors.append(f"Non trovo funzione {fn}")
        continue

    body = m.group("body")

    for marker in markers:
        if marker not in body:
            errors.append(f"{fn} non contiene marker non bloccante/obbligatorio: {marker}")

if errors:
    print("ERRORE V2A.20 GENERATORI NON BLOCCANTI:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.20 GENERATORI NON BLOCCANTI:")
print("- riassunto non bloccante")
print("- card non bloccante con V2A16/V2A17/V2A18/V2A19 espliciti")
print("- test non bloccante con V2A16/V2A17/V2A18/V2A19 espliciti")
print("- domande studio non bloccante con V2A16/V2A17/V2A18/V2A19 espliciti")
print("- tutti i generatori mostrano stato o errore visibile")
