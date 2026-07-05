#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12E — TEST / QUIZ QUALITY MOTORS V1

Motori atomici ricostruiti:
33. Test separato da card/riassunto/domande studio
34. Opzioni interne validate
35. Opzioni visibili pulite
36. Risposta corretta interna
37. Risposta corretta visibile
38. Mappa sicura tra risposta interna e visibile
39. Quattro opzioni per domanda
40. Risposta corretta presente tra le opzioni
41. Distrattori forti
42. Niente opzioni duplicate nella stessa domanda
43. Niente ripetizioni globali eccessive
44. Compatibilità bridge quiz V3.5B

Questo modulo NON modifica i 43 motori già collegati.
Questo modulo NON modifica la pipeline 5.11.
Questo modulo NON tocca UI/PDF/CSS/app.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional


PHASE = "5.12E"
VERSION = "v1"
READY_LABEL = "TEST_QUIZ_QUALITY_MOTORS_V512E_READY"


@dataclass
class QuizQualityIssue:
    motor_id: str
    severity: str
    message: str
    excerpt: str
    suggestion: str = ""


@dataclass
class QuizQualityMotorResult:
    motor_id: str
    title: str
    status: str
    issues: List[QuizQualityIssue]


@dataclass
class QuizQualityReport:
    phase: str
    ready_label: str
    approved: bool
    status: str
    total_motors: int
    passed_motors: int
    failed_motors: int
    total_issues: int
    blocking_issues: int
    warning_issues: int
    results: List[QuizQualityMotorResult]


GENERIC_OPTIONS = {
    "tutte le risposte",
    "nessuna risposta",
    "nessuna delle precedenti",
    "tutte le precedenti",
    "non so",
    "altro",
    "varie cose",
    "dipende",
    "opzione a",
    "opzione b",
    "opzione c",
    "opzione d",
}

UGLY_TOKENS = [
    "knowledge_base_json",
    "documento analizzato",
    "fallback",
    "demo",
    "placeholder",
    "debug",
    "raw",
    "todo",
    "mock",
    "stub",
    ".json",
    ".tmp",
    ".bak",
]


def _clean_excerpt(value: Any, max_len: int = 160) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _issue(
    motor_id: str,
    severity: str,
    message: str,
    excerpt: Any,
    suggestion: str = "",
) -> QuizQualityIssue:
    return QuizQualityIssue(
        motor_id=motor_id,
        severity=severity,
        message=message,
        excerpt=_clean_excerpt(excerpt),
        suggestion=suggestion,
    )


def _norm(value: Any) -> str:
    text = str(value or "").lower()
    text = text.replace("à", "a").replace("è", "e").replace("é", "e")
    text = text.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    text = re.sub(r"^[a-d][\)\.\-:]\s*", "", text.strip())
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _word_count(value: Any) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", str(value or "")))


def _contains_ugly(value: Any) -> bool:
    low = str(value or "").lower()
    return any(token in low for token in UGLY_TOKENS)


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _quiz_root(payload: Any) -> Any:
    if isinstance(payload, dict):
        for key in ["quiz", "test", "test_quiz", "questions", "domande"]:
            if key in payload:
                return payload[key]
    return payload


def _extract_questions(payload: Any) -> List[Dict[str, Any]]:
    root = _quiz_root(payload)

    if isinstance(root, dict):
        for key in ["questions", "domande", "items"]:
            if isinstance(root.get(key), list):
                return [q for q in root[key] if isinstance(q, dict)]

    if isinstance(root, list):
        return [q for q in root if isinstance(q, dict)]

    return []


def _question_text(q: Dict[str, Any]) -> str:
    return str(q.get("question") or q.get("domanda") or q.get("text") or "").strip()


def _options(q: Dict[str, Any]) -> List[str]:
    raw = (
        q.get("options")
        or q.get("opzioni")
        or q.get("visible_options")
        or q.get("opzioni_visibili")
        or q.get("internal_options")
        or q.get("opzioni_interne")
        or []
    )
    return [str(x).strip() for x in _as_list(raw) if str(x).strip()]


def _visible_options(q: Dict[str, Any]) -> List[str]:
    raw = q.get("visible_options") or q.get("opzioni_visibili") or q.get("options") or q.get("opzioni") or []
    return [str(x).strip() for x in _as_list(raw) if str(x).strip()]


