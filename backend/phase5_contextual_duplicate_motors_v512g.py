#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from difflib import SequenceMatcher
from typing import Any, Callable, Dict, List, Optional, Tuple


PHASE = "5.12G"
VERSION = "v1"
READY_LABEL = "CONTEXTUAL_DUPLICATE_MOTORS_V512G_READY"


STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "uno", "una", "di", "a", "da",
    "in", "con", "su", "per", "tra", "fra", "e", "o", "che", "del", "della",
    "dei", "degli", "delle", "nel", "nella", "nei", "nelle", "al", "alla",
    "ai", "agli", "alle", "si", "sono", "è", "viene", "vengono", "questo",
    "questa", "questi", "queste", "cosa", "quale",
}


@dataclass
class ContextTextItem:
    section: str
    kind: str
    purpose: str
    text: str
    path: str


@dataclass
class ContextDuplicateIssue:
    motor_id: str
    severity: str
    message: str
    excerpt: str
    first_path: str = ""
    second_path: str = ""
    similarity: Optional[float] = None
    suggestion: str = ""


@dataclass
class ContextDuplicateMotorResult:
    motor_id: str
    title: str
    status: str
    issues: List[ContextDuplicateIssue]


@dataclass
class ContextDuplicateReport:
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
    results: List[ContextDuplicateMotorResult]


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _excerpt(value: Any, max_len: int = 180) -> str:
    text = _clean(value)
    return text if len(text) <= max_len else text[: max_len - 3] + "..."


def _norm(value: Any) -> str:
    text = str(value or "").lower()
    text = (
        text.replace("à", "a")
        .replace("è", "e")
        .replace("é", "e")
        .replace("ì", "i")
        .replace("ò", "o")
        .replace("ù", "u")
    )
    text = re.sub(r"[^a-z0-9]+", " ", text)
    tokens = [t for t in text.split() if t and t not in STOPWORDS]
    return " ".join(tokens)


def _tokens(value: Any) -> List[str]:
    return _norm(value).split()


def _word_count(value: Any) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", str(value or "")))


def _similarity(a: str, b: str) -> float:
    na = _norm(a)
    nb = _norm(b)
    if not na or not nb:
        return 0.0

    seq = SequenceMatcher(None, na, nb).ratio()
    ta = set(na.split())
    tb = set(nb.split())
    jac = len(ta & tb) / max(1, len(ta | tb))
    return max(seq, jac)


def _sentences(text: str) -> List[str]:
    raw = re.split(r"(?<=[.!?])\s+", str(text or "").strip())
    return [s.strip() for s in raw if _word_count(s) >= 4]


def _issue(
    motor_id: str,
    message: str,
    excerpt: Any,
    first_path: str = "",
    second_path: str = "",
    similarity: Optional[float] = None,
    suggestion: str = "",
) -> ContextDuplicateIssue:
    return ContextDuplicateIssue(
        motor_id=motor_id,
        severity="blocking",
        message=message,
        excerpt=_excerpt(excerpt),
        first_path=first_path,
        second_path=second_path,
        similarity=similarity,
        suggestion=suggestion,
    )


