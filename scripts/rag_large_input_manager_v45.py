#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Large Input Manager V4.5

Scopo:
- leggere documenti TXT/MD/PDF;
- gestire ingressi più grandi con limite pagine;
- creare testo estratto, chunks JSONL e manifest;
- NON generare quiz;
- NON sostituire i motori qualità già esistenti.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any


SUPPORTED_TEXT_EXTENSIONS = {".txt", ".md", ".markdown"}
SUPPORTED_PDF_EXTENSIONS = {".pdf"}


@dataclass
class PageBlock:
    page: int
    text: str


@dataclass
class ChunkBlock:
    chunk_id: str
    chunk_index: int
    page_start: int
    page_end: int
    char_count: int
    text: str


def normalize_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{4,}", "\n\n\n", text)
    return text.strip()


def split_text_into_synthetic_pages(text: str, page_chars: int = 4500) -> List[PageBlock]:
    text = normalize_text(text)
    if not text:
        return []

    pages: List[PageBlock] = []
    start = 0
    page_no = 1

    while start < len(text):
        end = min(start + page_chars, len(text))

        if end < len(text):
            paragraph_break = text.rfind("\n\n", start, end)
            sentence_break = text.rfind(". ", start, end)

            if paragraph_break > start + int(page_chars * 0.45):
                end = paragraph_break
            elif sentence_break > start + int(page_chars * 0.45):
                end = sentence_break + 1

        page_text = normalize_text(text[start:end])
        if page_text:
            pages.append(PageBlock(page=page_no, text=page_text))
            page_no += 1

        start = max(end, start + 1)

    return pages


def read_text_document(input_path: Path, max_pages: int) -> List[PageBlock]:
    raw = input_path.read_text(encoding="utf-8", errors="replace")
    pages = split_text_into_synthetic_pages(raw)

    if max_pages > 0:
        pages = pages[:max_pages]

    return pages


def get_pdf_reader(input_path: Path):
    try:
        from pypdf import PdfReader  # type: ignore
        return PdfReader(str(input_path))
    except ImportError:
        pass

    try:
        from PyPDF2 import PdfReader  # type: ignore
        return PdfReader(str(input_path))
    except ImportError as exc:
        raise RuntimeError(
            "Per leggere PDF serve una libreria PDF. Installa una delle due:\n"
            "python3 -m pip install pypdf\n"
            "oppure\n"
            "python3 -m pip install PyPDF2"
        ) from exc


def read_pdf_document(input_path: Path, max_pages: int) -> List[PageBlock]:
    reader = get_pdf_reader(input_path)
    total_pages = len(reader.pages)

    limit = total_pages
    if max_pages > 0:
        limit = min(total_pages, max_pages)

    pages: List[PageBlock] = []

    for index in range(limit):
        page_no = index + 1
        try:
            text = reader.pages[index].extract_text() or ""
        except Exception as exc:
            text = f"[ERRORE ESTRAZIONE PAGINA {page_no}: {exc}]"

        text = normalize_text(text)

        if text:
            pages.append(PageBlock(page=page_no, text=text))

    return pages


def read_input_document(input_file: str | Path, max_pages: int = 0) -> List[PageBlock]:
    input_path = Path(input_file)

    if not input_path.exists():
        raise FileNotFoundError(f"File non trovato: {input_path}")

    ext = input_path.suffix.lower()

    if ext in SUPPORTED_TEXT_EXTENSIONS:
        pages = read_text_document(input_path, max_pages=max_pages)
    elif ext in SUPPORTED_PDF_EXTENSIONS:
        pages = read_pdf_document(input_path, max_pages=max_pages)
    else:
        raise ValueError(
            f"Formato non supportato: {ext}. Formati supportati: TXT, MD, PDF."
        )

    pages = [p for p in pages if normalize_text(p.text)]

    if not pages:
        raise ValueError(
            "Nessun testo estraibile trovato. "
            "Se è un PDF scannerizzato, serve il flusso OCR separato."
        )

    return pages


def paragraph_units(text: str) -> List[str]:
    text = normalize_text(text)
    if not text:
        return []

    units = re.split(r"\n\s*\n", text)
    clean_units = [normalize_text(unit) for unit in units if normalize_text(unit)]

    if len(clean_units) <= 1:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        clean_units = [normalize_text(sentence) for sentence in sentences if normalize_text(sentence)]

    return clean_units or [text]


