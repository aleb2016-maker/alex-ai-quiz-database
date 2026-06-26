#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Test V4.5:
- verifica input grandi TXT/MD;
- verifica chunks;
- verifica manifest;
- verifica bridge qualità;
- non sporca il progetto;
- non richiede PDF obbligatorio se manca la libreria PDF.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TMP = ROOT / "tmp" / "rag_v45_test"
SCRIPTS = ROOT / "scripts"


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    print("▶", " ".join(command))
    completed = subprocess.run(
        command,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
    )

    if completed.stdout:
        print(completed.stdout)

    if completed.stderr:
        print(completed.stderr)

    if completed.returncode != 0:
        raise AssertionError(f"Comando fallito: {' '.join(command)}")

    return completed


def assert_exists(path: Path) -> None:
    if not path.exists():
        raise AssertionError(f"File mancante: {path}")


def assert_json(path: Path) -> dict:
    assert_exists(path)
    return json.loads(path.read_text(encoding="utf-8"))


def create_sample_documents() -> tuple[Path, Path]:
    TMP.mkdir(parents=True, exist_ok=True)

    repeated = []
    for i in range(1, 70):
        repeated.append(
            f"Sezione {i}. Questo è un testo di prova per il RAG V4.5. "
            f"Contiene concetti, spiegazioni, esempi e frasi sufficienti "
            f"per verificare chunking, overlap e manifest. "
            f"La sezione {i} serve a simulare un documento lungo."
        )

    txt_path = TMP / "documento_grande_test.txt"
    md_path = TMP / "documento_grande_test.md"

    txt_path.write_text("\n\n".join(repeated), encoding="utf-8")

    md_path.write_text(
        "# Documento markdown grande test\n\n" + "\n\n".join(repeated),
        encoding="utf-8",
    )

    return txt_path, md_path


def create_fake_quiz(output_dir: Path) -> Path:
    quiz = {
        "version": "test_v45",
        "domande": [
            {
                "id": "TEST-001",
                "domanda": "Qual è lo scopo del bridge qualità V4.5?",
                "opzioni": [
                    "Riutilizzare i validatori già esistenti",
                    "Eliminare i validatori precedenti",
                    "Ignorare la struttura JSON",
                    "Creare domande senza controllo"
                ],
                "risposta_corretta": "Riutilizzare i validatori già esistenti",
                "spiegazione": "Il bridge non reinventa la qualità, ma collega il RAG ai controlli esistenti."
            }
        ]
    }

    quiz_path = output_dir / "quiz_generato.json"
    quiz_path.write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")
    return quiz_path


def check_output_dir(output_dir: Path) -> None:
    assert_exists(output_dir / "manifest.json")
    assert_exists(output_dir / "testo_estratto.md")
    assert_exists(output_dir / "chunks.jsonl")
    assert_exists(output_dir / "riassunto.md")
    assert_exists(output_dir / "domande_studio.json")
    assert_exists(output_dir / "report_qualita.json")
    assert_exists(output_dir / "pipeline_report.json")

    manifest = assert_json(output_dir / "manifest.json")

    if manifest["pages_read"] <= 0:
        raise AssertionError("pages_read deve essere maggiore di zero")

    if manifest["chunks_created"] <= 0:
        raise AssertionError("chunks_created deve essere maggiore di zero")

    chunks = (output_dir / "chunks.jsonl").read_text(encoding="utf-8").strip().splitlines()

    if not chunks:
        raise AssertionError("chunks.jsonl è vuoto")

    for line in chunks:
        item = json.loads(line)
        if not item.get("text", "").strip():
            raise AssertionError("Trovato chunk vuoto")

    quality = assert_json(output_dir / "report_qualita.json")
    if "status" not in quality:
        raise AssertionError("report_qualita.json senza status")


def has_pdf_reader() -> bool:
    return (
        importlib.util.find_spec("pypdf") is not None
        or importlib.util.find_spec("PyPDF2") is not None
    )


def main() -> int:
    if TMP.exists():
        shutil.rmtree(TMP)

    txt_path, md_path = create_sample_documents()

    txt_output = TMP / "out_txt"
    md_output = TMP / "out_md"

    run([
        sys.executable,
        str(SCRIPTS / "rag_pipeline_documenti_grandi_v45.py"),
        "--input",
        str(txt_path),
        "--output",
        str(txt_output),
        "--max-pages",
        "20",
        "--chunk-size",
        "1400",
        "--overlap",
        "180",
    ])

    check_output_dir(txt_output)

    quiz_path = create_fake_quiz(txt_output)

    run([
        sys.executable,
        str(SCRIPTS / "rag_quality_bridge_v45.py"),
        "--output",
        str(txt_output),
        "--quiz",
        str(quiz_path),
    ])

    check_output_dir(txt_output)

    run([
        sys.executable,
        str(SCRIPTS / "rag_pipeline_documenti_grandi_v45.py"),
        "--input",
        str(md_path),
        "--output",
        str(md_output),
        "--max-pages",
        "20",
        "--chunk-size",
        "1400",
        "--overlap",
        "180",
    ])

    check_output_dir(md_output)

    if has_pdf_reader():
        print("✅ Supporto PDF disponibile: pypdf/PyPDF2 trovato")
    else:
        print("ℹ️ Supporto PDF non installato nel venv: installa pypdf se vuoi testare PDF reali")

    print("")
    print("✅ TEST V4.5 SUPERATO")
    print("✅ TXT/MD letti")
    print("✅ chunks creati")
    print("✅ manifest creato")
    print("✅ nessun chunk vuoto")
    print("✅ bridge qualità richiamabile")
    print("✅ report qualità generato")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
