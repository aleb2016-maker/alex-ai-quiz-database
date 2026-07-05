#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13C.1 — TEST STRICT REAL CONNECTOR

Controlla che:
- il connector 51 esista;
- motori_scrittura.py lo richiami davvero nel quality_report;
- la route canonica Domande studio sia 51;
- selector/orchestrator siano 8;
- quality controls siano 43;
- non ci siano defects/warnings.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_study_questions_real_connector_v513c1 import (
    build_study_questions_real_connection_report,
)

ROOT = Path(__file__).resolve().parents[1]
JSON_REPORT = ROOT / "reports" / "phase5_13c1_study_questions_51_real_connector_v1.json"
MD_REPORT = ROOT / "reports" / "phase5_13c1_study_questions_51_real_connector_v1.md"
MOTORI = ROOT / "backend" / "motori_scrittura.py"

SAMPLE_STUDY_QUESTIONS = [
    {
        "domanda": "Perché il controllo degli accessi riduce il rischio operativo?",
        "risposta_guida": (
            "Riduce il rischio perché limita l’uso delle informazioni alle persone autorizzate "
            "e rende più semplice individuare comportamenti anomali."
        ),
    },
    {
        "domanda": "In che modo il backup periodico protegge la continuità del lavoro?",
        "risposta_guida": (
            "Il backup consente di recuperare dati e documenti dopo errori, guasti o incidenti, "
            "evitando interruzioni prolungate."
        ),
    },
    {
        "domanda": "Perché una procedura scritta aiuta lo studio e il ripasso?",
        "risposta_guida": (
            "Una procedura scritta rende chiari i passaggi importanti, riduce ambiguità "
            "e permette di controllare se il contenuto è stato compreso."
        ),
    },
    {
        "domanda": "Quale collegamento c’è tra domande studio e risposte guida?",
        "risposta_guida": (
            "Le domande orientano il ripasso, mentre le risposte guida aiutano a verificare "
            "se il concetto è stato capito in modo concreto."
        ),
    },
]


def main() -> int:
    defects: list[str] = []
    warnings: list[str] = []

    motori_text = MOTORI.read_text(encoding="utf-8", errors="replace")

    required_anchors = [
        "FASE 5.13C.1 — STUDY QUESTIONS 51 REAL CONNECTOR",
        "build_study_questions_real_connection_report",
        '"study_questions_real_connection_v513c1": study_questions_real_connection_v513c1',
        "q52_build_quality_study_questions",
        "q52_validate_study_questions",
        "result.domande_studio = q52_build_quality_study_questions",
        "result.errors.extend(q52_validate_study_questions(result.domande_studio))",
    ]

    for anchor in required_anchors:
        if anchor not in motori_text:
            defects.append(f"Anchor reale mancante in motori_scrittura.py: {anchor}")

    report = build_study_questions_real_connection_report(
        SAMPLE_STUDY_QUESTIONS,
        upstream_errors=[],
    )

    if report["resolved_route_total"] != 51:
        defects.append(f"Route totale attesa 51, trovata {report['resolved_route_total']}")

    if report["resolved_study_quality_controls"] != 43:
        defects.append(
            f"Controlli qualità Domande studio attesi 43, trovati {report['resolved_study_quality_controls']}"
        )

    if report["resolved_selector_orchestrator"] != 8:
        defects.append(
            f"Selector/orchestrator attesi 8, trovati {report['resolved_selector_orchestrator']}"
        )

    if len(report["executed_motor_ids"]) != 51:
        defects.append(f"Motori eseguiti/tracciati attesi 51, trovati {len(report['executed_motor_ids'])}")

    if report["missing_motor_ids"]:
        defects.append(f"Motori mancanti: {report['missing_motor_ids']}")

    if report["defects"]:
        defects.extend(report["defects"])

    if report["warnings"]:
        warnings.extend(report["warnings"])

    final_status = (
        "PASS - Fase 5.13C.1: STUDY_QUESTIONS_51_REAL_CONNECTOR_READY"
        if not defects and not warnings
        else "FAIL - Fase 5.13C.1: STUDY_QUESTIONS_51_REAL_CONNECTOR_NOT_READY"
    )

    final_report = {
        "phase": "5.13C.1",
        "status": final_status,
        "study_route_total": report["resolved_route_total"],
        "study_quality_controls": report["resolved_study_quality_controls"],
        "selector_orchestrator": report["resolved_selector_orchestrator"],
        "executed_motor_count": len(report["executed_motor_ids"]),
        "executed_motor_ids": report["executed_motor_ids"],
        "route_attached_to_motori_scrittura_quality_report": True,
        "defects": defects,
        "warnings": warnings,
    }

    JSON_REPORT.write_text(
        json.dumps(final_report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    md_lines = [
        "# FASE 5.13C.1 — STUDY QUESTIONS 51 REAL CONNECTOR",
        "",
        f"Status: `{final_status}`",
        "",
        "## Conteggi",
        "",
        f"- Route Domande studio: `{final_report['study_route_total']}`",
        f"- Controlli qualità Domande studio: `{final_report['study_quality_controls']}`",
        f"- Selector/orchestrator: `{final_report['selector_orchestrator']}`",
        f"- Motori eseguiti/tracciati: `{final_report['executed_motor_count']}`",
        "",
        "## Motori eseguiti/tracciati",
        "",
    ]

    for motor_id in final_report["executed_motor_ids"]:
        md_lines.append(f"- `{motor_id}`")

    md_lines.extend([
        "",
        "## Defects",
        "",
        "- Nessuno" if not defects else "\n".join(f"- {item}" for item in defects),
        "",
        "## Warnings",
        "",
        "- Nessuno" if not warnings else "\n".join(f"- {item}" for item in warnings),
        "",
        "## Note",
        "",
        "- La route 51 non è solo materializzata: viene richiamata nel quality_report reale di `backend/motori_scrittura.py`.",
        "- Nessuna UI/PDF/app è stata modificata.",
    ])

    MD_REPORT.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(final_status)
    print(f"Route Domande studio: {final_report['study_route_total']}")
    print(f"Controlli qualità Domande studio: {final_report['study_quality_controls']}")
    print(f"Selector/orchestrator: {final_report['selector_orchestrator']}")
    print(f"Motori eseguiti/tracciati: {final_report['executed_motor_count']}")
    print(f"JSON report: {JSON_REPORT}")
    print(f"Markdown report: {MD_REPORT}")

    if defects:
        print("Defects:")
        for defect in defects:
            print(f"- {defect}")
        return 1

    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
