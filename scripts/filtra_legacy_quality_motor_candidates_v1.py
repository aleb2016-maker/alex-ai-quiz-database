from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

INPUT_JSON = ROOT / "reports" / "legacy_quality_motor_candidates_v1.json"
REPORT_JSON = ROOT / "reports" / "legacy_quality_motor_shortlist_v1.json"
REPORT_MD = ROOT / "reports" / "legacy_quality_motor_shortlist_v1.md"


EXCLUDE_FUNCTION_PARTS = [
    "scan_legacy_quality_motors_registry_candidates_v1",
    "filtra_legacy_quality_motor_candidates_v1",
    "test_",
    ".test_",
    "_test",
    "benchmark_",
    "load_module",
    "main",
    "read_document",
    "markdown_report",
    "write_pipeline_report",
    "patch_page",
    "create_fake_quiz",
    "check_output_dir",
    "__init__",
]


EXCLUDE_PATH_PARTS = [
    "/test_",
    "tests/",
    "benchmark",
    "reports/",
    "phase5_live_quality_bridge_v1.py",
    "legacy_quality_motor_registry_v1.py",
    "scan_legacy_quality_motors_registry_candidates_v1.py",
    "filtra_legacy_quality_motor_candidates_v1.py",
]


EXCLUDE_CLASSIFICATIONS = {
    "diagnostic_or_test",
}


PREFERRED_CLASSIFICATIONS = {
    "quality_cleaner_or_refiner",
    "possible_quality_motor",
}


HIGH_VALUE_MODULE_HINTS = [
    "rag_revisore_qualita_testuale",
    "rag_revisore_accordo_pronomi",
    "rag_revisore_naturalezza",
    "rag_cleaner_finale_universale",
    "rag_motore_test_riutilizzabile",
    "rag_motore_didattico_riutilizzabile",
    "rag_genera_output_da_kb_clean",
]


PREFERRED_FUNCTION_HINTS = [
    "refine_output",
    "refine_summary",
    "refine_study",
    "refine_cards",
    "improve_output",
    "improve_summary",
    "clean_output",
    "pulisci_qualita_linguistica_quiz",
]


def _excluded(item: dict[str, Any]) -> tuple[bool, str]:
    function_id = str(item.get("function_id", "")).lower()
    path = str(item.get("path", "")).lower()
    classification = str(item.get("classification", ""))

    if classification in EXCLUDE_CLASSIFICATIONS:
        return True, "classification_excluded"

    for part in EXCLUDE_FUNCTION_PARTS:
        if part in function_id:
            return True, f"function_part:{part}"

    for part in EXCLUDE_PATH_PARTS:
        if part in path:
            return True, f"path_part:{part}"

    if "backup" in function_id or ".bak" in path or "main_backup" in function_id:
        return True, "backup_like"

    if function_id.startswith("backend.motori_scrittura.build_phase5"):
        return True, "current_phase_builder"

    if "validate" in function_id or "valida" in function_id or "validator" in function_id or "gate" in function_id:
        return True, "validator_not_refiner"

    return False, ""


def _priority_score(item: dict[str, Any]) -> int:
    score = int(item.get("score", 0))
    function_id = str(item.get("function_id", "")).lower()
    classification = str(item.get("classification", ""))

    if classification in PREFERRED_CLASSIFICATIONS:
        score += 10

    for hint in HIGH_VALUE_MODULE_HINTS:
        if hint in function_id:
            score += 12

    for hint in PREFERRED_FUNCTION_HINTS:
        if hint in function_id:
            score += 8

    if function_id.startswith("backend.main.pulisci_qualita_linguistica_quiz"):
        score += 20

    if "refine_output" in function_id:
        score += 6

    if "improve_output" in function_id:
        score += 6

    if "clean_output" in function_id:
        score += 6

    return score


def main() -> int:
    if not INPUT_JSON.exists():
        raise FileNotFoundError(f"Report sorgente non trovato: {INPUT_JSON}")

    source = json.loads(INPUT_JSON.read_text(encoding="utf-8"))
    candidates = source.get("candidates", [])

    shortlist = []
    excluded = []

    seen = set()

    for item in candidates:
        if item.get("type") != "candidate":
            continue

        function_id = item.get("function_id")

        if not function_id or function_id in seen:
            continue

        seen.add(function_id)

        is_excluded, reason = _excluded(item)

        enriched = dict(item)
        enriched["exclude_reason"] = reason
        enriched["priority_score"] = _priority_score(item)

        if is_excluded:
            excluded.append(enriched)
            continue

        shortlist.append(enriched)

    shortlist.sort(
        key=lambda item: (
            -int(item.get("priority_score", 0)),
            -int(item.get("score", 0)),
            item.get("function_id", ""),
        )
    )

    report = {
        "report_name": "legacy_quality_motor_shortlist_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "source_report": str(INPUT_JSON.relative_to(ROOT)),
        "source_total_candidates": len(candidates),
        "shortlist_count": len(shortlist),
        "excluded_count": len(excluded),
        "shortlist": shortlist,
        "notes": [
            "Shortlist diagnostica: non collega ancora nessun motore.",
            "Sono esclusi test, benchmark, scanner, hook, registry, bridge e validator puri.",
            "I motori in shortlist devono passare una verifica adapter prima di entrare nel registry.",
        ],
    }

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Legacy quality motor shortlist V1\n")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Candidati sorgente: `{report['source_total_candidates']}`")
    lines.append(f"- Shortlist: `{report['shortlist_count']}`")
    lines.append(f"- Esclusi: `{report['excluded_count']}`")
    lines.append("")
    lines.append("| Priority | Score | Classe | Funzione | File:riga |")
    lines.append("|---:|---:|---|---|---|")

    for item in shortlist[:80]:
        lines.append(
            f"| {item.get('priority_score')} "
            f"| {item.get('score')} "
            f"| `{item.get('classification')}` "
            f"| `{item.get('function_id')}` "
            f"| `{item.get('path')}:{item.get('line')}` |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ LEGACY QUALITY MOTOR SHORTLIST V1 COMPLETATA")
    print(f"Sorgente candidati: {len(candidates)}")
    print(f"Shortlist: {len(shortlist)}")
    print(f"Esclusi: {len(excluded)}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    print("\nTOP 25:")
    for item in shortlist[:25]:
        print(
            f"- priority={item['priority_score']} | score={item['score']} | "
            f"{item['classification']} | {item['function_id']} | "
            f"{item['path']}:{item['line']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
