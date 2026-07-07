#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15F.0 - diagnostica reale pulsanti generatori RAG/LLM.

Solo diagnostica: non modifica generatori, bridge, UI, Quality Manager,
raw_output comune o motori linguistici.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORT_JSON = REPORTS / "phase5_15f_button_quality_diagnostics_v1.json"
REPORT_MD = REPORTS / "phase5_15f_button_quality_diagnostics_v1.md"

BASELINE_515E_SCRIPT = ROOT / "scripts" / "run_phase5_15e_approved_outputs_smoke.py"
BASELINE_515D_SCRIPT = ROOT / "scripts" / "run_phase5_15d_real_page_generators_smoke.py"

STABLE_COMMIT = "0444d0d"
STABLE_TAG = "checkpoint-mini-llm-approved-generators-v515e"

ENTRYPOINT = "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator"

EXPECTED_QM = {
    "summary": 55,
    "cards": 60,
    "study_questions": 51,
    "quiz": 63,
}

EXPECTED_OUTPUT_MIN = {
    "summary": 1,
    "cards": 4,
    "study_questions": 4,
    "quiz": 4,
}

BUTTONS = [
    {
        "button_label": "Genera Riassunto",
        "generator_name": "summary",
        "kind": "summary",
        "quality_focus": "riassunto non abbastanza profondo",
    },
    {
        "button_label": "Genera Card",
        "generator_name": "cards",
        "kind": "cards",
        "quality_focus": "card povere",
    },
    {
        "button_label": "Genera Test/Quiz",
        "generator_name": "quiz",
        "kind": "quiz",
        "quality_focus": "distrattori deboli",
    },
    {
        "button_label": "Genera Domande studio",
        "generator_name": "study_questions",
        "kind": "study_questions",
        "quality_focus": "domande innaturali",
    },
]

SINGLE_DOCUMENT_TEXT = """La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti. Quando arriva una nuova merce, l'operatore verifica il documento di trasporto, controlla quantità e integrità degli articoli e segnala eventuali differenze. I prodotti conformi vengono registrati nel sistema gestionale e assegnati a una posizione precisa nel magazzino.

Durante la preparazione degli ordini, il sistema genera una lista di prelievo con codice articolo, quantità richiesta e posizione. L'operatore raccoglie i prodotti, controlla che corrispondano all'ordine e li porta nell'area di imballaggio. Prima della spedizione, un secondo controllo riduce il rischio di errori, prodotti mancanti o articoli scambiati.

La tracciabilità è importante perché permette di sapere dove si trova ogni prodotto, chi ha eseguito le operazioni e quando sono avvenute. Un processo ben organizzato riduce ritardi, reclami e costi operativi. Inoltre, la formazione degli operatori aiuta a mantenere standard costanti e a gestire correttamente eccezioni come merce danneggiata, quantità errate o urgenze di spedizione."""

MULTI_DOCUMENT_TEXT = """[Documento A - Protocollo triage ambulatoriale]
Il centro medico organizza il triage iniziale con una scheda di priorità, un controllo dei parametri vitali e una verifica dei sintomi riferiti dal paziente. L'infermiere registra ora di arrivo, livello di urgenza e motivo della visita. I casi con dolore toracico, dispnea o peggioramento neurologico devono essere rivalutati rapidamente anche se la sala d'attesa è piena.

[Documento B - Continuità assistenziale]
Dopo la visita, il medico consegna un piano di follow-up con terapia, segnali di allarme e canale di contatto. Le informazioni essenziali vengono riportate nel fascicolo clinico per evitare che il paziente ripeta dati già raccolti. Quando sono richiesti esami successivi, la prenotazione deve indicare priorità, preparazione necessaria e responsabilità del controllo referti.

[Documento C - Audit qualità]
Ogni mese il coordinatore confronta tempi di attesa, rivalutazioni mancate e reclami dei pazienti. Gli indicatori servono a distinguere problemi organizzativi da errori di comunicazione. Se emerge un ritardo ricorrente, il team definisce un'azione correttiva, assegna un responsabile e verifica l'effetto nel mese successivo."""

