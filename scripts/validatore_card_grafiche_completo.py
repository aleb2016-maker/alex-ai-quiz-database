#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "validatore_card_grafiche_completo.md"


def run(command: list[str]) -> None:
    print("▶️ " + " ".join(command))
    subprocess.run(command, cwd=ROOT, check=True)


def main() -> None:
    run([sys.executable, "scripts/validatore_temi_card.py"])
    run([sys.executable, "scripts/validatore_concetti_card.py"])
    run([sys.executable, "scripts/motore_card_grafiche.py", "--demo"])

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        "# Validazione completa motore card grafiche\n\n"
        "✅ Temi validi.\n"
        "✅ Concetti validi.\n"
        "✅ Demo HTML generata in `reports/demo_card_grafiche.html`.\n",
        encoding="utf-8",
    )

    print("✅ Validazione completa motore card grafiche superata")


if __name__ == "__main__":
    main()
