from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.legacy_quality_motor_registry_v1 import apply_legacy_quality_motors_v1


REPORT_JSON = ROOT / "reports" / "phase5_8_quality_delta_ready_safe_motors_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_8_quality_delta_ready_safe_motors_v1.md"


AREAS = {
    "summary": ["riassunto_qualita"],
    "cards": ["card_concettuali"],
    "study": ["domande_studio"],
    "quiz": ["test_quiz", "quiz_draft", "quiz"],
}


BAD_PATTERNS = {
    "double_words": r"\b(\w+)\s+\1\b",
    "space_before_punctuation": r"\s+[,.!?;:]",
    "wrong_accent_perche": r"\bperchè\b",
    "wrong_qual_e": r"\bqual e\b",
    "double_non": r"\bnon\s+non\b",
    "mechanical_study_phrase": r"quale regola o informazione emerge da",
    "mechanical_quiz_phrase": r"quale affermazione è supportata dal documento",
    "draft_words": r"\bbozza\b|\bdraft\b|macro-grezzo|grezzo",
    "suspicious_yes_prefix": r"\bsì,\s+",
}


POSITIVE_PATTERNS = {
    "has_explanatory_connectors": r"\bperché\b|\binoltre\b|\bquesto\b|\bin pratica\b|\bsul piano operativo\b",
    "has_specific_security_terms": r"\baccessi\b|\bcredenziali\b|\baccount\b|\bpermessi\b|\bsistemi interni\b",
}


def walk_strings(value: Any) -> list[str]:
    out: list[str] = []

    if isinstance(value, str):
        out.append(value)

    elif isinstance(value, dict):
        for child in value.values():
            out.extend(walk_strings(child))

    elif isinstance(value, list):
        for child in value:
            out.extend(walk_strings(child))

    return out


def get_area(payload: dict[str, Any], area: str) -> Any:
    for key in AREAS[area]:
        if key in payload:
            return payload[key]

    return None


def count_bad_patterns(value: Any) -> dict[str, int]:
    text = "\n".join(walk_strings(value)).lower()

    return {
        name: len(re.findall(pattern, text, flags=re.IGNORECASE))
        for name, pattern in BAD_PATTERNS.items()
    }


def count_positive_patterns(value: Any) -> dict[str, int]:
    text = "\n".join(walk_strings(value)).lower()

    return {
        name: len(re.findall(pattern, text, flags=re.IGNORECASE))
        for name, pattern in POSITIVE_PATTERNS.items()
    }


def total_count(counter: dict[str, int]) -> int:
    return sum(counter.values())


def text_length(value: Any) -> int:
    return len("\n".join(walk_strings(value)).strip())


def distinct_text_ratio(value: Any) -> float:
    strings = [
        s.strip().lower()
        for s in walk_strings(value)
        if s.strip()
    ]

    if not strings:
        return 1.0

    return round(len(set(strings)) / len(strings), 3)


def quiz_distractor_true_fact_risk(quiz: Any) -> int:
    if not isinstance(quiz, list):
        return 0

    risk = 0

    for question in quiz:
        if not isinstance(question, dict):
            continue

        options = question.get("opzioni") or question.get("options") or []
        source_facts = question.get("source_facts") or []

        if not isinstance(options, list) or not isinstance(source_facts, list):
            continue

        source_facts_norm = {
            str(fact).strip().lower()
            for fact in source_facts
            if str(fact).strip()
        }

        for option in options:
            if not isinstance(option, dict):
                continue

            is_correct = option.get("is_correct") is True
            text = str(option.get("testo") or option.get("text") or "").strip().lower()

            if not is_correct and text in source_facts_norm:
                risk += 1

    return risk


def area_metrics(payload: dict[str, Any], area: str) -> dict[str, Any]:
    value = get_area(payload, area)

    bad = count_bad_patterns(value)
    positive = count_positive_patterns(value)

    metrics = {
        "text_length": text_length(value),
        "distinct_text_ratio": distinct_text_ratio(value),
        "bad_patterns": bad,
        "bad_patterns_total": total_count(bad),
        "positive_patterns": positive,
        "positive_patterns_total": total_count(positive),
    }

    if area == "quiz":
        metrics["quiz_distractor_true_fact_risk"] = quiz_distractor_true_fact_risk(value)

    return metrics