def _collect_items(payload: Any) -> List[ContextTextItem]:
    items: List[ContextTextItem] = []

    def add_item(section: str, kind: str, purpose: str, text: Any, path: str) -> None:
        clean = _clean(text)
        if _word_count(clean) >= 4:
            items.append(ContextTextItem(
                section=section or "general",
                kind=kind or "text",
                purpose=purpose or "",
                text=clean,
                path=path,
            ))

    if isinstance(payload, dict) and isinstance(payload.get("items"), list):
        for i, row in enumerate(payload["items"]):
            if isinstance(row, dict):
                add_item(
                    str(row.get("section") or "general"),
                    str(row.get("kind") or row.get("type") or "text"),
                    str(row.get("purpose") or row.get("funzione") or ""),
                    row.get("text") or row.get("content") or row.get("question") or row.get("title") or "",
                    f"items[{i}]",
                )
            else:
                add_item("general", "text", "", row, f"items[{i}]")
        return items

    def walk(x: Any, path: str, section: str = "general", kind: str = "text") -> None:
        if isinstance(x, dict):
            local_section = str(x.get("section") or x.get("area") or section)
            local_kind = str(x.get("kind") or x.get("type") or kind)
            purpose = str(x.get("purpose") or x.get("funzione") or "")

            for key, value in x.items():
                lk = str(key).lower()
                if lk in {"context", "metadata", "report_files", "layout"}:
                    continue

                if isinstance(value, str) and lk in {
                    "text", "content", "body", "summary", "riassunto",
                    "question", "domanda", "answer", "risposta", "title",
                    "titolo", "description", "spiegazione",
                }:
                    add_item(local_section, local_kind, purpose, value, f"{path}.{key}" if path else key)
                else:
                    walk(value, f"{path}.{key}" if path else key, local_section, local_kind)

        elif isinstance(x, list):
            for i, value in enumerate(x):
                walk(value, f"{path}[{i}]", section, kind)

        elif isinstance(x, str):
            add_item(section, kind, "", x, path)

    walk(payload, "")
    return items


def _same_context(a: ContextTextItem, b: ContextTextItem) -> bool:
    return a.section == b.section and a.kind == b.kind


def _different_legitimate_function(a: ContextTextItem, b: ContextTextItem) -> bool:
    if a.section != b.section:
        if a.purpose and b.purpose and a.purpose != b.purpose:
            return True
        if a.kind and b.kind and a.kind != b.kind:
            return True
    return False


def _pairwise(items: List[ContextTextItem]) -> List[Tuple[ContextTextItem, ContextTextItem]]:
    return [(a, b) for i, a in enumerate(items) for b in items[i + 1:]]


def motor_045_exact_duplicates(payload: Any) -> ContextDuplicateMotorResult:
    motor_id = "qm_045_duplicati_contestuali_duplicati_esatti"
    title = "Duplicati contestuali: duplicati esatti"
    issues: List[ContextDuplicateIssue] = []

    seen: Dict[Tuple[str, str, str], ContextTextItem] = {}
    for item in _collect_items(payload):
        key = (item.section, item.kind, _norm(item.text))
        if not key[2]:
            continue

        if key in seen:
            other = seen[key]
            issues.append(_issue(
                motor_id,
                "Duplicato esatto nello stesso contesto.",
                item.text,
                other.path,
                item.path,
                1.0,
                "Rimuovere il duplicato o trasformarlo in contenuto con funzione diversa.",
            ))
        else:
            seen[key] = item

    return ContextDuplicateMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_046_near_duplicates(payload: Any) -> ContextDuplicateMotorResult:
    motor_id = "qm_046_duplicati_contestuali_quasi_duplicati"
    title = "Duplicati contestuali: quasi duplicati"
    issues: List[ContextDuplicateIssue] = []

    for a, b in _pairwise(_collect_items(payload)):
        if not _same_context(a, b):
            continue
        if _norm(a.text) == _norm(b.text):
            continue

        sim = _similarity(a.text, b.text)
        if sim >= 0.72:
            issues.append(_issue(
                motor_id,
                "Quasi duplicato nello stesso contesto.",
                f"{a.text} || {b.text}",
                a.path,
                b.path,
                round(sim, 3),
                "Unire le due frasi o differenziare davvero il contenuto.",
            ))

    return ContextDuplicateMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_047_useless_repetitions(payload: Any) -> ContextDuplicateMotorResult:
    motor_id = "qm_047_duplicati_contestuali_ripetizioni_inutili"
    title = "Duplicati contestuali: ripetizioni inutili"
    issues: List[ContextDuplicateIssue] = []

    for item in _collect_items(payload):
        sentences = _sentences(item.text)
        normalized = [_norm(s) for s in sentences if _norm(s)]

        for norm_sentence in sorted(set(normalized)):
            if normalized.count(norm_sentence) >= 3:
                issues.append(_issue(
                    motor_id,
                    "La stessa frase viene ripetuta troppe volte nello stesso testo.",
                    item.text,
                    item.path,
                    "",
                    1.0,
                    "Tenere una sola occorrenza e sostituire le altre con informazioni nuove.",
                ))

        tokens = _tokens(item.text)
        repeated_terms = [t for t in sorted(set(tokens)) if len(t) >= 5 and tokens.count(t) >= 6]
        if repeated_terms:
            issues.append(_issue(
                motor_id,
                "Termini ripetuti in modo eccessivo nello stesso testo.",
                ", ".join(repeated_terms),
                item.path,
                "",
                None,
                "Ridurre le ripetizioni e usare frasi più informative.",
            ))

    return ContextDuplicateMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def _is_question_item(item: ContextTextItem) -> bool:
    low_kind = item.kind.lower()
    low_section = item.section.lower()
    return (
        "question" in low_kind
        or "domanda" in low_kind
        or "quiz" in low_kind
        or "test" in low_section
        or item.text.strip().endswith("?")
    )


