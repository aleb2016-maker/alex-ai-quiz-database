#!/usr/bin/env python3
"""
PDF Text Extractor V1 per Mini LLM.

Scopo:
- estrarre testo da PDF testuali;
- pulire testo pagina per pagina;
- restituire testo pronto per la CLI documentale.

Limiti:
- funziona su PDF con testo selezionabile;
- non fa OCR;
- non legge immagini/scansioni;
- per PDF scannerizzati servirà un modulo OCR separato.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Dict, List


def normalize_text(text: str) -> str:
    text = str(text).replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_pdf_text(path: Path) -> Dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(f"PDF non trovato: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError(f"File non PDF: {path}")

    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError(
            "Dipendenza mancante: installa pypdf con `python -m pip install pypdf`."
        ) from exc

    reader = PdfReader(str(path))

    pages: List[Dict[str, object]] = []
    full_parts: List[str] = []

    for index, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        clean = normalize_text(raw)

        pages.append(
            {
                "page": index,
                "chars": len(clean),
                "text": clean,
            }
        )

        if clean:
            full_parts.append(f"[Pagina {index}]\n{clean}")

    full_text = normalize_text("\n\n".join(full_parts))

    status = "OK" if full_text else "EMPTY_TEXT"

    return {
        "extractor": "pdf_text_extractor_v1",
        "status": status,
        "file": str(path),
        "pages": len(reader.pages),
        "chars": len(full_text),
        "page_texts": pages,
        "text": full_text,
        "limits": [
            "PDF testuale/selezionabile.",
            "Non OCR.",
            "Non estrae testo da immagini scannerizzate.",
        ],
    }


def main() -> int:
    if len(sys.argv) != 2:
        print(
            json.dumps(
                {
                    "status": "ERROR",
                    "error": "Uso: python mini_llm/python/runtime/pdf_text_extractor_v1.py file.pdf",
                },
                ensure_ascii=False,
                indent=2,
            ),
            file=sys.stderr,
        )
        return 1

    path = Path(sys.argv[1]).expanduser().resolve()

    try:
        result = extract_pdf_text(path)
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

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
