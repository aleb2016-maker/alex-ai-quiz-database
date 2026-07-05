from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Set


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import backend.legacy_quality_motor_registry_v1 as registry

from scripts.verifica_phase5_10_universal_text_cleaner_summary_cards_v1 import (
    build_test_payload,
    count_bad_patterns,
    count_micro_concepts_with_sentence_punctuation,
)


REPORT_JSON = ROOT / "reports" / "phase5_10_2_final_registry_quality_snapshot_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_10_2_final_registry_quality_snapshot_v1.md"


MECHANICAL_STUDY_PATTERNS = [
    "quale regola o informazione emerge da",
]

MECHANICAL_QUIZ_PATTERNS = [
    "quale affermazione è supportata dal documento",
]

ROUGH_EXPLANATION_PATTERNS = [
    "il controllo degli accessi limita l'utilizzo dei sistemi interni.",
    "ogni account deve essere associato a una persona identificabile.",
    "le credenziali non devono essere condivise tra più operatori.",
    "la revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
]


def norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).lower()


def walk(value: Any):
    if isinstance(value, dict):
        yield value

        for item in value.values():
            yield from walk(item)

    elif isinstance(value, list):
        for item in value:
            yield from walk(item)


def collect_source_facts(payload: Dict[str, Any]) -> Set[str]:
    facts: Set[str] = set()

    for item in walk(payload):
        if not isinstance(item, dict):
            continue

        for key in ["source_facts", "key_facts", "global_facts"]:
            values = item.get(key)

            if isinstance(values, list):
                for value in values:
                    if isinstance(value, str) and value.strip():
                        facts.add(norm(value))

    return facts


