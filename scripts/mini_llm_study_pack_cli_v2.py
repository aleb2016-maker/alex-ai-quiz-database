#!/usr/bin/env python3
"""
Mini LLM Study Pack CLI V2.

Uso:
- prende TXT/MD/PDF testuale;
- usa Study Pack V3 Quality Gate;
- genera Markdown studente senza risposte corrette;
- può generare answer key separata;
- genera JSON completo se richiesto.

Output:
- riassunto;
- card studio;
- domande/risposte;
- test studente;
- answer key separata opzionale.

Limiti:
- PDF solo testuale/selezionabile;
- no OCR;
- structured/extractive;
- non è ancora LLM neurale generativo.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict


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
        extractor = load_module(extractor_path, "pdf_text_extractor_v1_cli_v2")
        result = extractor.extract_pdf_text(path)

        if result.get("status") != "OK":
            raise ValueError(
                "PDF senza testo estraibile. "
                "Per PDF scannerizzati serve un modulo OCR separato."
            )

        text = str(result.get("text", "")).strip()
    else:
        text = path.read_text(encoding="utf-8").strip()

    if not text:
        raise ValueError(f"Documento vuoto o senza testo estraibile: {path}")

    return text


def load_study_pack_engine(root: Path):
    engine_path = root / "mini_llm/python/runtime/mini_llm_study_pack_v3_quality_gate.py"
    return load_module(engine_path, "mini_llm_study_pack_v3_quality_gate_cli")


def public_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    pack = payload["pack"]

    return {
        "cli": payload["cli"],
        "status": payload["status"],
        "file": payload["file"],
        "document_chars": payload["document_chars"],
        "total_ms": payload["total_ms"],
        "pack": {
            "engine": pack.get("engine"),
            "status": pack.get("status"),
            "elapsed_ms": pack.get("elapsed_ms"),
            "summary": pack.get("summary"),
            "cards": pack.get("cards"),
            "qas": pack.get("qas"),
            "student_test": pack.get("student_test"),
            "counts": pack.get("counts"),
            "limits": pack.get("limits"),
        },
        "limits": payload["limits"],
    }


def answer_key_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    pack = payload["pack"]

    return {
        "cli": payload["cli"],
        "file": payload["file"],
        "engine": pack.get("engine"),
        "status": pack.get("status"),
        "answer_key": pack.get("answer_key", []),
        "internal_test": pack.get("test", []),
        "counts": pack.get("counts"),
        "note": "Answer key interna separata dal test studente.",
    }


def format_student_markdown(payload: Dict[str, Any]) -> str:
    pack = payload["pack"]

    lines = [
        "# Mini LLM Study Pack",
        "",
        f"- File: `{payload['file']}`",
        f"- Motore: `{pack.get('engine')}`",
        f"- Stato: `{pack.get('status')}`",
        f"- Tempo generazione: `{float(pack.get('elapsed_ms', 0.0)):.6f}` ms",
        "",
        "## Riassunto",
        "",
        str(pack.get("summary", {}).get("summary", "")),
        "",
        "## Card studio",
        "",
    ]

    for index, card in enumerate(pack.get("cards", []), start=1):
        lines.append(f"### {index}. {card.get('title')}")
        lines.append("")
        lines.append(str(card.get("message", "")))
        lines.append("")

        for bullet in card.get("bullets", []):
            lines.append(f"- {bullet}")

        lines.append("")

    lines.extend(["## Domande e risposte", ""])

    for index, qa in enumerate(pack.get("qas", []), start=1):
        lines.append(f"### Domanda {index}")
        lines.append("")
        lines.append(f"**D:** {qa.get('question')}")
        lines.append("")
        lines.append(f"**R:** {qa.get('answer')}")
        lines.append("")

    lines.extend(["## Test", ""])

    for index, item in enumerate(pack.get("student_test", []), start=1):
        lines.append(f"### Domanda test {index}")
        lines.append("")
        lines.append(str(item.get("question", "")))
        lines.append("")

        for option_index, option in enumerate(item.get("options", []), start=1):
            lines.append(f"{option_index}. {option}")

        lines.append("")

    lines.extend(
        [
            "## Nota",
            "",
            "Questo test non mostra le risposte corrette.",
            "Le risposte sono disponibili solo nella answer key separata, se generata.",
            "",
            "## Limiti",
            "",
            "- Motore structured/extractive.",
            "- Non è ancora LLM neurale generativo.",
            "- Non usa OCR per PDF scannerizzati.",
            "- Non inventa contenuti fuori dal documento.",
            "",
        ]
    )

    return "\n".join(lines)


def format_answer_key_markdown(payload: Dict[str, Any]) -> str:
    key = answer_key_payload(payload)

    lines = [
        "# Mini LLM Study Pack - Answer Key",
        "",
        f"- File: `{key['file']}`",
        f"- Motore: `{key['engine']}`",
        "",
    ]

    for item in key.get("answer_key", []):
        correct_number = int(item.get("correct_index", 0)) + 1

        lines.extend(
            [
                f"## {item.get('id')}",
                "",
                f"- Risposta corretta: `{correct_number}`",
                f"- Testo risposta: {item.get('answer')}",
                f"- Spiegazione: {item.get('explanation')}",
                "",
            ]
        )

    return "\n".join(lines)


def build_payload(args: argparse.Namespace) -> Dict[str, Any]:
    root = repo_root()
    document_path = Path(args.file).expanduser().resolve()

    text = read_document(document_path, root)
    engine_module = load_study_pack_engine(root)

    start = time.perf_counter()

    engine = engine_module.MiniLLMStudyPackV3QualityGate(
        text,
        max_words_per_chunk=args.max_words_per_chunk,
    )

    pack = engine.generate_pack(
        max_summary_sentences=args.summary_sentences,
        max_cards=args.cards,
        max_qas=args.qas,
        max_test_questions=args.test_questions,
    )

    total_ms = (time.perf_counter() - start) * 1000.0

    return {
        "cli": "mini_llm_study_pack_cli_v2",
        "status": "OK" if pack.get("status") == "OK" else pack.get("status"),
        "file": str(document_path),
        "document_chars": len(text),
        "total_ms": total_ms,
        "pack": pack,
        "limits": [
            "TXT/MD/PDF testuali.",
            "No OCR.",
            "Structured/extractive.",
            "Test studente separato da answer key.",
            "Ultra rapido rispetto agli LLM locali testati.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera riassunto, card, Q&A e test da TXT/MD/PDF testuale con Study Pack V3."
    )

    parser.add_argument("file", help="Percorso file TXT/MD/PDF testuale.")
    parser.add_argument(
        "--format",
        choices=["json", "public-json", "markdown", "answer-key-json", "answer-key-markdown"],
        default="markdown",
        help="Formato output.",
    )
    parser.add_argument("--out", default="", help="Percorso file output opzionale.")
    parser.add_argument("--answer-key-out", default="", help="Percorso output answer key opzionale.")
    parser.add_argument("--summary-sentences", type=int, default=8)
    parser.add_argument("--cards", type=int, default=6)
    parser.add_argument("--qas", type=int, default=8)
    parser.add_argument("--test-questions", type=int, default=6)
    parser.add_argument("--max-words-per-chunk", type=int, default=90)

    args = parser.parse_args()

    try:
        payload = build_payload(args)
    except Exception as exc:
        error = {
            "cli": "mini_llm_study_pack_cli_v2",
            "status": "ERROR",
            "error": str(exc),
        }
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    if args.format == "json":
        output = json.dumps(payload, ensure_ascii=False, indent=2)
    elif args.format == "public-json":
        output = json.dumps(public_payload(payload), ensure_ascii=False, indent=2)
    elif args.format == "answer-key-json":
        output = json.dumps(answer_key_payload(payload), ensure_ascii=False, indent=2)
    elif args.format == "answer-key-markdown":
        output = format_answer_key_markdown(payload)
    else:
        output = format_student_markdown(payload)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")
    else:
        print(output)

    answer_key_written = ""

    if args.answer_key_out:
        key_path = Path(args.answer_key_out).expanduser().resolve()
        key_path.parent.mkdir(parents=True, exist_ok=True)

        if key_path.suffix.lower() in {".md", ".markdown"}:
            key_output = format_answer_key_markdown(payload)
        else:
            key_output = json.dumps(answer_key_payload(payload), ensure_ascii=False, indent=2)

        key_path.write_text(key_output + "\n", encoding="utf-8")
        answer_key_written = str(key_path)

    if args.out:
        print(
            json.dumps(
                {
                    "cli": "mini_llm_study_pack_cli_v2",
                    "status": payload.get("status"),
                    "output_file": str(Path(args.out).expanduser().resolve()),
                    "answer_key_file": answer_key_written,
                    "total_ms": payload.get("total_ms"),
                    "counts": payload.get("pack", {}).get("counts", {}),
                },
                ensure_ascii=False,
                indent=2,
            )
        )

    return 0 if payload.get("status") == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
