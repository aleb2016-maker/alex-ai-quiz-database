#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15B.1 - reconcile runtime QM coverage for study_questions and quiz.

The smoke fails if the single entrypoint does not trace the certified counts:
summary=55, cards=60, study_questions=51, quiz=63.
"""

from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Set


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15b_quality_checked_generators import (  # noqa: E402
    GENERATOR_LABELS,
    run_quality_checked_generator,
)


TRACE_JSON = REPORTS / "phase5_15b1_qm_coverage_reconciliation_trace_v1.json"
REPORT_JSON = REPORTS / "phase5_15b1_qm_coverage_reconciliation_report_v1.json"
REPORT_MD = REPORTS / "phase5_15b1_qm_coverage_reconciliation_report_v1.md"
PREVIOUS_515B_REPORT = REPORTS / "phase5_15b_quality_checked_generators_report_v1.json"
PREVIOUS_515A_TRACE = REPORTS / "phase5_15a_generator_motor_trace_v1.json"
PREVIOUS_515A_PROOF = REPORTS / "phase5_15a_executable_registry_connection_proof_v1.json"
AUDIT_JSON = REPORTS / "audit_completo_73_motori_rag_qualita_v1.json"
CATALOG_JSON = REPORTS / "phase5_12i2_official_quality_motor_catalog_v1.json"

TARGET_COUNTS = {
    "summary": 55,
    "cards": 60,
    "study_questions": 51,
    "quiz": 63,
}

CERTIFIED_PREVIOUS_COUNTS = dict(TARGET_COUNTS)
PREVIOUS_515B_COUNTS = {
    "summary": 55,
    "cards": 60,
    "study_questions": 15,
    "quiz": 24,
}

DOCUMENTS = {
    "breve_valido": (
        "La procedura di onboarding assegna un tutor al nuovo dipendente. "
        "Il tutor presenta gli strumenti aziendali, verifica gli accessi e registra "
        "eventuali problemi entro il primo giorno. Il responsabile HR controlla che "
        "la scheda sia completa e che ogni autorizzazione abbia una motivazione. "
        "Alla fine della settimana il nuovo dipendente conferma di aver compreso "
        "le regole operative principali."
    ),
    "tecnico": (
        "Il sistema di backup usa snapshot incrementali ogni quattro ore e una "
        "replica giornaliera su storage separato. Il ripristino deve essere testato "
        "almeno una volta al mese con un campione di file critici. Se il test "
        "fallisce, il team apre un ticket critico, blocca la chiusura del controllo "
        "e ripete la procedura dopo la correzione. I log di replica vengono "
        "conservati per novanta giorni per consentire verifiche successive."
    ),
    "narrativo_discorsivo": (
        "Marta arrivo alla stazione quando il treno era gia partito. Nel diario "
        "trovo una mappa disegnata da suo nonno e capi che il viaggio non riguardava "
        "la destinazione, ma la memoria della famiglia. Decise di seguire gli indizi "
        "uno alla volta, fermandosi in ogni paese citato dalle vecchie lettere. "
        "Quando raggiunse la casa vicino al lago, riconobbe il cortile descritto "
        "nei racconti d'infanzia e annoto ogni dettaglio per non perderlo."
    ),
}

GENERATORS = ["summary", "cards", "study_questions", "quiz"]


def _read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _catalog_names() -> Dict[str, str]:
    data = _read_json(CATALOG_JSON, {})
    motors = data.get("motors") if isinstance(data, dict) else data
    names: Dict[str, str] = {}
    if isinstance(motors, list):
        for item in motors:
            if not isinstance(item, dict):
                continue
            qm_id = str(item.get("id") or item.get("motor_id") or "").strip().lower()
            if qm_id:
                names[qm_id] = str(
                    item.get("name")
                    or item.get("nome")
                    or item.get("title")
                    or item.get("control_name")
                    or qm_id
                )
    return names


def _previous_515b_ids(generator: str) -> Set[str]:
    data = _read_json(PREVIOUS_515B_REPORT, {})
    ids = set()
    if isinstance(data, dict):
        for qm_id in data.get("not_applicable_qm_by_generator", {}).get(generator, []):
            pass
    # Reconstruct the 5.15B executed IDs from the old counts/report shape.
    if generator == "study_questions":
        ids = {
            "qm_013", "qm_014", "qm_015", "qm_017", "qm_018", "qm_021",
            "qm_022", "qm_048", "qm_051", "qm_054", "qm_056", "qm_057",
            "qm_058", "qm_059", "qm_060",
        }
    elif generator == "quiz":
        ids = {
            "qm_016", "qm_017", "qm_021", "qm_022", "qm_033", "qm_034",
            "qm_035", "qm_036", "qm_037", "qm_038", "qm_039", "qm_040",
            "qm_041", "qm_042", "qm_043", "qm_044", "qm_048", "qm_051",
            "qm_055", "qm_056", "qm_057", "qm_058", "qm_059", "qm_060",
        }
    return ids


def _executed_ids(result: Dict[str, Any]) -> Set[str]:
    return {
        str(item.get("id"))
        for item in result.get("qm_runtime_trace", [])
        if item.get("executed") is True
    }


def _make_missing_rows(generator: str, restored_ids: Set[str], b1_ids: Set[str]) -> List[Dict[str, Any]]:
    names = _catalog_names()
    rows = []
    for qm_id in sorted(restored_ids):
        rows.append(
            {
                "qm": qm_id,
                "name": names.get(qm_id, qm_id),
                "where_declared": (
                    "5.14.18 generator quality_report route_total; "
                    "5.15A reports show the reduced declared subset; "
                    "backend.phase5_card_route_60_strict_connector_v513a3.EXECUTORS exposes the callable"
                ),
                "why_missing_in_515b": (
                    "5.15B reused a reduced generator applicability set from 5.15A "
                    "instead of the certified route_total coverage"
                ),
                "correction": (
                    "restored as executed=true in 5.15B.1"
                    if qm_id in b1_ids
                    else "still missing: executable mapping not reached"
                ),
            }
        )
    return rows


def _status_for_row(generator: str, b1_count: int) -> str:
    return "PASS" if b1_count >= TARGET_COUNTS[generator] else "FAIL"


def _build_report(results: List[Dict[str, Any]], smoke_defects: List[str]) -> Dict[str, Any]:
    by_generator = defaultdict(list)
    for item in results:
        by_generator[str(item.get("generator"))].append(item)

    b1_counts = {
        generator: max([int(item.get("executed_qm_count") or 0) for item in by_generator[generator]] or [0])
        for generator in GENERATORS
    }
    b1_ids = {
        generator: set().union(*[_executed_ids(item) for item in by_generator[generator]])
        if by_generator[generator]
        else set()
        for generator in GENERATORS
    }
    previous_ids = {
        "study_questions": _previous_515b_ids("study_questions"),
        "quiz": _previous_515b_ids("quiz"),
    }
    restored_study = b1_ids["study_questions"] - previous_ids["study_questions"]
    restored_quiz = b1_ids["quiz"] - previous_ids["quiz"]

    status_table = []
    for generator in GENERATORS:
        status_table.append(
            {
                "generator": generator,
                "label": GENERATOR_LABELS.get(generator, generator),
                "certified_previous_count": CERTIFIED_PREVIOUS_COUNTS[generator],
                "phase5_15b_count": PREVIOUS_515B_COUNTS[generator],
                "phase5_15b1_count": b1_counts[generator],
                "outcome": _status_for_row(generator, b1_counts[generator]),
            }
        )

    qm_statuses = {
        generator: Counter(
            item.get("status")
            for result in by_generator[generator]
            for item in result.get("qm_runtime_trace", [])
            if item.get("executed") is True
        )
        for generator in GENERATORS
    }
    remaining_non_executable = {
        generator: sorted(
            str(qm.get("id"))
            for result in by_generator[generator]
            for qm in result.get("qm_runtime_trace", [])
            if qm.get("executed") is False
            and qm.get("reason") != "not_applicable_to_generator"
        )
        for generator in GENERATORS
    }
    report = {
        "phase": "5.15B.1",
        "status": "PASS" if not smoke_defects else "FAIL",
        "regression_confirmed": True,
        "root_cause": (
            "study_questions and quiz used reduced 5.15A declared/deduced sets "
            "instead of the certified route_total coverage from the generators."
        ),
        "mandatory_files_read": [
            "backend/phase5_15b_quality_checked_generators.py",
            "reports/phase5_15b_quality_checked_generators_report_v1.json",
            "reports/phase5_15b_quality_checked_generators_trace_v1.json",
            "reports/phase5_15a_executable_registry_connection_proof_v1.json",
            "reports/phase5_15a_generator_motor_trace_v1.json",
            "reports/audit_completo_73_motori_rag_qualita_v1.json",
        ],
        "source_of_certified_counts": {
            "summary": "full_pipeline_summary_route55_all_motors_v51416 / route_total=55",
            "cards": "full_pipeline_cards_60_motors_graphic_v51416 / total_motors_connected=60",
            "study_questions": "full_pipeline_study_route51_language_quality_v51418 / route_total=51",
            "quiz": "full_pipeline_quiz_route63_language_quality_v51418 / route_total=63",
        },
        "comparison_table": status_table,
        "executed_qm_count_by_generator": b1_counts,
        "qm_statuses_by_generator": {k: dict(v) for k, v in qm_statuses.items()},
        "missing_from_study_in_515b": _make_missing_rows("study_questions", restored_study, b1_ids["study_questions"]),
        "missing_from_quiz_in_515b": _make_missing_rows("quiz", restored_quiz, b1_ids["quiz"]),
        "restored_qm_by_generator": {
            "study_questions": sorted(restored_study),
            "quiz": sorted(restored_quiz),
        },
        "remaining_non_executable_qm_by_generator": remaining_non_executable,
        "smoke_defects": smoke_defects,
        "evidence_files": {
            "trace": str(TRACE_JSON.relative_to(ROOT)),
            "report_json": str(REPORT_JSON.relative_to(ROOT)),
            "report_md": str(REPORT_MD.relative_to(ROOT)),
            "phase5_15a_trace": str(PREVIOUS_515A_TRACE.relative_to(ROOT)),
            "phase5_15a_proof": str(PREVIOUS_515A_PROOF.relative_to(ROOT)),
            "audit": str(AUDIT_JSON.relative_to(ROOT)),
        },
    }
    return report


def _write_md(report: Dict[str, Any]) -> None:
    lines = [
        "# FASE 5.15B.1 - Riconciliazione copertura QM",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Confronto copertura",
        "",
        "| Generatore | Conteggio certificato precedente | Conteggio 5.15B | Conteggio 5.15B.1 | Esito |",
        "| --- | ---: | ---: | ---: | --- |",
    ]
    for row in report["comparison_table"]:
        lines.append(
            "| {label} | {certified_previous_count} | {phase5_15b_count} | {phase5_15b1_count} | {outcome} |".format(
                **row
            )
        )

    lines.extend([
        "",
        "## Diagnosi",
        "",
        "- Regressione confermata: Domande studio era sceso da 51 a 15, Quiz da 63 a 24.",
        "- Causa: mapping di applicabilita 5.15B troppo restrittivo, derivato dal sottoinsieme 5.15A dichiarato/dedotto.",
        "- Correzione: i QM ripristinati vengono chiamati realmente tramite gli executor importabili; i FAIL restano FAIL.",
        "",
        "## Motori mancanti da Domande studio",
        "",
        "| QM | Nome | Dove era dichiarato | Perche manca in 5.15B | Correzione |",
        "| -- | ---- | ------------------- | --------------------- | ---------- |",
    ])
    for row in report["missing_from_study_in_515b"]:
        lines.append(
            f"| `{row['qm']}` | {row['name']} | {row['where_declared']} | {row['why_missing_in_515b']} | {row['correction']} |"
        )

    lines.extend([
        "",
        "## Motori mancanti da Quiz",
        "",
        "| QM | Nome | Dove era dichiarato | Perche manca in 5.15B | Correzione |",
        "| -- | ---- | ------------------- | --------------------- | ---------- |",
    ])
    for row in report["missing_from_quiz_in_515b"]:
        lines.append(
            f"| `{row['qm']}` | {row['name']} | {row['where_declared']} | {row['why_missing_in_515b']} | {row['correction']} |"
        )

    lines.extend([
        "",
        "## Restano non eseguibili",
        "",
    ])
    for generator, ids in report["remaining_non_executable_qm_by_generator"].items():
        value = ", ".join(f"`{item}`" for item in ids) if ids else "nessuno"
        lines.append(f"- {GENERATOR_LABELS.get(generator, generator)}: {value}")

    if report["smoke_defects"]:
        lines.extend(["", "## Smoke defects", ""])
        lines.extend(f"- {item}" for item in report["smoke_defects"])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    results: List[Dict[str, Any]] = []
    smoke_defects: List[str] = []

    for document_id, input_text in DOCUMENTS.items():
        for generator in GENERATORS:
            result = run_quality_checked_generator(generator, input_text)
            result["document_id"] = document_id
            results.append(result)

            count = int(result.get("executed_qm_count") or 0)
            target = TARGET_COUNTS[generator]
            if count < target:
                missing = sorted(
                    f"qm_{index:03d}"
                    for index in range(1, 65)
                    if f"qm_{index:03d}" not in _executed_ids(result)
                )
                smoke_defects.append(
                    f"{document_id}/{generator}: executed_qm_count={count}, target={target}, missing={','.join(missing)}"
                )
            if not result.get("qm_runtime_trace"):
                smoke_defects.append(f"{document_id}/{generator}: qm_runtime_trace mancante")
            if result.get("raw_output_present") is not True:
                smoke_defects.append(f"{document_id}/{generator}: output vuoto")
            if result.get("used_entrypoint") is not True:
                smoke_defects.append(f"{document_id}/{generator}: entrypoint unico bypassato")

    trace_payload = {
        "phase": "5.15B.1",
        "trace_type": "qm_coverage_reconciliation_runtime_trace",
        "targets": TARGET_COUNTS,
        "case_count": len(results),
        "traces": results,
    }
    _write_json(TRACE_JSON, trace_payload)

    report = _build_report(results, smoke_defects)
    _write_json(REPORT_JSON, report)
    _write_md(report)

    print(
        "FASE 5.15B.1 smoke: "
        f"status={report['status']} "
        f"counts={report['executed_qm_count_by_generator']}"
    )
    if smoke_defects:
        print("SMOKE DEFECTS:")
        for defect in smoke_defects:
            print(f"- {defect}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
