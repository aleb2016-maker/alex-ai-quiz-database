#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15D - real page/generator smoke.

Validates the practical route used by the clean page:
UI page -> /api/generate -> bridge -> quality entrypoint -> visible output.
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
BRIDGE_SCRIPT = ROOT / "scripts" / "run_phase5_14_3_local_backend_bridge.py"
HTML_PAGE = ROOT / "demo-rag" / "test-documenti-universale.html"

API = "http://127.0.0.1:8765"
PAGE_URL = "http://localhost:8000/demo-rag/test-documenti-universale.html"
ENTRYPOINT = "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator"

TRACE_JSON = REPORTS / "phase5_15d_real_page_generators_trace_v1.json"
REPORT_JSON = REPORTS / "phase5_15d_real_page_generators_report_v1.json"
REPORT_MD = REPORTS / "phase5_15d_real_page_generators_report_v1.md"

EXPECTED_QM = {
    "summary": 55,
    "cards": 60,
    "study_questions": 51,
    "quiz": 63,
}

LABELS = {
    "summary": "Riassunto",
    "cards": "Card",
    "study_questions": "Domande studio",
    "quiz": "Test/Quiz",
}

WAREHOUSE_TEXT = (
    "La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, "
    "controllare, registrare e spedire i prodotti. Quando arriva una nuova merce, l’operatore verifica "
    "il documento di trasporto, controlla quantità e integrità degli articoli e segnala eventuali differenze. "
    "I prodotti conformi vengono registrati nel sistema gestionale e assegnati a una posizione precisa nel magazzino.\n\n"
    "Durante la preparazione degli ordini, il sistema genera una lista di prelievo con codice articolo, quantità "
    "richiesta e posizione. L’operatore raccoglie i prodotti, controlla che corrispondano all’ordine e li porta "
    "nell’area di imballaggio. Prima della spedizione, un secondo controllo riduce il rischio di errori, prodotti "
    "mancanti o articoli scambiati.\n\n"
    "La tracciabilità è importante perché permette di sapere dove si trova ogni prodotto, chi ha eseguito le "
    "operazioni e quando sono avvenute. Un processo ben organizzato riduce ritardi, reclami e costi operativi. "
    "Inoltre, la formazione degli operatori aiuta a mantenere standard costanti e a gestire correttamente eccezioni "
    "come merce danneggiata, quantità errate o urgenze di spedizione."
)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def request_json(url: str, payload: Optional[Dict[str, Any]] = None, timeout: int = 60) -> Tuple[int, Dict[str, Any]]:
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
        defects.append("Bridge attivo ma non collegato all'entrypoint qualità 5.15B.")
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
            defects.append(f"Bridge terminato durante avvio: stdout={stdout[-500:]}; stderr={stderr[-500:]}")
            return process, defects
    defects.append("Bridge non pronto su /health dopo 10 secondi.")
    return process, defects


def final_output(result: Dict[str, Any]) -> Dict[str, Any]:
    value = result.get("final_output") or result.get("raw_output") or result
    return value if isinstance(value, dict) else {"content": str(value or "")}


def visible_text_for(result: Dict[str, Any], generator: str) -> str:
    output = final_output(result)
    if generator == "summary":
        return str(output.get("content") or result.get("content") or "")
    chunks: List[str] = []
    for item in output.get("items") or result.get("items") or []:
        if isinstance(item, dict):
            chunks.append(json.dumps(item, ensure_ascii=False))
        else:
            chunks.append(str(item))
    return "\n".join(chunks)


def output_non_empty(result: Dict[str, Any], generator: str) -> bool:
    output = final_output(result)
    if generator == "summary":
        return bool(str(output.get("content") or "").strip())
    return isinstance(output.get("items"), list) and len(output.get("items") or []) > 0


def no_fallback(text: str) -> bool:
    low = text.lower()
    return "sicurezza informatica aziendale" not in low and "lorem ipsum" not in low and "testo di esempio" not in low


