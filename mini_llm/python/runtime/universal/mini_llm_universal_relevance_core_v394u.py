#!/usr/bin/env python3
"""
Mini LLM Universal Relevance Core V3.9.4U.1.

Core universale.
Non contiene dizionari specialistici.

Usa:
- core domande universale;
- core linguistico universale;
- profili specialistici esterni.
"""

from __future__ import annotations

from typing import Any, Dict, List, Set

from mini_llm.python.runtime.universal.mini_llm_universal_question_core_v394u import (
    classify_query,
    choose_concepts,
)
from mini_llm.python.runtime.universal.mini_llm_universal_linguistic_core_v394u import (
    normalize,
    split_sentences,
    tokenize,
    is_safe_sentence,
)


def profile_tokens(profile: Dict[str, Any], query_type: str) -> Set[str]:
    tokens = set()

    for concept in choose_concepts(profile, query_type, max_items=10):
        tokens.update(tokenize(concept))

    tokens.update(tokenize(str(profile.get("domain_name", ""))))

    return tokens


def score_sentence(expanded_query: str, sentence: str, profile: Dict[str, Any]) -> float:
    qtype = classify_query(expanded_query)
    q_tokens = tokenize(expanded_query)
    s_tokens = tokenize(sentence)
    p_tokens = profile_tokens(profile, qtype)

    score = 0.0
    score += len(q_tokens.intersection(s_tokens)) * 3.0
    score += len(p_tokens.intersection(s_tokens)) * 4.0

    low = normalize(sentence).lower()

    if any(marker in low for marker in ["è", "sono", "serve", "permette", "riduce", "protegge", "migliora", "spiega"]):
        score += 1.0

    if normalize(sentence).startswith(("Bisogna ", "Serve ", "Può ", "Quando ")):
        score -= 1.0

    return score


def lead_sentence(expanded_query: str, selected_sentences: List[str], profile: Dict[str, Any]) -> str:
    qtype = classify_query(expanded_query)
    domain = normalize(profile.get("domain_name", "contenuto del documento"))
    concepts = choose_concepts(profile, qtype, max_items=5)
    joined = ", ".join(concepts)

    if qtype == "risks":
        return (
            f"I rischi o le criticità di {domain} spiegati nel documento "
            f"riguardano {joined}."
        )

    if qtype == "main_points":
        return (
            f"I punti principali del documento riguardano {domain}, "
            f"con attenzione a {joined}."
        )

    if qtype == "study_memory":
        return (
            f"Su {domain}, il documento richiama concetti e comportamenti da ricordare "
            f"come {joined}."
        )

    if qtype == "summary":
        return (
            f"La sintesi del documento su {domain} riguarda soprattutto {joined}."
        )

    if qtype == "procedure":
        return (
            f"Nel contesto di {domain}, i passaggi operativi riguardano {joined}."
        )

    if qtype == "definition":
        return (
            f"Nel contesto di {domain}, la definizione richiesta va collegata a {joined}."
        )

    return f"Nel contesto di {domain}, la risposta riguarda {joined}."


def build_answer(
    original_query: str,
    expanded_query: str,
    document_text: str,
    profile: Dict[str, Any],
    max_sentences: int = 3,
) -> Dict[str, Any]:
    candidates = [
        sentence
        for sentence in split_sentences(document_text)
        if is_safe_sentence(sentence, profile)
    ]

    ranked = []

    for sentence in candidates:
        score = score_sentence(expanded_query, sentence, profile)

        if score > 0:
            ranked.append((score, sentence))

    ranked.sort(key=lambda item: item[0], reverse=True)

    selected = []
    seen = set()

    for _, sentence in ranked:
        key = normalize(sentence).lower()

        if key in seen:
            continue

        seen.add(key)
        selected.append(sentence)

        if len(selected) >= max_sentences:
            break

    if not selected:
        selected = candidates[:max_sentences]

    lead = lead_sentence(expanded_query, selected, profile)
    answer = " ".join([lead] + selected)

    return {
        "status": "OK" if selected else "EMPTY",
        "query": original_query,
        "expanded_query": expanded_query,
        "answer": answer,
        "sentences_used": len(selected) + 1,
        "quality_errors": [],
        "relevance": {
            "profile_id": profile.get("profile_id"),
            "domain_name": profile.get("domain_name"),
            "query_type": classify_query(expanded_query),
        },
        "limits": [
            "Pertinenza universale.",
            "Concetti specialistici forniti dal profilo.",
            "Nessun fix su domanda singola.",
        ],
    }


def validate_answer_relevance(answer_row: Dict[str, Any], profile: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    original = normalize(answer_row.get("query", ""))
    expanded = normalize(answer_row.get("expanded_query", ""))
    answer = normalize(answer_row.get("answer", ""))

    if not expanded or expanded == original:
        errors.append(f"query_not_contextualized:{original}")

    if not answer:
        errors.append("answer_empty")
        return errors

    qtype = classify_query(expanded)
    domain = normalize(profile.get("domain_name", "")).lower()

    if domain and domain not in answer.lower():
        errors.append(f"answer_missing_domain:{domain}:{answer[:160]}")

    concepts = choose_concepts(profile, qtype, max_items=6)
    low = answer.lower()
    concept_hits = 0

    for concept in concepts:
        if normalize(concept).lower() in low:
            concept_hits += 1

    if concept_hits < 1:
        errors.append(f"answer_missing_profile_concepts:{concepts}:{answer[:160]}")

    if qtype == "risks" and not answer.lower().startswith("i rischi o le criticità"):
        errors.append(f"risk_answer_not_anchored:{answer[:160]}")

    if qtype == "main_points" and not answer.lower().startswith("i punti principali del documento"):
        errors.append(f"main_points_answer_not_anchored:{answer[:160]}")

    if qtype == "study_memory" and not answer.lower().startswith("su "):
        errors.append(f"study_memory_answer_not_anchored:{answer[:160]}")

    return errors


def validate_report(report: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []

    for index, answer in enumerate(report.get("answers", []), start=1):
        for error in validate_answer_relevance(answer, profile):
            errors.append(f"answer_{index}:{error}")

    return {
        "core": "mini_llm_universal_relevance_core_v394u",
        "version": "V3.9.4U.1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "profile_id": profile.get("profile_id"),
        "domain_name": profile.get("domain_name"),
        "limits": [
            "Gate universale di pertinenza.",
            "Usa profilo esterno.",
            "Non contiene dizionari specialistici interni.",
        ],
    }