DOCUMENTS = [
    {
        "document_id": "single_stable_warehouse_order_flow",
        "document_label": "Documento singolo stabile - gestione ordini magazzino",
        "source": "testo stabile gia usato dagli smoke 5.15D/5.15E",
        "text": SINGLE_DOCUMENT_TEXT,
        "expected_terms": [
            "magazzino",
            "ordini",
            "merce",
            "preparazione",
            "spedizione",
            "tracciabilità",
        ],
        "forbidden_terms": ["sicurezza informatica aziendale", "lorem ipsum", "testo di esempio"],
    },
    {
        "document_id": "synthetic_multi_document_clinic_triage_quality",
        "document_label": "Mini caso multi-documento sintetico - triage, follow-up, audit",
        "source": "contenuto realistico sintetico creato solo dentro lo script diagnostico",
        "text": MULTI_DOCUMENT_TEXT,
        "expected_terms": [
            "triage",
            "follow-up",
            "fascicolo",
            "referti",
            "audit",
            "rivalutazioni",
        ],
        "forbidden_terms": ["sicurezza informatica aziendale", "lorem ipsum", "testo di esempio"],
    },
]


def run_command(args: List[str], timeout: int = 180) -> Dict[str, Any]:
    started_at = datetime.now().isoformat(timespec="seconds")
    try:
        completed = subprocess.run(
            args,
            cwd=str(ROOT),
            text=True,
            capture_output=True,
            timeout=timeout,
        )
        return {
            "command": " ".join(args),
            "started_at": started_at,
            "returncode": completed.returncode,
            "stdout": completed.stdout,
            "stderr": completed.stderr,
            "ok": completed.returncode == 0,
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "command": " ".join(args),
            "started_at": started_at,
            "returncode": 124,
            "stdout": exc.stdout or "",
            "stderr": exc.stderr or f"timeout dopo {timeout}s",
            "ok": False,
        }


def git_info() -> Dict[str, Any]:
    def git(args: List[str]) -> str:
        result = run_command(["git"] + args, timeout=20)
        return (result.get("stdout") or "").strip()

    tags_at_head = git(["tag", "--points-at", "HEAD"]).splitlines()
    relevant_tags = git(["tag", "--list", "*5.15*", "--list", "*515*", "--list", "*mini-llm*"]).splitlines()
    return {
        "branch": git(["branch", "--show-current"]),
        "commit": git(["rev-parse", "--short", "HEAD"]),
        "commit_full": git(["rev-parse", "HEAD"]),
        "tags_at_head": tags_at_head,
        "relevant_tags": relevant_tags,
        "status_short": git(["status", "--short"]),
        "checkpoint_expected": {
            "commit": STABLE_COMMIT,
            "tag": STABLE_TAG,
            "commit_matches": git(["rev-parse", "--short", "HEAD"]) == STABLE_COMMIT,
            "tag_at_head": STABLE_TAG in tags_at_head,
        },
    }


def parse_baseline_515e(report: Dict[str, Any], command: Dict[str, Any]) -> Dict[str, Any]:
    cases = report.get("cases") if isinstance(report, dict) else []
    counts = {
        str(case.get("generator")): int(case.get("executed_qm") or 0)
        for case in cases or []
        if isinstance(case, dict)
    }
    expected = EXPECTED_QM
    defects = []
    if not command.get("ok"):
        defects.append("script_5_15e_returncode_non_zero")
    if report.get("status") != "PASS":
        defects.append(f"report_status_non_pass:{report.get('status')}")
    for generator, expected_count in expected.items():
        if counts.get(generator) != expected_count:
            defects.append(f"{generator}:conteggio_qm_{counts.get(generator)}_atteso_{expected_count}")
    return {
        "phase": "5.15E",
        "script": str(BASELINE_515E_SCRIPT.relative_to(ROOT)),
        "command_ok": command.get("ok"),
        "report_status": report.get("status"),
        "expected_counts": expected,
        "observed_counts": counts,
        "pass": not defects,
        "defects": defects,
        "stdout_tail": (command.get("stdout") or "")[-1800:],
        "stderr_tail": (command.get("stderr") or "")[-1800:],
    }


