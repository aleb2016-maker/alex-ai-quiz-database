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


SHORTLIST_JSON = ROOT / "reports" / "phase5_9_5_quiz_quality_motors_shortlist_v1.json"
REPORT_JSON = ROOT / "reports" / "phase5_9_6_quiz_motor_compatibility_inspection_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_6_quiz_motor_compatibility_inspection_v1.md"


SIDE_EFFECT_WORDS = [
    "open(",
    ".write_text(",
    ".write_bytes(",
    "Path(",
    "subprocess",
    "os.system",
    "requests.",
    "urllib",
    "httpx",
    "ollama",
    "git ",
    "shutil.",
    "unlink(",
    "remove(",
    "rmdir(",
    "mkdir(",
    "input(",
    "print(",
]


TRANSFORM_OUTPUT_WORDS = [
    "return",
    "copy",
    "deepcopy",
    "replace",
    "append",
    "extend",
    "setdefault",
    "options",
    "opzioni",
    "question",
    "domanda",
    "explanation",
    "spiegazione",
    "answer",
    "risposta",
    "is_correct",
    "correct_option_id",
]


QUIZ_TARGET_WORDS = [
    "quiz",
    "test_quiz",
    "quiz_draft",
    "options",
    "opzioni",
    "question",
    "domanda",
    "explanation",
    "spiegazione",
    "distrattor",
    "is_correct",
    "correct_option_id",
    "source_facts",
]


VALIDATOR_ONLY_WORDS = [
    "error",
    "errors",
    "issue",
    "issues",
    "warning",
    "warnings",
    "validate",
    "valida",
    "controlla",
    "audit",
    "report",
    "score",
    "return []",
    "return False",
    "return True",
]


GOOD_FUNCTION_NAME_WORDS = [
    "refine",
    "repair",
    "clean",
    "pulisci",
    "migliora",
    "correggi",
    "normalizza",
    "adatta",
    "riscrivi",
    "natural",
    "explanation",
    "distrattori",
    "output",
]


BAD_FUNCTION_NAME_WORDS = [
    "main",
    "test",
    "validate",
    "valida",
    "controlla",
    "audit",
    "report",
    "crea_prompt",
    "crea_file",
    "analizza_motore",
]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_function_source(path: str, function_name: str, lineno: int) -> tuple[str, Dict[str, Any]]:
    file_path = ROOT / path

    info: Dict[str, Any] = {
        "exists": file_path.exists(),
        "syntax_ok": False,
        "args": [],
        "args_count": None,
        "has_return": False,
        "return_count": 0,
        "returns_constant_bool_or_none": False,
        "source_lines_count": 0,
    }

    if not file_path.exists():
        return "", info

    text = file_path.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(text)
        info["syntax_ok"] = True
    except SyntaxError:
        return "", info

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
        source = "\n".join(lines[start:end])

        info["args"] = [arg.arg for arg in node.args.args]
        info["args_count"] = len(info["args"])
        info["source_lines_count"] = end - start

        returns = [child for child in ast.walk(node) if isinstance(child, ast.Return)]
        info["return_count"] = len(returns)
        info["has_return"] = bool(returns)

        constant_returns = 0

        for ret in returns:
            value = ret.value

            if isinstance(value, ast.Constant) and value.value in {True, False, None}:
                constant_returns += 1

        info["returns_constant_bool_or_none"] = bool(returns) and constant_returns == len(returns)

        return source, info

    return "", info


def count_words(text: str, words: List[str]) -> int:
    lower = text.lower()
    return sum(lower.count(word.lower()) for word in words)


