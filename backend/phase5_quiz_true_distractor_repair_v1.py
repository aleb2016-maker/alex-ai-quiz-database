from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Optional, Set, Tuple


# FASE 5.9.2 — QUIZ TRUE DISTRACTOR REPAIR V1
#
# Motore separato, non ancora collegato al registry.
# Scopo:
# - riconoscere distrattori marcati falsi che però coincidono con source_facts veri;
# - sostituirli con distrattori falsi plausibili;
# - preservare risposta corretta, option_id, numero opzioni e struttura quiz.
#
# Limite:
# - deterministico, locale, senza AI/API;
# - funziona soprattutto quando il distrattore falso coincide testualmente con un source_fact.


FALSE_DISTRACTOR_BANK: List[str] = [
    "Le credenziali possono essere condivise liberamente tra più operatori se il sistema è interno.",
    "La revisione periodica degli accessi può essere evitata quando gli account sono già attivi.",
    "Ogni account può restare anonimo se viene usato solo da personale autorizzato.",
    "I permessi attivi non richiedono controlli quando l'utente ha già lavorato sull'applicazione.",
    "Il controllo degli accessi serve solo a registrare gli utenti, non a limitare l'utilizzo dei sistemi.",
    "Le credenziali possono essere archiviate in documenti condivisi se il gruppo è ristretto.",
    "Gli account non devono essere associati a persone identificabili quando l'accesso è frequente.",
    "La revisione degli accessi aumenta il rischio perché mantiene permessi non autorizzati.",
    "I sistemi interni possono essere usati senza controllo quando l'operatore conosce la procedura.",
    "La protezione delle credenziali riguarda solo la lunghezza della password, non la condivisione.",
]


