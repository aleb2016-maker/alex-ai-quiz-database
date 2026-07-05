from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


import backend.legacy_quality_motor_registry_v1 as registry

from scripts.verifica_phase5_10_universal_text_cleaner_summary_cards_v1 import (
    build_test_payload,
    count_bad_patterns,
    count_micro_concepts_with_sentence_punctuation,
    snapshot_protected_outputs,
    all_summary_card_texts,
)


REPORT_JSON = ROOT / "reports" / "phase5_10_1_summary_card_cleaner_registry_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_10_1_summary_card_cleaner_registry_v1.md"

MOTOR_ID = "backend.phase5_universal_text_cleaner_summary_cards_v1.universal_text_cleaner_summary_cards_payload_target_v1"


def apply_registry_without_cleaner(payload: Dict[str, Any]) -> Dict[str, Any]:
    original_motors = list(registry.LEGACY_QUALITY_MOTORS)

    filtered_motors = [
        spec for spec in original_motors
        if getattr(spec, "motor_id", "") != MOTOR_ID
    ]

    registry.LEGACY_QUALITY_MOTORS = filtered_motors

    try:
        return registry.apply_legacy_quality_motors_v1(
            copy.deepcopy(payload),
            context="phase5_10_1_registry_without_summary_card_cleaner",
        )
    finally:
        registry.LEGACY_QUALITY_MOTORS = original_motors


def changed_rows(before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    before_texts = all_summary_card_texts(before)
    after_texts = all_summary_card_texts(after)

    for index, before_text in enumerate(before_texts):
        if index >= len(after_texts):
            continue

        after_text = after_texts[index]

        if before_text != after_text:
            rows.append(
                {
                    "index": index,
                    "before": before_text,
                    "after": after_text,
                }
            )

    return rows


def main() -> int:
    raw_payload = build_test_payload()

    baseline_payload = apply_registry_without_cleaner(raw_payload)

    final_payload = registry.apply_legacy_quality_motors_v1(
        copy.deepcopy(raw_payload),
        context="phase5_10_1_summary_card_cleaner_registry",
    )

    raw_bad = count_bad_patterns(raw_payload)
    baseline_bad = count_bad_patterns(baseline_payload)
    final_bad = count_bad_patterns(final_payload)

    micro_punctuation_after = count_micro_concepts_with_sentence_punctuation(final_payload)

    protected_baseline = snapshot_protected_outputs(baseline_payload)
    protected_final = snapshot_protected_outputs(final_payload)

    registry_meta = final_payload.get("_legacy_quality_motor_registry_v1") or {}
    motors = registry_meta.get("motors") or {}
    motor_meta = motors.get(MOTOR_ID) or {}

    rows = changed_rows(baseline_payload, final_payload)

    errors: List[str] = []

    if raw_bad <= 0:
        errors.append("Il payload test grezzo non contiene bad pattern iniziali.")

    if baseline_bad <= 0:
        errors.append(
            f"La baseline registry senza cleaner non contiene bad pattern: raw={raw_bad}, baseline={baseline_bad}"
        )

    if final_bad != 0:
        errors.append(f"Bad pattern summary/cards non azzerati dal cleaner: baseline={baseline_bad} -> final={final_bad}")

    if final_bad >= baseline_bad:
        errors.append(f"Il cleaner non migliora rispetto alla baseline: {baseline_bad} -> {final_bad}")

    if micro_punctuation_after != 0:
        errors.append(f"I micro-concetti sono stati trasformati in frasi: {micro_punctuation_after}")

    if protected_baseline != protected_final:
        errors.append(
            "Quiz o study questions cambiano tra registry senza cleaner e registry con cleaner."
        )

    if not motor_meta:
        errors.append("Metadata cleaner summary/cards non trovato nel registry.")

    if motor_meta.get("status") not in {"ok", "partial"}:
        errors.append(f"Status cleaner summary/cards non ok: {motor_meta.get('status')}")

    if not isinstance(motor_meta.get("applied"), int) or motor_meta.get("applied", 0) <= 0:
        errors.append(f"Cleaner summary/cards non applicato: applied={motor_meta.get('applied')}")

    status = "PASS" if not errors else "FAIL"

    report = {
        "report_name": "phase5_10_1_summary_card_cleaner_registry_v1",
        "status": status,
        "motor_id": MOTOR_ID,
        "raw_bad_patterns": raw_bad,
        "baseline_bad_patterns_without_cleaner": baseline_bad,
        "final_bad_patterns_with_cleaner": final_bad,
        "micro_concept_sentence_punctuation_after": micro_punctuation_after,
        "protected_outputs_same_between_baseline_and_final": protected_baseline == protected_final,
        "motor_meta": motor_meta,
        "registry_meta_summary": {
            "motors_count": len(motors),
            "known_text_defects_before": registry_meta.get("known_text_defects_before"),
            "known_text_defects_after": registry_meta.get("known_text_defects_after"),
        },
        "changed_rows_baseline_to_final": rows,
        "errors": errors,
        "notes": [
            "Verifica corretta: confronta registry senza cleaner vs registry con cleaner.",
            "Gli altri motori registry possono modificare quiz/study: per questo il confronto protetto è baseline vs final.",
            "Il cleaner deve migliorare summary/cards senza cambiare quiz/study rispetto alla baseline registry.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.10.1 — Summary/Card Cleaner Registry V1\n")
    lines.append(f"- Status: `{status}`")
    lines.append(f"- Motore: `{MOTOR_ID}`")
    lines.append(f"- Raw bad pattern: `{raw_bad}`")
    lines.append(f"- Baseline senza cleaner: `{baseline_bad}`")
    lines.append(f"- Final con cleaner: `{final_bad}`")
    lines.append(f"- Protected outputs same baseline/final: `{protected_baseline == protected_final}`")
    lines.append(f"- Micro-concepts sentence punctuation after: `{micro_punctuation_after}`")
    lines.append(f"- Motore status: `{motor_meta.get('status')}`")
    lines.append(f"- Motore applied: `{motor_meta.get('applied')}`")
    lines.append("")
    lines.append("## Modifiche osservate baseline -> final\n")
    lines.append("| # | Baseline senza cleaner | Final con cleaner |")
    lines.append("|---:|---|---|")

    for item in rows:
        before = str(item["before"]).replace("\n", "<br>")
        after = str(item["after"]).replace("\n", "<br>")
        lines.append(f"| {item['index']} | {before} | {after} |")

    if errors:
        lines.append("")
        lines.append("## Errori\n")

        for error in errors:
            lines.append(f"- {error}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.10.1 SUMMARY/CARD CLEANER REGISTRY PASS" if status == "PASS" else "❌ FASE 5.10.1 FAIL")
    print(f"Raw bad pattern: {raw_bad}")
    print(f"Baseline senza cleaner: {baseline_bad}")
    print(f"Final con cleaner: {final_bad}")
    print(f"Protected outputs same baseline/final: {protected_baseline == protected_final}")
    print(f"Micro-concepts sentence punctuation after: {micro_punctuation_after}")
    print(f"Motore status: {motor_meta.get('status')}")
    print(f"Motore applied: {motor_meta.get('applied')}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    if status != "PASS":
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        raise AssertionError("Fase 5.10.1 fallita: vedi report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