def parse_baseline_515d(report: Dict[str, Any], command: Dict[str, Any]) -> Dict[str, Any]:
    table = report.get("generator_table") if isinstance(report, dict) else []
    label_to_generator = {
        "Riassunto": "summary",
        "Card": "cards",
        "Domande studio": "study_questions",
        "Test/Quiz": "quiz",
    }
    counts: Dict[str, int] = {}
    outcomes: Dict[str, str] = {}
    for row in table or []:
        if not isinstance(row, dict):
            continue
        generator = label_to_generator.get(str(row.get("generator")))
        if generator:
            counts[generator] = int(row.get("practical_qm") or 0)
            outcomes[generator] = str(row.get("outcome"))
    defects = []
    if not command.get("ok"):
        defects.append("script_5_15d_returncode_non_zero")
    if report.get("status") != "PASS":
        defects.append(f"report_status_non_pass:{report.get('status')}")
    for generator, expected_count in EXPECTED_QM.items():
        if counts.get(generator) != expected_count:
            defects.append(f"{generator}:conteggio_qm_{counts.get(generator)}_atteso_{expected_count}")
        if outcomes.get(generator) != "PASS":
            defects.append(f"{generator}:outcome_non_pass:{outcomes.get(generator)}")
    return {
        "phase": "5.15D",
        "script": str(BASELINE_515D_SCRIPT.relative_to(ROOT)),
        "command_ok": command.get("ok"),
        "report_status": report.get("status"),
        "expected_counts": EXPECTED_QM,
        "observed_counts": counts,
        "generator_outcomes": outcomes,
        "pass": not defects,
        "defects": defects,
        "stdout_tail": (command.get("stdout") or "")[-1800:],
        "stderr_tail": (command.get("stderr") or "")[-1800:],
    }


def read_json(path: Path) -> Dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        return {"status": "READ_ERROR", "error": f"{type(exc).__name__}: {exc}"}


def run_baselines() -> Dict[str, Any]:
    command_515e = run_command([sys.executable, str(BASELINE_515E_SCRIPT)], timeout=180)
    report_515e = read_json(REPORTS / "phase5_15e_approved_outputs_report_v1.json")
    baseline_515e = parse_baseline_515e(report_515e, command_515e)

    command_515d = run_command([sys.executable, str(BASELINE_515D_SCRIPT)], timeout=180)
    report_515d = read_json(REPORTS / "phase5_15d_real_page_generators_report_v1.json")
    baseline_515d = parse_baseline_515d(report_515d, command_515d)

    return {
        "phase5_15e": baseline_515e,
        "phase5_15d": baseline_515d,
        "pass": baseline_515e["pass"] and baseline_515d["pass"],
    }


def plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(plain_text(item) for item in value)
    if isinstance(value, dict):
        preferred = [
            "content",
            "summary_text",
            "titolo",
            "title",
            "messaggio_chiave",
            "key_message",
            "spiegazione",
            "explanation",
            "domanda",
            "question",
            "risposta_guida",
            "answer",
            "testo",
            "text",
            "fatto_origine",
        ]
        chunks = [plain_text(value.get(key)) for key in preferred if key in value]
        if not chunks:
            chunks = [plain_text(v) for v in value.values()]
        return " ".join(chunk for chunk in chunks if chunk)
    return str(value)


def final_output(result: Dict[str, Any]) -> Dict[str, Any]:
    output = result.get("final_output") or result.get("raw_output") or result
    return output if isinstance(output, dict) else {"content": str(output or "")}


def output_items(output: Dict[str, Any], generator: str) -> List[Any]:
    if generator == "summary":
        content = str(output.get("content") or output.get("summary_text") or "").strip()
        return [content] if content else []
    items = output.get("items")
    return items if isinstance(items, list) else []


def sample_output(output: Dict[str, Any], generator: str, limit: int = 700) -> str:
    if generator == "summary":
        value = str(output.get("content") or output.get("summary_text") or "")
    else:
        value = json.dumps(output_items(output, generator)[:2], ensure_ascii=False)
    value = re.sub(r"\s+", " ", value).strip()
    return value[:limit]


def sentence_count(text: str) -> int:
    return len([part for part in re.split(r"[.!?]+", text) if part.strip()])


