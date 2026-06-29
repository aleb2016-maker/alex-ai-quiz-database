#!/usr/bin/env python3
"""
Verifica motori didattici RAG riutilizzabili V3.5C.

Passaggi:
1. verifica V3.4E
2. verifica bridge V3.5B verso motori quiz
3. genera output didattico V3.5C
4. fa passare anche l'output didattico nel bridge V3.5B
5. controlla naturalezza/fonte/layout/assenza riempitivi
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_motori_didattici_riutilizzabili_v35c.md"
BASE_IN = ROOT / "dist/generated/rag_output_kb_clean_v34e/outputs"
BASE_OUT = ROOT / "dist/generated/rag_output_didattico_riutilizzabile_v35c"
BASE_BRIDGE = ROOT / "dist/generated/rag_output_didattico_riutilizzabile_v35c_bridge"

DOCS = ["sicurezza", "sport", "curriculum", "poesia", "aziendale", "sicurezza_reale"]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    risultati = []
    errori = []

    code, log = run(["python3", "scripts/verifica_rag_output_kb_clean_v34e.py"])
    if code != 0:
        errori.append("V3.4E fallisce prima dei motori didattici")
        errori.append(log)

    code, log = run(["python3", "scripts/verifica_rag_bridge_motori_qualita_esistenti_v35b.py"])
    if code != 0:
        errori.append("Bridge V3.5B verso motori quiz fallisce prima dei motori didattici")
        errori.append(log)

    for name in DOCS:
        src = BASE_IN / name / "rag_output_kb_clean_v34e.json"
        dst = BASE_OUT / name / "rag_output_didactic_v35c.json"
        bridge_report = BASE_BRIDGE / name / "bridge_report.json"

        if not src.exists():
            errori.append(f"input V3.4E mancante per {name}: {src}")
            continue

        code, log = run([
            "python3",
            "scripts/rag_motore_didattico_riutilizzabile_v35c.py",
            "--input",
            str(src),
            "--output",
            str(dst),
        ])

        if code != 0:
            errori.append(f"motore didattico fallito per {name}")
            errori.append(log)
            continue

        data = json.loads(dst.read_text(encoding="utf-8"))
        q = data.get("controlli_qualita", {}).get("motore_didattico_v35c", {})

        if q.get("ok"):
            risultati.append(f"OK: motore didattico valido per {name}")
        else:
            errori.append(f"{name}: qualità didattica non valida: {q}")

        code, log = run([
            "python3",
            "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
            "--input",
            str(dst),
            "--output-report-json",
            str(bridge_report),
        ])

        if code != 0:
            errori.append(f"{name}: output didattico non passa nel bridge motori quiz")
            errori.append(log)
        else:
            risultati.append(f"OK: output didattico passa anche nei motori quiz per {name}")

    script_text = (ROOT / "scripts/rag_motore_didattico_riutilizzabile_v35c.py").read_text(encoding="utf-8", errors="ignore")

    required = [
        "naturalezza_domande_studio",
        "stile_card",
        "fonti_visibili",
        "rimozione_frasi_riempitive",
        "tono_didattico_finale",
        "layout_grafico",
        "ui_layout",
        "stile_card",
    ]

    for item in required:
        if item not in script_text:
            errori.append(f"motore didattico non dichiara copertura: {item}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Motori Didattici RAG Riutilizzabili V3.5C",
        "",
        "Verifica dei motori riutilizzabili per naturalezza, card, fonti, tono e layout.",
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

    print("=== VERIFICA MOTORI DIDATTICI RAG RIUTILIZZABILI V3.5C ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
