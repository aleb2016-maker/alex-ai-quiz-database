#!/usr/bin/env python3
"""
Verifica RAG Motore Test Riutilizzabile V3.5D.

Passaggi:
1. verifica V3.4E
2. verifica bridge V3.5B
3. verifica motore didattico V3.5C
4. genera output test V3.5D
5. ricontrolla V3.5D nel bridge V3.5B
6. verifica campi interni/visibili/mappa risposta corretta
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_motore_test_riutilizzabile_v35d.md"

BASE_IN = ROOT / "dist/generated/rag_output_didattico_riutilizzabile_v35c"
BASE_OUT = ROOT / "dist/generated/rag_output_test_riutilizzabile_v35d"
BASE_BRIDGE = ROOT / "dist/generated/rag_output_test_riutilizzabile_v35d_bridge"

DOCS = ["sicurezza", "sport", "curriculum", "poesia", "aziendale", "sicurezza_reale"]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    risultati = []
    errori = []

    preliminari = [
        ("V3.4E", ["python3", "scripts/verifica_rag_output_kb_clean_v34e.py"]),
        ("V3.5B", ["python3", "scripts/verifica_rag_bridge_motori_qualita_esistenti_v35b.py"]),
        ("V3.5C", ["python3", "scripts/verifica_rag_motori_didattici_riutilizzabili_v35c.py"]),
    ]

    for label, command in preliminari:
        code, log = run(command)
        if code != 0:
            errori.append(f"{label} fallisce prima del motore test V3.5D")
            errori.append(log)
        else:
            risultati.append(f"OK: verifica preliminare {label}")

    for name in DOCS:
        src = BASE_IN / name / "rag_output_didactic_v35c.json"
        dst = BASE_OUT / name / "rag_output_test_v35d.json"
        bridge_report = BASE_BRIDGE / name / "bridge_report.json"

        if not src.exists():
            errori.append(f"input V3.5C mancante per {name}: {src}")
            continue

        code, log = run([
            "python3",
            "scripts/rag_motore_test_riutilizzabile_v35d.py",
            "--input",
            str(src),
            "--output",
            str(dst),
        ])

        if code != 0:
            errori.append(f"motore test V3.5D fallito per {name}")
            errori.append(log)
            continue

        data = json.loads(dst.read_text(encoding="utf-8"))
        q = data.get("controlli_qualita", {}).get("motore_test_v35d", {})

        if q.get("ok"):
            risultati.append(f"OK: motore test valido per {name}")
        else:
            errori.append(f"{name}: qualità test V3.5D non valida: {q}")

        code, log = run([
            "python3",
            "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
            "--input",
            str(dst),
            "--output-report-json",
            str(bridge_report),
        ])

        if code != 0:
            errori.append(f"{name}: output V3.5D non passa nel bridge motori quiz")
            errori.append(log)
        else:
            risultati.append(f"OK: output V3.5D passa nel bridge motori quiz per {name}")

        for idx, test in enumerate(data.get("test", []) or [], start=1):
            required = [
                "opzioni",
                "risposta_corretta",
                "opzioni_visibili",
                "risposta_corretta_visibile",
                "mappa_opzioni_v35d",
            ]

            for field in required:
                if field not in test:
                    errori.append(f"{name} test {idx}: campo mancante {field}")

    script_text = (ROOT / "scripts/rag_motore_test_riutilizzabile_v35d.py").read_text(encoding="utf-8", errors="ignore")

    required_markers = [
        "opzioni_visibili",
        "risposta_corretta_visibile",
        "mappa_opzioni_v35d",
        "test_rag_v35d",
        "motore_test_v35d",
    ]

    for marker in required_markers:
        if marker not in script_text:
            errori.append(f"motore test non contiene marker richiesto: {marker}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report RAG Motore Test Riutilizzabile V3.5D",
        "",
        "Verifica del ramo TEST separato da card, riassunti e domande studio.",
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

    print("=== VERIFICA RAG MOTORE TEST RIUTILIZZABILE V3.5D ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