def chunk_pages(
    pages: List[PageBlock],
    chunk_size: int = 1800,
    overlap: int = 250,
) -> List[ChunkBlock]:
    if chunk_size < 500:
        raise ValueError("chunk_size troppo piccolo. Usa almeno 500 caratteri.")

    if overlap < 0:
        raise ValueError("overlap non può essere negativo.")

    if overlap >= chunk_size:
        raise ValueError("overlap deve essere minore di chunk_size.")

    chunks: List[ChunkBlock] = []
    current_parts: List[str] = []
    current_pages: List[int] = []
    current_len = 0

    def flush(keep_overlap: bool) -> None:
        nonlocal current_parts, current_pages, current_len

        text = normalize_text("\n\n".join(current_parts))
        if not text:
            current_parts = []
            current_pages = []
            current_len = 0
            return

        chunk_index = len(chunks) + 1
        page_start = min(current_pages) if current_pages else 1
        page_end = max(current_pages) if current_pages else page_start

        chunks.append(
            ChunkBlock(
                chunk_id=f"chunk_{chunk_index:05d}",
                chunk_index=chunk_index,
                page_start=page_start,
                page_end=page_end,
                char_count=len(text),
                text=text,
            )
        )

        if keep_overlap and overlap > 0 and len(text) > overlap:
            tail = normalize_text(text[-overlap:])
            last_page = page_end
            current_parts = [tail] if tail else []
            current_pages = [last_page] if tail else []
            current_len = len(tail)
        else:
            current_parts = []
            current_pages = []
            current_len = 0

    for page in pages:
        units = paragraph_units(page.text)

        for unit in units:
            if len(unit) > chunk_size:
                flush(keep_overlap=True)

                step = max(1, chunk_size - overlap)
                start = 0

                while start < len(unit):
                    part = normalize_text(unit[start:start + chunk_size])
                    if part:
                        chunk_index = len(chunks) + 1
                        chunks.append(
                            ChunkBlock(
                                chunk_id=f"chunk_{chunk_index:05d}",
                                chunk_index=chunk_index,
                                page_start=page.page,
                                page_end=page.page,
                                char_count=len(part),
                                text=part,
                            )
                        )
                    start += step

                continue

            projected_len = current_len + len(unit) + 2

            if current_parts and projected_len > chunk_size:
                flush(keep_overlap=True)

            current_parts.append(unit)
            current_pages.append(page.page)
            current_len += len(unit) + 2

    flush(keep_overlap=False)

    return chunks


def write_text_extracted(pages: List[PageBlock], output_path: Path) -> None:
    lines: List[str] = []

    for page in pages:
        lines.append(f"\n\n<!-- PAGINA {page.page} -->\n\n")
        lines.append(page.text)

    output_path.write_text(normalize_text("\n".join(lines)) + "\n", encoding="utf-8")


def write_chunks_jsonl(chunks: List[ChunkBlock], output_path: Path) -> None:
    with output_path.open("w", encoding="utf-8") as handle:
        for chunk in chunks:
            handle.write(json.dumps(asdict(chunk), ensure_ascii=False) + "\n")


def write_manifest(
    input_path: Path,
    pages: List[PageBlock],
    chunks: List[ChunkBlock],
    output_dir: Path,
    chunk_size: int,
    overlap: int,
    max_pages: int,
) -> Dict[str, Any]:
    text_chars = sum(len(p.text) for p in pages)

    manifest: Dict[str, Any] = {
        "version": "V4.5",
        "module": "rag_large_input_manager_v45",
        "input_file": str(input_path),
        "input_name": input_path.name,
        "input_extension": input_path.suffix.lower(),
        "max_pages_requested": max_pages,
        "pages_read": len(pages),
        "chunks_created": len(chunks),
        "chunk_size": chunk_size,
        "overlap": overlap,
        "total_text_chars": text_chars,
        "average_chunk_chars": round(
            sum(c.char_count for c in chunks) / len(chunks), 2
        ) if chunks else 0,
        "status": "ok",
        "outputs": {
            "testo_estratto": str(output_dir / "testo_estratto.md"),
            "chunks_jsonl": str(output_dir / "chunks.jsonl"),
            "manifest": str(output_dir / "manifest.json"),
        },
        "note": (
            "Questo modulo legge e spezza il documento. "
            "La qualità delle domande/test resta affidata ai motori già esistenti."
        ),
    }

    manifest_path = output_dir / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return manifest


def process_input(
    input_file: str | Path,
    output_dir: str | Path,
    max_pages: int = 0,
    chunk_size: int = 1800,
    overlap: int = 250,
) -> Dict[str, Any]:
    input_path = Path(input_file)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    pages = read_input_document(input_path, max_pages=max_pages)
    chunks = chunk_pages(pages, chunk_size=chunk_size, overlap=overlap)

    if not chunks:
        raise ValueError("Nessun chunk creato. Il documento contiene troppo poco testo utile.")

    write_text_extracted(pages, out_dir / "testo_estratto.md")
    write_chunks_jsonl(chunks, out_dir / "chunks.jsonl")

    manifest = write_manifest(
        input_path=input_path,
        pages=pages,
        chunks=chunks,
        output_dir=out_dir,
        chunk_size=chunk_size,
        overlap=overlap,
        max_pages=max_pages,
    )

    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RAG Large Input Manager V4.5 - TXT/MD/PDF grandi in chunks."
    )
    parser.add_argument("--input", required=True, help="File TXT/MD/PDF in ingresso.")
    parser.add_argument("--output", required=True, help="Cartella di output.")
    parser.add_argument("--max-pages", type=int, default=0, help="Numero massimo pagine. 0 = tutte.")
    parser.add_argument("--chunk-size", type=int, default=1800, help="Dimensione chunk in caratteri.")
    parser.add_argument("--overlap", type=int, default=250, help="Overlap tra chunk in caratteri.")
    args = parser.parse_args()

    manifest = process_input(
        input_file=args.input,
        output_dir=args.output,
        max_pages=args.max_pages,
        chunk_size=args.chunk_size,
        overlap=args.overlap,
    )

    print("✅ RAG Large Input Manager V4.5 completato")
    print(f"📄 Pagine lette: {manifest['pages_read']}")
    print(f"🧩 Chunk creati: {manifest['chunks_created']}")
    print(f"📁 Output: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