def motor_048_mechanical_repetitions_between_questions(payload: Any) -> ContextDuplicateMotorResult:
    motor_id = "qm_048_duplicati_contestuali_ripetizioni_meccaniche_tra_domande"
    title = "Duplicati contestuali: ripetizioni meccaniche tra domande"
    issues: List[ContextDuplicateIssue] = []

    questions = [item for item in _collect_items(payload) if _is_question_item(item)]

    for a, b in _pairwise(questions):
        sim = _similarity(a.text, b.text)

        a_tokens = _tokens(a.text)
        b_tokens = _tokens(b.text)

        common = set(a_tokens) & set(b_tokens)
        common_ratio = len(common) / max(1, min(len(set(a_tokens)), len(set(b_tokens))))

        same_first_two = len(a_tokens) >= 2 and len(b_tokens) >= 2 and a_tokens[:2] == b_tokens[:2]

        # Domande tipo:
        # "Che cosa protegge il backup aziendale?"
        # "Che cosa protegge il backup periodico?"
        # Sono meccaniche anche se cambia solo l'ultima parola.
        mechanical_template = same_first_two and common_ratio >= 0.60

        # Caso più generale: alta somiglianza + molte parole in comune.
        high_similarity_template = sim >= 0.68 and common_ratio >= 0.60

        if mechanical_template or high_similarity_template:
            issues.append(_issue(
                motor_id,
                "Domande troppo meccaniche o ripetute tra loro.",
                f"{a.text} || {b.text}",
                a.path,
                b.path,
                round(sim, 3),
                "Variare davvero il focus della domanda, non solo una parola finale.",
            ))

    return ContextDuplicateMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_049_too_similar_sentences(payload: Any) -> ContextDuplicateMotorResult:
    motor_id = "qm_049_duplicati_contestuali_frasi_troppo_simili"
    title = "Duplicati contestuali: frasi troppo simili"
    issues: List[ContextDuplicateIssue] = []
    sentence_items: List[ContextTextItem] = []

    for item in _collect_items(payload):
        for idx, sentence in enumerate(_sentences(item.text)):
            sentence_items.append(ContextTextItem(
                section=item.section,
                kind=item.kind,
                purpose=item.purpose,
                text=sentence,
                path=f"{item.path}.sentence[{idx}]",
            ))

    for a, b in _pairwise(sentence_items):
        if not _same_context(a, b):
            continue
        if _norm(a.text) == _norm(b.text):
            continue

        sim = _similarity(a.text, b.text)
        if sim >= 0.72:
            issues.append(_issue(
                motor_id,
                "Frasi troppo simili nello stesso contesto.",
                f"{a.text} || {b.text}",
                a.path,
                b.path,
                round(sim, 3),
                "Riscrivere una delle frasi aggiungendo informazione nuova o rimuoverla.",
            ))

    return ContextDuplicateMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_050_same_content_without_reason(payload: Any) -> ContextDuplicateMotorResult:
    motor_id = "qm_050_duplicati_contestuali_stesso_contenuto_ripetuto_senza_motivo"
    title = "Duplicati contestuali: stesso contenuto ripetuto senza motivo"
    issues: List[ContextDuplicateIssue] = []

    for a, b in _pairwise(_collect_items(payload)):
        if _same_context(a, b):
            continue

        sim = _similarity(a.text, b.text)
        if sim < 0.93:
            continue

        if _different_legitimate_function(a, b):
            continue

        issues.append(_issue(
            motor_id,
            "Stesso contenuto ripetuto in sezioni diverse senza funzione diversa.",
            f"{a.text} || {b.text}",
            a.path,
            b.path,
            round(sim, 3),
            "Dichiarare funzioni diverse oppure differenziare il contenuto tra le sezioni.",
        ))

    return ContextDuplicateMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


