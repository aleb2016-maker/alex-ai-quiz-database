#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.5 - diagnostica reale motore Interroga Documento.

Esegue domande vere su documenti reali/locali senza collegare UI e senza
modificare generatori Summary, Cards, Quiz/Test o Study Questions.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15g1_long_document_orchestrator import is_long_document  # noqa: E402
from backend.phase5_15g5_document_qa_engine import (  # noqa: E402
    answer_document_question,
    validate_grounded_document_answer,
)

REPORT_JSON = ROOT / "reports/phase5_15g5_document_qa_diagnostics_v1.json"
REPORT_MD = ROOT / "reports/phase5_15g5_document_qa_diagnostics_v1.md"
SAFETY_MD = ROOT / "reports/phase5_15g5_document_qa_safety_review_v1.md"

DOCUMENTS: List[Tuple[str, str, str]] = [
    ("audit_effetti_premi_ai_its", "reports/audit_effetti_premi_ai_its.md", "real_long_audit"),
    ("synthetic_long_business_doc", "rag/documenti/test_documento_lungo_aziendale_120_pagine.txt", "synthetic_long_stress"),
    ("security_training_doc", "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md", "medium_security"),
    ("ai_generative_rag_doc", "rag/documenti/documento_ai_generativa_test_rag.md", "ai_rag_domain"),
    ("business_training_short_doc", "rag/documenti/esempio_documento_aziendale_formazione.md", "short_business"),
]

QUESTIONS: List[Tuple[str, str, str]] = [
    ("present_answer", "Qual è il tema principale del documento?", "ANSWERED"),
    ("responsibilities_procedures_risks", "Quali responsabilità, procedure o rischi vengono citati?", "ANSWERED"),
    ("simple_explanation", "Spiegami questo documento in modo semplice.", "ANSWERED"),
    ("out_of_document_petrolio", "Qual è il prezzo del petrolio indicato nel documento?", "NOT_FOUND_IN_DOCUMENT"),
]

QUIZLIKE_PATTERNS = [
    r"\bopzione\s+[abcd]\b",
    r"\bla\s+risposta\s+corretta\s+(?:è|e')\b",
    r"\brisposta\s+corretta\s*[:=]",
    r"\bdistrattor[ei]\b",
    r"\bdomanda\s+\d+\b",
    r"\ba\)\s.+\bb\)\s.+\bc\)\s.+\bd\)",
]

STUDY_QUESTION_PATTERNS = [
    r"\bdomande\s+di\s+studio\b",
    r"\bstudy\s+questions?\b",
    r"\bpreparati\s+a\s+rispondere\b",
]


def word_count(text: Any) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or "")))


def compact(text: Any, limit: int = 260) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    return clean if len(clean) <= limit else clean[: limit - 3].rstrip() + "..."


def pattern_count(text: Any, patterns: List[str]) -> int:
    low = str(text or "").lower()
    return sum(len(re.findall(pattern, low)) for pattern in patterns)


def inspect_question(document_text: str, document_name: str, question_id: str, question: str, expected_status: str) -> Dict[str, Any]:
    result = answer_document_question(
        document_text,
        question,
        document_title=document_name,
        max_context_chunks=8,
        answer_style="balanced",
    )
    validation = validate_grounded_document_answer(result, document_text, question)
    answer = str(result.get("answer") or "")
    evidence = result.get("evidence") if isinstance(result.get("evidence"), list) else []
    metrics = result.get("metrics") if isinstance(result.get("metrics"), dict) else {}

    defects: List[str] = []
    warnings: List[str] = []
    if result.get("status") != expected_status:
        defects.append(f"unexpected_status:{result.get('status')} expected:{expected_status}")
    if expected_status == "ANSWERED" and not evidence:
        defects.append("answered_expected_but_no_evidence")
    if expected_status == "NOT_FOUND_IN_DOCUMENT" and evidence:
        defects.append("not_found_expected_but_evidence_present")
    if validation.get("defects"):
        defects.extend([f"validation:{item}" for item in validation["defects"]])
    if validation.get("warnings"):
        warnings.extend([f"validation:{item}" for item in validation["warnings"]])
    quizlike_count = pattern_count(answer, QUIZLIKE_PATTERNS)
    study_question_count = pattern_count(answer, STUDY_QUESTION_PATTERNS)
    if quizlike_count:
        defects.append("quiz_like_answer_visible")
    if study_question_count:
        defects.append("study_question_like_answer_visible")

    return {
        "question_id": question_id,
        "question": question,
        "expected_status": expected_status,
        "status": result.get("status"),
        "confidence": result.get("confidence"),
        "not_found": result.get("not_found"),
        "answer_words": word_count(answer),
        "answer_preview": compact(answer, 360),
        "evidence_count": len(evidence),
        "evidence_preview": [
            {
                "chunk_id": item.get("chunk_id"),
                "score": item.get("score"),
                "text": compact(item.get("text"), 280),
            }
            for item in evidence[:2]
        ],
        "engine_warnings": result.get("warnings") or [],
        "validation_pass": validation.get("pass"),
        "validation_metrics": validation.get("metrics") or {},
        "metrics": metrics,
        "fallback_demo_count": int(metrics.get("fallback_demo_count") or 0),
        "unsupported_claim_count": int(metrics.get("unsupported_claim_count") or 0),
        "template_phrase_count": int(metrics.get("template_phrase_count") or 0),
        "empty_answer_count": int(metrics.get("empty_answer_count") or 0),
        "generic_answer_count": int(metrics.get("generic_answer_count") or 0),
        "quizlike_count": quizlike_count,
        "study_question_like_count": study_question_count,
        "defects": defects,
        "warnings": warnings,
        "judgment": "FAIL" if defects else "PASS",
    }


