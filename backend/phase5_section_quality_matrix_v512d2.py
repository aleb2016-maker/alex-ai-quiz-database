#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12D.2 — SECTION QUALITY SELECTION MATRIX

Obiettivo:
- definire quali motori qualità attivare per ogni sezione:
  Card, Riassunto, Test/Quiz, Domande studio.
- usare il registry da 43 motori pronti e collegati della Fase 5.12D.1.
- confermare che la Card usa anche i motori universali testuali e didattici.
- confermare che la Card NON usa motori quiz/test specifici.

Questo modulo NON crea nuovi motori.
Questo modulo NON modifica i 43 motori già chiusi.
Questo modulo NON modifica la pipeline 5.11.
Questo modulo NON modifica UI/PDF/CSS/app.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

PHASE = "5.12D.2"
READY_LABEL = "SECTION_QUALITY_SELECTION_MATRIX_V512D2_READY"

REGISTRY_43_REPORT = REPORTS_DIR / "phase5_12d1_quality_registry_43_connected_v1.json"


FUTURE_QUIZ_SPECIFIC_IDS = [
    "qm_033_test_quiz_test_separato_da_card_riassunto_domande_studio",
    "qm_034_test_quiz_opzioni_interne_validate",
    "qm_035_test_quiz_opzioni_visibili_pulite",
    "qm_036_test_quiz_risposta_corretta_interna",
    "qm_037_test_quiz_risposta_corretta_visibile",
    "qm_038_test_quiz_mappa_sicura_tra_risposta_interna_e_visibile",
    "qm_039_test_quiz_quattro_opzioni_per_domanda",
    "qm_040_test_quiz_risposta_corretta_presente_tra_le_opzioni",
    "qm_041_test_quiz_distrattori_forti",
    "qm_042_test_quiz_niente_opzioni_duplicate_nella_stessa_domanda",
    "qm_043_test_quiz_niente_ripetizioni_globali_eccessive",
    "qm_044_test_quiz_compatibilita_bridge_quiz_v3_5b",
]


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
    if not match:
        return None
    return int(match.group(1))


def _classify_motors(connected: List[Dict[str, Any]]) -> Dict[str, List[str]]:
    foundation: List[str] = []
    textual: List[str] = []
    didactic: List[str] = []
    card_summary_source: List[str] = []

    for motor in connected:
        mid = str(motor.get("id") or "")
        source_phase = str(motor.get("source_phase") or "")
        category = str(motor.get("category") or "").lower()
        title = str(motor.get("title") or "").lower()
        num = _motor_number(mid)

        if source_phase == "5.12D" or "card_summary_source" in category:
            card_summary_source.append(mid)
            continue

        if source_phase == "5.12C" or "didactic" in category or "didattic" in category:
            didactic.append(mid)
            continue

        if source_phase == "5.12B" or "text" in category or "testuale" in title:
            textual.append(mid)
            continue

        if num is not None and 1 <= num <= 12:
            textual.append(mid)
        elif num is not None and 13 <= num <= 22:
            didactic.append(mid)
        elif num is not None and 23 <= num <= 32:
            card_summary_source.append(mid)
        else:
            foundation.append(mid)

    return {
        "foundation": _unique(foundation),
        "textual_universal": _unique(textual),
        "didactic_universal": _unique(didactic),
        "card_summary_source_specific": _unique(card_summary_source),
    }


def _summary_source_ids(card_ids: List[str]) -> List[str]:
    wanted_numbers = {27, 28, 29, 30, 31}
    out = []
    for mid in card_ids:
        if _motor_number(mid) in wanted_numbers:
            out.append(mid)
    return _unique(out)


def _card_only_ids(card_ids: List[str]) -> List[str]:
    wanted_numbers = {23, 24, 25, 26, 32}
    out = []
    for mid in card_ids:
        if _motor_number(mid) in wanted_numbers:
            out.append(mid)
    return _unique(out)


def _validate_ids_exist(section: str, ids: List[str], available: Set[str], defects: List[str]) -> None:
    missing = [x for x in ids if x not in available]
    if missing:
        defects.append(f"{section}_references_missing_motor_ids:" + ",".join(missing))


def _validate_no_duplicates(section: str, ids: List[str], defects: List[str]) -> None:
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    if duplicates:
        defects.append(f"{section}_has_duplicate_motor_ids:" + ",".join(duplicates))