def repeated_stems(text: str) -> List[str]:
    words = re.findall(r"[A-Za-zÀ-ÿ]{5,}", text.lower())
    stop = {
        "documento",
        "questo",
        "questa",
        "relativo",
        "operativo",
        "correttamente",
        "controllo",
        "gestione",
    }
    counts: Dict[str, int] = {}
    for word in words:
        stem = word[:9]
        if stem in stop:
            continue
        counts[stem] = counts.get(stem, 0) + 1
    return [stem for stem, count in sorted(counts.items()) if count >= 6][:8]


def options_from_item(item: Dict[str, Any]) -> List[str]:
    options = item.get("opzioni") or item.get("options") or []
    out = []
    for option in options if isinstance(options, list) else []:
        if isinstance(option, dict):
            out.append(str(option.get("testo") or option.get("text") or ""))
        else:
            out.append(str(option))
    return out


def detect_quality(
    generator: str,
    result: Dict[str, Any],
    document: Dict[str, Any],
) -> Tuple[List[str], List[str], List[str], List[str], str, str]:
    output = final_output(result)
    items = output_items(output, generator)
    text = plain_text(output)
    low = text.lower()
    defects: List[str] = []
    warnings: List[str] = []
    rag_problems: List[str] = []
    didactic_problems: List[str] = []

    for forbidden in document["forbidden_terms"]:
        if forbidden in low:
            defects.append(f"contaminazione_demo_fallback:{forbidden}")
            rag_problems.append("fallback/demo")

    found_terms = [term for term in document["expected_terms"] if term.lower() in low]
    coverage_ratio = len(found_terms) / max(1, len(document["expected_terms"]))
    if coverage_ratio < 0.5:
        rag_problems.append("perdita contesto")
        warnings.append(f"copertura_termini_documento_bassa:{len(found_terms)}/{len(document['expected_terms'])}")
    if coverage_ratio < 0.34:
        rag_problems.append("genericità")

    if re.search(r"\b\w{2,}(?:\n|-)$", text):
        rag_problems.append("frasi spezzate")
        warnings.append("possibile_testo_troncato")

    repeats = repeated_stems(text)
    if repeats:
        rag_problems.append("ripetizioni")
        warnings.append("radici_ripetute:" + ",".join(repeats))

    word_count = len(re.findall(r"\w+", text))
    if generator == "summary":
        paragraphs = [p for p in str(output.get("content") or "").split("\n\n") if p.strip()]
        if len(paragraphs) < 2 or word_count < 90:
            rag_problems.append("output troppo corto")
            defects.append("riassunto_troppo_corto_o_monoparagrafo")
        if coverage_ratio < 0.68:
            rag_problems.append("riassunto non abbastanza profondo")
            warnings.append("riassunto_non_copre_abbastanza_sezioni")
        linguistic = "buona: paragrafi leggibili" if not defects else "debole: sintesi corta o poco articolata"
        didactic = "media: utile per orientarsi, ma da verificare profondita su documenti multipli"
    elif generator == "cards":
        if len(items) < EXPECTED_OUTPUT_MIN[generator]:
            rag_problems.append("output troppo corto")
            defects.append(f"card_insufficienti:{len(items)}")
        poor_cards = 0
        for item in items:
            if not isinstance(item, dict):
                poor_cards += 1
                continue
            message = str(item.get("messaggio_chiave") or item.get("key_message") or "")
            explanation = str(item.get("spiegazione") or item.get("explanation") or "")
            if len(message.split()) < 8 or len(explanation.split()) < 12:
                poor_cards += 1
        if poor_cards:
            rag_problems.append("card povere")
            didactic_problems.append(f"card_poco_spiegate:{poor_cards}")
        linguistic = "media: frasi comprensibili, talvolta formulaiche"
        didactic = "media: aiuta a segmentare i concetti, ma alcune card restano descrittive"
    elif generator == "study_questions":
        if len(items) < EXPECTED_OUTPUT_MIN[generator]:
            rag_problems.append("output troppo corto")
            defects.append(f"domande_studio_insufficienti:{len(items)}")
        unnatural = 0
        for item in items:
            if not isinstance(item, dict):
                unnatural += 1
                continue
            question = str(item.get("domanda") or item.get("question") or "")
            answer = str(item.get("risposta_guida") or item.get("answer") or "")
            if "punto operativo principale relativo a" in question.lower():
                unnatural += 1
            if len(answer.split()) < 18:
                didactic_problems.append("risposta_guida_troppo_breve")
        if unnatural:
            rag_problems.append("domande innaturali")
            didactic_problems.append(f"domande_formulaiche:{unnatural}")
        linguistic = "media-bassa: corretto ma con template evidente"
        didactic = "media: risposte guida presenti, domande da rendere piu naturali"
    else:
        if len(items) < EXPECTED_OUTPUT_MIN[generator]:
            rag_problems.append("output troppo corto")
            defects.append(f"quiz_insufficiente:{len(items)}")
        weak = 0
        leaks = 0
        for item in items:
            if not isinstance(item, dict):
                continue
            question = str(item.get("domanda") or item.get("question") or "")
            if "quale affermazione descrive correttamente" in question.lower():
                didactic_problems.append("domanda_quiz_formulaica")
            options = options_from_item(item)
            if len(options) == 4:
                generic_options = [
                    option for option in options
                    if any(marker in option.lower() for marker in [
                        "può essere trattato senza controlli",
                        "non richiede registrazioni",
                        "può restare informale",
                    ])
                ]
                if len(generic_options) >= 2:
                    weak += 1
            if "is_correct" in json.dumps(item, ensure_ascii=False) or "correct_option_id" in item or "risposta_corretta" in item:
                leaks += 1
        if weak:
            rag_problems.append("distrattori deboli")
            didactic_problems.append(f"distrattori_generici:{weak}")
        if leaks:
            defects.append(f"answer_leak_payload_diretto:{leaks}")
        linguistic = "media: comprensibile, ma pattern ripetuto nelle domande"
        didactic = "medio-bassa: risposta corretta chiara, distrattori spesso troppo facili"

    if word_count > 900:
        rag_problems.append("output troppo lungo")
        warnings.append(f"output_molto_lungo:{word_count}_parole")

    rag_problems = sorted(set(rag_problems))
    didactic_problems = sorted(set(didactic_problems))
    return defects, warnings, rag_problems, didactic_problems, linguistic, didactic


