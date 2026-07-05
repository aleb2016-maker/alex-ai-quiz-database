from __future__ import annotations

import copy
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.legacy_quality_motor_registry_v1 import (
    LEGACY_QUALITY_MOTORS,
    apply_legacy_quality_motors_v1,
)

from scripts.verifica_phase5_8_quality_delta_ready_safe_motors_v1 import (
    area_metrics,
    build_dirty_payload,
    compare_metrics,
)


REPORT_JSON = ROOT / "reports" / "phase5_9_neutral_areas_root_cause_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_neutral_areas_root_cause_v1.md"


NEUTRAL_AREAS = ["summary", "quiz"]


TARGET_KIND_TO_AREA = {
    "summary": "summary",
    "quiz": "quiz",
    "cards": "cards",
    "study": "study",
    "full_output": "global",
}


def _safe_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _safe_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _motor_specs() -> dict[str, dict[str, Any]]:
    specs = {}

    for spec in LEGACY_QUALITY_MOTORS:
        motor_id = getattr(spec, "motor_id", "")
        specs[motor_id] = {
            "motor_id": motor_id,
            "module_name": getattr(spec, "module_name", ""),
            "function_name": getattr(spec, "function_name", ""),
            "adapter_name": getattr(spec, "adapter_name", ""),
            "target_kind": getattr(spec, "target_kind", ""),
            "area": TARGET_KIND_TO_AREA.get(getattr(spec, "target_kind", ""), "unknown"),
        }

    return specs


def _summarize_motor_execution(
    motor_id: str,
    spec_info: dict[str, Any],
    motor_meta: dict[str, Any],
) -> dict[str, Any]:
    targets = _safe_list(motor_meta.get("targets"))

    structural_rejections = [
        target for target in targets
        if target.get("structural_rejected") is True
    ]

    guarded_rejections = [
        target for target in targets
        if target.get("guarded_rejected") is True
    ]

    target_labels = [
        str(target.get("target"))
        for target in targets
        if target.get("target")
    ]

    reasons = []

    status = motor_meta.get("status")
    applied = motor_meta.get("applied", 0)
    changed = motor_meta.get("changed", 0)

    if status == "skipped_no_target":
        reasons.append("Il motore non trova un target compatibile nel payload.")

    if applied == 0:
        reasons.append("Il motore è registrato ma non viene applicato.")

    if applied and not changed:
        reasons.append("Il motore viene applicato ma non modifica il contenuto.")

    if structural_rejections:
        reasons.append("Almeno un output è rifiutato perché non preserva la struttura del target.")

    if guarded_rejections:
        reasons.append("Almeno un output è rifiutato dalla guardia anti-peggioramento.")

    if applied and changed and not structural_rejections and not guarded_rejections:
        reasons.append("Il motore modifica contenuto senza rifiuti; va verificato se modifica i difetti giusti.")

    if not reasons:
        reasons.append("Nessuna causa evidente dai metadata.")

    return {
        **spec_info,
        "status": status,
        "applied": applied,
        "changed": changed,
        "target_labels": target_labels,
        "targets_count": len(targets),
        "structural_rejections_count": len(structural_rejections),
        "guarded_rejections_count": len(guarded_rejections),
        "structural_reject_reasons": sorted({
            str(target.get("structural_reject_reason"))
            for target in structural_rejections
            if target.get("structural_reject_reason")
        }),
        "root_cause_notes": reasons,
        "raw_meta": motor_meta,
    }


def _area_root_cause(
    area: str,
    area_delta: dict[str, Any],
    motor_summaries: list[dict[str, Any]],
) -> dict[str, Any]:
    area_motors = [
        item for item in motor_summaries
        if item.get("area") == area
    ]

    global_motors = [
        item for item in motor_summaries
        if item.get("area") == "global"
    ]

    relevant_motors = area_motors + global_motors

    applied = [
        item for item in relevant_motors
        if isinstance(item.get("applied"), int) and item["applied"] > 0
    ]

    changed = [
        item for item in relevant_motors
        if isinstance(item.get("changed"), int) and item["changed"] > 0
    ]

    noops = [
        item for item in relevant_motors
        if isinstance(item.get("applied"), int)
        and item["applied"] > 0
        and item.get("changed", 0) == 0
    ]

    structural_rejected = [
        item for item in relevant_motors
        if item.get("structural_rejections_count", 0) > 0
    ]

    guarded_rejected = [
        item for item in relevant_motors
        if item.get("guarded_rejections_count", 0) > 0
    ]

    notes = []

    if not area_motors and area != "quiz":
        notes.append("Nessun motore specifico registrato per questa area.")

    if area == "quiz" and not area_motors:
        notes.append("Nessun motore target_kind=quiz registrato o applicato per correggere i distrattori.")

    if area_motors and not applied:
        notes.append("Esistono motori dell'area, ma non vengono applicati.")

    if noops:
        notes.append("Almeno un motore dell'area viene applicato ma non cambia nulla.")

    if changed and area_delta.get("neutral"):
        notes.append("Almeno un motore cambia contenuto, ma non riduce le metriche problematiche dell'area.")

    if structural_rejected:
        notes.append("Almeno un motore viene limitato dalla guardia struttura.")

    if guarded_rejected:
        notes.append("Almeno un motore viene limitato dalla guardia anti-peggioramento.")

    if area == "summary" and area_delta.get("bad_patterns_delta") == 0:
        notes.append("Il riassunto non riduce bad patterns: l'adapter summary non sta normalizzando difetti testuali misurati.")

    if area == "quiz" and area_delta.get("quiz_distractor_true_fact_risk_delta") == 0:
        notes.append("Il quiz non riduce il rischio distrattori veri: serve motore/adattatore quiz specifico.")

    if not notes:
        notes.append("Causa non determinata: servono metriche più fini o log intermedi.")

    return {
        "area": area,
        "area_delta": area_delta,
        "motors_specific_count": len(area_motors),
        "motors_relevant_count": len(relevant_motors),
        "applied_count": len(applied),
        "changed_count": len(changed),
        "noop_count": len(noops),
        "structural_rejected_count": len(structural_rejected),
        "guarded_rejected_count": len(guarded_rejected),
        "root_cause_notes": notes,
        "relevant_motors": relevant_motors,
    }