def build_section_matrix() -> SectionMatrixResult:
    data = _load_json(REGISTRY_43_REPORT)
    defects: List[str] = []
    warnings: List[str] = []

    connected: List[Dict[str, Any]] = []

    if not data:
        defects.append("registry_43_report_missing_or_invalid")
        registry_total = 0
    else:
        registry_total = int(data.get("total_ready_connected_motors", 0))

        if data.get("status") != "PASS":
            defects.append("registry_43_status_not_pass")

        if data.get("approved") is not True:
            defects.append("registry_43_not_approved")

        if data.get("ready_label") != "QUALITY_REGISTRY_43_MOTORS_CONNECTED_V512D1":
            defects.append("registry_43_ready_label_missing")

        if registry_total != 43:
            defects.append(f"registry_43_total_not_43:{registry_total}")

        connected = list(data.get("connected_motors") or [])

        if len(connected) != 43:
            defects.append(f"registry_43_connected_motors_list_not_43:{len(connected)}")

        if data.get("defects"):
            defects.append("registry_43_has_defects")

    available_ids = {str(m.get("id")) for m in connected}
    groups = _classify_motors(connected)

    foundation_ids = groups["foundation"]
    textual_ids = groups["textual_universal"]
    didactic_ids = groups["didactic_universal"]
    card_source_ids = groups["card_summary_source_specific"]
    summary_source_ids = _summary_source_ids(card_source_ids)
    card_only_ids = _card_only_ids(card_source_ids)

    if len(textual_ids) != 12:
        defects.append(f"textual_universal_group_not_12:{len(textual_ids)}")

    if len(didactic_ids) != 10:
        defects.append(f"didactic_universal_group_not_10:{len(didactic_ids)}")

    if len(card_source_ids) != 10:
        defects.append(f"card_summary_source_group_not_10:{len(card_source_ids)}")

    if len(summary_source_ids) != 5:
        defects.append(f"summary_source_group_not_5:{len(summary_source_ids)}")

    if len(card_only_ids) != 5:
        defects.append(f"card_only_group_not_5:{len(card_only_ids)}")

    card_active = _unique(foundation_ids + textual_ids + didactic_ids + card_source_ids)
    summary_active = _unique(foundation_ids + textual_ids + didactic_ids + summary_source_ids)
    study_active = _unique(foundation_ids + textual_ids + didactic_ids)
    test_active_current = _unique(foundation_ids + textual_ids + didactic_ids)

    sections: Dict[str, Any] = {
        "card": {
            "description": "Card usa foundation, motori testuali universali, motori didattici e tutti i motori Card/Riassunto/Fonti.",
            "active_motor_ids": card_active,
            "required_groups": {
                "foundation": foundation_ids,
                "textual_universal": textual_ids,
                "didactic_universal": didactic_ids,
                "card_summary_source_specific": card_source_ids,
            },
            "excluded_until_quiz_phase": FUTURE_QUIZ_SPECIFIC_IDS,
            "expected_active_count": len(card_active),
        },
        "summary": {
            "description": "Riassunto usa foundation, motori testuali universali, motori didattici e motori specifici riassunto/fonti.",
            "active_motor_ids": summary_active,
            "required_groups": {
                "foundation": foundation_ids,
                "textual_universal": textual_ids,
                "didactic_universal": didactic_ids,
                "summary_source_specific": summary_source_ids,
            },
            "expected_active_count": len(summary_active),
        },
        "study_questions": {
            "description": "Domande studio usa foundation, motori testuali universali e motori didattici.",
            "active_motor_ids": study_active,
            "required_groups": {
                "foundation": foundation_ids,
                "textual_universal": textual_ids,
                "didactic_universal": didactic_ids,
            },
            "expected_active_count": len(study_active),
        },
        "test_quiz": {
            "description": "Test/Quiz usa foundation, motori testuali universali e motori didattici ora; i motori quiz specifici saranno aggiunti dopo la loro ricostruzione.",
            "active_motor_ids": test_active_current,
            "required_groups_now": {
                "foundation": foundation_ids,
                "textual_universal": textual_ids,
                "didactic_universal": didactic_ids,
            },
            "future_quiz_specific_motor_ids": FUTURE_QUIZ_SPECIFIC_IDS,
            "expected_active_count_now": len(test_active_current),
        },
    }

    for section_name, section in sections.items():
        active = list(section["active_motor_ids"])
        _validate_no_duplicates(section_name, active, defects)
        _validate_ids_exist(section_name, active, available_ids, defects)

    if not set(textual_ids).issubset(set(sections["card"]["active_motor_ids"])):
        defects.append("card_missing_textual_universal_motors")

    if not set(didactic_ids).issubset(set(sections["card"]["active_motor_ids"])):
        defects.append("card_missing_didactic_universal_motors")

    if not set(card_source_ids).issubset(set(sections["card"]["active_motor_ids"])):
        defects.append("card_missing_card_summary_source_specific_motors")

    forbidden_in_card = set(FUTURE_QUIZ_SPECIFIC_IDS) & set(sections["card"]["active_motor_ids"])
    if forbidden_in_card:
        defects.append("card_includes_future_quiz_specific_motors:" + ",".join(sorted(forbidden_in_card)))

    approved = not defects

    return SectionMatrixResult(
        phase=PHASE,
        ready_label=READY_LABEL if approved else None,
        status="PASS" if approved else "FAIL",
        approved=approved,
        registry_total_motors=registry_total,
        detected_groups={
            "foundation_count": len(foundation_ids),
            "textual_universal_count": len(textual_ids),
            "didactic_universal_count": len(didactic_ids),
            "card_summary_source_specific_count": len(card_source_ids),
            "summary_source_specific_count": len(summary_source_ids),
            "card_only_specific_count": len(card_only_ids),
            "foundation_ids": foundation_ids,
            "textual_universal_ids": textual_ids,
            "didactic_universal_ids": didactic_ids,
            "card_summary_source_specific_ids": card_source_ids,
            "summary_source_specific_ids": summary_source_ids,
            "card_only_specific_ids": card_only_ids,
        },
        sections=sections,
        defects=defects,
        warnings=warnings,
        scope_guard={
            "created_new_motors": False,
            "changed_existing_43_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "matrix_only": True,
            "card_uses_universal_textual_motors": True,
            "card_uses_didactic_motors": True,
            "card_uses_card_summary_source_motors": True,
            "card_excludes_quiz_specific_motors_until_quiz_phase": True,
            "test_quiz_waits_for_future_quiz_specific_motors": True,
        },
    )


def section_matrix_to_dict(result: SectionMatrixResult) -> Dict[str, Any]:
    return asdict(result)
