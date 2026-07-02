#!/usr/bin/env python3
"""
Mini LLM Document CLI V1.

Comandi:
- build   <file.txt|file.md>
- ask     <file.txt|file.md> "domanda"
- summary <file.txt|file.md>

Base tecnica:
- fast_document_qa_summary_v2_cache
- cache persistente per documento testuale

Limiti:
- supporta testo UTF-8, TXT, MD e PDF testuali;
- non legge ancora PDF direttamente;
- non fa OCR;
- Q&A e summary sono extractive;
- non applica ancora la regola riassunto 10% pagine / sinossi 1%.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path


SUPPORTED_SUFFIXES = {".txt", ".md", ".markdown", ".pdf"}


def load_runtime(root: Path):
    module_path = root / "mini_llm/python/runtime/fast_document_qa_summary_v2_cache.py"

    if not module_path.exists():
        raise FileNotFoundError(f"Runtime V2 cache non trovato: {module_path}")

    spec = importlib.util.spec_from_file_location(
        "fast_document_qa_summary_v2_cache",
        module_path,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare runtime: {module_path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def read_document(path: Path, root: Path) -> str:
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

        if not extractor_path.exists():
            raise FileNotFoundError(f"PDF extractor non trovato: {extractor_path}")

        spec = importlib.util.spec_from_file_location(
            "pdf_text_extractor_v1",
            extractor_path,
        )

        if spec is None or spec.loader is None:
            raise RuntimeError(f"Impossibile caricare PDF extractor: {extractor_path}")

        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        result = module.extract_pdf_text(path)

        if result.get("status") != "OK":
            raise ValueError(
                "PDF senza testo estraibile. "
                "Per PDF scannerizzati servirà il modulo OCR."
            )

        text = str(result.get("text", "")).strip()
    else:
        text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(f"Documento vuoto o senza testo estraibile: {path}")

    return text


def build_engine(root: Path, document_path: Path, max_words_per_chunk: int):
    module = load_runtime(root)
    text = read_document(document_path, root=root)

    cache_dir = root / "mini_llm/data/fast_runtime/cache_v2_user_docs"

    start = time.perf_counter()
    engine, cache_info = module.FastDocumentQASummaryCache.from_text_with_cache(
        text,
        cache_dir,
        max_words_per_chunk=max_words_per_chunk,
    )
    total_ms = (time.perf_counter() - start) * 1000.0

    return engine, cache_info, total_ms, len(text)


def command_build(args) -> int:
    root = Path(__file__).resolve().parents[1]
    document_path = Path(args.file).expanduser().resolve()

    engine, cache_info, total_ms, chars = build_engine(
        root,
        document_path,
        args.max_words_per_chunk,
    )

    payload = {
        "command": "build",
        "status": "OK",
        "file": str(document_path),
        "document_chars": chars,
        "chunks": len(engine.chunks),
        "cache": cache_info,
        "total_ms": total_ms,
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def command_ask(args) -> int:
    root = Path(__file__).resolve().parents[1]
    document_path = Path(args.file).expanduser().resolve()

    engine, cache_info, build_ms, chars = build_engine(
        root,
        document_path,
        args.max_words_per_chunk,
    )

    result = engine.ask(args.question, top_k=args.top_k)

    payload = {
        "command": "ask",
        "status": result.get("status"),
        "file": str(document_path),
        "document_chars": chars,
        "chunks": len(engine.chunks),
        "cache": cache_info,
        "build_or_load_ms": build_ms,
        "question": args.question,
        "answer": result.get("answer", ""),
        "answer_ms": result.get("elapsed_ms", 0.0),
        "matches": result.get("matches", []),
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    return 0 if result.get("status") == "OK" else 1


def command_summary(args) -> int:
    root = Path(__file__).resolve().parents[1]
    document_path = Path(args.file).expanduser().resolve()

    engine, cache_info, build_ms, chars = build_engine(
        root,
        document_path,
        args.max_words_per_chunk,
    )

    result = engine.summarize(max_sentences=args.max_sentences)

    payload = {
        "command": "summary",
        "status": result.get("status"),
        "file": str(document_path),
        "document_chars": chars,
        "chunks": len(engine.chunks),
        "cache": cache_info,
        "build_or_load_ms": build_ms,
        "summary": result.get("summary", ""),
        "summary_ms": result.get("elapsed_ms", 0.0),
        "sentences_used": result.get("sentences_used", 0),
    }

    print(json.dumps(payload, ensure_ascii=False, indent=2))

    return 0 if result.get("status") == "OK" else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Mini LLM Document CLI V1 - Q&A e riassunto veloce su TXT/MD/PDF testuali.",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    common_help = "Dimensione chunk in parole. Default: 90."

    build = sub.add_parser("build", help="Indicizza documento e crea/usa cache.")
    build.add_argument("file", help="Percorso file TXT/MD/PDF testuale.")
    build.add_argument("--max-words-per-chunk", type=int, default=90, help=common_help)
    build.set_defaults(func=command_build)

    ask = sub.add_parser("ask", help="Risponde a una domanda sul documento.")
    ask.add_argument("file", help="Percorso file TXT/MD/PDF testuale.")
    ask.add_argument("question", help="Domanda utente.")
    ask.add_argument("--top-k", type=int, default=4, help="Numero chunk recuperati.")
    ask.add_argument("--max-words-per-chunk", type=int, default=90, help=common_help)
    ask.set_defaults(func=command_ask)

    summary = sub.add_parser("summary", help="Genera riassunto extractive.")
    summary.add_argument("file", help="Percorso file TXT/MD/PDF testuale.")
    summary.add_argument("--max-sentences", type=int, default=8, help="Numero frasi nel riassunto.")
    summary.add_argument("--max-words-per-chunk", type=int, default=90, help=common_help)
    summary.set_defaults(func=command_summary)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        return args.func(args)
    except Exception as exc:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "error": str(exc),
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
