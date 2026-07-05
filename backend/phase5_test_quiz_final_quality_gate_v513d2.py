#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.2 — TEST/QUIZ FINAL QUALITY GATE

Controlla:
- output reale approvato;
- route 63 nel quality_report;
- 4 opzioni per domanda;
- risposta corretta presente;
- un solo flag corretto;
- distrattori non vuoti, non duplicati, non uguali alla corretta;
- no "non non";
- no fallback/demo;
- no spiegazioni troppo corte;
- no contaminazioni grossolane.

Non modifica UI/PDF/app.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from difflib import SequenceMatcher
from typing import Any, Dict, List, Tuple


EXPECTED_ROUTE_TOTAL = 63
EXPECTED_TEST_QUALITY_CONTROLS = 55
EXPECTED_SELECTOR_ORCHESTRATOR = 8
EXPECTED_OPTIONS_COUNT = 4
MIN_QUIZ_QUESTIONS = 4
MIN_QUESTION_CHARS = 48
MIN_OPTION_CHARS = 18
MIN_EXPLANATION_CHARS = 90


FORBIDDEN_FRAGMENTS = [
    "fallback",
    "demo",
    "placeholder",
    "lorem ipsum",
    "knowledge_base_json",
    "documento analizzato",
    "argomento principale del documento",
    "qual è l'argomento principale",
    "boh",
    "n/a",
    "undefined",
    "null",
    "[object object]",
    "non non",
    "non  non",
]

MOJIBAKE_FRAGMENTS = ["Ã", "Â", "�", "â€™", "â€œ", "â€"]

BROKEN_ENDINGS = {
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "o", "ma", "che", "il", "lo", "la", "i", "gli", "le",
    "un", "uno", "una", "del", "della", "dei", "degli", "delle",
}


@dataclass
class QuizQualityItem:
    index: int
    question_id: str
    domanda_chars: int
    options_count: int
    explanation_chars: int
    correct_option_id: str
    defects: List[str]
    warnings: List[str]


@dataclass
class TestQuizFinalQualityReport:
    phase: str
    status: str
    approved: bool
    source_status: str
    quiz_questions_count: int
    route_total: int
    test_quality_controls: int
    selector_orchestrator: int
    missing_motor_ids: List[str]
    duplicate_pairs: List[str]
    near_duplicate_pairs: List[str]
    items: List[Dict[str, Any]]
    defects: List[str]
    warnings: List[str]


def _text(value: Any) -> str:
    return str(value or "").strip()


def _norm(value: Any) -> str:
    return " ".join(_text(value).lower().split())


def _as_list(value: Any) -> List[Any]:
    return value if isinstance(value, list) else []


def _last_word(text: str) -> str:
    cleaned = _norm(text).rstrip(".?!:;,-")
    if not cleaned:
        return ""
    return cleaned.split()[-1]


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _forbidden(text: str) -> List[str]:
    low = _norm(text)
    return [fragment for fragment in FORBIDDEN_FRAGMENTS if fragment in low]


def _mojibake(text: str) -> List[str]:
    return [fragment for fragment in MOJIBAKE_FRAGMENTS if fragment in text]


def _option_id(option: Dict[str, Any]) -> str:
    return _text(option.get("option_id") or option.get("id") or "")


def _option_text(option: Dict[str, Any]) -> str:
    return _text(option.get("testo") or option.get("text") or "")


def _validate_text(label: str, value: str, defects: List[str]) -> None:
    if not value:
        defects.append(f"{label}_vuoto")
        return

    forbidden = _forbidden(value)
    if forbidden:
        defects.append(f"{label}_contiene_frasi_vietate:{','.join(forbidden)}")

    mojibake = _mojibake(value)
    if mojibake:
        defects.append(f"{label}_contiene_mojibake:{','.join(mojibake)}")

    if _last_word(value) in BROKEN_ENDINGS:
        defects.append(f"{label}_finale_sospetto:{_last_word(value)}")

    if "  " in value:
        defects.append(f"{label}_spazi_doppi")


