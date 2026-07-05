#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12B — RUN TEXT QUALITY MOTORS

Esegue test sui 12 motori qualità testuale ricostruiti.
Produce report JSON e Markdown.
Non collega ancora alla pipeline 5.11.
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

from backend.phase5_text_quality_motors_v512b import (  # noqa: E402
    analyze_text_quality,
    registry_entry,
    report_to_dict,
)


OUT_JSON = REPORTS_DIR / "phase5_12b_text_quality_motors_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12b_text_quality_motors_v1.md"

PHASE = "5.12B"
READY_LABEL = "TEXT_QUALITY_MOTORS_V512B_READY"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def targeted_cases() -> List[Dict[str, Any]]:
    return [
        {
            "id": "case_001_grammar",
            "motor_id": "qm_001_qualita_testuale_grammatica_italiana_corretta",
            "text": "Regola operativa viene presentato nel riepilogo.",
            "expected_blocking": True,
        },
        {
            "id": "case_002_accents",
            "motor_id": "qm_002_qualita_testuale_accenti_corretti",
            "text": "Perche puo essere piu utile gia da oggi, cioe cosi pero qual'e il motivo?",
            "expected_blocking": True,
        },
        {
            "id": "case_003_apostrophes",
            "motor_id": "qm_003_qualita_testuale_apostrofi_corretti",
            "text": "L utente salva un informazione e un idea. Siamo d accordo.",
            "expected_blocking": True,
        },
        {
            "id": "case_004_punctuation",
            "motor_id": "qm_004_qualita_testuale_punteggiatura_corretta",
            "text": "Il riassunto contiene concetti utili,,, e termina male",
            "expected_blocking": True,
        },
        {
            "id": "case_005_spacing",
            "motor_id": "qm_005_qualita_testuale_spazi_corretti_prima_e_dopo_punteggiatura",
            "text": "Il testo è chiaro ,ma deve essere corretto.Bene.",
            "expected_blocking": True,
        },
        {
            "id": "case_006_complete_sentences",
            "motor_id": "qm_006_qualita_testuale_frasi_complete",
            "text": "Obiettivi principali senza contesto operativo chiaro.",
            "expected_blocking": True,
        },
        {
            "id": "case_007_broken_sentences",
            "motor_id": "qm_007_qualita_testuale_assenza_di_frasi_spezzate",
            "text": "Il sistema organizza i contenuti\nin sezioni utili per il ripasso.",
            "expected_blocking": True,
        },
        {
            "id": "case_008_unfinished",
            "motor_id": "qm_008_qualita_testuale_assenza_di_frasi_non_terminate",
            "text": "Il riassunto descrive le regole operative con",
            "expected_blocking": True,
        },
        {
            "id": "case_009_suspicious_endings",
            "motor_id": "qm_009_qualita_testuale_assenza_di_finali_sospetti",
            "text": "La card spiega il concetto principale di.",
            "expected_blocking": True,
        },
        {
            "id": "case_010_fillers",
            "motor_id": "qm_010_qualita_testuale_assenza_di_frasi_riempitive",
            "text": "In questo documento viene analizzato il tema. È importante sottolineare diversi elementi importanti.",
            "expected_blocking": True,
        },
        {
            "id": "case_011_generic",
            "motor_id": "qm_011_qualita_testuale_assenza_di_testo_generico",
            "text": "Il documento analizzato contiene contenuti generati e un punto centrale.",
            "expected_blocking": True,
        },
        {
            "id": "case_012_fallback_demo",
            "motor_id": "qm_012_qualita_testuale_assenza_di_vecchi_fallback_demo_test",
            "text": "Fallback demo con knowledge_base_json e sicurezza informatica aziendale.",
            "expected_blocking": True,
        },
    ]


def good_case_text() -> str:
    return (
        "Il sistema organizza le informazioni in sezioni chiare. "
        "Le domande guidano il ripasso e le fonti indicano il contesto usato. "
        "Ogni card presenta un messaggio specifico, leggibile e collegato al contenuto reale."
    )


def run_targeted_tests() -> List[Dict[str, Any]]:
    rows = []

    for case in targeted_cases():
        report = analyze_text_quality(case["text"])
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
    text = good_case_text()
    report = analyze_text_quality(text)

    blocking = report.blocking_issues
    passed = blocking == 0

    return {
        "passed": passed,
        "blocking_issues": blocking,
        "warning_issues": report.warning_issues,
        "status": report.status,
        "approved": report.approved,
        "repaired_text": report.repaired_text,
        "full_report": report_to_dict(report),
    }


def write_reports(final_report: Dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    OUT_JSON.write_text(
        json.dumps(final_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: List[str] = []
    lines.append("# Fase 5.12B — Text Quality Motors V1")
    lines.append("")
    lines.append(f"- Status: **{final_report['status']}**")
    lines.append(f"- Ready label: `{final_report['ready_label']}`")
    lines.append(f"- Generated at: `{final_report['generated_at']}`")
    lines.append(f"- Motori testuali ricostruiti: `{final_report['registry']['total_motors']}`")
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
        "Questi motori sono ricostruiti come controlli rule-based universali. "
        "Non sono ancora collegati alla pipeline 5.11. Il collegamento va fatto "
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
            "created_text_quality_motors": True,
            "connected_to_pipeline_5_11": False,
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
        print(f"Motori testuali ricostruiti: {final_report['registry']['total_motors']}")
        print(f"Targeted tests: {targeted_passed}/{targeted_total}")
        print(f"Good case: PASS")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: text quality motors not ready")
    print(f"Targeted tests: {targeted_passed}/{targeted_total}")
    print(f"Good case passed: {good_case['passed']}")
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
