#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12D — RUN CARD / SUMMARY / SOURCE QUALITY MOTORS

Esegue test sui 10 motori Card/Riassunto/Fonti ricostruiti.
Produce report JSON e Markdown.
Non collega ancora al registry da 33.
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

from backend.phase5_card_summary_source_quality_motors_v512d import (  # noqa: E402
    analyze_card_summary_source_quality,
    registry_entry,
    report_to_dict,
)


OUT_JSON = REPORTS_DIR / "phase5_12d_card_summary_source_quality_motors_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12d_card_summary_source_quality_motors_v1.md"

PHASE = "5.12D"
READY_LABEL = "CARD_SUMMARY_SOURCE_QUALITY_MOTORS_V512D_READY"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def base_good_payload() -> Dict[str, Any]:
    return {
        "source_text": (
            "Il backup periodico protegge i dati aziendali perché consente di recuperarli dopo errori, "
            "guasti o cancellazioni accidentali. L'autenticazione a due fattori riduce il rischio "
            "di accessi non autorizzati perché richiede una verifica aggiuntiva oltre alla password."
        ),
        "card_layout": {
            "variant": "didactic_card",
            "template": "title_key_points_source",
            "density": "balanced",
            "controlled": True,
        },
        "cards": [
            {
                "title": "Backup periodico dei dati",
                "key_message": (
                    "Il backup periodico riduce il rischio di perdita definitiva dei dati aziendali."
                ),
                "body": (
                    "La card spiega che salvare copie aggiornate permette di recuperare informazioni "
                    "dopo errori, guasti tecnici o cancellazioni accidentali."
                ),
                "bullets": [
                    "Protegge i dati da perdite improvvise.",
                    "Permette il recupero dopo guasti o errori.",
                    "Richiede copie aggiornate e controllate.",
                ],
                "source": "Fonte: sezione Backup periodico",
                "layout": {
                    "icon": "backup",
                    "density": "balanced",
                },
            },
            {
                "title": "Autenticazione a due fattori",
                "key_message": (
                    "La verifica aggiuntiva rende più sicuro l'accesso agli account aziendali."
                ),
                "body": (
                    "La card mostra che la password da sola può non bastare e che un secondo controllo "
                    "riduce il rischio di ingresso da parte di utenti non autorizzati."
                ),
                "bullets": [
                    "Aggiunge un controllo oltre alla password.",
                    "Riduce il rischio di accessi non autorizzati.",
                    "Rafforza la sicurezza degli account.",
                ],
                "source": "Fonte: sezione Autenticazione a due fattori",
                "layout": {
                    "icon": "security",
                    "density": "balanced",
                },
            },
        ],
        "summary": {
            "text": (
                "Il contenuto evidenzia due pratiche centrali per la sicurezza dei dati aziendali. "
                "Il backup periodico consente di recuperare informazioni dopo errori o guasti, mentre "
                "l'autenticazione a due fattori rafforza l'accesso agli account con una verifica aggiuntiva."
            ),
            "key_points": [
                "Il backup periodico riduce la perdita definitiva dei dati.",
                "La verifica aggiuntiva protegge meglio gli account aziendali.",
                "Le fonti indicano le sezioni usate per costruire le card.",
            ],
        },
        "sources": [
            {"label": "Fonte: sezione Backup periodico"},
            {"label": "Fonte: sezione Autenticazione a due fattori"},
        ],
    }


