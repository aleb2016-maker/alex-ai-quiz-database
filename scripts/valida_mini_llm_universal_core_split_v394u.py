#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))

    errors: List[str] = []

    core_files = [
        root / "mini_llm/python/runtime/universal/mini_llm_universal_linguistic_core_v394u.py",
        root / "mini_llm/python/runtime/universal/mini_llm_universal_question_core_v394u.py",
        root / "mini_llm/python/runtime/universal/mini_llm_universal_relevance_core_v394u.py",
    ]

    profile_files = [
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_informatics_v394u.py",
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_sport_v394u.py",
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_curriculum_v394u.py",
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_science_v394u.py",
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_business_v394u.py",
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_generic_v394u.py",
        root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py",
    ]

    for path in core_files + profile_files:
        if not path.exists():
            errors.append(f"missing_file:{path}")

    forbidden_core_terms = [
        "phishing",
        "ransomware",
        "malware",
        "2fa",
        "credenziali",
        "curriculum",
        "allenamento",
        "sicurezza informatica",
        "documento scientifico",
    ]

    for path in core_files:
        text = path.read_text(encoding="utf-8").lower()
        for term in forbidden_core_terms:
            if term in text:
                errors.append(f"specialist_term_inside_universal_core:{path.name}:{term}")
        if "quali rischi vengono spiegati nel documento" in text:
            errors.append(f"single_question_hardcoded_in_core:{path.name}")

    if errors:
        validation = {"validator": "valida_mini_llm_universal_core_split_v394u", "status": "FAIL", "errors": errors}
        print(json.dumps(validation, ensure_ascii=False, indent=2))
        return 1

    registry = load_module(root / "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py", "registry_v394u_validation")
    linguistic = load_module(root / "mini_llm/python/runtime/universal/mini_llm_universal_linguistic_core_v394u.py", "linguistic_v394u_validation")
    question_core = load_module(root / "mini_llm/python/runtime/universal/mini_llm_universal_question_core_v394u.py", "question_v394u_validation")
    relevance_core = load_module(root / "mini_llm/python/runtime/universal/mini_llm_universal_relevance_core_v394u.py", "relevance_v394u_validation")

    cases = [
        {
            "expected_profile": "informatics_security_v394u",
            "text": "La sicurezza informatica protegge dati, account e sistemi digitali. Il phishing usa messaggi ingannevoli per ottenere credenziali. Il ransomware può bloccare dati aziendali e richiedere un riscatto. Le password deboli aumentano il rischio di accessi non autorizzati.",
        },
        {
            "expected_profile": "sport_training_v394u",
            "text": "Il programma di allenamento prevede esercizi di forza, serie e ripetizioni. Il recupero tra le sedute aiuta ad adattare il carico. Una tecnica scorretta aumenta il rischio di infortunio. La progressione deve essere controllata nel tempo.",
        },
        {
            "expected_profile": "curriculum_profile_v394u",
            "text": "Il curriculum presenta esperienze, formazione e competenze tecniche. Il profilo professionale deve chiarire il ruolo desiderato. I progetti aiutano a dimostrare capacità concrete. Un obiettivo poco definito rende il CV meno efficace.",
        },
        {
            "expected_profile": "science_document_v394u",
            "text": "Il documento scientifico descrive ipotesi, metodo sperimentale e risultati. I dati raccolti devono essere confrontati con le osservazioni. Un campione limitato può ridurre la solidità della conclusione. Le variabili non controllate possono alterare l'interpretazione.",
        },
        {
            "expected_profile": "business_document_v394u",
            "text": "Il documento aziendale definisce processo, responsabilità e scadenze. Il reparto deve monitorare attività, budget e risultati. Una comunicazione insufficiente può generare errori operativi. Le procedure aiutano a controllare tempi e priorità.",
        },
    ]

    queries = [
        "Quali sono i punti principali del documento?",
        "Che cosa devo ricordare?",
        "Quali rischi o problemi vengono spiegati nel documento?",
    ]

    case_results = []
    detected_profiles = set()

    for case in cases:
        profile = registry.detect_profile(case["text"])
        detected_profiles.add(profile.get("profile_id"))

        if profile.get("profile_id") != case["expected_profile"]:
            errors.append(f"profile_detection_wrong:{case['expected_profile']}:{profile.get('profile_id')}")

        expansion = question_core.expand_queries(queries, profile)
        answers = []

        for row in expansion.get("queries", []):
            answers.append(
                relevance_core.build_answer(
                    row.get("original_query", ""),
                    row.get("expanded_query", ""),
                    case["text"],
                    profile,
                )
            )

        for row in expansion.get("queries", []):
            if not row.get("changed"):
                errors.append(f"query_not_expanded:{profile.get('profile_id')}:{row.get('original_query')}")

            q_errors = linguistic.check_question(row.get("expanded_query", ""), profile)
            if q_errors:
                errors.append(f"question_quality:{profile.get('profile_id')}:{q_errors}")

            if row.get("original_query", "").startswith("Che cosa devo ricordare") and row.get("query_type") != "study_memory":
                errors.append(f"study_memory_misclassified:{profile.get('profile_id')}:{row}")

        relevance_report = relevance_core.validate_report({"answers": answers}, profile)

        if relevance_report.get("status") != "PASS":
            errors.append(f"relevance_fail:{profile.get('profile_id')}:{relevance_report.get('errors')}")

        for answer in answers:
            text_errors = linguistic.check_text(answer.get("answer", ""), profile)
            if text_errors:
                errors.append(f"linguistic_fail:{profile.get('profile_id')}:{text_errors}")

        case_results.append(
            {
                "profile": profile.get("profile_id"),
                "domain": profile.get("domain_name"),
                "expansion": expansion,
                "answers": answers,
                "relevance": relevance_report,
            }
        )

    if len(detected_profiles) < 5:
        errors.append(f"multi_domain_not_enough:{sorted(detected_profiles)}")

    status = "PASS" if not errors else "FAIL"

    validation = {
        "validator": "valida_mini_llm_universal_core_split_v394u",
        "version": "V3.9.4U.1",
        "status": status,
        "errors": errors,
        "core_files": [str(path) for path in core_files],
        "profile_files": [str(path) for path in profile_files],
        "detected_profiles": sorted(detected_profiles),
        "case_results": case_results,
        "limits": [
            "Valida separazione fisica.",
            "Valida multi-dominio.",
            "Blocca termini specialistici nel core universale.",
            "Non sostituisce ancora la pipeline principale.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"
    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_universal_core_split_v394u_validation.json"
    md_path = report_dir / "mini_llm_universal_core_split_v394u_validation.md"

    json_path.write_text(json.dumps(validation, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Mini LLM Universal Core Split V3.9.4U.1",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Separazione fisica",
        "",
        "### Core universale",
    ]

    for path in core_files:
        lines.append(f"- `{path.relative_to(root)}`")

    lines.extend(["", "### Profili specialistici"])

    for path in profile_files:
        lines.append(f"- `{path.relative_to(root)}`")

    lines.extend(["", "## Profili rilevati nei test", "", f"- `{sorted(detected_profiles)}`", "", "## Risultati multi-dominio", ""])

    for result in case_results:
        lines.extend([f"### {result.get('domain')}", "", f"- Profilo: `{result.get('profile')}`", f"- Relevance: `{result.get('relevance', {}).get('status')}`", ""])
        for row in result.get("expansion", {}).get("queries", []):
            lines.extend([f"- Originale: `{row.get('original_query')}`", f"  Migliorata: `{row.get('expanded_query')}`"])
        lines.append("")

    lines.extend([
        "## Regola architetturale",
        "",
        "- Il core universale controlla lingua, domande e pertinenza.",
        "- I profili specialistici forniscono dominio e vocabolario.",
        "- I fix su domanda singola o risposta singola sono vietati.",
        "- Le specializzazioni sono ammesse solo come layer separati.",
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())
