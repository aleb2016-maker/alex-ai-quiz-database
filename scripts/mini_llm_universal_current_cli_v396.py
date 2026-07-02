#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_pdf_with_pypdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except Exception as exc:
        raise RuntimeError(f"pypdf non disponibile per leggere PDF testuali: {exc}") from exc

    reader = PdfReader(str(path))
    parts = []

    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            parts.append(text.strip())

    return "\n\n".join(parts).strip()


def read_document(path: Path, root: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"Documento non trovato: {path}")

    suffix = path.suffix.lower()

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")

    if suffix == ".pdf":
        existing_reader = root / "scripts/mini_llm_practical_real_test_v391.py"

        if existing_reader.exists():
            module = load_module(existing_reader, "practical_reader_v391_for_current_v396")
            if hasattr(module, "read_document"):
                return module.read_document(path, root)

        return read_pdf_with_pypdf(path)

    raise ValueError(f"Formato non supportato dal CLI V3.9.6.1: {suffix}")


def detect_profile_id(text: str, root: Path) -> str:
    try:
        registry = load_module(
            root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py",
            "registry_for_safe_clean_v396",
        )
        return registry.detect_profile(text).get("profile_id", "")
    except Exception:
        return ""


def clean_document_safely(text: str, root: Path) -> dict:
    raw = str(text or "")
    raw_words = len(raw.split())

    if raw_words < 80:
        return {
            "text": raw,
            "used_cleaner": False,
            "reason": "Documento corto: uso testo grezzo per non perdere segnali di dominio.",
            "raw_words": raw_words,
            "cleaned_words": raw_words,
        }

    cleaner_path = root / "scripts/mini_llm_real_output_cleaner_v393.py"

    if not cleaner_path.exists():
        return {
            "text": raw,
            "used_cleaner": False,
            "reason": "Cleaner non disponibile.",
            "raw_words": raw_words,
            "cleaned_words": raw_words,
        }

    try:
        cleaner = load_module(cleaner_path, "cleaner_v393_for_current_v396")

        if not hasattr(cleaner, "clean_document_text"):
            raise RuntimeError("clean_document_text non presente")

        cleaned = cleaner.clean_document_text(raw)
    except Exception as exc:
        return {
            "text": raw,
            "used_cleaner": False,
            "reason": f"Cleaner fallito: {exc}",
            "raw_words": raw_words,
            "cleaned_words": raw_words,
        }

    cleaned_words = len(str(cleaned or "").split())

    if cleaned_words < max(40, int(raw_words * 0.55)):
        return {
            "text": raw,
            "used_cleaner": False,
            "reason": "Cleaner rifiutato: ha ridotto troppo il documento.",
            "raw_words": raw_words,
            "cleaned_words": cleaned_words,
        }

    raw_profile = detect_profile_id(raw, root)
    cleaned_profile = detect_profile_id(cleaned, root)

    if raw_profile and raw_profile != "generic_document_v394u" and cleaned_profile == "generic_document_v394u":
        return {
            "text": raw,
            "used_cleaner": False,
            "reason": "Cleaner rifiutato: peggiorava il profilo documento a generico.",
            "raw_words": raw_words,
            "cleaned_words": cleaned_words,
            "raw_profile": raw_profile,
            "cleaned_profile": cleaned_profile,
        }

    return {
        "text": cleaned,
        "used_cleaner": True,
        "reason": "Cleaner accettato.",
        "raw_words": raw_words,
        "cleaned_words": cleaned_words,
        "raw_profile": raw_profile,
        "cleaned_profile": cleaned_profile,
    }


def main() -> int:
    root = repo_root()

    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    from mini_llm.python.runtime.mini_llm_universal_current_engine_v396 import run_document

    parser = argparse.ArgumentParser(description="Mini LLM Universal Current Engine V3.9.6.1")
    parser.add_argument("file")
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--out", default="")
    parser.add_argument("--no-study-pack", action="store_true")
    args = parser.parse_args()

    path = Path(args.file).expanduser().resolve()

    try:
        raw_text = read_document(path, root)
        clean_info = clean_document_safely(raw_text, root)

        result = run_document(
            clean_info["text"],
            queries=args.query or None,
            include_study_pack=not args.no_study_pack,
            source=str(path),
        )

        result["document_cleaning"] = {
            key: value for key, value in clean_info.items() if key != "text"
        }

    except Exception as exc:
        result = {
            "engine": "mini_llm_universal_current_engine_v396_cli",
            "version": "V3.9.6.1",
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
