#!/usr/bin/env python3
"""
Validazione Mini LLM Practical Real Test V3.9.3.1 Clean.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    doc = root / "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md"
    out_dir = root / "mini_llm/data/real_tests/test_sicurezza_v393_clean"

    errors = []

    if not doc.exists():
        errors.append(f"documento_non_trovato:{doc}")

    if not errors:
        result = subprocess.run(
            [
                sys.executable,
                "scripts/mini_llm_practical_real_test_v393_clean.py",
                str(doc),
                "--query",
                "Quali sono i punti principali del documento?",
                "--query",
                "Che cosa devo ricordare sulla sicurezza informatica?",
                "--query",
                "Quali rischi vengono spiegati nel documento?",
                "--study-query",
                "sicurezza informatica phishing backup password credenziali ransomware formazione procedure dati aziendali malware autenticazione",
                "--out-dir",
                str(out_dir),
            ],
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            errors.append("script_v393_clean_non_pass")
            errors.append(result.stdout[-5000:])
            errors.append(result.stderr[-2000:])

    report = {}
    report_json = out_dir / "practical_real_test_v393_clean_report.json"

    if not errors:
        if not report_json.exists():
            errors.append(f"report_non_trovato:{report_json}")
        else:
            report = json.loads(report_json.read_text(encoding="utf-8"))

    if report:
        if report.get("status") != "PASS":
            errors.append(f"report_status_not_pass:{report.get('status')}:{report.get('errors')}")

        gate = report.get("real_quality_gate", {})

        if gate.get("status") != "PASS":
            errors.append(f"gate_not_pass:{gate.get('status')}:{gate.get('errors')}")

        cleaner = report.get("cleaner", {})

        if cleaner.get("status") != "OK":
            errors.append(f"cleaner_not_ok:{cleaner}")

        diagnostics = report.get("diagnostics", {})

        if diagnostics.get("engine") != "mini_llm_long_document_rag_v391_semantic_repair":
            errors.append("wrong_engine")

        if diagnostics.get("sentences", 0) < 20:
            errors.append(f"sentences_too_few:{diagnostics.get('sentences')}")

        study = report.get("study_pack", {})
        pack = study.get("study_pack", {}) if isinstance(study.get("study_pack", {}), dict) else {}
        counts = pack.get("counts", {})

        if counts.get("cards", 0) < 6:
            errors.append("cards_less_than_6")

        if counts.get("qas", 0) < 8:
            errors.append("qas_less_than_8")

        if counts.get("student_test_questions", 0) < 6:
            errors.append("student_test_less_than_6")

    status = "PASS" if not errors else "FAIL"

    validation = {
        "validator": "valida_mini_llm_practical_real_test_v393_clean",
        "version": "V3.9.3.1",
        "status": status,
        "errors": errors,
        "tested_document": str(doc),
        "real_report": str(report_json),
        "report_status": report.get("status"),
        "gate_status": report.get("real_quality_gate", {}).get("status") if report else None,
        "cleaner": report.get("cleaner") if report else {},
        "diagnostics": report.get("diagnostics") if report else {},
        "counts": (
            report.get("study_pack", {})
            .get("study_pack", {})
            .get("counts", {})
            if report else {}
        ),
        "limits": [
            "Valida documento reale nel repo.",
            "Richiede gate V3.9.2 PASS.",
            "Output reale resta ignorato da git.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_practical_real_test_v393_clean_validation.json"
    md_path = report_dir / "mini_llm_practical_real_test_v393_clean_validation.md"

    json_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Mini LLM Practical Real Test V3.9.3.1 Clean",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Documento testato",
        "",
        f"- `{doc}`",
        "",
        "## Risultati",
        "",
        f"- Report status: `{validation.get('report_status')}`",
        f"- Gate status: `{validation.get('gate_status')}`",
        f"- Cleaner: `{validation.get('cleaner')}`",
        f"- Counts: `{validation.get('counts')}`",
        "",
        "## Cosa valida",
        "",
        "- Cleaner reale V3.9.3.1.",
        "- RAG V3.9.1 su testo pulito.",
        "- Study Pack su contesto safe.",
        "- Real Quality Gate V3.9.2 obbligatorio.",
        "",
        "## Limiti",
        "",
        "- No OCR.",
        "- Non ancora LLM neurale generativo.",
        "- Output reale ignorato da git.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