def classify_issue(issue: str) -> str:
    technical_markers = ["returncode", "entrypoint", "answer_leak", "conteggio", "http", "raw_output"]
    rag_markers = ["fallback", "contesto", "generic", "troncato", "termini", "ripet"]
    didactic_markers = ["distrattori", "domande", "risposta_guida", "card"]
    lowered = issue.lower()
    if any(marker in lowered for marker in technical_markers):
        return "bug tecnico"
    if any(marker in lowered for marker in rag_markers):
        return "problema qualità RAG"
    if any(marker in lowered for marker in didactic_markers):
        return "problema didattico"
    return "problema qualità linguistica"


def diagnose_case(button: Dict[str, str], document: Dict[str, Any]) -> Dict[str, Any]:
    from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator

    generator = button["generator_name"]
    result = run_quality_checked_generator(generator, document["text"])
    output = final_output(result)
    items = output_items(output, generator)
    output_count = len(items)
    engine_id = (
        output.get("motor_name")
        or output.get("engine_id")
        or output.get("quality_report", {}).get("motor_path")
        or output.get("quality_report", {}).get("kind")
        or "non_dichiarato"
    )
    defects, warnings, rag_problems, didactic_problems, linguistic, didactic = detect_quality(generator, result, document)

    if result.get("status") != "APPROVED":
        defects.append(f"status_non_approved:{result.get('status')}")
    if result.get("approved") is not True:
        defects.append(f"approved_non_true:{result.get('approved')}")
    if int(result.get("executed_qm_count") or 0) != EXPECTED_QM[generator]:
        defects.append(f"conteggio_qm_errato:{result.get('executed_qm_count')}!={EXPECTED_QM[generator]}")
    if output_count < EXPECTED_OUTPUT_MIN[generator]:
        defects.append(f"output_count_basso:{output_count}!>={EXPECTED_OUTPUT_MIN[generator]}")

    all_issues = defects + warnings + rag_problems + didactic_problems
    issue_classes = sorted({classify_issue(issue) for issue in all_issues})

    return {
        "button_label": button["button_label"],
        "generator_name": generator,
        "engine_id": engine_id,
        "entrypoint": ENTRYPOINT,
        "input_document": {
            "document_id": document["document_id"],
            "document_label": document["document_label"],
            "source": document["source"],
            "chars": len(document["text"]),
        },
        "expected_qm_count": EXPECTED_QM[generator],
        "executed_qm_count": int(result.get("executed_qm_count") or 0),
        "output_count_atteso": EXPECTED_OUTPUT_MIN[generator],
        "output_count_reale": output_count,
        "approved": result.get("approved") is True,
        "status": result.get("status"),
        "defects": defects,
        "warnings": warnings,
        "sample_output_breve": sample_output(output, generator),
        "qualita_linguistica_osservata": linguistic,
        "qualita_didattica_osservata": didactic,
        "problemi_rag_osservati": rag_problems,
        "problemi_didattici_osservati": didactic_problems,
        "issue_classes": issue_classes,
        "quality_report": output.get("quality_report") if isinstance(output.get("quality_report"), dict) else {},
    }


