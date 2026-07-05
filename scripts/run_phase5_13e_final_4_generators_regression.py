#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13E — REGRESSIONE AGGREGATA FINALE 4 GENERATORI

Scopo:
- verificare in un unico punto lo stato finale dei 4 generatori:
  1. Card
  2. Riassunto
  3. Domande studio
  4. Test/Quiz

Metodo:
- usa i report/checkpoint già presenti per Card e Riassunto;
- esegue i runner reali per Domande studio e Test/Quiz;
- esegue il test reale backend/test_phase5_study_quiz_v1.py;
- produce report JSON + MD;
- fallisce se mancano prove, PASS o conteggi minimi attesi.

Non modifica UI/PDF/app.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"

JSON_REPORT = REPORTS / "phase5_13e_final_4_generators_regression_v1.json"
MD_REPORT = REPORTS / "phase5_13e_final_4_generators_regression_v1.md"

EXPECTED = {
    "card_quality_controls": 52,
    "summary_route_total": 55,
    "study_route_total": 51,
    "study_quality_controls": 43,
    "test_quiz_route_total": 63,
    "test_quiz_quality_controls": 55,
    "selector_orchestrator": 8,
}


@dataclass
class CommandResult:
    label: str
    command: List[str]
    returncode: int
    stdout_tail: str


@dataclass
class GeneratorCheck:
    name: str
    status: str
    evidence: List[str]
    defects: List[str]
    warnings: List[str]


@dataclass
class FinalRegressionReport:
    phase: str
    status: str
    generators: List[Dict[str, Any]]
    commands: List[Dict[str, Any]]
    defects: List[str]
    warnings: List[str]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def _load_json(path: Path) -> Optional[Any]:
    try:
        return json.loads(_read_text(path))
    except Exception:
        return None


def _norm(value: Any) -> str:
    return " ".join(str(value or "").lower().split())


def _tail(text: str, max_chars: int = 7000) -> str:
    if len(text) <= max_chars:
        return text
    return text[-max_chars:]


