#!/usr/bin/env python3
"""
RAG Orchestratore Riutilizzabile V3.5E

Esegue la pipeline completa RAG già costruita:

V3.4E -> output da KB pulita
V3.5B -> bridge motori qualità quiz
V3.5C -> motore didattico card/riassunti/domande studio/layout
V3.5D -> motore test separato
V3.5E -> output finale orchestrato per UI/PDF/app

Nota:
questo NON è ancora il selezionatore intelligente.
Il selezionatore sarà il livello successivo e deciderà quali motori usare in base al compito.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

DOCS_DEFAULT = [
    "sicurezza",
    "sport",
    "curriculum",
    "poesia",
    "aziendale",
    "sicurezza_reale",
]

BASE_V34E = ROOT / "dist/generated/rag_output_kb_clean_v34e/outputs"
BASE_V35C = ROOT / "dist/generated/rag_output_didattico_riutilizzabile_v35c"
BASE_V35D = ROOT / "dist/generated/rag_output_test_riutilizzabile_v35d"
BASE_FINAL = ROOT / "dist/generated/rag_output_finale_orchestrato_v35e"
BASE_BRIDGE = ROOT / "dist/generated/rag_output_finale_orchestrato_v35e_bridge"


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def tail(text: str, max_lines: int = 80) -> str:
    lines = text.splitlines()
    return "\n".join(lines[-max_lines:])


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def add_orchestrator_metadata(data: dict[str, Any], name: str) -> dict[str, Any]:
    final = dict(data)

    final["orchestratore_v35e"] = {
        "ok": True,
        "documento": name,
        "versione": "rag_orchestratore_riutilizzabile_v35e",
        "creato_il": datetime.now().isoformat(timespec="seconds"),
        "pipeline": [
            "rag_output_kb_clean_v34e",
            "rag_bridge_motori_qualita_esistenti_v35b",
            "rag_motore_didattico_riutilizzabile_v35c",
            "rag_motore_test_riutilizzabile_v35d",
            "rag_output_finale_orchestrato_v35e",
        ],
        "output_finale": "ui_pdf_app",
        "nota_architetturale": (
            "Card, riassunti e domande studio passano dal motore didattico; "
            "i test passano dal motore test separato con campi interni e campi visibili."
        ),
    }

    quality = dict(final.get("controlli_qualita", {}))
    quality["orchestratore_v35e"] = {
        "ok": True,
        "pipeline_completa": True,
        "output_finale_presente": True,
    }
    quality["ok"] = bool(quality.get("ok", True))
    final["controlli_qualita"] = quality

    motors = dict(final.get("motori_riutilizzabili", {}))
    motors["orchestratore"] = "rag_orchestratore_riutilizzabile_v35e"
    final["motori_riutilizzabili"] = motors

    return final


def orchestrate_document(name: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "documento": name,
        "ok": False,
        "passaggi": [],
        "errori": [],
        "output": {},
    }

    input_v34e = BASE_V34E / name / "rag_output_kb_clean_v34e.json"
    output_v35c = BASE_V35C / name / "rag_output_didactic_v35c.json"
    output_v35d = BASE_V35D / name / "rag_output_test_v35d.json"
    output_finale = BASE_FINAL / name / "rag_output_finale_v35e.json"

    bridge_base = BASE_BRIDGE / name / "bridge_base_v35b.json"
    bridge_didattico = BASE_BRIDGE / name / "bridge_didattico_v35c.json"
    bridge_test = BASE_BRIDGE / name / "bridge_test_v35d.json"
    bridge_finale = BASE_BRIDGE / name / "bridge_finale_v35e.json"

    if not input_v34e.exists():
        result["errori"].append(f"input V3.4E mancante: {input_v34e}")
        return result

    steps = [
        (
            "bridge_base_v35b",
            [
                "python3",
                "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
                "--input",
                str(input_v34e),
                "--output-report-json",
                str(bridge_base),
            ],
        ),
        (
            "motore_didattico_v35c",
            [
                "python3",
                "scripts/rag_motore_didattico_riutilizzabile_v35c.py",
                "--input",
                str(input_v34e),
                "--output",
                str(output_v35c),
            ],
        ),
        (
            "bridge_didattico_v35b",
            [
                "python3",
                "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
                "--input",
                str(output_v35c),
                "--output-report-json",
                str(bridge_didattico),
            ],
        ),
        (
            "motore_test_v35d",
            [
                "python3",
                "scripts/rag_motore_test_riutilizzabile_v35d.py",
                "--input",
                str(output_v35c),
                "--output",
                str(output_v35d),
            ],
        ),
        (
            "bridge_test_v35b",
            [
                "python3",
                "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
                "--input",
                str(output_v35d),
                "--output-report-json",
                str(bridge_test),
            ],
        ),
    ]

    for label, command in steps:
        code, log = run(command)
        step_ok = code == 0

        result["passaggi"].append({
            "nome": label,
            "ok": step_ok,
            "codice": code,
            "log": tail(log),
        })

        if not step_ok:
            result["errori"].append(f"{name}: passaggio fallito {label}")
            result["errori"].append(tail(log))
            return result

    if not output_v35d.exists():
        result["errori"].append(f"output V3.5D mancante: {output_v35d}")
        return result

    final_data = add_orchestrator_metadata(read_json(output_v35d), name)
    write_json(output_finale, final_data)

    code, log = run([
        "python3",
        "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
        "--input",
        str(output_finale),
        "--output-report-json",
        str(bridge_finale),
    ])

    result["passaggi"].append({
        "nome": "bridge_finale_v35b",
        "ok": code == 0,
        "codice": code,
        "log": tail(log),
    })

    if code != 0:
        result["errori"].append(f"{name}: output finale V3.5E non passa nel bridge")
        result["errori"].append(tail(log))
        return result

    result["ok"] = True
    result["output"] = {
        "v34e": str(input_v34e.relative_to(ROOT)),
        "v35c": str(output_v35c.relative_to(ROOT)),
        "v35d": str(output_v35d.relative_to(ROOT)),
        "finale_v35e": str(output_finale.relative_to(ROOT)),
        "bridge_finale": str(bridge_finale.relative_to(ROOT)),
    }

    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--docs",
        nargs="*",
        default=DOCS_DEFAULT,
        help="Documenti da orchestrare. Default: tutti i documenti test.",
    )
    parser.add_argument(
        "--skip-precheck",
        action="store_true",
        help="Salta le verifiche preliminari complete.",
    )
    parser.add_argument(
        "--report-json",
        default=str(ROOT / "dist/generated/rag_output_finale_orchestrato_v35e/orchestratore_report_v35e.json"),
    )
    args = parser.parse_args()

    risultati = []
    errori = []

    if not args.skip_precheck:
        preliminari = [
            ("V3.4E output base", ["python3", "scripts/verifica_rag_output_kb_clean_v34e.py"]),
            ("V3.5B bridge quiz", ["python3", "scripts/verifica_rag_bridge_motori_qualita_esistenti_v35b.py"]),
            ("V3.5C motori didattici", ["python3", "scripts/verifica_rag_motori_didattici_riutilizzabili_v35c.py"]),
            ("V3.5D motore test", ["python3", "scripts/verifica_rag_motore_test_riutilizzabile_v35d.py"]),
        ]

        for label, command in preliminari:
            code, log = run(command)
            if code == 0:
                risultati.append(f"OK: precheck {label}")
            else:
                errori.append(f"precheck fallito: {label}")
                errori.append(tail(log))

    document_results = []

    if not errori:
        for name in args.docs:
            res = orchestrate_document(name)
            document_results.append(res)

            if res["ok"]:
                risultati.append(f"OK: orchestrazione completa per {name}")
            else:
                errori.extend(res["errori"])

    report = {
        "ok": not errori,
        "versione": "rag_orchestratore_riutilizzabile_v35e",
        "risultati": risultati,
        "errori": errori,
        "documenti": document_results,
    }

    report_path = Path(args.report_json)
    write_json(report_path, report)

    print("=== RAG ORCHESTRATORE RIUTILIZZABILE V3.5E ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report JSON:", report_path.relative_to(ROOT) if report_path.is_relative_to(ROOT) else report_path)
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    if errori:
        print("")
        print("ERRORI:")
        for e in errori[:20]:
            print("-", e)

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
