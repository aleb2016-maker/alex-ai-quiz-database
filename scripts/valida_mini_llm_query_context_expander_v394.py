#!/usr/bin/env python3
"""
Validazione Mini LLM Query Context Expander V3.9.4 FIX.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    doc = root / "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md"
    out_dir = root / "mini_llm/data/real_tests/test_sicurezza_v394_context"

    errors = []

    result = subprocess.run(
        [
            sys.executable,
            "scripts/mini_llm_practical_real_test_v394_context.py",
            str(doc),
            "--query",
            "Quali sono i punti principali del documento?",
            "--query",
            "Che cosa devo ricordare sulla sicurezza informatica?",
            "--query",
            "Quali rischi vengono spiegati nel documento?",
            "--out-dir",
            str(out_dir),
        ],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        errors.append("script_v394_context_non_pass")
        errors.append(result.stdout[-5000:])
        errors.append(result.stderr[-2000:])

    report_json = out_dir / "practical_real_test_v394_context_report.json"
    report = {}

    if not report_json.exists():
        errors.append(f"report_non_trovato:{report_json}")
    else:
        report = json.loads(report_json.read_text(encoding="utf-8"))

    if report:
        if report.get("status") != "PASS":
            errors.append(f"report_status_not_pass:{report.get('status')}:{report.get('errors')}")

        if report.get("real_quality_gate", {}).get("status") != "PASS":
            errors.append(f"real_quality_gate_not_pass:{report.get('real_quality_gate', {}).get('errors')}")

        if report.get("query_context_relevance_gate", {}).get("status") != "PASS":
            errors.append(f"query_context_relevance_not_pass:{report.get('query_context_relevance_gate', {}).get('errors')}")

        expansion = report.get("query_expansion", {})
        context = expansion.get("document_context", {})

        if context.get("domain") != "sicurezza informatica aziendale":
            errors.append(f"domain_not_detected:{context}")

        expanded_queries = [
            row.get("expanded_query", "")
            for row in expansion.get("queries", [])
        ]

        all_expanded = " ".join(expanded_queries).lower()

        if "punti principali del documento su sicurezza informatica aziendale" not in all_expanded:
            errors.append(f"main_points_query_not_contextualized:{expanded_queries}")

        if "rischi di sicurezza informatica aziendale" not in all_expanded:
            errors.append(f"risk_query_not_contextualized:{expanded_queries}")

        if "phishing" not in all_expanded or "ransomware" not in all_expanded:
            errors.append(f"expanded_query_missing_specific_terms:{expanded_queries}")

        answers = report.get("answers", [])

        main_answer = ""
        risk_answer = ""

        for answer in answers:
            q = str(answer.get("query", "")).lower()

            if "punti principali" in q:
                main_answer = str(answer.get("answer", ""))

            if "rischi" in q:
                risk_answer = str(answer.get("answer", ""))

        if not main_answer.lower().startswith("i punti principali del documento"):
            errors.append(f"main_answer_not_anchored:{main_answer[:240]}")

        if not risk_answer.lower().startswith("i rischi di sicurezza informatica aziendale"):
            errors.append(f"risk_answer_not_anchored:{risk_answer[:240]}")

    status = "PASS" if not errors else "FAIL"

    validation = {
        "validator": "valida_mini_llm_query_context_expander_v394",
        "status": status,
        "errors": errors,
        "tested_document": str(doc),
        "real_report": str(report_json),
        "report_status": report.get("status"),
        "real_quality_gate": report.get("real_quality_gate", {}).get("status") if report else None,
        "query_context_relevance_gate": report.get("query_context_relevance_gate", {}).get("status") if report else None,
        "query_expansion": report.get("query_expansion") if report else {},
        "answers": report.get("answers", []) if report else [],
        "limits": [
            "Valida espansione delle domande.",
            "Valida dominio documento.",
            "Valida risposta ancorata.",
            "Non è LLM neurale generativo.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_query_context_expander_v394_validation.json"
    md_path = report_dir / "mini_llm_query_context_expander_v394_validation.md"

    json_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Mini LLM Query Context Expander V3.9.4",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Gate",
        "",
        f"- Real Quality Gate V3.9.2: `{validation.get('real_quality_gate')}`",
        f"- Query Context Relevance V3.9.4: `{validation.get('query_context_relevance_gate')}`",
        "",
        "## Espansione domande",
        "",
    ]

    for row in validation.get("query_expansion", {}).get("queries", []):
        lines.extend(
            [
                "### Originale",
                "",
                str(row.get("original_query", "")),
                "",
                "### Migliorata",
                "",
                str(row.get("expanded_query", "")),
                "",
            ]
        )

    lines.extend(
        [
            "## Risposte",
            "",
        ]
    )

    for answer in validation.get("answers", []):
        lines.extend(
            [
                f"### {answer.get('query')}",
                "",
                f"Domanda migliorata: {answer.get('expanded_query')}",
                "",
                str(answer.get("answer", "")),
                "",
            ]
        )

    lines.extend(
        [
            "## Limiti",
            "",
            "- Espansione deterministica.",
            "- Structured/extractive.",
            "- Non ancora LLM neurale generativo.",
            "- No OCR.",
            "",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
