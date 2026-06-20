#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = [
    "demo-rag/index.html",
    "demo-rag/style.css",
    "demo-rag/app.js",
    "runtime/web/theme-engine.css",
    "runtime/web/theme-engine.js",
    "config/temi_grafici_formazione.json",
    "scripts/applica_tema_formazione.py",
    "scripts/validatore_rag_distrattori_forti_v2.py",
    "docs/RAG_INSERIMENTO_DOCUMENTI.md",
    "docs/MOTORE_GRAFICO_RIUTILIZZABILE.md",
]

ok = True

for rel in REQUIRED:
    path = ROOT / rel
    if path.exists():
        print(f"✅ {rel}")
    else:
        ok = False
        print(f"❌ manca {rel}")

readme = ROOT / "README.md"

if readme.exists():
    text = readme.read_text(encoding="utf-8").lower()
    markers = [
        "motore rag documenti",
        "pipeline materiale formativo",
        "motore grafico riutilizzabile"
    ]

    for marker in markers:
        if marker in text:
            print(f"✅ README contiene: {marker}")
        else:
            ok = False
            print(f"❌ README non contiene: {marker}")
else:
    ok = False
    print("❌ manca README.md")

if not ok:
    raise SystemExit(1)

print("\n✅ Verifica migliorie finali completata")
