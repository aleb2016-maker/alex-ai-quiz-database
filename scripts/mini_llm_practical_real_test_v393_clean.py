#!/usr/bin/env python3
"""
Mini LLM Practical Real Test V3.9.3.1 Clean.

Esegue test pratico reale con:
- cleaner V3.9.3.1;
- RAG V3.9.1;
- Study Pack Current V3 su contesto safe;
- Real Quality Gate V3.9.2 obbligatorio.
"""

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
    if not path.exists():
        raise FileNotFoundError(f"Modulo non trovato: {path}")

    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def safe_first(items: Any) -> Dict[str, Any]:
    if isinstance(items, list) and items:
        first = items[0]
        if isinstance(first, dict):
            return first
    return {}


def read_document(path: Path, root: Path) -> str:
    practical_v391 = load_module(
        root / "scripts/mini_llm_practical_real_test_v391.py",
        "mini_llm_practical_real_test_v391_for_clean_v3931",
    )

    return practical_v391.read_document(path, root)


def markdown_report(report: Dict[str, Any]) -> str:
    diagnostics = report.get("diagnostics", {})
    cleaner = report.get("cleaner", {})
    targets = diagnostics.get("compression_targets", {})
    answers = report.get("answers", [])
    summary = report.get("progressive_summary", {})
    study = report.get("study_pack", {})
    pack = study.get("study_pack", {}) if isinstance(study.get("study_pack", {}), dict) else {}
    gate = report.get("real_quality_gate", {})

    lines = [
        "# Mini LLM Practical Real Test V3.9.3.1 Clean",
        "",
        f"- Stato: **{report.get('status')}**",
        f"- File: `{report.get('file')}`",
        f"- Formato: `{report.get('file_suffix')}`",
        f"- Tempo totale: `{float(report.get('total_ms', 0.0)):.6f}` ms",
        "",
        "## Cleaner V3.9.3.1",
        "",
        f"- Stato cleaner: `{cleaner.get('status')}`",
        f"- Parole originali: `{cleaner.get('raw_words')}`",
        f"- Parole pulite: `{cleaner.get('cleaned_words')}`",
        f"- Parole rimosse: `{cleaner.get('removed_words')}`",
        "",
        "## Diagnostica RAG",
        "",
        f"- Engine: `{diagnostics.get('engine')}`",
        f"- Pagine logiche: `{diagnostics.get('pages')}`",
        f"- Parole: `{diagnostics.get('words')}`",
        f"- Frasi valide: `{diagnostics.get('sentences')}`",
        f"- Chunk sentence-safe: `{diagnostics.get('chunks')}`",
        f"- Build index: `{float(diagnostics.get('build_ms', 0.0)):.6f}` ms",
        "",
        "## Target compressione",
        "",
        f"- Riassunto qualità 10%: `{targets.get('quality_summary_pages_10_percent')}` pagine equivalenti",
        f"- Sintesi breve 1%: `{targets.get('brief_summary_pages_1_percent')}` pagine equivalenti",
        "",
        "## Real Quality Gate V3.9.2",
        "",
        f"- Stato gate: `{gate.get('status')}`",
        f"- Errori gate: `{gate.get('errors')}`",
        "",
        "## Risposte",
        "",
    ]

    for index, answer in enumerate(answers, start=1):
        lines.extend(
            [
                f"### Domanda {index}",
                "",
                f"**Q:** {answer.get('query')}",
                "",
                f"**Status:** `{answer.get('status')}`",
                "",
                str(answer.get("answer", "")),
                "",
            ]
        )

    lines.extend(
        [
            "## Riassunto progressivo pulito",
            "",
            f"- Status: `{summary.get('status')}`",
            f"- Errori qualità: `{summary.get('quality_errors')}`",
            f"- Frasi quality: `{summary.get('quality_sentences')}`",
            f"- Frasi brief: `{summary.get('brief_sentences')}`",
            "",
            "### Quality summary preview",
            "",
            str(summary.get("quality_summary", ""))[:3000],
            "",
            "### Brief summary",
            "",
            str(summary.get("brief_summary", ""))[:1600],
            "",
            "## Study Pack pulito",
            "",
            f"- Status: `{study.get('status')}`",
            f"- Semantic errors: `{study.get('semantic_errors')}`",
            f"- Counts: `{pack.get('counts')}`",
            "",
            "### Prima card",
            "",
            json.dumps(safe_first(pack.get("cards", [])), ensure_ascii=False, indent=2),
            "",
            "### Prima Q&A",
            "",
            json.dumps(safe_first(pack.get("qas", [])), ensure_ascii=False, indent=2),
            "",
            "### Primo test studente",
            "",
            json.dumps(safe_first(pack.get("student_test", [])), ensure_ascii=False, indent=2),
            "",
            "## Limiti",
            "",
            "- No OCR.",
            "- PDF scannerizzati non supportati.",
            "- Motore structured/extractive.",
            "- Non ancora LLM neurale generativo.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test pratico reale clean V3.9.3.1.")
    parser.add_argument("file")
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument(
        "--study-query",
        default="sicurezza informatica phishing backup password credenziali ransomware formazione procedure dati aziendali malware autenticazione",
    )
    parser.add_argument("--out-dir", default="mini_llm/data/real_tests/v393_clean_last")
    args = parser.parse_args()

    root = repo_root()
    file_path = Path(args.file).expanduser().resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    try:
        raw_text = read_document(file_path, root)

        cleaner_module = load_module(
            root / "scripts/mini_llm_real_output_cleaner_v393.py",
            "mini_llm_real_output_cleaner_v3931_runtime",
        )

        cleaned_text = cleaner_module.clean_document_text(raw_text)
        safe_context = cleaner_module.safe_study_context(cleaned_text, max_sentences=48)
        cleaner_diagnostics = cleaner_module.cleaner_diagnostics(raw_text, cleaned_text)

        (out_dir / "cleaned_input_preview.txt").write_text(cleaned_text, encoding="utf-8")
        (out_dir / "safe_study_context.txt").write_text(safe_context, encoding="utf-8")

        if cleaner_diagnostics.get("status") != "OK":
            raise ValueError(f"Cleaner output troppo corto o non valido: {cleaner_diagnostics}")

        rag_module = load_module(
            root / "mini_llm/python/runtime/mini_llm_long_document_rag_v391_semantic_repair.py",
            "mini_llm_long_document_rag_v391_for_clean_v3931",
        )

        rag = rag_module.MiniLLMLongDocumentRAGV391SemanticRepair(
            cleaned_text,
            words_per_page=320,
            max_words_per_chunk=180,
            overlap_sentences=1,
        )

        diagnostics = rag.diagnostics()

        queries = args.query or [
            "Quali sono i punti principali del documento?",
            "Che cosa devo ricordare sulla sicurezza informatica?",
            "Quali rischi vengono spiegati nel documento?",
        ]

        answers: List[Dict[str, Any]] = [
            rag.answer_query(query, top_k=12, max_sentences=5)
            for query in queries
        ]

        progressive_summary = rag.progressive_summary(
            max_quality_sentences=40,
            max_brief_sentences=16,
        )

        current_module = load_module(
            root / "mini_llm/python/runtime/mini_llm_study_pack_current.py",
            "mini_llm_study_pack_current_for_v3931",
        )

        pack = current_module.generate_study_pack(safe_context)

        study_pack = {
            "status": "OK" if pack.get("status") == "OK" else pack.get("status"),
            "query": args.study_query,
            "context": {
                "context_chars": len(safe_context),
                "sentences": len(cleaner_module.split_into_sentences(safe_context)),
                "quality_errors": [],
                "references": [],
            },
            "study_pack": pack,
            "semantic_errors": [],
            "elapsed_ms": pack.get("elapsed_ms"),
        }

        base_errors: List[str] = []

        if diagnostics.get("status") != "OK":
            base_errors.append(f"diagnostics_not_ok:{diagnostics.get('status')}")

        for answer in answers:
            if answer.get("status") != "OK":
                base_errors.append(f"answer_not_ok:{answer.get('query')}:{answer.get('status')}")

            if answer.get("quality_errors"):
                base_errors.append(f"answer_quality_errors:{answer.get('query')}:{answer.get('quality_errors')}")

        if progressive_summary.get("status") != "OK":
            base_errors.append(f"summary_not_ok:{progressive_summary.get('status')}")

        if progressive_summary.get("quality_errors"):
            base_errors.append(f"summary_quality_errors:{progressive_summary.get('quality_errors')}")

        if study_pack.get("status") != "OK":
            base_errors.append(f"study_pack_not_ok:{study_pack.get('status')}")

        provisional_status = "PASS" if not base_errors else "FAIL"

        report: Dict[str, Any] = {
            "test": "mini_llm_practical_real_test_v3931_clean",
            "status": provisional_status,
            "errors": base_errors,
            "file": str(file_path),
            "file_suffix": file_path.suffix.lower(),
            "cleaned_input_preview": str(out_dir / "cleaned_input_preview.txt"),
            "safe_study_context": str(out_dir / "safe_study_context.txt"),
            "total_ms": (time.perf_counter() - start) * 1000.0,
            "cleaner": cleaner_diagnostics,
            "diagnostics": diagnostics,
            "answers": answers,
            "progressive_summary": progressive_summary,
            "study_pack": study_pack,
            "limits": [
                "No OCR.",
                "PDF scannerizzati non supportati.",
                "Structured/extractive.",
                "Non ancora LLM neurale generativo.",
            ],
        }

        gate_module = load_module(
            root / "scripts/mini_llm_real_quality_gate_v392.py",
            "mini_llm_real_quality_gate_v392_for_clean_v3931",
        )

        gate_result = gate_module.validate_report(report)
        report["real_quality_gate"] = gate_result

        if gate_result.get("status") != "PASS":
            report["status"] = "FAIL"
            report["errors"] = base_errors + [f"real_quality_gate_fail:{gate_result.get('errors')}"]
        else:
            report["status"] = provisional_status

        report["total_ms"] = (time.perf_counter() - start) * 1000.0

    except Exception as exc:
        report = {
            "test": "mini_llm_practical_real_test_v3931_clean",
            "status": "ERROR",
            "errors": [str(exc)],
            "file": str(file_path),
            "file_suffix": file_path.suffix.lower(),
            "total_ms": (time.perf_counter() - start) * 1000.0,
        }

    json_path = out_dir / "practical_real_test_v393_clean_report.json"
    md_path = out_dir / "practical_real_test_v393_clean_report.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