def bad_payload_for_motor(motor_id: str) -> Dict[str, Any]:
    payload = base_good_payload()

    if motor_id == "qm_023_card_riassunto_fonti_card_scritte_bene":
        payload["cards"][0]["title"] = "Card"
        payload["cards"][0]["key_message"] = "Documento analizzato."
        payload["cards"][0]["body"] = "Punto centrale."
    elif motor_id == "qm_024_card_riassunto_fonti_card_non_troppo_corte":
        payload["cards"][0]["key_message"] = "Il backup è utile."
        payload["cards"][0]["body"] = "Protegge i dati."
        payload["cards"][0]["bullets"] = []
    elif motor_id == "qm_025_card_riassunto_fonti_card_non_troppo_compresse":
        payload["cards"][0]["body"] = (
            "Il backup periodico protegge i dati aziendali perché consente il recupero dopo errori "
            "guasti cancellazioni accidentali problemi tecnici perdita di file incidenti interni "
            "mancanza di copie aggiornate e difficoltà operative che possono bloccare il lavoro "
            "delle persone e rallentare la continuità delle attività aziendali senza una struttura "
            "chiara di protezione e ripristino delle informazioni."
        )
        payload["cards"][0]["bullets"] = []
    elif motor_id == "qm_026_card_riassunto_fonti_messaggio_chiave_completo":
        payload["cards"][0]["key_message"] = "Dati."
    elif motor_id == "qm_027_card_riassunto_fonti_riassunto_chiaro":
        payload["summary"]["text"] = "Informazioni principali."
    elif motor_id == "qm_028_card_riassunto_fonti_punti_chiave_leggibili":
        payload["summary"]["key_points"] = ["Punto centrale.", "Varie cose."]
    elif motor_id == "qm_029_card_riassunto_fonti_fonti_visibili_belle":
        payload["sources"] = ["Backup"]
        payload["cards"][0]["source"] = "Backup"
    elif motor_id == "qm_030_card_riassunto_fonti_fonti_coerenti":
        payload["sources"] = [{"label": "Fonte: sezione Ricetta cucina"}]
        payload["cards"][0]["source"] = "Fonte: sezione Ricetta cucina"
    elif motor_id == "qm_031_card_riassunto_fonti_niente_fonti_brutte":
        payload["sources"] = [{"label": "knowledge_base_json/documento_analizzato.json"}]
        payload["cards"][0]["source"] = "knowledge_base_json/documento_analizzato.json"
    elif motor_id == "qm_032_card_riassunto_fonti_layout_grafico_controllato":
        payload.pop("card_layout", None)
        for card in payload["cards"]:
            card.pop("layout", None)

    return payload


def targeted_cases() -> List[Dict[str, Any]]:
    motor_ids = [
        "qm_023_card_riassunto_fonti_card_scritte_bene",
        "qm_024_card_riassunto_fonti_card_non_troppo_corte",
        "qm_025_card_riassunto_fonti_card_non_troppo_compresse",
        "qm_026_card_riassunto_fonti_messaggio_chiave_completo",
        "qm_027_card_riassunto_fonti_riassunto_chiaro",
        "qm_028_card_riassunto_fonti_punti_chiave_leggibili",
        "qm_029_card_riassunto_fonti_fonti_visibili_belle",
        "qm_030_card_riassunto_fonti_fonti_coerenti",
        "qm_031_card_riassunto_fonti_niente_fonti_brutte",
        "qm_032_card_riassunto_fonti_layout_grafico_controllato",
    ]

    return [
        {
            "id": f"case_{i + 23:03d}",
            "motor_id": motor_id,
            "payload": bad_payload_for_motor(motor_id),
            "expected_blocking": True,
        }
        for i, motor_id in enumerate(motor_ids)
    ]


def run_targeted_tests() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    for case in targeted_cases():
        report = analyze_card_summary_source_quality(case["payload"])
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
    report = analyze_card_summary_source_quality(payload)

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
    lines.append("# Fase 5.12D — Card Summary Source Quality Motors V1")
    lines.append("")
    lines.append(f"- Status: **{final_report['status']}**")
    lines.append(f"- Ready label: `{final_report['ready_label']}`")
    lines.append(f"- Generated at: `{final_report['generated_at']}`")
    lines.append(f"- Motori Card/Riassunto/Fonti ricostruiti: `{final_report['registry']['total_motors']}`")
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
        "Questi motori sono ricostruiti come controlli Card/Riassunto/Fonti universali. "
        "Non sono ancora collegati al registry da 33 motori. Il controllo layout è solo "
        "su dati e struttura della card, non su CSS/UI/PDF."
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
            "created_card_summary_source_quality_motors": True,
            "connected_to_33_registry": False,
            "changed_existing_33_motors": False,
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
        print(f"Motori Card/Riassunto/Fonti ricostruiti: {final_report['registry']['total_motors']}")
        print(f"Targeted tests: {targeted_passed}/{targeted_total}")
        print("Good case: PASS")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: card summary source quality motors not ready")
    print(f"Targeted tests: {targeted_passed}/{targeted_total}")
    print(f"Good case passed: {good_case['passed']}")
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
