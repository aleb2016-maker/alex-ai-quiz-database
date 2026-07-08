#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15G.1 - diagnostica orchestratore globale documenti lunghi.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Sequence


ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
FIXTURES = REPORTS / "fixtures"
FIXTURE_PATH = FIXTURES / "phase5_15g1_long_manual_fixture.txt"
REPORT_JSON = REPORTS / "phase5_15g1_long_document_global_orchestrator_diagnostics_v1.json"
REPORT_MD = REPORTS / "phase5_15g1_long_document_global_orchestrator_diagnostics_v1.md"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

EXPECTED_QM = {
    "summary": 55,
    "cards": 60,
    "study_questions": 51,
    "quiz": 63,
}

BAD_CARD_TITLES = {
    "aspetto operativo del documento",
    "procedura operativa",
    "elemento",
    "punto operativo",
}

FORBIDDEN_CARD_PHRASES = [
    "La card evidenzia",
    "Questo passaggio collega",
    "Nel contesto",
    "la sezione",
]

BAD_KEYWORDS = {"contesto", "sezione", "descrive", "documento", "passaggio", "aspetto"}


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or "")))


def plain_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return " ".join(plain_text(item) for item in value)
    if isinstance(value, dict):
        preferred = [
            "content", "summary_text", "titolo", "title", "messaggio_chiave",
            "key_message", "spiegazione", "explanation", "domanda", "question",
            "risposta_guida", "answer", "testo", "text", "fatto_origine",
        ]
        chunks = [plain_text(value.get(key)) for key in preferred if key in value]
        if not chunks:
            chunks = [plain_text(v) for v in value.values()]
        return " ".join(chunk for chunk in chunks if chunk)
    return str(value)


def final_output(result: Dict[str, Any]) -> Dict[str, Any]:
    value = result.get("final_output") or result.get("raw_output") or result
    return value if isinstance(value, dict) else {"content": str(value or "")}


def text_key(text: str) -> str:
    words = re.findall(r"[a-zàèéìòù0-9]{4,}", str(text or "").lower())
    return " ".join(words[:10])


def duplicate_count(items: Sequence[Dict[str, Any]], field: str) -> int:
    seen = set()
    duplicates = 0
    for item in items:
        key = text_key(str(item.get(field) or ""))
        if not key:
            continue
        if key in seen:
            duplicates += 1
        seen.add(key)
    return duplicates


def find_real_manual() -> Path | None:
    candidates = []
    for base in [ROOT / "rag", ROOT / "documents", ROOT / "data", REPORTS / "fixtures"]:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in {".txt", ".md"}:
                continue
            name = path.name.lower()
            if "manuale" in name and "rag" in name:
                candidates.append(path)
    for path in candidates:
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        if "Manuale aziendale completo RAG V1" in text or word_count(text) > 6000:
            return path
    return None


def build_fixture_text() -> str:
    areas = [
        ("Governance accessi", "CTRL-ACC-101", "responsabile sicurezza", "account nominali", "revoca tempestiva"),
        ("Gestione fornitori", "CTRL-FOR-204", "ufficio acquisti", "qualifica fornitori", "rischio contrattuale"),
        ("Incident response", "CTRL-INC-310", "team operativo", "classificazione incidenti", "ritardo di escalation"),
        ("Qualita dati", "CTRL-DAT-118", "data owner", "riconciliazione mensile", "errore di registrazione"),
        ("Continuita operativa", "CTRL-BCP-402", "coordinatore continuita", "test di ripristino", "interruzione servizio"),
        ("Formazione operatori", "CTRL-FRM-221", "responsabile formazione", "verifica competenze", "uso non conforme"),
        ("Gestione modifiche", "CTRL-CHG-509", "change manager", "approvazione cambi", "modifica non autorizzata"),
        ("Audit interno", "CTRL-AUD-630", "auditor interno", "piano audit", "non conformita ripetuta"),
    ]
    paragraphs: List[str] = ["Manuale aziendale completo RAG V1"]
    for cycle in range(5):
        for index, (area, control, owner, procedure, risk) in enumerate(areas, start=1):
            section_no = cycle * len(areas) + index
            paragraphs.append(f"\n{section_no}. {area} - {control}")
            paragraphs.append(
                (
                    f"La macro-area {area} stabilisce come il {owner} deve governare {procedure} "
                    f"con evidenze tracciabili, criteri di priorita e controlli periodici. "
                    f"Il codice {control} richiede che ogni attivita sia registrata con data, owner, "
                    f"decisione presa e verifica dell'esito."
                )
            )
            paragraphs.append(
                (
                    f"La procedura operativa prevede apertura della richiesta, valutazione iniziale, "
                    f"approvazione, controllo indipendente e chiusura documentata. "
                    f"Quando emerge {risk}, il team deve assegnare una misura correttiva, definire "
                    f"una scadenza e verificare che il problema non si ripeta nel ciclo successivo."
                )
            )
            paragraphs.append(
                (
                    f"Le responsabilita sono distribuite tra {owner}, referente di processo e direzione. "
                    f"Il referente raccoglie le anomalie, il {owner} decide la priorita e la direzione "
                    f"approva le eccezioni che impattano budget, servizio o conformita normativa."
                )
            )
            paragraphs.append(
                (
                    f"La definizione chiave di {area.lower()} include confine operativo, criteri di ingresso, "
                    f"criteri di uscita e dati minimi da conservare. "
                    f"Le decisioni operative devono distinguere urgenza, impatto, probabilita e reversibilita, "
                    f"cosi il controllo {control} resta verificabile anche durante audit e riesame."
                )
            )
            paragraphs.append(
                (
                    f"Gli indicatori collegati a {area.lower()} misurano tempi di attraversamento, "
                    f"azioni correttive aperte, eccezioni approvate e reclami interni. "
                    f"Se gli indicatori peggiorano per due periodi consecutivi, il processo viene riesaminato "
                    f"con una retrospettiva documentata e con un piano di miglioramento assegnato."
                )
            )
    return "\n\n".join(paragraphs) + "\n"


