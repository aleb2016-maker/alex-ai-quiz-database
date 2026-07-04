import ast
import json
from datetime import datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

SEARCH_DIRS = [
    ROOT / "backend",
    ROOT / "scripts",
    ROOT / "rag",
    ROOT / "runtime",
    ROOT / "config",
]

EXCLUDE_PARTS = {
    ".venv",
    "__pycache__",
    ".git",
    "node_modules",
    "dist",
    "reports",
}

EXCLUDE_FILE_HINTS = {
    "test_",
    "patch_",
    "regressione_",
    ".bak",
}

KEYWORDS = {
    "grammatica": [
        "grammatica",
        "grammar",
        "ortografia",
        "apostrofo",
        "apostrofi",
        "accento",
        "accenti",
        "punteggiatura",
        "spazi",
        "pulizia",
        "clean",
        "normalize",
        "normalizza",
        "correggi",
        "correzione",
        "italiano",
        "frase",
        "frasi",
        "linguistico",
        "linguistica",
    ],
    "qualita": [
        "qualita",
        "quality",
        "validator",
        "validatore",
        "validate",
        "valida",
        "gate",
        "guard",
        "controllo",
        "anti",
        "fallback",
        "demo",
        "generic",
        "generico",
        "meccanica",
        "meccanico",
        "ripetizione",
        "duplicati",
    ],
    "didattica": [
        "didattica",
        "studio",
        "domande",
        "question",
        "quiz",
        "distrattori",
        "distractor",
        "spiegazione",
        "answer",
        "risposta",
        "test",
    ],
}


def safe_read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        try:
            return path.read_text(encoding="latin-1")
        except Exception:
            return ""
    except Exception:
        return ""


def should_skip(path: Path) -> bool:
    parts = set(path.parts)

    if EXCLUDE_PARTS.intersection(parts):
        return True

    name = path.name.lower()

    for hint in EXCLUDE_FILE_HINTS:
        if hint in name:
            return True

    return False


def classify_text(text: str):
    lowered = text.lower()
    categories = []

    for category, words in KEYWORDS.items():
        hits = [word for word in words if word in lowered]
        if hits:
            categories.append(
                {
                    "category": category,
                    "hits": hits[:12],
                    "score": len(hits),
                }
            )

    return categories


def count_required_args(fn: ast.FunctionDef) -> int:
    args = fn.args.args or []
    defaults = fn.args.defaults or []
    required = len(args) - len(defaults)

    # togli self/cls
    if args and args[0].arg in {"self", "cls"}:
        required -= 1

    return max(0, required)


def extract_candidates(path: Path):
    text = safe_read(path)
    if not text.strip():
        return []

    file_categories = classify_text(path.name + "\n" + text[:5000])
    if not file_categories:
        return []

    try:
        tree = ast.parse(text)
    except SyntaxError:
        return [
            {
                "file": str(path.relative_to(ROOT)),
                "type": "syntax_error_file_candidate",
                "name": path.name,
                "line": 1,
                "categories": file_categories,
                "reason": "Il file contiene parole chiave qualità ma non è parsabile con ast.",
            }
        ]

    candidates = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            name_text = node.name
            doc = ast.get_docstring(node) or ""
            combined = f"{name_text}\n{doc}"

            categories = classify_text(combined)
            if not categories:
                continue

            candidates.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "type": "function",
                    "name": node.name,
                    "line": node.lineno,
                    "required_args": count_required_args(node),
                    "total_args": len(node.args.args or []),
                    "categories": categories,
                    "reason": "Funzione con nome/docstring compatibile con motori qualità.",
                }
            )

        elif isinstance(node, ast.ClassDef):
            name_text = node.name
            doc = ast.get_docstring(node) or ""
            combined = f"{name_text}\n{doc}"

            categories = classify_text(combined)
            if not categories:
                continue

            methods = []
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_categories = classify_text(item.name + "\n" + (ast.get_docstring(item) or ""))
                    if method_categories:
                        methods.append(
                            {
                                "name": item.name,
                                "line": item.lineno,
                                "required_args": count_required_args(item),
                                "categories": method_categories,
                            }
                        )

            candidates.append(
                {
                    "file": str(path.relative_to(ROOT)),
                    "type": "class",
                    "name": node.name,
                    "line": node.lineno,
                    "methods": methods,
                    "categories": categories,
                    "reason": "Classe con nome/docstring compatibile con motori qualità.",
                }
            )

    if not candidates and file_categories:
        candidates.append(
            {
                "file": str(path.relative_to(ROOT)),
                "type": "file_candidate",
                "name": path.name,
                "line": 1,
                "categories": file_categories,
                "reason": "File con parole chiave qualità, ma senza funzioni/classi candidate evidenti.",
            }
        )

    return candidates


def main():
    all_candidates = []

    for directory in SEARCH_DIRS:
        if not directory.exists():
            continue

        for path in directory.rglob("*.py"):
            if should_skip(path):
                continue

            all_candidates.extend(extract_candidates(path))

    def score(candidate):
        total = 0
        for cat in candidate.get("categories", []):
            total += cat.get("score", 0)

        if candidate.get("type") == "function":
            total += 5
            if candidate.get("required_args") in {1, 2}:
                total += 3

        if candidate.get("type") == "class":
            total += 3

        return total

    all_candidates = sorted(all_candidates, key=score, reverse=True)

    report = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(ROOT),
        "total_candidates": len(all_candidates),
        "candidates": all_candidates,
    }

    json_path = REPORTS_DIR / "motori_qualita_esistenti_v1.json"
    md_path = REPORTS_DIR / "motori_qualita_esistenti_v1.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Motori qualità esistenti V1",
        "",
        f"- Generato: `{report['generated_at']}`",
        f"- Totale candidati: `{len(all_candidates)}`",
        "",
        "## Top candidati",
        "",
    ]

    for candidate in all_candidates[:80]:
        cats = []
        for cat in candidate.get("categories", []):
            cats.append(f"{cat['category']}({cat['score']})")

        lines.append(
            f"- `{candidate.get('type')}` `{candidate.get('name')}` "
            f"in `{candidate.get('file')}` riga `{candidate.get('line')}` "
            f"args_required=`{candidate.get('required_args', '-')}` "
            f"categorie=`{', '.join(cats)}`"
        )

        reason = candidate.get("reason")
        if reason:
            lines.append(f"  - {reason}")

        methods = candidate.get("methods") or []
        for method in methods[:8]:
            lines.append(
                f"  - metodo `{method['name']}` riga `{method['line']}` "
                f"args_required=`{method.get('required_args', '-')}`"
            )

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("✅ SCANSIONE MOTORI QUALITÀ COMPLETATA")
    print(f"Candidati trovati: {len(all_candidates)}")
    print(f"Report JSON: {json_path}")
    print(f"Report MD:   {md_path}")

    print("\nTOP 25:")
    for candidate in all_candidates[:25]:
        print(
            f"- {candidate.get('type')} {candidate.get('name')} "
            f"| {candidate.get('file')}:{candidate.get('line')} "
            f"| args_required={candidate.get('required_args', '-')}"
        )

    if not all_candidates:
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
