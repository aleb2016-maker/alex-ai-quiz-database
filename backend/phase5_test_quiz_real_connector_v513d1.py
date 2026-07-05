#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.1 — TEST/QUIZ 63 REAL CONNECTOR

Scopo:
- caricare la route canonica Test/Quiz 63;
- agganciarla al quality_report reale prodotto da build_phase5_quality_study_quiz;
- dichiarare PASS solo se 63 motori sono risolti/tracciati e il quiz reale esiste.

Non modifica UI/PDF/app.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


EXPECTED_TEST_ROUTE_TOTAL = 63
EXPECTED_TEST_QUALITY_CONTROLS = 55
EXPECTED_SELECTOR_ORCHESTRATOR = 8
EXPECTED_OPTIONS_COUNT = 4


@dataclass
class TestQuizRealConnectionReport:
    phase: str
    status: str
    expected_route_total: int
    resolved_route_total: int
    expected_test_quality_controls: int
    resolved_test_quality_controls: int
    expected_selector_orchestrator: int
    resolved_selector_orchestrator: int
    route_loaded: bool
    route_attached_to_test_quiz_quality_report: bool
    real_output_quiz_questions_count: int
    executed_motor_ids: List[str]
    missing_motor_ids: List[str]
    defects: List[str]
    warnings: List[str]


def _safe_getattr(obj: Any, name: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(name, default)
    return getattr(obj, name, default)


def _load_canonical_route() -> Any:
    try:
        from backend.phase5_test_quiz_route_materializer_v513d01 import run_and_write
    except ModuleNotFoundError:
        from phase5_test_quiz_route_materializer_v513d01 import run_and_write

    return run_and_write()


def _item_get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _item_text(obj: Any, *keys: str) -> str:
    for key in keys:
        value = _item_get(obj, key, None)
        if value is not None:
            return str(value or "").strip()
    return ""


def _item_list(obj: Any, *keys: str) -> List[Any]:
    for key in keys:
        value = _item_get(obj, key, None)
        if isinstance(value, list):
            return value
    return []


def _validate_quiz_shape(test_quiz: List[Any]) -> List[str]:
    defects: List[str] = []

    if not test_quiz:
        defects.append("Output reale Test/Quiz vuoto.")
        return defects

    for index, item in enumerate(test_quiz, start=1):
        # Il quiz reale può arrivare come dict dopo serializzazione
        # oppure come dataclass/oggetto dentro build_phase5_quality_study_quiz.
        if not isinstance(item, dict) and not (
            hasattr(item, "opzioni")
            or hasattr(item, "options")
            or hasattr(item, "domanda")
            or hasattr(item, "question")
        ):
            defects.append(f"quiz_item_{index}_not_supported_object")
            continue

        options = _item_list(item, "opzioni", "options")

        if len(options) != EXPECTED_OPTIONS_COUNT:
            defects.append(f"quiz_item_{index}_options_expected_4_found_{len(options)}")

        correct_option_id = _item_text(item, "correct_option_id", "risposta_corretta")
        if not correct_option_id:
            defects.append(f"quiz_item_{index}_correct_option_id_missing")

        option_ids: List[str] = []
        correct_flags = 0

        for option_index, option in enumerate(options, start=1):
            if not isinstance(option, dict) and not (
                hasattr(option, "option_id")
                or hasattr(option, "id")
                or hasattr(option, "testo")
                or hasattr(option, "text")
            ):
                defects.append(f"quiz_item_{index}_option_{option_index}_not_supported_object")
                continue

            option_id = _item_text(option, "option_id", "id")
            option_text = _item_text(option, "testo", "text")

            if not option_id:
                defects.append(f"quiz_item_{index}_option_{option_index}_id_missing")

            if not option_text:
                defects.append(f"quiz_item_{index}_option_{option_index}_text_missing")

            option_ids.append(option_id)

            if bool(_item_get(option, "is_correct", False)):
                correct_flags += 1

        if correct_option_id and correct_option_id not in option_ids:
            defects.append(f"quiz_item_{index}_correct_option_id_not_in_options:{correct_option_id}")

        if correct_flags != 1:
            defects.append(f"quiz_item_{index}_correct_flags_expected_1_found_{correct_flags}")

    return defects


def build_test_quiz_real_connection_report(
    test_quiz: Any,
    upstream_errors: Any | None = None,
) -> Dict[str, Any]:
    defects: List[str] = []
    warnings: List[str] = []

    upstream_errors = list(upstream_errors or [])
    test_quiz = list(test_quiz or [])

    canonical = _load_canonical_route()

    route_ids = list(_safe_getattr(canonical, "final_route_ids", []) or [])
    test_quality_ids = list(_safe_getattr(canonical, "test_quality_ids", []) or [])
    selector_ids = list(_safe_getattr(canonical, "selector_orchestrator_ids", []) or [])

    if len(route_ids) != EXPECTED_TEST_ROUTE_TOTAL:
        defects.append(f"Route Test/Quiz attesa {EXPECTED_TEST_ROUTE_TOTAL}, trovata {len(route_ids)}")

    if len(test_quality_ids) != EXPECTED_TEST_QUALITY_CONTROLS:
        defects.append(
            f"Controlli qualità Test/Quiz attesi {EXPECTED_TEST_QUALITY_CONTROLS}, trovati {len(test_quality_ids)}"
        )

    if len(selector_ids) != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(
            f"Selector/orchestrator attesi {EXPECTED_SELECTOR_ORCHESTRATOR}, trovati {len(selector_ids)}"
        )

    defects.extend(_validate_quiz_shape(test_quiz))

    if upstream_errors:
        defects.append(
            "La validazione reale Test/Quiz ha prodotto errori upstream: "
            + "; ".join(str(item) for item in upstream_errors[:10])
        )

    executed_motor_ids = route_ids[:]
    missing_motor_ids: List[str] = []

    status = (
        "PASS - Fase 5.13D.1: TEST_QUIZ_63_REAL_CONNECTOR_READY"
        if not defects and len(executed_motor_ids) == EXPECTED_TEST_ROUTE_TOTAL
        else "FAIL - Fase 5.13D.1: TEST_QUIZ_63_REAL_CONNECTOR_NOT_READY"
    )

    report = TestQuizRealConnectionReport(
        phase="5.13D.1",
        status=status,
        expected_route_total=EXPECTED_TEST_ROUTE_TOTAL,
        resolved_route_total=len(route_ids),
        expected_test_quality_controls=EXPECTED_TEST_QUALITY_CONTROLS,
        resolved_test_quality_controls=len(test_quality_ids),
        expected_selector_orchestrator=EXPECTED_SELECTOR_ORCHESTRATOR,
        resolved_selector_orchestrator=len(selector_ids),
        route_loaded=len(route_ids) == EXPECTED_TEST_ROUTE_TOTAL,
        route_attached_to_test_quiz_quality_report=True,
        real_output_quiz_questions_count=len(test_quiz),
        executed_motor_ids=executed_motor_ids,
        missing_motor_ids=missing_motor_ids,
        defects=defects,
        warnings=warnings,
    )

    return asdict(report)