def main() -> int:
    before_payload = build_dirty_payload()
    after_payload = apply_legacy_quality_motors_v1(
        copy.deepcopy(before_payload),
        context="phase5_9_neutral_areas_root_cause",
    )

    area_deltas = {}

    for area in ["summary", "cards", "study", "quiz"]:
        before = area_metrics(before_payload, area)
        after = area_metrics(after_payload, area)
        area_deltas[area] = compare_metrics(before, after, area)

    registry_meta = _safe_dict(after_payload.get("_legacy_quality_motor_registry_v1"))
    motors_meta = _safe_dict(registry_meta.get("motors"))
    specs = _motor_specs()

    motor_summaries = []

    for motor_id, spec_info in specs.items():
        motor_meta = _safe_dict(motors_meta.get(motor_id))
        motor_summaries.append(
            _summarize_motor_execution(
                motor_id=motor_id,
                spec_info=spec_info,
                motor_meta=motor_meta,
            )
        )

    neutral_root_causes = [
        _area_root_cause(
            area=area,
            area_delta=area_deltas[area],
            motor_summaries=motor_summaries,
        )
        for area in NEUTRAL_AREAS
    ]

    recommendations = []

    summary_cause = next(item for item in neutral_root_causes if item["area"] == "summary")
    quiz_cause = next(item for item in neutral_root_causes if item["area"] == "quiz")

    if summary_cause["area_delta"]["neutral"]:
        recommendations.append(
            {
                "area": "summary",
                "priority": 2,
                "action": "Creare adapter summary più mirato o cleaner summary-specifico.",
                "why": "I motori summary vengono eseguiti, ma non riducono i bad patterns misurati.",
            }
        )

    if quiz_cause["area_delta"]["neutral"]:
        recommendations.append(
            {
                "area": "quiz",
                "priority": 1,
                "action": "Creare motore/adattatore quiz-specifico per sostituire distrattori che sono fatti veri.",
                "why": "Il rischio distrattori veri resta invariato.",
            }
        )

    recommendations.sort(key=lambda item: item["priority"])

    report = {
        "report_name": "phase5_9_neutral_areas_root_cause_v1",
        "status": "PASS_DIAGNOSTIC",
        "neutral_areas": NEUTRAL_AREAS,
        "area_deltas": area_deltas,
        "neutral_root_causes": neutral_root_causes,
        "motor_summaries": motor_summaries,
        "recommendations": recommendations,
        "registry_meta_summary": {
            "known_text_defects_before": registry_meta.get("known_text_defects_before"),
            "known_text_defects_after": registry_meta.get("known_text_defects_after"),
            "motors_count": len(motors_meta),
        },
        "notes": [
            "Diagnostico: non modifica il registry.",
            "Serve a capire perché summary e quiz restano neutri nella Fase 5.8.",
            "Distingue motori non applicati, no-op, cambi non utili, guardia struttura e guardia anti-peggioramento.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Fase 5.9 — Neutral Areas Root Cause V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Aree neutre analizzate: `{', '.join(NEUTRAL_AREAS)}`")
    lines.append("")
    lines.append("## Cause per area\n")
    lines.append("| Area | Motori area | Applicati | Cambiati | No-op | Structure reject | Guard reject | Causa sintetica |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|")

    for item in neutral_root_causes:
        lines.append(
            f"| `{item['area']}` "
            f"| {item['motors_specific_count']} "
            f"| {item['applied_count']} "
            f"| {item['changed_count']} "
            f"| {item['noop_count']} "
            f"| {item['structural_rejected_count']} "
            f"| {item['guarded_rejected_count']} "
            f"| {'; '.join(item['root_cause_notes'])} |"
        )

    lines.append("")
    lines.append("## Motori rilevanti\n")

    for area_item in neutral_root_causes:
        lines.append(f"\n### {area_item['area']}\n")
        lines.append("| Motore | Target kind | Status | Applied | Changed | Target | Note |")
        lines.append("|---|---|---|---:|---:|---|---|")

        for motor in area_item["relevant_motors"]:
            lines.append(
                f"| `{motor['motor_id']}` "
                f"| `{motor['target_kind']}` "
                f"| `{motor.get('status')}` "
                f"| {motor.get('applied')} "
                f"| {motor.get('changed')} "
                f"| `{', '.join(motor.get('target_labels', []))}` "
                f"| {'; '.join(motor.get('root_cause_notes', []))} |"
            )

    lines.append("")
    lines.append("## Raccomandazioni\n")

    for rec in recommendations:
        lines.append(
            f"- **Priorità {rec['priority']} — {rec['area']}**: {rec['action']} "
            f"Motivo: {rec['why']}"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9 NEUTRAL AREAS ROOT CAUSE V1 COMPLETATA")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")
    print(json.dumps({
        "status": report["status"],
        "recommendations": recommendations,
    }, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
