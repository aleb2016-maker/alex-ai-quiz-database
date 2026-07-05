from __future__ import annotations

import ast
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

SHORTLIST_JSON = ROOT / "reports" / "legacy_quality_motor_shortlist_v1.json"

REPORT_JSON = ROOT / "reports" / "legacy_quality_motor_version_families_v1.json"
REPORT_MD = ROOT / "reports" / "legacy_quality_motor_version_families_v1.md"


SCAN_ROOTS = [
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


EXCLUDED_NAME_PARTS = [
    ".bak",
    "backup",
    "main_backup",
    "old_backup",
    "deprecated_backup",
]


QUALITY_HINTS = [
    "qualita",
    "quality",
    "revisore",
    "refine",
    "clean",
    "cleaner",
    "pulisci",
    "rifinisci",
    "motore",
    "didattico",
    "testuale",
    "naturalezza",
    "accordo",
    "pronomi",
    "antikeyword",
    "study",
    "quiz",
    "domande",
    "summary",
    "riassunto",
    "cards",
    "gate",
    "validator",
    "valida",
]


VERSION_TOKEN_RE = re.compile(
    r"(?i)^v\d+(?:[._]?\d+)*(?:[a-z])?(?:\d+[a-z]?)?$"
)

VERSION_IN_NAME_RE = re.compile(
    r"(?i)(?:^|[_-])(v\d+(?:[._]?\d+)*(?:[a-z])?(?:\d+[a-z]?)?)(?=$|[_-])"
)


def _is_excluded(path: Path) -> bool:
    parts = set(path.parts)

    if parts & EXCLUDED_PARTS:
        return True

    lower = str(path).lower()

    for part in EXCLUDED_NAME_PARTS:
        if part in lower:
            return True

    return False


def _module_name(path: Path) -> str | None:
    try:
        rel = path.relative_to(ROOT)
    except ValueError:
        return None

    if rel.suffix != ".py":
        return None

    return ".".join(rel.with_suffix("").parts)


def _version_tokens_from_stem(stem: str) -> list[str]:
    tokens = []

    for raw in re.split(r"[_-]+", stem):
        if VERSION_TOKEN_RE.match(raw):
            tokens.append(raw)

    for found in VERSION_IN_NAME_RE.findall(stem):
        if found not in tokens:
            tokens.append(found)

    return tokens


def _family_from_stem(stem: str) -> str:
    parts = re.split(r"[_-]+", stem)

    kept = []

    for part in parts:
        if VERSION_TOKEN_RE.match(part):
            continue

        kept.append(part)

    family = "_".join(kept)
    family = re.sub(r"_+", "_", family).strip("_")

    return family or stem


def _looks_relevant(path: Path, stem: str) -> bool:
    haystack = f"{path} {stem}".lower()

    return any(hint in haystack for hint in QUALITY_HINTS)


def _function_names(path: Path) -> list[dict[str, Any]]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="ignore")

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return []

    functions = []

    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            name_lower = node.name.lower()

            if any(hint in name_lower for hint in QUALITY_HINTS):
                functions.append(
                    {
                        "name": node.name,
                        "line": node.lineno,
                    }
                )

    return sorted(functions, key=lambda item: item["line"])


def _load_shortlist_function_ids() -> set[str]:
    if not SHORTLIST_JSON.exists():
        return set()

    try:
        data = json.loads(SHORTLIST_JSON.read_text(encoding="utf-8"))
    except Exception:
        return set()

    out = set()

    for item in data.get("shortlist", []):
        fid = item.get("function_id")

        if isinstance(fid, str):
            out.add(fid)

    return out


def main() -> int:
    shortlist_ids = _load_shortlist_function_ids()

    families: dict[str, dict[str, Any]] = {}

    for root in SCAN_ROOTS:
        if not root.exists():
            continue

        for path in root.rglob("*.py"):
            if _is_excluded(path):
                continue

            stem = path.stem

            versions = _version_tokens_from_stem(stem)

            if not versions:
                continue

            if not _looks_relevant(path, stem):
                continue

            module = _module_name(path)

            if not module:
                continue

            family = _family_from_stem(stem)
            functions = _function_names(path)

            module_function_ids = {
                f"{module}.{fn['name']}"
                for fn in functions
            }

            in_shortlist = bool(module_function_ids & shortlist_ids)

            entry = families.setdefault(
                family,
                {
                    "family": family,
                    "files_count": 0,
                    "versions": [],
                    "files": [],
                    "in_shortlist": False,
                    "quality_functions_count": 0,
                },
            )

            entry["files_count"] += 1
            entry["in_shortlist"] = entry["in_shortlist"] or in_shortlist
            entry["quality_functions_count"] += len(functions)

            for version in versions:
                if version not in entry["versions"]:
                    entry["versions"].append(version)

            entry["files"].append(
                {
                    "path": str(path.relative_to(ROOT)),
                    "module": module,
                    "stem": stem,
                    "versions": versions,
                    "quality_functions": functions[:20],
                    "quality_functions_count": len(functions),
                    "in_shortlist": in_shortlist,
                }
            )

    family_list = list(families.values())

    for family in family_list:
        family["versions"] = sorted(
            family["versions"],
            key=lambda item: (
                len(item),
                item,
            ),
        )

        family["files"] = sorted(
            family["files"],
            key=lambda item: (
                item["path"],
            ),
        )

    family_list.sort(
        key=lambda item: (
            not item["in_shortlist"],
            -len(item["versions"]),
            -item["quality_functions_count"],
            item["family"],
        )
    )

    report = {
        "report_name": "legacy_quality_motor_version_families_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "families_count": len(family_list),
        "families": family_list,
        "notes": [
            "Mappa diagnostica: non modifica registry e non collega motori.",
            "Raggruppa file versionati per famiglia rimuovendo token tipo v3, v34e, v35c, v4004.",
            "Le famiglie in_shortlist=True hanno almeno una funzione già comparsa nella shortlist qualità.",
            "Serve a scegliere quale versione testare prima di inserirla nel registry.",
        ],
    }

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Legacy quality motor version families V1\n")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Famiglie trovate: `{len(family_list)}`")
    lines.append("")
    lines.append("| Shortlist | Versioni | Funzioni qualità | Famiglia | File principali |")
    lines.append("|---|---:|---:|---|---|")

    for family in family_list[:100]:
        files_preview = "<br>".join(
            f"`{item['path']}`"
            for item in family["files"][:4]
        )

        lines.append(
            f"| {'✅' if family['in_shortlist'] else ''} "
            f"| `{', '.join(family['versions'])}` "
            f"| {family['quality_functions_count']} "
            f"| `{family['family']}` "
            f"| {files_preview} |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ VERSION FAMILY MAP MOTORI LEGACY V1 COMPLETATA")
    print(f"Famiglie trovate: {len(family_list)}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    print("\nTOP 40 FAMIGLIE:")
    for family in family_list[:40]:
        print(
            f"- shortlist={'yes' if family['in_shortlist'] else 'no'} | "
            f"versions={family['versions']} | "
            f"functions={family['quality_functions_count']} | "
            f"family={family['family']}"
        )

        for item in family["files"][:3]:
            print(f"    {item['path']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
