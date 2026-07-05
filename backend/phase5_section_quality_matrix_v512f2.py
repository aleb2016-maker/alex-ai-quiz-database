#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

PHASE = "5.12F.2"
READY_LABEL = "SECTION_QUALITY_SELECTION_MATRIX_WITH_ADVANCED_LANGUAGE_V512F2_READY"

REGISTRY_59_REPORT = REPORTS_DIR / "phase5_12f1_quality_registry_59_connected_v1.json"


@dataclass
class SectionMatrixResult:
    phase: str
    ready_label: Optional[str]
    status: str
    approved: bool
    registry_total_motors: int
    detected_groups: Dict[str, Any]
    sections: Dict[str, Any]
    defects: List[str]
    warnings: List[str]
    scope_guard: Dict[str, Any]


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _unique(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if item and item not in seen:
            seen.add(item)
            out.append(item)
    return out


def _motor_number(motor_id: str) -> Optional[int]:
    match = re.search(r"qm_(\d+)", str(motor_id))
    return int(match.group(1)) if match else None


def _classify_motors(connected: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    foundation: List[str] = []
    textual: List[str] = []
    didactic: List[str] = []
    card_summary_source: List[str] = []
    test_quiz: List[str] = []
    advanced_language: List[str] = []

    for motor in connected:
        mid = str(motor.get("id") or "")
        source_phase = str(motor.get("source_phase") or "")
        category = str(motor.get("category") or "").lower()
        title = str(motor.get("title") or "").lower()
        num = _motor_number(mid)

        if source_phase == "5.12F" or "advanced_language" in category:
            advanced_language.append(mid)
        elif source_phase == "5.12E" or "test_quiz" in category:
            test_quiz.append(mid)
        elif source_phase == "5.12D" or "card_summary_source" in category:
            card_summary_source.append(mid)
        elif source_phase == "5.12C" or "didactic" in category or "didattic" in category:
            didactic.append(mid)
        elif source_phase == "5.12B" or "text" in category or "testuale" in title:
            textual.append(mid)
        elif num is not None and 1 <= num <= 12:
            textual.append(mid)
        elif num is not None and 13 <= num <= 22:
            didactic.append(mid)
        elif num is not None and 23 <= num <= 32:
            card_summary_source.append(mid)
        elif num is not None and 33 <= num <= 44:
            test_quiz.append(mid)
        elif num is not None and 61 <= num <= 64:
            advanced_language.append(mid)
        else:
            foundation.append(mid)

    return {
        "foundation": _unique(foundation),
        "textual_universal": _unique(textual),
        "didactic_universal": _unique(didactic),
        "card_summary_source_specific": _unique(card_summary_source),
        "test_quiz_specific": _unique(test_quiz),
        "advanced_language_universal": _unique(advanced_language),
    }


def _summary_source_ids(card_ids: List[str]) -> List[str]:
    return _unique([mid for mid in card_ids if _motor_number(mid) in {27, 28, 29, 30, 31}])


def _validate_ids_exist(section: str, ids: List[str], available: Set[str], defects: List[str]) -> None:
    missing = [x for x in ids if x not in available]
    if missing:
        defects.append(f"{section}_references_missing_motor_ids:" + ",".join(missing))


def _validate_no_duplicates(section: str, ids: List[str], defects: List[str]) -> None:
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        defects.append(f"{section}_has_duplicate_motor_ids:" + ",".join(duplicates))


def build_section_matrix() -> SectionMatrixResult:
    data = _load_json(REGISTRY_59_REPORT)
    defects: List[str] = []
    warnings: List[str] = []
    connected: List[Dict[str, Any]] = []

    if not data:
        defects.append("registry_59_report_missing_or_invalid")
        registry_total = 0
    else:
        registry_total = int(data.get("total_ready_connected_motors", 0))

        if data.get("status") != "PASS":
            defects.append("registry_59_status_not_pass")
        if data.get("approved") is not True:
            defects.append("registry_59_not_approved")
        if data.get("ready_label") != "QUALITY_REGISTRY_59_MOTORS_CONNECTED_V512F1":
            defects.append("registry_59_ready_label_missing")
        if registry_total != 59:
            defects.append(f"registry_59_total_not_59:{registry_total}")

        connected = list(data.get("connected_motors") or [])

        if len(connected) != 59:
            defects.append(f"registry_59_connected_motors_list_not_59:{len(connected)}")
        if data.get("defects"):
            defects.append("registry_59_has_defects")

    available_ids = {str(m.get("id")) for m in connected}
    groups = _classify_motors(connected)

    foundation = groups["foundation"]
    textual = groups["textual_universal"]
    didactic = groups["didactic_universal"]
    card_source = groups["card_summary_source_specific"]
    summary_source = _summary_source_ids(card_source)
    quiz_specific = groups["test_quiz_specific"]
    advanced = groups["advanced_language_universal"]

    expected = {
        "foundation": 11,
        "textual": 12,
        "didactic": 10,
        "card_summary_source": 10,
        "summary_source": 5,
        "test_quiz_specific": 12,
        "advanced_language": 4,
    }

    actual = {
        "foundation": len(foundation),
        "textual": len(textual),
        "didactic": len(didactic),
        "card_summary_source": len(card_source),
        "summary_source": len(summary_source),
        "test_quiz_specific": len(quiz_specific),
        "advanced_language": len(advanced),
    }

    for key, exp in expected.items():
        if actual[key] != exp:
            defects.append(f"{key}_group_not_{exp}:{actual[key]}")

    card_active = _unique(foundation + textual + didactic + card_source + advanced)
    summary_active = _unique(foundation + textual + didactic + summary_source + advanced)
    study_active = _unique(foundation + textual + didactic + advanced)
    test_active = _unique(foundation + textual + didactic + quiz_specific + advanced)

    sections: Dict[str, Any] = {
        "card": {
            "description": "Card usa foundation + testuali + didattici + Card/Riassunto/Fonti + linguistici avanzati.",
            "active_motor_ids": card_active,
            "expected_active_count": len(card_active),
        },
        "summary": {
            "description": "Riassunto usa foundation + testuali + didattici + riassunto/fonti + linguistici avanzati.",
            "active_motor_ids": summary_active,
            "expected_active_count": len(summary_active),
        },
        "study_questions": {
            "description": "Domande studio usa foundation + testuali + didattici + linguistici avanzati.",
            "active_motor_ids": study_active,
            "expected_active_count": len(study_active),
        },
        "test_quiz": {
            "description": "Test/Quiz usa foundation + testuali + didattici + Test/Quiz specifici + linguistici avanzati.",
            "active_motor_ids": test_active,
            "expected_active_count": len(test_active),
        },
    }

    for name, section in sections.items():
        active = list(section["active_motor_ids"])
        _validate_no_duplicates(name, active, defects)
        _validate_ids_exist(name, active, available_ids, defects)

    if not set(advanced).issubset(set(card_active)):
        defects.append("card_missing_advanced_language_motors")
    if not set(advanced).issubset(set(summary_active)):
        defects.append("summary_missing_advanced_language_motors")
    if not set(advanced).issubset(set(study_active)):
        defects.append("study_questions_missing_advanced_language_motors")
    if not set(advanced).issubset(set(test_active)):
        defects.append("test_quiz_missing_advanced_language_motors")

    if set(quiz_specific) & set(card_active):
        defects.append("card_includes_test_quiz_specific_motors")
    if set(quiz_specific) & set(summary_active):
        defects.append("summary_includes_test_quiz_specific_motors")
    if set(quiz_specific) & set(study_active):
        defects.append("study_questions_includes_test_quiz_specific_motors")

    approved = not defects

    return SectionMatrixResult(
        phase=PHASE,
        ready_label=READY_LABEL if approved else None,
        status="PASS" if approved else "FAIL",
        approved=approved,
        registry_total_motors=registry_total,
        detected_groups={
            "foundation_count": len(foundation),
            "textual_universal_count": len(textual),
            "didactic_universal_count": len(didactic),
            "card_summary_source_specific_count": len(card_source),
            "summary_source_specific_count": len(summary_source),
            "test_quiz_specific_count": len(quiz_specific),
            "advanced_language_universal_count": len(advanced),
            "foundation_ids": foundation,
            "textual_universal_ids": textual,
            "didactic_universal_ids": didactic,
            "card_summary_source_specific_ids": card_source,
            "summary_source_specific_ids": summary_source,
            "test_quiz_specific_ids": quiz_specific,
            "advanced_language_universal_ids": advanced,
        },
        sections=sections,
        defects=defects,
        warnings=warnings,
        scope_guard={
            "created_new_motors": False,
            "changed_existing_59_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "matrix_only": True,
            "advanced_language_added_to_card": True,
            "advanced_language_added_to_summary": True,
            "advanced_language_added_to_study_questions": True,
            "advanced_language_added_to_test_quiz": True,
            "card_excludes_test_quiz_specific_motors": True,
            "summary_excludes_test_quiz_specific_motors": True,
            "study_questions_excludes_test_quiz_specific_motors": True,
            "test_quiz_uses_test_quiz_specific_motors": True,
        },
    )


def section_matrix_to_dict(result: SectionMatrixResult) -> Dict[str, Any]:
    return asdict(result)