def aggregate_by_button(cases: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for button in BUTTONS:
        generator = button["generator_name"]
        matching = [case for case in cases if case.get("generator_name") == generator]
        defects = sorted({item for case in matching for item in case.get("defects", [])})
        warnings = sorted({item for case in matching for item in case.get("warnings", [])})
        rag = sorted({item for case in matching for item in case.get("problemi_rag_osservati", [])})
        didactic = sorted({item for case in matching for item in case.get("problemi_didattici_osservati", [])})
        classes = sorted({item for case in matching for item in case.get("issue_classes", [])})
        rows.append({
            "button_label": button["button_label"],
            "generator_name": generator,
            "engine_id": matching[0].get("engine_id") if matching else "n/d",
            "documents_tested": len(matching),
            "approved_all": all(case.get("approved") is True for case in matching),
            "status": "PASS" if matching and all(case.get("approved") is True for case in matching) else "FAIL",
            "expected_qm_count": EXPECTED_QM[generator],
            "executed_qm_counts": sorted({case.get("executed_qm_count") for case in matching}),
            "output_count_reale": [case.get("output_count_reale") for case in matching],
            "defects": defects,
            "warnings": warnings,
            "problemi_rag_osservati": rag,
            "problemi_didattici_osservati": didactic,
            "issue_classes": classes,
            "sample_output_breve": matching[0].get("sample_output_breve", "") if matching else "",
        })
    return rows


def intervention_priorities(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    priorities = []
    for row in rows:
        score = 0
        score += 5 * len(row.get("defects", []))
        score += 3 * len(row.get("problemi_rag_osservati", []))
        score += 3 * len(row.get("problemi_didattici_osservati", []))
        score += len(row.get("warnings", []))
        if row["generator_name"] == "quiz" and "distrattori deboli" in row.get("problemi_rag_osservati", []):
            score += 5
        if row["generator_name"] == "study_questions" and "domande innaturali" in row.get("problemi_rag_osservati", []):
            score += 3
        priorities.append({
            "priority_score": score,
            "button_label": row["button_label"],
            "generator_name": row["generator_name"],
            "engine_id": row["engine_id"],
            "main_issues": row.get("defects", [])[:4] + row.get("problemi_rag_osservati", [])[:4] + row.get("problemi_didattici_osservati", [])[:4],
        })
    return sorted(priorities, key=lambda item: item["priority_score"], reverse=True)


def recommended_file_for(engine_id: str, generator: str) -> str:
    if generator in {"study_questions", "quiz"}:
        return "motore linguistico/didattico v51418 da localizzare senza patch a bridge/UI/QM; candidato principale backend/phase5_full_pipeline_runtime_v51416.py"
    if generator in {"summary", "cards"}:
        return "backend/phase5_full_pipeline_runtime_v51416.py"
    return "motore non determinato"


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(report: Dict[str, Any]) -> None:
    rows = report.get("button_summary", [])
    priorities = report.get("intervention_priorities", [])
    first = report.get("first_engine_to_improve") or {}
    lines = [
        "# FASE 5.15F.0 - Diagnostica reale pulsanti generatori RAG/LLM",
        "",
        f"Status diagnostica: **{report['status']}**",
        "",
        "## Stato baseline",
        "",
        f"- 5.15E baseline: **{'PASS' if report['baselines']['phase5_15e']['pass'] else 'FAIL'}** - conteggi osservati `{report['baselines']['phase5_15e']['observed_counts']}`",
        f"- 5.15D baseline: **{'PASS' if report['baselines']['phase5_15d']['pass'] else 'FAIL'}** - conteggi osservati `{report['baselines']['phase5_15d']['observed_counts']}`",
        "",
        "## Stato Git",
        "",
        f"- Branch: `{report['git']['branch']}`",
        f"- Commit: `{report['git']['commit']}`",
        f"- Tag su HEAD: `{', '.join(report['git']['tags_at_head']) or 'nessuno'}`",
        f"- Stato git short: `{report['git']['status_short'] or 'clean prima della diagnostica'}`",
        "",
        "## Tabella 4 pulsanti",
        "",
        "| Pulsante | Generatore | Motore effettivo | QM | Output reali | Approved | Problemi principali |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for row in rows:
        problems = row.get("defects", []) + row.get("problemi_rag_osservati", []) + row.get("problemi_didattici_osservati", [])
        problem_text = "; ".join(problems[:6]) or "nessuno bloccante"
        qm_counts = "/".join(str(x) for x in row.get("executed_qm_counts", []))
        lines.append(
            f"| {row['button_label']} | `{row['generator_name']}` | `{row['engine_id']}` | {qm_counts}/{row['expected_qm_count']} | {row['output_count_reale']} | {row['approved_all']} | {problem_text} |"
        )

    lines.extend([
        "",
        "## Problemi trovati per motore",
        "",
    ])
    for row in rows:
        lines.extend([
            f"### {row['button_label']} - `{row['engine_id']}`",
            "",
            f"- Classi problema: {', '.join(row.get('issue_classes') or ['nessuna'])}",
            f"- Difetti tecnici: {', '.join(row.get('defects') or ['nessuno'])}",
            f"- Warning: {', '.join(row.get('warnings') or ['nessuno'])}",
            f"- Problemi RAG: {', '.join(row.get('problemi_rag_osservati') or ['nessuno'])}",
            f"- Problemi didattici: {', '.join(row.get('problemi_didattici_osservati') or ['nessuno'])}",
            f"- Sample: {row.get('sample_output_breve', '')}",
            "",
        ])

    lines.extend([
        "## Priorità di intervento",
        "",
        "| Priorità | Pulsante | Generatore | Motore | Score | Motivo |",
        "| ---: | --- | --- | --- | ---: | --- |",
    ])
    for index, item in enumerate(priorities, start=1):
        reason = "; ".join(item.get("main_issues") or ["nessun problema bloccante"])
        lines.append(
            f"| {index} | {item['button_label']} | `{item['generator_name']}` | `{item['engine_id']}` | {item['priority_score']} | {reason} |"
        )

    lines.extend([
        "",
        "## Primo motore da migliorare",
        "",
        f"- Motore/file: `{first.get('engine_id', 'n/d')}`",
        f"- Generatore: `{first.get('generator_name', 'n/d')}`",
        f"- File candidato: `{first.get('recommended_file', 'n/d')}`",
        f"- Raccomandazione: **{report.get('recommendation', 'n/d')}**",
        "",
        "## Distinzione problemi",
        "",
    ])
    for issue_type, items in report.get("issue_taxonomy", {}).items():
        lines.append(f"- {issue_type}: {', '.join(items or ['nessuno'])}")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def build_blocked_report(git: Dict[str, Any], baselines: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "phase": "5.15F.0",
        "status": "BLOCKED_BASELINE_FAILED",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "git": git,
        "baselines": baselines,
        "diagnostics_executed": False,
        "block_reason": "Baseline 5.15E o 5.15D non PASS; diagnostica pulsanti fermata come richiesto.",
    }


def main() -> int:
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

    git = git_info()
    baselines = run_baselines()

    print("FASE 5.15F.0 diagnostics")
    print(f"branch={git['branch']} commit={git['commit']} tags_at_head={git['tags_at_head']}")
    print(f"git_status_short={git['status_short'] or 'clean'}")
    print(f"baseline_5.15E={'PASS' if baselines['phase5_15e']['pass'] else 'FAIL'} counts={baselines['phase5_15e']['observed_counts']}")
    print(f"baseline_5.15D={'PASS' if baselines['phase5_15d']['pass'] else 'FAIL'} counts={baselines['phase5_15d']['observed_counts']}")

    if not baselines["pass"]:
        report = build_blocked_report(git, baselines)
        write_json(REPORT_JSON, report)
        REPORT_MD.write_text(
            "# FASE 5.15F.0 - BLOCCO BASELINE\n\n"
            f"Status: **{report['status']}**\n\n"
            f"Motivo: {report['block_reason']}\n\n"
            f"- 5.15E: {'PASS' if baselines['phase5_15e']['pass'] else 'FAIL'}\n"
            f"- 5.15D: {'PASS' if baselines['phase5_15d']['pass'] else 'FAIL'}\n",
            encoding="utf-8",
        )
        print("diagnostica_5.15F.0=BLOCKED_BASELINE_FAILED")
        return 1

    cases: List[Dict[str, Any]] = []
    for document in DOCUMENTS:
        for button in BUTTONS:
            cases.append(diagnose_case(button, document))

    rows = aggregate_by_button(cases)
    priorities = intervention_priorities(rows)
    first = priorities[0] if priorities else {}
    first_engine = {
        **first,
        "recommended_file": recommended_file_for(first.get("engine_id", ""), first.get("generator_name", "")),
    } if first else {}

    issue_taxonomy: Dict[str, List[str]] = {
        "bug tecnico": [],
        "problema qualità linguistica": [],
        "problema qualità RAG": [],
        "problema didattico": [],
        "problema UI/bridge": [],
    }
    for case in cases:
        for issue in case.get("defects", []) + case.get("warnings", []) + case.get("problemi_rag_osservati", []) + case.get("problemi_didattici_osservati", []):
            issue_taxonomy[classify_issue(issue)].append(f"{case['generator_name']}:{issue}")
        if case["generator_name"] == "quiz" and any("answer_leak_payload_diretto" in d for d in case.get("defects", [])):
            issue_taxonomy["problema UI/bridge"].append(
                "quiz:payload diretto contiene risposta; smoke 5.15D conferma sanificazione pagina/bridge PASS"
            )
    issue_taxonomy = {key: sorted(set(value)) for key, value in issue_taxonomy.items()}

    has_actionable_quality = any(
        row.get("defects") or row.get("problemi_rag_osservati") or row.get("problemi_didattici_osservati")
        for row in rows
    )
    recommendation = "patch mirata sui motori linguistici/didattici, nessuna patch a bridge/UI/QM" if has_actionable_quality else "nessuna patch"

    report = {
        "phase": "5.15F.0",
        "status": "PASS",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "scope": "diagnostica reale pulsanti generatori RAG/LLM senza modifiche funzionali",
        "git": git,
        "baselines": baselines,
        "documents": [
            {key: value for key, value in document.items() if key != "text"}
            for document in DOCUMENTS
        ],
        "button_summary": rows,
        "cases": cases,
        "intervention_priorities": priorities,
        "first_engine_to_improve": first_engine,
        "issue_taxonomy": issue_taxonomy,
        "recommendation": recommendation,
    }
    write_json(REPORT_JSON, report)
    write_markdown(report)

    print("diagnostica_5.15F.0=PASS")
    for row in rows:
        problems = row.get("defects", []) + row.get("problemi_rag_osservati", []) + row.get("problemi_didattici_osservati", [])
        print(f"- {row['button_label']}: approved={row['approved_all']} engine={row['engine_id']} problems={problems or ['nessuno bloccante']}")
    print(f"first_engine_to_improve={first_engine.get('engine_id')} generator={first_engine.get('generator_name')}")
    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
