#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "config" / "temi_card_materie.json"
REPORT = ROOT / "reports" / "validatore_temi_card.md"
REQUIRED_FIELDS = ["nome_visibile", "palette", "sfondo", "icona_base", "stile", "badge", "parole_chiave"]


def is_hex_color(value: str) -> bool:
    return bool(re.fullmatch(r"#[0-9a-fA-F]{6}", value))


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    errors = []

    if "generico" not in data:
        errors.append("Manca il tema fallback generico.")

    for subject, theme in data.items():
        for field in REQUIRED_FIELDS:
            if field not in theme:
                errors.append(f"{subject}: manca campo {field}.")

        palette = theme.get("palette", [])
        if not isinstance(palette, list) or len(palette) < 3:
            errors.append(f"{subject}: palette deve avere almeno 3 colori.")
        else:
            for color in palette[:3]:
                if not is_hex_color(str(color)):
                    errors.append(f"{subject}: colore non valido {color}.")

        if not isinstance(theme.get("parole_chiave", []), list) or not theme.get("parole_chiave"):
            errors.append(f"{subject}: parole_chiave vuote o non valide.")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Validatore temi card", ""]
    if errors:
        lines.append("## Errori")
        lines.extend(f"- {error}" for error in errors)
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise SystemExit("❌ Temi card non validi. Vedi reports/validatore_temi_card.md")

    lines.append("✅ Tutti i temi card sono validi.")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("✅ Temi card validi")


if __name__ == "__main__":
    main()
