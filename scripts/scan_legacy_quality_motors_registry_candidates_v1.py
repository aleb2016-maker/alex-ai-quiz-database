from __future__ import annotations

import ast
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

REPORT_JSON = ROOT / "reports" / "legacy_quality_motor_candidates_v1.json"
REPORT_MD = ROOT / "reports" / "legacy_quality_motor_candidates_v1.md"


SEARCH_ROOTS = [
    ROOT / "backend",
    ROOT / "scripts",
    ROOT / "rag",
    ROOT / "mini_llm",
]


EXCLUDED_PARTS = {
    ".git",
    "__pycache__",
    ".venv",
    "node_modules",
    "reports",
    "dist",
    "build",
}


EXCLUDED_NAME_PATTERNS = [
    ".bak",
    "backup",
    "main_backup",
    "old_backup",
    "deprecated_backup",
]


QUALITY_KEYWORDS = [
    "qualita",
    "quality",
    "clean",
    "pulisci",
    "refine",
    "rifinisci",
    "validate",
    "valida",
    "validator",
    "gate",
    "guard",
    "quiz",
    "test",
    "study",
    "domande",
    "cards",
    "summary",
    "riassunto",
]


BAD_FUNCTION_KEYWORDS = [
    "main",
    "test_",
    "_test",
    "debug",
    "print",
    "demo",
]


def _is_excluded(path: Path) -> bool:
    parts = set(path.parts)

    if parts & EXCLUDED_PARTS:
        return True

    name_lower = path.name.lower()
    full_lower = str(path).lower()

    for pattern in EXCLUDED_NAME_PATTERNS:
        if pattern in name_lower or pattern in full_lower:
            return True

    return False


def _module_name_from_path(path: Path) -> str | None:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return None

    if rel.suffix != ".py":
        return None

    parts = list(rel.with_suffix("").parts)

    if not parts:
        return None

    return ".".join(parts)


def _score_function(file_path: Path, function_name: str, source_text: str, node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    score = 0

    haystack = " ".join(
        [
            file_path.name.lower(),
            str(file_path.parent).lower(),
            function_name.lower(),
            ast.get_docstring(node) or "",
            "\n".join(source_text[node.lineno - 1 : min(len(source_text), node.lineno + 20)]).lower(),
        ]
    )

    for keyword in QUALITY_KEYWORDS:
        if keyword in haystack:
            score += 3

    for bad in BAD_FUNCTION_KEYWORDS:
        if bad in function_name.lower():
            score -= 4

    if function_name.startswith("_"):
        score -= 2

    if "return" in haystack:
        score += 1

    if "json" in haystack or "dict" in haystack or "list" in haystack:
        score += 1

    return score


def _signature_info(node: ast.FunctionDef | ast.AsyncFunctionDef) -> dict[str, Any]:
    args = node.args

    positional = [arg.arg for arg in args.args]
    keyword_only = [arg.arg for arg in args.kwonlyargs]

    return {
        "positional_args": positional,
        "keyword_only_args": keyword_only,
        "args_count": len(positional),
        "has_varargs": args.vararg is not None,
        "has_kwargs": args.kwarg is not None,
    }


def _collect_candidates() -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            if _is_excluded(path):
                continue

            module_name = _module_name_from_path(path)

            if not module_name:
                continue

            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                text = path.read_text(encoding="utf-8", errors="ignore")

            try:
                tree = ast.parse(text)
            except SyntaxError as exc:
                candidates.append(
                    {
                        "type": "parse_error",
                        "path": str(path.relative_to(ROOT)),
                        "module": module_name,
                        "error": f"{exc.__class__.__name__}: {exc}",
                    }
                )
                continue

            lines = text.splitlines()

            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue

                score = _score_function(path, node.name, lines, node)

                if score < 6:
                    continue

                function_id = f"{module_name}.{node.name}"

                candidates.append(
                    {
                        "type": "candidate",
                        "function_id": function_id,
                        "module": module_name,
                        "function": node.name,
                        "path": str(path.relative_to(ROOT)),
                        "line": node.lineno,
                        "score": score,
                        "signature": _signature_info(node),
                        "docstring": ast.get_docstring(node) or "",
                    }
                )

    candidates = [item for item in candidates if item.get("type") == "candidate"]

    candidates.sort(
        key=lambda item: (
            -int(item.get("score", 0)),
            item.get("path", ""),
            item.get("line", 0),
        )
    )

    return candidates


def _classify_candidate(item: dict[str, Any]) -> str:
    function_id = item.get("function_id", "").lower()
    path = item.get("path", "").lower()

    if "backup" in function_id or ".bak" in path or "main_backup" in function_id:
        return "excluded_backup_like"

    if "test_" in function_id or path.startswith("tests/"):
        return "diagnostic_or_test"

    if "valida" in function_id or "validate" in function_id or "validator" in function_id or "gate" in function_id:
        return "validator_or_gate"

    if "pulisci" in function_id or "clean" in function_id or "refine" in function_id or "rifinisci" in function_id:
        return "quality_cleaner_or_refiner"

    if "quiz" in function_id or "study" in function_id or "domande" in function_id:
        return "quiz_or_study_motor"

    return "possible_quality_motor"


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    candidates = _collect_candidates()

    for item in candidates:
        item["classification"] = _classify_candidate(item)

    report = {
        "report_name": "legacy_quality_motor_candidates_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(ROOT),
        "total_candidates": len(candidates),
        "candidates": candidates,
        "notes": [
            "Scanner diagnostico: non modifica il codice.",
            "Esclude backup, .bak, main_backup, .venv, reports, dist, build.",
            "I candidati devono essere testati con adapter prima di entrare nel registry.",
        ],
    }

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: list[str] = []
    lines.append("# Legacy quality motor candidates V1\n")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Totale candidati: `{len(candidates)}`")
    lines.append("")
    lines.append("| Score | Classificazione | Funzione | File:riga |")
    lines.append("|---:|---|---|---|")

    for item in candidates[:80]:
        lines.append(
            f"| {item['score']} "
            f"| `{item['classification']}` "
            f"| `{item['function_id']}` "
            f"| `{item['path']}:{item['line']}` |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ LEGACY QUALITY MOTOR DISCOVERY MAP V1 COMPLETATA")
    print(f"Candidati trovati: {len(candidates)}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    for item in candidates[:20]:
        print(
            f"- score={item['score']} | {item['classification']} | "
            f"{item['function_id']} | {item['path']}:{item['line']}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
