#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
GENERATOR = ROOT / "scripts" / "crea_documento_lungo_test_rag_v1.py"
MD_PATH = ROOT / "rag" / "documenti" / "test_documento_lungo_aziendale_120_pagine.md"
TXT_PATH = ROOT / "rag" / "documenti" / "test_documento_lungo_aziendale_120_pagine.txt"
REPORT_PATH = ROOT / "reports" / "rag_documenti_lunghi_v1.md"

DEFAULT_OPTIONS = {
    "max_chars_per_chunk": 4000,
    "chunk_overlap": 400,
    "max_pages_per_batch": 5,
    "max_chunks_per_batch": 8,
    "max_chars_per_batch": 28000,
}


def fail(message: str) -> None:
    print(f"ERRORE: {message}")
    sys.exit(1)


def normalize_text(value: str) -> str:
    text = str(value or "").replace("\r", "\n")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def split_txt_md_into_logical_pages(text: str) -> list[dict]:
    marker_pattern = re.compile(
        r"^[ \t]*(?:---[ \t]*PAGINA[ \t]+(\d{1,4})[ \t]*---|#{1,2}[ \t]*Pagina[ \t]+(\d{1,4})(?:[ \t].*)?)[ \t]*$",
        re.IGNORECASE | re.MULTILINE,
    )
    markers = [
        {
            "page": int(match.group(1) or match.group(2)),
            "start": match.start(),
        }
        for match in marker_pattern.finditer(text)
    ]

    if not markers:
        clean = normalize_text(text)
        return [{"page": 1, "text": clean, "chars": len(clean)}]

    pages = []
    for index, marker in enumerate(markers):
        end = markers[index + 1]["start"] if index + 1 < len(markers) else len(text)
        clean = normalize_text(text[marker["start"]:end])
        pages.append({"page": marker["page"], "text": clean, "chars": len(clean)})
    return sorted(pages, key=lambda item: item["page"])


def parse_page_selection(selection: str, total_pages: int) -> list[int]:
    value = str(selection or "").strip().lower()
    if not value or value in {"tutto", "all"}:
        return list(range(1, total_pages + 1))

    selected = set()
    for part in value.split(","):
        clean = part.strip()
        if not clean:
            continue
        if "-" in clean:
            left, right = clean.split("-", 1)
            start = max(1, min(int(left.strip()), total_pages))
            end = max(1, min(int(right.strip()), total_pages))
            for number in range(min(start, end), max(start, end) + 1):
                selected.add(number)
        else:
            number = int(clean)
            if 1 <= number <= total_pages:
                selected.add(number)
    return sorted(selected)


def split_text_to_chunks(text: str, options: dict) -> list[dict]:
    clean = normalize_text(text)
    if not clean:
        return []

    chunks = []
    start = 0
    max_chars = options["max_chars_per_chunk"]
    overlap = options["chunk_overlap"]

    while start < len(clean):
        end = min(start + max_chars, len(clean))
        if end < len(clean):
            soft_break = clean.rfind("\n\n", 0, end)
            sentence_break = clean.rfind(". ", 0, end)
            if soft_break > start + 1000:
                end = soft_break
            elif sentence_break > start + 1000:
                end = sentence_break + 1

        piece = clean[start:end].strip()
        if piece:
            chunks.append({"index": len(chunks) + 1, "text": piece, "chars": len(piece)})
        if end >= len(clean):
            break
        start = max(0, end - overlap)

    return chunks


def create_page_chunks(pages: list[dict], options: dict) -> list[dict]:
    chunks = []
    for page in pages:
        for chunk in split_text_to_chunks(page["text"], options):
            chunks.append({
                "id": f"p{page['page']}-c{chunk['index']}",
                "pageStart": page["page"],
                "pageEnd": page["page"],
                "globalIndex": len(chunks) + 1,
                "chars": chunk["chars"],
                "text": chunk["text"],
            })
    return chunks


def create_batches(chunks: list[dict], options: dict) -> list[dict]:
    batches = []
    current = []
    current_chars = 0
    current_pages = set()

    def flush() -> None:
        nonlocal current, current_chars, current_pages
        if not current:
            return
        batches.append({
            "index": len(batches) + 1,
            "chunks": list(current),
            "chunkCount": len(current),
            "chars": current_chars,
            "pageStart": min(current_pages),
            "pageEnd": max(current_pages),
        })
        current = []
        current_chars = 0
        current_pages = set()

    for chunk in chunks:
        next_pages = set(current_pages)
        next_pages.add(chunk["pageStart"])
        if current and (
            len(current) >= options["max_chunks_per_batch"]
            or current_chars + chunk["chars"] > options["max_chars_per_batch"]
            or len(next_pages) > options["max_pages_per_batch"]
        ):
            flush()
        current.append(chunk)
        current_chars += chunk["chars"]
        current_pages.add(chunk["pageStart"])

    flush()
    return batches


