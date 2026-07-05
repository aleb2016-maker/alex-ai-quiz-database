from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from scripts.mappa_phase5_9_4_existing_quiz_quality_motors_v1 import (
    scan_python_functions,
    registry_specs,
)


REPORT_JSON = ROOT / "reports" / "phase5_9_5_quiz_quality_motors_shortlist_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_5_quiz_quality_motors_shortlist_v1.md"


TRANSFORMER_WORDS = [
    "refine",
    "repair",
    "clean",
    "pulisci",
    "migliora",
    "correggi",
    "normalizza",
    "adatta",
    "adatta_domande",
    "genera",
    "genera_distrattori",
    "riscrivi",
    "migliora_spiegazione",
    "revisore",
    "quality",
    "qualita",
]

VALIDATOR_WORDS = [
    "valida",
    "validatore",
    "validate",
    "controlla",
    "audit",
    "review",
    "diagnosi",
    "verifica",
    "test_",
    "run_test",
    "assert",
]

NOISE_PATH_WORDS = [
    "/__pycache__/",
    "/.venv/",
    "/node_modules/",
    "_backup",
    "backup_",
    "main_backup",
    ".bak",
    "test_",
    "verifica_",
    "mappa_",
    "patch_",
    "audit_",
    "review_",
    "diagnosi_",
    "create_quiz_package.py",
    "rigenera",
    "installer",
]

GOOD_CAPABILITIES = [
    "quiz_question_naturalness",
    "strong_distractors",
    "grammar_accents_text_quality",
    "quiz_explanation_quality",
]


def read_source_segment(path: str, function_name: str, lineno: int) -> str:
    file_path = ROOT / path

    if not file_path.exists():
        return ""

    text = file_path.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return ""

    lines = text.splitlines()

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        if node.name != function_name:
            continue

        if getattr(node, "lineno", None) != lineno:
            continue

        start = max(node.lineno - 1, 0)
        end = min(getattr(node, "end_lineno", node.lineno), len(lines))

        return "\n".join(lines[start:end])

    return ""


def function_signature_info(path: str, function_name: str, lineno: int) -> Dict[str, Any]:
    file_path = ROOT / path

    info: Dict[str, Any] = {
        "args_count": None,
        "args": [],
        "returns_tuple_hint": False,
        "returns_dict_hint": False,
        "returns_list_hint": False,
        "has_any_annotation": False,
    }

    if not file_path.exists():
        return info

    text = file_path.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return info

    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue

        if node.name != function_name:
            continue

        if getattr(node, "lineno", None) != lineno:
            continue

        args = [arg.arg for arg in node.args.args]
        info["args"] = args
        info["args_count"] = len(args)
        info["has_any_annotation"] = bool(node.returns or any(arg.annotation for arg in node.args.args))

        segment = read_source_segment(path, function_name, lineno).lower()

        info["returns_tuple_hint"] = "return " in segment and (", meta" in segment or ", report" in segment or "tuple" in segment)
        info["returns_dict_hint"] = "return {" in segment or "dict[" in segment or "-> dict" in segment
        info["returns_list_hint"] = "return [" in segment or "list[" in segment or "-> list" in segment

        return info

    return info


def text_has_any(text: str, words: List[str]) -> bool:
    lower = text.lower()
    return any(word.lower() in lower for word in words)


def text_count_any(text: str, words: List[str]) -> int:
    lower = text.lower()
    return sum(lower.count(word.lower()) for word in words)


def classify_candidate(item: Dict[str, Any]) -> Dict[str, Any]:
    path = item.get("path", "")
    function_name = item.get("function_name", "")
    source = read_source_segment(path, function_name, item.get("lineno", 0))

    haystack = f"{path}\n{function_name}\n{source}"

    transformer_score = text_count_any(haystack, TRANSFORMER_WORDS)
    validator_score = text_count_any(haystack, VALIDATOR_WORDS)
    noise_score = text_count_any(path, NOISE_PATH_WORDS)

    capabilities = item.get("capabilities", {})
    good_capability_score = sum(int(capabilities.get(capability, 0)) for capability in GOOD_CAPABILITIES)

    signature = function_signature_info(path, function_name, item.get("lineno", 0))

    args_count = signature.get("args_count")
    adapter_difficulty = "unknown"

    if args_count == 0:
        adapter_difficulty = "hard_no_input"
    elif args_count == 1:
        adapter_difficulty = "easy_single_input"
    elif args_count in {2, 3}:
        adapter_difficulty = "medium_multi_input"
    elif isinstance(args_count, int) and args_count > 3:
        adapter_difficulty = "hard_many_inputs"

    is_registered = bool(item.get("registered_in_registry"))

    category = "REJECT_NOISE"
    reasons: List[str] = []

    if is_registered:
        category = "ALREADY_REGISTERED"
        reasons.append("Già presente nel registry.")

    elif noise_score > 0:
        category = "REJECT_NOISE"
        reasons.append("File/funzione probabilmente test, patch, review, audit, backup o demo.")

    elif validator_score > transformer_score and validator_score >= 2:
        category = "VALIDATOR_ONLY"
        reasons.append("Sembra più un validatore/controllore che un motore trasformativo.")

    elif transformer_score >= 2 and good_capability_score >= 8 and adapter_difficulty in {"easy_single_input", "medium_multi_input"}:
        category = "READY_TO_COMPAT_TEST"
        reasons.append("Sembra motore trasformativo con capability quiz e firma adattabile.")

    elif transformer_score >= 1 and good_capability_score >= 5:
        category = "MAYBE_NEEDS_MANUAL_REVIEW"
        reasons.append("Possibile motore utile, ma serve controllo manuale/adapter.")

    else:
        category = "LOW_PRIORITY"
        reasons.append("Segnale troppo debole per collegamento immediato.")

    return {
        **item,
        "shortlist_category": category,
        "shortlist_reasons": reasons,
        "transformer_score": transformer_score,
        "validator_score": validator_score,
        "noise_score": noise_score,
        "good_capability_score": good_capability_score,
        "signature": signature,
        "adapter_difficulty": adapter_difficulty,
    }


