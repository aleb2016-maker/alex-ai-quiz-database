#!/usr/bin/env python3
"""
Validazione supporto PDF testuale Mini LLM Document CLI V1.

Crea un PDF testuale minimale, poi verifica:
- estrazione PDF;
- build CLI su PDF;
- ask su PDF;
- summary su PDF;
- cache HIT;
- riassunto senza heading Markdown.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


PDF_LINES = [
    "Documento PDF testuale Mini LLM.",
    "La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.",
    "Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.",
    "I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.",
    "L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.",
    "Il ransomware e' un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.",
    "Gli aggiornamenti software correggono errori e chiudono vulnerabilita' di sicurezza.",
]


def pdf_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("(", "\\(")
        .replace(")", "\\)")
    )


def write_minimal_text_pdf(path: Path, lines: list[str]) -> None:
    content_lines = [
        "BT",
        "/F1 11 Tf",
        "50 780 Td",
        "14 TL",
    ]

    first = True

    for line in lines:
        if first:
            content_lines.append(f"({pdf_escape(line)}) Tj")
            first = False
        else:
            content_lines.append("T*")
            content_lines.append(f"({pdf_escape(line)}) Tj")

    content_lines.append("ET")

    stream = "\n".join(content_lines).encode("latin-1", errors="replace")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    output = bytearray()
    output.extend(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")

    offsets = [0]

    for index, obj in enumerate(objects, start=1):
        offsets.append(len(output))
        output.extend(f"{index} 0 obj\n".encode("ascii"))
        output.extend(obj)
        output.extend(b"\nendobj\n")

    xref_offset = len(output)

    output.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    output.extend(b"0000000000 65535 f \n")

    for offset in offsets[1:]:
        output.extend(f"{offset:010d} 00000 n \n".encode("ascii"))

    output.extend(
        (
            "trailer\n"
            f"<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("ascii")
    )

    path.write_bytes(bytes(output))


def run_json(root: Path, args: list[str]) -> dict:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Comando fallito:\n"
            + " ".join(args)
            + "\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )

    return json.loads(result.stdout)


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    sample_dir = root / "mini_llm/data/fast_runtime/pdf_v1_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)

    pdf_path = sample_dir / "documento_pdf_testuale_mini_llm.pdf"
    write_minimal_text_pdf(pdf_path, PDF_LINES)

    extractor = run_json(
        root,
        [
            "mini_llm/python/runtime/pdf_text_extractor_v1.py",
            str(pdf_path),
        ],
    )

    build = run_json(
        root,
        [
            "scripts/mini_llm_document_cli_v1.py",
            "build",
            str(pdf_path),
        ],
    )

    ask = run_json(
        root,
        [
            "scripts/mini_llm_document_cli_v1.py",
            "ask",
            str(pdf_path),
            "Che cosa fa il phishing?",
        ],
    )

    summary = run_json(
        root,
        [
            "scripts/mini_llm_document_cli_v1.py",
            "summary",
            str(pdf_path),
            "--max-sentences",
            "5",
        ],
    )

    errors = []

    if extractor.get("status") != "OK" or extractor.get("chars", 0) < 100:
        errors.append("extractor_not_ok")

    if build.get("status") != "OK":
        errors.append("build_not_ok")

    if ask.get("status") != "OK" or not ask.get("answer"):
        errors.append("ask_not_ok")

    if summary.get("status") != "OK" or not summary.get("summary"):
        errors.append("summary_not_ok")

    if ask.get("cache", {}).get("cache_status") != "HIT":
        errors.append("ask_cache_not_hit")

    if str(summary.get("summary", "")).lstrip().startswith("#"):
        errors.append("summary_has_markdown_heading")

    report = {
        "validator": "valida_mini_llm_document_cli_pdf_v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "pdf_file": str(pdf_path),
        "extractor": extractor,
        "build": build,
        "ask": ask,
        "summary": summary,
        "limits": [
            "PDF testuale generato in validazione.",
            "Non OCR.",
            "Non PDF scannerizzato.",
            "Q&A e summary extractive.",
        ],
    }

    json_path = root / "mini_llm/data/fast_runtime/mini_llm_document_cli_pdf_v1_validation.json"
    md_path = root / "mini_llm/reports/validazione_mini_llm_document_cli_pdf_v1.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Validazione Mini LLM Document CLI PDF V1",
        "",
        f"- Stato: **{report['status']}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        f"- PDF sample: `{pdf_path}`",
        "",
        "## Risultati",
        "",
        f"- Extractor: `{extractor.get('status')}`",
        f"- Pagine: `{extractor.get('pages')}`",
        f"- Caratteri estratti: `{extractor.get('chars')}`",
        f"- Build: `{build.get('status')}`",
        f"- Ask: `{ask.get('status')}`",
        f"- Cache ask: `{ask.get('cache', {}).get('cache_status')}`",
        f"- Summary: `{summary.get('status')}`",
        "",
        "## Risposta esempio",
        "",
        str(ask.get("answer", "")),
        "",
        "## Riassunto esempio",
        "",
        str(summary.get("summary", "")),
        "",
        "## Limiti",
        "",
        "- Supporta PDF testuali/selezionabili.",
        "- Non supporta ancora PDF scannerizzati senza OCR.",
        "- Q&A e summary sono extractive.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
