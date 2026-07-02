#!/usr/bin/env python3
"""
Mini LLM Universal Linguistic Core V3.9.4U.1.

Core universale.
Non contiene vocabolari specialistici.

Responsabilità:
- grammatica minima;
- frasi concluse;
- soggetto/riferimento chiaro;
- domande contestualizzate ma non troppo lunghe;
- niente fix su domanda singola.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set


BAD_STARTS = {
    "al", "allo", "alla", "agli", "alle", "della", "dello", "delle",
    "degli", "dei", "del", "pagina", "e", "o", "ma", "con", "per",
}


BAD_ENDINGS = {
    "al", "allo", "alla", "agli", "alle", "a", "di", "del", "della",
    "dello", "delle", "e", "o", "ma", "che", "con", "per", "tra",
    "fra", "cui",
}


GENERIC_FLOATING_STARTS = {
    "bisogna",
    "serve",
    "può",
    "possono",
    "quando",
    "questo",
    "questa",
    "ciò",
    "esso",
    "essa",
}


QUESTION_WORDS = {
    "che",
    "cosa",
    "quale",
    "quali",
    "quando",
    "dove",
    "come",
    "perché",
    "quanto",
    "quanti",
}


def normalize(text: Any) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").strip().split())


def split_sentences(text: str) -> List[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", normalize(text))
        if sentence.strip()
    ]


def tokenize(text: str) -> Set[str]:
    return {
        word
        for word in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", normalize(text).lower())
        if len(word) > 2
    }


def first_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return re.sub(r"^[\"'“”‘’(\[]+", "", words[0]).lower().strip(".,;:!?")


def last_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return words[-1].lower().strip(".,;:!?\"'“”‘’)]}")


def profile_concepts(profile: Dict[str, Any]) -> Set[str]:
    concepts = set()

    for key in [
        "core_concepts",
        "risk_concepts",
        "main_concepts",
        "memory_concepts",
        "procedure_concepts",
    ]:
        for item in profile.get(key, []) or []:
            concepts.update(tokenize(str(item)))

    concepts.update(tokenize(str(profile.get("domain_name", ""))))

    return concepts


def has_domain_reference(text: str, profile: Dict[str, Any]) -> bool:
    value = normalize(text).lower()

    if not value:
        return False

    domain_name = str(profile.get("domain_name", "")).lower()

    if domain_name and domain_name in value:
        return True

    concepts = profile_concepts(profile)
    tokens = tokenize(value)

    return len(tokens.intersection(concepts)) >= 1


def has_clear_subject_or_reference(sentence: str, profile: Dict[str, Any]) -> bool:
    value = normalize(sentence)

    if not value:
        return False

    fw = first_word(value)

    if fw in GENERIC_FLOATING_STARTS:
        return has_domain_reference(value, profile)

    if has_domain_reference(value, profile):
        return True

    if re.match(r"^(Il|La|I|Gli|Le|Un|Una|L'|Lo)\s+[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", value):
        return True

    return False


def check_sentence(sentence: str, profile: Dict[str, Any] | None = None) -> List[str]:
    errors: List[str] = []
    profile = profile or {}
    value = normalize(sentence)

    if not value:
        errors.append("sentence_empty")
        return errors

    words = value.split()

    if len(words) < 5:
        errors.append(f"sentence_too_short:{value[:120]}")

    if len(words) > 45:
        errors.append(f"sentence_too_long:{value[:120]}")

    if first_word(value) in BAD_STARTS:
        errors.append(f"sentence_bad_start:{value[:120]}")

    if last_word(value) in BAD_ENDINGS:
        errors.append(f"sentence_bad_ending:{value[:120]}")

    if not re.search(r"[.!?]$", value):
        errors.append(f"sentence_not_closed:{value[:120]}")

    if "#" in value or re.search(r"(^|\s)[*_`]{1,3}", value):
        errors.append(f"sentence_contains_markup:{value[:120]}")

    if re.search(r"\b([a-zà-öø-ÿ]{4,})\s+(Il|La|I|Gli|Le|Un|Una|L')\b", value):
        errors.append(f"sentence_probably_fused:{value[:120]}")

    if not has_clear_subject_or_reference(value, profile):
        errors.append(f"sentence_missing_clear_reference:{value[:120]}")

    return errors


def check_text(text: str, profile: Dict[str, Any] | None = None) -> List[str]:
    errors: List[str] = []

    for index, sentence in enumerate(split_sentences(text), start=1):
        for error in check_sentence(sentence, profile):
            errors.append(f"sentence_{index}:{error}")

    return errors


def check_question(question: str, profile: Dict[str, Any] | None = None) -> List[str]:
    errors: List[str] = []
    profile = profile or {}
    value = normalize(question)

    if not value:
        errors.append("question_empty")
        return errors

    words = value.split()

    if not value.endswith("?"):
        errors.append(f"question_missing_mark:{value[:120]}")

    if len(words) < 5:
        errors.append(f"question_too_short:{value[:120]}")

    # Domande contestualizzate possono essere un po' più lunghe,
    # ma non devono diventare muri di testo.
    if len(words) > 34:
        errors.append(f"question_too_long:{value[:180]}")

    if first_word(value) not in QUESTION_WORDS:
        errors.append(f"question_weak_start:{value[:120]}")

    if not has_domain_reference(value, profile):
        errors.append(f"question_missing_domain_context:{value[:160]}")

    return errors


def is_safe_sentence(sentence: str, profile: Dict[str, Any] | None = None) -> bool:
    return not check_sentence(sentence, profile)


def quality_report(text: str, profile: Dict[str, Any] | None = None) -> Dict[str, Any]:
    errors = check_text(text, profile)

    return {
        "core": "mini_llm_universal_linguistic_core_v394u",
        "version": "V3.9.4U.1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "sentences": len(split_sentences(text)),
        "limits": [
            "Core universale.",
            "Nessun vocabolario specialistico interno.",
            "I concetti di dominio arrivano dai profili separati.",
        ],
    }
