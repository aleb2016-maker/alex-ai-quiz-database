#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12D.1 — QUALITY REGISTRY BRIDGE CARD/SUMMARY/SOURCE MOTORS

Obiettivo:
- leggere il registry da 33 motori pronti e collegati della Fase 5.12C.1
- leggere i 10 motori Card/Riassunto/Fonti della Fase 5.12D
- collegare i 10 motori Card/Riassunto/Fonti
- produrre registry totale: 43 motori pronti e collegati

Questo modulo NON crea nuovi motori.
Questo modulo NON modifica i 33 motori già chiusi.
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

PHASE = "5.12D.1"
READY_LABEL = "QUALITY_REGISTRY_43_MOTORS_CONNECTED_V512D1"

REGISTRY_33_REPORT = REPORTS_DIR / "phase5_12c1_quality_registry_33_connected_v1.json"
CARD_REPORT = REPORTS_DIR / "phase5_12d_card_summary_source_quality_motors_v1.json"


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
    new_card_summary_source_motors: int
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


def _validate_registry_33(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["registry_33_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("registry_33_status_not_pass")

    if data.get("approved") is not True:
        defects.append("registry_33_not_approved")

    if data.get("ready_label") != "QUALITY_REGISTRY_33_MOTORS_CONNECTED_V512C1":
        defects.append("registry_33_ready_label_missing")

    if int(data.get("total_ready_connected_motors", -1)) != 33:
        defects.append(f"registry_33_total_not_33:{data.get('total_ready_connected_motors')}")

    motors = data.get("connected_motors") or []
    if len(motors) != 33:
        defects.append(f"registry_33_connected_motors_list_not_33:{len(motors)}")

    if data.get("defects"):
        defects.append("registry_33_has_defects")

    return defects


def _validate_card_report(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["card_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("card_status_not_pass")

    if data.get("approved") is not True:
        defects.append("card_not_approved")

    if data.get("ready_label") != "CARD_SUMMARY_SOURCE_QUALITY_MOTORS_V512D_READY":
        defects.append("card_ready_label_missing")

    registry = data.get("registry") or {}
    if int(registry.get("total_motors", -1)) != 10:
        defects.append(f"card_total_motors_not_10:{registry.get('total_motors')}")

    if data.get("targeted_tests_passed") != data.get("targeted_tests_total"):
        defects.append("card_targeted_tests_not_all_passed")

    if (data.get("good_case") or {}).get("passed") is not True:
        defects.append("card_good_case_not_passed")

    if (data.get("good_case") or {}).get("blocking_issues", 999) != 0:
        defects.append("card_good_case_has_blocking_issues")

    return defects


def _previous_connected_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []

    for m in data.get("connected_motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase=str(m.get("source_phase")),
            source_report=str(m.get("source_report", _rel(REGISTRY_33_REPORT))),
            category=str(m.get("category", "previous_ready_connected_motor")),
            status="READY_CONNECTED",
            confidence=str(m.get("confidence", "HIGH")),
            connection_type=str(m.get("connection_type", "registry_bridge_existing_verified")),
            areas=list(m.get("areas") or []),
        ))

    return rows


def _new_card_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []
    registry = data.get("registry") or {}

    for m in registry.get("motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase="5.12D",
            source_report=_rel(CARD_REPORT),
            category="card_summary_source_atomic_motor",
            status="READY_CONNECTED",
            confidence="HIGH",
            connection_type="registry_bridge_new_card_summary_source_motor",
            areas=["card", "summary", "sources"],
        ))

    return rows


def build_registry_bridge() -> RegistryBridgeResult:
    registry_33_data = _load_json(REGISTRY_33_REPORT)
    card_data = _load_json(CARD_REPORT)

    defects: List[str] = []
    warnings: List[str] = []

    defects.extend(_validate_registry_33(registry_33_data))
    defects.extend(_validate_card_report(card_data))

    connected: List[ConnectedMotor] = []

    if registry_33_data:
        connected.extend(_previous_connected_motors(registry_33_data))

    if card_data:
        connected.extend(_new_card_motors(card_data))

    ids = [m.id for m in connected]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    if duplicate_ids:
        defects.append("duplicate_connected_motor_ids:" + ",".join(duplicate_ids))

    previous_count = len([m for m in connected if m.source_phase != "5.12D"])
    card_count = len([m for m in connected if m.source_phase == "5.12D"])
    total = len(connected)

    if previous_count != 33:
        defects.append(f"previous_ready_connected_motors_not_33:{previous_count}")

    if card_count != 10:
        defects.append(f"connected_card_summary_source_motors_not_10:{card_count}")

    if total != 43:
        defects.append(f"total_ready_connected_motors_not_43:{total}")

    remaining_atomic_controls = {
        "atomic_controls_total_from_5_12a1": 64,
        "ready_connected_textual_controls": 12,
        "ready_connected_didactic_controls": 10,
        "ready_connected_card_summary_source_controls": 10,
        "ready_connected_atomic_controls": 32,
        "still_to_recreate": 31,
        "still_to_verify": 1,
        "total_ready_connected_registry_motors": 43,
    }

    approved = not defects

    return RegistryBridgeResult(
        phase=PHASE,
        ready_label=READY_LABEL if approved else None,
        status="PASS" if approved else "FAIL",
        approved=approved,
        total_ready_connected_motors=total,
        previous_ready_connected_motors=previous_count,
        new_card_summary_source_motors=card_count,
        connected_motors=connected,
        remaining_atomic_controls=remaining_atomic_controls,
        defects=defects,
        warnings=warnings,
        scope_guard={
            "created_new_motors": False,
            "connected_existing_5_12d_motors": True,
            "changed_existing_33_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "deleted_existing_files": False,
            "registry_bridge_only": True,
        },
    )


def registry_bridge_to_dict(result: RegistryBridgeResult) -> Dict[str, Any]:
    return asdict(result)