def inspect_document(name: str, rel_path: str, doc_type: str) -> Dict[str, Any] | None:
    path = ROOT / rel_path
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    question_results = [
        inspect_question(text, name, question_id, question, expected_status)
        for question_id, question, expected_status in QUESTIONS
    ]
    answered_count = sum(1 for item in question_results if item["status"] == "ANSWERED")
    not_found_count = sum(1 for item in question_results if item["status"] == "NOT_FOUND_IN_DOCUMENT")
    fallback_demo_count = sum(item["fallback_demo_count"] for item in question_results)
    unsupported_claim_count = sum(item["unsupported_claim_count"] for item in question_results)
    template_phrase_count = sum(item["template_phrase_count"] for item in question_results)
    generic_answer_count = sum(item["generic_answer_count"] for item in question_results)
    empty_answer_count = sum(item["empty_answer_count"] for item in question_results)
    quizlike_count = sum(item["quizlike_count"] for item in question_results)
    study_question_like_count = sum(item["study_question_like_count"] for item in question_results)
    defects = [f"{item['question_id']}:{defect}" for item in question_results for defect in item["defects"]]
    warnings = [f"{item['question_id']}:{warning}" for item in question_results for warning in item["warnings"]]
    if answered_count < 3:
        defects.append("answered_count_below_3")
    if not_found_count < 1:
        defects.append("missing_out_of_document_not_found")
    if fallback_demo_count:
        defects.append("fallback_demo_visible")
    if quizlike_count:
        defects.append("quiz_like_output_visible")
    if study_question_like_count:
        defects.append("study_question_output_visible")
    if unsupported_claim_count > 4:
        defects.append("unsupported_claims_above_threshold")
    elif unsupported_claim_count:
        warnings.append("minor_unsupported_claims_present")

    return {
        "name": name,
        "filepath": rel_path,
        "type": doc_type,
        "words": word_count(text),
        "long_document": is_long_document(text),
        "question_count": len(question_results),
        "answered_count": answered_count,
        "not_found_count": not_found_count,
        "fallback_demo_count": fallback_demo_count,
        "unsupported_claim_count": unsupported_claim_count,
        "template_phrase_count": template_phrase_count,
        "generic_answer_count": generic_answer_count,
        "empty_answer_count": empty_answer_count,
        "quizlike_count": quizlike_count,
        "study_question_like_count": study_question_like_count,
        "questions": question_results,
        "defects": defects,
        "warnings": warnings,
        "judgment": "FAIL" if defects else ("WARNING" if warnings else "PASS"),
    }


