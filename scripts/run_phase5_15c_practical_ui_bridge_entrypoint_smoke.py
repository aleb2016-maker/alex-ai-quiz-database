#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15C - practical UI/bridge smoke.

It validates the real path:
demo page -> /api/generate -> local bridge -> run_quality_checked_generator
-> generators -> runtime QM trace.
"""

from __future__ import annotations

import json
import subprocess
import sys
import time
import traceback
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
TRACE_JSON = REPORTS / "phase5_15c_ui_bridge_entrypoint_practical_trace_v1.json"
REPORT_JSON = REPORTS / "phase5_15c_ui_bridge_entrypoint_practical_report_v1.json"
REPORT_MD = REPORTS / "phase5_15c_ui_bridge_entrypoint_practical_report_v1.md"
SLOTS_JSON = REPORTS / "phase5_15c_slot_65_73_status_v1.json"
HTML_PAGE = ROOT / "demo-rag" / "test-documenti-universale.html"
BRIDGE_SCRIPT = ROOT / "scripts" / "run_phase5_14_3_local_backend_bridge.py"

API = "http://127.0.0.1:8765"
ENTRYPOINT = "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator"

EXPECTED_QM = {
    "summary": 55,
    "cards": 60,
    "study_questions": 51,
    "quiz": 63,
}

GENERATOR_LABELS = {
    "summary": "Riassunto",
    "cards": "Card",
    "study_questions": "Domande studio",
    "quiz": "Test/Quiz",
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


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def request_json(url: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 30) -> Tuple[int, Dict[str, Any]]:
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json"
    request = urllib.request.Request(url, data=data, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return int(response.status), json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(body)
        except Exception:
            parsed = {"error": body}
        return int(exc.code), parsed


def health() -> Optional[Dict[str, Any]]:
    try:
        status, payload = request_json(API + "/health", timeout=2)
        if status == 200 and payload.get("ok") is True:
            return payload
    except Exception:
        return None
    return None


def start_bridge_if_needed() -> Tuple[Optional[subprocess.Popen], List[str]]:
    defects: List[str] = []
    current = health()
    if current:
        if current.get("quality_entrypoint") == ENTRYPOINT:
            return None, defects
        defects.append("bridge attivo ma non collegato all'entrypoint 5.15B")
        return None, defects

    process = subprocess.Popen(
        [sys.executable, str(BRIDGE_SCRIPT)],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    for _ in range(40):
        time.sleep(0.25)
        current = health()
        if current and current.get("quality_entrypoint") == ENTRYPOINT:
            return process, defects
        if process.poll() is not None:
            stdout, stderr = process.communicate(timeout=2)
            defects.append(f"bridge terminato durante avvio: stdout={stdout[-500:]}; stderr={stderr[-500:]}")
            return process, defects
    defects.append("bridge non pronto su /health dopo 10 secondi")
    return process, defects


def output_present(result: Dict[str, Any]) -> bool:
    final_output = result.get("final_output") or result.get("raw_output") or result
    if isinstance(final_output, dict):
        if str(final_output.get("content") or "").strip():
            return True
        items = final_output.get("items")
        if isinstance(items, list) and len(items) > 0:
            return True
    return bool(str(final_output or "").strip())


def has_demo_input(text: str) -> bool:
    low = str(text or "").lower()
    return (
        "lorem ipsum" in low
        or "testo di esempio" in low
        or ("sicurezza informatica aziendale" in low and len(text) < 500)
    )


def call_generate(document_id: str, generator: str, text: str) -> Dict[str, Any]:
    status, payload = request_json(
        API + "/api/generate",
        {
            "kind": generator,
            "text": text,
            "strictNoFallback": True,
            "source": "phase5_15c_practical_smoke",
        },
        timeout=60,
    )
    result = payload.get("result") if isinstance(payload, dict) else {}
    if not isinstance(result, dict):
        result = {}

    expected = EXPECTED_QM[generator]
    defects: List[str] = []
    if status != 200 or payload.get("ok") is not True:
        defects.append(f"http_not_ok:{status}:{payload.get('error')}")
    if result.get("entrypoint") != ENTRYPOINT:
        defects.append("entrypoint_bypass_or_missing")
    if result.get("bridge_entrypoint_connected") is not True:
        defects.append("bridge_entrypoint_marker_missing")
    if result.get("input_verified") is not True:
        defects.append("input_not_verified")
    if not output_present(result):
        defects.append("output_empty")
    if not result.get("qm_runtime_trace"):
        defects.append("qm_runtime_trace_missing")
    if int(result.get("executed_qm_count") or 0) != expected:
        defects.append(f"qm_count_mismatch:{result.get('executed_qm_count')}!={expected}")
    if int(result.get("expected_qm_count") or 0) != expected:
        defects.append(f"expected_qm_count_mismatch:{result.get('expected_qm_count')}!={expected}")
    if result.get("all_motors_connected") is True and not result.get("qm_runtime_trace"):
        defects.append("all_motors_connected_without_trace")
    if result.get("all_motors_connected") is not True:
        defects.append("all_motors_connected_not_true")
    if result.get("connection_status") != "RUNTIME_TRACE_PROVED":
        defects.append(f"connection_status_not_runtime_trace:{result.get('connection_status')}")
    if has_demo_input(text):
        defects.append("fallback_demo_input_used")

    return {
        "document": document_id,
        "generator": generator,
        "http_status": status,
        "ok": payload.get("ok") is True,
        "output_non_empty": output_present(result),
        "input_verified": result.get("input_verified") is True,
        "trace_qm": bool(result.get("qm_runtime_trace")),
        "expected_qm_count": expected,
        "executed_qm_count": int(result.get("executed_qm_count") or 0),
        "all_motors_connected": result.get("all_motors_connected") is True,
        "connection_status": result.get("connection_status"),
        "fallback_absent": not has_demo_input(text),
        "entrypoint": result.get("entrypoint"),
        "bridge_entrypoint_connected": result.get("bridge_entrypoint_connected") is True,
        "status": result.get("status"),
        "approved": result.get("approved"),
        "defects": defects,
    }


def validate_quiz_ui_leak() -> Dict[str, Any]:
    html = HTML_PAGE.read_text(encoding="utf-8")
    defects: List[str] = []
    if '.correct' in html or '"correct"' in html or "'correct'" in html:
        defects.append("classe correct ancora presente nella pagina")
    if 'opt.is_correct ? "correct"' in html or "opt.is_correct ? 'correct'" in html:
        defects.append("classe correct derivata da is_correct nel render iniziale")
    if 'opt.is_correct ? " ✅"' in html or "opt.is_correct ? ' ✅'" in html or "✅" in html.split("function renderQuiz", 1)[-1]:
        defects.append("marker visivo risposta corretta presente nel render quiz")
    render_quiz = html.split("function renderQuiz", 1)[-1].split("function renderError", 1)[0]
    if "q.spiegazione" in render_quiz and "quizAnswerState" not in render_quiz:
        defects.append("spiegazione quiz renderizzata direttamente prima della scelta")
    if "quiz-feedback" not in render_quiz:
        defects.append("feedback quiz post-click mancante")
    return {
        "checked_file": str(HTML_PAGE.relative_to(ROOT)),
        "quiz_answer_leak_fixed": not defects,
        "defects": defects,
    }


def build_slot_report() -> Dict[str, Any]:
    slots = []
    for number in range(65, 74):
        slots.append(
            {
                "slot": f"registry_orchestration_slot_{number:03d}",
                "number": number,
                "status": "ORCHESTRATION_ONLY",
                "serve_as_concrete_motor": False,
                "serve_as_orchestration": True,
                "recommended_action": (
                    "Keep as orchestration metadata for now; materialize only if a distinct "
                    "runtime quality behavior is defined, otherwise exclude from concrete QM count."
                ),
                "source": "reports/phase5_15a_executable_registry_connection_proof_v1.json",
            }
        )
    payload = {
        "phase": "5.15C",
        "status": "PASS",
        "slots_clarified": True,
        "concrete_qm_count": 64,
        "slot_count": 9,
        "slots": slots,
    }
    write_json(SLOTS_JSON, payload)
    return payload


def build_report(
    cases: List[Dict[str, Any]],
    bridge_defects: List[str],
    quiz_ui: Dict[str, Any],
    slot_report: Dict[str, Any],
    bridge_started_by_smoke: bool,
) -> Dict[str, Any]:
    smoke_defects = list(bridge_defects)
    smoke_defects.extend(quiz_ui.get("defects") or [])
    for case in cases:
        smoke_defects.extend(f"{case['document']}/{case['generator']}: {d}" for d in case["defects"])

    practical_counts = {
        generator: max([case["executed_qm_count"] for case in cases if case["generator"] == generator] or [0])
        for generator in GENERATORS
    }
    practical_rows = []
    for generator in GENERATORS:
        expected = EXPECTED_QM[generator]
        actual = practical_counts[generator]
        practical_rows.append(
            {
                "generator": generator,
                "label": GENERATOR_LABELS[generator],
                "expected_qm_count": expected,
                "practical_qm_count_via_bridge": actual,
                "outcome": "PASS" if actual == expected else "FAIL",
            }
        )

    test_rows = []
    for case in cases:
        test_rows.append(
            {
                "document": case["document"],
                "generator": GENERATOR_LABELS[case["generator"]],
                "output_non_empty": case["output_non_empty"],
                "qm_trace": case["trace_qm"],
                "qm_count_correct": case["executed_qm_count"] == case["expected_qm_count"],
                "fallback_absent": case["fallback_absent"],
                "outcome": "PASS" if not case["defects"] else "FAIL",
            }
        )

    report = {
        "phase": "5.15C",
        "status": "PASS" if not smoke_defects else "FAIL",
        "bridge_connected_to_entrypoint_515b": not bridge_defects,
        "ui_connected_to_updated_bridge": 'API + "/api/generate"' in HTML_PAGE.read_text(encoding="utf-8"),
        "quiz_answer_leak_fixed": quiz_ui["quiz_answer_leak_fixed"],
        "slots_65_73_clarified": slot_report["slots_clarified"],
        "practical_four_generator_test": "PASS" if not [c for c in cases if c["defects"]] else "FAIL",
        "bridge_started_by_smoke": bridge_started_by_smoke,
        "expected_qm_counts": EXPECTED_QM,
        "practical_qm_counts": practical_counts,
        "practical_qm_table": practical_rows,
        "practical_test_rows": test_rows,
        "quiz_ui_check": quiz_ui,
        "slot_report_file": str(SLOTS_JSON.relative_to(ROOT)),
        "remaining_issues": [
            "Output quality can still be QUALITY_BLOCKED by real QM failures; this phase validates routing and trace, not content perfection.",
            "Slots 65-73 remain orchestration-only until distinct runtime behaviors are defined.",
        ],
        "smoke_defects": smoke_defects,
    }
    return report


def write_md(report: Dict[str, Any], slot_report: Dict[str, Any]) -> None:
    lines = [
        "# FASE 5.15C - UI/Bridge collegati all'entrypoint qualita",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Stato fase",
        "",
        f"- Bridge collegato all'entrypoint 5.15B: {report['bridge_connected_to_entrypoint_515b']}",
        f"- UI collegata al bridge aggiornato: {report['ui_connected_to_updated_bridge']}",
        f"- Quiz answer leak corretto: {report['quiz_answer_leak_fixed']}",
        f"- 9 slot chiariti: {report['slots_65_73_clarified']}",
        f"- Test pratico 4 generatori: {report['practical_four_generator_test']}",
        "",
        "## Conteggi QM pratici",
        "",
        "| Generatore | Conteggio atteso | Conteggio pratico via bridge/UI | Esito |",
        "| --- | ---: | ---: | --- |",
    ]
    for row in report["practical_qm_table"]:
        lines.append(
            f"| {row['label']} | {row['expected_qm_count']} | {row['practical_qm_count_via_bridge']} | {row['outcome']} |"
        )

    lines.extend([
        "",
        "## Test pratici",
        "",
        "| Documento | Generatore | Output non vuoto | Trace QM | Conteggio corretto | Fallback assente | Esito |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ])
    for row in report["practical_test_rows"]:
        lines.append(
            f"| {row['document']} | {row['generator']} | {row['output_non_empty']} | {row['qm_trace']} | {row['qm_count_correct']} | {row['fallback_absent']} | {row['outcome']} |"
        )

    lines.extend([
        "",
        "## Slot 65-73",
        "",
        "| Slot | Stato | Serve come motore concreto? | Serve come orchestrazione? | Azione consigliata |",
        "| --- | --- | --- | --- | --- |",
    ])
    for slot in slot_report["slots"]:
        lines.append(
            f"| `{slot['slot']}` | {slot['status']} | {slot['serve_as_concrete_motor']} | {slot['serve_as_orchestration']} | {slot['recommended_action']} |"
        )

    lines.extend(["", "## Problemi rimasti", ""])
    lines.extend(f"- {item}" for item in report["remaining_issues"])
    if report["smoke_defects"]:
        lines.extend(["", "## Smoke defects", ""])
        lines.extend(f"- {item}" for item in report["smoke_defects"])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    process = None
    cases: List[Dict[str, Any]] = []
    bridge_started = False
    bridge_defects: List[str] = []
    try:
        process, bridge_defects = start_bridge_if_needed()
        bridge_started = process is not None and not bridge_defects

        if not bridge_defects:
            for document_id, text in DOCUMENTS.items():
                for generator in GENERATORS:
                    try:
                        cases.append(call_generate(document_id, generator, text))
                    except Exception as exc:
                        cases.append(
                            {
                                "document": document_id,
                                "generator": generator,
                                "http_status": 0,
                                "ok": False,
                                "output_non_empty": False,
                                "input_verified": False,
                                "trace_qm": False,
                                "expected_qm_count": EXPECTED_QM[generator],
                                "executed_qm_count": 0,
                                "all_motors_connected": False,
                                "connection_status": "ERROR",
                                "fallback_absent": not has_demo_input(text),
                                "entrypoint": "",
                                "bridge_entrypoint_connected": False,
                                "status": "ERROR",
                                "approved": False,
                                "defects": [f"request_exception:{type(exc).__name__}:{exc}", traceback.format_exc(limit=4)],
                            }
                        )

        quiz_ui = validate_quiz_ui_leak()
        slot_report = build_slot_report()
        trace_payload = {
            "phase": "5.15C",
            "trace_type": "practical_ui_bridge_entrypoint_trace",
            "entrypoint": ENTRYPOINT,
            "case_count": len(cases),
            "bridge_started_by_smoke": bridge_started,
            "cases": cases,
        }
        write_json(TRACE_JSON, trace_payload)

        report = build_report(cases, bridge_defects, quiz_ui, slot_report, bridge_started)
        write_json(REPORT_JSON, report)
        write_md(report, slot_report)

        print(
            "FASE 5.15C smoke: "
            f"status={report['status']} "
            f"counts={report['practical_qm_counts']} "
            f"bridge_started={bridge_started}"
        )
        if report["smoke_defects"]:
            print("SMOKE DEFECTS:")
            for defect in report["smoke_defects"]:
                print(f"- {defect}")
            return 1
        return 0
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()


if __name__ == "__main__":
    raise SystemExit(main())
