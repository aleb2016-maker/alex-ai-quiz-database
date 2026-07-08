#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.4 - real quality review per quiz/test long-doc.

Diagnostica e report soltanto: non modifica runtime, generatori o QM.
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator  # noqa: E402
from backend.phase5_15g1_long_document_orchestrator import is_long_document  # noqa: E402

REPORT_JSON = ROOT / "reports/phase5_15g4_quiz_real_quality_review_v1.json"
REPORT_MD = ROOT / "reports/phase5_15g4_quiz_real_quality_review_v1.md"

DOCUMENTS: List[Tuple[str, str, str]] = [
    ("real_long_audit_doc", "reports/audit_effetti_premi_ai_its.md", "real_long"),
    ("synthetic_long_business_doc", "rag/documenti/test_documento_lungo_aziendale_120_pagine.txt", "synthetic_long_stress"),
    ("security_training_doc", "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md", "medium_security"),
    ("ai_generative_rag_doc", "rag/documenti/documento_ai_generativa_test_rag.md", "different_domain_ai"),
    ("business_training_short_doc", "rag/documenti/esempio_documento_aziendale_formazione.md", "short_business"),
]

SYSTEM_NOISE = [
    "fallback",
    "fixture tecnica",
    "documento fixture",
    "non contiene dati reali",
    "collegato alla demo",
]
DEMO_PATTERNS = [r"\bdemo\b", r"\btest tecnico\b", r"\bplaceholder\b"]
TEMPLATE_PHRASES = [
    "La risposta corretta conserva il riferimento concreto della macro-area",
    "La risposta corretta è coerente con il documento perché riprende il punto operativo verificabile",
    "i distrattori cambiano categoria, responsabilita o controllo",
    "Spostare il controllo su una fase diversa",
    "Registrare l'attività in modo parziale",
    "Applicare una regola simile ma riferita a un'altra sezione",
]
GENERIC_QUESTION_PATTERNS = [
    r"quale opzione conserva il dettaglio documentale essenziale",
    r"come verificare .+ nella macro-area \d+",
    r"il documento parla di",
    r"aspetti importanti",
]
FORBIDDEN_OPTION_PATTERNS = [
    r"tutte le precedenti",
    r"nessuna delle precedenti",
    r"la risposta giusta",
    r"risposta corretta",
]
ACCENT_WARNINGS = {
    "qualita": "qualità",
    "attivita": "attività",
    "responsabilita": "responsabilità",
    "priorita": "priorità",
    "conformita": "conformità",
    "finche": "finché",
    "perche": "perché",
    "cosi": "così",
}


def word_tokens(text: Any) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def word_count(text: Any) -> int:
    return len(word_tokens(text))


def normalize(text: Any) -> str:
    low = str(text or "").lower()
    low = re.sub(r"[^a-z0-9àèéìòù]+", " ", low)
    return re.sub(r"\s+", " ", low).strip()


def compact(text: Any, limit: int = 240) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    return clean if len(clean) <= limit else clean[: limit - 3].rstrip() + "..."


def final_output(result: Dict[str, Any]) -> Dict[str, Any]:
    output = result.get("final_output") or result.get("raw_output") or result
    return output if isinstance(output, dict) else {"content": str(output or "")}


