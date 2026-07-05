from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.phase5_universal_quiz_quality_adapter_v1 import (
    apply_payload_universal_quiz_quality_v1,
)

from scripts.verifica_phase5_8_quality_delta_ready_safe_motors_v1 import build_dirty_payload
from scripts.verifica_phase5_9_7_quiz_motor_runtime_test_v1 import (
    bad_total,
    quiz_from_payload,
    quiz_metrics,
)


REPORT_JSON = ROOT / "reports" / "phase5_9_8_universal_quiz_quality_adapter_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_8_universal_quiz_quality_adapter_v1.md"


def correct_option_texts(payload: Dict[str, Any]) -> List[str]:
    out: List[str] = []

    for question in quiz_from_payload(payload):
        options = question.get("opzioni") or question.get("options") or []

        if not isinstance(options, list):
            continue

        correct_id = question.get("correct_option_id")

        for option in options:
            if not isinstance(option, dict):
                continue

            if option.get("is_correct") is True or option.get("option_id") == correct_id:
                out.append(str(option.get("testo") or option.get("text") or ""))

    return out


def correct_counts(payload: Dict[str, Any]) -> List[int]:
    counts: List[int] = []

    for question in quiz_from_payload(payload):
        options = question.get("opzioni") or question.get("options") or []

        if not isinstance(options, list):
            continue

        correct_id = question.get("correct_option_id")
        count = 0

        for option in options:
            if not isinstance(option, dict):
                continue

            if option.get("is_correct") is True or option.get("option_id") == correct_id:
                count += 1

        counts.append(count)

    return counts


def changed_questions(before_payload: Dict[str, Any], after_payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    before_quiz = quiz_from_payload(before_payload)
    after_quiz = quiz_from_payload(after_payload)

    for index, before_question in enumerate(before_quiz):
        if index >= len(after_quiz):
            continue

        after_question = after_quiz[index]

        before_text = str(before_question.get("domanda") or before_question.get("question") or "")
        after_text = str(after_question.get("domanda") or after_question.get("question") or "")

        before_exp = str(
            before_question.get("spiegazione")
            or before_question.get("explanation")
            or before_question.get("explanation_draft")
            or ""
        )

        after_exp = str(
            after_question.get("spiegazione")
            or after_question.get("explanation")
            or after_question.get("explanation_draft")
            or ""
        )

        if before_text != after_text or before_exp != after_exp:
            rows.append(
                {
                    "index": index,
                    "question_before": before_text,
                    "question_after": after_text,
                    "explanation_before": before_exp,
                    "explanation_after": after_exp,
                }
            )

    return rows


def main() -> int:
    before_payload = build_dirty_payload()
    after_payload, meta = apply_payload_universal_quiz_quality_v1(copy.deepcopy(before_payload))

    before_quiz = quiz_from_payload(before_payload)
    after_quiz = quiz_from_payload(after_payload)

    before_metrics = quiz_metrics(before_quiz)
    after_metrics = quiz_metrics(after_quiz)

    before_bad = bad_total(before_metrics)
    after_bad = bad_total(after_metrics)

    correct_before = correct_option_texts(before_payload)
    correct_after = correct_option_texts(after_payload)

    counts_before = correct_counts(before_payload)
    counts_after = correct_counts(after_payload)

    rows = changed_questions(before_payload, after_payload)

    errors: List[str] = []

    if after_bad >= before_bad:
        errors.append(f"Bad total non migliora: {before_bad} -> {after_bad}")

    if after_metrics["true_fact_distractors"] != 0:
        errors.append(
            f"Distrattori veri non azzerati: {before_metrics['true_fact_distractors']} -> {after_metrics['true_fact_distractors']}"
        )

    if after_metrics["mechanical_questions"] != 0:
        errors.append(
            f"Domande meccaniche non azzerate: {before_metrics['mechanical_questions']} -> {after_metrics['mechanical_questions']}"
        )

    if after_metrics["rough_explanations"] != 0:
        errors.append(
            f"Spiegazioni grezze non azzerate: {before_metrics['rough_explanations']} -> {after_metrics['rough_explanations']}"
        )

    if correct_before != correct_after:
        errors.append("La risposta corretta testuale è cambiata.")

    if counts_before != counts_after:
        errors.append("Il numero di risposte corrette per domanda è cambiato.")

    if any(count != 1 for count in counts_after):
        errors.append("Dopo il motore non c'è esattamente una risposta corretta per domanda.")

    status = "PASS" if not errors else "FAIL"

    report = {
        "report_name": "phase5_9_8_universal_quiz_quality_adapter_v1",
        "status": status,
        "before_metrics": before_metrics,
        "after_metrics": after_metrics,
        "bad_total_before": before_bad,
        "bad_total_after": after_bad,
        "correct_option_texts_preserved": correct_before == correct_after,
        "correct_counts_before": counts_before,
        "correct_counts_after": counts_after,
        "changed_questions": rows,
        "adapter_meta": meta,
        "errors": errors,
        "notes": [
            "Test separato: il motore non è ancora collegato al registry.",
            "Obiettivo: trasformare pezzi parziali in un motore quiz completo.",
            "Migliora domande meccaniche, spiegazioni grezze e distrattori veri.",
            "Deve preservare risposta corretta, numero opzioni e struttura quiz.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append("# Fase 5.9.8 — Universal Quiz Quality Adapter V1\n")
    lines.append(f"- Status: `{status}`")
    lines.append(f"- Bad total: `{before_bad} -> {after_bad}`")
    lines.append(f"- Distrattori veri: `{before_metrics['true_fact_distractors']} -> {after_metrics['true_fact_distractors']}`")
    lines.append(f"- Domande meccaniche: `{before_metrics['mechanical_questions']} -> {after_metrics['mechanical_questions']}`")
    lines.append(f"- Domande duplicate: `{before_metrics['duplicate_questions']} -> {after_metrics['duplicate_questions']}`")
    lines.append(f"- Spiegazioni grezze: `{before_metrics['rough_explanations']} -> {after_metrics['rough_explanations']}`")
    lines.append(f"- Risposta corretta preservata: `{correct_before == correct_after}`")
    lines.append("")
    lines.append("## Domande/spiegazioni modificate\n")
    lines.append("| # | Domanda prima | Domanda dopo | Spiegazione prima | Spiegazione dopo |")
    lines.append("|---:|---|---|---|---|")

    for item in rows:
        lines.append(
            f"| {item['index']} "
            f"| {item['question_before']} "
            f"| {item['question_after']} "
            f"| {item['explanation_before']} "
            f"| {item['explanation_after']} |"
        )

    if errors:
        lines.append("")
        lines.append("## Errori\n")

        for error in errors:
            lines.append(f"- {error}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.8 UNIVERSAL QUIZ QUALITY ADAPTER PASS" if status == "PASS" else "❌ FASE 5.9.8 FAIL")
    print(f"Bad total: {before_bad} -> {after_bad}")
    print(f"Distrattori veri: {before_metrics['true_fact_distractors']} -> {after_metrics['true_fact_distractors']}")
    print(f"Domande meccaniche: {before_metrics['mechanical_questions']} -> {after_metrics['mechanical_questions']}")
    print(f"Spiegazioni grezze: {before_metrics['rough_explanations']} -> {after_metrics['rough_explanations']}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    if status != "PASS":
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        raise AssertionError("Fase 5.9.8 fallita: vedi report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
