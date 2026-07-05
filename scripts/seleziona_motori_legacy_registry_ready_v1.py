from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

INPUT_JSON = ROOT / "reports" / "compatibilita_batch_motori_legacy_v1.json"

REPORT_JSON = ROOT / "reports" / "legacy_quality_motors_registry_ready_v1.json"
REPORT_MD = ROOT / "reports" / "legacy_quality_motors_registry_ready_v1.md"


def _decision(item: dict[str, Any]) -> tuple[str, str]:
    function_id = item.get("function_id", "")
    status = item.get("status")
    best = item.get("best_status")
    payload = item.get("best_payload")
    accepted = item.get("accepted") is True
    has_worsening = item.get("has_worsening_case") is True

    if "rag_revisore_naturalezza_antikeyword_v35i" in function_id and status == "skipped_signature":
        return (
            "NEEDS_ADAPTER",
            "Firma diversa: motore interessante, ma serve adapter dedicato prima del registry.",
        )

    if not accepted:
        if best in {"exception", "none_output", "none"}:
            return (
                "EXCLUDE_FOR_NOW",
                "Non ha prodotto output utile nel batch standard.",
            )

        return (
            "EXCLUDE_FOR_NOW",
            f"Non accettato dal batch: status={status}, best={best}.",
        )

    if has_worsening:
        return (
            "GUARDED_ONLY",
            "Ha almeno un caso di peggioramento: collegabile solo con guardia anti-peggioramento stretta.",
        )

    if best == "changed_no_worse":
        return (
            "READY_SAFE",
            f"Cambia output senza peggiorare sul payload migliore: {payload}.",
        )

    if best == "unchanged_no_worse":
        return (
            "LOW_PRIORITY",
            "Accetta input e non peggiora, ma nel batch non migliora/cambia output.",
        )

    return (
        "EXCLUDE_FOR_NOW",
        f"Decisione prudente: best={best}, status={status}.",
    )


def _adapter_hint(item: dict[str, Any]) -> str:
    function_id = item.get("function_id", "")
    payload = item.get("best_payload")

    if payload == "summary_dict":
        return "summary_dict_adapter"

    if payload == "phase5_full_output":
        return "phase5_full_output_adapter"

    if payload == "cards_list":
        return "cards_list_adapter"

    if payload == "study_list":
        return "study_list_adapter"

    if payload == "quiz_list":
        return "quiz_list_adapter"

    if "rag_revisore_naturalezza_antikeyword_v35i" in function_id:
        return "custom_signature_adapter_required"

    return "unknown_adapter"


def main() -> int:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Report batch non trovato: {INPUT_JSON}")

    source = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    results = source.get("results", [])

    selected: list[dict[str, Any]] = []

    for item in results:
        decision, reason = _decision(item)

        enriched = dict(item)
        enriched["registry_decision"] = decision
        enriched["decision_reason"] = reason
        enriched["adapter_hint"] = _adapter_hint(item)

        selected.append(enriched)

    order = {
        "READY_SAFE": 0,
        "GUARDED_ONLY": 1,
        "NEEDS_ADAPTER": 2,
        "LOW_PRIORITY": 3,
        "EXCLUDE_FOR_NOW": 4,
    }

    selected.sort(
        key=lambda item: (
            order.get(item["registry_decision"], 99),
            item.get("function_id", ""),
        )
    )

    groups: dict[str, list[dict[str, Any]]] = {}

    for item in selected:
        groups.setdefault(item["registry_decision"], []).append(item)

    report = {
        "report_name": "legacy_quality_motors_registry_ready_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_report": str(INPUT_JSON.relative_to(ROOT)),
        "total": len(selected),
        "counts": {key: len(value) for key, value in groups.items()},
        "selected": selected,
        "notes": [
            "Questo report non collega motori al registry.",
            "READY_SAFE può entrare nella prossima fase con adapter e guardia standard.",
            "GUARDED_ONLY richiede guardia anti-peggioramento obbligatoria.",
            "NEEDS_ADAPTER non è bocciato: serve studio firma/input-output dedicato.",
            "EXCLUDE_FOR_NOW non va integrato ora.",
        ],
    }

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Legacy quality motors registry-ready V1\n")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Totale valutati: `{report['total']}`")
    lines.append("")
    lines.append("## Conteggi\n")

    for key in ["READY_SAFE", "GUARDED_ONLY", "NEEDS_ADAPTER", "LOW_PRIORITY", "EXCLUDE_FOR_NOW"]:
        lines.append(f"- `{key}`: `{report['counts'].get(key, 0)}`")

    lines.append("")
    lines.append("| Decisione | Adapter hint | Best | Payload | Funzione | Motivo |")
    lines.append("|---|---|---|---|---|---|")

    for item in selected:
        lines.append(
            f"| `{item.get('registry_decision')}` "
            f"| `{item.get('adapter_hint')}` "
            f"| `{item.get('best_status')}` "
            f"| `{item.get('best_payload')}` "
            f"| `{item.get('function_id')}` "
            f"| {item.get('decision_reason')} |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ REGISTRY READY SELECTION V1 COMPLETATA")
    print(f"Totale valutati: {report['total']}")

    for key in ["READY_SAFE", "GUARDED_ONLY", "NEEDS_ADAPTER", "LOW_PRIORITY", "EXCLUDE_FOR_NOW"]:
        print(f"- {key}: {report['counts'].get(key, 0)}")

    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    print("\nREADY_SAFE:")
    for item in groups.get("READY_SAFE", []):
        print(f"- {item['function_id']} | adapter={item['adapter_hint']}")

    print("\nGUARDED_ONLY:")
    for item in groups.get("GUARDED_ONLY", []):
        print(f"- {item['function_id']} | adapter={item['adapter_hint']}")

    print("\nNEEDS_ADAPTER:")
    for item in groups.get("NEEDS_ADAPTER", []):
        print(f"- {item['function_id']} | adapter={item['adapter_hint']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
