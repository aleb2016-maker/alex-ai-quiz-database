from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.legacy_quality_motor_registry_v1 import apply_legacy_quality_motors_v1
from backend.phase5_quiz_true_distractor_repair_v1 import count_true_fact_distractors_v1
from scripts.verifica_phase5_8_quality_delta_ready_safe_motors_v1 import build_dirty_payload


REPORT_JSON = ROOT / "reports" / "phase5_9_3_quiz_repair_registry_integration_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_3_quiz_repair_registry_integration_v1.md"

MOTOR_ID = "backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1"


def _quiz(payload: dict[str, Any]) -> list[dict[str, Any]]:
    value = payload.get("test_quiz")
    return value if isinstance(value, list) else []


def _correct_option_texts(payload: dict[str, Any]) -> list[str]:
    out: list[str] = []

    for question in _quiz(payload):
        options = question.get("opzioni") or question.get("options") or []

        if not isinstance(options, list):
            continue

        correct_option_id = question.get("correct_option_id")

        for option in options:
            if not isinstance(option, dict):
                continue

            is_correct = option.get("is_correct") is True or option.get("option_id") == correct_option_id

            if is_correct:
                out.append(str(option.get("testo") or option.get("text") or ""))

    return out


def _correct_counts(payload: dict[str, Any]) -> list[int]:
    counts: list[int] = []

    for question in _quiz(payload):
        options = question.get("opzioni") or question.get("options") or []

        if not isinstance(options, list):
            continue

        correct_option_id = question.get("correct_option_id")
        count = 0

        for option in options:
            if not isinstance(option, dict):
                continue

            if option.get("is_correct") is True or option.get("option_id") == correct_option_id:
                count += 1

        counts.append(count)

    return counts


def _replacement_rows(before_payload: dict[str, Any], after_payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    before_quiz = _quiz(before_payload)
    after_quiz = _quiz(after_payload)

    for q_index, before_question in enumerate(before_quiz):
        if q_index >= len(after_quiz):
            continue

        after_question = after_quiz[q_index]

        before_options = before_question.get("opzioni") or before_question.get("options") or []
        after_options = after_question.get("opzioni") or after_question.get("options") or []

        if not isinstance(before_options, list) or not isinstance(after_options, list):
            continue

        for o_index, before_option in enumerate(before_options):
            if o_index >= len(after_options):
                continue

            after_option = after_options[o_index]

            if not isinstance(before_option, dict) or not isinstance(after_option, dict):
                continue

            before_text = str(before_option.get("testo") or before_option.get("text") or "")
            after_text = str(after_option.get("testo") or after_option.get("text") or "")

            if before_text == after_text:
                continue

            rows.append(
                {
                    "question_index": q_index,
                    "option_index": o_index,
                    "option_id": before_option.get("option_id"),
                    "before": before_text,
                    "after": after_text,
                }
            )

    return rows


def main() -> int:
    before_payload = build_dirty_payload()
    after_payload = apply_legacy_quality_motors_v1(
        copy.deepcopy(before_payload),
        context="phase5_9_3_quiz_repair_registry_integration",
    )

    before_risk = count_true_fact_distractors_v1(_quiz(before_payload))
    after_risk = count_true_fact_distractors_v1(_quiz(after_payload))

    correct_before = _correct_option_texts(before_payload)
    correct_after = _correct_option_texts(after_payload)

    correct_counts_before = _correct_counts(before_payload)
    correct_counts_after = _correct_counts(after_payload)

    registry_meta = after_payload.get("_legacy_quality_motor_registry_v1") or {}
    motors = registry_meta.get("motors") or {}
    motor_meta = motors.get(MOTOR_ID) or {}

    replacements = _replacement_rows(before_payload, after_payload)

    errors: list[str] = []

    if before_risk <= 0:
        errors.append("Il payload test non contiene distrattori veri prima del registry.")

    if after_risk != 0:
        errors.append(f"Il registry non azzera il rischio distrattori veri: {before_risk} -> {after_risk}")

    if not isinstance(motor_meta, dict) or not motor_meta:
        errors.append("Metadata del motore quiz repair non trovato nel registry.")

    if motor_meta.get("status") not in {"ok", "partial"}:
        errors.append(f"Status motore non ok: {motor_meta.get('status')}")

    if not isinstance(motor_meta.get("applied"), int) or motor_meta.get("applied", 0) <= 0:
        errors.append(f"Motore non applicato: applied={motor_meta.get('applied')}")

    if correct_before != correct_after:
        errors.append("La risposta corretta è cambiata dopo il registry.")

    if correct_counts_before != correct_counts_after:
        errors.append("Il numero di risposte corrette per domanda è cambiato dopo il registry.")

    if any(count != 1 for count in correct_counts_after):
        errors.append("Dopo il registry non c'è esattamente una risposta corretta per domanda.")

    if len(replacements) < before_risk:
        errors.append("Le sostituzioni osservate sono meno dei distrattori veri iniziali.")

    status = "PASS" if not errors else "FAIL"

    report = {
        "report_name": "phase5_9_3_quiz_repair_registry_integration_v1",
        "status": status,
        "motor_id": MOTOR_ID,
        "before_true_fact_distractors": before_risk,
        "after_true_fact_distractors": after_risk,
        "correct_option_texts_preserved": correct_before == correct_after,
        "correct_counts_before": correct_counts_before,
        "correct_counts_after": correct_counts_after,
        "replacements": replacements,
        "motor_meta": motor_meta,
        "registry_meta_summary": {
            "known_text_defects_before": registry_meta.get("known_text_defects_before"),
            "known_text_defects_after": registry_meta.get("known_text_defects_after"),
            "motors_count": len(motors),
        },
        "errors": errors,
        "notes": [
            "Verifica integrazione: controlla che il riparatore quiz lavori dentro il registry.",
            "Obiettivo: rischio distrattori veri 3 -> 0 anche dopo apply_legacy_quality_motors_v1.",
            "La risposta corretta deve restare invariata.",
            "La struttura quiz deve restare compatibile.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: list[str] = []
    lines.append("# Fase 5.9.3 — Quiz Repair Registry Integration V1\n")
    lines.append(f"- Status: `{status}`")
    lines.append(f"- Motore: `{MOTOR_ID}`")
    lines.append(f"- Rischio distrattori veri: `{before_risk} -> {after_risk}`")
    lines.append(f"- Motore status: `{motor_meta.get('status')}`")
    lines.append(f"- Motore applied: `{motor_meta.get('applied')}`")
    lines.append(f"- Risposta corretta preservata: `{correct_before == correct_after}`")
    lines.append("")
    lines.append("## Sostituzioni osservate nel registry\n")
    lines.append("| Domanda | Opzione | Prima | Dopo |")
    lines.append("|---:|---|---|---|")

    for item in replacements:
        lines.append(
            f"| {item.get('question_index')} "
            f"| `{item.get('option_id')}` "
            f"| {item.get('before')} "
            f"| {item.get('after')} |"
        )

    if errors:
        lines.append("")
        lines.append("## Errori\n")

        for error in errors:
            lines.append(f"- {error}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.3 QUIZ REPAIR REGISTRY INTEGRATION PASS" if status == "PASS" else "❌ FASE 5.9.3 FAIL")
    print(f"Rischio distrattori veri: {before_risk} -> {after_risk}")
    print(f"Motore status: {motor_meta.get('status')}")
    print(f"Motore applied: {motor_meta.get('applied')}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    if status != "PASS":
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        raise AssertionError("Fase 5.9.3 fallita: vedi report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
