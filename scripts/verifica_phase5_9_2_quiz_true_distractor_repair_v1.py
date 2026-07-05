from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.phase5_quiz_true_distractor_repair_v1 import (
    count_true_fact_distractors_v1,
    repair_payload_quiz_true_distractors_v1,
)

from scripts.verifica_phase5_8_quality_delta_ready_safe_motors_v1 import build_dirty_payload


REPORT_JSON = ROOT / "reports" / "phase5_9_2_quiz_true_distractor_repair_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_2_quiz_true_distractor_repair_v1.md"


def _quiz(payload: dict[str, Any]) -> list[dict[str, Any]]:
    value = payload.get("test_quiz")

    return value if isinstance(value, list) else []


def _correct_option_texts(payload: dict[str, Any]) -> list[str]:
    out = []

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
    counts = []

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


def main() -> int:
    before_payload = build_dirty_payload()
    after_payload, meta = repair_payload_quiz_true_distractors_v1(copy.deepcopy(before_payload))

    before_quiz = _quiz(before_payload)
    after_quiz = _quiz(after_payload)

    before_risk = count_true_fact_distractors_v1(before_quiz)
    after_risk = count_true_fact_distractors_v1(after_quiz)

    correct_before = _correct_option_texts(before_payload)
    correct_after = _correct_option_texts(after_payload)

    correct_counts_before = _correct_counts(before_payload)
    correct_counts_after = _correct_counts(after_payload)

    errors = []

    if before_risk <= 0:
        errors.append("Il payload test non contiene distrattori veri prima della riparazione.")

    if after_risk != 0:
        errors.append(f"Rischio distrattori veri non azzerato: {before_risk} -> {after_risk}")

    if correct_before != correct_after:
        errors.append("La risposta corretta è stata modificata.")

    if correct_counts_before != correct_counts_after:
        errors.append("Il numero di risposte corrette per domanda è cambiato.")

    if any(count != 1 for count in correct_counts_after):
        errors.append("Dopo la riparazione non c'è esattamente una risposta corretta per domanda.")

    if meta.get("replaced_distractors_count", 0) < before_risk:
        errors.append("Sono stati sostituiti meno distrattori veri di quelli rilevati.")

    status = "PASS" if not errors else "FAIL"

    report = {
        "report_name": "phase5_9_2_quiz_true_distractor_repair_v1",
        "status": status,
        "before_true_fact_distractors": before_risk,
        "after_true_fact_distractors": after_risk,
        "correct_option_texts_preserved": correct_before == correct_after,
        "correct_counts_before": correct_counts_before,
        "correct_counts_after": correct_counts_after,
        "repair_meta": meta,
        "errors": errors,
        "before_quiz": before_quiz,
        "after_quiz": after_quiz,
        "notes": [
            "Test separato: non collega ancora il motore al registry.",
            "Obiettivo minimo: rischio distrattori veri 3 -> 0.",
            "La risposta corretta deve restare invariata.",
            "La struttura quiz deve restare compatibile.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Fase 5.9.2 — Quiz True Distractor Repair V1\n")
    lines.append(f"- Status: `{status}`")
    lines.append(f"- Rischio distrattori veri: `{before_risk} -> {after_risk}`")
    lines.append(f"- Distrattori sostituiti: `{meta.get('replaced_distractors_count')}`")
    lines.append(f"- Risposta corretta preservata: `{correct_before == correct_after}`")
    lines.append("")
    lines.append("## Sostituzioni\n")
    lines.append("| Domanda | Opzione | Vecchio distrattore vero | Nuovo distrattore falso |")
    lines.append("|---:|---|---|---|")

    for item in meta.get("replacements", []):
        lines.append(
            f"| {item.get('question_index')} "
            f"| `{item.get('option_id')}` "
            f"| {item.get('old_text')} "
            f"| {item.get('new_text')} |"
        )

    if errors:
        lines.append("")
        lines.append("## Errori\n")

        for error in errors:
            lines.append(f"- {error}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.2 QUIZ TRUE DISTRACTOR REPAIR V1 PASS" if status == "PASS" else "❌ FASE 5.9.2 FAIL")
    print(f"Rischio distrattori veri: {before_risk} -> {after_risk}")
    print(f"Distrattori sostituiti: {meta.get('replaced_distractors_count')}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    if status != "PASS":
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        raise AssertionError("Fase 5.9.2 fallita: vedi report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
