#!/usr/bin/env python3
"""
CLI Mini LLM Universal LLM Bridge V3.9.5.

Legge TXT/MD e usa:
- core universale;
- profili specialistici separati;
- domande contestualizzate;
- risposte validate.

Nota:
questo CLI non sostituisce ancora la pipeline PDF/OCR.
Serve a validare il collegamento LLM/RAG al core universale.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Documento non trovato: {path}")

    if path.suffix.lower() not in {".txt", ".md"}:
        raise ValueError("Bridge V3.9.5: per ora CLI diretto solo TXT/MD. PDF/OCR restano nella pipeline già esistente.")

    return path.read_text(encoding="utf-8")


def main() -> int:
    root = repo_root()

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from mini_llm.python.runtime.mini_llm_universal_llm_bridge_v395 import answer_document

    parser = argparse.ArgumentParser(description="Mini LLM Universal LLM Bridge V3.9.5")
    parser.add_argument("file")
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()

    try:
        text = read_text(path)
        result = answer_document(text, args.query or None)
    except Exception as exc:
        result = {
            "engine": "mini_llm_universal_llm_bridge_v395_cli",
            "status": "ERROR",
            "errors": [str(exc)],
            "file": str(path),
        }

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)

    if args.out:
        out = Path(args.out).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output + "\n", encoding="utf-8")

    return 0 if result.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
