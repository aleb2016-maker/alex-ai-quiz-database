#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONCEPTS_PATH = ROOT / "config" / "icone_concetti_materie.json"
SYNONYMS_PATH = ROOT / "config" / "sinonimi_concetti.json"
THEMES_PATH = ROOT / "config" / "temi_card_materie.json"
REPORT = ROOT / "reports" / "validatore_concetti_card.md"


def main() -> None:
    concepts = json.loads(CONCEPTS_PATH.read_text(encoding="utf-8"))
    synonyms = json.loads(SYNONYMS_PATH.read_text(encoding="utf-8"))
    themes = json.loads(THEMES_PATH.read_text(encoding="utf-8"))
    errors = []

    for subject in concepts:
        if subject not in themes:
            errors.append(f"Materia {subject} presente nei concetti ma assente nei temi.")

    for subject, subject_concepts in concepts.items():
        if not isinstance(subject_concepts, dict) or not subject_concepts:
            errors.append(f"{subject}: nessun concetto configurato.")
            continue

        for concept_name, config in subject_concepts.items():
            if "icona" not in config or not str(config.get("icona", "")).strip():
                errors.append(f"{subject}/{concept_name}: manca icona.")
            if "decorazioni" not in config or not isinstance(config.get("decorazioni"), list):
                errors.append(f"{subject}/{concept_name}: decorazioni deve essere lista.")
            if concept_name not in synonyms:
                errors.append(f"{subject}/{concept_name}: manca voce in sinonimi_concetti.json.")

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = ["# Validatore concetti card", ""]
    if errors:
        lines.append("## Errori")
        lines.extend(f"- {error}" for error in errors)
        REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
        raise SystemExit("❌ Concetti card non validi. Vedi reports/validatore_concetti_card.md")

    lines.append("✅ Tutti i concetti card sono validi.")
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("✅ Concetti card validi")


if __name__ == "__main__":
    main()
