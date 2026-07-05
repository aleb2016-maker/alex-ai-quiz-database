#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import copy
import json
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

sys.path.insert(0, str(ROOT))

from backend.phase5_test_quiz_quality_motors_v512e import (  # noqa: E402
    READY_LABEL,
    analyze_test_quiz_quality,
    registry_entry,
    report_to_dict,
)


PHASE = "5.12E"
OUT_JSON = REPORTS_DIR / "phase5_12e_test_quiz_quality_motors_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12e_test_quiz_quality_motors_v1.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def base_good_payload() -> Dict[str, Any]:
    return {
        "quiz": {
            "questions": [
                {
                    "question": "Quale pratica aiuta a recuperare dati dopo un errore o un guasto?",
                    "options": [
                        "Eseguire backup periodici controllati",
                        "Usare password semplici per tutti gli account",
                        "Conservare una sola copia locale dei file",
                        "Disattivare gli aggiornamenti di sicurezza",
                    ],
                    "visible_options": [
                        "Eseguire backup periodici controllati",
                        "Usare password semplici per tutti gli account",
                        "Conservare una sola copia locale dei file",
                        "Disattivare gli aggiornamenti di sicurezza",
                    ],
                    "correct_answer": "Eseguire backup periodici controllati",
                    "correct_answer_visible": "Eseguire backup periodici controllati",
                    "explanation": "Il backup periodico consente di recuperare dati dopo errori, guasti o cancellazioni accidentali.",
                    "category": "Sicurezza dati",
                    "subcategory": "Backup",
                },
                {
                    "question": "Perché l'autenticazione a due fattori aumenta la sicurezza di un account?",
                    "options": [
                        "Richiede una verifica aggiuntiva oltre alla password",
                        "Elimina la necessità di controllare gli accessi",
                        "Permette di condividere la password più facilmente",
                        "Rende inutili le copie di sicurezza",
                    ],
                    "visible_options": [
                        "Richiede una verifica aggiuntiva oltre alla password",
                        "Elimina la necessità di controllare gli accessi",
                        "Permette di condividere la password più facilmente",
                        "Rende inutili le copie di sicurezza",
                    ],
                    "correct_answer": "Richiede una verifica aggiuntiva oltre alla password",
                    "correct_answer_visible": "Richiede una verifica aggiuntiva oltre alla password",
                    "explanation": "La verifica aggiuntiva riduce il rischio di accessi non autorizzati anche se la password viene scoperta.",
                    "category": "Sicurezza account",
                    "subcategory": "Autenticazione",
                },
                {
                    "question": "Che cosa rende più sicura una procedura di ripristino dei dati?",
                    "options": [
                        "Testare regolarmente il recupero dai backup",
                        "Archiviare file senza controllare le copie",
                        "Usare sempre lo stesso archivio non verificato",
                        "Affidarsi solo alla memoria degli utenti",
                    ],
                    "visible_options": [
                        "Testare regolarmente il recupero dai backup",
                        "Archiviare file senza controllare le copie",
                        "Usare sempre lo stesso archivio non verificato",
                        "Affidarsi solo alla memoria degli utenti",
                    ],
                    "correct_answer": "Testare regolarmente il recupero dai backup",
                    "correct_answer_visible": "Testare regolarmente il recupero dai backup",
                    "explanation": "Il test di ripristino verifica che le copie siano davvero utilizzabili quando servono.",
                    "category": "Continuità operativa",
                    "subcategory": "Ripristino",
                },
            ]
        }
    }


