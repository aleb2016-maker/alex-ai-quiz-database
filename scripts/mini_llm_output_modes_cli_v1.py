#!/usr/bin/env python3
"""
Mini LLM Output Modes CLI V1.

Permette di scegliere cosa generare da un documento reale:

--mode summary
--mode cards
--mode qa
--mode test
--mode full

Base:
- usa mini_llm_study_pack_current;
- current punta a Study Pack V3 Quality Gate;
- supporta TXT/MD/PDF testuali;
- non usa modelli locali lenti;
- mantiene test studente separato da answer key.

Limiti:
- niente OCR;
- structured/extractive;
- non ancora LLM neurale generativo;
- non ancora RAG lungo da 500 pagine.
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
MODES = {"summary", "cards", "qa", "test", "full"}


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
        extractor = load_module(extractor_path, "pdf_text_extractor_modes_cli_v1")
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


def load_current_engine(root: Path):
    current_path = root / "mini_llm/python/runtime/mini_llm_study_pack_current.py"
    return load_module(current_path, "mini_llm_study_pack_current_modes_cli_v1")


def build_full_payload(args: argparse.Namespace) -> Dict[str, Any]:
    root = repo_root()
    document_path = Path(args.file).expanduser().resolve()

    text = read_document(document_path, root)
    current_module = load_current_engine(root)

    start = time.perf_counter()

    engine = current_module.MiniLLMStudyPackCurrent(
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
        "cli": "mini_llm_output_modes_cli_v1",
        "mode": args.mode,
        "status": "OK" if pack.get("status") == "OK" else pack.get("status"),
        "file": str(document_path),
        "document_chars": len(text),
        "total_ms": total_ms,
        "pack": pack,
        "limits": [
            "TXT/MD/PDF testuali.",
            "No OCR.",
            "Structured/extractive.",
            "Non ancora RAG lungo da 500 pagine.",
            "Usa Study Pack Current V3.",
        ],
    }


def filtered_pack(pack: Dict[str, Any], mode: str, public: bool = True) -> Dict[str, Any]:
    base: Dict[str, Any] = {
        "engine": pack.get("engine"),
        "status": pack.get("status"),
        "elapsed_ms": pack.get("elapsed_ms"),
        "current": pack.get("current"),
        "counts": pack.get("counts"),
        "limits": pack.get("limits"),
    }

    if mode in {"summary", "full"}:
        base["summary"] = pack.get("summary")

    if mode in {"cards", "full"}:
        base["cards"] = pack.get("cards", [])

    if mode in {"qa", "full"}:
        base["qas"] = pack.get("qas", [])

    if mode in {"test", "full"}:
        base["student_test"] = pack.get("student_test", [])

        if not public:
            base["answer_key"] = pack.get("answer_key", [])
            base["internal_test"] = pack.get("test", [])

    return base


def public_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "cli": payload["cli"],
        "mode": payload["mode"],
        "status": payload["status"],
        "file": payload["file"],
        "document_chars": payload["document_chars"],
        "total_ms": payload["total_ms"],
        "pack": filtered_pack(payload["pack"], payload["mode"], public=True),
        "limits": payload["limits"],
    }


def internal_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    copied = dict(payload)
    copied["pack"] = filtered_pack(payload["pack"], payload["mode"], public=False)
    return copied


def answer_key_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    pack = payload["pack"]

    return {
        "cli": payload["cli"],
        "mode": payload["mode"],
        "file": payload["file"],
        "engine": pack.get("engine"),
        "status": pack.get("status"),
        "answer_key": pack.get("answer_key", []),
        "internal_test": pack.get("test", []),
        "note": "Answer key interna separata dal test studente.",
    }


def format_markdown(payload: Dict[str, Any]) -> str:
    mode = payload["mode"]
    pack = payload["pack"]

    lines = [
        "# Mini LLM Output",
        "",
        f"- File: `{payload['file']}`",
        f"- Mode: `{mode}`",
        f"- Motore: `{pack.get('engine')}`",
        f"- Stato: `{pack.get('status')}`",
        f"- Tempo generazione: `{float(pack.get('elapsed_ms', 0.0)):.6f}` ms",
        "",
    ]

    if mode in {"summary", "full"}:
        lines.extend(
            [
                "## Riassunto",
                "",
                str(pack.get("summary", {}).get("summary", "")),
                "",
            ]
        )

    if mode in {"cards", "full"}:
        lines.extend(["## Card studio", ""])

        for index, card in enumerate(pack.get("cards", []), start=1):
            lines.append(f"### {index}. {card.get('title')}")
            lines.append("")
            lines.append(str(card.get("message", "")))
            lines.append("")

            for bullet in card.get("bullets", []):
                lines.append(f"- {bullet}")

            lines.append("")

    if mode in {"qa", "full"}:
        lines.extend(["## Domande e risposte", ""])

        for index, qa in enumerate(pack.get("qas", []), start=1):
            lines.append(f"### Domanda {index}")
            lines.append("")
            lines.append(f"**D:** {qa.get('question')}")
            lines.append("")
            lines.append(f"**R:** {qa.get('answer')}")
            lines.append("")

    if mode in {"test", "full"}:
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
                "### Nota test",
                "",
                "Questo test non mostra le risposte corrette.",
                "Le risposte sono disponibili solo nella answer key separata, se generata.",
                "",
            ]
        )

    lines.extend(
        [
            "## Limiti",
            "",
            "- Motore structured/extractive.",
            "- Non è ancora LLM neurale generativo.",
            "- Non usa OCR per PDF scannerizzati.",
            "- Non è ancora il RAG lungo da 500 pagine.",
            "",
        ]
    )

    return "\n".join(lines)


def format_answer_key_markdown(payload: Dict[str, Any]) -> str:
    key = answer_key_payload(payload)

    lines = [
        "# Mini LLM Output - Answer Key",
        "",
        f"- File: `{key['file']}`",
        f"- Mode: `{key['mode']}`",
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


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Genera output selettivi: summary, cards, qa, test, full."
    )

    parser.add_argument("file", help="Percorso file TXT/MD/PDF testuale.")
    parser.add_argument(
        "--mode",
        choices=sorted(MODES),
        default="full",
        help="Tipo di output da generare.",
    )
    parser.add_argument(
        "--format",
        choices=["markdown", "public-json", "json", "answer-key-json", "answer-key-markdown"],
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
        payload = build_full_payload(args)
    except Exception as exc:
        error = {
            "cli": "mini_llm_output_modes_cli_v1",
            "status": "ERROR",
            "error": str(exc),
        }
        print(json.dumps(error, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    if args.format == "json":
        output = json.dumps(internal_payload(payload), ensure_ascii=False, indent=2)
    elif args.format == "public-json":
        output = json.dumps(public_payload(payload), ensure_ascii=False, indent=2)
    elif args.format == "answer-key-json":
        output = json.dumps(answer_key_payload(payload), ensure_ascii=False, indent=2)
    elif args.format == "answer-key-markdown":
        output = format_answer_key_markdown(payload)
    else:
        output = format_markdown(payload)

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
                    "cli": "mini_llm_output_modes_cli_v1",
                    "mode": args.mode,
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