def quiz_items(output: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ("items", "quiz_plan", "questions", "quiz", "domande"):
        value = output.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
    return []


def option_texts(item: Dict[str, Any]) -> List[str]:
    raw = item.get("opzioni") or item.get("options") or []
    out: List[str] = []
    for option in raw:
        if isinstance(option, dict):
            out.append(str(option.get("testo") or option.get("text") or option.get("label") or "").strip())
        else:
            out.append(str(option or "").strip())
    return out


def question_text(item: Dict[str, Any]) -> str:
    return str(item.get("domanda") or item.get("question") or "").strip()


def explanation_text(item: Dict[str, Any]) -> str:
    return str(item.get("spiegazione") or item.get("explanation") or item.get("answer_explanation") or "").strip()


def origin_text(item: Dict[str, Any]) -> str:
    return str(item.get("fatto_origine") or item.get("source_sentence") or item.get("fact") or "").strip()


def infer_correct_option(item: Dict[str, Any]) -> Tuple[int | None, str]:
    options = option_texts(item)
    origin = normalize(origin_text(item))
    if not origin:
        return None, ""
    scored: List[Tuple[int, int]] = []
    origin_terms = set(word for word in origin.split() if len(word) >= 5)
    for index, option in enumerate(options):
        key = normalize(option)
        if not key:
            continue
        if key == origin or key in origin or origin in key:
            return index, option
        option_terms = set(word for word in key.split() if len(word) >= 5)
        overlap = len(origin_terms & option_terms)
        scored.append((overlap, index))
    if scored:
        scored.sort(reverse=True)
        if scored[0][0] >= max(3, int(len(origin_terms) * 0.35)):
            idx = scored[0][1]
            return idx, options[idx]
    return None, ""


def duplicate_count(values: Sequence[str]) -> int:
    seen = set()
    count = 0
    for value in values:
        key = normalize(value)
        if not key:
            continue
        if key in seen:
            count += 1
        seen.add(key)
    return count


def near_duplicate_count(values: Sequence[str]) -> int:
    keys = [" ".join(normalize(value).split()[:8]) for value in values if normalize(value)]
    seen = set()
    count = 0
    for key in keys:
        if key in seen:
            count += 1
        seen.add(key)
    return count


def grammar_warnings(text: str) -> List[str]:
    warnings = []
    low = str(text or "").lower()
    for raw, correct in ACCENT_WARNINGS.items():
        if re.search(rf"\b{re.escape(raw)}\b", low):
            warnings.append(f"accento: {raw}->{correct}")
    if re.search(r"\s+[,.!?;:]", text):
        warnings.append("spazio_prima_punteggiatura")
    if text and text[-1] not in ".?!:;”\"')":
        warnings.append("finale_senza_punteggiatura")
    if re.search(r"\b\w{1,2}\b\s*$", text) and word_count(text) > 8:
        warnings.append("finale_sospetto")
    return warnings


def broken_sentence(text: str) -> bool:
    clean = str(text or "").strip()
    if not clean:
        return True
    if len(clean) > 35 and clean[-1] not in ".?!:;”\"')":
        return True
    if re.search(r"\b(?:e|di|con|per|tra|fra|che)\s*$", clean.lower()):
        return True
    return False


def source_coherence(item: Dict[str, Any]) -> float:
    question = normalize(question_text(item))
    explanation = normalize(explanation_text(item))
    origin = normalize(origin_text(item))
    if not origin:
        return 0.0
    origin_terms = {word for word in origin.split() if len(word) >= 5}
    quiz_terms = {word for word in f"{question} {explanation}".split() if len(word) >= 5}
    if not origin_terms:
        return 0.0
    return round(min(1.0, len(origin_terms & quiz_terms) / max(1, min(10, len(origin_terms))) + 0.35), 3)


def distractor_quality(item: Dict[str, Any], correct_index: int | None) -> Tuple[int, int, List[str]]:
    options = option_texts(item)
    correct = options[correct_index] if correct_index is not None and correct_index < len(options) else ""
    correct_len = max(1, word_count(correct))
    strong = 0
    weak = 0
    defects: List[str] = []
    for idx, option in enumerate(options):
        if idx == correct_index:
            continue
        opt_words = word_count(option)
        low = option.lower()
        if not option or opt_words < 6:
            weak += 1
            defects.append(f"distrattore_{idx + 1}_troppo_corto")
            continue
        similarity_len = min(opt_words, correct_len) / max(opt_words, correct_len)
        plausible_marker = any(token in low for token in ["controll", "respons", "risch", "verifica", "sezione", "documento", "attività", "regola", "fase", "contesto"])
        absurd_marker = any(token in low for token in ["sempre", "mai", "casuale", "irrilevante", "magico"])
        duplicate_like = normalize(option) == normalize(correct) or normalize(option) in normalize(correct)
        if duplicate_like:
            weak += 1
            defects.append(f"distrattore_{idx + 1}_duplica_risposta")
        elif plausible_marker and not absurd_marker and similarity_len >= 0.35:
            strong += 1
        else:
            weak += 1
            defects.append(f"distrattore_{idx + 1}_debole")
    return strong, weak, defects


def inspect_item(item: Dict[str, Any], index: int) -> Dict[str, Any]:
    question = question_text(item)
    options = option_texts(item)
    explanation = explanation_text(item)
    correct_index, correct_text = infer_correct_option(item)
    text_blob = " ".join([question, explanation] + options)
    item_defects: List[str] = []
    item_warnings: List[str] = []
    if not question:
        item_defects.append("domanda_assente")
    if len(options) != 4:
        item_defects.append(f"opzioni_count_{len(options)}")
    if correct_index is None:
        item_defects.append("risposta_corretta_non_inferibile")
    if duplicate_count(options):
        item_defects.append("opzioni_duplicate")
    if near_duplicate_count(options):
        item_warnings.append("opzioni_quasi_duplicate")
    if any(not option for option in options):
        item_defects.append("opzione_vuota")
    if any(word_count(option) <= 2 for option in options):
        item_warnings.append("opzione_troppo_breve")
    if any(re.search(pattern, option.lower(), flags=re.I) for option in options for pattern in FORBIDDEN_OPTION_PATTERNS):
        item_defects.append("opzione_con_indizio_o_formula_vietata")
    if any(re.search(pattern, question.lower(), flags=re.I) for pattern in GENERIC_QUESTION_PATTERNS):
        item_warnings.append("domanda_generica_o_template")
    if not explanation:
        item_defects.append("spiegazione_assente")
    elif word_count(explanation) < 12:
        item_warnings.append("spiegazione_troppo_corta")
    if explanation and any(phrase.lower() in explanation.lower() for phrase in TEMPLATE_PHRASES):
        item_warnings.append("spiegazione_template")
    if "risposta corretta" in question.lower() or any("risposta corretta" in option.lower() for option in options):
        item_defects.append("risposta_corretta_visibile_prima_interazione")
    if any(noise in text_blob.lower() for noise in SYSTEM_NOISE) or any(re.search(pattern, text_blob.lower()) for pattern in DEMO_PATTERNS):
        item_defects.append("fallback_demo_noise")
    if broken_sentence(question) or any(broken_sentence(option) for option in options) or broken_sentence(explanation):
        item_warnings.append("frase_rotta_o_troncata")
    grammar = grammar_warnings(text_blob)
    if grammar:
        item_warnings.extend(grammar[:4])
    strong, weak, distractor_defects = distractor_quality(item, correct_index)
    item_warnings.extend(distractor_defects)
    if strong < 2:
        item_warnings.append("distrattori_poco_forti")
    quality = "PASS"
    if item_defects:
        quality = "FAIL"
    elif item_warnings:
        quality = "WARNING"
    return {
        "index": index,
        "question": question,
        "options": options,
        "correct_option_index": correct_index,
        "correct_answer": correct_text,
        "explanation": explanation,
        "strong_distractors": strong,
        "weak_distractors": weak,
        "source_coherence_score": source_coherence(item),
        "quality": quality,
        "defects": item_defects,
        "warnings": sorted(set(item_warnings)),
    }


def concept_coverage(items: Sequence[Dict[str, Any]], long_doc: bool) -> float:
    if not items:
        return 0.0
    areas = set()
    question_keys = set()
    for item in items:
        if item.get("source_macro_area_index"):
            areas.add(str(item.get("source_macro_area_index")))
        elif item.get("source_macro_area"):
            areas.add(str(item.get("source_macro_area")))
        key = " ".join(normalize(question_text(item)).split()[:5])
        if key:
            question_keys.add(key)
    base = len(question_keys) / max(1, len(items))
    if long_doc:
        base = min(1.0, (base * 0.55) + (len(areas) / max(1, min(6, len(items))) * 0.45))
    return round(base, 3)


def read_documents() -> List[Dict[str, Any]]:
    docs: List[Dict[str, Any]] = []
    for name, rel_path, doc_type in DOCUMENTS:
        path = ROOT / rel_path
        if path.exists():
            text = path.read_text(encoding="utf-8")
            docs.append({"name": name, "filepath": rel_path, "type": doc_type, "text": text})
    return docs


def severity_from_case(defects: List[str], warnings: List[str], approved: bool, qm_count: int) -> str:
    if not approved or qm_count != 63:
        return "BLOCKING"
    if any(token in defects for token in ["missing_four_options", "missing_single_correct", "fallback_demo_visible", "missing_explanations"]):
        return "BLOCKING"
    if warnings or defects:
        return "WARNING"
    return "NON_BLOCKING"


def inspect_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    text = doc["text"]
    long_doc = is_long_document(text)
    result = run_quality_checked_generator("quiz", text)
    output = final_output(result)
    items = quiz_items(output)
    inspected = [inspect_item(item, idx + 1) for idx, item in enumerate(items)]
    options_counts = [len(option_texts(item)) for item in items]
    correct_count = sum(1 for item in inspected if item["correct_option_index"] is not None)
    with_4 = sum(1 for value in options_counts if value == 4)
    with_3_distractors = sum(1 for item in inspected if len(item["options"]) == 4 and item["correct_option_index"] is not None)
    explanations_present = sum(1 for item in inspected if bool(item["explanation"]))
    explanation_short = sum(1 for item in inspected if "spiegazione_troppo_corta" in item["warnings"])
    explanation_generic = sum(1 for item in inspected if "spiegazione_template" in item["warnings"])
    question_values = [item["question"] for item in inspected]
    option_dup_count = sum(duplicate_count(item["options"]) for item in inspected)
    option_near_dup_count = sum(near_duplicate_count(item["options"]) for item in inspected)
    visible_answer_count = sum(1 for item in inspected if "risposta_corretta_visibile_prima_interazione" in item["defects"])
    fallback_demo_count = sum(1 for item in inspected if "fallback_demo_noise" in item["defects"])
    template_phrase_count = sum(
        sum(1 for phrase in TEMPLATE_PHRASES if phrase.lower() in " ".join([item["question"], item["explanation"]] + item["options"]).lower())
        for item in inspected
    )
    grammar_warning_count = sum(1 for item in inspected for warning in item["warnings"] if warning.startswith("accento:") or warning in {"spazio_prima_punteggiatura", "finale_senza_punteggiatura", "finale_sospetto"})
    broken_count = sum(1 for item in inspected if "frase_rotta_o_troncata" in item["warnings"])
    strong = sum(item["strong_distractors"] for item in inspected)
    weak = sum(item["weak_distractors"] for item in inspected)
    coherence_scores = [item["source_coherence_score"] for item in inspected]
    source_score = round(sum(coherence_scores) / max(1, len(coherence_scores)), 3)
    coverage_score = concept_coverage(items, long_doc)
    explanation_score = explanations_present / max(1, len(items))
    distractor_score = strong / max(1, strong + weak)
    didactic_score = round((coverage_score * 0.25) + (source_score * 0.25) + (distractor_score * 0.25) + (explanation_score * 0.25), 3)
    linguistic_score = round(max(0.0, 1.0 - (grammar_warning_count + broken_count) / max(1, len(items) * 5)), 3)
    overall = round((didactic_score * 0.5) + (linguistic_score * 0.2) + (distractor_score * 0.2) + (source_score * 0.1), 3)
    case_defects: List[str] = []
    case_warnings: List[str] = []
    if result.get("approved") is not True:
        case_defects.append(f"approved_non_true:{result.get('approved')}")
    if result.get("status") != "APPROVED":
        case_defects.append(f"status_non_approved:{result.get('status')}")
    if int(result.get("executed_qm_count") or 0) != 63:
        case_defects.append(f"qm_quiz_count:{result.get('executed_qm_count')}")
    if with_4 != len(items):
        case_defects.append("missing_four_options")
    if correct_count != len(items):
        case_defects.append("missing_single_correct")
    if with_3_distractors != len(items):
        case_defects.append("missing_three_distractors")
    if explanations_present != len(items):
        case_defects.append("missing_explanations")
    if fallback_demo_count:
        case_defects.append("fallback_demo_visible")
    if option_dup_count:
        case_defects.append("duplicate_options")
    if visible_answer_count:
        case_defects.append("correct_answer_visible_before_interaction")
    if duplicate_count(question_values):
        case_defects.append("duplicate_questions")
    if weak:
        case_warnings.append(f"weak_distractors:{weak}")
    if template_phrase_count:
        case_warnings.append(f"template_phrases:{template_phrase_count}")
    if grammar_warning_count:
        case_warnings.append(f"grammar_warnings:{grammar_warning_count}")
    if explanation_short or explanation_generic:
        case_warnings.append(f"explanation_quality:{explanation_short + explanation_generic}")
    if near_duplicate_count(question_values):
        case_warnings.append(f"near_duplicate_questions:{near_duplicate_count(question_values)}")
    if option_near_dup_count:
        case_warnings.append(f"near_duplicate_options:{option_near_dup_count}")
    if didactic_score < 0.72:
        case_warnings.append(f"didactic_score_low:{didactic_score}")
    severity = severity_from_case(case_defects, case_warnings, result.get("approved") is True, int(result.get("executed_qm_count") or 0))
    judgment = "FAIL" if severity == "BLOCKING" else ("WARNING" if case_warnings or case_defects else "PASS")
    return {
        "name": doc["name"],
        "filepath": doc["filepath"],
        "type": doc["type"],
        "input_words": word_count(text),
        "long_doc": long_doc,
        "quiz_active": output.get("kind") == "quiz" or bool(items),
        "questions_generated": len(items),
        "qm_quiz_count": int(result.get("executed_qm_count") or 0),
        "expected_qm_quiz_count": int(result.get("expected_qm_count") or 63),
        "approved": result.get("approved"),
        "status": result.get("status"),
        "motor": output.get("motor_name"),
        "question_count": len(items),
        "options_per_question": options_counts,
        "questions_with_4_options": with_4,
        "questions_with_1_correct": correct_count,
        "questions_with_3_distractors": with_3_distractors,
        "strong_distractors_count": strong,
        "weak_distractors_count": weak,
        "duplicate_options_count": option_dup_count,
        "near_duplicate_options_count": option_near_dup_count,
        "visible_correct_answers_count": visible_answer_count,
        "explanations_present_count": explanations_present,
        "short_explanations_count": explanation_short,
        "generic_explanations_count": explanation_generic,
        "generic_questions_count": sum(1 for item in inspected if "domanda_generica_o_template" in item["warnings"]),
        "duplicate_questions_count": duplicate_count(question_values),
        "near_duplicate_questions_count": near_duplicate_count(question_values),
        "fallback_demo_count": fallback_demo_count,
        "template_phrase_count": template_phrase_count,
        "grammar_warning_count": grammar_warning_count,
        "broken_sentence_count": broken_count,
        "source_coherence_score": source_score,
        "concept_coverage_score": coverage_score,
        "didactic_quality_score": didactic_score,
        "linguistic_quality_score": linguistic_score,
        "overall_quiz_real_quality_score": overall,
        "severity": severity,
        "judgment": judgment,
        "human_usefulness_estimate": "utile con warning" if judgment == "WARNING" else ("utile" if judgment == "PASS" else "non utile senza correzioni"),
        "defects": case_defects,
        "warnings": case_warnings,
        "qm_defects_sample": list(result.get("defects") or [])[:12],
        "examples": inspected[:5],
    }


def write_reports(report: Dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# FASE 5.15G.4 - Real quality review quiz/test",
        "",
        f"Status: **{report['status']}**",
        "",
        "## Sintesi",
        "",
        f"- Documenti testati: `{len(report['documents'])}`",
        f"- Quiz 63/63 su documenti APPROVED: `{report['quiz_63_63_pass']}`",
        f"- Runtime/generatori modificati: `False`",
        f"- Target 10% applicato: `False`",
        "",
    ]
    for doc in report["documents"]:
        lines.extend(
            [
                f"## {doc['name']} - {doc['judgment']}",
                "",
                f"- Filepath: `{doc['filepath']}`",
                f"- Type: `{doc['type']}`; input_words: `{doc['input_words']}`; long_doc: `{doc['long_doc']}`; quiz_active: `{doc['quiz_active']}`",
                f"- Domande: `{doc['question_count']}`; 4 opzioni: `{doc['questions_with_4_options']}`; 1 corretta inferita: `{doc['questions_with_1_correct']}`; 3 distrattori: `{doc['questions_with_3_distractors']}`",
                f"- QM quiz: `{doc['qm_quiz_count']}/{doc['expected_qm_quiz_count']}`; approved: `{doc['approved']}`; status: `{doc['status']}`",
                f"- Distrattori forti/deboli: `{doc['strong_distractors_count']}` / `{doc['weak_distractors_count']}`",
                f"- Spiegazioni presenti/corte/generiche: `{doc['explanations_present_count']}` / `{doc['short_explanations_count']}` / `{doc['generic_explanations_count']}`",
                f"- Duplicati domande/opzioni: `{doc['duplicate_questions_count']}` / `{doc['duplicate_options_count']}`; quasi duplicati: `{doc['near_duplicate_questions_count']}` / `{doc['near_duplicate_options_count']}`",
                f"- Noise/template/grammar/broken: `{doc['fallback_demo_count']}` / `{doc['template_phrase_count']}` / `{doc['grammar_warning_count']}` / `{doc['broken_sentence_count']}`",
                f"- Score source/coverage/didactic/linguistic/overall: `{doc['source_coherence_score']}` / `{doc['concept_coverage_score']}` / `{doc['didactic_quality_score']}` / `{doc['linguistic_quality_score']}` / `{doc['overall_quiz_real_quality_score']}`",
                f"- Severity: `{doc['severity']}`; utilità stimata: `{doc['human_usefulness_estimate']}`",
                f"- Difetti: `{doc['defects']}`",
                f"- Warning: `{doc['warnings']}`",
                "",
                "### Esempi",
                "",
            ]
        )
        for example in doc["examples"][:5]:
            lines.extend(
                [
                    f"#### Domanda {example['index']} - {example['quality']}",
                    "",
                    f"Domanda: {example['question']}",
                    "",
                    "Opzioni:",
                ]
            )
            for idx, option in enumerate(example["options"], start=1):
                marker = " (corretta inferita)" if example["correct_option_index"] == idx - 1 else ""
                lines.append(f"- {idx}. {compact(option)}{marker}")
            lines.extend(
                [
                    "",
                    f"Risposta corretta: {compact(example['correct_answer'])}",
                    f"Spiegazione: {compact(example['explanation'])}",
                    f"Giudizio qualità: `{example['quality']}`",
                    f"Difetti item: `{example['defects']}`",
                    f"Warning item: `{example['warnings']}`",
                    "",
                ]
            )
    REPORT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    documents = [inspect_document(doc) for doc in read_documents()]
    blocking = [doc for doc in documents if doc["severity"] == "BLOCKING"]
    warnings = [doc for doc in documents if doc["judgment"] == "WARNING"]
    quiz_63_63_pass = all(doc["qm_quiz_count"] == 63 for doc in documents)
    if blocking:
        status = "FAIL"
    elif warnings:
        status = "WARNING"
    else:
        status = "PASS"
    report = {
        "phase": "5.15G.4",
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "status": status,
        "quiz_63_63_pass": quiz_63_63_pass,
        "documents": documents,
        "rules": {
            "runtime_modified": False,
            "target_10_percent_applied": False,
            "scope": "quiz/test only; diagnostics/report only",
        },
    }
    write_reports(report)
    print(f"phase5_15g4_quiz_real_quality_review: {status}")
    print(f"json: {REPORT_JSON}")
    print(f"markdown: {REPORT_MD}")
    return 0 if status in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
