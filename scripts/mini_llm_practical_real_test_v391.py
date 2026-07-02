#!/usr/bin/env python3
"""
Mini LLM Practical Real Test V3.9.1.

Test pratico su file vero:
- TXT;
- MD / Markdown;
- PDF testuale.

Usa:
- Mini LLM Long Document RAG V3.9.1 Semantic Repair;
- Study Pack Current V3;
- Semantic Repair Gate.

Non è un test sintetico da 500 pagine.
Serve per vedere se il mini LLM funziona su un documento reale.

Limiti:
- no OCR;
- PDF scannerizzati non supportati;
- motore structured/extractive;
- non ancora LLM neurale generativo.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List


SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".pdf"}


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


def read_document(path: Path, root: Path) -> str:
    path = path.expanduser().resolve()

    if not path.exists():
        raise FileNotFoundError(f"Documento non trovato: {path}")

    if not path.is_file():
        raise IsADirectoryError(f"Il percorso non è un file: {path}")

    suffix = path.suffix.lower()

    if suffix not in SUPPORTED_SUFFIXES:
        raise ValueError(
            "Formato non supportato. Usa TXT, MD, MARKDOWN o PDF testuale. "
            f"File ricevuto: {path.name}"
        )

    if suffix == ".pdf":
        extractor_path = root / "mini_llm/python/runtime/pdf_text_extractor_v1.py"
        extractor = load_module(extractor_path, "pdf_text_extractor_practical_v391")
        result = extractor.extract_pdf_text(path)

        if result.get("status") != "OK":
            raise ValueError(
                "PDF senza testo estraibile. "
                "Per PDF scannerizzati serve OCR separato."
            )

        text = str(result.get("text", "")).strip()
    else:
        text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(f"Documento vuoto o senza testo estraibile: {path}")

    return text


def load_rag_engine(root: Path):
    path = root / "mini_llm/python/runtime/mini_llm_long_document_rag_v391_semantic_repair.py"
    return load_module(path, "mini_llm_long_document_rag_v391_practical")


def safe_first(items: Any) -> Dict[str, Any]:
    if isinstance(items, list) and items:
        first = items[0]
        if isinstance(first, dict):
            return first
    return {}


def markdown_report(report: Dict[str, Any]) -> str:
    diagnostics = report.get("diagnostics", {})
    targets = diagnostics.get("compression_targets", {})
    answers = report.get("answers", [])
    summary = report.get("progressive_summary", {})
    study = report.get("study_pack", {})
    pack = study.get("study_pack", {}) if isinstance(study.get("study_pack", {}), dict) else {}

    lines = [
        "# Mini LLM Practical Real Test V3.9.1",
        "",
        f"- Stato: **{report.get('status')}**",
        f"- File: `{report.get('file')}`",
        f"- Formato: `{report.get('file_suffix')}`",
        f"- Tempo totale: `{float(report.get('total_ms', 0.0)):.6f}` ms",
        "",
        "## Diagnostica documento",
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
        "## Risposte alle domande",
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
                f"**Errori qualità:** `{answer.get('quality_errors')}`",
                "",
                str(answer.get("answer", "")),
                "",
            ]
        )

    lines.extend(
        [
            "## Riassunto progressivo",
            "",
            f"- Status: `{summary.get('status')}`",
            f"- Errori qualità: `{summary.get('quality_errors')}`",
            f"- Frasi quality: `{summary.get('quality_sentences')}`",
            f"- Frasi brief: `{summary.get('brief_sentences')}`",
            f"- Tempo: `{float(summary.get('elapsed_ms', 0.0)):.6f}` ms",
            "",
            "### Quality summary preview",
            "",
            str(summary.get("quality_summary", ""))[:3000],
            "",
            "### Brief summary",
            "",
            str(summary.get("brief_summary", ""))[:1600],
            "",
            "## Study Pack da documento reale",
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
            "- Test pratico su documento reale.",
            "- No OCR.",
            "- PDF scannerizzati non supportati.",
            "- Motore structured/extractive.",
            "- Non ancora LLM neurale generativo.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Test pratico reale del Mini LLM Long Document RAG V3.9.1."
    )

    parser.add_argument("file", help="Documento reale TXT/MD/PDF testuale.")
    parser.add_argument(
        "--query",
        action="append",
        default=[],
        help="Domanda da fare al documento. Può essere ripetuta più volte.",
    )
    parser.add_argument(
        "--study-query",
        default="punti principali concetti importanti definizioni procedure esempi rischi vantaggi",
        help="Query larga per creare contesto Study Pack.",
    )
    parser.add_argument("--words-per-page", type=int, default=320)
    parser.add_argument("--max-words-per-chunk", type=int, default=180)
    parser.add_argument("--overlap-sentences", type=int, default=1)
    parser.add_argument("--max-quality-sentences", type=int, default=80)
    parser.add_argument("--max-brief-sentences", type=int, default=20)
    parser.add_argument(
        "--out-dir",
        default="mini_llm/data/real_tests/v391_last",
        help="Cartella output. È ignorata da git.",
    )

    args = parser.parse_args()

    root = repo_root()
    file_path = Path(args.file).expanduser().resolve()
    out_dir = (root / args.out_dir).resolve()

    out_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    try:
        text = read_document(file_path, root)
        module = load_rag_engine(root)

        rag = module.MiniLLMLongDocumentRAGV391SemanticRepair(
            text,
            words_per_page=args.words_per_page,
            max_words_per_chunk=args.max_words_per_chunk,
            overlap_sentences=args.overlap_sentences,
        )

        diagnostics = rag.diagnostics()

        queries = args.query or [
            "Quali sono i punti principali del documento?",
            "Quali concetti devo ricordare?",
            "Che cosa spiega il documento?",
        ]

        answers: List[Dict[str, Any]] = [
            rag.answer_query(query, top_k=12, max_sentences=5)
            for query in queries
        ]

        progressive_summary = rag.progressive_summary(
            max_quality_sentences=args.max_quality_sentences,
            max_brief_sentences=args.max_brief_sentences,
        )

        study_pack = rag.study_pack_from_query(
            args.study_query,
            top_k=40,
            max_chars=24000,
        )

        total_ms = (time.perf_counter() - start) * 1000.0

        errors: List[str] = []

        if diagnostics.get("status") != "OK":
            errors.append(f"diagnostics_not_ok:{diagnostics.get('status')}")

        if diagnostics.get("sentences", 0) < 5:
            errors.append(f"too_few_valid_sentences:{diagnostics.get('sentences')}")

        for answer in answers:
            if answer.get("status") != "OK":
                errors.append(f"answer_not_ok:{answer.get('query')}:{answer.get('status')}")

            if answer.get("quality_errors"):
                errors.append(f"answer_quality_errors:{answer.get('query')}:{answer.get('quality_errors')}")

        if progressive_summary.get("status") != "OK":
            errors.append(f"summary_not_ok:{progressive_summary.get('status')}")

        if progressive_summary.get("quality_errors"):
            errors.append(f"summary_quality_errors:{progressive_summary.get('quality_errors')}")

        if study_pack.get("status") != "OK":
            errors.append(f"study_pack_not_ok:{study_pack.get('status')}")

        if study_pack.get("semantic_errors"):
            errors.append(f"study_pack_semantic_errors:{study_pack.get('semantic_errors')}")

        status = "PASS" if not errors else "FAIL"

        report: Dict[str, Any] = {
            "test": "mini_llm_practical_real_test_v391",
            "status": status,
            "errors": errors,
            "file": str(file_path),
            "file_suffix": file_path.suffix.lower(),
            "total_ms": total_ms,
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

    except Exception as exc:
        report = {
            "test": "mini_llm_practical_real_test_v391",
            "status": "ERROR",
            "errors": [str(exc)],
            "file": str(file_path),
            "file_suffix": file_path.suffix.lower(),
            "total_ms": (time.perf_counter() - start) * 1000.0,
        }

    json_path = out_dir / "practical_real_test_v391_report.json"
    md_path = out_dir / "practical_real_test_v391_report.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_path.write_text(markdown_report(report), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
