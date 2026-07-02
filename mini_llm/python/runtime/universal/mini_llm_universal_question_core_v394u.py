#!/usr/bin/env python3
"""
Mini LLM Universal Question Core V3.9.4U.1.

Core universale.
Non contiene vocabolari specialistici.

Fix:
- l'intento della domanda si riconosce dalla forma della domanda;
- non da parole casuali dentro i concetti specialistici;
- domande espanse più compatte.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Set


def normalize(text: Any) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").strip().split())


def tokenize(text: str) -> Set[str]:
    stop = {
        "quali", "sono", "cosa", "che", "devo", "vengono", "spiegati",
        "documento", "punti", "principali", "ricordare", "nel", "nella",
        "sul", "sulla", "di", "a", "da", "in", "con", "per", "e", "o",
        "il", "lo", "la", "gli", "le", "un", "una",
    }

    return {
        word
        for word in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", normalize(text).lower())
        if len(word) > 2 and word not in stop
    }


def classify_query(query: str) -> str:
    low = normalize(query).lower()

    # Intenzione per forma della domanda, non per parole dentro i concetti.
    if low.startswith("quali rischi") or low.startswith("quali problemi") or "criticità" in low:
        return "risks"

    if low.startswith("quali sono i punti principali") or low.startswith("quali punti principali"):
        return "main_points"

    if low.startswith("che cosa devo ricordare") or low.startswith("cosa devo ricordare"):
        return "study_memory"

    if low.startswith("fammi una sintesi") or "riassunto" in low or "panoramica" in low:
        return "summary"

    if low.startswith("come ") and any(marker in low for marker in ["fare", "funziona", "applicare", "usare"]):
        return "procedure"

    if low.startswith("che cos") or "definizione" in low or "significa" in low:
        return "definition"

    # Fallback meno aggressivo.
    if "risch" in low or "problemi" in low or "pericol" in low or "minacc" in low:
        return "risks"

    if "punti principali" in low:
        return "main_points"

    if "ricordare" in low or "studiare" in low:
        return "study_memory"

    return "generic"


def is_generic_query(query: str) -> bool:
    low = normalize(query).lower()

    generic_markers = [
        "nel documento",
        "punti principali",
        "quali rischi",
        "quali problemi",
        "cosa devo ricordare",
        "che cosa spiega",
        "quali concetti",
        "fammi una sintesi",
    ]

    if len(tokenize(query)) <= 3:
        return True

    return any(marker in low for marker in generic_markers)


def choose_concepts(profile: Dict[str, Any], query_type: str, max_items: int | None = None) -> List[str]:
    key_by_type = {
        "risks": "risk_concepts",
        "main_points": "main_concepts",
        "study_memory": "memory_concepts",
        "summary": "main_concepts",
        "procedure": "procedure_concepts",
        "definition": "core_concepts",
        "generic": "core_concepts",
    }

    if max_items is None:
        # Le domande devono restare leggibili.
        max_items = 5 if query_type == "risks" else 6

    key = key_by_type.get(query_type, "core_concepts")
    values = list(profile.get(key, []) or [])

    if not values:
        values = list(profile.get("core_concepts", []) or [])

    if not values:
        values = [str(profile.get("domain_name", "contenuto del documento"))]

    unique = []
    seen = set()

    for value in values:
        clean = normalize(value)

        if not clean:
            continue

        lower = clean.lower()

        if lower in seen:
            continue

        seen.add(lower)
        unique.append(clean)

        if len(unique) >= max_items:
            break

    return unique


def join_concepts(concepts: List[str]) -> str:
    if not concepts:
        return ""

    if len(concepts) == 1:
        return concepts[0]

    return ", ".join(concepts[:-1]) + " e " + concepts[-1]


def expand_query(query: str, profile: Dict[str, Any]) -> Dict[str, Any]:
    original = normalize(query)
    qtype = classify_query(original)
    domain = normalize(profile.get("domain_name", "contenuto del documento"))
    concepts = choose_concepts(profile, qtype)

    if not domain:
        domain = "contenuto del documento"

    if qtype == "risks":
        expanded = (
            f"Quali rischi o criticità di {domain}, "
            f"legati a {join_concepts(concepts)}, vengono spiegati?"
        )

    elif qtype == "main_points":
        expanded = (
            f"Quali sono i punti principali su {domain}, "
            f"in particolare {join_concepts(concepts)}?"
        )

    elif qtype == "study_memory":
        expanded = (
            f"Che cosa devo ricordare su {domain}, "
            f"in particolare {join_concepts(concepts)}?"
        )

    elif qtype == "summary":
        expanded = (
            f"Fammi una sintesi chiara su {domain}, "
            f"evidenziando {join_concepts(concepts)}."
        )

    elif qtype == "procedure":
        expanded = (
            f"Come si applicano nel contesto di {domain} i passaggi legati a "
            f"{join_concepts(concepts)}?"
        )

    elif qtype == "definition":
        expanded = (
            f"Che cosa significa nel contesto di {domain} il concetto richiesto, "
            f"considerando {join_concepts(concepts)}?"
        )

    else:
        if is_generic_query(original):
            expanded = (
                f"{original} Rispondi nel contesto di {domain}, "
                f"considerando {join_concepts(concepts)}."
            )
        else:
            expanded = original

    return {
        "original_query": original,
        "expanded_query": expanded,
        "query_type": qtype,
        "changed": expanded != original,
        "document_domain": domain,
        "concepts_used": concepts,
        "reason": "Domanda contestualizzata con dominio e concetti specialistici forniti dal profilo.",
    }


def expand_queries(queries: List[str], profile: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "core": "mini_llm_universal_question_core_v394u",
        "version": "V3.9.4U.1",
        "profile_id": profile.get("profile_id"),
        "document_domain": profile.get("domain_name"),
        "queries": [expand_query(query, profile) for query in queries],
        "limits": [
            "Core universale.",
            "Non contiene vocabolario specialistico.",
            "Usa concetti forniti dal profilo di dominio.",
        ],
    }