def _internal_answer(q: Dict[str, Any]) -> str:
    value = (
        q.get("correct_answer")
        or q.get("answer")
        or q.get("risposta_corretta")
        or q.get("correct")
        or ""
    )
    return str(value).strip()


def _visible_answer(q: Dict[str, Any]) -> str:
    # Se la risposta visibile è dichiarata esplicitamente, va rispettata anche se vuota.
    # Questo evita che il controllo "risposta corretta visibile" venga mascherato
    # dal fallback sulla risposta interna.
    explicit_visible_keys = [
        "correct_answer_visible",
        "risposta_corretta_visibile",
        "visible_correct_answer",
    ]

    for key in explicit_visible_keys:
        if key in q:
            return str(q.get(key) or "").strip()

    value = (
        q.get("correct_answer")
        or q.get("risposta_corretta")
        or ""
    )
    return str(value).strip()


def _explanation(q: Dict[str, Any]) -> str:
    return str(q.get("explanation") or q.get("spiegazione") or q.get("feedback") or "").strip()


def _wrong_options(q: Dict[str, Any]) -> List[str]:
    answer = _norm(_visible_answer(q) or _internal_answer(q))
    return [opt for opt in _options(q) if _norm(opt) != answer]


def _has_section_contamination(payload: Any) -> bool:
    if not isinstance(payload, dict):
        return False

    forbidden_top_keys = {
        "cards",
        "card",
        "summary",
        "riassunto",
        "sintesi",
        "study_questions",
        "domande_studio",
        "flashcards",
    }

    root = payload.get("quiz") or payload.get("test") or payload.get("test_quiz")
    if isinstance(root, dict):
        root_forbidden = forbidden_top_keys & {str(k).lower() for k in root.keys()}
        if root_forbidden:
            return True

    top_forbidden = forbidden_top_keys & {str(k).lower() for k in payload.keys()}
    return bool(top_forbidden)