def _validate_quiz_item(index: int, item: Dict[str, Any]) -> QuizQualityItem:
    defects: List[str] = []
    warnings: List[str] = []

    question_id = _text(item.get("question_id") or item.get("id") or f"quiz_question_{index:03d}")
    domanda = _text(item.get("domanda") or item.get("question") or "")
    spiegazione = _text(item.get("spiegazione") or item.get("explanation") or "")
    correct_option_id = _text(item.get("correct_option_id") or item.get("risposta_corretta") or "")
    options = _as_list(item.get("opzioni") or item.get("options"))

    if len(domanda) < MIN_QUESTION_CHARS:
        defects.append(f"domanda_troppo_corta:{len(domanda)}")

    if not domanda.endswith("?"):
        defects.append("domanda_non_termina_con_punto_interrogativo")

    _validate_text("domanda", domanda, defects)

    if len(spiegazione) < MIN_EXPLANATION_CHARS:
        defects.append(f"spiegazione_troppo_corta:{len(spiegazione)}")

    _validate_text("spiegazione", spiegazione, defects)

    if len(options) != EXPECTED_OPTIONS_COUNT:
        defects.append(f"opzioni_attese_4_trovate_{len(options)}")

    if not correct_option_id:
        defects.append("correct_option_id_mancante")

    option_ids: List[str] = []
    option_texts: List[str] = []
    correct_flags = 0
    correct_text = ""

    for opt_index, option in enumerate(options, start=1):
        if not isinstance(option, dict):
            defects.append(f"opzione_{opt_index}_non_dict")
            continue

        oid = _option_id(option)
        txt = _option_text(option)

        option_ids.append(oid)
        option_texts.append(txt)

        if len(txt) < MIN_OPTION_CHARS:
            defects.append(f"opzione_{opt_index}_troppo_corta:{len(txt)}")

        _validate_text(f"opzione_{opt_index}", txt, defects)

        if bool(option.get("is_correct")):
            correct_flags += 1
            correct_text = txt

    if correct_option_id and correct_option_id not in option_ids:
        defects.append(f"correct_option_id_non_presente:{correct_option_id}")

    if correct_flags != 1:
        defects.append(f"correct_flags_attesi_1_trovati_{correct_flags}")

    if len(set(option_ids)) != len(option_ids):
        defects.append("option_id_duplicati")

    normalized_options = [_norm(txt) for txt in option_texts if txt]
    if len(set(normalized_options)) != len(normalized_options):
        defects.append("opzioni_testo_duplicate")

    if correct_text:
        correct_norm = _norm(correct_text)
        for opt_index, txt in enumerate(option_texts, start=1):
            if _norm(txt) == correct_norm and txt != correct_text:
                defects.append(f"opzione_{opt_index}_uguale_alla_corretta")

        for opt_index, txt in enumerate(option_texts, start=1):
            if txt == correct_text:
                continue
            ratio = _similarity(txt, correct_text)
            if ratio >= 0.96:
                defects.append(f"opzione_{opt_index}_quasi_uguale_alla_corretta:{ratio:.3f}")

    if not _as_list(item.get("micro_concetti")):
        defects.append("micro_concetti_assenti")

    if not _as_list(item.get("fonte_pagine")):
        defects.append("fonte_pagine_assenti")

    if not _text(item.get("fatto_origine")):
        defects.append("fatto_origine_assente")

    return QuizQualityItem(
        index=index,
        question_id=question_id,
        domanda_chars=len(domanda),
        options_count=len(options),
        explanation_chars=len(spiegazione),
        correct_option_id=correct_option_id,
        defects=defects,
        warnings=warnings,
    )


