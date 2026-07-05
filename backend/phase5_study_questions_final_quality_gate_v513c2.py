#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13C.2 — STUDY QUESTIONS FINAL QUALITY GATE

Scopo:
- validare la qualità finale reale delle Domande studio;
- usare come base il risultato reale già prodotto dalla pipeline;
- verificare che la route 51 sia presente nel quality_report;
- bloccare genericità, fallback/demo, frasi spezzate, duplicati, output vuoti o contaminati.

Questo modulo NON modifica UI/PDF/app.
È un gate di qualità finale.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, Iterable, List, Tuple


EXPECTED_ROUTE_TOTAL = 51
EXPECTED_STUDY_QUALITY_CONTROLS = 43
EXPECTED_SELECTOR_ORCHESTRATOR = 8
MIN_STUDY_QUESTIONS = 4
MIN_QUESTION_CHARS = 42
MIN_ANSWER_CHARS = 75


FORBIDDEN_FRAGMENTS = [
    "fallback",
    "demo",
    "lorem ipsum",
    "test placeholder",
    "placeholder",
    "knowledge_base_json",
    "documento analizzato?",
    "documento analizzato",
    "contenuto generico",
    "argomento principale del documento",
    "qual è l'argomento principale",
    "qual è il tema principale",
    "cose importanti",
    "varie cose",
    "diversi aspetti importanti",
    "boh",
    "n/a",
    "undefined",
    "null",
    "[object object]",
]

BROKEN_ENDINGS = {
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "o", "ma", "che", "il", "lo", "la", "i", "gli", "le",
    "un", "uno", "una", "del", "della", "dei", "degli", "delle",
}

MOJIBAKE_FRAGMENTS = ["Ã", "Â", "�", "â€™", "â€œ", "â€"]


@dataclass
class StudyQuestionQualityItem:
    index: int
    question_id: str
    domanda_chars: int
    risposta_guida_chars: int
    micro_concetti_count: int
    defects: List[str]
    warnings: List[str]


@dataclass
class StudyQuestionsFinalQualityReport:
    phase: str
    status: str
    approved: bool
    source_status: str
    study_questions_count: int
    route_total: int
    study_quality_controls: int
    selector_orchestrator: int
    missing_motor_ids: List[str]
    duplicate_pairs: List[str]
    near_duplicate_pairs: List[str]
    items: List[Dict[str, Any]]
    defects: List[str]
    warnings: List[str]


def _norm(value: Any) -> str:
    return " ".join(str(value or "").strip().lower().split())


def _text(value: Any) -> str:
    return str(value or "").strip()


def _collect_texts(item: Dict[str, Any]) -> Tuple[str, str]:
    domanda = _text(
        item.get("domanda")
        or item.get("question")
        or item.get("titolo")
        or ""
    )
    risposta = _text(
        item.get("risposta_guida")
        or item.get("guide_answer")
        or item.get("answer_guide")
        or item.get("risposta")
        or ""
    )
    return domanda, risposta


def _contains_forbidden(text: str) -> List[str]:
    low = _norm(text)
    return [fragment for fragment in FORBIDDEN_FRAGMENTS if fragment in low]


def _contains_mojibake(text: str) -> List[str]:
    return [fragment for fragment in MOJIBAKE_FRAGMENTS if fragment in text]


def _last_word(text: str) -> str:
    cleaned = _norm(text).rstrip(".?!:;,-")
    if not cleaned:
        return ""
    return cleaned.split()[-1]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    return []


def _validate_item(index: int, item: Dict[str, Any]) -> StudyQuestionQualityItem:
    defects: List[str] = []
    warnings: List[str] = []

    domanda, risposta = _collect_texts(item)
    question_id = _text(item.get("question_id") or item.get("id") or f"study_question_{index:03d}")

    if len(domanda) < MIN_QUESTION_CHARS:
        defects.append(f"domanda_troppo_corta:{len(domanda)}")

    if len(risposta) < MIN_ANSWER_CHARS:
        defects.append(f"risposta_guida_troppo_corta:{len(risposta)}")

    if not domanda.endswith("?"):
        defects.append("domanda_non_termina_con_punto_interrogativo")

    for label, value in [("domanda", domanda), ("risposta_guida", risposta)]:
        if not value:
            defects.append(f"{label}_vuota")
            continue

        forbidden = _contains_forbidden(value)
        if forbidden:
            defects.append(f"{label}_contiene_frasi_vietate:{','.join(forbidden)}")

        mojibake = _contains_mojibake(value)
        if mojibake:
            defects.append(f"{label}_contiene_mojibake:{','.join(mojibake)}")

        if _last_word(value) in BROKEN_ENDINGS:
            defects.append(f"{label}_finale_sospetto:{_last_word(value)}")

        if "  " in value:
            defects.append(f"{label}_spazi_doppi")

        if value.count("?") > 1:
            defects.append(f"{label}_troppi_punti_interrogativi")

    micro_concetti = _as_list(item.get("micro_concetti"))
    if len(micro_concetti) < 2:
        defects.append("micro_concetti_insufficienti")

    if not _as_list(item.get("fonte_pagine")):
        defects.append("fonte_pagine_assenti")

    if "fatto_origine" not in item or not _text(item.get("fatto_origine")):
        defects.append("fatto_origine_assente")

    return StudyQuestionQualityItem(
        index=index,
        question_id=question_id,
        domanda_chars=len(domanda),
        risposta_guida_chars=len(risposta),
        micro_concetti_count=len(micro_concetti),
        defects=defects,
        warnings=warnings,
    )


