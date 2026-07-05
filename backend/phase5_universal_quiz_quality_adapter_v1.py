from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Tuple


# FASE 5.9.8 — UNIVERSAL QUIZ QUALITY ADAPTER V1
#
# Scopo:
# - trasformare funzioni/parziali quiz in un motore completo e riutilizzabile;
# - lavorare su quiz in formato Phase 5, legacy o misto;
# - migliorare:
#   1. distrattori veri,
#   2. domande meccaniche,
#   3. domande ripetitive,
#   4. spiegazioni grezze,
#   5. piccoli difetti linguistici.
#
# Stato:
# - motore reale separato;
# - non ancora collegato al registry;
# - nessun effetto collaterale su file;
# - input/output compatibile con lista quiz o payload completo.


try:
    from backend.phase5_quiz_true_distractor_repair_v1 import (
        repair_quiz_true_distractors_v1,
    )
except Exception:  # pragma: no cover
    repair_quiz_true_distractors_v1 = None


MECHANICAL_QUESTION_PATTERNS = [
    "quale affermazione è supportata dal documento",
    "quale regola o informazione emerge da",
    "il documento dice che",
]


BAD_TEXT_REPLACEMENTS = [
    (r"\bperchè\b", "perché"),
    (r"\bqual e\b", "qual è"),
    (r"\bnon\s+non\b", "non"),
    (r"\s+([,.!?;:])", r"\1"),
    (r"\s{2,}", " "),
    (r"\bsì,\s+", ""),
]


def normalize_space_v1(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_key_v1(value: Any) -> str:
    text = normalize_space_v1(value).lower()
    text = text.strip(" .,:;!?")
    return text


def clean_text_v1(value: Any) -> str:
    text = str(value or "").strip()

    for pattern, replacement in BAD_TEXT_REPLACEMENTS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    text = normalize_space_v1(text)

    return text


def is_mechanical_question_v1(text: Any) -> bool:
    normalized = normalize_key_v1(text)

    return any(pattern in normalized for pattern in MECHANICAL_QUESTION_PATTERNS)


def question_key_v1(question: Dict[str, Any]) -> str:
    if "domanda" in question:
        return "domanda"

    if "question" in question:
        return "question"

    return "domanda"


def options_key_v1(question: Dict[str, Any]) -> str:
    if isinstance(question.get("opzioni"), list):
        return "opzioni"

    if isinstance(question.get("options"), list):
        return "options"

    return "opzioni"


def option_text_key_v1(option: Dict[str, Any]) -> str:
    if "testo" in option:
        return "testo"

    if "text" in option:
        return "text"

    return "testo"


def explanation_key_v1(question: Dict[str, Any]) -> str:
    if "spiegazione" in question:
        return "spiegazione"

    if "explanation" in question:
        return "explanation"

    if "explanation_draft" in question:
        return "explanation_draft"

    return "spiegazione"


def quiz_options_v1(question: Dict[str, Any]) -> List[Dict[str, Any]]:
    value = question.get(options_key_v1(question))

    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]

    return []


def question_text_v1(question: Dict[str, Any]) -> str:
    return str(question.get(question_key_v1(question)) or "")


def explanation_text_v1(question: Dict[str, Any]) -> str:
    for key in ["spiegazione", "explanation", "explanation_draft"]:
        value = question.get(key)

        if isinstance(value, str) and value.strip():
            return value

    return ""


def option_text_v1(option: Dict[str, Any]) -> str:
    return str(option.get(option_text_key_v1(option)) or "")


def is_correct_option_v1(option: Dict[str, Any], question: Dict[str, Any]) -> bool:
    if option.get("is_correct") is True:
        return True

    correct_option_id = question.get("correct_option_id")
    option_id = option.get("option_id")

    return bool(correct_option_id and option_id and correct_option_id == option_id)


def correct_option_text_v1(question: Dict[str, Any]) -> str:
    for option in quiz_options_v1(question):
        if is_correct_option_v1(option, question):
            return option_text_v1(option)

    return ""


def collect_source_facts_v1(question: Dict[str, Any]) -> List[str]:
    facts = question.get("source_facts")

    if isinstance(facts, list):
        return [clean_text_v1(item) for item in facts if str(item).strip()]

    return []


def best_fact_for_question_v1(question: Dict[str, Any]) -> str:
    facts = collect_source_facts_v1(question)

    if facts:
        return facts[0]

    correct = correct_option_text_v1(question)

    if correct:
        return correct

    return question_text_v1(question)


