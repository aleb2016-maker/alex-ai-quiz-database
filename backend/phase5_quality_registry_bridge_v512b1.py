#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12B.1 — QUALITY REGISTRY BRIDGE

Obiettivo:
- collegare i 12 motori qualità testuale della Fase 5.12B
- sommarli agli 11 motori reali salvabili della Fase 5.12A.1
- produrre registry totale: 23 motori pronti e collegati

Questo modulo NON crea nuovi motori.
Questo modulo NON modifica UI/PDF/CSS/app.
Questo modulo NON cambia i motori esistenti.
Questo modulo collega e registra motori già verificati.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

PHASE = "5.12B.1"
READY_LABEL = "QUALITY_REGISTRY_23_MOTORS_CONNECTED_V512B1"

PIPELINE_READY_REPORT = REPORTS_DIR / "phase5_11_pipeline_output_ready_report.json"
SALVABLE_REPORT = REPORTS_DIR / "phase5_12a1_motori_salvabili_strict_v1.json"
TEXT_QUALITY_REPORT = REPORTS_DIR / "phase5_12b_text_quality_motors_v1.json"


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
    previous_salvable_motors: int
    new_text_quality_motors: int
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


def _validate_pipeline_ready(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["pipeline_ready_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("pipeline_5_11_status_not_pass")

    if data.get("pipeline_output_ready") is not True:
        defects.append("pipeline_output_ready_not_true")

    if data.get("ready_label") != "PIPELINE_OUTPUT_READY":
        defects.append("pipeline_ready_label_missing")

    return defects


def _validate_salvable_report(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["salvable_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("salvable_report_status_not_pass")

    if data.get("ready_label") != "MOTORI_SALVABILI_STRICT_MAP_READY":
        defects.append("salvable_ready_label_missing")

    if int(data.get("salvable_motors_count", -1)) != 11:
        defects.append(f"salvable_motors_count_not_11:{data.get('salvable_motors_count')}")

    motors = data.get("salvable_motors") or []
    if len(motors) != 11:
        defects.append(f"salvable_motors_list_not_11:{len(motors)}")

    return defects


def _validate_text_quality_report(data: Optional[Dict[str, Any]]) -> List[str]:
    defects: List[str] = []

    if not data:
        return ["text_quality_report_missing_or_invalid"]

    if data.get("status") != "PASS":
        defects.append("text_quality_status_not_pass")

    if data.get("approved") is not True:
        defects.append("text_quality_not_approved")

    if data.get("ready_label") != "TEXT_QUALITY_MOTORS_V512B_READY":
        defects.append("text_quality_ready_label_missing")

    registry = data.get("registry") or {}
    if int(registry.get("total_motors", -1)) != 12:
        defects.append(f"text_quality_total_motors_not_12:{registry.get('total_motors')}")

    if data.get("targeted_tests_passed") != data.get("targeted_tests_total"):
        defects.append("text_quality_targeted_tests_not_all_passed")

    if (data.get("good_case") or {}).get("passed") is not True:
        defects.append("text_quality_good_case_not_passed")

    return defects


def _connected_previous_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []

    for m in data.get("salvable_motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase="5.12A.1",
            source_report=_rel(SALVABLE_REPORT),
            category="previous_salvable_registry_motor",
            status="READY_CONNECTED",
            confidence=str(m.get("confidence", "HIGH")),
            connection_type="registry_bridge_existing_verified",
            areas=list(m.get("covered_areas") or []),
        ))

    return rows


def _connected_text_quality_motors(data: Dict[str, Any]) -> List[ConnectedMotor]:
    rows: List[ConnectedMotor] = []
    registry = data.get("registry") or {}

    for m in registry.get("motors", []):
        rows.append(ConnectedMotor(
            id=str(m.get("id")),
            title=str(m.get("title")),
            source_phase="5.12B",
            source_report=_rel(TEXT_QUALITY_REPORT),
            category="text_quality_atomic_motor",
            status="READY_CONNECTED",
            confidence="HIGH",
            connection_type="registry_bridge_new_text_quality_motor",
            areas=["qualita_testuale"],
        ))

    return rows


def build_registry_bridge() -> RegistryBridgeResult:
    pipeline_data = _load_json(PIPELINE_READY_REPORT)
    salvable_data = _load_json(SALVABLE_REPORT)
    text_quality_data = _load_json(TEXT_QUALITY_REPORT)

    defects: List[str] = []
    warnings: List[str] = []

    defects.extend(_validate_pipeline_ready(pipeline_data))
    defects.extend(_validate_salvable_report(salvable_data))
    defects.extend(_validate_text_quality_report(text_quality_data))

    connected: List[ConnectedMotor] = []

    if salvable_data:
        connected.extend(_connected_previous_motors(salvable_data))

    if text_quality_data:
        connected.extend(_connected_text_quality_motors(text_quality_data))

    ids = [m.id for m in connected]
    duplicate_ids = sorted({x for x in ids if ids.count(x) > 1})
    if duplicate_ids:
        defects.append("duplicate_connected_motor_ids:" + ",".join(duplicate_ids))

    previous_count = len([m for m in connected if m.source_phase == "5.12A.1"])
    text_count = len([m for m in connected if m.source_phase == "5.12B"])
    total = len(connected)

    if previous_count != 11:
        defects.append(f"connected_previous_motors_not_11:{previous_count}")

    if text_count != 12:
        defects.append(f"connected_text_quality_motors_not_12:{text_count}")

    if total != 23:
        defects.append(f"total_ready_connected_motors_not_23:{total}")

    # Dopo aver collegato i 12 testuali:
    # prima: 64 controlli atomici, 63 da ricreare, 1 da verificare
    # ora: 12 ricostruiti/collegati, 51 ancora da ricreare, 1 da verificare
    remaining_atomic_controls = {
        "atomic_controls_total_from_5_12a1": 64,
        "ready_connected_textual_controls": 12,
        "still_to_recreate": 51,
        "still_to_verify": 1,
    }

    approved = not defects

    return RegistryBridgeResult(
        phase=PHASE,
        ready_label=READY_LABEL if approved else None,
        status="PASS" if approved else "FAIL",
        approved=approved,
        total_ready_connected_motors=total,
        previous_salvable_motors=previous_count,
        new_text_quality_motors=text_count,
        connected_motors=connected,
        remaining_atomic_controls=remaining_atomic_controls,
        defects=defects,
        warnings=warnings,
        scope_guard={
            "created_new_motors": False,
            "connected_existing_5_12b_motors": True,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "deleted_existing_files": False,
            "registry_bridge_only": True,
        },
    )


def registry_bridge_to_dict(result: RegistryBridgeResult) -> Dict[str, Any]:
    return asdict(result)
