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

from backend.phase5_contextual_duplicate_motors_v512g import (  # noqa: E402
    READY_LABEL,
    analyze_contextual_duplicate_quality,
    registry_entry,
    report_to_dict,
)


PHASE = "5.12G"
OUT_JSON = REPORTS_DIR / "phase5_12g_contextual_duplicate_motors_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12g_contextual_duplicate_motors_v1.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def base_good_payload() -> Dict[str, Any]:
    return {
        "items": [
            {
                "section": "card",
                "kind": "card",
                "purpose": "messaggio_chiave",
                "text": "Il backup periodico protegge i dati aziendali da errori, guasti e cancellazioni accidentali.",
            },
            {
                "section": "summary",
                "kind": "summary",
                "purpose": "sintesi",
                "text": "La sintesi evidenzia che copie regolari permettono di recuperare informazioni quando si verifica un problema tecnico.",
            },
            {
                "section": "study_questions",
                "kind": "study_question",
                "purpose": "ripasso",
                "text": "Perché il backup periodico aiuta a ridurre il rischio di perdita dei dati?",
            },
            {
                "section": "test_quiz",
                "kind": "quiz_question",
                "purpose": "verifica",
                "text": "Quale vantaggio offre un backup periodico in un contesto aziendale?",
            },
            {
                "section": "sources",
                "kind": "source_note",
                "purpose": "riferimento",
                "text": "La fonte collegata descrive il recupero dei dati come misura di continuità operativa.",
            },
        ]
    }


def bad_payload_for_motor(motor_id: str) -> Dict[str, Any]:
    payload = copy.deepcopy(base_good_payload())

    if motor_id == "qm_045_duplicati_contestuali_duplicati_esatti":
        payload["items"] = [
            {
                "section": "card",
                "kind": "card",
                "purpose": "messaggio_chiave",
                "text": "Il backup periodico protegge i dati aziendali da errori e guasti.",
            },
            {
                "section": "card",
                "kind": "card",
                "purpose": "messaggio_chiave",
                "text": "Il backup periodico protegge i dati aziendali da errori e guasti.",
            },
        ]

    elif motor_id == "qm_046_duplicati_contestuali_quasi_duplicati":
        payload["items"] = [
            {
                "section": "summary",
                "kind": "summary",
                "purpose": "sintesi",
                "text": "Il backup periodico protegge i dati aziendali in caso di errore.",
            },
            {
                "section": "summary",
                "kind": "summary",
                "purpose": "sintesi",
                "text": "Il backup periodico protegge i dati aziendali in caso di guasto.",
            },
        ]

    elif motor_id == "qm_047_duplicati_contestuali_ripetizioni_inutili":
        payload["items"] = [
            {
                "section": "card",
                "kind": "card",
                "purpose": "messaggio_chiave",
                "text": (
                    "Il backup protegge i dati aziendali. "
                    "Il backup protegge i dati aziendali. "
                    "Il backup protegge i dati aziendali."
                ),
            },
        ]

    elif motor_id == "qm_048_duplicati_contestuali_ripetizioni_meccaniche_tra_domande":
        payload["items"] = [
            {
                "section": "test_quiz",
                "kind": "quiz_question",
                "purpose": "verifica",
                "text": "Che cosa protegge il backup aziendale?",
            },
            {
                "section": "test_quiz",
                "kind": "quiz_question",
                "purpose": "verifica",
                "text": "Che cosa protegge il backup periodico?",
            },
            {
                "section": "test_quiz",
                "kind": "quiz_question",
                "purpose": "verifica",
                "text": "Che cosa protegge il backup dei dati?",
            },
        ]

    elif motor_id == "qm_049_duplicati_contestuali_frasi_troppo_simili":
        payload["items"] = [
            {
                "section": "summary",
                "kind": "summary",
                "purpose": "sintesi",
                "text": (
                    "Il backup protegge i dati aziendali dagli errori. "
                    "Il backup protegge i dati aziendali dagli errori gravi."
                ),
            },
        ]

    elif motor_id == "qm_050_duplicati_contestuali_stesso_contenuto_ripetuto_senza_motivo":
        payload["items"] = [
            {
                "section": "card",
                "kind": "text",
                "purpose": "",
                "text": "Il backup protegge i dati aziendali da errori e guasti.",
            },
            {
                "section": "summary",
                "kind": "text",
                "purpose": "",
                "text": "Il backup protegge i dati aziendali da errori e guasti.",
            },
            {
                "section": "study_questions",
                "kind": "text",
                "purpose": "",
                "text": "Il backup protegge i dati aziendali da errori e guasti.",
            },
        ]

    return payload


def targeted_cases() -> List[Dict[str, Any]]:
    ids = [m["id"] for m in registry_entry()["motors"]]
    return [
        {
            "case_id": f"case_{i + 45:03d}",
            "motor_id": mid,
            "payload": bad_payload_for_motor(mid),
            "expected_blocking": True,
        }
        for i, mid in enumerate(ids)
    ]


def run_targeted_tests() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for case in targeted_cases():
        report = analyze_contextual_duplicate_quality(case["payload"])
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
    report = analyze_contextual_duplicate_quality(base_good_payload())
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
    lines.append("# Fase 5.12G — Contextual Duplicate Motors V1")
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
    lines.append("## Regola duplicati contestuali")
    lines.append("")
    lines.append(
        "Il controllo non boccia lo stesso concetto quando appare in sezioni diverse "
        "con funzioni diverse. Blocca solo duplicati meccanici, inutili o senza motivo."
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
            "created_contextual_duplicate_motors": True,
            "connected_to_59_registry": False,
            "changed_existing_59_motors": False,
            "changed_pipeline_5_11": False,
            "changed_ui_pdf_css_app": False,
            "deleted_existing_files": False,
            "contextual_not_global": True,
        },
        "report_files": {
            "json": str(OUT_JSON.relative_to(ROOT)),
            "markdown": str(OUT_MD.relative_to(ROOT)),
        },
    }

    write_reports(final_report)

    if approved:
        print(f"PASS - Fase {PHASE}: {READY_LABEL}")
        print(f"Motori duplicati contestuali ricostruiti: {final_report['registry']['total_motors']}")
        print(f"Targeted tests: {targeted_passed}/{targeted_total}")
        print("Good case: PASS")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: contextual duplicate motors not ready")
    print(f"Targeted tests: {targeted_passed}/{targeted_total}")
    print(f"Good case passed: {good_case['passed']}")
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
