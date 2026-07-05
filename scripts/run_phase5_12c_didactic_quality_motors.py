#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12C — RUN DIDACTIC QUALITY MOTORS

Esegue test sui 10 motori qualità didattica ricostruiti.
Produce report JSON e Markdown.
Non collega ancora al registry da 23.
"""

from __future__ import annotations

import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

sys.path.insert(0, str(ROOT))

from backend.phase5_didactic_quality_motors_v512c import (  # noqa: E402
    analyze_didactic_quality,
    registry_entry,
    report_to_dict,
)


OUT_JSON = REPORTS_DIR / "phase5_12c_didactic_quality_motors_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12c_didactic_quality_motors_v1.md"

PHASE = "5.12C"
READY_LABEL = "DIDACTIC_QUALITY_MOTORS_V512C_READY"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def base_good_payload() -> Dict[str, Any]:
    return {
        "source_text": (
            "Il backup periodico protegge i dati perché permette di recuperarli dopo errori, "
            "guasti o cancellazioni accidentali. L'autenticazione a due fattori riduce il rischio "
            "di accessi non autorizzati perché richiede una verifica aggiuntiva oltre alla password."
        ),
        "categories": ["Sicurezza dei dati"],
        "subcategories": ["Backup periodico", "Autenticazione a due fattori"],
        "study_questions": [
            {
                "question": "Perché il backup periodico aiuta a proteggere i dati aziendali?",
                "guide_answer": (
                    "Il backup periodico protegge i dati perché consente di recuperarli dopo errori, "
                    "guasti o cancellazioni accidentali, riducendo il rischio di perdita definitiva."
                ),
            },
            {
                "question": "Come l'autenticazione a due fattori riduce gli accessi non autorizzati?",
                "guide_answer": (
                    "L'autenticazione a due fattori riduce gli accessi non autorizzati perché richiede "
                    "una verifica aggiuntiva oltre alla password e rende più difficile l'ingresso di utenti non autorizzati."
                ),
            },
        ],
        "quiz": [
            {
                "question": "Quale pratica aiuta a recuperare dati dopo un errore o un guasto?",
                "options": [
                    "Backup periodico",
                    "Colore dell'interfaccia",
                    "Nome del documento",
                    "Ordine casuale delle sezioni",
                ],
                "correct_answer": "Backup periodico",
                "explanation": (
                    "La risposta corretta è backup periodico perché permette di recuperare dati "
                    "dopo errori, guasti o cancellazioni accidentali."
                ),
            }
        ],
    }


def bad_payload_for_motor(motor_id: str) -> Dict[str, Any]:
    payload = base_good_payload()

    if motor_id == "qm_013_qualita_didattica_domande_studio_naturali":
        payload["study_questions"][0]["question"] = "Documento analizzato?"
    elif motor_id == "qm_014_qualita_didattica_domande_studio_utili_per_ripassare":
        payload["study_questions"][0]["question"] = "È vero che il documento parla?"
    elif motor_id == "qm_015_qualita_didattica_risposte_guida_specifiche":
        payload["study_questions"][0]["guide_answer"] = "È importante e utile."
    elif motor_id == "qm_016_qualita_didattica_spiegazioni_test_chiare":
        payload["quiz"][0]["explanation"] = "È quella giusta."
    elif motor_id == "qm_017_qualita_didattica_spiegazioni_non_troppo_corte":
        payload["quiz"][0]["explanation"] = "Perché sì."
    elif motor_id == "qm_018_qualita_didattica_tono_didattico_finale":
        payload["study_questions"][0]["guide_answer"] = "Boh, è facile, basta leggere."
        payload["quiz"][0]["explanation"] = "Boh, è facile."
    elif motor_id == "qm_019_qualita_didattica_categorie_presenti":
        payload.pop("categories", None)
    elif motor_id == "qm_020_qualita_didattica_sottocategorie_presenti":
        payload.pop("subcategories", None)
    elif motor_id == "qm_021_qualita_didattica_coerenza_tra_domanda_risposta_e_contenuto":
        payload["study_questions"][0]["question"] = "Perché il backup periodico aiuta a proteggere i dati aziendali?"
        payload["study_questions"][0]["guide_answer"] = (
            "La fotosintesi permette alle piante di trasformare la luce in energia chimica."
        )
    elif motor_id == "qm_022_qualita_didattica_niente_risposte_vaghe":
        payload["study_questions"][0]["guide_answer"] = "Dipende, ci sono varie cose e diversi aspetti importanti."

    return payload


def targeted_cases() -> List[Dict[str, Any]]:
    motor_ids = [
        "qm_013_qualita_didattica_domande_studio_naturali",
        "qm_014_qualita_didattica_domande_studio_utili_per_ripassare",
        "qm_015_qualita_didattica_risposte_guida_specifiche",
        "qm_016_qualita_didattica_spiegazioni_test_chiare",
        "qm_017_qualita_didattica_spiegazioni_non_troppo_corte",
        "qm_018_qualita_didattica_tono_didattico_finale",
        "qm_019_qualita_didattica_categorie_presenti",
        "qm_020_qualita_didattica_sottocategorie_presenti",
        "qm_021_qualita_didattica_coerenza_tra_domanda_risposta_e_contenuto",
        "qm_022_qualita_didattica_niente_risposte_vaghe",
    ]

    return [
        {
            "id": f"case_{i + 13:03d}",
            "motor_id": motor_id,
            "payload": bad_payload_for_motor(motor_id),
            "expected_blocking": True,
        }
        for i, motor_id in enumerate(motor_ids)
    ]


def run_targeted_tests() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for case in targeted_cases():
        report = analyze_didactic_quality(case["payload"])
        target_result = next((r for r in report.results if r.motor_id == case["motor_id"]), None)

        blocking_hits = 0
        if target_result:
            blocking_hits = sum(1 for i in target_result.issues if i.severity == "blocking")

        passed = blocking_hits > 0 if case["expected_blocking"] else blocking_hits == 0

        rows.append({
            "case_id": case["id"],
            "motor_id": case["motor_id"],
            "passed": passed,
            "blocking_hits": blocking_hits,
            "expected_blocking": case["expected_blocking"],
            "target_status": target_result.status if target_result else "MISSING",
            "issues": [asdict(i) for i in target_result.issues] if target_result else [],
        })

    return rows


def run_good_case() -> Dict[str, Any]:
    payload = base_good_payload()
    report = analyze_didactic_quality(payload)

    return {
        "passed": report.blocking_issues == 0,
        "blocking_issues": report.blocking_issues,
        "warning_issues": report.warning_issues,
        "status": report.status,
        "approved": report.approved,
        "full_report": report_to_dict(report),
    }


def write_reports(final_report: Dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(
        json.dumps(final_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append("# Fase 5.12C — Didactic Quality Motors V1")
    lines.append("")
    lines.append(f"- Status: **{final_report['status']}**")
    lines.append(f"- Ready label: `{final_report['ready_label']}`")
    lines.append(f"- Generated at: `{final_report['generated_at']}`")
    lines.append(f"- Motori didattici ricostruiti: `{final_report['registry']['total_motors']}`")
    lines.append(f"- Targeted tests passed: `{final_report['targeted_tests_passed']}/{final_report['targeted_tests_total']}`")
    lines.append(f"- Good case passed: `{final_report['good_case']['passed']}`")
    lines.append("")
    lines.append("## Motori ricostruiti")
    lines.append("")
    for m in final_report["registry"]["motors"]:
        lines.append(f"- `{m['id']}` — **{m['title']}**")
        lines.append(f"  - Type: `{m['type']}`")
        lines.append(f"  - Severity: `{m['severity']}`")
        lines.append("")
    lines.append("## Targeted tests")
    lines.append("")
    for row in final_report["targeted_tests"]:
        lines.append(f"- `{row['case_id']}` — `{row['motor_id']}`")
        lines.append(f"  - Passed: `{row['passed']}`")
        lines.append(f"  - Blocking hits: `{row['blocking_hits']}`")
        lines.append("")
    lines.append("## Good case")
    lines.append("")
    lines.append(f"- Passed: `{final_report['good_case']['passed']}`")
    lines.append(f"- Blocking issues: `{final_report['good_case']['blocking_issues']}`")
    lines.append(f"- Warning issues: `{final_report['good_case']['warning_issues']}`")
    lines.append("")
    lines.append("## Scope guard")
    lines.append("")
    for k, v in final_report["registry"]["scope_guard"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append("## Nota tecnica")
    lines.append("")
    lines.append(
        "Questi motori sono ricostruiti come controlli didattici universali. "
        "Non sono ancora collegati al registry da 23 motori. Il collegamento va fatto "
        "solo dopo checkpoint e regressione dedicata."
    )
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    targeted = run_targeted_tests()
    good_case = run_good_case()

    targeted_passed = sum(1 for x in targeted if x["passed"])
    targeted_total = len(targeted)

    approved = targeted_passed == targeted_total and good_case["passed"]

    final_report = {
        "phase": PHASE,
        "generated_at": now_iso(),
        "status": "PASS" if approved else "FAIL",
        "approved": approved,
        "ready_label": READY_LABEL if approved else None,
        "registry": registry_entry(),
        "targeted_tests_total": targeted_total,
        "targeted_tests_passed": targeted_passed,
        "targeted_tests": targeted,
        "good_case": good_case,
        "scope_guard": {
            "created_didactic_quality_motors": True,
            "connected_to_23_registry": False,
            "changed_existing_23_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "deleted_existing_files": False,
        },
        "report_files": {
            "json": str(OUT_JSON.relative_to(ROOT)),
            "markdown": str(OUT_MD.relative_to(ROOT)),
        },
    }

    write_reports(final_report)

    if approved:
        print(f"PASS - Fase {PHASE}: {READY_LABEL}")
        print(f"Motori didattici ricostruiti: {final_report['registry']['total_motors']}")
        print(f"Targeted tests: {targeted_passed}/{targeted_total}")
        print("Good case: PASS")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: didactic quality motors not ready")
    print(f"Targeted tests: {targeted_passed}/{targeted_total}")
    print(f"Good case passed: {good_case['passed']}")
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
