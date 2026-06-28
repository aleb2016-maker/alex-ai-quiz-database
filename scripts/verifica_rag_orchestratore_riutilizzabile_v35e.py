#!/usr/bin/env python3
"""
Verifica RAG Orchestratore Riutilizzabile V3.5E.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_orchestratore_riutilizzabile_v35e.md"
BASE_FINAL = ROOT / "dist/generated/rag_output_finale_orchestrato_v35e"

DOCS = ["sicurezza", "sport", "curriculum", "poesia", "aziendale", "sicurezza_reale"]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    risultati = []
    errori = []

    code, log = run(["python3", "scripts/rag_orchestratore_riutilizzabile_v35e.py"])

    if code != 0:
        errori.append("orchestratore V3.5E fallito")
        errori.append(log)
    else:
        risultati.append("OK: orchestratore V3.5E eseguito")

    for name in DOCS:
        path = BASE_FINAL / name / "rag_output_finale_v35e.json"

        if not path.exists():
            errori.append(f"{name}: output finale V3.5E mancante")
            continue

        data = json.loads(path.read_text(encoding="utf-8"))

        required_top = [
            "riassunto",
            "card",
            "test",
            "domande_studio",
            "controlli_qualita",
            "motori_riutilizzabili",
            "orchestratore_v35e",
        ]

        for field in required_top:
            if field not in data:
                errori.append(f"{name}: campo finale mancante {field}")

        if not data.get("controlli_qualita", {}).get("ok", False):
            errori.append(f"{name}: controlli_qualita finale non OK")

        if not data.get("orchestratore_v35e", {}).get("ok", False):
            errori.append(f"{name}: metadata orchestratore non OK")

        if "ui_layout" not in data:
            errori.append(f"{name}: ui_layout mancante")

        tests = data.get("test", []) or []

        if not tests:
            errori.append(f"{name}: test mancante")
        else:
            for idx, item in enumerate(tests, start=1):
                for field in [
                    "opzioni",
                    "risposta_corretta",
                    "opzioni_visibili",
                    "risposta_corretta_visibile",
                    "mappa_opzioni_v35d",
                ]:
                    if field not in item:
                        errori.append(f"{name} test {idx}: campo test mancante {field}")

        motors = data.get("motori_riutilizzabili", {})

        for motor in ["didattico", "test", "orchestratore"]:
            if motor not in motors:
                errori.append(f"{name}: motore riutilizzabile non dichiarato: {motor}")

        risultati.append(f"OK: output finale controllato per {name}")

    code, log = run(["python3", "scripts/verifica_rag_demo_output_kb_clean_v34f.py"])

    if code != 0:
        errori.append("pagina demo separata non valida dopo V3.5E")
        errori.append(log)
    else:
        risultati.append("OK: pagina demo separata valida dopo V3.5E")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report RAG Orchestratore Riutilizzabile V3.5E",
        "",
        "Verifica dell'orchestratore completo RAG.",
        "",
        "## Risultati",
    ]

    for r in risultati:
        lines.append(f"- {r}")

    lines.append("")
    lines.append(f"Errori totali: {len(errori)}")
    lines.append("")

    if errori:
        lines.append("## Errori")
        for e in errori:
            lines.append(f"- {e}")
        lines.append("")
        lines.append("ESITO: DA CORREGGERE")
    else:
        lines.append("ESITO: OK")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA RAG ORCHESTRATORE RIUTILIZZABILE V3.5E ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
