#!/usr/bin/env python3
"""
Validazione Mini LLM Study Pack CLI V2.

Verifica:
- input MD;
- input PDF testuale;
- output Markdown studente;
- answer key separata;
- niente risposte corrette nel Markdown studente;
- JSON pubblico senza answer key;
- JSON completo opzionale;
- uso Study Pack V3 Quality Gate.
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


def run_capture(root: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, *args],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def run_json(root: Path, args: list[str]) -> dict:
    result = run_capture(root, args)

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

    with tempfile.TemporaryDirectory(prefix="mini_llm_study_cli_v2_") as tmp:
        tmp_path = Path(tmp)

        md_file = tmp_path / "documento_studio.md"
        pdf_file = tmp_path / "documento_studio.pdf"

        student_md = tmp_path / "study_pack_student.md"
        answer_key_json = tmp_path / "study_pack_answers.json"
        answer_key_md = tmp_path / "study_pack_answers.md"

        md_file.write_text(SAMPLE_TEXT.strip() + "\n", encoding="utf-8")
        write_minimal_text_pdf(pdf_file, SAMPLE_TEXT)

        public_json = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v2.py",
                str(md_file),
                "--format",
                "public-json",
            ],
        )

        full_json = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v2.py",
                str(md_file),
                "--format",
                "json",
            ],
        )

        pdf_public_json = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v2.py",
                str(pdf_file),
                "--format",
                "public-json",
            ],
        )

        markdown_result = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v2.py",
                str(md_file),
                "--format",
                "markdown",
                "--out",
                str(student_md),
                "--answer-key-out",
                str(answer_key_json),
            ],
        )

        key_md_result = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v2.py",
                str(md_file),
                "--format",
                "markdown",
                "--out",
                str(tmp_path / "study_pack_student_2.md"),
                "--answer-key-out",
                str(answer_key_md),
            ],
        )

        student_text = student_md.read_text(encoding="utf-8")
        key_json = json.loads(answer_key_json.read_text(encoding="utf-8"))
        key_md_text = answer_key_md.read_text(encoding="utf-8")

    errors = []

    if public_json.get("status") != "OK":
        errors.append("public_json_not_ok")

    if full_json.get("status") != "OK":
        errors.append("full_json_not_ok")

    if pdf_public_json.get("status") != "OK":
        errors.append("pdf_public_json_not_ok")

    public_pack = public_json.get("pack", {})

    if public_pack.get("engine") != "mini_llm_study_pack_v3_quality_gate":
        errors.append("public_json_not_using_v3")

    if "answer_key" in json.dumps(public_json, ensure_ascii=False):
        errors.append("public_json_leaks_answer_key")

    if "correct_index" in json.dumps(public_json, ensure_ascii=False):
        errors.append("public_json_leaks_correct_index")

    if "answer_key" not in json.dumps(full_json, ensure_ascii=False):
        errors.append("full_json_missing_answer_key")

    if "Risposta corretta interna" in student_text:
        errors.append("student_markdown_leaks_old_correct_label")

    forbidden_student_strings = [
        "correct_index",
        "answer_key",
        "Risposta corretta:",
        "Answer Key",
        "Spiegazione:",
    ]

    for forbidden in forbidden_student_strings:
        if forbidden in student_text:
            errors.append(f"student_markdown_leaks:{forbidden}")

    for required in [
        "## Riassunto",
        "## Card studio",
        "## Domande e risposte",
        "## Test",
    ]:
        if required not in student_text:
            errors.append(f"student_markdown_missing:{required}")

    if markdown_result.get("status") != "OK":
        errors.append("markdown_result_not_ok")

    if not markdown_result.get("answer_key_file"):
        errors.append("answer_key_file_not_reported")

    if not key_json.get("answer_key"):
        errors.append("answer_key_json_empty")

    if "Risposta corretta" not in key_md_text:
        errors.append("answer_key_markdown_missing_correct_answer")

    counts = public_pack.get("counts", {})

    if counts.get("cards", 0) < 6:
        errors.append("cards_less_than_6")

    if counts.get("qas", 0) < 8:
        errors.append("qas_less_than_8")

    if counts.get("student_test_questions", 0) < 6:
        errors.append("student_test_less_than_6")

    if float(public_json.get("total_ms", 9999.0)) > 100.0:
        errors.append("public_json_too_slow")

    status = "PASS" if not errors else "FAIL"

    report = {
        "validator": "valida_mini_llm_study_pack_cli_v2",
        "status": status,
        "errors": errors,
        "public_json": {
            "status": public_json.get("status"),
            "engine": public_pack.get("engine"),
            "total_ms": public_json.get("total_ms"),
            "counts": counts,
        },
        "pdf_public_json": {
            "status": pdf_public_json.get("status"),
            "total_ms": pdf_public_json.get("total_ms"),
            "counts": pdf_public_json.get("pack", {}).get("counts", {}),
        },
        "markdown_result": markdown_result,
        "answer_key_markdown_result": key_md_result,
        "examples": {
            "first_student_test": public_pack.get("student_test", [{}])[0],
            "first_answer_key": key_json.get("answer_key", [{}])[0],
        },
        "quality_checks": {
            "student_markdown_hides_answers": "PASS" if not errors else "CHECK_ERRORS",
            "public_json_hides_answer_key": "answer_key" not in json.dumps(public_json, ensure_ascii=False),
            "uses_v3": public_pack.get("engine") == "mini_llm_study_pack_v3_quality_gate",
        },
        "limits": [
            "CLI V2 su TXT/MD/PDF testuali.",
            "No OCR.",
            "Structured/extractive.",
            "Usa Study Pack V3 Quality Gate.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_study_pack_cli_v2_validation.json"
    md_path = report_dir / "validazione_mini_llm_study_pack_cli_v2.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    first_test = report["examples"]["first_student_test"]
    first_key = report["examples"]["first_answer_key"]

    lines = [
        "# Validazione Mini LLM Study Pack CLI V2",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Risultati",
        "",
        f"- Engine: `{report['public_json']['engine']}`",
        f"- MD/Public JSON status: `{report['public_json']['status']}`",
        f"- MD tempo: `{float(report['public_json']['total_ms']):.6f}` ms",
        f"- PDF/Public JSON status: `{report['pdf_public_json']['status']}`",
        f"- PDF tempo: `{float(report['pdf_public_json']['total_ms']):.6f}` ms",
        f"- Conteggi: `{report['public_json']['counts']}`",
        f"- Markdown studente: `{markdown_result.get('status')}`",
        f"- Answer key file: `{markdown_result.get('answer_key_file')}`",
        "",
        "## Test studente esempio",
        "",
        f"**Domanda:** {first_test.get('question')}",
        "",
    ]

    for index, option in enumerate(first_test.get("options", []), start=1):
        lines.append(f"{index}. {option}")

    lines.extend(
        [
            "",
            "## Answer key esempio",
            "",
            f"- ID: `{first_key.get('id')}`",
            f"- Correct index: `{first_key.get('correct_index')}`",
            f"- Answer: {first_key.get('answer')}",
            "",
            "## Garanzie V2",
            "",
            "- Markdown studente senza risposte corrette.",
            "- Public JSON senza answer key.",
            "- Answer key separata su file dedicato.",
            "- Motore collegato a Study Pack V3 Quality Gate.",
            "",
            "## Limiti",
            "",
            "- Non è ancora LLM neurale generativo.",
            "- Non usa OCR.",
            "- Usa file TXT/MD/PDF testuali.",
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