def normalize_text_v1(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip(" .,:;!?")


def option_text_key_v1(option: Dict[str, Any]) -> str:
    if "testo" in option:
        return "testo"

    if "text" in option:
        return "text"

    return "testo"


def options_key_v1(question: Dict[str, Any]) -> str:
    if isinstance(question.get("opzioni"), list):
        return "opzioni"

    if isinstance(question.get("options"), list):
        return "options"

    return "opzioni"


def is_option_correct_v1(option: Dict[str, Any], question: Dict[str, Any]) -> bool:
    if option.get("is_correct") is True:
        return True

    correct_option_id = question.get("correct_option_id")
    option_id = option.get("option_id")

    return bool(correct_option_id and option_id and correct_option_id == option_id)


def collect_source_facts_v1(
    question: Dict[str, Any],
    global_source_facts: Optional[List[str]] = None,
) -> List[str]:
    facts: List[str] = []

    for value in question.get("source_facts") or []:
        if str(value).strip():
            facts.append(str(value).strip())

    for value in global_source_facts or []:
        if str(value).strip():
            facts.append(str(value).strip())

    return facts


def is_true_fact_distractor_v1(
    *,
    option: Dict[str, Any],
    question: Dict[str, Any],
    source_facts: List[str],
) -> bool:
    if is_option_correct_v1(option, question):
        return False

    text_key = option_text_key_v1(option)
    option_norm = normalize_text_v1(option.get(text_key))

    if not option_norm:
        return False

    source_norm = {
        normalize_text_v1(fact)
        for fact in source_facts
        if normalize_text_v1(fact)
    }

    return option_norm in source_norm


def existing_option_texts_v1(question: Dict[str, Any]) -> Set[str]:
    key = options_key_v1(question)
    options = question.get(key) or []

    out: Set[str] = set()

    if not isinstance(options, list):
        return out

    for option in options:
        if not isinstance(option, dict):
            continue

        text_key = option_text_key_v1(option)
        norm = normalize_text_v1(option.get(text_key))

        if norm:
            out.add(norm)

    return out


def choose_replacement_distractor_v1(
    *,
    source_facts: List[str],
    already_used: Set[str],
) -> str:
    source_norm = {
        normalize_text_v1(fact)
        for fact in source_facts
        if normalize_text_v1(fact)
    }

    for candidate in FALSE_DISTRACTOR_BANK:
        candidate_norm = normalize_text_v1(candidate)

        if not candidate_norm:
            continue

        if candidate_norm in source_norm:
            continue

        if candidate_norm in already_used:
            continue

        already_used.add(candidate_norm)
        return candidate

    fallback_index = 1

    while True:
        candidate = (
            "Il documento indica che il controllo può essere ignorato senza conseguenze operative "
            f"nel caso {fallback_index}."
        )

        candidate_norm = normalize_text_v1(candidate)

        if candidate_norm not in source_norm and candidate_norm not in already_used:
            already_used.add(candidate_norm)
            return candidate

        fallback_index += 1


def count_true_fact_distractors_v1(
    quiz: Any,
    global_source_facts: Optional[List[str]] = None,
) -> int:
    if not isinstance(quiz, list):
        return 0

    count = 0

    for question in quiz:
        if not isinstance(question, dict):
            continue

        key = options_key_v1(question)
        options = question.get(key) or []

        if not isinstance(options, list):
            continue

        source_facts = collect_source_facts_v1(question, global_source_facts)

        for option in options:
            if not isinstance(option, dict):
                continue

            if is_true_fact_distractor_v1(
                option=option,
                question=question,
                source_facts=source_facts,
            ):
                count += 1

    return count


def repair_quiz_true_distractors_v1(
    quiz: Any,
    *,
    global_source_facts: Optional[List[str]] = None,
) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(quiz, list):
        return quiz, {
            "changed": False,
            "questions_seen": 0,
            "replaced_distractors_count": 0,
            "before_true_fact_distractors": 0,
            "after_true_fact_distractors": 0,
            "replacements": [],
            "warnings": ["quiz_not_list"],
        }

    repaired = copy.deepcopy(quiz)
    before_risk = count_true_fact_distractors_v1(repaired, global_source_facts)

    replacements: List[Dict[str, Any]] = []

    for question_index, question in enumerate(repaired):
        if not isinstance(question, dict):
            continue

        key = options_key_v1(question)
        options = question.get(key) or []

        if not isinstance(options, list):
            continue

        source_facts = collect_source_facts_v1(question, global_source_facts)
        already_used = existing_option_texts_v1(question)

        for option_index, option in enumerate(options):
            if not isinstance(option, dict):
                continue

            if not is_true_fact_distractor_v1(
                option=option,
                question=question,
                source_facts=source_facts,
            ):
                continue

            text_key = option_text_key_v1(option)
            old_text = str(option.get(text_key) or "")

            already_used.discard(normalize_text_v1(old_text))

            new_text = choose_replacement_distractor_v1(
                source_facts=source_facts,
                already_used=already_used,
            )

            option[text_key] = new_text
            option["is_correct"] = False

            replacements.append(
                {
                    "question_index": question_index,
                    "option_index": option_index,
                    "option_id": option.get("option_id"),
                    "old_text": old_text,
                    "new_text": new_text,
                }
            )

    after_risk = count_true_fact_distractors_v1(repaired, global_source_facts)

    meta = {
        "changed": bool(replacements),
        "questions_seen": len(repaired),
        "replaced_distractors_count": len(replacements),
        "before_true_fact_distractors": before_risk,
        "after_true_fact_distractors": after_risk,
        "replacements": replacements,
        "warnings": [],
    }

    if after_risk > before_risk:
        meta["warnings"].append("risk_increased")

    return repaired, meta


def repair_payload_quiz_true_distractors_v1(payload: Any) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(payload, dict):
        return payload, {
            "changed": False,
            "keys_seen": [],
            "replaced_distractors_count": 0,
            "before_true_fact_distractors": 0,
            "after_true_fact_distractors": 0,
            "per_key": {},
            "warnings": ["payload_not_dict"],
        }

    repaired = copy.deepcopy(payload)

    quiz_keys = [
        "test_quiz",
        "quiz_draft",
        "quiz",
        "domande_quiz",
        "tests",
    ]

    total_meta: Dict[str, Any] = {
        "changed": False,
        "keys_seen": [],
        "replaced_distractors_count": 0,
        "before_true_fact_distractors": 0,
        "after_true_fact_distractors": 0,
        "per_key": {},
        "replacements": [],
        "warnings": [],
    }

    global_source_facts: List[str] = []

    for key in ["source_facts", "global_source_facts"]:
        values = repaired.get(key)

        if isinstance(values, list):
            global_source_facts.extend(
                str(value)
                for value in values
                if str(value).strip()
            )

    for key in quiz_keys:
        value = repaired.get(key)

        if not isinstance(value, list):
            continue

        fixed_quiz, meta = repair_quiz_true_distractors_v1(
            value,
            global_source_facts=global_source_facts,
        )

        repaired[key] = fixed_quiz

        total_meta["keys_seen"].append(key)
        total_meta["changed"] = total_meta["changed"] or meta["changed"]
        total_meta["replaced_distractors_count"] += meta["replaced_distractors_count"]
        total_meta["before_true_fact_distractors"] += meta["before_true_fact_distractors"]
        total_meta["after_true_fact_distractors"] += meta["after_true_fact_distractors"]
        for replacement in meta.get("replacements", []):
            enriched = dict(replacement)
            enriched["quiz_key"] = key
            total_meta["replacements"].append(enriched)

        total_meta["per_key"][key] = meta

    if not total_meta["keys_seen"]:
        total_meta["warnings"].append("no_quiz_key_found")

    return repaired, total_meta