def concept_from_fact_v1(fact: str) -> str:
    text = clean_text_v1(fact).strip(". ")

    if not text:
        return "questo punto del documento"

    lowered = text.lower()

    if "controllo degli accessi" in lowered:
        return "controllo degli accessi"

    if "account" in lowered:
        return "account utente"

    if "credenziali" in lowered:
        return "credenziali"

    if "revisione periodica" in lowered or "accessi" in lowered:
        return "revisione periodica degli accessi"

    words = re.findall(r"[A-Za-zÀ-ÿ0-9']+", text)

    if len(words) >= 4:
        return " ".join(words[:4]).lower()

    return text.lower()


def natural_question_from_fact_v1(fact: str, index: int) -> str:
    text = clean_text_v1(fact).strip(". ")
    lowered = text.lower()

    if "controllo degli accessi" in lowered and "limita" in lowered:
        return "Quale funzione svolge il controllo degli accessi nei sistemi interni?"

    if "account" in lowered and "persona identificabile" in lowered:
        return "Perché ogni account deve essere associato a una persona identificabile?"

    if "credenziali" in lowered and "condivise" in lowered:
        return "Quale regola riguarda la condivisione delle credenziali?"

    if "revisione periodica" in lowered and "riduce il rischio" in lowered:
        return "Perché la revisione periodica degli accessi riduce il rischio?"

    concept = concept_from_fact_v1(text)

    templates = [
        "Che cosa chiarisce il documento su {concept}?",
        "Quale aspetto operativo riguarda {concept}?",
        "Perché è importante il punto relativo a {concept}?",
        "Quale indicazione pratica emerge su {concept}?",
    ]

    template = templates[index % len(templates)]

    return template.format(concept=concept)


def make_natural_explanation_v1(question: Dict[str, Any]) -> str:
    correct = clean_text_v1(correct_option_text_v1(question)).strip(". ")
    fact = clean_text_v1(best_fact_for_question_v1(question)).strip(". ")

    if not correct and fact:
        correct = fact

    if not correct:
        return "La risposta corretta riprende l'informazione centrale indicata dal documento."

    if fact and normalize_key_v1(fact) != normalize_key_v1(correct):
        return (
            f"La risposta corretta è “{correct}” perché è coerente con il fatto indicato "
            f"dal documento: “{fact}”."
        )

    return f"La risposta corretta è “{correct}” perché riprende direttamente l'informazione indicata dal documento."


def clean_question_fields_v1(question: Dict[str, Any]) -> Dict[str, Any]:
    fixed = copy.deepcopy(question)

    q_key = question_key_v1(fixed)
    fixed[q_key] = clean_text_v1(fixed.get(q_key))

    e_key = explanation_key_v1(fixed)
    fixed[e_key] = clean_text_v1(fixed.get(e_key))

    for option in quiz_options_v1(fixed):
        t_key = option_text_key_v1(option)
        option[t_key] = clean_text_v1(option.get(t_key))

    return fixed


def improve_question_text_v1(
    question: Dict[str, Any],
    *,
    index: int,
    seen_questions: set,
) -> Tuple[Dict[str, Any], bool]:
    fixed = copy.deepcopy(question)
    q_key = question_key_v1(fixed)
    original = str(fixed.get(q_key) or "")

    normalized_original = normalize_key_v1(original)

    should_rewrite = False

    if not original.strip():
        should_rewrite = True

    if is_mechanical_question_v1(original):
        should_rewrite = True

    if normalized_original in seen_questions:
        should_rewrite = True

    if should_rewrite:
        fact = best_fact_for_question_v1(fixed)
        fixed[q_key] = natural_question_from_fact_v1(fact, index)

    normalized_new = normalize_key_v1(fixed.get(q_key))

    if normalized_new in seen_questions:
        concept = concept_from_fact_v1(best_fact_for_question_v1(fixed))
        fixed[q_key] = f"Quale elemento specifico riguarda {concept}?"

    seen_questions.add(normalize_key_v1(fixed.get(q_key)))

    return fixed, normalize_key_v1(original) != normalize_key_v1(fixed.get(q_key))


def improve_explanation_v1(question: Dict[str, Any]) -> Tuple[Dict[str, Any], bool]:
    fixed = copy.deepcopy(question)
    e_key = explanation_key_v1(fixed)

    original = str(fixed.get(e_key) or "")
    normalized = normalize_key_v1(original)
    correct = normalize_key_v1(correct_option_text_v1(fixed))

    should_rewrite = False

    if not original.strip():
        should_rewrite = True

    if normalized == correct:
        should_rewrite = True

    if any(token in normalized for token in ["bozza", "draft", "macro-grezzo", "non non", "perchè", "qual e"]):
        should_rewrite = True

    if len(original.strip()) < 35:
        should_rewrite = True

    if should_rewrite:
        fixed[e_key] = make_natural_explanation_v1(fixed)
    else:
        fixed[e_key] = clean_text_v1(original)

    return fixed, normalize_key_v1(original) != normalize_key_v1(fixed.get(e_key))