def evaluate_test_quiz_final_quality(result: Dict[str, Any]) -> Dict[str, Any]:
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

    quiz = _as_list(result.get("test_quiz") or result.get("quiz") or result.get("test"))

    if len(quiz) < MIN_QUIZ_QUESTIONS:
        defects.append(f"quiz_questions_too_few:{len(quiz)}")

    quality_report = result.get("quality_report") or {}
    if not isinstance(quality_report, dict) or not quality_report:
        defects.append("quality_report_missing_or_empty")
        quality_report = {}

    real_connection = quality_report.get("test_quiz_real_connection_v513d1") or {}
    if not isinstance(real_connection, dict) or not real_connection:
        defects.append("test_quiz_real_connection_v513d1_missing")
        real_connection = {}

    route_total = int(real_connection.get("resolved_route_total") or 0)
    test_quality_controls = int(real_connection.get("resolved_test_quality_controls") or 0)
    selector_orchestrator = int(real_connection.get("resolved_selector_orchestrator") or 0)
    missing_motor_ids = _as_list(real_connection.get("missing_motor_ids"))

    if route_total != EXPECTED_ROUTE_TOTAL:
        defects.append(f"route_total_expected_63_found_{route_total}")

    if test_quality_controls != EXPECTED_TEST_QUALITY_CONTROLS:
        defects.append(f"test_quality_controls_expected_55_found_{test_quality_controls}")

    if selector_orchestrator != EXPECTED_SELECTOR_ORCHESTRATOR:
        defects.append(f"selector_orchestrator_expected_8_found_{selector_orchestrator}")

    if missing_motor_ids:
        defects.append(f"missing_motor_ids:{missing_motor_ids}")

    executed_ids = _as_list(real_connection.get("executed_motor_ids"))
    if len(executed_ids) != EXPECTED_ROUTE_TOTAL:
        defects.append(f"executed_motor_ids_expected_63_found_{len(executed_ids)}")

    connection_status = _text(real_connection.get("status"))
    if not connection_status.startswith("PASS - Fase 5.13D.1"):
        defects.append(f"test_quiz_real_connection_status_not_pass:{connection_status}")

    connection_defects = _as_list(real_connection.get("defects"))
    if connection_defects:
        defects.append(f"test_quiz_real_connection_defects_not_empty:{connection_defects}")

    connection_warnings = _as_list(real_connection.get("warnings"))
    if connection_warnings:
        defects.append(f"test_quiz_real_connection_warnings_not_empty:{connection_warnings}")

    items: List[Dict[str, Any]] = []
    question_texts: List[Tuple[int, str]] = []

    for index, item in enumerate(quiz, start=1):
        if not isinstance(item, dict):
            defects.append(f"quiz_item_{index}_not_dict")
            continue

        item_report = _validate_quiz_item(index, item)
        items.append(asdict(item_report))

        defects.extend(f"item_{index}:{defect}" for defect in item_report.defects)
        warnings.extend(f"item_{index}:{warning}" for warning in item_report.warnings)

        question_texts.append((index, _text(item.get("domanda") or item.get("question") or "")))

    seen_questions: Dict[str, int] = {}
    for index, domanda in question_texts:
        key = _norm(domanda)
        if key in seen_questions:
            duplicate_pairs.append(f"domande:{seen_questions[key]}-{index}")
        else:
            seen_questions[key] = index

    for pos_a in range(len(question_texts)):
        idx_a, text_a = question_texts[pos_a]
        for pos_b in range(pos_a + 1, len(question_texts)):
            idx_b, text_b = question_texts[pos_b]
            ratio = _similarity(text_a, text_b)
            if ratio >= 0.92:
                near_duplicate_pairs.append(f"domande:{idx_a}-{idx_b}:similarity={ratio:.3f}")

    if duplicate_pairs:
        defects.append(f"duplicate_pairs:{duplicate_pairs}")

    if near_duplicate_pairs:
        defects.append(f"near_duplicate_pairs:{near_duplicate_pairs}")

    status = (
        "PASS - Fase 5.13D.2: TEST_QUIZ_FINAL_QUALITY_GATE_READY"
        if not defects and not warnings
        else "FAIL - Fase 5.13D.2: TEST_QUIZ_FINAL_QUALITY_GATE_NOT_READY"
    )

    return asdict(TestQuizFinalQualityReport(
        phase="5.13D.2",
        status=status,
        approved=approved,
        source_status=source_status,
        quiz_questions_count=len(quiz),
        route_total=route_total,
        test_quality_controls=test_quality_controls,
        selector_orchestrator=selector_orchestrator,
        missing_motor_ids=[str(item) for item in missing_motor_ids],
        duplicate_pairs=duplicate_pairs,
        near_duplicate_pairs=near_duplicate_pairs,
        items=items,
        defects=defects,
        warnings=warnings,
    ))