def inspect_candidate(item: Dict[str, Any]) -> Dict[str, Any]:
    path = item.get("path", "")
    function_name = item.get("function_name", "")
    lineno = int(item.get("lineno") or 0)

    source, info = read_function_source(path, function_name, lineno)
    haystack = f"{path}\n{function_name}\n{source}"

    side_effect_score = count_words(source, SIDE_EFFECT_WORDS)
    transform_score = count_words(haystack, TRANSFORM_OUTPUT_WORDS)
    quiz_target_score = count_words(haystack, QUIZ_TARGET_WORDS)
    validator_score = count_words(haystack, VALIDATOR_ONLY_WORDS)
    good_name_score = count_words(function_name, GOOD_FUNCTION_NAME_WORDS)
    bad_name_score = count_words(function_name, BAD_FUNCTION_NAME_WORDS)

    args_count = info.get("args_count")

    compatible_input = False
    input_reason = ""

    if args_count == 1:
        compatible_input = True
        input_reason = "Firma a 1 argomento: adattabile facilmente a quiz/payload."
    elif args_count in {2, 3}:
        compatible_input = True
        input_reason = "Firma a 2-3 argomenti: adattabile con wrapper controllato."
    else:
        compatible_input = False
        input_reason = f"Firma poco compatibile: args_count={args_count}."

    no_side_effect_risk = side_effect_score == 0

    looks_transformative = (
        info.get("has_return") is True
        and transform_score >= 4
        and quiz_target_score >= 4
        and not info.get("returns_constant_bool_or_none")
        and validator_score <= transform_score + 2
    )

    looks_validator_only = (
        validator_score > transform_score
        or info.get("returns_constant_bool_or_none") is True
        or bad_name_score > good_name_score
    )

    verdict = "REJECT"

    reasons: List[str] = []

    if not info.get("exists"):
        verdict = "REJECT"
        reasons.append("File non trovato.")

    elif not info.get("syntax_ok"):
        verdict = "REJECT"
        reasons.append("File non parseabile.")

    elif not compatible_input:
        verdict = "REJECT"
        reasons.append(input_reason)

    elif side_effect_score > 0:
        verdict = "REVIEW_SIDE_EFFECT_RISK"
        reasons.append("Possibili effetti collaterali: file, rete, subprocess, print o input.")

    elif looks_transformative and not looks_validator_only:
        verdict = "COMPAT_TEST_READY"
        reasons.append("Sembra trasformativo, orientato al quiz e con firma adattabile.")

    elif looks_transformative and looks_validator_only:
        verdict = "MANUAL_REVIEW_MIXED"
        reasons.append("Ha segnali trasformativi ma anche segnali da validatore/report.")

    elif looks_validator_only:
        verdict = "VALIDATOR_OR_REPORT_ONLY"
        reasons.append("Sembra più validatore/report che motore trasformativo.")

    else:
        verdict = "LOW_CONFIDENCE"
        reasons.append("Compatibile solo debolmente: servono ispezione o adapter manuale.")

    if input_reason:
        reasons.append(input_reason)

    return {
        "motor_id": item.get("motor_id"),
        "path": path,
        "function_name": function_name,
        "lineno": lineno,
        "original_score": item.get("score"),
        "top_capabilities": item.get("top_capabilities", []),
        "signature": info,
        "scores": {
            "side_effect_score": side_effect_score,
            "transform_score": transform_score,
            "quiz_target_score": quiz_target_score,
            "validator_score": validator_score,
            "good_name_score": good_name_score,
            "bad_name_score": bad_name_score,
        },
        "verdict": verdict,
        "reasons": reasons,
    }