CONTEXTUAL_DUPLICATE_MOTORS: List[Callable[[Any], ContextDuplicateMotorResult]] = [
    motor_045_exact_duplicates,
    motor_046_near_duplicates,
    motor_047_useless_repetitions,
    motor_048_mechanical_repetitions_between_questions,
    motor_049_too_similar_sentences,
    motor_050_same_content_without_reason,
]


def analyze_contextual_duplicate_quality(payload: Any) -> ContextDuplicateReport:
    results = [motor(payload) for motor in CONTEXTUAL_DUPLICATE_MOTORS]

    total_issues = sum(len(r.issues) for r in results)
    blocking_issues = sum(1 for r in results for i in r.issues if i.severity == "blocking")
    warning_issues = sum(1 for r in results for i in r.issues if i.severity == "warning")
    failed_motors = sum(1 for r in results if r.status == "FAIL")
    passed_motors = len(results) - failed_motors
    approved = blocking_issues == 0

    return ContextDuplicateReport(
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


def report_to_dict(report: ContextDuplicateReport) -> Dict[str, Any]:
    return asdict(report)


def registry_entry() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "version": VERSION,
        "ready_label": READY_LABEL,
        "total_motors": len(CONTEXTUAL_DUPLICATE_MOTORS),
        "motors": [
            {
                "id": "qm_045_duplicati_contestuali_duplicati_esatti",
                "title": "Duplicati contestuali: duplicati esatti",
                "type": "validator",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
            {
                "id": "qm_046_duplicati_contestuali_quasi_duplicati",
                "title": "Duplicati contestuali: quasi duplicati",
                "type": "validator",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
            {
                "id": "qm_047_duplicati_contestuali_ripetizioni_inutili",
                "title": "Duplicati contestuali: ripetizioni inutili",
                "type": "validator",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
            {
                "id": "qm_048_duplicati_contestuali_ripetizioni_meccaniche_tra_domande",
                "title": "Duplicati contestuali: ripetizioni meccaniche tra domande",
                "type": "validator",
                "severity": "blocking",
                "areas": ["test_quiz", "study_questions"],
            },
            {
                "id": "qm_049_duplicati_contestuali_frasi_troppo_simili",
                "title": "Duplicati contestuali: frasi troppo simili",
                "type": "validator",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
            {
                "id": "qm_050_duplicati_contestuali_stesso_contenuto_ripetuto_senza_motivo",
                "title": "Duplicati contestuali: stesso contenuto ripetuto senza motivo",
                "type": "validator",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
        ],
        "scope_guard": {
            "ui_pdf_css_app_touched": False,
            "pipeline_5_11_changed": False,
            "existing_59_motors_changed": False,
            "standalone_first": True,
            "contextual_not_global": True,
            "allows_same_concept_with_different_function": True,
            "no_fallback": True,
            "no_demo_output": True,
        },
    }
