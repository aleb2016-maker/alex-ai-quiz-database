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

from backend.phase5_advanced_language_repair_motors_v512f import (  # noqa: E402
    READY_LABEL,
    analyze_advanced_language_repair_quality,
    registry_entry,
    report_to_dict,
)


PHASE = "5.12F"
OUT_JSON = REPORTS_DIR / "phase5_12f_advanced_language_repair_motors_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12f_advanced_language_repair_motors_v1.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def base_good_payload() -> Dict[str, Any]:
    return {
        "context": {
            "theme": "Sicurezza dei dati aziendali",
            "subtheme": "Backup periodico",
            "category": "Protezione delle informazioni",
            "subcategory": "Ripristino dopo errore o guasto",
        },
        "text": (
            "Il backup periodico protegge i dati aziendali perché consente di recuperare informazioni "
            "dopo errori, guasti o cancellazioni accidentali. La procedura operativa viene presentata "
            "in modo chiaro e gli obiettivi principali vengono spiegati senza copiarli in modo meccanico."
        ),
    }


def bad_payload_for_motor(motor_id: str) -> Dict[str, Any]:
    payload = copy.deepcopy(base_good_payload())

    if motor_id == "qm_061_naturalezza_linguistica_naturalezza_linguistica_anti_keyword":
        payload["text"] = (
            "Backup, password, accesso, dati, sicurezza, autenticazione, rischio, account, "
            "ripristino, controllo, procedura, utenti."
        )

    elif motor_id == "qm_062_accordo_grammaticale_accordo_grammaticale_e_pronomi":
        payload["text"] = (
            "La regola operativa viene presentato nella card. "
            "Gli obiettivi principali vengono spiegati senza copiarlo."
        )

    elif motor_id == "qm_063_repair_contestuale_correzione_frasi_non_finite_usando_contesto_tema_sottotema_categorie_e_":
        payload["text"] = (
            "Il backup periodico consente di. "
            "La procedura viene spiegata usando."
        )

    elif motor_id == "qm_064_repair_ortografico_correzione_parole_con_lettere_invertite":
        payload["text"] = (
            "Il sotttotema serve per conrollare meglio la selezioa dei motori "
            "e decidere se oricostruire il controllo."
        )

    return payload


def targeted_cases() -> List[Dict[str, Any]]:
    ids = [m["id"] for m in registry_entry()["motors"]]
    return [
        {
            "case_id": f"case_{i + 61:03d}",
            "motor_id": mid,
            "payload": bad_payload_for_motor(mid),
            "expected_blocking": True,
        }
        for i, mid in enumerate(ids)
    ]


def run_targeted_tests() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for case in targeted_cases():
        report = analyze_advanced_language_repair_quality(case["payload"])
        target = next((r for r in report.results if r.motor_id == case["motor_id"]), None)

        blocking_hits = 0
        repair_hits = 0
        if target:
            blocking_hits = sum(1 for i in target.issues if i.severity == "blocking")
            repair_hits = sum(1 for i in target.issues if i.repaired_text)

        passed = blocking_hits > 0

        rows.append({
            "case_id": case["case_id"],
            "motor_id": case["motor_id"],
            "passed": passed,
            "blocking_hits": blocking_hits,
            "repair_hits": repair_hits,
            "target_status": target.status if target else "MISSING",
            "issues": [asdict(i) for i in target.issues] if target else [],
        })

    return rows


def run_good_case() -> Dict[str, Any]:
    report = analyze_advanced_language_repair_quality(base_good_payload())
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
    lines.append("# Fase 5.12F — Advanced Language / Repair Motors V1")
    lines.append("")
    lines.append(f"- Status: **{final_report['status']}**")
    lines.append(f"- Approved: `{final_report['approved']}`")
    lines.append(f"- Ready label: `{final_report['ready_label']}`")
    lines.append(f"- Generated at: `{final_report['generated_at']}`")
    lines.append(f"- Motori ricostruiti: `{final_report['registry']['total_motors']}`")
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
        lines.append(f"  - Repair hits: `{row['repair_hits']}`")
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
        "Questi motori sono controlli linguistici avanzati universali. "
        "Producono anche suggerimenti di repair, ma non modificano automaticamente la pipeline 5.11."
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
            "created_advanced_language_repair_motors": True,
            "connected_to_55_registry": False,
            "changed_existing_55_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "deleted_existing_files": False,
            "repair_suggestions_only": True,
        },
        "report_files": {
            "json": str(OUT_JSON.relative_to(ROOT)),
            "markdown": str(OUT_MD.relative_to(ROOT)),
        },
    }

    write_reports(final_report)

    if approved:
        print(f"PASS - Fase {PHASE}: {READY_LABEL}")
        print(f"Motori linguistici avanzati ricostruiti: {final_report['registry']['total_motors']}")
        print(f"Targeted tests: {targeted_passed}/{targeted_total}")
        print("Good case: PASS")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: advanced language repair motors not ready")
    print(f"Targeted tests: {targeted_passed}/{targeted_total}")
    print(f"Good case passed: {good_case['passed']}")
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