def bad_payload_for_motor(motor_id: str) -> Dict[str, Any]:
    payload = copy.deepcopy(base_good_payload())
    q0 = payload["quiz"]["questions"][0]

    if motor_id == "qm_033_test_quiz_test_separato_da_card_riassunto_domande_studio":
        payload["cards"] = [{"title": "Backup", "body": "Card mescolata al test"}]
    elif motor_id == "qm_034_test_quiz_opzioni_interne_validate":
        q0["options"][1] = "A"
    elif motor_id == "qm_035_test_quiz_opzioni_visibili_pulite":
        q0["visible_options"][0] = "A) Eseguire backup periodici controllati"
    elif motor_id == "qm_036_test_quiz_risposta_corretta_interna":
        q0["correct_answer"] = ""
    elif motor_id == "qm_037_test_quiz_risposta_corretta_visibile":
        q0["correct_answer_visible"] = ""
    elif motor_id == "qm_038_test_quiz_mappa_sicura_tra_risposta_interna_e_visibile":
        q0["correct_answer"] = "Eseguire backup periodici controllati"
        q0["correct_answer_visible"] = "Usare password semplici per tutti gli account"
    elif motor_id == "qm_039_test_quiz_quattro_opzioni_per_domanda":
        q0["options"] = q0["options"][:3]
        q0["visible_options"] = q0["visible_options"][:3]
    elif motor_id == "qm_040_test_quiz_risposta_corretta_presente_tra_le_opzioni":
        q0["correct_answer"] = "Risposta corretta assente dalle opzioni"
        q0["correct_answer_visible"] = "Risposta corretta assente dalle opzioni"
    elif motor_id == "qm_041_test_quiz_distrattori_forti":
        q0["options"] = [
            "Eseguire backup periodici controllati",
            "Altro",
            "Dipende",
            "Non so",
        ]
        q0["visible_options"] = list(q0["options"])
    elif motor_id == "qm_042_test_quiz_niente_opzioni_duplicate_nella_stessa_domanda":
        q0["options"] = [
            "Eseguire backup periodici controllati",
            "Usare password semplici per tutti gli account",
            "Usare password semplici per tutti gli account",
            "Disattivare gli aggiornamenti di sicurezza",
        ]
        q0["visible_options"] = list(q0["options"])
    elif motor_id == "qm_043_test_quiz_niente_ripetizioni_globali_eccessive":
        for q in payload["quiz"]["questions"]:
            q["options"][1] = "Usare sempre la stessa opzione debole"
            q["visible_options"][1] = "Usare sempre la stessa opzione debole"
    elif motor_id == "qm_044_test_quiz_compatibilita_bridge_quiz_v3_5b":
        q0.pop("explanation", None)

    return payload


def targeted_cases() -> List[Dict[str, Any]]:
    ids = [m["id"] for m in registry_entry()["motors"]]
    return [
        {
            "case_id": f"case_{i + 33:03d}",
            "motor_id": mid,
            "payload": bad_payload_for_motor(mid),
            "expected_blocking": True,
        }
        for i, mid in enumerate(ids)
    ]


def run_targeted_tests() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for case in targeted_cases():
        report = analyze_test_quiz_quality(case["payload"])
        target = next((r for r in report.results if r.motor_id == case["motor_id"]), None)

        blocking_hits = 0
        if target:
            blocking_hits = sum(1 for i in target.issues if i.severity == "blocking")

        passed = blocking_hits > 0

        rows.append({
            "case_id": case["case_id"],
            "motor_id": case["motor_id"],
            "passed": passed,
            "blocking_hits": blocking_hits,
            "target_status": target.status if target else "MISSING",
            "issues": [asdict(i) for i in target.issues] if target else [],
        })

    return rows


def run_good_case() -> Dict[str, Any]:
    report = analyze_test_quiz_quality(base_good_payload())
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
    OUT_JSON.write_text(json.dumps(final_report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.12E — Test/Quiz Quality Motors V1")
    lines.append("")
    lines.append(f"- Status: **{final_report['status']}**")
    lines.append(f"- Ready label: `{final_report['ready_label']}`")
    lines.append(f"- Generated at: `{final_report['generated_at']}`")
    lines.append(f"- Motori Test/Quiz ricostruiti: `{final_report['registry']['total_motors']}`")
    lines.append(f"- Targeted tests passed: `{final_report['targeted_tests_passed']}/{final_report['targeted_tests_total']}`")
    lines.append(f"- Good case passed: `{final_report['good_case']['passed']}`")
    lines.append("")
    lines.append("## Motori ricostruiti")
    lines.append("")
    for m in final_report["registry"]["motors"]:
        lines.append(f"- `{m['id']}` — **{m['title']}**")
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
        "Questi motori sono ricostruiti come controlli specifici Test/Quiz. "
        "Non sono ancora collegati al registry da 43 motori e non sono ancora inseriti nella matrice sezioni."
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
            "created_test_quiz_quality_motors": True,
            "connected_to_43_registry": False,
            "added_to_section_matrix": False,
            "changed_existing_43_motors": False,
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
        print(f"Motori Test/Quiz ricostruiti: {final_report['registry']['total_motors']}")
        print(f"Targeted tests: {targeted_passed}/{targeted_total}")
        print("Good case: PASS")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: test quiz quality motors not ready")
    print(f"Targeted tests: {targeted_passed}/{targeted_total}")
    print(f"Good case passed: {good_case['passed']}")
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