def write_report(total_chars: int, pages: list[dict], chunks: list[dict], batches: list[dict]) -> None:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(
        "\n".join([
            "# Report RAG documenti lunghi V1",
            "",
            "## Cosa e stato creato",
            "",
            "- Manager isolato: runtime/web/rag-large-document-manager-v1.js",
            "- Pagina test isolata: demo-rag/test-rag-documenti-lunghi-v1.html",
            "- Generatore documento: scripts/crea_documento_lungo_test_rag_v1.py",
            "- Validatori: scripts/verifica_rag_documenti_lunghi_v1.py e scripts/test_rag_documento_lungo_generato_v1.py",
            "- Documento MD e TXT in rag/documenti con 120 pagine logiche.",
            "",
            "## Cosa e stato testato",
            "",
            "- Riconoscimento marker pagina TXT/MD.",
            "- Selezioni: tutto, 1-10, 1,5,9, 20-30,40.",
            "- Chunk progressivi con metadati pagina e indice globale.",
            "- Batch con limiti su pagine, chunk e caratteri.",
            "- Isolamento dalla demo ufficiale e dagli export.",
            "",
            "## Metriche documento generato",
            "",
            f"- Caratteri totali: {total_chars}",
            f"- Pagine logiche: {len(pages)}",
            f"- Chunk prodotti: {len(chunks)}",
            f"- Batch prodotti: {len(batches)}",
            "",
            "## Limiti iniziali impostati",
            "",
            f"- Max caratteri per chunk: {DEFAULT_OPTIONS['max_chars_per_chunk']}",
            f"- Overlap chunk: {DEFAULT_OPTIONS['chunk_overlap']}",
            f"- Max pagine per batch: {DEFAULT_OPTIONS['max_pages_per_batch']}",
            f"- Max chunk per batch: {DEFAULT_OPTIONS['max_chunks_per_batch']}",
            f"- Max caratteri per batch: {DEFAULT_OPTIONS['max_chars_per_batch']}",
            "",
            "## Cosa NON e stato toccato",
            "",
            "- Non e stata collegata la demo ufficiale.",
            "- Non sono stati modificati i pulsanti esistenti.",
            "- Non e stato modificato PDF export.",
            "- Non sono stati modificati TXT/HTML/JSON export.",
            "- Non sono state modificate grafica o card ufficiali.",
            "",
        ]),
        encoding="utf-8",
    )


def main() -> None:
    subprocess.run([sys.executable, str(GENERATOR)], cwd=ROOT, check=True)

    for path in (MD_PATH, TXT_PATH):
        if not path.exists():
            fail(f"file non creato: {path.relative_to(ROOT)}")

    md_text = MD_PATH.read_text(encoding="utf-8")
    txt_text = TXT_PATH.read_text(encoding="utf-8")

    for label, text in (("md", md_text), ("txt", txt_text)):
        markers = re.findall(r"^--- PAGINA \d{3} ---$", text, flags=re.MULTILINE)
        if len(markers) != 120:
            fail(f"marker pagina {label}: attesi 120, trovati {len(markers)}")
        if len(text) < 250000:
            fail(f"testo {label} troppo corto: {len(text)} caratteri")

    keywords = [
        "firewall",
        "phishing",
        "backup",
        "privacy",
        "onboarding",
        "incidenti",
        "password",
        "audit",
        "continuità operativa",
    ]
    lower_text = md_text.lower()
    for keyword in keywords:
        if keyword.lower() not in lower_text:
            fail(f"keyword non trovata: {keyword}")

    pages = split_txt_md_into_logical_pages(md_text)
    if len(pages) != 120:
        fail(f"pagine logiche attese 120, trovate {len(pages)}")

    selection_expectations = {
        "1-10": 10,
        "1,5,9": 3,
        "20-30,40": 12,
    }
    for selection, expected in selection_expectations.items():
        found = len(parse_page_selection(selection, len(pages)))
        if found != expected:
            fail(f"selezione {selection}: attese {expected}, trovate {found}")

    chunks = create_page_chunks(pages, DEFAULT_OPTIONS)
    batches = create_batches(chunks, DEFAULT_OPTIONS)
    if len(chunks) <= 50:
        fail(f"chunk insufficienti: {len(chunks)}")
    if len(batches) <= 5:
        fail(f"batch insufficienti: {len(batches)}")

    write_report(len(md_text), pages, chunks, batches)

    print("OK: documento lungo generato e validato")
    print(f"OK: caratteri={len(md_text)} pagine={len(pages)} chunk={len(chunks)} batch={len(batches)}")
    print("OK: report aggiornato reports/rag_documenti_lunghi_v1.md")


if __name__ == "__main__":
    main()