def load_or_create_fixture() -> Dict[str, Any]:
    real = find_real_manual()
    if real:
        return {
            "path": str(real),
            "source": "real_manual_found",
            "text": real.read_text(encoding="utf-8"),
        }
    FIXTURES.mkdir(parents=True, exist_ok=True)
    if not FIXTURE_PATH.exists():
        FIXTURE_PATH.write_text(build_fixture_text(), encoding="utf-8")
    return {
        "path": str(FIXTURE_PATH),
        "source": "synthetic_long_fixture_created_for_diagnostics",
        "text": FIXTURE_PATH.read_text(encoding="utf-8"),
    }


def summary_metrics(result: Dict[str, Any], text: str) -> Dict[str, Any]:
    output = final_output(result)
    content = str(output.get("content") or output.get("summary_text") or "")
    report = output.get("quality_report") if isinstance(output.get("quality_report"), dict) else {}
    long_metrics = report.get("long_summary_metrics") if isinstance(report.get("long_summary_metrics"), dict) else {}
    structure = [
        "Executive summary",
        "Mappa del documento",
        "Macro-aree principali",
        "Processi e procedure",
        "Controlli, responsabilita e rischi",
        "Punti operativi da ricordare",
        "Conclusione",
    ]
    required_structure_count = 7
    if report.get("phase5_15g2_universal_summary_smoothing") is True:
        profile = report.get("document_profile") if isinstance(report.get("document_profile"), dict) else {}
        vocab = profile.get("vocabolario_sezioni") if isinstance(profile.get("vocabolario_sezioni"), dict) else {}
        structure = ["Sintesi tematica"] + [str(value) for value in vocab.values() if str(value).strip()]
        required_structure_count = min(7, len(structure))
    formulaic = sum(
        content.count(phrase)
        for phrase in ["Il documento spiega che", "La parte centrale approfondisce", "La parte conclusiva"]
    )
    genericity = [
        phrase for phrase in ["aspetto importante", "contenuto del documento", "passaggio operativo generico"]
        if phrase in content.lower()
    ]
    input_words = word_count(text)
    target_words = max(int(input_words * 0.10), 450)
    summary_words = word_count(content)
    return {
        "input_words": input_words,
        "target_words_10_percent": target_words,
        "summary_words": summary_words,
        "coverage_ratio_words": round(summary_words / max(1, input_words), 3),
        "target_10_percent_reached": summary_words >= target_words,
        "macro_blocks_count": report.get("macro_blocks_count"),
        "covered_blocks": long_metrics.get("covered_blocks", []),
        "missing_blocks": long_metrics.get("missing_blocks", []),
        "structure_sections_present": [item for item in structure if item in content],
        "formulaic_sentences": formulaic,
        "genericity_flags": genericity,
        "summary_long_quality_pass": bool(
            result.get("approved") is True
            and summary_words >= target_words
            and len([item for item in structure if item in content]) >= required_structure_count
            and not genericity
        ),
        "sample": content[:1200],
    }


