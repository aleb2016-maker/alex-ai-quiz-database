#!/usr/bin/env python3
"""
Validazione Mini LLM Universal LLM Bridge V3.9.5.

Controlla:
- regressione V3.9.4U;
- regressione V3.9.4;
- bridge universale su 5 domini;
- bridge su documento reale informatico;
- assenza vocabolari specialistici nel bridge.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def run(cmd: List[str], root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )


def write_temp_doc(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: List[str] = []

    bridge_file = root / "mini_llm/python/runtime/mini_llm_universal_llm_bridge_v395.py"
    cli_file = root / "scripts/mini_llm_universal_llm_bridge_cli_v395.py"

    for path in [bridge_file, cli_file]:
        if not path.exists():
            errors.append(f"missing_file:{path}")

    forbidden_bridge_terms = [
        "phishing",
        "ransomware",
        "malware",
        "allenamento",
        "curriculum",
        "documento scientifico",
        "documento aziendale",
    ]

    if bridge_file.exists():
        bridge_text = bridge_file.read_text(encoding="utf-8").lower()

        for term in forbidden_bridge_terms:
            if term in bridge_text:
                errors.append(f"specialist_term_inside_bridge:{term}")

    # Regressione V3.9.4U.
    v394u = run([sys.executable, "scripts/valida_mini_llm_universal_core_split_v394u.py"], root)

    if v394u.returncode != 0:
        errors.append("regression_v394u_failed")
        errors.append(v394u.stdout[-3000:])
        errors.append(v394u.stderr[-1000:])

    # Regressione V3.9.4 precedente.
    v394 = run([sys.executable, "scripts/valida_mini_llm_query_context_expander_v394.py"], root)

    if v394.returncode != 0:
        errors.append("regression_v394_failed")
        errors.append(v394.stdout[-3000:])
        errors.append(v394.stderr[-1000:])

    test_dir = root / "mini_llm/data/real_tests/test_v395_bridge_docs"

    cases = [
        {
            "name": "informatics",
            "expected_profile": "informatics_security_v394u",
            "text": "La sicurezza informatica protegge dati, account e sistemi digitali. Il phishing usa messaggi ingannevoli. Il ransomware può bloccare dati aziendali. Le password deboli aumentano il rischio di accessi non autorizzati.",
        },
        {
            "name": "sport",
            "expected_profile": "sport_training_v394u",
            "text": "Il programma di allenamento prevede esercizi di forza, serie e ripetizioni. Il recupero aiuta ad adattare il carico. Una tecnica scorretta aumenta il rischio di infortunio.",
        },
        {
            "name": "curriculum",
            "expected_profile": "curriculum_profile_v394u",
            "text": "Il curriculum presenta esperienze, formazione e competenze tecniche. Il profilo professionale deve chiarire il ruolo desiderato. Un obiettivo poco definito rende il CV meno efficace.",
        },
        {
            "name": "science",
            "expected_profile": "science_document_v394u",
            "text": "Il documento scientifico descrive ipotesi, metodo sperimentale e risultati. Un campione limitato può ridurre la solidità della conclusione. Le variabili non controllate possono alterare l'interpretazione.",
        },
        {
            "name": "business",
            "expected_profile": "business_document_v394u",
            "text": "Il documento aziendale definisce processo, responsabilità e scadenze. Una comunicazione insufficiente può generare errori operativi. Le procedure aiutano a controllare tempi e priorità.",
        },
    ]

    bridge_results: List[Dict[str, object]] = []

    for case in cases:
        doc_path = test_dir / f"{case['name']}.md"
        out_path = test_dir / f"{case['name']}_bridge_report.json"

        write_temp_doc(doc_path, case["text"])

        result = run(
            [
                sys.executable,
                "scripts/mini_llm_universal_llm_bridge_cli_v395.py",
                str(doc_path),
                "--query",
                "Quali sono i punti principali del documento?",
                "--query",
                "Che cosa devo ricordare?",
                "--query",
                "Quali rischi o problemi vengono spiegati nel documento?",
                "--out",
                str(out_path),
            ],
            root,
        )

        if result.returncode != 0:
            errors.append(f"bridge_case_failed:{case['name']}")
            errors.append(result.stdout[-3000:])
            errors.append(result.stderr[-1000:])
            continue

        report = json.loads(out_path.read_text(encoding="utf-8"))
        bridge_results.append(report)

        if report.get("status") != "PASS":
            errors.append(f"bridge_report_not_pass:{case['name']}:{report.get('errors')}")

        profile_id = report.get("profile", {}).get("profile_id")

        if profile_id != case["expected_profile"]:
            errors.append(f"profile_wrong:{case['name']}:{profile_id}:{case['expected_profile']}")

        for answer in report.get("answers", []):
            if not answer.get("expanded_query"):
                errors.append(f"missing_expanded_query:{case['name']}")

            if not answer.get("answer"):
                errors.append(f"missing_answer:{case['name']}")

            if answer.get("relevance", {}).get("profile_id") != case["expected_profile"]:
                errors.append(f"answer_profile_wrong:{case['name']}:{answer.get('relevance')}")

    # Documento reale informatico.
    real_doc = root / "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md"
    real_out = root / "mini_llm/data/real_tests/test_v395_bridge_real/bridge_real_report.json"

    if real_doc.exists():
        real_result = run(
            [
                sys.executable,
                "scripts/mini_llm_universal_llm_bridge_cli_v395.py",
                str(real_doc),
                "--query",
                "Quali sono i punti principali del documento?",
                "--query",
                "Che cosa devo ricordare?",
                "--query",
                "Quali rischi o problemi vengono spiegati nel documento?",
                "--out",
                str(real_out),
            ],
            root,
        )

        if real_result.returncode != 0:
            errors.append("real_doc_bridge_failed")
            errors.append(real_result.stdout[-3000:])
            errors.append(real_result.stderr[-1000:])
        else:
            real_report = json.loads(real_out.read_text(encoding="utf-8"))
            bridge_results.append(real_report)

            if real_report.get("status") != "PASS":
                errors.append(f"real_doc_report_not_pass:{real_report.get('errors')}")

            if real_report.get("profile", {}).get("profile_id") != "informatics_security_v394u":
                errors.append(f"real_doc_profile_wrong:{real_report.get('profile')}")
    else:
        errors.append(f"real_doc_missing:{real_doc}")

    status = "PASS" if not errors else "FAIL"

    validation = {
        "validator": "valida_mini_llm_universal_llm_bridge_v395",
        "status": status,
        "errors": errors,
        "regressions": {
            "v394u_universal_core_split": "PASS" if v394u.returncode == 0 else "FAIL",
            "v394_query_context_expander": "PASS" if v394.returncode == 0 else "FAIL",
        },
        "bridge_results_count": len(bridge_results),
        "bridge_results": bridge_results,
        "limits": [
            "Valida bridge LLM universale.",
            "Non sostituisce ancora PDF/OCR.",
            "Non deve contenere vocabolari specialistici nel bridge.",
            "Profili specialistici restano separati.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_universal_llm_bridge_v395_validation.json"
    md_path = report_dir / "mini_llm_universal_llm_bridge_v395_validation.md"

    json_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Mini LLM Universal LLM Bridge V3.9.5",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Regressioni",
        "",
        f"- V3.9.4U Universal Core Split: `{validation['regressions']['v394u_universal_core_split']}`",
        f"- V3.9.4 Query Context Expander: `{validation['regressions']['v394_query_context_expander']}`",
        "",
        "## Risultati bridge",
        "",
        f"- Report generati: `{len(bridge_results)}`",
        "",
    ]

    for report in bridge_results:
        diagnostics = report.get("diagnostics", {})
        lines.extend(
            [
                f"### {diagnostics.get('domain_name')}",
                "",
                f"- Status: `{report.get('status')}`",
                f"- Profilo: `{diagnostics.get('profile_id')}`",
                f"- Errori: `{report.get('errors')}`",
                "",
            ]
        )

        for answer in report.get("answers", []):
            lines.extend(
                [
                    f"- Domanda: `{answer.get('query')}`",
                    f"  Migliorata: `{answer.get('expanded_query')}`",
                ]
            )

        lines.append("")

    lines.extend(
        [
            "## Architettura",
            "",
            "- Il bridge usa il core universale V3.9.4U.",
            "- Il bridge non contiene vocabolari specialistici.",
            "- I profili specialistici restano separati.",
            "- Il bridge è pronto per essere collegato alla pipeline principale dopo ulteriore regressione.",
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
