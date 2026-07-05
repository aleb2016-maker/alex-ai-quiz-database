#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12C.1 — QUALITY REGISTRY BRIDGE DIDACTIC MOTORS

Obiettivo:
- leggere il registry da 23 motori pronti e collegati della Fase 5.12B.1
- leggere i 10 motori qualità didattica della Fase 5.12C
- collegare i 10 motori didattici
- produrre registry totale: 33 motori pronti e collegati

Questo modulo NON crea nuovi motori.
Questo modulo NON modifica i 23 motori già chiusi.
Questo modulo NON modifica la pipeline 5.11.
Questo modulo NON modifica UI/PDF/CSS/app.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

PHASE = "5.12C.1"
READY_LABEL = "QUALITY_REGISTRY_33_MOTORS_CONNECTED_V512C1"

REGISTRY_23_REPORT = REPORTS_DIR / "phase5_12b1_quality_registry_23_connected_v1.json"
DIDACTIC_REPORT = REPORTS_DIR / "phase5_12c_didactic_quality_motors_v1.json"


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
    new_didactic_quality_motors: int
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


def _validate_registry_23(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["registry_23_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("registry_23_status_not_pass")

    if data.get("approved") is not True:
        defects.append("registry_23_not_approved")

    if data.get("ready_label") != "QUALITY_REGISTRY_23_MOTORS_CONNECTED_V512B1":
        defects.append("registry_23_ready_label_missing")

    if int(data.get("total_ready_connected_motors", -1)) != 23:
        defects.append(f"registry_23_total_not_23:{data.get('total_ready_connected_motors')}")

    motors = data.get("connected_motors") or []
    if len(motors) != 23:
        defects.append(f"registry_23_connected_motors_list_not_23:{len(motors)}")

    if data.get("defects"):
        defects.append("registry_23_has_defects")

    return defects


def _validate_didactic_report(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["didactic_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("didactic_status_not_pass")

    if data.get("approved") is not True:
        defects.append("didactic_not_approved")

    if data.get("ready_label") != "DIDACTIC_QUALITY_MOTORS_V512C_READY":
        defects.append("didactic_ready_label_missing")

    registry = data.get("registry") or {}
    if int(registry.get("total_motors", -1)) != 10:
        defects.append(f"didactic_total_motors_not_10:{registry.get('total_motors')}")

    if data.get("targeted_tests_passed") != data.get("targeted_tests_total"):
        defects.append("didactic_targeted_tests_not_all_passed")

    if (data.get("good_case") or {}).get("passed") is not True:
        defects.append("didactic_good_case_not_passed")

    if (data.get("good_case") or {}).get("blocking_issues", 999) != 0:
        defects.append("didactic_good_case_has_blocking_issues")

    return defects


def _previous_connected_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []

    for m in data.get("connected_motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase=str(m.get("source_phase")),
            source_report=str(m.get("source_report", _rel(REGISTRY_23_REPORT))),
            category=str(m.get("category", "previous_ready_connected_motor")),
            status="READY_CONNECTED",
            confidence=str(m.get("confidence", "HIGH")),
            connection_type=str(m.get("connection_type", "registry_bridge_existing_verified")),
            areas=list(m.get("areas") or []),
        ))

    return rows


def _new_didactic_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []
    registry = data.get("registry") or {}

    for m in registry.get("motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase="5.12C",
            source_report=_rel(DIDACTIC_REPORT),
            category="didactic_quality_atomic_motor",
            status="READY_CONNECTED",
            confidence="HIGH",
            connection_type="registry_bridge_new_didactic_quality_motor",
            areas=["qualita_didattica"],
        ))

    return rows


def build_registry_bridge() -> RegistryBridgeResult:
    registry_23_data = _load_json(REGISTRY_23_REPORT)
    didactic_data = _load_json(DIDACTIC_REPORT)

    defects: List[str] = []
    warnings: List[str] = []

    defects.extend(_validate_registry_23(registry_23_data))
    defects.extend(_validate_didactic_report(didactic_data))

    connected: List[ConnectedMotor] = []

    if registry_23_data:
        connected.extend(_previous_connected_motors(registry_23_data))

    if didactic_data:
        connected.extend(_new_didactic_motors(didactic_data))

    ids = [m.id for m in connected]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    if duplicate_ids:
        defects.append("duplicate_connected_motor_ids:" + ",".join(duplicate_ids))

    previous_count = len([m for m in connected if m.source_phase != "5.12C"])
    didactic_count = len([m for m in connected if m.source_phase == "5.12C"])
    total = len(connected)

    if previous_count != 23:
        defects.append(f"previous_ready_connected_motors_not_23:{previous_count}")

    if didactic_count != 10:
        defects.append(f"connected_didactic_quality_motors_not_10:{didactic_count}")

    if total != 33:
        defects.append(f"total_ready_connected_motors_not_33:{total}")

    remaining_atomic_controls = {
        "atomic_controls_total_from_5_12a1": 64,
        "ready_connected_textual_controls": 12,
        "ready_connected_didactic_controls": 10,
        "ready_connected_atomic_controls": 22,
        "still_to_recreate": 41,
        "still_to_verify": 1,
        "total_ready_connected_registry_motors": 33,
    }

    approved = not defects

    return RegistryBridgeResult(
        phase=PHASE,
        ready_label=READY_LABEL if approved else None,
        status="PASS" if approved else "FAIL",
        approved=approved,
        total_ready_connected_motors=total,
        previous_ready_connected_motors=previous_count,
        new_didactic_quality_motors=didactic_count,
        connected_motors=connected,
        remaining_atomic_controls=remaining_atomic_controls,
        defects=defects,
        warnings=warnings,
        scope_guard={
            "created_new_motors": False,
            "connected_existing_5_12c_motors": True,
            "changed_existing_23_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "deleted_existing_files": False,
            "registry_bridge_only": True,
        },
    )


def registry_bridge_to_dict(result: RegistryBridgeResult) -> Dict[str, Any]:
    return asdict(result)
