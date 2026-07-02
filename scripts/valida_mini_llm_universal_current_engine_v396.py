#!/usr/bin/env python3
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


def write_doc(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_json(path: Path) -> Dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    errors: List[str] = []

    runtime_file = root / "mini_llm/python/runtime/mini_llm_universal_current_engine_v396.py"
    cli_file = root / "scripts/mini_llm_universal_current_cli_v396.py"

    required_files = [
        runtime_file,
        cli_file,
        root / "mini_llm/python/runtime/mini_llm_universal_llm_bridge_v395.py",
        root / "mini_llm/python/runtime/universal/mini_llm_universal_linguistic_core_v394u.py",
        root / "mini_llm/python/runtime/universal/mini_llm_universal_question_core_v394u.py",
        root / "mini_llm/python/runtime/universal/mini_llm_universal_relevance_core_v394u.py",
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py",
    ]

    for path in required_files:
        if not path.exists():
            errors.append(f"missing_file:{path}")

    forbidden_runtime_terms = [
        "phishing",
        "ransomware",
        "malware",
        "allenamento",
        "curriculum",
        "documento scientifico",
        "documento aziendale",
        "sicurezza informatica",
    ]

    if runtime_file.exists():
        text = runtime_file.read_text(encoding="utf-8").lower()
        for term in forbidden_runtime_terms:
            if term in text:
                errors.append(f"specialist_term_inside_current_engine:{term}")

    test_dir = root / "mini_llm/data/real_tests/test_v396_current_engine"
    test_dir.mkdir(parents=True, exist_ok=True)

    cases = [
        {
            "name": "informatics",
            "suffix": ".md",
            "expected_profile": "informatics_security_v394u",
            "text": "La sicurezza informatica protegge dati, account e sistemi digitali. Il phishing usa messaggi ingannevoli. Il ransomware può bloccare dati aziendali. Le password deboli aumentano il rischio di accessi non autorizzati.",
        },
        {
            "name": "sport",
            "suffix": ".txt",
            "expected_profile": "sport_training_v394u",
            "text": "Il programma di allenamento prevede esercizi di forza, serie e ripetizioni. Il recupero aiuta ad adattare il carico. Una tecnica scorretta aumenta il rischio di infortunio.",
        },
        {
            "name": "curriculum",
            "suffix": ".md",
            "expected_profile": "curriculum_profile_v394u",
            "text": "Il curriculum presenta esperienze, formazione e competenze tecniche. Il profilo professionale deve chiarire il ruolo desiderato. Un obiettivo poco definito rende il CV meno efficace.",
        },
        {
            "name": "science",
            "suffix": ".txt",
            "expected_profile": "science_document_v394u",
            "text": "Il documento scientifico descrive ipotesi, metodo sperimentale e risultati. Un campione limitato può ridurre la solidità della conclusione. Le variabili non controllate possono alterare l'interpretazione.",
        },
        {
            "name": "business",
            "suffix": ".md",
            "expected_profile": "business_document_v394u",
            "text": "Il documento aziendale definisce processo, responsabilità e scadenze. Una comunicazione insufficiente può generare errori operativi. Le procedure aiutano a controllare tempi e priorità.",
        },
    ]

    results: List[Dict] = []

    for case in cases:
        doc = test_dir / f"{case['name']}{case['suffix']}"
        out = test_dir / f"{case['name']}_current_report.json"
        write_doc(doc, case["text"])

        result = run(
            [
                sys.executable,
                "scripts/mini_llm_universal_current_cli_v396.py",
                str(doc),
                "--query", "Quali sono i punti principali del documento?",
                "--query", "Che cosa devo ricordare?",
                "--query", "Quali rischi o problemi vengono spiegati nel documento?",
                "--no-study-pack",
                "--out", str(out),
            ],
            root,
        )

        if result.returncode != 0:
            errors.append(f"current_case_failed:{case['name']}")
            errors.append(result.stdout[-3000:])
            errors.append(result.stderr[-1000:])
            continue

        report = load_json(out)
        results.append(report)

        if report.get("status") != "PASS":
            errors.append(f"current_report_not_pass:{case['name']}:{report.get('errors')}")

        profile_id = report.get("profile", {}).get("profile_id")

        if profile_id != case["expected_profile"]:
            errors.append(f"profile_wrong:{case['name']}:{profile_id}:{case['expected_profile']}")

        if report.get("bridge_result", {}).get("status") != "PASS":
            errors.append(f"bridge_result_not_pass:{case['name']}:{report.get('bridge_result', {}).get('errors')}")

        if report.get("study_pack", {}).get("status") != "SKIPPED":
            errors.append(f"study_pack_should_be_skipped:{case['name']}:{report.get('study_pack')}")

        if len(case["text"].split()) < 80 and report.get("document_cleaning", {}).get("used_cleaner") is not False:
            errors.append(f"short_doc_cleaner_should_be_skipped:{case['name']}:{report.get('document_cleaning')}")

    real_doc = root / "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md"
    real_out = root / "mini_llm/data/real_tests/test_v396_current_real/current_real_report.json"

    if not real_doc.exists():
        errors.append(f"real_doc_missing:{real_doc}")
    else:
        real_result = run(
            [
                sys.executable,
                "scripts/mini_llm_universal_current_cli_v396.py",
                str(real_doc),
                "--query", "Quali sono i punti principali del documento?",
                "--query", "Che cosa devo ricordare?",
                "--query", "Quali rischi o problemi vengono spiegati nel documento?",
                "--out", str(real_out),
            ],
            root,
        )

        if real_result.returncode != 0:
            errors.append("current_real_doc_failed")
            errors.append(real_result.stdout[-4000:])
            errors.append(real_result.stderr[-1500:])
        else:
            real_report = load_json(real_out)
            results.append(real_report)

            if real_report.get("status") != "PASS":
                errors.append(f"current_real_report_not_pass:{real_report.get('errors')}")

            if real_report.get("profile", {}).get("profile_id") != "informatics_security_v394u":
                errors.append(f"current_real_profile_wrong:{real_report.get('profile')}")

            if real_report.get("bridge_result", {}).get("status") != "PASS":
                errors.append(f"current_real_bridge_not_pass:{real_report.get('bridge_result', {}).get('errors')}")

            study_status = real_report.get("study_pack", {}).get("status")

            if study_status not in {"OK", "QUALITY_BLOCKED"}:
                errors.append(f"current_real_study_pack_bad_status:{real_report.get('study_pack')}")

            if study_status == "QUALITY_BLOCKED" and not real_report.get("study_pack", {}).get("errors"):
                errors.append("quality_blocked_without_errors")

            if study_status == "OK":
                pack = real_report.get("study_pack", {}).get("study_pack", {})
                bad_dump = json.dumps(pack, ensure_ascii=False).lower()

                for bad in [
                    "che cosa usa quando",
                    "quale informazione importante viene data su",
                    " sui.",
                ]:
                    if bad in bad_dump:
                        errors.append(f"bad_legacy_output_not_blocked:{bad}")

    status = "PASS" if not errors else "FAIL"

    validation = {
        "validator": "valida_mini_llm_universal_current_engine_v396",
        "version": "V3.9.6.1",
        "status": status,
        "errors": errors,
        "results_count": len(results),
        "results": results,
        "checks": {
            "current_engine_without_specialist_terms": "PASS" if not any("specialist_term_inside_current_engine" in e for e in errors) else "FAIL",
            "multi_domain": "PASS" if len(results) >= 5 else "FAIL",
            "real_document": "PASS" if any(r.get("source", "").endswith("documento_rag_sicurezza_informatica_aziendale.md") and r.get("status") == "PASS" for r in results) else "FAIL",
            "study_pack_quality_guard": "PASS" if not any("bad_legacy_output_not_blocked" in e for e in errors) else "FAIL",
        },
        "limits": [
            "Valida current engine V3.9.6.1.",
            "Non sostituisce UI/PDF export/OCR.",
            "Safe cleaner obbligatorio.",
            "Study pack legacy non viene esposto se fallisce il gate qualità.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_universal_current_engine_v396_validation.json"
    md_path = report_dir / "mini_llm_universal_current_engine_v396_validation.md"

    json_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Mini LLM Universal Current Engine V3.9.6.1",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Controlli",
        "",
        f"- Current senza termini specialistici: `{validation['checks']['current_engine_without_specialist_terms']}`",
        f"- Multi-dominio: `{validation['checks']['multi_domain']}`",
        f"- Documento reale: `{validation['checks']['real_document']}`",
        f"- Study pack quality guard: `{validation['checks']['study_pack_quality_guard']}`",
        f"- Report generati: `{len(results)}`",
        "",
        "## Architettura",
        "",
        "- Current Engine V3.9.6.1 usa il bridge V3.9.5.",
        "- Il bridge usa il core universale V3.9.4U.",
        "- I profili specialistici restano separati.",
        "- Il cleaner è safe.",
        "- Lo study pack legacy viene bloccato se produce domande, titoli o opzioni brutte.",
        "- Non sono stati toccati UI, OCR o PDF export.",
        "",
    ]

    for report in results:
        diagnostics = report.get("diagnostics", {})
        bridge = diagnostics.get("bridge", {})
        lines.extend(
            [
                f"### {bridge.get('domain_name')}",
                "",
                f"- Status: `{report.get('status')}`",
                f"- Profilo: `{bridge.get('profile_id')}`",
                f"- Study pack: `{report.get('study_pack', {}).get('status')}`",
                f"- Cleaner: `{report.get('document_cleaning')}`",
                f"- Errori: `{report.get('errors')}`",
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
