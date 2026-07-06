#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Smoke test Fase 5.15A.

Runs the executable registry probe and fails if the current pipeline still has
declarative motor claims without real generator-level QM trace.
"""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
PROOF_JSON = REPORTS / "phase5_15a_executable_registry_connection_proof_v1.json"
TRACE_JSON = REPORTS / "phase5_15a_generator_motor_trace_v1.json"


def ensure_import_path() -> None:
    for path in [ROOT, ROOT / "scripts", ROOT / "backend"]:
        value = str(path)
        if value not in sys.path:
            sys.path.insert(0, value)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def append_defect(defects: List[str], code: str, detail: str) -> None:
    defects.append(f"{code}: {detail}")


def validate_reports(proof: Dict[str, Any], trace: List[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not PROOF_JSON.exists():
        append_defect(defects, "PROOF_JSON_MISSING", str(PROOF_JSON))
    if not TRACE_JSON.exists():
        append_defect(defects, "TRACE_JSON_MISSING", str(TRACE_JSON))

    summary = proof.get("summary") or {}
    if summary.get("concrete_motors_identified") != 64:
        append_defect(defects, "CONCRETE_MOTORS_COUNT_UNEXPECTED", str(summary.get("concrete_motors_identified")))
    if summary.get("slot_to_materialize") != 9:
        append_defect(defects, "SLOTS_TO_MATERIALIZE_UNEXPECTED", str(summary.get("slot_to_materialize")))
    if summary.get("executable_motors", 0) <= 0:
        append_defect(defects, "NO_EXECUTABLE_MOTORS_PROVED", "probe did not execute any motor")

    statuses = {m.get("status") for m in proof.get("motors") or []}
    required_statuses = {"EXECUTABLE", "SLOT_TO_MATERIALIZE"}
    if not required_statuses.issubset(statuses):
        append_defect(defects, "REGISTRY_CATEGORIES_NOT_DISTINGUISHED", ",".join(sorted(statuses)))

    generators = {t.get("kind") for t in trace}
    if generators != {"summary", "cards", "study", "quiz"}:
        append_defect(defects, "GENERATOR_TRACE_INCOMPLETE", ",".join(sorted(str(x) for x in generators)))

    for item in trace:
        kind = item.get("kind")
        if item.get("output_produced") and item.get("input_chars", 0) <= 0:
            append_defect(defects, "OUTPUT_WITHOUT_REAL_INPUT", str(kind))
        text = (item.get("output_preview") or "").lower()
        if "sicurezza informatica aziendale" in text and item.get("input_label") != "fixture_sicurezza":
            append_defect(defects, "FALLBACK_OR_DEMO_OUTPUT_DETECTED", str(kind))
        if item.get("declared_all_motors_connected") and not item.get("real_invoked_quality_motor_ids"):
            append_defect(
                defects,
                "ALL_MOTORS_CONNECTED_WITHOUT_REAL_QM_TRACE",
                f"{item.get('input_label')}:{kind}",
            )
        if item.get("output_produced") and item.get("route") in {"", None, "ERROR"}:
            append_defect(defects, "UNTRACEABLE_ROUTE", f"{item.get('input_label')}:{kind}")

    return defects


def main() -> int:
    ensure_import_path()
    probe = importlib.import_module("scripts.phase5_15a_executable_quality_registry_probe")
    probe.main()

    proof = load_json(PROOF_JSON)
    trace = load_json(TRACE_JSON)
    defects = validate_reports(proof, trace)

    smoke_report = {
        "phase": "5.15A",
        "status": "FAIL" if defects else "PASS",
        "defects": defects,
        "proof_json": str(PROOF_JSON.relative_to(ROOT)),
        "trace_json": str(TRACE_JSON.relative_to(ROOT)),
    }
    (REPORTS / "phase5_15a_executable_registry_connection_smoke_v1.json").write_text(
        json.dumps(smoke_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(json.dumps(smoke_report, ensure_ascii=False, indent=2))
    return 1 if defects else 0


if __name__ == "__main__":
    raise SystemExit(main())