def cards_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    output = final_output(result)
    items = output.get("items") if isinstance(output.get("items"), list) else []
    titles = [str(item.get("title") or item.get("titolo") or "") for item in items if isinstance(item, dict)]
    blob = json.dumps(items, ensure_ascii=False)
    generic_titles = [title for title in titles if title.lower() in BAD_CARD_TITLES or title.lower().startswith("aspetto")]
    bad_keywords = []
    for item in items:
        if not isinstance(item, dict):
            continue
        for kw in item.get("keywords") or item.get("micro_concetti") or []:
            if str(kw).lower() in BAD_KEYWORDS:
                bad_keywords.append(str(kw))
    covered = sorted({
        int(item.get("macro_area_index") or 0)
        for item in items if isinstance(item, dict) and item.get("macro_area_index")
    })
    return {
        "cards_count": len(items),
        "generic_titles_count": len(generic_titles),
        "duplicate_titles_count": duplicate_count(items, "title"),
        "near_duplicate_titles_count": duplicate_count(items, "titolo"),
        "forbidden_phrases_count": sum(blob.count(phrase) for phrase in FORBIDDEN_CARD_PHRASES),
        "bad_keywords_count": len(bad_keywords),
        "covered_macro_areas": covered,
        "card_quality_pass": bool(
            result.get("approved") is True
            and len(items) >= 8
            and not generic_titles
            and duplicate_count(items, "title") == 0
            and sum(blob.count(phrase) for phrase in FORBIDDEN_CARD_PHRASES) == 0
            and not bad_keywords
            and len(covered) >= 6
        ),
        "sample": items[:2],
    }


def quiz_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    output = final_output(result)
    items = output.get("items") if isinstance(output.get("items"), list) else []
    text = json.dumps(output, ensure_ascii=False)
    covered = sorted({
        int(item.get("source_macro_area_index") or 0)
        for item in items if isinstance(item, dict) and item.get("source_macro_area_index")
    })
    weak = 0
    for item in items:
        if not isinstance(item, dict):
            weak += 1
            continue
        options = item.get("opzioni") or item.get("options") or []
        option_texts = [str(opt.get("testo") or "") for opt in options if isinstance(opt, dict)]
        if len(option_texts) != 4 or len(set(option_texts)) != 4:
            weak += 1
        if any(len(opt.split()) < 6 for opt in option_texts):
            weak += 1
    leaks = sum(marker in text for marker in ["is_correct", "correct_option_id", "risposta_corretta"])
    return {
        "quiz_count": len(items),
        "covered_macro_areas": covered,
        "duplicate_questions_count": duplicate_count(items, "domanda"),
        "weak_distractors_count": weak,
        "leaked_answer_fields_count": leaks,
        "quiz_long_quality_pass": bool(
            result.get("approved") is True
            and len(items) >= 6
            and len(covered) >= 6
            and duplicate_count(items, "domanda") == 0
            and weak == 0
            and leaks == 0
        ),
        "sample": items[:2],
    }


def study_metrics(result: Dict[str, Any]) -> Dict[str, Any]:
    output = final_output(result)
    items = output.get("items") if isinstance(output.get("items"), list) else []
    covered = sorted({
        int(item.get("source_macro_area_index") or 0)
        for item in items if isinstance(item, dict) and item.get("source_macro_area_index")
    })
    formulaic = 0
    generic = 0
    weak = 0
    for item in items:
        if not isinstance(item, dict):
            weak += 1
            continue
        question = str(item.get("domanda") or item.get("question") or "")
        answer = str(item.get("risposta_guida") or item.get("answer") or "")
        low = question.lower()
        if "qual è un aspetto importante" in low or "punto operativo principale" in low:
            formulaic += 1
        if "documento" in low and len(question.split()) < 10:
            generic += 1
        if word_count(answer) < 18:
            weak += 1
    return {
        "study_count": len(items),
        "covered_macro_areas": covered,
        "formulaic_questions_count": formulaic,
        "generic_questions_count": generic,
        "weak_answer_guidance_count": weak,
        "study_long_quality_pass": bool(
            result.get("approved") is True
            and len(items) >= 6
            and len(covered) >= 6
            and formulaic == 0
            and generic == 0
            and weak == 0
        ),
        "sample": items[:2],
    }


def run_case(generator: str, text: str) -> Dict[str, Any]:
    from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator

    result = run_quality_checked_generator(generator, text)
    output = final_output(result)
    quality_report = output.get("quality_report") if isinstance(output.get("quality_report"), dict) else {}
    if generator == "summary":
        metrics = summary_metrics(result, text)
        passed = metrics["summary_long_quality_pass"]
    elif generator == "cards":
        metrics = cards_metrics(result)
        passed = metrics["card_quality_pass"]
    elif generator == "quiz":
        metrics = quiz_metrics(result)
        passed = metrics["quiz_long_quality_pass"]
    else:
        metrics = study_metrics(result)
        passed = metrics["study_long_quality_pass"]
    defects = []
    if result.get("approved") is not True:
        defects.append(f"approved_non_true:{result.get('approved')}")
    if result.get("status") != "APPROVED":
        defects.append(f"status_non_approved:{result.get('status')}")
    if int(result.get("executed_qm_count") or 0) != EXPECTED_QM[generator]:
        defects.append(f"qm_count:{result.get('executed_qm_count')}!={EXPECTED_QM[generator]}")
    if quality_report.get("phase5_15g1_long_document_orchestrator") is not True:
        defects.append("long_orchestrator_flag_missing")
    if not passed:
        defects.append(f"{generator}_long_quality_fail")
    return {
        "generator": generator,
        "approved": result.get("approved"),
        "status": result.get("status"),
        "executed_qm_count": int(result.get("executed_qm_count") or 0),
        "expected_qm_count": EXPECTED_QM[generator],
        "motor_name": output.get("motor_name"),
        "long_orchestrator_active": quality_report.get("phase5_15g1_long_document_orchestrator") is True,
        "metrics": metrics,
        "pass": not defects,
        "defects": defects,
    }