def evaluate_study_questions_final_quality(result: Dict[str, Any]) -> Dict[str, Any]:
    defects: List[str] = []
    warnings: List[str] = []
    duplicate_pairs: List[str] = []
    near_duplicate_pairs: List[str] = []

    approved = bool(result.get("approved"))
    source_status = _text(result.get("status"))

    if not approved:
        defects.append("source_result_not_approved")

    if source_status not in {"APPROVED", "PASS", "OK"}:
        defects.append(f"source_status_not_approved:{source_status}")

    if result.get("errors"):
        defects.append(f"source_errors_not_empty:{result.get('errors')}")

    if result.get("warnings"):
        defects.append(f"source_warnings_not_empty:{result.get('warnings')}")

    study_questions = _as_list(result.get("domande_studio") or result.get("study_questions"))

    if len(study_questions) < MIN_STUDY_QUESTIONS:
        defects.append(f"study_questions_too_few:{len(study_questions)}")

    quality_report = result.get("quality_report") or {}
    if not isinstance(quality_report, dict) or not quality_report:
        defects.append("quality_report_missing_or_empty")
        quality_report = {}

    real_connection = quality_report.get("study_questions_real_connection_v513c1") or {}
    if not isinstance(real_connection, dict) or not real_connection:
        defects.append("study_questions_real_connection_v513c1_missing")
        real_connection = {}

    route_total = int(real_connection.get("resolved_route_total") or 0)
    study_quality_controls = int(real_connection.get("resolved_study_quality_controls") or 0)
    selector_orchestrator = int(real_connection.get("resolved_selector_orchestrator") or 0)
    missing_motor_ids = _as_list(real_connection.get("missing_motor_ids"))

    if route_total != EXPECTED_ROUTE_TOTAL:
        defects.append(f"route_total_expected_51_found_{route_total}")

    if study_quality_controls != EXPECTED_STUDY_QUALITY_CONTROLS:
        defects.append(f"study_quality_controls_expected_43_found_{study_quality_controls}")

    if selector_orchestrator != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(f"selector_orchestrator_expected_8_found_{selector_orchestrator}")

    if missing_motor_ids:
        defects.append(f"missing_motor_ids:{missing_motor_ids}")

    if len(_as_list(real_connection.get("executed_motor_ids"))) != EXPECTED_ROUTE_TOTAL:
        defects.append(
            f"executed_motor_ids_expected_51_found_{len(_as_list(real_connection.get('executed_motor_ids')))}"
        )

    items: List[Dict[str, Any]] = []
    question_texts: List[Tuple[int, str]] = []
    answer_texts: List[Tuple[int, str]] = []

    for index, item in enumerate(study_questions, start=1):
        if not isinstance(item, dict):
            defects.append(f"study_question_{index}_not_dict")
            continue

        item_report = _validate_item(index, item)
        items.append(asdict(item_report))

        defects.extend(f"item_{index}:{defect}" for defect in item_report.defects)
        warnings.extend(f"item_{index}:{warning}" for warning in item_report.warnings)

        domanda, risposta = _collect_texts(item)
        question_texts.append((index, domanda))
        answer_texts.append((index, risposta))

    seen_questions: Dict[str, int] = {}
    for index, domanda in question_texts:
        key = _norm(domanda)
        if key in seen_questions:
            duplicate_pairs.append(f"domande:{seen_questions[key]}-{index}")
        else:
            seen_questions[key] = index

    for collection_name, collection in [("domande", question_texts), ("risposte", answer_texts)]:
        for pos_a in range(len(collection)):
            idx_a, text_a = collection[pos_a]
            for pos_b in range(pos_a + 1, len(collection)):
                idx_b, text_b = collection[pos_b]
                if not text_a or not text_b:
                    continue
                ratio = _similarity(text_a, text_b)
                if ratio >= 0.92:
                    near_duplicate_pairs.append(
                        f"{collection_name}:{idx_a}-{idx_b}:similarity={ratio:.3f}"
                    )

    if duplicate_pairs:
        defects.append(f"duplicate_pairs:{duplicate_pairs}")

    if near_duplicate_pairs:
        defects.append(f"near_duplicate_pairs:{near_duplicate_pairs}")

    status = (
        "PASS - Fase 5.13C.2: STUDY_QUESTIONS_FINAL_QUALITY_GATE_READY"
        if not defects and not warnings
        else "FAIL - Fase 5.13C.2: STUDY_QUESTIONS_FINAL_QUALITY_GATE_NOT_READY"
    )

    report = StudyQuestionsFinalQualityReport(
        phase="5.13C.2",
        status=status,
        approved=approved,
        source_status=source_status,
        study_questions_count=len(study_questions),
        route_total=route_total,
        study_quality_controls=study_quality_controls,
        selector_orchestrator=selector_orchestrator,
        missing_motor_ids=[str(item) for item in missing_motor_ids],
        duplicate_pairs=duplicate_pairs,
        near_duplicate_pairs=near_duplicate_pairs,
        items=items,
        defects=defects,
        warnings=warnings,
    )

    return asdict(report)
