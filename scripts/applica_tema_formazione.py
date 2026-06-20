#!/usr/bin/env python3
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "temi_grafici_formazione.json"
OUT_DIR = ROOT / "dist" / "formazione"


def main():
    tema = sys.argv[1] if len(sys.argv) > 1 else "dark-tech"
    temi = json.loads(CONFIG.read_text(encoding="utf-8"))

    if tema not in temi:
        validi = ", ".join(sorted(temi))
        raise SystemExit(f"Tema non valido: {tema}. Temi disponibili: {validi}")

    scelto = temi[tema]
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUT_DIR / "tema_selezionato.json").write_text(
        json.dumps({tema: scelto}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8"
    )

    css = (
        ":root {\n"
        f"  --bg: {scelto['sfondo']};\n"
        f"  --card: {scelto['card']};\n"
        f"  --text: {scelto['testo']};\n"
        f"  --accent: {scelto['accento']};\n"
        "}\n"
    )

    (OUT_DIR / "theme-selected.css").write_text(css, encoding="utf-8")
    print(f"✅ Tema formazione applicato: {scelto['nome']} ({tema})")
    print("📌 File creati: dist/formazione/tema_selezionato.json, dist/formazione/theme-selected.css")


if __name__ == "__main__":
    main()