def write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_markdown(report: Dict[str, Any]) -> None:
    cases = {case["generator"]: case for case in report["cases"]}
    summary = cases["summary"]["metrics"]
    cards = cases["cards"]["metrics"]
    quiz = cases["quiz"]["metrics"]
    study = cases["study_questions"]["metrics"]
    lines = [
        "# FASE 5.15G.1 - Long document global orchestrator diagnostics",
        "",
        f"Status: **{report['status']}**",
        "",
        f"- Fixture: `{report['fixture']['path']}`",
        f"- Fonte fixture: `{report['fixture']['source']}`",
        f"- Input words: `{report['fixture']['input_words']}`",
        "",
        "## Summary lungo",
        "",
        f"- PASS: `{summary['summary_long_quality_pass']}`",
        f"- Target 10%: `{summary['target_words_10_percent']}` parole",
        f"- Summary words: `{summary['summary_words']}`",
        f"- Coverage ratio: `{summary['coverage_ratio_words']}`",
        f"- 10% raggiunto: `{summary['target_10_percent_reached']}`",
        f"- Covered blocks: `{summary['covered_blocks']}`",
        f"- Missing blocks: `{summary['missing_blocks']}`",
        "",
        "## Cards lunghe",
        "",
        f"- PASS: `{cards['card_quality_pass']}`",
        f"- Cards count: `{cards['cards_count']}`",
        f"- Generic titles: `{cards['generic_titles_count']}`",
        f"- Duplicate titles: `{cards['duplicate_titles_count']}`",
        f"- Forbidden phrases: `{cards['forbidden_phrases_count']}`",
        f"- Bad keywords: `{cards['bad_keywords_count']}`",
        f"- Covered macro areas: `{cards['covered_macro_areas']}`",
        "",
        "## Quiz lungo",
        "",
        f"- PASS: `{quiz['quiz_long_quality_pass']}`",
        f"- Quiz count: `{quiz['quiz_count']}`",
        f"- Covered macro areas: `{quiz['covered_macro_areas']}`",
        f"- Duplicate questions: `{quiz['duplicate_questions_count']}`",
        f"- Weak distractors: `{quiz['weak_distractors_count']}`",
        f"- Answer leak fields: `{quiz['leaked_answer_fields_count']}`",
        "",
        "## Study lungo",
        "",
        f"- PASS: `{study['study_long_quality_pass']}`",
        f"- Study count: `{study['study_count']}`",
        f"- Covered macro areas: `{study['covered_macro_areas']}`",
        f"- Formulaic questions: `{study['formulaic_questions_count']}`",
        f"- Generic questions: `{study['generic_questions_count']}`",
        f"- Weak answer guidance: `{study['weak_answer_guidance_count']}`",
        "",
        "## Casi",
        "",
        "| Generatore | Motore | QM | Approved | PASS | Difetti |",
        "| --- | --- | ---: | --- | --- | --- |",
    ]
    for case in report["cases"]:
        lines.append(
            f"| `{case['generator']}` | `{case['motor_name']}` | {case['executed_qm_count']}/{case['expected_qm_count']} | {case['approved']} | {case['pass']} | {', '.join(case['defects']) or 'nessuno'} |"
        )
    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    fixture = load_or_create_fixture()
    text = fixture["text"]
    cases = [run_case(generator, text) for generator in ["summary", "cards", "quiz", "study_questions"]]
    status = "PASS" if all(case["pass"] for case in cases) else "FAIL"
    report = {
        "phase": "5.15G.1",
        "status": status,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "fixture": {
            "path": fixture["path"],
            "source": fixture["source"],
            "input_words": word_count(text),
            "input_chars": len(text),
        },
        "cases": cases,
    }
    write_json(REPORT_JSON, report)
    write_markdown(report)
    print(f"FASE 5.15G.1 long diagnostics: status={status}")
    for case in cases:
        print(
            f"- {case['generator']}: pass={case['pass']} approved={case['approved']} "
            f"qm={case['executed_qm_count']}/{case['expected_qm_count']} motor={case['motor_name']}"
        )
    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