def main() -> int:
    registered = registry_specs()
    registered_ids = set(registered.keys())

    candidates = scan_python_functions()

    enriched: List[Dict[str, Any]] = []

    for item in candidates:
        motor_id = item.get("motor_id")
        item["registered_in_registry"] = motor_id in registered_ids
        item["registry_spec"] = registered.get(motor_id)

        enriched.append(classify_candidate(item))

    buckets: Dict[str, List[Dict[str, Any]]] = {}

    for item in enriched:
        buckets.setdefault(item["shortlist_category"], []).append(item)

    for category_items in buckets.values():
        category_items.sort(
            key=lambda item: (
                item.get("good_capability_score", 0),
                item.get("transformer_score", 0),
                item.get("score", 0),
            ),
            reverse=True,
        )

    ready = buckets.get("READY_TO_COMPAT_TEST", [])
    maybe = buckets.get("MAYBE_NEEDS_MANUAL_REVIEW", [])
    validators = buckets.get("VALIDATOR_ONLY", [])
    already = buckets.get("ALREADY_REGISTERED", [])
    noise = buckets.get("REJECT_NOISE", [])
    low = buckets.get("LOW_PRIORITY", [])

    report = {
        "report_name": "phase5_9_5_quiz_quality_motors_shortlist_v1",
        "status": "PASS_DIAGNOSTIC",
        "total_candidates": len(enriched),
        "counts": {
            "READY_TO_COMPAT_TEST": len(ready),
            "MAYBE_NEEDS_MANUAL_REVIEW": len(maybe),
            "VALIDATOR_ONLY": len(validators),
            "ALREADY_REGISTERED": len(already),
            "REJECT_NOISE": len(noise),
            "LOW_PRIORITY": len(low),
        },
        "ready_to_compat_test": ready[:80],
        "manual_review": maybe[:80],
        "validator_only_top": validators[:50],
        "already_registered": already[:50],
        "rejected_noise_count": len(noise),
        "low_priority_count": len(low),
        "recommended_next_phase": {
            "phase": "5.9.6",
            "action": "Eseguire compatibility test sui candidati READY_TO_COMPAT_TEST, uno per uno, senza collegarli ancora al registry.",
        },
        "notes": [
            "Diagnostico: non modifica registry e non collega motori.",
            "Filtra i candidati grezzi della Fase 5.9.4.",
            "Separa motori trasformativi da validator, test, review, audit, demo e frontend.",
            "I validator possono servire come quality gate, ma non migliorano direttamente l'output.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.9.5 — Quiz Quality Motors Shortlist V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Candidati totali analizzati: `{len(enriched)}`")
    lines.append("")
    lines.append("## Conteggi\n")
    lines.append("| Categoria | Conteggio |")
    lines.append("|---|---:|")

    for key, value in report["counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.append("")
    lines.append("## READY_TO_COMPAT_TEST\n")
    lines.append("| Score | File | Funzione | Adapter | Capability | Motivo |")
    lines.append("|---:|---|---|---|---|---|")

    for item in ready[:40]:
        lines.append(
            f"| {item.get('score')} "
            f"| `{item.get('path')}:{item.get('lineno')}` "
            f"| `{item.get('function_name')}` "
            f"| `{item.get('adapter_difficulty')}` "
            f"| `{', '.join(item.get('top_capabilities', []))}` "
            f"| {'; '.join(item.get('shortlist_reasons', []))} |"
        )

    lines.append("")
    lines.append("## MAYBE_NEEDS_MANUAL_REVIEW\n")
    lines.append("| Score | File | Funzione | Adapter | Capability | Motivo |")
    lines.append("|---:|---|---|---|---|---|")

    for item in maybe[:30]:
        lines.append(
            f"| {item.get('score')} "
            f"| `{item.get('path')}:{item.get('lineno')}` "
            f"| `{item.get('function_name')}` "
            f"| `{item.get('adapter_difficulty')}` "
            f"| `{', '.join(item.get('top_capabilities', []))}` "
            f"| {'; '.join(item.get('shortlist_reasons', []))} |"
        )

    lines.append("")
    lines.append("## VALIDATOR_ONLY più forti\n")
    lines.append("| Score | File | Funzione | Capability |")
    lines.append("|---:|---|---|---|")

    for item in validators[:25]:
        lines.append(
            f"| {item.get('score')} "
            f"| `{item.get('path')}:{item.get('lineno')}` "
            f"| `{item.get('function_name')}` "
            f"| `{', '.join(item.get('top_capabilities', []))}` |"
        )

    lines.append("")
    lines.append("## Prossimo step\n")
    lines.append("- Fase 5.9.6: test compatibilità sui candidati `READY_TO_COMPAT_TEST`.")
    lines.append("- Nessun collegamento automatico al registry.")
    lines.append("- Ogni candidato deve dimostrare almeno un miglioramento misurabile e zero peggioramenti.")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.5 SHORTLIST MOTORI QUIZ QUALITÀ COMPLETATA")
    print(f"Candidati totali: {len(enriched)}")
    print(json.dumps(report["counts"], ensure_ascii=False, indent=2))
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