def compare_metrics(before: dict[str, Any], after: dict[str, Any], area: str) -> dict[str, Any]:
    bad_before = before["bad_patterns_total"]
    bad_after = after["bad_patterns_total"]

    pos_before = before["positive_patterns_total"]
    pos_after = after["positive_patterns_total"]

    result = {
        "area": area,
        "bad_patterns_before": bad_before,
        "bad_patterns_after": bad_after,
        "bad_patterns_delta": bad_after - bad_before,
        "positive_patterns_before": pos_before,
        "positive_patterns_after": pos_after,
        "positive_patterns_delta": pos_after - pos_before,
        "distinct_text_ratio_before": before["distinct_text_ratio"],
        "distinct_text_ratio_after": after["distinct_text_ratio"],
        "text_length_before": before["text_length"],
        "text_length_after": after["text_length"],
        "improved": False,
        "worsened": False,
        "neutral": False,
        "notes": [],
    }

    if bad_after < bad_before:
        result["improved"] = True
        result["notes"].append("Riduce pattern testuali problematici.")

    if pos_after > pos_before:
        result["improved"] = True
        result["notes"].append("Aumenta segnali testuali positivi/naturali.")

    if bad_after > bad_before:
        result["worsened"] = True
        result["notes"].append("Aumenta pattern problematici.")

    if area == "quiz":
        q_before = before.get("quiz_distractor_true_fact_risk", 0)
        q_after = after.get("quiz_distractor_true_fact_risk", 0)

        result["quiz_distractor_true_fact_risk_before"] = q_before
        result["quiz_distractor_true_fact_risk_after"] = q_after
        result["quiz_distractor_true_fact_risk_delta"] = q_after - q_before

        if q_after < q_before:
            result["improved"] = True
            result["notes"].append("Riduce rischio distrattori veri.")

        if q_after > q_before:
            result["worsened"] = True
            result["notes"].append("Aumenta rischio distrattori veri.")

    if not result["improved"] and not result["worsened"]:
        result["neutral"] = True
        result["notes"].append("Nessun miglioramento misurabile su queste metriche.")

    return result


def build_dirty_payload() -> dict[str, Any]:
    return {
        "document_id": "phase5_8_quality_delta_ready_safe_motors_v1",
        "phase_name": "QUALITY_STUDY_QUIZ",
        "approved": True,
        "status": "APPROVED",
        "riassunto_qualita": {
            "titolo": "Bozza riassunto macro-grezzo",
            "paragrafi": [
                "Il controllo degli accessi limita l'utilizzo dei sistemi interni  .",
                "Le credenziali non non devono essere condivise tra più operatori.",
                "La revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati.",
            ],
            "testo_completo": (
                "Il controllo degli accessi limita l'utilizzo dei sistemi interni  . "
                "Le credenziali non non devono essere condivise tra più operatori. "
                "La revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati."
            ),
            "fonte_pagine": [1, 2],
        },
        "card_concettuali": [
            {
                "card_id": "phase5_card_001",
                "titolo": "Controllo accessi",
                "contenuto_esplicativo": "Il controllo degli accessi limita l'utilizzo dei sistemi interni  .",
                "micro_concetti": ["controllo accessi", "account utente"],
                "fonte_pagine": [1, 2],
            },
            {
                "card_id": "phase5_card_002",
                "titolo": "Protezione credenziali",
                "contenuto_esplicativo": "Le credenziali non non devono essere condivise tra più operatori.",
                "micro_concetti": ["credenziali", "operatori"],
                "fonte_pagine": [1, 2],
            },
        ],
        "domande_studio": [
            {
                "question_id": "study_question_001",
                "domanda": "Quale regola o informazione emerge da: Il controllo degli accessi limita l'utilizzo dei...?",
                "risposta_guida": "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                "fonte_pagine": [1, 2],
            },
            {
                "question_id": "study_question_002",
                "domanda": "Qual e il rischio delle credenziali condivise?",
                "risposta_guida": "Le credenziali non non devono essere condivise tra più operatori.",
                "fonte_pagine": [1, 2],
            },
        ],
        "test_quiz": [
            {
                "question_id": "phase5_quiz_question_001",
                "domanda": "Quale affermazione è supportata dal documento?",
                "opzioni": [
                    {
                        "option_id": "A",
                        "testo": "Le credenziali non devono essere condivise tra più operatori.",
                        "is_correct": True,
                    },
                    {
                        "option_id": "B",
                        "testo": "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                        "is_correct": False,
                    },
                    {
                        "option_id": "C",
                        "testo": "Ogni account deve essere associato a una persona identificabile.",
                        "is_correct": False,
                    },
                    {
                        "option_id": "D",
                        "testo": "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
                        "is_correct": False,
                    },
                ],
                "correct_option_id": "A",
                "spiegazione": "Le credenziali non non devono essere condivise tra più operatori.",
                "source_facts": [
                    "Le credenziali non devono essere condivise tra più operatori.",
                    "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                    "Ogni account deve essere associato a una persona identificabile.",
                    "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
                ],
            }
        ],
        "warnings": [],
        "errors": [],
    }


