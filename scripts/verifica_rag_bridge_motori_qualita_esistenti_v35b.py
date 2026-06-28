#!/usr/bin/env python3
"""
Verifica bridge reale RAG → motori qualità esistenti V3.5B.

Non basta che i file esistano:
questa verifica fallisce se il bridge non importa e non usa davvero
funzioni dei motori vecchi.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT_MD = ROOT / "reports/rag_bridge_motori_qualita_esistenti_v35b.md"
BASE = ROOT / "dist/generated/rag_bridge_motori_qualita_esistenti_v35b"

INPUTS = [
    "sicurezza",
    "sport",
    "curriculum",
    "poesia",
    "aziendale",
    "sicurezza_reale",
]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    risultati = []
    errori = []

    code, log = run(["python3", "scripts/verifica_rag_output_kb_clean_v34e.py"])

    if code != 0:
        errori.append("V3.4E non passa prima del bridge")
        errori.append(log)

    for name in INPUTS:
        input_path = ROOT / "dist/generated/rag_output_kb_clean_v34e/outputs" / name / "rag_output_kb_clean_v34e.json"
        report_json = BASE / name / "bridge_report.json"

        if not input_path.exists():
            errori.append(f"output V3.4E mancante: {input_path}")
            continue

        code, log = run([
            "python3",
            "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
            "--input",
            str(input_path),
            "--output-report-json",
            str(report_json),
        ])

        if not report_json.exists():
            errori.append(f"report bridge mancante per {name}")
            errori.append(log)
            continue

        data = json.loads(report_json.read_text(encoding="utf-8"))

        if data.get("funzioni_usate"):
            risultati.append(f"OK: bridge ha usato motori esistenti per {name}")
        else:
            errori.append(f"{name}: nessuna funzione dei motori vecchi usata")

        if data.get("ok"):
            risultati.append(f"OK: output RAG passa nei motori esistenti per {name}")
        else:
            risultati.append(f"DA CORREGGERE: output RAG bocciato dai motori esistenti per {name}")
            for e in data.get("errori", []):
                errori.append(f"{name}: {e}")

    script_text = (ROOT / "scripts/rag_bridge_motori_qualita_esistenti_v35b.py").read_text(encoding="utf-8", errors="ignore")

    required_refs = [
        "motore_qualita_generale.py",
        "motore_distrattori_ai.py",
        "importlib.util",
        "funzioni_usate",
    ]

    for ref in required_refs:
        if ref not in script_text:
            errori.append(f"bridge non contiene riferimento obbligatorio: {ref}")

    REPORT_MD.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Bridge RAG verso motori qualità esistenti V3.5B",
        "",
        "Verifica che l'output RAG venga davvero controllato dai motori qualità già presenti nel progetto.",
        "",
        "## Risultati",
    ]

    for r in risultati:
        lines.append(f"- {r}")

    lines.append("")
    lines.append(f"Errori totali: {len(errori)}")
    lines.append("")

    if errori:
        lines.append("## Errori / Da correggere")
        for e in errori:
            lines.append(f"- {e}")
        lines.append("")
        lines.append("ESITO: DA CORREGGERE")
    else:
        lines.append("ESITO: OK")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA BRIDGE RAG MOTORI QUALITÀ ESISTENTI V3.5B ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT_MD.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