def main() -> int:
    if not SHORTLIST_JSON.exists():
        raise FileNotFoundError(f"Shortlist 5.9.5 non trovata: {SHORTLIST_JSON}")

    shortlist = read_json(SHORTLIST_JSON)
    ready_candidates = shortlist.get("ready_to_compat_test") or []

    inspected = [inspect_candidate(item) for item in ready_candidates]

    buckets: Dict[str, List[Dict[str, Any]]] = {}

    for item in inspected:
        buckets.setdefault(item["verdict"], []).append(item)

    for items in buckets.values():
        items.sort(
            key=lambda item: (
                item["scores"]["quiz_target_score"],
                item["scores"]["transform_score"],
                item["original_score"] or 0,
            ),
            reverse=True,
        )

    compat_ready = buckets.get("COMPAT_TEST_READY", [])
    mixed = buckets.get("MANUAL_REVIEW_MIXED", [])
    side_effect = buckets.get("REVIEW_SIDE_EFFECT_RISK", [])
    validator_only = buckets.get("VALIDATOR_OR_REPORT_ONLY", [])
    low_confidence = buckets.get("LOW_CONFIDENCE", [])
    rejected = buckets.get("REJECT", [])

    report = {
        "report_name": "phase5_9_6_quiz_motor_compatibility_inspection_v1",
        "status": "PASS_DIAGNOSTIC",
        "input_candidates": len(ready_candidates),
        "counts": {
            "COMPAT_TEST_READY": len(compat_ready),
            "MANUAL_REVIEW_MIXED": len(mixed),
            "REVIEW_SIDE_EFFECT_RISK": len(side_effect),
            "VALIDATOR_OR_REPORT_ONLY": len(validator_only),
            "LOW_CONFIDENCE": len(low_confidence),
            "REJECT": len(rejected),
        },
        "compat_test_ready": compat_ready,
        "manual_review_mixed": mixed,
        "side_effect_risk": side_effect,
        "validator_or_report_only": validator_only,
        "low_confidence": low_confidence,
        "rejected": rejected,
        "recommended_next_phase": {
            "phase": "5.9.7",
            "action": "Eseguire test runtime solo sui candidati COMPAT_TEST_READY, con wrapper e payload controllato.",
        },
        "notes": [
            "Diagnostico statico: non importa né esegue i candidati.",
            "Serve a evitare di lanciare script con effetti collaterali.",
            "Solo COMPAT_TEST_READY passa alla fase runtime.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.9.6 — Quiz Motor Compatibility Inspection V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Candidati READY 5.9.5 analizzati: `{len(ready_candidates)}`")
    lines.append("")
    lines.append("## Conteggi\n")
    lines.append("| Verdetto | Conteggio |")
    lines.append("|---|---:|")

    for key, value in report["counts"].items():
        lines.append(f"| `{key}` | {value} |")

    lines.append("")
    lines.append("## COMPAT_TEST_READY\n")
    lines.append("| Original score | File | Funzione | Args | Quiz score | Transform score | Note |")
    lines.append("|---:|---|---|---|---:|---:|---|")

    for item in compat_ready[:40]:
        lines.append(
            f"| {item.get('original_score')} "
            f"| `{item.get('path')}:{item.get('lineno')}` "
            f"| `{item.get('function_name')}` "
            f"| `{', '.join(item.get('signature', {}).get('args', []))}` "
            f"| {item.get('scores', {}).get('quiz_target_score')} "
            f"| {item.get('scores', {}).get('transform_score')} "
            f"| {'; '.join(item.get('reasons', []))} |"
        )

    lines.append("")
    lines.append("## REVIEW_SIDE_EFFECT_RISK\n")
    lines.append("| Original score | File | Funzione | Side effect score | Note |")
    lines.append("|---:|---|---|---:|---|")

    for item in side_effect[:30]:
        lines.append(
            f"| {item.get('original_score')} "
            f"| `{item.get('path')}:{item.get('lineno')}` "
            f"| `{item.get('function_name')}` "
            f"| {item.get('scores', {}).get('side_effect_score')} "
            f"| {'; '.join(item.get('reasons', []))} |"
        )

    lines.append("")
    lines.append("## VALIDATOR_OR_REPORT_ONLY\n")
    lines.append("| Original score | File | Funzione | Validator score | Transform score | Note |")
    lines.append("|---:|---|---|---:|---:|---|")

    for item in validator_only[:30]:
        lines.append(
            f"| {item.get('original_score')} "
            f"| `{item.get('path')}:{item.get('lineno')}` "
            f"| `{item.get('function_name')}` "
            f"| {item.get('scores', {}).get('validator_score')} "
            f"| {item.get('scores', {}).get('transform_score')} "
            f"| {'; '.join(item.get('reasons', []))} |"
        )

    lines.append("")
    lines.append("## Prossimo step\n")
    lines.append("- Fase 5.9.7: runtime test solo sui candidati `COMPAT_TEST_READY`.")
    lines.append("- Nessun collegamento al registry finché non dimostrano miglioramento misurabile.")
    lines.append("- I validator/report restano utili come gate, ma non come motori trasformativi.")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.6 COMPATIBILITY INSPECTION COMPLETATA")
    print(json.dumps(report["counts"], ensure_ascii=False, indent=2))
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
