#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.4.1 - patch locale qualità reale quiz/test.

Il modulo opera solo su payload quiz e solo sui campi visibili. Non modifica
QM comuni, raw_output comune, summary, cards o study_questions.
"""

from __future__ import annotations

import copy
import re
from typing import Any, Dict, Iterable, List, Sequence, Tuple

PHASE = "5.15G.4.1"

ACCENT_FIXES = {
    "responsabilita": "responsabilità",
    "qualita": "qualità",
    "finche": "finché",
    "attivita": "attività",
    "criticita": "criticità",
    "continuita": "continuità",
    "possibilita": "possibilità",
    "modalita": "modalità",
    "priorita": "priorità",
    "necessita": "necessità",
    "capacita": "capacità",
    "validita": "validità",
    "tracciabilita": "tracciabilità",
    "conformita": "conformità",
}

CONTAMINATION_PATTERNS = [
    r"\brisposta\s+corretta\b",
    r"\bopzione\s+corretta\b",
    r"\bla\s+risposta\s+giusta\s+è\b",
    r"\bprogetto\s+quiz\b",
    r"\bmotore\s+RAG\s+del\s+progetto\s+quiz\b",
    r"\bgenerare\s+quiz\b",
    r"\bquiz\b",
    r"\bquiz\s+generato\b",
    r"\bdomanda\s+di\s+test\b",
    r"\btest\s+tecnico\b",
    r"\bdocumento\s+RAG\s+di\s+test\b",
    r"\bfixture\b",
    r"\bdemo\b",
    r"\bfallback\b",
    r"\bscript\b",
    r"\bQM\b",
    r"\braw_output\b",
    r"\bgenerator\b",
]

TEMPLATE_EXPLANATION_PATTERNS = [
    r"\bla\s+risposta\s+corretta\s+(?:è|e')\b",
    r"\bquesta\s+risposta\s+(?:è|e')\s+corretta\s+perch",
    r"\ble\s+altre\s+risposte\s+sono\s+sbagliate\b",
    r"\bil\s+documento\s+evidenzia\b",
    r"\bla\s+sezione\s+descrive\b",
    r"\bquesto\s+concetto\s+(?:è|e')\s+importante\b",
    r"\bi\s+distrattori\s+cambiano\s+categoria\b",
]

OPTION_TEMPLATE_PATTERNS = [
    r"\bSpostare il controllo su una fase diversa\b",
    r"\bRegistrare l'attività in modo parziale\b",
    r"\bApplicare una regola simile ma riferita a un'altra sezione\b",
]

VISIBLE_ITEM_FIELDS = [
    "domanda",
    "question",
    "spiegazione",
    "explanation",
    "feedback",
    "fatto_origine",
    "source_fact",
]


def _finish_sentence(text: Any) -> str:
    clean = re.sub(r"\s+", " ", str(text or "").strip(" \t\r\n-;"))
    if clean and clean[-1] not in ".?!":
        clean += "."
    return clean


def _word_tokens(text: Any) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def _word_count(text: Any) -> int:
    return len(_word_tokens(text))


def _normal_key(text: Any) -> str:
    low = str(text or "").lower()
    low = re.sub(r"[^a-z0-9àèéìòù]+", " ", low)
    return re.sub(r"\s+", " ", low).strip()


def _polish_accents(text: Any) -> str:
    clean = str(text or "")
    for raw, fixed in ACCENT_FIXES.items():
        clean = re.sub(rf"\b{raw}\b", fixed, clean, flags=re.I)
    return clean


def _strip_json_noise(text: str) -> str:
    clean = re.sub(r"\bL\d+\s*:\s*", "", str(text or ""))
    clean = re.sub(r"`+", "", clean)
    clean = re.sub(r"##+", " ", clean)
    clean = re.sub(r'"\s*,\s*"(?:tags|difficolta|difficoltà|distrattore_forte|punteggio|frase|spiegazione)"\s*:\s*.*$', "", clean, flags=re.I)
    clean = re.sub(r"\[[^\]]{0,160}\]", "", clean)
    clean = re.sub(r"\{[^{}]{0,240}\}", "", clean)
    clean = re.sub(r'["“”]+', "", clean)
    return clean


def _remove_contamination_text(text: Any) -> str:
    clean = _strip_json_noise(str(text or ""))
    clean = re.sub(r"\bDocumento\s+RAG\s+di\s+test\s*:\s*", "", clean, flags=re.I)
    clean = re.sub(r"\bfonte\s+di\s+prova\s+per\s+il\s+motore\s+RAG\s+del\s+progetto\s+quiz\b", "fonte documentale per il percorso di studio", clean, flags=re.I)
    clean = re.sub(r"\bgenerare\s+quiz,\s*test\s+e\s+mini-corsi\b", "costruire esercizi e percorsi di studio", clean, flags=re.I)
    clean = re.sub(r"^\s*Keyword\s*:\s*", "", clean, flags=re.I)
    clean = re.sub(r"\bcorretta\s+risposta\b", "", clean, flags=re.I)
    clean = re.sub(r"\brisposta\s+corretta\b", "", clean, flags=re.I)
    clean = re.sub(r"\bopzione\s+corretta\b", "", clean, flags=re.I)
    clean = re.sub(r"\bla\s+risposta\s+giusta\s+è\b", "", clean, flags=re.I)
    for pattern in CONTAMINATION_PATTERNS:
        clean = re.sub(pattern, "", clean, flags=re.I)
    clean = re.sub(r"\s+([,.;:!?])", r"\1", clean)
    clean = re.sub(r"\s+", " ", clean).strip(" .,:;-")
    return _finish_sentence(_polish_accents(clean)) if clean else ""


def _has_contamination(text: Any) -> bool:
    value = str(text or "")
    return any(re.search(pattern, value, flags=re.I) for pattern in CONTAMINATION_PATTERNS)


def _has_template_explanation(text: Any) -> bool:
    value = str(text or "")
    return any(re.search(pattern, value, flags=re.I) for pattern in TEMPLATE_EXPLANATION_PATTERNS)


def _accent_warning_count(text: Any) -> int:
    value = str(text or "").lower()
    return sum(1 for raw in ACCENT_FIXES if re.search(rf"\b{raw}\b", value))


def _visible_blob(items: Sequence[Dict[str, Any]]) -> str:
    parts: List[str] = []
    for item in items:
        for field in VISIBLE_ITEM_FIELDS:
            if item.get(field):
                parts.append(str(item.get(field)))
        for option in _options(item):
            parts.append(str(option.get("testo") or option.get("text") or ""))
    return " ".join(parts)


def _options(item: Dict[str, Any]) -> List[Dict[str, Any]]:
    value = item.get("opzioni") or item.get("options") or []
    return [option for option in value if isinstance(option, dict)]


def _option_text(option: Dict[str, Any]) -> str:
    return str(option.get("testo") or option.get("text") or "").strip()


def _set_option_text(option: Dict[str, Any], text: str) -> None:
    option["testo"] = _finish_sentence(text)
    if "text" in option:
        option["text"] = option["testo"]


def _infer_correct_option(item: Dict[str, Any]) -> Tuple[str, int | None]:
    correct_id = str(item.get("correct_option_id") or item.get("risposta_corretta") or "")
    options = _options(item)
    for index, option in enumerate(options):
        option_id = str(option.get("option_id") or "")
        if option.get("is_correct") is True or (correct_id and option_id == correct_id):
            return option_id, index
    origin = _normal_key(item.get("fatto_origine") or item.get("source_fact") or "")
    origin_terms = {word for word in origin.split() if len(word) >= 5}
    best_index = None
    best_score = 0
    for index, option in enumerate(options):
        text = _normal_key(_option_text(option))
        if origin and (text in origin or origin in text):
            return str(option.get("option_id") or ""), index
        terms = {word for word in text.split() if len(word) >= 5}
        score = len(origin_terms & terms)
        if score > best_score:
            best_score = score
            best_index = index
    if best_index is not None and best_score >= max(2, min(5, len(origin_terms) // 3)):
        return str(options[best_index].get("option_id") or ""), best_index
    return correct_id, None


def _concept_terms(item: Dict[str, Any], input_text: str = "") -> List[str]:
    source = " ".join(
        str(item.get(key) or "")
        for key in ["titolo", "title", "fatto_origine", "source_fact", "domanda", "question"]
    )
    source = _remove_contamination_text(source)
    stop = {
        "come", "quale", "passaggio", "documento", "opzione", "conserva", "dettaglio",
        "essenziale", "verificare", "macro", "area", "nella", "della", "delle",
        "degli", "responsabilità", "controllo", "verifica", "attività", "corretta",
        "risposta", "test", "quiz", "domanda",
    }
    out: List[str] = []
    for word in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{5,}", source.lower()):
        if word in stop or word in out:
            continue
        out.append(word)
        if len(out) >= 5:
            break
    if not out and input_text:
        for word in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{5,}", input_text.lower()):
            if word not in stop and word not in out:
                out.append(word)
            if len(out) >= 4:
                break
    return out or ["passaggio", "operativo"]


def _concept_label(item: Dict[str, Any], input_text: str = "") -> str:
    terms = _concept_terms(item, input_text)
    label = " ".join(terms[:4])
    return label[:1].upper() + label[1:]


def _safe_correct_text(item: Dict[str, Any], original_text: str, input_text: str = "") -> str:
    cleaned = _remove_contamination_text(original_text)
    if _word_count(cleaned) >= 8 and not _has_contamination(cleaned):
        return cleaned
    label = _concept_label(item, input_text)
    return _finish_sentence(f"{label}: mantiene insieme contenuto, responsabilità, evidenza e verifica indicati dal documento")


def _fallback_distractors(item: Dict[str, Any], input_text: str = "") -> List[str]:
    return [
        _finish_sentence("Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica"),
        _finish_sentence("Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento"),
        _finish_sentence("Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile"),
    ]


def _clean_question(item: Dict[str, Any], input_text: str = "") -> str:
    question = _remove_contamination_text(item.get("domanda") or item.get("question") or "")
    if (
        not question
        or _has_contamination(question)
        or re.search(r"\b(?:quale opzione conserva il dettaglio documentale essenziale|come verificare\s+\w+\s+nella macro-area)\b", question, flags=re.I)
    ):
        label = _concept_label(item, input_text).lower()
        question = _finish_sentence(f"Quale scelta mantiene verificabile {label} secondo il documento?")
    return question


def remove_quiz_contamination(payload: Dict[str, Any], input_text: str = "") -> Dict[str, Any]:
    fixed = copy.deepcopy(payload)
    items = fixed.get("items") if isinstance(fixed.get("items"), list) else []
    for item in items:
        if not isinstance(item, dict):
            continue
        item["domanda"] = item["question"] = _clean_question(item, input_text)
        for field in ["titolo", "title", "fatto_origine", "source_fact", "feedback"]:
            if field in item and isinstance(item.get(field), str):
                item[field] = _remove_contamination_text(item.get(field))
        options = _options(item)
        has_visible_correct_contract = (
            "correct_option_id" in item
            or "risposta_corretta" in item
            or any(isinstance(option, dict) and option.get("is_correct") is True for option in options)
        )
        correct_id, correct_index = _infer_correct_option(item)
        fallback_distractors = _fallback_distractors(item, input_text)
        fallback_index = 0
        for index, option in enumerate(options):
            original = _option_text(option)
            if correct_index is not None and index == correct_index:
                cleaned = _safe_correct_text(item, original or item.get("fatto_origine") or "", input_text)
            else:
                cleaned = _remove_contamination_text(original)
                is_template_option = any(re.search(pattern, cleaned, flags=re.I) for pattern in OPTION_TEMPLATE_PATTERNS)
                if _word_count(cleaned) < 6 or _has_contamination(cleaned) or is_template_option:
                    cleaned = fallback_distractors[fallback_index % len(fallback_distractors)]
                    fallback_index += 1
            _set_option_text(option, cleaned)
        if correct_id and has_visible_correct_contract:
            item["correct_option_id"] = correct_id
            item["risposta_corretta"] = correct_id
    return fixed


def polish_quiz_language_universal(payload: Dict[str, Any]) -> Dict[str, Any]:
    fixed = copy.deepcopy(payload)
    items = fixed.get("items") if isinstance(fixed.get("items"), list) else []
    for item in items:
        if not isinstance(item, dict):
            continue
        for field in VISIBLE_ITEM_FIELDS + ["titolo", "title"]:
            if field in item and isinstance(item.get(field), str):
                item[field] = _finish_sentence(_polish_accents(item.get(field))) if field in {"domanda", "question", "spiegazione", "explanation", "feedback", "fatto_origine", "source_fact"} else _polish_accents(item.get(field))
        for option in _options(item):
            _set_option_text(option, _polish_accents(_option_text(option)))
    return fixed


def _explanation_for(item: Dict[str, Any], index: int, input_text: str = "") -> str:
    label = _concept_label(item, input_text).lower()
    options = _options(item)
    correct_id, correct_index = _infer_correct_option(item)
    correct = _option_text(options[correct_index]) if correct_index is not None and correct_index < len(options) else ""
    distractor = ""
    for idx, option in enumerate(options):
        if idx != correct_index:
            distractor = _option_text(option)
            break
    variants = [
        f"La scelta più adatta mantiene {label} collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio documentale.",
        f"Il punto da riconoscere è {label}: la soluzione selezionata conserva il legame con il contenuto fonte. Un distrattore modifica fase, responsabilità o tracciabilità e per questo perde coerenza con il documento.",
        f"Per rispondere bisogna tenere insieme concetto, prova e conseguenza operativa. L'opzione più adatta riprende {label}, mentre una scelta generica non chiarisce chi verifica il passaggio e con quale evidenza.",
        f"La domanda verifica {label} come passaggio concreto, non come formula astratta. La scelta migliore resta ancorata al contenuto; un distrattore confonde contesto o controllo e riduce il valore didattico.",
    ]
    explanation = variants[(index - 1) % len(variants)]
    if correct and distractor and _word_count(explanation) < 34:
        explanation += f" In pratica, {correct[:90].rstrip(' .')} resta più specifico di {distractor[:70].rstrip(' .')}."
    return _finish_sentence(explanation)


def improve_quiz_explanations(payload: Dict[str, Any], input_text: str = "") -> Dict[str, Any]:
    fixed = copy.deepcopy(payload)
    items = fixed.get("items") if isinstance(fixed.get("items"), list) else []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        explanation = str(item.get("spiegazione") or item.get("explanation") or "")
        if _has_template_explanation(explanation) or _word_count(explanation) < 18 or _has_contamination(explanation):
            explanation = _explanation_for(item, index, input_text)
        else:
            explanation = _remove_contamination_text(explanation)
        item["spiegazione"] = item["explanation"] = _finish_sentence(_polish_accents(explanation))
        if isinstance(item.get("answer_check"), dict):
            item["answer_check"] = dict(item["answer_check"])
            item["answer_check"]["explanation"] = item["spiegazione"]
    if isinstance(fixed.get("quality_report"), dict):
        fixed["quality_report"] = dict(fixed["quality_report"])
    return fixed


def _duplicate_option_count(items: Sequence[Dict[str, Any]]) -> int:
    duplicates = 0
    for item in items:
        seen = set()
        for option in _options(item):
            key = _normal_key(_option_text(option))
            if key and key in seen:
                duplicates += 1
            seen.add(key)
    return duplicates


def _weak_distractor_count(items: Sequence[Dict[str, Any]]) -> int:
    weak = 0
    for item in items:
        _, correct_index = _infer_correct_option(item)
        for index, option in enumerate(_options(item)):
            if correct_index is not None and index == correct_index:
                continue
            text = _option_text(option)
            if _word_count(text) < 6 or _has_contamination(text):
                weak += 1
    return weak


def validate_quiz_real_quality(payload: Dict[str, Any]) -> Dict[str, Any]:
    items = payload.get("items") if isinstance(payload.get("items"), list) else []
    visible_blob = _visible_blob(items)
    contamination_count = sum(1 for pattern in CONTAMINATION_PATTERNS if re.search(pattern, visible_blob, flags=re.I))
    visible_correct_answer_leak_count = len(re.findall(r"\b(?:risposta\s+corretta|opzione\s+corretta|la\s+risposta\s+giusta)\b", visible_blob, flags=re.I))
    template_explanation_count = sum(1 for item in items if _has_template_explanation(item.get("spiegazione") or item.get("explanation") or ""))
    accent_warning_count = _accent_warning_count(visible_blob)
    short_explanation_count = sum(1 for item in items if _word_count(item.get("spiegazione") or item.get("explanation") or "") < 18)
    duplicate_option_count = _duplicate_option_count(items)
    weak_distractor_count = _weak_distractor_count(items)
    options_ok = all(len(_options(item)) == 4 for item in items)
    correct_ok = all(_infer_correct_option(item)[1] is not None for item in items)
    metrics = {
        "contamination_count": contamination_count,
        "visible_correct_answer_leak_count": visible_correct_answer_leak_count,
        "template_explanation_count": template_explanation_count,
        "accent_warning_count": accent_warning_count,
        "short_explanation_count": short_explanation_count,
        "duplicate_option_count": duplicate_option_count,
        "weak_distractor_count": weak_distractor_count,
        "questions_count": len(items),
        "questions_with_4_options": sum(1 for item in items if len(_options(item)) == 4),
        "questions_with_1_correct": sum(1 for item in items if _infer_correct_option(item)[1] is not None),
        "questions_with_3_distractors": sum(1 for item in items if len(_options(item)) == 4 and _infer_correct_option(item)[1] is not None),
    }
    defects = []
    if contamination_count:
        defects.append("visible_contamination_present")
    if visible_correct_answer_leak_count:
        defects.append("visible_correct_answer_leak_present")
    if duplicate_option_count:
        defects.append("duplicate_options_present")
    if not options_ok:
        defects.append("four_options_contract_broken")
    if not correct_ok:
        defects.append("single_correct_contract_broken")
    warnings = []
    if template_explanation_count:
        warnings.append("template_explanations_present")
    if accent_warning_count:
        warnings.append("accent_warnings_present")
    if short_explanation_count:
        warnings.append("short_explanations_present")
    if weak_distractor_count:
        warnings.append("weak_distractors_present")
    return {
        "pass": not defects,
        "defects": defects,
        "warnings": warnings,
        "metrics": {
            **metrics,
            "quiz_real_quality_pass": not defects and template_explanation_count == 0 and accent_warning_count == 0,
        },
    }


def apply_quiz_real_quality_fix(payload: Dict[str, Any], input_text: str = "") -> Dict[str, Any]:
    if not isinstance(payload, dict):
        return payload
    fixed = remove_quiz_contamination(payload, input_text)
    fixed = polish_quiz_language_universal(fixed)
    fixed = improve_quiz_explanations(fixed, input_text)
    validation = validate_quiz_real_quality(fixed)
    report = dict(fixed.get("quality_report") or {})
    report.update(
        {
            "phase5_15g41_quiz_real_quality_fix": True,
            "g41_quiz_real_quality_validation": validation,
            "g41_quiz_real_quality_metrics": validation.get("metrics", {}),
            "g41_quiz_real_quality_defects": validation.get("defects", []),
            "g41_quiz_real_quality_warnings": validation.get("warnings", []),
        }
    )
    fixed["quality_report"] = report
    return fixed