def main() -> int:
    before_payload = build_dirty_payload()
    after_payload = apply_legacy_quality_motors_v1(
        copy.deepcopy(before_payload),
        context="phase5_8_quality_delta_ready_safe_motors",
    )

    area_reports = []

    for area in ["summary", "cards", "study", "quiz"]:
        before = area_metrics(before_payload, area)
        after = area_metrics(after_payload, area)
        area_reports.append(compare_metrics(before, after, area))

    improved_areas = [item for item in area_reports if item["improved"]]
    worsened_areas = [item for item in area_reports if item["worsened"]]
    neutral_areas = [item for item in area_reports if item["neutral"]]

    registry_meta = after_payload.get("_legacy_quality_motor_registry_v1", {})

    status = "PASS"

    if worsened_areas:
        status = "FAIL_WORSENED"
    elif not improved_areas:
        status = "PASS_NEUTRAL_NO_MEASURABLE_IMPROVEMENT"
    else:
        status = "PASS_IMPROVES"

    report = {
        "report_name": "phase5_8_quality_delta_ready_safe_motors_v1",
        "status": status,
        "improved_areas_count": len(improved_areas),
        "neutral_areas_count": len(neutral_areas),
        "worsened_areas_count": len(worsened_areas),
        "areas": area_reports,
        "registry_meta": registry_meta,
        "notes": [
            "Misura diagnostica qualità: confronta output prima/dopo registry.",
            "Non modifica il registry.",
            "PASS_IMPROVES significa che almeno una sezione migliora senza peggioramenti.",
            "PASS_NEUTRAL_NO_MEASURABLE_IMPROVEMENT significa che i motori non peggiorano ma queste metriche non vedono miglioramenti.",
            "FAIL_WORSENED significa che almeno una sezione peggiora.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Fase 5.8 — Quality Delta Ready Safe Motors V1\n")
    lines.append(f"- Status: `{status}`")
    lines.append(f"- Aree migliorate: `{len(improved_areas)}`")
    lines.append(f"- Aree neutre: `{len(neutral_areas)}`")
    lines.append(f"- Aree peggiorate: `{len(worsened_areas)}`")
    lines.append("")
    lines.append("| Area | Bad before | Bad after | Delta bad | Positive before | Positive after | Delta positive | Esito | Note |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---|---|")

    for item in area_reports:
        if item["worsened"]:
            esito = "PEGGIORA"
        elif item["improved"]:
            esito = "MIGLIORA"
        else:
            esito = "NEUTRO"

        lines.append(
            f"| `{item['area']}` "
            f"| {item['bad_patterns_before']} "
            f"| {item['bad_patterns_after']} "
            f"| {item['bad_patterns_delta']} "
            f"| {item['positive_patterns_before']} "
            f"| {item['positive_patterns_after']} "
            f"| {item['positive_patterns_delta']} "
            f"| `{esito}` "
            f"| {'; '.join(item['notes'])} |"
        )

    lines.append("")
    lines.append("## Dettaglio quiz\n")

    for item in area_reports:
        if item["area"] == "quiz":
            lines.append(f"- Rischio distrattori veri: `{item.get('quiz_distractor_true_fact_risk_before')} -> {item.get('quiz_distractor_true_fact_risk_after')}`")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.8 QUALITY DELTA COMPLETATA")
    print(f"Status: {status}")
    print(f"Aree migliorate: {len(improved_areas)}")
    print(f"Aree neutre: {len(neutral_areas)}")
    print(f"Aree peggiorate: {len(worsened_areas)}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    print(json.dumps({
        "status": status,
        "improved_areas": [item["area"] for item in improved_areas],
        "neutral_areas": [item["area"] for item in neutral_areas],
        "worsened_areas": [item["area"] for item in worsened_areas],
    }, ensure_ascii=False, indent=2))

    if status == "FAIL_WORSENED":
        raise AssertionError("Fase 5.8 fallita: almeno un'area peggiora.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
