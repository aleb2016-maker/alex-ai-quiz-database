#!/usr/bin/env python3
"""
Validazione Mini LLM Study Pack CLI V1.

Verifica:
- input MD;
- input PDF testuale;
- output JSON;
- output Markdown;
- riassunto/card/Q&A/test;
- qualità V2;
- risposta corretta mescolata;
- velocità accettabile.
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


BAD_QUESTIONS = [
    "Che cosa protegge sicurezza informatica?",
    "Che cosa usa phishing?",
    "Che cosa rafforza L'autenticazione",
    "Qual è il punto chiave su",
]


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


def validate_payload(name: str, payload: dict) -> list[str]:
    errors = []

    if payload.get("status") != "OK":
        errors.append(f"{name}_status_not_ok:{payload.get('status')}")

    pack = payload.get("pack", {})

    if pack.get("status") != "OK":
        errors.append(f"{name}_pack_status_not_ok:{pack.get('status')}")

    counts = pack.get("counts", {})

    if counts.get("cards", 0) < 6:
        errors.append(f"{name}_cards_less_than_6")

    if counts.get("qas", 0) < 8:
        errors.append(f"{name}_qas_less_than_8")

    if counts.get("test_questions", 0) < 6:
        errors.append(f"{name}_test_less_than_6")

    text_blob = json.dumps(pack, ensure_ascii=False)

    for bad in BAD_QUESTIONS:
        if bad in text_blob:
            errors.append(f"{name}_bad_question_present:{bad}")

    correct_indexes = [
        item.get("correct_index")
        for item in pack.get("test", [])
    ]

    if len(set(correct_indexes)) < 2:
        errors.append(f"{name}_correct_indexes_not_mixed")

    if float(payload.get("total_ms", 9999.0)) > 80.0:
        errors.append(f"{name}_too_slow")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory(prefix="mini_llm_study_cli_") as tmp:
        tmp_path = Path(tmp)

        md_file = tmp_path / "documento_studio.md"
        pdf_file = tmp_path / "documento_studio.pdf"
        markdown_out = tmp_path / "study_pack.md"

        md_file.write_text(SAMPLE_TEXT.strip() + "\n", encoding="utf-8")
        write_minimal_text_pdf(pdf_file, SAMPLE_TEXT)

        md_json = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v1.py",
                str(md_file),
                "--format",
                "json",
            ],
        )

        pdf_json = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v1.py",
                str(pdf_file),
                "--format",
                "json",
            ],
        )

        markdown_result = run_json(
            root,
            [
                "scripts/mini_llm_study_pack_cli_v1.py",
                str(md_file),
                "--format",
                "markdown",
                "--out",
                str(markdown_out),
            ],
        )

        markdown_text = markdown_out.read_text(encoding="utf-8")

    errors = []

    errors.extend(validate_payload("md", md_json))
    errors.extend(validate_payload("pdf", pdf_json))

    if markdown_result.get("status") != "OK":
        errors.append("markdown_output_status_not_ok")

    for required in [
        "## Riassunto",
        "## Card studio",
        "## Domande e risposte",
        "## Test",
    ]:
        if required not in markdown_text:
            errors.append(f"markdown_missing:{required}")

    status = "PASS" if not errors else "FAIL"

    report = {
        "validator": "valida_mini_llm_study_pack_cli_v1",
        "status": status,
        "errors": errors,
        "md": {
            "status": md_json.get("status"),
            "total_ms": md_json.get("total_ms"),
            "counts": md_json.get("pack", {}).get("counts", {}),
        },
        "pdf": {
            "status": pdf_json.get("status"),
            "total_ms": pdf_json.get("total_ms"),
            "counts": pdf_json.get("pack", {}).get("counts", {}),
        },
        "markdown_output": markdown_result,
        "examples": {
            "md_first_card": md_json.get("pack", {}).get("cards", [{}])[0],
            "md_first_qa": md_json.get("pack", {}).get("qas", [{}])[0],
            "md_first_test": md_json.get("pack", {}).get("test", [{}])[0],
        },
        "limits": [
            "CLI su TXT/MD/PDF testuali.",
            "No OCR.",
            "Structured/extractive.",
            "Usa Study Pack V2 Quality.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_study_pack_cli_v1_validation.json"
    md_path = report_dir / "validazione_mini_llm_study_pack_cli_v1.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    first_card = report["examples"]["md_first_card"]
    first_qa = report["examples"]["md_first_qa"]
    first_test = report["examples"]["md_first_test"]

    lines = [
        "# Validazione Mini LLM Study Pack CLI V1",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Risultati",
        "",
        f"- MD status: `{report['md']['status']}`",
        f"- MD tempo: `{float(report['md']['total_ms']):.6f}` ms",
        f"- MD conteggi: `{report['md']['counts']}`",
        f"- PDF status: `{report['pdf']['status']}`",
        f"- PDF tempo: `{float(report['pdf']['total_ms']):.6f}` ms",
        f"- PDF conteggi: `{report['pdf']['counts']}`",
        f"- Markdown output: `{markdown_result.get('status')}`",
        "",
        "## Card esempio",
        "",
        f"### {first_card.get('title')}",
        "",
        str(first_card.get("message", "")),
        "",
        "## Q&A esempio",
        "",
        f"**D:** {first_qa.get('question')}",
        "",
        f"**R:** {first_qa.get('answer')}",
        "",
        "## Test esempio",
        "",
        f"**Domanda:** {first_test.get('question')}",
        "",
    ]

    for index, option in enumerate(first_test.get("options", []), start=1):
        lines.append(f"{index}. {option}")

    lines.extend(
        [
            "",
            f"Corretto interno: `{first_test.get('correct_index')}`",
            "",
            "## Limiti",
            "",
            "- Non è ancora LLM neurale generativo.",
            "- Non usa OCR.",
            "- Usa Study Pack V2 Quality.",
            "- È pronto per essere collegato alla UI o al livello LLM controllato.",
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