def quality_summary(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    content = str(final_output(result).get("content") or "")
    low = content.lower()
    defects: List[str] = []
    paragraphs = [p for p in content.split("\n\n") if p.strip()]
    if len(paragraphs) < 2:
        defects.append("riassunto_meno_di_2_paragrafi")
    if len(content.split()) < 90:
        defects.append("riassunto_troppo_corto")
    for term in ["ricezione", "registrazione", "preparazione", "spedizione", "tracciabilità"]:
        if term not in low:
            defects.append(f"riassunto_non_collega_{term}")
    if any(line.strip().startswith(("-", "•", "1.")) for line in content.splitlines()):
        defects.append("riassunto_sembra_lista")
    if "magazzino moderno richiede" in low and "spiega che" not in low:
        defects.append("incipit_meccanico")
    return not defects, defects


def quality_cards(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    items = final_output(result).get("items") or []
    defects: List[str] = []
    if len(items) < 4:
        defects.append("card_meno_di_4")
    for index, card in enumerate(items, start=1):
        if not str(card.get("titolo") or "").strip():
            defects.append(f"card_{index}_titolo_vuoto")
        message = str(card.get("messaggio_chiave") or "")
        if not message.strip() or "Il punto centrale" in message:
            defects.append(f"card_{index}_messaggio_generico")
        if "diffe\n" in message or message.endswith("diffe"):
            defects.append(f"card_{index}_testo_tagliato")
        visual = card.get("visual") or {}
        if not visual.get("svg"):
            defects.append(f"card_{index}_visual_rotto")
    return not defects, defects


def quality_study(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    items = final_output(result).get("items") or []
    defects: List[str] = []
    if len(items) < 4:
        defects.append("domande_studio_meno_di_4")
    blob = json.dumps(items, ensure_ascii=False).lower()
    if "magazzino stabilisce" in blob or "tema procedura" in blob:
        defects.append("domande_studio_frase_vietata")
    if not any(term in blob for term in ["magazzino", "merce", "ordini", "preparazione"]):
        defects.append("domande_studio_non_specifiche")
    for index, item in enumerate(items, start=1):
        if not str(item.get("domanda") or "").strip():
            defects.append(f"domanda_{index}_vuota")
        if not str(item.get("risposta_guida") or "").strip():
            defects.append(f"risposta_{index}_vuota")
    return not defects, defects


def quality_quiz(result: Dict[str, Any]) -> Tuple[bool, List[str]]:
    output = final_output(result)
    items = output.get("items") or []
    text = json.dumps(result, ensure_ascii=False)
    defects: List[str] = []
    if len(items) < 4:
        defects.append("quiz_meno_di_4_domande")
    if "is_correct" in text or "correct_option_id" in text or "risposta_corretta" in text:
        defects.append("answer_leak_payload")
    for index, item in enumerate(items, start=1):
        options = item.get("opzioni") or []
        if len(options) != 4:
            defects.append(f"quiz_{index}_opzioni_non_4")
            continue
        option_texts = [str(opt.get("testo") or "").strip().lower() for opt in options]
        if len(set(option_texts)) != 4:
            defects.append(f"quiz_{index}_opzioni_duplicate")
        if not item.get("answer_check", {}).get("answer_ok_hash"):
            defects.append(f"quiz_{index}_answer_check_mancante")
    return not defects, defects


QUALITY_CHECKS = {
    "summary": quality_summary,
    "cards": quality_cards,
    "study_questions": quality_study,
    "quiz": quality_quiz,
}


def call_generator(generator: str) -> Dict[str, Any]:
    status, payload = request_json(
        API + "/api/generate",
        {
            "kind": generator,
            "text": WAREHOUSE_TEXT,
            "strictNoFallback": True,
            "source": "phase5_15d_real_page_smoke",
        },
        timeout=60,
    )
    result = payload.get("result") if isinstance(payload, dict) else {}
    result = result if isinstance(result, dict) else {}
    text = visible_text_for(result, generator)
    quality_ok, quality_defects = QUALITY_CHECKS[generator](result)
    defects: List[str] = []
    expected = EXPECTED_QM[generator]

    if status != 200 or payload.get("ok") is not True:
        defects.append(f"http_not_ok:{status}:{payload.get('error')}")
    if result.get("entrypoint") != ENTRYPOINT:
        defects.append("entrypoint_bypass")
    if result.get("bridge_entrypoint_connected") is not True:
        defects.append("bridge_marker_missing")
    if not output_non_empty(result, generator):
        defects.append("output_vuoto")
    if result.get("input_verified") is not True:
        defects.append("input_non_verificato")
    if not result.get("qm_runtime_trace"):
        defects.append("qm_runtime_trace_mancante")
    if int(result.get("executed_qm_count") or 0) != expected:
        defects.append(f"conteggio_qm_errato:{result.get('executed_qm_count')}!={expected}")
    if result.get("all_motors_connected") is not True:
        defects.append("all_motors_connected_non_true")
    if result.get("connection_status") != "RUNTIME_TRACE_PROVED":
        defects.append("connection_status_non_runtime_trace")
    if not no_fallback(text):
        defects.append("fallback_demo_rilevato")
    defects.extend(quality_defects)

    return {
        "generator": generator,
        "label": LABELS[generator],
        "http_status": status,
        "output_visible": output_non_empty(result, generator),
        "expected_qm": expected,
        "practical_qm": int(result.get("executed_qm_count") or 0),
        "quality_minimum": "PASS" if quality_ok else "FAIL",
        "outcome": "PASS" if not defects else "FAIL",
        "status": result.get("status"),
        "approved": result.get("approved"),
        "visible_text_preview": text[:900],
        "defects": defects,
    }


def validate_render_initial() -> Dict[str, Any]:
    html = HTML_PAGE.read_text(encoding="utf-8")
    defects: List[str] = []
    render = html.split("function renderQuiz", 1)[-1].split("function renderError", 1)[0]
    if '.correct' in html or '"correct"' in html or "'correct'" in html:
        defects.append("classe_correct_presente")
    if "is_correct" in render or "correct_option_id" in render or "risposta_corretta" in render:
        defects.append("render_quiz_usa_campi_risposta_diretti")
    if "quiz-feedback" not in render:
        defects.append("feedback_post_click_mancante")
    return {
        "checked_file": str(HTML_PAGE.relative_to(ROOT)),
        "answer_leak_absent_in_initial_render": not defects,
        "defects": defects,
    }


def build_report(cases: List[Dict[str, Any]], bridge_defects: List[str], render_check: Dict[str, Any], bridge_started: bool) -> Dict[str, Any]:
    defects = list(bridge_defects)
    defects.extend(render_check["defects"])
    for case in cases:
        defects.extend(f"{case['generator']}: {item}" for item in case["defects"])

    table = [
        {
            "generator": case["label"],
            "output_visible": case["output_visible"],
            "expected_qm": case["expected_qm"],
            "practical_qm": case["practical_qm"],
            "quality_minimum": case["quality_minimum"],
            "outcome": case["outcome"],
        }
        for case in cases
    ]

    return {
        "phase": "5.15D",
        "status": "PASS" if not defects else "FAIL",
        "url_used": PAGE_URL,
        "startup_commands_used": [
            "cd /Users/alessandrobarbarossa/alex-ai-workspace",
            "backend/.venv/bin/python scripts/run_phase5_14_3_local_backend_bridge.py (fallback: python3 scripts/run_phase5_14_3_local_backend_bridge.py)",
            "python3 -m http.server 8000",
        ],
        "bridge_started_by_smoke": bridge_started,
        "text_used": WAREHOUSE_TEXT,
        "generator_table": table,
        "render_check": render_check,
        "defects_found": defects,
        "fixes_applied": [
            "Card: messaggio_chiave reso specifico rispetto al fatto invece del testo generico ripetuto.",
            "Quiz: distrattori resi specifici per topic e posizione della risposta corretta ruotata.",
            "Quiz/UI: payload frontend sanificato da is_correct/correct_option_id/risposta_corretta; verifica click via hash.",
            "Summary: micro-correzione dei connettivi e punteggiatura tra fatti.",
        ],
        "remaining_defects": [] if not defects else defects,
    }


def write_md(report: Dict[str, Any]) -> None:
    lines = [
        "# FASE 5.15D - Test pratico reale 4 generatori",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- URL usato: `{report['url_used']}`",
        "- Comandi di avvio:",
        "",
    ]
    lines.extend(f"  - `{cmd}`" for cmd in report["startup_commands_used"])
    lines.extend([
        "",
        "## Esito generatori",
        "",
        "| Generatore | Output visibile | QM attesi | QM pratici | Qualità minima | Esito |",
        "| --- | --- | ---: | ---: | --- | --- |",
    ])
    for row in report["generator_table"]:
        lines.append(
            f"| {row['generator']} | {'sì' if row['output_visible'] else 'no'} | {row['expected_qm']} | {row['practical_qm']} | {row['quality_minimum']} | {row['outcome']} |"
        )
    lines.extend(["", "## Testo usato", "", report["text_used"], "", "## Fix applicati", ""])
    lines.extend(f"- {item}" for item in report["fixes_applied"])
    lines.extend(["", "## Difetti trovati", ""])
    lines.extend(f"- {item}" for item in report["defects_found"] or ["nessuno"])
    lines.extend(["", "## Difetti rimasti", ""])
    lines.extend(f"- {item}" for item in report["remaining_defects"] or ["nessuno"])
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    process = None
    bridge_started = False
    cases: List[Dict[str, Any]] = []
    try:
        process, bridge_defects = start_bridge_if_needed()
        bridge_started = process is not None and not bridge_defects

        if not bridge_defects:
            for generator in ["summary", "cards", "study_questions", "quiz"]:
                try:
                    cases.append(call_generator(generator))
                except Exception as exc:
                    cases.append({
                        "generator": generator,
                        "label": LABELS[generator],
                        "http_status": 0,
                        "output_visible": False,
                        "expected_qm": EXPECTED_QM[generator],
                        "practical_qm": 0,
                        "quality_minimum": "FAIL",
                        "outcome": "FAIL",
                        "status": "ERROR",
                        "approved": False,
                        "visible_text_preview": "",
                        "defects": [f"request_exception:{type(exc).__name__}:{exc}", traceback.format_exc(limit=4)],
                    })

        render_check = validate_render_initial()
        trace = {
            "phase": "5.15D",
            "url_used": PAGE_URL,
            "entrypoint": ENTRYPOINT,
            "bridge_started_by_smoke": bridge_started,
            "cases": cases,
            "render_check": render_check,
        }
        write_json(TRACE_JSON, trace)

        report = build_report(cases, bridge_defects, render_check, bridge_started)
        write_json(REPORT_JSON, report)
        write_md(report)

        counts_map = {case["generator"]: case["practical_qm"] for case in cases}
        print(
            "FASE 5.15D smoke: "
            f"status={report['status']} "
            f"counts={counts_map}"
        )
        if report["defects_found"]:
            print("SMOKE DEFECTS:")
            for defect in report["defects_found"]:
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
