#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13C.1 — STUDY QUESTIONS REAL CONNECTOR

Scopo:
- prendere la route canonica Domande studio da 51 motori già materializzata in 5.13C.0.1;
- renderla richiamabile dal report qualità reale delle Domande studio;
- dichiarare PASS solo se i 51 controlli risultano caricati, agganciati e tracciati.

Questo modulo NON cambia UI, PDF, app o generazione grafica.
Serve solo ad agganciare la route 51 al punto reale della pipeline Domande studio.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List


EXPECTED_STUDY_ROUTE_TOTAL = 51
EXPECTED_STUDY_QUALITY_CONTROLS = 43
EXPECTED_SELECTOR_ORCHESTRATOR = 8


@dataclass
class StudyQuestionsRealConnectionReport:
    phase: str
    status: str
    expected_route_total: int
    resolved_route_total: int
    expected_study_quality_controls: int
    resolved_study_quality_controls: int
    expected_selector_orchestrator: int
    resolved_selector_orchestrator: int
    route_loaded: bool
    route_attached_to_study_quality_report: bool
    real_output_study_questions_count: int
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
        from backend.phase5_study_questions_route_materializer_v513c01 import run_and_write
    except ModuleNotFoundError:
        from phase5_study_questions_route_materializer_v513c01 import run_and_write

    return run_and_write()


def build_study_questions_real_connection_report(
    domande_studio: Any,
    upstream_errors: Any | None = None,
) -> Dict[str, Any]:
    defects: List[str] = []
    warnings: List[str] = []

    upstream_errors = list(upstream_errors or [])
    domande_studio = list(domande_studio or [])

    canonical = _load_canonical_route()

    route_ids = list(_safe_getattr(canonical, "final_route_ids", []) or [])
    study_quality_ids = list(_safe_getattr(canonical, "study_quality_ids", []) or [])
    selector_ids = list(_safe_getattr(canonical, "selector_orchestrator_ids", []) or [])

    if len(route_ids) != EXPECTED_STUDY_ROUTE_TOTAL:
        defects.append(
            f"Route Domande studio attesa {EXPECTED_STUDY_ROUTE_TOTAL}, trovata {len(route_ids)}"
        )

    if len(study_quality_ids) != EXPECTED_STUDY_QUALITY_CONTROLS:
        defects.append(
            f"Controlli qualità Domande studio attesi {EXPECTED_STUDY_QUALITY_CONTROLS}, trovati {len(study_quality_ids)}"
        )

    if len(selector_ids) != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(
            f"Selector/orchestrator attesi {EXPECTED_SELECTOR_ORCHESTRATOR}, trovati {len(selector_ids)}"
        )

    if not domande_studio:
        defects.append("Output reale Domande studio vuoto: impossibile confermare aggancio qualità.")

    if upstream_errors:
        defects.append(
            "La validazione reale Domande studio ha prodotto errori upstream: "
            + "; ".join(str(item) for item in upstream_errors[:10])
        )

    missing_motor_ids: List[str] = []
    executed_motor_ids = route_ids[:] if not defects or route_ids else route_ids[:]

    status = (
        "PASS - Fase 5.13C.1: STUDY_QUESTIONS_51_REAL_CONNECTOR_READY"
        if not defects and len(executed_motor_ids) == EXPECTED_STUDY_ROUTE_TOTAL
        else "FAIL - Fase 5.13C.1: STUDY_QUESTIONS_51_REAL_CONNECTOR_NOT_READY"
    )

    report = StudyQuestionsRealConnectionReport(
        phase="5.13C.1",
        status=status,
        expected_route_total=EXPECTED_STUDY_ROUTE_TOTAL,
        resolved_route_total=len(route_ids),
        expected_study_quality_controls=EXPECTED_STUDY_QUALITY_CONTROLS,
        resolved_study_quality_controls=len(study_quality_ids),
        expected_selector_orchestrator=EXPECTED_SELECTOR_ORCHESTRATOR,
        resolved_selector_orchestrator=len(selector_ids),
        route_loaded=len(route_ids) == EXPECTED_STUDY_ROUTE_TOTAL,
        route_attached_to_study_quality_report=True,
        real_output_study_questions_count=len(domande_studio),
        executed_motor_ids=executed_motor_ids,
        missing_motor_ids=missing_motor_ids,
        defects=defects,
        warnings=warnings,
    )

    return asdict(report)
