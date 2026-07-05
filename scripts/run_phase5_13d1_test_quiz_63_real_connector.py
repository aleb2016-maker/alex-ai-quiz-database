#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.1 — RUNNER TEST/QUIZ 63 REAL CONNECTOR
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_test_quiz_real_connector_v513d1 import (
    build_test_quiz_real_connection_report,
)

JSON_REPORT = ROOT / "reports" / "phase5_13d1_test_quiz_63_real_connector_v1.json"
MD_REPORT = ROOT / "reports" / "phase5_13d1_test_quiz_63_real_connector_v1.md"
SOURCE_TEST = ROOT / "backend" / "test_phase5_study_quiz_v1.py"
MOTORI = ROOT / "backend" / "motori_scrittura.py"


def extract_first_json_object(text: str) -> Dict[str, Any]:
    start = text.find("{")
    if start < 0:
        raise ValueError("Nessun oggetto JSON trovato nell'output del test reale.")

    depth = 0
    in_string = False
    escape = False

    for pos in range(start, len(text)):
        char = text[pos]
        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start:pos + 1])

    raise ValueError("Oggetto JSON iniziato ma non chiuso.")


def render_markdown(report: Dict[str, Any]) -> str:
    lines = [
        "# FASE 5.13D.1 — TEST/QUIZ 63 REAL CONNECTOR",
        "",
        f"Status: `{report['status']}`",
        "",
        "## Conteggi",
        "",
        f"- Route Test/Quiz: `{report['resolved_route_total']}`",
        f"- Controlli qualità Test/Quiz: `{report['resolved_test_quality_controls']}`",
        f"- Selector/orchestrator: `{report['resolved_selector_orchestrator']}`",
        f"- Quiz reali: `{report['real_output_quiz_questions_count']}`",
        f"- Motori eseguiti/tracciati: `{len(report['executed_motor_ids'])}`",
        f"- Motori mancanti: `{len(report['missing_motor_ids'])}`",
        "",
        "## Motori eseguiti/tracciati",
        "",
    ]

    for motor_id in report["executed_motor_ids"]:
        lines.append(f"- `{motor_id}`")

    lines.extend(["", "## Defects", ""])
    lines.append("- Nessuno" if not report["defects"] else "\n".join(f"- `{item}`" for item in report["defects"]))

    lines.extend(["", "## Warnings", ""])
    lines.append("- Nessuno" if not report["warnings"] else "\n".join(f"- `{item}`" for item in report["warnings"]))

    lines.extend([
        "",
        "## Note",
        "",
        "- Il connector 63 viene verificato sull'output reale di `backend/test_phase5_study_quiz_v1.py`.",
        "- Verifica anche 4 opzioni, risposta corretta presente e un solo flag corretto.",
        "- Nessuna UI/PDF/app viene modificata.",
    ])

    return "\n".join(lines) + "\n"


def main() -> int:
    defects: list[str] = []
    motori_text = MOTORI.read_text(encoding="utf-8", errors="replace")

    required_anchors = [
        "FASE 5.13D.1 — TEST/QUIZ 63 REAL CONNECTOR LOCAL SCOPE",
        "build_test_quiz_real_connection_report",
        '"test_quiz_real_connection_v513d1": test_quiz_real_connection_v513d1',
        "q52_build_quality_quiz",
        "q52_validate_quiz",
        "result.test_quiz = q52_build_quality_quiz",
        "result.errors.extend(q52_validate_quiz(result.test_quiz, facts, cfg.quiz_options_count))",
    ]

    for anchor in required_anchors:
        if anchor not in motori_text:
            defects.append(f"Anchor reale mancante in motori_scrittura.py: {anchor}")

    completed = subprocess.run(
        [sys.executable, str(SOURCE_TEST)],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )

    source_result = extract_first_json_object(completed.stdout)

    report = build_test_quiz_real_connection_report(
        source_result.get("test_quiz") or [],
        source_result.get("errors") or [],
    )

    if completed.returncode != 0:
        defects.append(f"source_test_returncode_not_zero:{completed.returncode}")

    if not source_result.get("approved"):
        defects.append("source_result_not_approved")

    if source_result.get("status") != "APPROVED":
        defects.append(f"source_status_not_APPROVED:{source_result.get('status')}")

    defects.extend(report["defects"])

    if defects:
        report["defects"] = defects
        report["status"] = "FAIL - Fase 5.13D.1: TEST_QUIZ_63_REAL_CONNECTOR_NOT_READY"

    JSON_REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    MD_REPORT.write_text(render_markdown(report), encoding="utf-8")

    print(report["status"])
    print(f"Route Test/Quiz: {report['resolved_route_total']}")
    print(f"Controlli qualità Test/Quiz: {report['resolved_test_quality_controls']}")
    print(f"Selector/orchestrator: {report['resolved_selector_orchestrator']}")
    print(f"Quiz reali: {report['real_output_quiz_questions_count']}")
    print(f"Motori eseguiti/tracciati: {len(report['executed_motor_ids'])}")
    print(f"Defects: {len(report['defects'])}")
    print(f"Warnings: {len(report['warnings'])}")
    print(f"JSON report: {JSON_REPORT}")
    print(f"Markdown report: {MD_REPORT}")

    if report["defects"]:
        print("Defects:")
        for defect in report["defects"]:
            print(f"- {defect}")
        return 1

    if report["warnings"]:
        print("Warnings:")
        for warning in report["warnings"]:
            print(f"- {warning}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