def run_command(label: str, args: List[str]) -> CommandResult:
    completed = subprocess.run(
        args,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    return CommandResult(
        label=label,
        command=args,
        returncode=completed.returncode,
        stdout_tail=_tail(completed.stdout),
    )


def all_report_files() -> List[Path]:
    if not REPORTS.exists():
        return []
    return sorted(
        list(REPORTS.glob("*.json")) + list(REPORTS.glob("*.md")),
        key=lambda p: p.name,
    )


def find_reports_containing(*needles: str) -> List[Path]:
    found: List[Path] = []
    lowered_needles = [needle.lower() for needle in needles]
    for path in all_report_files():
        text = _read_text(path).lower()
        if all(needle in text for needle in lowered_needles):
            found.append(path)
    return found


def extract_first_json_object(text: str) -> Dict[str, Any]:
    start = text.find("{")
    if start < 0:
        raise ValueError("Nessun oggetto JSON trovato.")

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

    raise ValueError("JSON iniziato ma non chiuso.")


def _json_find_numbers(obj: Any, key_fragments: List[str]) -> List[int]:
    values: List[int] = []

    if isinstance(obj, dict):
        for key, value in obj.items():
            low_key = str(key).lower()
            if all(fragment in low_key for fragment in key_fragments):
                if isinstance(value, int):
                    values.append(value)
                elif isinstance(value, str) and value.isdigit():
                    values.append(int(value))
            values.extend(_json_find_numbers(value, key_fragments))
    elif isinstance(obj, list):
        for item in obj:
            values.extend(_json_find_numbers(item, key_fragments))

    return values


def check_card() -> GeneratorCheck:
    defects: List[str] = []
    warnings: List[str] = []
    evidence: List[str] = []

    candidate_names = [
        "phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.json",
        "phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.md",
    ]

    candidates = [REPORTS / name for name in candidate_names if (REPORTS / name).exists()]
    if not candidates:
        candidates = find_reports_containing("card", "52")

    if not candidates:
        defects.append("Nessun report Card trovato con evidenza conteggio 52.")
    else:
        for path in candidates[:5]:
            evidence.append(str(path.relative_to(ROOT)))

        matched_52 = False
        for path in candidates:
            text = _read_text(path)
            data = _load_json(path)

            if "Card 52" in text or "Card: 52" in text or "`52`" in text and "Card" in text:
                matched_52 = True

            if data is not None:
                numbers = _json_find_numbers(data, ["card"])
                if EXPECTED["card_quality_controls"] in numbers:
                    matched_52 = True

            if "card" in text.lower() and "52" in text:
                matched_52 = True

        if not matched_52:
            defects.append("Report Card trovato, ma non conferma chiaramente Card=52.")

    status = "PASS" if not defects else "FAIL"
    return GeneratorCheck("Card", status, evidence, defects, warnings)


def check_summary() -> GeneratorCheck:
    defects: List[str] = []
    warnings: List[str] = []
    evidence: List[str] = []

    candidates = find_reports_containing("summary", "55")
    candidates += find_reports_containing("riassunto", "55")

    unique: List[Path] = []
    seen = set()
    for path in candidates:
        if path not in seen:
            seen.add(path)
            unique.append(path)

    if not unique:
        defects.append("Nessun report Riassunto/Summary trovato con evidenza route 55.")
    else:
        for path in unique[:8]:
            evidence.append(str(path.relative_to(ROOT)))

        matched = False
        for path in unique:
            text = _read_text(path).lower()
            if "pass" in text and ("summary" in text or "riassunto" in text) and "55" in text:
                matched = True
                break

        if not matched:
            defects.append("Report Summary/Riassunto trovato, ma non conferma PASS + 55.")

    status = "PASS" if not defects else "FAIL"
    return GeneratorCheck("Riassunto", status, evidence, defects, warnings)


def check_study(commands: List[CommandResult]) -> GeneratorCheck:
    defects: List[str] = []
    warnings: List[str] = []
    evidence: List[str] = []

    c1 = run_command(
        "5.13C.1 Study Questions 51 connector",
        [sys.executable, "scripts/run_phase5_13c1_study_questions_real_connector.py"],
    )
    commands.append(c1)

    c2 = run_command(
        "5.13C.2 Study Questions final quality",
        [sys.executable, "scripts/run_phase5_13c2_study_questions_final_quality_gate.py"],
    )
    commands.append(c2)

    if c1.returncode != 0:
        defects.append("Runner 5.13C.1 non PASS.")
    if "PASS - Fase 5.13C.1" not in c1.stdout_tail:
        defects.append("Output 5.13C.1 non contiene PASS.")

    if c2.returncode != 0:
        defects.append("Runner 5.13C.2 non PASS.")
    if "PASS - Fase 5.13C.2" not in c2.stdout_tail:
        defects.append("Output 5.13C.2 non contiene PASS.")

    study_report = REPORTS / "phase5_13c2_study_questions_final_quality_gate_v1.json"
    if study_report.exists():
        evidence.append(str(study_report.relative_to(ROOT)))
        data = _load_json(study_report) or {}
        if data.get("route_total") != EXPECTED["study_route_total"]:
            defects.append(f"Study route_total atteso 51, trovato {data.get('route_total')}.")
        if data.get("study_quality_controls") != EXPECTED["study_quality_controls"]:
            defects.append(f"Study quality_controls atteso 43, trovato {data.get('study_quality_controls')}.")
        if data.get("selector_orchestrator") != EXPECTED["selector_orchestrator"]:
            defects.append(f"Study selector/orchestrator atteso 8, trovato {data.get('selector_orchestrator')}.")
        if data.get("defects"):
            defects.append(f"Study defects non vuoti: {data.get('defects')}")
        if data.get("warnings"):
            defects.append(f"Study warnings non vuoti: {data.get('warnings')}")
    else:
        defects.append("Report JSON 5.13C.2 mancante.")

    status = "PASS" if not defects else "FAIL"
    return GeneratorCheck("Domande studio", status, evidence, defects, warnings)


def check_test_quiz(commands: List[CommandResult]) -> GeneratorCheck:
    defects: List[str] = []
    warnings: List[str] = []
    evidence: List[str] = []

    d01 = run_command(
        "5.13D.0.1 Test/Quiz route 63",
        [sys.executable, "scripts/run_phase5_13d01_test_quiz_route_materializer.py"],
    )
    commands.append(d01)

    d1 = run_command(
        "5.13D.1 Test/Quiz 63 connector",
        [sys.executable, "scripts/run_phase5_13d1_test_quiz_63_real_connector.py"],
    )
    commands.append(d1)

    real_completed = subprocess.run(
        [sys.executable, "backend/test_phase5_study_quiz_v1.py"],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    real_full_stdout = real_completed.stdout
    real = CommandResult(
        label="Real study quiz test",
        command=[sys.executable, "backend/test_phase5_study_quiz_v1.py"],
        returncode=real_completed.returncode,
        stdout_tail=_tail(real_full_stdout),
    )
    commands.append(real)

    d2 = run_command(
        "5.13D.2 Test/Quiz final quality",
        [sys.executable, "scripts/run_phase5_13d2_test_quiz_final_quality_gate.py"],
    )
    commands.append(d2)

    expected_passes = [
        (d01, "PASS - Fase 5.13D.0.1"),
        (d1, "PASS - Fase 5.13D.1"),
        (real, "✅ TEST FASE 5.2 STUDY QUIZ V1 PASSATO"),
        (d2, "PASS - Fase 5.13D.2"),
    ]

    for result, token in expected_passes:
        if result.returncode != 0:
            defects.append(f"Comando {result.label} returncode={result.returncode}.")
        if token not in result.stdout_tail:
            defects.append(f"Comando {result.label} non contiene token PASS atteso: {token}")

    try:
        source = extract_first_json_object(real_full_stdout)
    except Exception as exc:
        defects.append(f"Impossibile leggere JSON test reale: {type(exc).__name__}:{exc}")
        source = {}

    if source:
        if source.get("approved") is not True:
            defects.append("Test reale approved non True.")
        if source.get("status") != "APPROVED":
            defects.append(f"Test reale status non APPROVED: {source.get('status')}")
        if source.get("errors"):
            defects.append(f"Test reale errors non vuoti: {source.get('errors')}")
        if source.get("warnings"):
            defects.append(f"Test reale warnings non vuoti: {source.get('warnings')}")

        quality_report = source.get("quality_report") or {}
        test_conn = quality_report.get("test_quiz_real_connection_v513d1") or {}
        if not str(test_conn.get("status", "")).startswith("PASS - Fase 5.13D.1"):
            defects.append(f"Connector Test/Quiz interno non PASS: {test_conn.get('status')}")
        if test_conn.get("resolved_route_total") != EXPECTED["test_quiz_route_total"]:
            defects.append(f"Route Test/Quiz attesa 63, trovata {test_conn.get('resolved_route_total')}.")
        if test_conn.get("resolved_test_quality_controls") != EXPECTED["test_quiz_quality_controls"]:
            defects.append(f"Controlli Test/Quiz attesi 55, trovati {test_conn.get('resolved_test_quality_controls')}.")
        if test_conn.get("resolved_selector_orchestrator") != EXPECTED["selector_orchestrator"]:
            defects.append(f"Selector Test/Quiz atteso 8, trovato {test_conn.get('resolved_selector_orchestrator')}.")
        if test_conn.get("missing_motor_ids"):
            defects.append(f"Test/Quiz missing_motor_ids non vuoti: {test_conn.get('missing_motor_ids')}")
        if test_conn.get("defects"):
            defects.append(f"Test/Quiz connector defects non vuoti: {test_conn.get('defects')}")
        if test_conn.get("warnings"):
            defects.append(f"Test/Quiz connector warnings non vuoti: {test_conn.get('warnings')}")

    d2_report = REPORTS / "phase5_13d2_test_quiz_final_quality_gate_v1.json"
    if d2_report.exists():
        evidence.append(str(d2_report.relative_to(ROOT)))
        data = _load_json(d2_report) or {}
        if data.get("route_total") != EXPECTED["test_quiz_route_total"]:
            defects.append(f"D2 route_total atteso 63, trovato {data.get('route_total')}.")
        if data.get("test_quality_controls") != EXPECTED["test_quiz_quality_controls"]:
            defects.append(f"D2 test_quality_controls atteso 55, trovato {data.get('test_quality_controls')}.")
        if data.get("selector_orchestrator") != EXPECTED["selector_orchestrator"]:
            defects.append(f"D2 selector/orchestrator atteso 8, trovato {data.get('selector_orchestrator')}.")
        if data.get("defects"):
            defects.append(f"D2 defects non vuoti: {data.get('defects')}")
        if data.get("warnings"):
            defects.append(f"D2 warnings non vuoti: {data.get('warnings')}")
    else:
        defects.append("Report JSON 5.13D.2 mancante.")

    status = "PASS" if not defects else "FAIL"
    return GeneratorCheck("Test/Quiz", status, evidence, defects, warnings)


def render_markdown(report: FinalRegressionReport) -> str:
    lines = [
        "# FASE 5.13E — REGRESSIONE AGGREGATA FINALE 4 GENERATORI",
        "",
        f"Status: `{report.status}`",
        "",
        "## Generatori",
        "",
        "| Generatore | Status | Evidenze | Defects | Warnings |",
        "|---|---|---:|---:|---:|",
    ]

    for generator in report.generators:
        lines.append(
            f"| {generator['name']} | `{generator['status']}` | "
            f"{len(generator['evidence'])} | {len(generator['defects'])} | {len(generator['warnings'])} |"
        )

    lines.extend(["", "## Comandi eseguiti", ""])

    for command in report.commands:
        cmd_text = " ".join(command["command"])
        lines.append(f"- `{command['label']}` → returncode `{command['returncode']}`")
        lines.append(f"  - comando: `{cmd_text}`")

    lines.extend(["", "## Evidenze", ""])

    for generator in report.generators:
        lines.append(f"### {generator['name']}")
        if generator["evidence"]:
            for item in generator["evidence"]:
                lines.append(f"- `{item}`")
        else:
            lines.append("- Nessuna")

    lines.extend(["", "## Defects", ""])

    if report.defects:
        for item in report.defects:
            lines.append(f"- `{item}`")
    else:
        lines.append("- Nessuno")

    lines.extend(["", "## Warnings", ""])

    if report.warnings:
        for item in report.warnings:
            lines.append(f"- `{item}`")
    else:
        lines.append("- Nessuno")

    lines.extend([
        "",
        "## Note",
        "",
        "- Questa regressione non modifica UI/PDF/app.",
        "- Card e Riassunto vengono verificati tramite evidenze/report già salvati.",
        "- Domande studio e Test/Quiz vengono verificati con runner reali e test reale.",
        "- Il checkpoint va committato solo se status finale PASS e working tree è controllato.",
    ])

    return "\n".join(lines) + "\n"


def main() -> int:
    REPORTS.mkdir(exist_ok=True)

    commands: List[CommandResult] = []
    generators: List[GeneratorCheck] = []

    generators.append(check_card())
    generators.append(check_summary())
    generators.append(check_study(commands))
    generators.append(check_test_quiz(commands))

    defects: List[str] = []
    warnings: List[str] = []

    for generator in generators:
        for defect in generator.defects:
            defects.append(f"{generator.name}: {defect}")
        for warning in generator.warnings:
            warnings.append(f"{generator.name}: {warning}")

    for command in commands:
        if command.returncode != 0:
            defects.append(f"Command failed: {command.label} returncode={command.returncode}")

    status = (
        "PASS - Fase 5.13E: FINAL_4_GENERATORS_REGRESSION_READY"
        if not defects and not warnings
        else "FAIL - Fase 5.13E: FINAL_4_GENERATORS_REGRESSION_NOT_READY"
    )

    report = FinalRegressionReport(
        phase="5.13E",
        status=status,
        generators=[asdict(item) for item in generators],
        commands=[asdict(item) for item in commands],
        defects=defects,
        warnings=warnings,
    )

    JSON_REPORT.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    MD_REPORT.write_text(render_markdown(report), encoding="utf-8")

    print(status)
    for generator in generators:
        print(
            f"{generator.name}: {generator.status} "
            f"defects={len(generator.defects)} warnings={len(generator.warnings)}"
        )
    print(f"Defects: {len(defects)}")
    print(f"Warnings: {len(warnings)}")
    print(f"JSON report: {JSON_REPORT}")
    print(f"Markdown report: {MD_REPORT}")

    if defects:
        print("Defects:")
        for defect in defects:
            print(f"- {defect}")
        return 1

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