def collect_study_questions(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for key in ["study_questions", "study_questions_draft", "domande_studio"]:
        values = payload.get(key)

        if isinstance(values, list):
            out.extend([item for item in values if isinstance(item, dict)])

    return out


def collect_quiz_questions(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []

    for key in ["quiz_draft", "quiz", "quiz_questions", "test"]:
        values = payload.get(key)

        if isinstance(values, list):
            out.extend([item for item in values if isinstance(item, dict)])

    return out


def count_study_mechanical(payload: Dict[str, Any]) -> int:
    total = 0

    for question in collect_study_questions(payload):
        text = norm(question.get("question"))

        if any(pattern in text for pattern in MECHANICAL_STUDY_PATTERNS):
            total += 1

    return total


def count_quiz_mechanical(payload: Dict[str, Any]) -> int:
    total = 0

    for question in collect_quiz_questions(payload):
        text = norm(question.get("question"))

        if any(pattern in text for pattern in MECHANICAL_QUIZ_PATTERNS):
            total += 1

    return total


def count_quiz_duplicate_questions(payload: Dict[str, Any]) -> int:
    questions = [norm(item.get("question")) for item in collect_quiz_questions(payload)]
    questions = [item for item in questions if item]

    seen: Set[str] = set()
    duplicates = 0

    for question in questions:
        if question in seen:
            duplicates += 1
        else:
            seen.add(question)

    return duplicates


def count_true_fact_distractors(payload: Dict[str, Any], source_facts: Set[str]) -> int:
    total = 0

    for question in collect_quiz_questions(payload):
        options = question.get("options")

        if not isinstance(options, list):
            continue

        correct_id = str(question.get("correct_option_id") or "").strip()

        for option in options:
            if not isinstance(option, dict):
                continue

            option_id = str(option.get("option_id") or "").strip()
            is_correct = bool(option.get("is_correct")) or bool(correct_id and option_id == correct_id)

            if is_correct:
                continue

            text = norm(option.get("text"))

            if text and text in source_facts:
                total += 1

    return total


def count_rough_explanations(payload: Dict[str, Any]) -> int:
    total = 0

    for question in collect_quiz_questions(payload):
        explanation = norm(
            question.get("explanation")
            or question.get("explanation_draft")
            or question.get("spiegazione")
        )

        if not explanation:
            continue

        if len(explanation) < 70:
            total += 1
            continue

        if any(explanation == pattern for pattern in ROUGH_EXPLANATION_PATTERNS):
            total += 1

    return total


def collect_correct_map(payload: Dict[str, Any]) -> Dict[str, str]:
    result: Dict[str, str] = {}

    for index, question in enumerate(collect_quiz_questions(payload), start=1):
        qid = str(question.get("question_id") or f"quiz_{index}")
        correct = str(question.get("correct_option_id") or "").strip()
        result[qid] = correct

    return result


def defect_snapshot(payload: Dict[str, Any], source_facts: Set[str]) -> Dict[str, int]:
    summary_card_bad = count_bad_patterns(payload)
    study_mechanical = count_study_mechanical(payload)
    quiz_mechanical = count_quiz_mechanical(payload)
    quiz_true_fact_distractors = count_true_fact_distractors(payload, source_facts)
    quiz_duplicate_questions = count_quiz_duplicate_questions(payload)
    rough_explanations = count_rough_explanations(payload)
    micro_concepts_sentence_punctuation = count_micro_concepts_with_sentence_punctuation(payload)

    return {
        "summary_card_bad_patterns": summary_card_bad,
        "study_mechanical_questions": study_mechanical,
        "quiz_mechanical_questions": quiz_mechanical,
        "quiz_true_fact_distractors": quiz_true_fact_distractors,
        "quiz_duplicate_questions": quiz_duplicate_questions,
        "quiz_rough_explanations": rough_explanations,
        "micro_concepts_sentence_punctuation": micro_concepts_sentence_punctuation,
        "total": (
            summary_card_bad
            + study_mechanical
            + quiz_mechanical
            + quiz_true_fact_distractors
            + quiz_duplicate_questions
            + rough_explanations
            + micro_concepts_sentence_punctuation
        ),
    }


def registry_motor_rows() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for index, spec in enumerate(registry.LEGACY_QUALITY_MOTORS, start=1):
        rows.append(
            {
                "index": index,
                "motor_id": getattr(spec, "motor_id", ""),
                "module_name": getattr(spec, "module_name", ""),
                "function_name": getattr(spec, "function_name", ""),
                "adapter_name": getattr(spec, "adapter_name", ""),
                "target_kind": getattr(spec, "target_kind", ""),
            }
        )

    return rows


def main() -> int:
    raw_payload = build_test_payload()
    source_facts = collect_source_facts(raw_payload)

    final_payload = registry.apply_legacy_quality_motors_v1(
        copy.deepcopy(raw_payload),
        context="phase5_10_2_final_registry_quality_snapshot",
    )

    raw_defects = defect_snapshot(raw_payload, source_facts)
    final_defects = defect_snapshot(final_payload, source_facts)

    raw_correct_map = collect_correct_map(raw_payload)
    final_correct_map = collect_correct_map(final_payload)

    registry_meta = final_payload.get("_legacy_quality_motor_registry_v1") or {}
    registry_motors_meta = registry_meta.get("motors") or {}

    motors = registry_motor_rows()

    errors: List[str] = []

    if len(motors) < 11:
        errors.append(f"Numero motori registry sospetto: {len(motors)}. Atteso almeno 11 dopo 5.10.1.")

    if raw_defects["total"] <= 0:
        errors.append("Il payload grezzo non contiene difetti misurabili: test non significativo.")

    if final_defects["total"] >= raw_defects["total"]:
        errors.append(f"Il registry non migliora il totale difetti: {raw_defects['total']} -> {final_defects['total']}")

    if final_defects["summary_card_bad_patterns"] != 0:
        errors.append(
            f"Summary/card bad pattern non azzerati: {raw_defects['summary_card_bad_patterns']} -> {final_defects['summary_card_bad_patterns']}"
        )

    if final_defects["quiz_true_fact_distractors"] != 0:
        errors.append(
            f"Distrattori quiz veri non azzerati: {raw_defects['quiz_true_fact_distractors']} -> {final_defects['quiz_true_fact_distractors']}"
        )

    if final_defects["micro_concepts_sentence_punctuation"] != 0:
        errors.append(
            f"Micro-concetti trasformati in frasi: {final_defects['micro_concepts_sentence_punctuation']}"
        )

    if raw_correct_map and final_correct_map and raw_correct_map != final_correct_map:
        errors.append("Mappa correct_option_id cambiata dopo registry.")

    status = "PASS" if not errors else "FAIL"

    report = {
        "report_name": "phase5_10_2_final_registry_quality_snapshot_v1",
        "status": status,
        "registry_motors_count": len(motors),
        "raw_defects": raw_defects,
        "final_defects": final_defects,
        "improvement_total": raw_defects["total"] - final_defects["total"],
        "correct_option_map_preserved": raw_correct_map == final_correct_map,
        "registry_motors": motors,
        "registry_meta_summary": {
            "motors_meta_count": len(registry_motors_meta),
            "known_text_defects_before": registry_meta.get("known_text_defects_before"),
            "known_text_defects_after": registry_meta.get("known_text_defects_after"),
        },
        "errors": errors,
        "notes": [
            "Snapshot diagnostico finale dopo 5.9.9 e 5.10.1.",
            "Non modifica motori: misura soltanto l'effetto del registry completo.",
            "Il payload usato contiene difetti noti in summary/card, study questions e quiz.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.10.2 — Final Registry Quality Snapshot V1\n")
    lines.append(f"- Status: `{status}`")
    lines.append(f"- Registry motors count: `{len(motors)}`")
    lines.append(f"- Raw total defects: `{raw_defects['total']}`")
    lines.append(f"- Final total defects: `{final_defects['total']}`")
    lines.append(f"- Improvement total: `{raw_defects['total'] - final_defects['total']}`")
    lines.append(f"- Correct option map preserved: `{raw_correct_map == final_correct_map}`")
    lines.append("")
    lines.append("## Difetti misurati\n")
    lines.append("| Area | Raw | Final |")
    lines.append("|---|---:|---:|")

    for key in [
        "summary_card_bad_patterns",
        "study_mechanical_questions",
        "quiz_mechanical_questions",
        "quiz_true_fact_distractors",
        "quiz_duplicate_questions",
        "quiz_rough_explanations",
        "micro_concepts_sentence_punctuation",
        "total",
    ]:
        lines.append(f"| `{key}` | {raw_defects[key]} | {final_defects[key]} |")

    lines.append("")
    lines.append("## Motori registry\n")
    lines.append("| # | Motor ID | Adapter | Target |")
    lines.append("|---:|---|---|---|")

    for motor in motors:
        lines.append(
            f"| {motor['index']} | `{motor['motor_id']}` | `{motor['adapter_name']}` | `{motor['target_kind']}` |"
        )

    if errors:
        lines.append("")
        lines.append("## Errori\n")

        for error in errors:
            lines.append(f"- {error}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.10.2 FINAL REGISTRY QUALITY SNAPSHOT PASS" if status == "PASS" else "❌ FASE 5.10.2 FAIL")
    print(f"Registry motors count: {len(motors)}")
    print(f"Raw defects total: {raw_defects['total']}")
    print(f"Final defects total: {final_defects['total']}")
    print(f"Improvement total: {raw_defects['total'] - final_defects['total']}")
    print(f"Correct option map preserved: {raw_correct_map == final_correct_map}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    if status != "PASS":
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        raise AssertionError("Fase 5.10.2 fallita: vedi report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
