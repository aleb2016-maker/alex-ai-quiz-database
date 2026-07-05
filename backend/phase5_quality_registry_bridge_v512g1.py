#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

PHASE = "5.12G.1"
READY_LABEL = "QUALITY_REGISTRY_65_MOTORS_CONNECTED_V512G1"

REGISTRY_59_REPORT = REPORTS_DIR / "phase5_12f1_quality_registry_59_connected_v1.json"
DUPLICATE_REPORT = REPORTS_DIR / "phase5_12g_contextual_duplicate_motors_v1.json"


@dataclass
class ConnectedMotor:
    id: str
    title: str
    source_phase: str
    source_report: str
    category: str
    status: str
    confidence: str
    connection_type: str
    areas: List[str]


@dataclass
class RegistryBridgeResult:
    phase: str
    ready_label: Optional[str]
    status: str
    approved: bool
    total_ready_connected_motors: int
    previous_ready_connected_motors: int
    new_contextual_duplicate_motors: int
    connected_motors: List[ConnectedMotor]
    remaining_atomic_controls: Dict[str, int]
    defects: List[str]
    warnings: List[str]
    scope_guard: Dict[str, Any]


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except Exception:
        return str(path)


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _validate_registry_59(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["registry_59_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("registry_59_status_not_pass")
    if data.get("approved") is not True:
        defects.append("registry_59_not_approved")
    if data.get("ready_label") != "QUALITY_REGISTRY_59_MOTORS_CONNECTED_V512F1":
        defects.append("registry_59_ready_label_missing")
    if int(data.get("total_ready_connected_motors", -1)) != 59:
        defects.append(f"registry_59_total_not_59:{data.get('total_ready_connected_motors')}")
    if len(data.get("connected_motors") or []) != 59:
        defects.append(f"registry_59_connected_list_not_59:{len(data.get('connected_motors') or [])}")
    if data.get("defects"):
        defects.append("registry_59_has_defects")

    return defects


def _validate_duplicate_report(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["contextual_duplicate_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("contextual_duplicate_status_not_pass")
    if data.get("approved") is not True:
        defects.append("contextual_duplicate_not_approved")
    if data.get("ready_label") != "CONTEXTUAL_DUPLICATE_MOTORS_V512G_READY":
        defects.append("contextual_duplicate_ready_label_missing")

    registry = data.get("registry") or {}
    if int(registry.get("total_motors", -1)) != 6:
        defects.append(f"contextual_duplicate_total_motors_not_6:{registry.get('total_motors')}")

    if data.get("targeted_tests_passed") != data.get("targeted_tests_total"):
        defects.append("contextual_duplicate_targeted_tests_not_all_passed")

    if (data.get("good_case") or {}).get("passed") is not True:
        defects.append("contextual_duplicate_good_case_not_passed")

    if (data.get("good_case") or {}).get("blocking_issues", 999) != 0:
        defects.append("contextual_duplicate_good_case_has_blocking_issues")

    return defects


def _previous_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []

    for m in data.get("connected_motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase=str(m.get("source_phase")),
            source_report=str(m.get("source_report", _rel(REGISTRY_59_REPORT))),
            category=str(m.get("category", "previous_ready_connected_motor")),
            status="READY_CONNECTED",
            confidence=str(m.get("confidence", "HIGH")),
            connection_type=str(m.get("connection_type", "registry_bridge_existing_verified")),
            areas=list(m.get("areas") or []),
        ))

    return rows


def _new_duplicate_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []
    registry = data.get("registry") or {}

    for m in registry.get("motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase="5.12G",
            source_report=_rel(DUPLICATE_REPORT),
            category="contextual_duplicate_universal_motor",
            status="READY_CONNECTED",
            confidence="HIGH",
            connection_type="registry_bridge_new_contextual_duplicate_motor",
            areas=list(m.get("areas") or ["card", "summary", "study_questions", "test_quiz", "general_text"]),
        ))

    return rows


def build_registry_bridge() -> RegistryBridgeResult:
    registry_59 = _load_json(REGISTRY_59_REPORT)
    duplicate_report = _load_json(DUPLICATE_REPORT)

    defects: List[str] = []
    warnings: List[str] = []

    defects.extend(_validate_registry_59(registry_59))
    defects.extend(_validate_duplicate_report(duplicate_report))

    connected: List[ConnectedMotor] = []

    if registry_59:
        connected.extend(_previous_motors(registry_59))
    if duplicate_report:
        connected.extend(_new_duplicate_motors(duplicate_report))

    ids = [m.id for m in connected]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    if duplicate_ids:
        defects.append("duplicate_connected_motor_ids:" + ",".join(duplicate_ids))

    previous_count = len([m for m in connected if m.source_phase != "5.12G"])
    duplicate_count = len([m for m in connected if m.source_phase == "5.12G"])
    total = len(connected)

    if previous_count != 59:
        defects.append(f"previous_ready_connected_motors_not_59:{previous_count}")
    if duplicate_count != 6:
        defects.append(f"connected_contextual_duplicate_motors_not_6:{duplicate_count}")
    if total != 65:
        defects.append(f"total_ready_connected_motors_not_65:{total}")

    remaining_atomic_controls = {
        "atomic_controls_total_from_5_12a1": 64,
        "ready_connected_textual_controls": 12,
        "ready_connected_didactic_controls": 10,
        "ready_connected_card_summary_source_controls": 10,
        "ready_connected_test_quiz_controls": 12,
        "ready_connected_advanced_language_repair_controls": 4,
        "ready_connected_contextual_duplicate_controls": 6,
        "ready_connected_atomic_controls": 54,
        "still_to_recreate": 9,
        "still_to_verify": 1,
        "total_ready_connected_registry_motors": 65,
    }

    approved = not defects

    return RegistryBridgeResult(
        phase=PHASE,
        ready_label=READY_LABEL if approved else None,
        status="PASS" if approved else "FAIL",
        approved=approved,
        total_ready_connected_motors=total,
        previous_ready_connected_motors=previous_count,
        new_contextual_duplicate_motors=duplicate_count,
        connected_motors=connected,
        remaining_atomic_controls=remaining_atomic_controls,
        defects=defects,
        warnings=warnings,
        scope_guard={
            "created_new_motors": False,
            "connected_existing_5_12g_motors": True,
            "changed_existing_59_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "deleted_existing_files": False,
            "registry_bridge_only": True,
        },
    )


def registry_bridge_to_dict(result: RegistryBridgeResult) -> Dict[str, Any]:
    return asdict(result)
