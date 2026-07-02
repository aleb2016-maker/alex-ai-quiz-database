#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Documento non trovato: {path}")
    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("Questo adapter V3.9.4U legge solo TXT/MD.")
    return path.read_text(encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description="Test pratico V3.9.4U Universal Split.")
    parser.add_argument("file")
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--out-dir", default="mini_llm/data/real_tests/test_v394u_universal_split")
    args = parser.parse_args()

    root = repo_root()
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    file_path = Path(args.file).expanduser().resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    start = time.perf_counter()

    try:
        raw_text = read_text(file_path)

        cleaner_path = root / "scripts/mini_llm_real_output_cleaner_v393.py"
        if cleaner_path.exists():
            cleaner = load_module(cleaner_path, "cleaner_v393_for_v394u")
            document_text = cleaner.clean_document_text(raw_text)
        else:
            document_text = raw_text

        registry = load_module(root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py", "registry_v394u_runtime")
        linguistic = load_module(root / "mini_llm/python/runtime/universal/mini_llm_universal_linguistic_core_v394u.py", "linguistic_v394u_runtime")
        question_core = load_module(root / "mini_llm/python/runtime/universal/mini_llm_universal_question_core_v394u.py", "question_v394u_runtime")
        relevance_core = load_module(root / "mini_llm/python/runtime/universal/mini_llm_universal_relevance_core_v394u.py", "relevance_v394u_runtime")

        profile = registry.detect_profile(document_text)
        queries = args.query or [
            "Quali sono i punti principali del documento?",
            "Che cosa devo ricordare?",
            "Quali rischi o problemi vengono spiegati nel documento?",
        ]

        expanded = question_core.expand_queries(queries, profile)
        answers: List[Dict[str, Any]] = []

        for row in expanded.get("queries", []):
            answers.append(
                relevance_core.build_answer(
                    row.get("original_query", ""),
                    row.get("expanded_query", ""),
                    document_text,
                    profile,
                )
            )

        answer_errors = []
        question_errors = []

        for answer in answers:
            answer_errors.extend(relevance_core.validate_answer_relevance(answer, profile))
            answer_errors.extend(linguistic.check_text(answer.get("answer", ""), profile))

        for row in expanded.get("queries", []):
            question_errors.extend(linguistic.check_question(row.get("expanded_query", ""), profile))

        errors = []
        if answer_errors:
            errors.append(f"answer_errors:{answer_errors}")
        if question_errors:
            errors.append(f"question_errors:{question_errors}")

        report = {
            "test": "mini_llm_practical_real_test_v394u_universal_split",
            "version": "V3.9.4U.1",
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
            "file": str(file_path),
            "profile": profile,
            "query_expansion": expanded,
            "answers": answers,
            "linguistic_core": linguistic.quality_report(" ".join(a.get("answer", "") for a in answers), profile),
            "total_ms": (time.perf_counter() - start) * 1000.0,
            "limits": [
                "Adapter V3.9.4U.1.",
                "Core universale separato dai profili.",
                "Non sostituisce ancora la pipeline principale.",
            ],
        }

    except Exception as exc:
        report = {
            "test": "mini_llm_practical_real_test_v394u_universal_split",
            "version": "V3.9.4U.1",
            "status": "ERROR",
            "errors": [str(exc)],
            "file": str(file_path),
            "total_ms": (time.perf_counter() - start) * 1000.0,
        }

    json_path = out_dir / "v394u_universal_split_report.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")

    return 0 if report.get("status") == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