def motor_033_test_separated(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_033_test_quiz_test_separato_da_card_riassunto_domande_studio"
    title = "Test separato da card/riassunto/domande studio"
    issues: List[QuizQualityIssue] = []

    questions = _extract_questions(payload)

    if not questions:
        issues.append(_issue(motor_id, "blocking", "Nessuna domanda quiz rilevata.", payload))

    if _has_section_contamination(payload):
        issues.append(_issue(
            motor_id,
            "blocking",
            "Il test contiene dati di card, riassunto o domande studio.",
            payload,
            "Separare il blocco test dagli altri output.",
        ))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_034_internal_options_validated(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_034_test_quiz_opzioni_interne_validate"
    title = "Opzioni interne validate"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        opts = _options(q)
        if not opts:
            issues.append(_issue(motor_id, "blocking", "Opzioni interne mancanti.", q))
        for opt in opts:
            if _word_count(opt) < 2:
                issues.append(_issue(motor_id, "blocking", "Opzione interna troppo povera.", opt))
            if _contains_ugly(opt):
                issues.append(_issue(motor_id, "blocking", "Opzione interna sporca/demo/debug.", opt))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_035_visible_options_clean(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_035_test_quiz_opzioni_visibili_pulite"
    title = "Opzioni visibili pulite"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        opts = _visible_options(q)
        if not opts:
            issues.append(_issue(motor_id, "blocking", "Opzioni visibili mancanti.", q))
        for opt in opts:
            if _contains_ugly(opt):
                issues.append(_issue(motor_id, "blocking", "Opzione visibile sporca/demo/debug.", opt))
            if re.match(r"^\s*[a-d][\)\.\-:]\s*", opt.lower()):
                issues.append(_issue(
                    motor_id,
                    "blocking",
                    "Opzione visibile contiene prefisso tecnico A/B/C/D.",
                    opt,
                    "Mostrare solo il testo pulito dell'opzione.",
                ))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_036_internal_correct_answer(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_036_test_quiz_risposta_corretta_interna"
    title = "Risposta corretta interna"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        ans = _internal_answer(q)
        if not ans:
            issues.append(_issue(motor_id, "blocking", "Risposta corretta interna mancante.", q))
        elif _contains_ugly(ans):
            issues.append(_issue(motor_id, "blocking", "Risposta corretta interna sporca/demo/debug.", ans))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_037_visible_correct_answer(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_037_test_quiz_risposta_corretta_visibile"
    title = "Risposta corretta visibile"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        ans = _visible_answer(q)
        if not ans:
            issues.append(_issue(motor_id, "blocking", "Risposta corretta visibile mancante.", q))
        elif _contains_ugly(ans):
            issues.append(_issue(motor_id, "blocking", "Risposta corretta visibile sporca/demo/debug.", ans))
        elif re.match(r"^\s*[a-d][\)\.\-:]\s*", ans.lower()):
            issues.append(_issue(motor_id, "blocking", "Risposta visibile contiene prefisso tecnico.", ans))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_038_safe_internal_visible_map(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_038_test_quiz_mappa_sicura_tra_risposta_interna_e_visibile"
    title = "Mappa sicura tra risposta interna e visibile"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        internal = _internal_answer(q)
        visible = _visible_answer(q)
        opts = [_norm(x) for x in _visible_options(q)]

        if not internal or not visible:
            issues.append(_issue(motor_id, "blocking", "Mappa risposta incompleta.", q))
            continue

        if _norm(internal) != _norm(visible):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta interna e visibile non coincidono.",
                q,
                "Allineare risposta interna e risposta mostrata.",
            ))

        if _norm(visible) not in opts:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta visibile non presente tra le opzioni visibili.",
                q,
                "Inserire la risposta corretta tra le opzioni.",
            ))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_039_four_options(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_039_test_quiz_quattro_opzioni_per_domanda"
    title = "Quattro opzioni per domanda"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        opts = _options(q)
        if len(opts) != 4:
            issues.append(_issue(
                motor_id,
                "blocking",
                f"Numero opzioni non valido: {len(opts)}.",
                q,
                "Ogni domanda deve avere esattamente 4 opzioni.",
            ))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_040_correct_answer_in_options(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_040_test_quiz_risposta_corretta_presente_tra_le_opzioni"
    title = "Risposta corretta presente tra le opzioni"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        ans = _norm(_visible_answer(q) or _internal_answer(q))
        opts = [_norm(x) for x in _options(q)]

        if not ans:
            issues.append(_issue(motor_id, "blocking", "Risposta corretta mancante.", q))
        elif ans not in opts:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta corretta non presente tra le opzioni.",
                q,
                "Aggiungere la risposta corretta tra le 4 opzioni.",
            ))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_041_strong_distractors(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_041_test_quiz_distrattori_forti"
    title = "Distrattori forti"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        wrong = _wrong_options(q)

        if len(wrong) != 3:
            issues.append(_issue(motor_id, "blocking", "Numero distrattori diverso da 3.", q))

        for opt in wrong:
            n = _norm(opt)
            if n in GENERIC_OPTIONS:
                issues.append(_issue(motor_id, "blocking", "Distrattore generico o debole.", opt))
            if _word_count(opt) < 2:
                issues.append(_issue(motor_id, "blocking", "Distrattore troppo corto.", opt))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_042_no_duplicate_options_same_question(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_042_test_quiz_niente_opzioni_duplicate_nella_stessa_domanda"
    title = "Niente opzioni duplicate nella stessa domanda"
    issues: List[QuizQualityIssue] = []

    for q in _extract_questions(payload):
        opts = [_norm(x) for x in _options(q)]
        duplicates = sorted({x for x in opts if opts.count(x) > 1})
        if duplicates:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Opzioni duplicate nella stessa domanda.",
                q,
                "Rendere le 4 opzioni diverse tra loro.",
            ))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_043_no_excessive_global_repetitions(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_043_test_quiz_niente_ripetizioni_globali_eccessive"
    title = "Niente ripetizioni globali eccessive"
    issues: List[QuizQualityIssue] = []

    counts: Dict[str, int] = {}
    for q in _extract_questions(payload):
        for opt in _options(q):
            key = _norm(opt)
            if key:
                counts[key] = counts.get(key, 0) + 1

    repeated = {k: v for k, v in counts.items() if v >= 3}
    if repeated:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Ripetizioni globali eccessive nelle opzioni.",
            repeated,
            "Variare i distrattori tra domande diverse.",
        ))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_044_bridge_v35b_compatibility(payload: Any) -> QuizQualityMotorResult:
    motor_id = "qm_044_test_quiz_compatibilita_bridge_quiz_v3_5b"
    title = "Compatibilità bridge quiz V3.5B"
    issues: List[QuizQualityIssue] = []

    questions = _extract_questions(payload)
    if not questions:
        issues.append(_issue(motor_id, "blocking", "Nessuna domanda compatibile rilevata.", payload))

    for q in questions:
        if not _question_text(q):
            issues.append(_issue(motor_id, "blocking", "Campo domanda mancante.", q))
        if len(_options(q)) != 4:
            issues.append(_issue(motor_id, "blocking", "Formato opzioni non compatibile V3.5B.", q))
        if not _internal_answer(q):
            issues.append(_issue(motor_id, "blocking", "Campo correct_answer mancante.", q))
        if not _explanation(q):
            issues.append(_issue(motor_id, "blocking", "Spiegazione/feedback mancante.", q))

    return QuizQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


TEST_QUIZ_QUALITY_MOTORS: List[Callable[[Any], QuizQualityMotorResult]] = [
    motor_033_test_separated,
    motor_034_internal_options_validated,
    motor_035_visible_options_clean,
    motor_036_internal_correct_answer,
    motor_037_visible_correct_answer,
    motor_038_safe_internal_visible_map,
    motor_039_four_options,
    motor_040_correct_answer_in_options,
    motor_041_strong_distractors,
    motor_042_no_duplicate_options_same_question,
    motor_043_no_excessive_global_repetitions,
    motor_044_bridge_v35b_compatibility,
]


def analyze_test_quiz_quality(payload: Any) -> QuizQualityReport:
    results = [motor(payload) for motor in TEST_QUIZ_QUALITY_MOTORS]

    total_issues = sum(len(r.issues) for r in results)
    blocking_issues = sum(1 for r in results for i in r.issues if i.severity == "blocking")
    warning_issues = sum(1 for r in results for i in r.issues if i.severity == "warning")
    failed_motors = sum(1 for r in results if r.status == "FAIL")
    passed_motors = len(results) - failed_motors
    approved = blocking_issues == 0

    return QuizQualityReport(
        phase=PHASE,
        ready_label=READY_LABEL,
        approved=approved,
        status="PASS" if approved else "FAIL",
        total_motors=len(results),
        passed_motors=passed_motors,
        failed_motors=failed_motors,
        total_issues=total_issues,
        blocking_issues=blocking_issues,
        warning_issues=warning_issues,
        results=results,
    )


def report_to_dict(report: QuizQualityReport) -> Dict[str, Any]:
    return asdict(report)


def registry_entry() -> Dict[str, Any]:
    titles = [
        ("qm_033_test_quiz_test_separato_da_card_riassunto_domande_studio", "Test separato da card/riassunto/domande studio"),
        ("qm_034_test_quiz_opzioni_interne_validate", "Opzioni interne validate"),
        ("qm_035_test_quiz_opzioni_visibili_pulite", "Opzioni visibili pulite"),
        ("qm_036_test_quiz_risposta_corretta_interna", "Risposta corretta interna"),
        ("qm_037_test_quiz_risposta_corretta_visibile", "Risposta corretta visibile"),
        ("qm_038_test_quiz_mappa_sicura_tra_risposta_interna_e_visibile", "Mappa sicura tra risposta interna e visibile"),
        ("qm_039_test_quiz_quattro_opzioni_per_domanda", "Quattro opzioni per domanda"),
        ("qm_040_test_quiz_risposta_corretta_presente_tra_le_opzioni", "Risposta corretta presente tra le opzioni"),
        ("qm_041_test_quiz_distrattori_forti", "Distrattori forti"),
        ("qm_042_test_quiz_niente_opzioni_duplicate_nella_stessa_domanda", "Niente opzioni duplicate nella stessa domanda"),
        ("qm_043_test_quiz_niente_ripetizioni_globali_eccessive", "Niente ripetizioni globali eccessive"),
        ("qm_044_test_quiz_compatibilita_bridge_quiz_v3_5b", "Compatibilità bridge quiz V3.5B"),
    ]

    return {
        "phase": PHASE,
        "version": VERSION,
        "ready_label": READY_LABEL,
        "total_motors": len(titles),
        "motors": [
            {
                "id": mid,
                "title": title,
                "type": "validator",
                "severity": "blocking",
            }
            for mid, title in titles
        ],
        "scope_guard": {
            "ui_pdf_css_app_touched": False,
            "pipeline_5_11_changed": False,
            "existing_43_motors_changed": False,
            "standalone_first": True,
            "no_fallback": True,
            "no_demo_output": True,
            "quiz_section_only": True,
        },
    }