def write_reports(report: Dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# FASE 5.15G.5 - Document QA diagnostics",
        "",
        f"Status: **{report['status']}**",
        f"Documents tested: `{report['document_count']}`",
        f"Questions tested: `{report['question_count']}`",
        f"Answered / not found: `{report['answered_count']}` / `{report['not_found_count']}`",
        f"Fallback/demo/template/unsupported: `{report['fallback_demo_count']}` / `{report['template_phrase_count']}` / `{report['unsupported_claim_count']}`",
        f"Quiz-like / study-question-like outputs: `{report['quizlike_count']}` / `{report['study_question_like_count']}`",
        "",
        "## Scope confirmations",
        "",
        "- Interroga Documento is a new isolated engine.",
        "- Study Questions were not deleted or replaced.",
        "- No UI route/button was linked in this diagnostic phase.",
        "- Summary, Cards and Test/Quiz generators are not invoked by this script.",
        "",
    ]
    for case in report["documents"]:
        lines.extend(
            [
                f"## {case['name']} - {case['judgment']}",
                "",
                f"- File: `{case['filepath']}`",
                f"- Type: `{case['type']}`; words: `{case['words']}`; long_doc: `{case['long_document']}`",
                f"- Questions: `{case['question_count']}`; answered: `{case['answered_count']}`; not_found: `{case['not_found_count']}`",
                f"- Noise metrics: fallback `{case['fallback_demo_count']}`, template `{case['template_phrase_count']}`, unsupported `{case['unsupported_claim_count']}`, quizlike `{case['quizlike_count']}`, study_question_like `{case['study_question_like_count']}`",
                f"- Defects: `{case['defects']}`",
                f"- Warnings: `{case['warnings']}`",
                "",
            ]
        )
        for item in case["questions"]:
            lines.extend(
                [
                    f"### {item['question_id']} - {item['judgment']}",
                    "",
                    f"- Question: {item['question']}",
                    f"- Expected/status/confidence: `{item['expected_status']}` / `{item['status']}` / `{item['confidence']}`",
                    f"- Answer: {item['answer_preview']}",
                    f"- Evidence chunks: `{item['evidence_count']}`",
                    f"- Defects: `{item['defects']}`",
                    "",
                ]
            )
            for evidence in item["evidence_preview"]:
                lines.append(f"  - Evidence `{evidence['chunk_id']}` score `{evidence['score']}`: {evidence['text']}")
            if item["evidence_preview"]:
                lines.append("")
    REPORT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    safety = [
        "# FASE 5.15G.5 - Safety review",
        "",
        f"Status: **{report['status']}**",
        "",
        "- No external API or web retrieval is used.",
        "- The engine receives only the provided document text and user question.",
        "- Out-of-document probe uses a petrolio question and must return NOT_FOUND_IN_DOCUMENT.",
        "- The diagnostic checks fallback/demo strings, quiz-like output, study-question-like output and unsupported claims.",
        "- UI integration is intentionally absent in this phase.",
        "",
        f"Out-of-document pass count: `{report['not_found_count']}` of `{report['document_count']}`",
        f"Fallback/demo count: `{report['fallback_demo_count']}`",
        f"Unsupported claim count: `{report['unsupported_claim_count']}`",
    ]
    SAFETY_MD.write_text("\n".join(safety).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    documents: List[Dict[str, Any]] = []
    missing: List[str] = []
    for name, rel_path, doc_type in DOCUMENTS:
        inspected = inspect_document(name, rel_path, doc_type)
        if inspected is None:
            missing.append(rel_path)
        else:
            documents.append(inspected)

    fail_count = sum(1 for item in documents if item["judgment"] == "FAIL")
    warning_count = sum(1 for item in documents if item["judgment"] == "WARNING")
    document_count = len(documents)
    question_count = sum(item["question_count"] for item in documents)
    answered_count = sum(item["answered_count"] for item in documents)
    not_found_count = sum(item["not_found_count"] for item in documents)
    fallback_demo_count = sum(item["fallback_demo_count"] for item in documents)
    unsupported_claim_count = sum(item["unsupported_claim_count"] for item in documents)
    template_phrase_count = sum(item["template_phrase_count"] for item in documents)
    quizlike_count = sum(item["quizlike_count"] for item in documents)
    study_question_like_count = sum(item["study_question_like_count"] for item in documents)

    blocking_defects: List[str] = []
    if missing:
        blocking_defects.append(f"missing_documents:{missing}")
    if document_count < 5:
        blocking_defects.append("document_count_below_5")
    if not_found_count < document_count:
        blocking_defects.append("out_of_document_not_found_below_document_count")
    if fallback_demo_count:
        blocking_defects.append("fallback_demo_visible")
    if quizlike_count or study_question_like_count:
        blocking_defects.append("wrong_generator_shape_visible")
    if unsupported_claim_count > 4:
        blocking_defects.append("unsupported_claims_above_global_threshold")

    if fail_count or blocking_defects:
        status = "FAIL"
    elif warning_count or unsupported_claim_count:
        status = "WARNING"
    else:
        status = "PASS"

    report: Dict[str, Any] = {
        "phase": "5.15G.5",
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "status": status,
        "document_count": document_count,
        "missing_documents": missing,
        "question_count": question_count,
        "answered_count": answered_count,
        "not_found_count": not_found_count,
        "fallback_demo_count": fallback_demo_count,
        "unsupported_claim_count": unsupported_claim_count,
        "template_phrase_count": template_phrase_count,
        "quizlike_count": quizlike_count,
        "study_question_like_count": study_question_like_count,
        "fail_count": fail_count,
        "warning_count": warning_count,
        "blocking_defects": blocking_defects,
        "scope_confirmations": {
            "interroga_documento_is_new_engine": True,
            "ui_linked": False,
            "study_questions_deleted": False,
            "summary_cards_quiz_study_generators_invoked": False,
            "test_quiz_g4_1_touched": False,
        },
        "documents": documents,
    }
    write_reports(report)
    print(f"phase5_15g5_document_qa_diagnostics: {status}")
    print(f"documents/questions: {document_count}/{question_count}")
    print(f"answered/not_found: {answered_count}/{not_found_count}")
    print(f"fallback/template/unsupported: {fallback_demo_count}/{template_phrase_count}/{unsupported_claim_count}")
    print(f"reports: {REPORT_JSON} {REPORT_MD} {SAFETY_MD}")
    return 0 if status in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