def preserve_correctness_v1(
    before_question: Dict[str, Any],
    after_question: Dict[str, Any],
) -> Dict[str, Any]:
    fixed = copy.deepcopy(after_question)

    before_options = quiz_options_v1(before_question)
    after_options = quiz_options_v1(fixed)

    before_correct_id = before_question.get("correct_option_id")

    if before_correct_id:
        fixed["correct_option_id"] = before_correct_id

    for option in after_options:
        option_id = option.get("option_id")

        if before_correct_id and option_id:
            option["is_correct"] = option_id == before_correct_id

    # Se mancavano option_id o correct_option_id, preservo la posizione della corretta.
    if not before_correct_id:
        correct_indexes = [
            idx for idx, option in enumerate(before_options)
            if option.get("is_correct") is True
        ]

        if correct_indexes:
            correct_index = correct_indexes[0]

            for idx, option in enumerate(after_options):
                option["is_correct"] = idx == correct_index

    return fixed


def apply_universal_quiz_quality_v1(quiz: Any) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(quiz, list):
        return quiz, {
            "changed": False,
            "questions_seen": 0,
            "warnings": ["quiz_not_list"],
        }

    original_quiz = copy.deepcopy(quiz)
    working_quiz = copy.deepcopy(quiz)

    meta: Dict[str, Any] = {
        "changed": False,
        "questions_seen": len(working_quiz),
        "true_distractor_repair_applied": False,
        "true_distractor_repair_meta": None,
        "questions_rewritten": 0,
        "explanations_rewritten": 0,
        "text_cleaned_questions": 0,
        "warnings": [],
    }

    if repair_quiz_true_distractors_v1 is not None:
        try:
            repaired, repair_meta = repair_quiz_true_distractors_v1(working_quiz)
            working_quiz = repaired
            meta["true_distractor_repair_applied"] = True
            meta["true_distractor_repair_meta"] = repair_meta
            meta["changed"] = meta["changed"] or bool(repair_meta.get("changed"))
        except Exception as exc:  # pragma: no cover
            meta["warnings"].append(f"true_distractor_repair_failed:{type(exc).__name__}")

    seen_questions: set = set()
    final_quiz: List[Dict[str, Any]] = []

    for index, question in enumerate(working_quiz):
        if not isinstance(question, dict):
            final_quiz.append(question)
            continue

        before_question = copy.deepcopy(question)

        fixed = clean_question_fields_v1(question)

        if normalize_key_v1(str(fixed)) != normalize_key_v1(str(question)):
            meta["text_cleaned_questions"] += 1
            meta["changed"] = True

        fixed, question_changed = improve_question_text_v1(
            fixed,
            index=index,
            seen_questions=seen_questions,
        )

        if question_changed:
            meta["questions_rewritten"] += 1
            meta["changed"] = True

        fixed, explanation_changed = improve_explanation_v1(fixed)

        if explanation_changed:
            meta["explanations_rewritten"] += 1
            meta["changed"] = True

        fixed = preserve_correctness_v1(before_question, fixed)

        final_quiz.append(fixed)

    return final_quiz, meta


def quiz_keys_in_payload_v1(payload: Dict[str, Any]) -> List[str]:
    keys = []

    for key in ["test_quiz", "quiz_draft", "quiz", "domande_quiz", "tests"]:
        if isinstance(payload.get(key), list):
            keys.append(key)

    return keys


def apply_payload_universal_quiz_quality_v1(payload: Any) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(payload, dict):
        return payload, {
            "changed": False,
            "warnings": ["payload_not_dict"],
        }

    repaired = copy.deepcopy(payload)

    total_meta: Dict[str, Any] = {
        "changed": False,
        "keys_seen": [],
        "per_key": {},
        "warnings": [],
    }

    keys = quiz_keys_in_payload_v1(repaired)

    if not keys:
        total_meta["warnings"].append("no_quiz_key_found")
        return repaired, total_meta

    for key in keys:
        fixed_quiz, meta = apply_universal_quiz_quality_v1(repaired[key])
        repaired[key] = fixed_quiz

        total_meta["keys_seen"].append(key)
        total_meta["per_key"][key] = meta
        total_meta["changed"] = total_meta["changed"] or bool(meta.get("changed"))

    return repaired, total_meta


# Wrapper futuro per registry: riceve lista quiz e restituisce lista quiz.
def universal_quiz_quality_target_v1(quiz: Any) -> Any:
    fixed_quiz, _meta = apply_universal_quiz_quality_v1(quiz)
    return fixed_quiz


# Wrapper futuro per payload: utile nei test o in pipeline più ampia.
def universal_quiz_quality_payload_target_v1(payload: Any) -> Any:
    fixed_payload, _meta = apply_payload_universal_quiz_quality_v1(payload)
    return fixed_payload
