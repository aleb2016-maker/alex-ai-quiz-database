#!/usr/bin/env python3
"""
Validazione Mini LLM Output Modes V1.

Verifica:
- mode summary;
- mode cards;
- mode qa;
- mode test;
- mode full;
- public JSON senza answer key;
- test markdown senza risposte corrette;
- answer key separata;
- PDF testuale;
- velocità.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SAMPLE_TEXT = """
# Documento aziendale di sicurezza informatica

La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.
Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.
Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi.
I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati.
La formazione del personale riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano.
Le procedure di sicurezza aiutano a gestire incidenti, accessi, backup, dispositivi e comunicazioni interne.
"""


def pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def write_minimal_text_pdf(path: Path, text: str) -> None:
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    content_lines = [
        "BT",
        "/F1 10 Tf",
        "45 780 Td",
        "13 TL",
    ]

    first = True

    for line in lines:
        safe = pdf_escape(line)

        if first:
            content_lines.append(f"({safe}) Tj")
            first = False
        else:
            content_lines.append("T*")
            content_lines.append(f"({safe}) Tj")

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

    with tempfile.TemporaryDirectory(prefix="mini_llm_modes_v1_") as tmp:
        tmp_path = Path(tmp)

        md_file = tmp_path / "documento_modes.md"
        pdf_file = tmp_path / "documento_modes.pdf"
        test_md = tmp_path / "test_student.md"
        full_md = tmp_path / "full_student.md"
        answer_key = tmp_path / "answers.json"

        md_file.write_text(SAMPLE_TEXT.strip() + "\n", encoding="utf-8")
        write_minimal_text_pdf(pdf_file, SAMPLE_TEXT)

        mode_payloads = {}

        for mode in ["summary", "cards", "qa", "test", "full"]:
            mode_payloads[mode] = run_json(
                root,
                [
                    "scripts/mini_llm_output_modes_cli_v1.py",
                    str(md_file),
                    "--mode",
                    mode,
                    "--format",
                    "public-json",
                ],
            )

        pdf_full = run_json(
            root,
            [
                "scripts/mini_llm_output_modes_cli_v1.py",
                str(pdf_file),
                "--mode",
                "full",
                "--format",
                "public-json",
            ],
        )

        test_markdown_result = run_json(
            root,
            [
                "scripts/mini_llm_output_modes_cli_v1.py",
                str(md_file),
                "--mode",
                "test",
                "--format",
                "markdown",
                "--out",
                str(test_md),
                "--answer-key-out",
                str(answer_key),
            ],
        )

        full_markdown_result = run_json(
            root,
            [
                "scripts/mini_llm_output_modes_cli_v1.py",
                str(md_file),
                "--mode",
                "full",
                "--format",
                "markdown",
                "--out",
                str(full_md),
            ],
        )

        test_text = test_md.read_text(encoding="utf-8")
        full_text = full_md.read_text(encoding="utf-8")
        answer_key_json = json.loads(answer_key.read_text(encoding="utf-8"))

    errors = []

    for mode, payload in mode_payloads.items():
        if payload.get("status") != "OK":
            errors.append(f"{mode}_status_not_ok:{payload.get('status')}")

        if payload.get("mode") != mode:
            errors.append(f"{mode}_wrong_mode:{payload.get('mode')}")

        if payload.get("pack", {}).get("current", {}).get("engine") != "mini_llm_study_pack_v3_quality_gate":
            errors.append(f"{mode}_not_using_current_v3")

    summary_pack = mode_payloads["summary"].get("pack", {})

    if "summary" not in summary_pack:
        errors.append("summary_mode_missing_summary")

    if "cards" in summary_pack:
        errors.append("summary_mode_leaks_cards")

    cards_pack = mode_payloads["cards"].get("pack", {})

    if len(cards_pack.get("cards", [])) < 6:
        errors.append("cards_mode_less_than_6")

    if "summary" in cards_pack:
        errors.append("cards_mode_leaks_summary")

    qa_pack = mode_payloads["qa"].get("pack", {})

    if len(qa_pack.get("qas", [])) < 8:
        errors.append("qa_mode_less_than_8")

    if "cards" in qa_pack:
        errors.append("qa_mode_leaks_cards")

    test_pack = mode_payloads["test"].get("pack", {})

    if len(test_pack.get("student_test", [])) < 6:
        errors.append("test_mode_less_than_6")

    test_blob = json.dumps(test_pack, ensure_ascii=False)

    for forbidden in ["answer_key", "correct_index", "internal_test", "source_sentence"]:
        if forbidden in test_blob:
            errors.append(f"test_public_json_leaks:{forbidden}")

    full_pack = mode_payloads["full"].get("pack", {})

    for required in ["summary", "cards", "qas", "student_test"]:
        if required not in full_pack:
            errors.append(f"full_mode_missing:{required}")

    full_blob = json.dumps(full_pack, ensure_ascii=False)

    for forbidden in ["answer_key", "correct_index", "internal_test"]:
        if forbidden in full_blob:
            errors.append(f"full_public_json_leaks:{forbidden}")

    if pdf_full.get("status") != "OK":
        errors.append("pdf_full_not_ok")

    if test_markdown_result.get("status") != "OK":
        errors.append("test_markdown_result_not_ok")

    if full_markdown_result.get("status") != "OK":
        errors.append("full_markdown_result_not_ok")

    for forbidden in [
        "correct_index",
        "answer_key",
        "Risposta corretta",
        "Answer Key",
        "Spiegazione:",
        "source_sentence",
    ]:
        if forbidden in test_text:
            errors.append(f"test_markdown_leaks:{forbidden}")

    for required in ["## Test", "Questo test non mostra le risposte corrette"]:
        if required not in test_text:
            errors.append(f"test_markdown_missing:{required}")

    for required in ["## Riassunto", "## Card studio", "## Domande e risposte", "## Test"]:
        if required not in full_text:
            errors.append(f"full_markdown_missing:{required}")

    if not answer_key_json.get("answer_key"):
        errors.append("answer_key_json_empty")

    if float(mode_payloads["full"].get("total_ms", 9999.0)) > 120.0:
        errors.append("full_mode_too_slow")

    status = "PASS" if not errors else "FAIL"

    report = {
        "validator": "valida_mini_llm_output_modes_v1",
        "status": status,
        "errors": errors,
        "modes": {
            mode: {
                "status": payload.get("status"),
                "total_ms": payload.get("total_ms"),
                "counts": payload.get("pack", {}).get("counts", {}),
            }
            for mode, payload in mode_payloads.items()
        },
        "pdf_full": {
            "status": pdf_full.get("status"),
            "total_ms": pdf_full.get("total_ms"),
            "counts": pdf_full.get("pack", {}).get("counts", {}),
        },
        "markdown_outputs": {
            "test": test_markdown_result,
            "full": full_markdown_result,
        },
        "examples": {
            "summary": summary_pack.get("summary", {}),
            "first_card": cards_pack.get("cards", [{}])[0],
            "first_qa": qa_pack.get("qas", [{}])[0],
            "first_test": test_pack.get("student_test", [{}])[0],
            "first_answer_key": answer_key_json.get("answer_key", [{}])[0],
        },
        "limits": [
            "Output Modes V1 usa Study Pack Current V3.",
            "Non è ancora RAG lungo 500 pagine.",
            "Non è ancora LLM neurale generativo.",
            "No OCR.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_output_modes_v1_validation.json"
    md_path = report_dir / "validazione_mini_llm_output_modes_v1.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    first_card = report["examples"]["first_card"]
    first_qa = report["examples"]["first_qa"]
    first_test = report["examples"]["first_test"]

    lines = [
        "# Validazione Mini LLM Output Modes V1",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Modes validati",
        "",
    ]

    for mode in ["summary", "cards", "qa", "test", "full"]:
        info = report["modes"][mode]
        lines.append(f"- `{mode}`: `{info['status']}` in `{float(info['total_ms']):.6f}` ms")

    lines.extend(
        [
            "",
            "## PDF",
            "",
            f"- Full PDF status: `{report['pdf_full']['status']}`",
            f"- Full PDF tempo: `{float(report['pdf_full']['total_ms']):.6f}` ms",
            "",
            "## Esempi",
            "",
            f"### Card: {first_card.get('title')}",
            "",
            str(first_card.get("message", "")),
            "",
            "### Q&A",
            "",
            f"**D:** {first_qa.get('question')}",
            "",
            f"**R:** {first_qa.get('answer')}",
            "",
            "### Test studente",
            "",
            f"**Domanda:** {first_test.get('question')}",
            "",
        ]
    )

    for index, option in enumerate(first_test.get("options", []), start=1):
        lines.append(f"{index}. {option}")

    lines.extend(
        [
            "",
            "## Garanzie",
            "",
            "- Mode summary genera solo riassunto.",
            "- Mode cards genera solo card.",
            "- Mode qa genera solo domande e risposte.",
            "- Mode test genera test studente senza risposte corrette.",
            "- Mode full genera tutto il materiale pubblico.",
            "- Answer key separata se richiesta.",
            "",
            "## Limiti",
            "",
            "- Non ancora RAG 500 pagine.",
            "- Non ancora LLM neurale generativo.",
            "- No OCR.",
            "",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
