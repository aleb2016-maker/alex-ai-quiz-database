from pathlib import Path

engine = Path("demo-rag/universal-document-learning-engine.js")
txt = engine.read_text(encoding="utf-8", errors="ignore")

errors = []

required = [
    "function attivaBindingForzatoPulsantiV2A21",
    "window.addEventListener(\"click\", intercettaClick, true)",
    "document.addEventListener(\"click\", intercettaClick, true)",
    "evento.stopImmediatePropagation()",
    "eseguiAzioneForzataPulsanteV2A21",
    "generaRiassunto()",
    "generaCardVisive()",
    "generaTest()",
    "generaDomandeStudio()",
    "disattivaOnclickVecchiPulsantiV2A21",
    "data-rag-v2a21",
]

for r in required:
    if r not in txt:
        errors.append(f"Manca requisito V2A.21: {r}")

if errors:
    print("ERRORE V2A.21 BINDING FORZATO:")
    for e in errors:
        print("-", e)
    raise SystemExit(1)

print("OK V2A.21 BINDING FORZATO:")
print("- i click dei 4 pulsanti vengono intercettati in capture")
print("- i vecchi listener vengono bloccati con stopImmediatePropagation")
print("- onclick vecchi rimossi")
print("- i pulsanti vengono forzati sui generatori V2A.20")
