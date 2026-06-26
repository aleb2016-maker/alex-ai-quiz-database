#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pipeline RAG Documenti Grandi V4.5

Scopo:
- orchestrare ingresso documenti grandi;
- creare manifest/chunks/testo estratto;
- collegare il report qualità ai motori già esistenti;
- NON rompere i motori vecchi;
- NON fingere qualità se i validatori non passano.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List, Dict, Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from rag_large_input_manager_v45 import process_input  # noqa: E402
from rag_quality_bridge_v45 import validate_quiz  # noqa: E402


def read_chunks(chunks_path: Path, limit: int = 12) -> List[Dict[str, Any]]:
    chunks: List[Dict[str, Any]] = []

    if not chunks_path.exists():
        return chunks

    with chunks_path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue

            try:
                chunks.append(json.loads(line))
            except json.JSONDecodeError:
                continue

            if len(chunks) >= limit:
                break

    return chunks


def create_document_map(output_dir: Path) -> None:
    """
    Crea una mappa tecnica minima del documento.

    Nota importante:
    questa NON sostituisce il motore riassunto/card già esistente.
    Serve solo come indice tecnico dei chunk creati dalla V4.5.
    """
    chunks_path = output_dir / "chunks.jsonl"
    chunks = read_chunks(chunks_path, limit=20)

    lines: List[str] = []
    lines.append("# Mappa tecnica documento RAG V4.5")
    lines.append("")
    lines.append(
        "Questo file conferma che il documento è stato letto e diviso in blocchi. "
        "Il riassunto didattico/grafico resta affidato ai motori già presenti nel progetto."
    )
    lines.append("")

    for chunk in chunks:
        preview = chunk.get("text", "").replace("\n", " ")
        preview = preview[:320].strip()
        lines.append(
            f"## {chunk.get('chunk_id')} — pagine {chunk.get('page_start')}-{chunk.get('page_end')}"
        )
        lines.append("")
        lines.append(f"- Caratteri: {chunk.get('char_count')}")
        lines.append(f"- Anteprima: {preview}...")
        lines.append("")

    (output_dir / "riassunto.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def create_study_question_skeleton(output_dir: Path) -> None:
    """
    Crea solo una struttura tecnica per future domande studio.

    Non genera domande finte.
    Non sostituisce il motore domande studio già esistente.
    """
    chunks_path = output_dir / "chunks.jsonl"
    chunks = read_chunks(chunks_path, limit=12)

    items = []

    for chunk in chunks:
        items.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "pages": [chunk.get("page_start"), chunk.get("page_end")],
                "status": "pronto_per_motore_domande_studio",
                "note": (
                    "Questo blocco può essere passato al motore domande studio già esistente. "
                    "La V4.5 non inventa domande non validate."
                ),
            }
        )

    payload = {
        "version": "V4.5",
        "module": "rag_pipeline_documenti_grandi_v45",
        "type": "study_questions_skeleton",
        "items": items,
    }

    (output_dir / "domande_studio.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_pipeline_report(
    output_dir: Path,
    manifest: Dict[str, Any],
    quality_report: Dict[str, Any],
) -> None:
    report = {
        "version": "V4.5",
        "module": "rag_pipeline_documenti_grandi_v45",
        "status": "ok",
        "manifest_status": manifest.get("status"),
        "quality_status": quality_report.get("status"),
        "pages_read": manifest.get("pages_read"),
        "chunks_created": manifest.get("chunks_created"),
        "outputs": {
            "manifest": str(output_dir / "manifest.json"),
            "testo_estratto": str(output_dir / "testo_estratto.md"),
            "chunks": str(output_dir / "chunks.jsonl"),
            "riassunto": str(output_dir / "riassunto.md"),
            "domande_studio": str(output_dir / "domande_studio.json"),
            "report_qualita": str(output_dir / "report_qualita.json"),
        },
        "rule": (
            "La pipeline V4.5 prepara il documento grande e collega i report qualità. "
            "La generazione finale deve continuare a passare dai motori già consolidati."
        ),
    }

    (output_dir / "pipeline_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md_lines = [
        "# Report pipeline RAG documenti grandi V4.5",
        "",
        f"- Stato: **{report['status']}**",
        f"- Pagine lette: **{report['pages_read']}**",
        f"- Chunk creati: **{report['chunks_created']}**",
        f"- Stato qualità: **{report['quality_status']}**",
        "",
        "## Regola",
        "",
        report["rule"],
        "",
    ]

    (output_dir / "pipeline_report.md").write_text("\n".join(md_lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Pipeline RAG V4.5 per documenti grandi."
    )
    parser.add_argument("--input", required=True, help="Documento TXT/MD/PDF.")
    parser.add_argument("--output", required=True, help="Cartella output.")
    parser.add_argument("--max-pages", type=int, default=0, help="0 = tutte.")
    parser.add_argument("--chunk-size", type=int, default=1800)
    parser.add_argument("--overlap", type=int, default=250)
    parser.add_argument("--quiz", default=None, help="Quiz JSON opzionale da validare.")
    parser.add_argument("--strict-quality", action="store_true", help="Blocca se qualità fallisce.")
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = process_input(
        input_file=args.input,
        output_dir=output_dir,
        max_pages=args.max_pages,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    create_document_map(output_dir)
    create_study_question_skeleton(output_dir)

    quality_report = validate_quiz(
        output_dir=output_dir,
        quiz_file=args.quiz,
        strict=args.strict_quality,
    )

    write_pipeline_report(
        output_dir=output_dir,
        manifest=manifest,
        quality_report=quality_report,
    )

    print("✅ Pipeline RAG Documenti Grandi V4.5 completata")
    print(f"📄 Pagine lette: {manifest['pages_read']}")
    print(f"🧩 Chunk creati: {manifest['chunks_created']}")
    print(f"📊 Qualità: {quality_report['status']}")
    print(f"📁 Output: {output_dir}")

    if args.strict_quality and quality_report["status"] in {
        "validation_failed",
        "no_validators_found",
        "validators_present_but_not_executed",
    }:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
