#!/usr/bin/env python3
"""
Mini LLM Query Context Expander V3.9.4.

Migliora domande generiche aggiungendo:
- dominio del documento;
- concetti principali;
- contesto utile per persona e macchina.

Fix:
- le domande sui "punti principali" hanno priorità su "sicurezza informatica";
- così non vengono confuse con domande di memoria/studio.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List, Set


SECURITY_CONCEPTS = [
    "sicurezza informatica",
    "phishing",
    "ransomware",
    "malware",
    "password",
    "password deboli",
    "credenziali",
    "backup",
    "autenticazione a due fattori",
    "2FA",
    "account",
    "dati sensibili",
    "reti pubbliche",
    "procedure interne",
    "formazione del personale",
]


RISK_CONCEPTS = [
    "phishing",
    "ransomware",
    "malware",
    "password deboli",
    "credenziali",
    "dati sensibili",
    "reti pubbliche",
    "accessi non autorizzati",
    "furto",
    "cancellazione accidentale",
    "guasto",
]


GENERIC_PATTERNS = [
    r"\bnel documento\b",
    r"\bpunti principali\b",
    r"\brischi\b",
    r"\bcosa devo ricordare\b",
    r"\bche cosa spiega\b",
    r"\bquali concetti\b",
]


def normalize(text: Any) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").strip().split())


def tokenize(text: str) -> Set[str]:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", normalize(text).lower())
    stop = {
        "quali", "sono", "cosa", "che", "devo", "vengono", "spiegati",
        "documento", "punti", "principali", "ricordare", "nel", "nella",
        "sul", "sulla", "di", "a", "da", "in", "con", "per", "e", "o",
        "il", "lo", "la", "gli", "le", "un", "una",
    }
    return {word for word in words if len(word) > 2 and word not in stop}


def detect_document_domain(text: str) -> Dict[str, object]:
    low = normalize(text).lower()

    scores = {
        "sicurezza informatica aziendale": 0,
        "documento formativo": 0,
        "generico": 0,
    }

    for marker in [
        "sicurezza informatica",
        "phishing",
        "ransomware",
        "malware",
        "password",
        "credenziali",
        "backup",
        "2fa",
        "account",
        "dati sensibili",
    ]:
        if marker in low:
            scores["sicurezza informatica aziendale"] += 1

    for marker in ["formazione", "studiare", "concetti", "procedura"]:
        if marker in low:
            scores["documento formativo"] += 1

    domain = max(scores, key=scores.get)

    if scores[domain] == 0:
        domain = "generico"

    concepts = []

    for concept in SECURITY_CONCEPTS:
        if concept.lower() in low:
            concepts.append(concept)

    if "2FA" in concepts and "autenticazione a due fattori" not in concepts:
        concepts.append("autenticazione a due fattori")

    unique_concepts = []
    seen = set()

    for concept in concepts:
        key = concept.lower()
        if key not in seen:
            seen.add(key)
            unique_concepts.append(concept)

    return {
        "domain": domain,
        "domain_score": scores.get(domain, 0),
        "concepts": unique_concepts[:12],
        "risk_concepts": [
            concept for concept in RISK_CONCEPTS
            if concept.lower() in low
        ][:10],
    }


def query_type(query: str) -> str:
    low = normalize(query).lower()

    # Ordine importante:
    # prima i tipi specifici, poi il dominio.
    if "risch" in low or "pericol" in low or "minacc" in low:
        return "risks"

    if "punti principali" in low or "principali" in low:
        return "main_points"

    if "ricordare" in low or "studiare" in low or "concetti" in low:
        return "study_memory"

    if "sintesi" in low or "riassunto" in low:
        return "summary"

    if "sicurezza informatica" in low:
        return "security_memory"

    return "generic"


def is_generic_query(query: str) -> bool:
    low = normalize(query).lower()

    if len(tokenize(query)) <= 3:
        return True

    return any(re.search(pattern, low) for pattern in GENERIC_PATTERNS)


def join_concepts(concepts: List[str], fallback: List[str], max_items: int = 7) -> str:
    values = concepts[:max_items] if concepts else fallback[:max_items]

    if not values:
        return ""

    if len(values) == 1:
        return values[0]

    return ", ".join(values[:-1]) + " e " + values[-1]


def expand_query(query: str, document_context: Dict[str, object]) -> Dict[str, object]:
    original = normalize(query)
    qtype = query_type(original)
    domain = str(document_context.get("domain") or "generico")
    concepts = list(document_context.get("concepts") or [])
    risk_concepts = list(document_context.get("risk_concepts") or [])

    if domain == "generico":
        return {
            "original_query": original,
            "expanded_query": original,
            "query_type": qtype,
            "changed": False,
            "reason": "Dominio non rilevato con sicurezza.",
            "document_domain": domain,
            "concepts_used": [],
        }

    if qtype == "risks":
        used = risk_concepts or [
            "phishing",
            "ransomware",
            "password deboli",
            "credenziali",
            "malware",
            "backup",
            "reti pubbliche",
        ]

        expanded = (
            f"Quali rischi di {domain} legati a "
            f"{join_concepts(used, used)} vengono spiegati nel documento?"
        )

    elif qtype == "main_points":
        used = concepts or [
            "sicurezza informatica",
            "password",
            "phishing",
            "backup",
            "malware",
            "ransomware",
            "autenticazione",
        ]

        expanded = (
            f"Quali sono i punti principali del documento su {domain}, "
            f"in particolare {join_concepts(used, used)}?"
        )

    elif qtype in {"study_memory", "security_memory"}:
        used = concepts or [
            "sicurezza informatica",
            "password",
            "phishing",
            "backup",
            "credenziali",
            "ransomware",
        ]

        expanded = (
            f"Che cosa devo ricordare su {domain}, "
            f"in particolare {join_concepts(used, used)}?"
        )

    elif qtype == "summary":
        used = concepts or [
            "sicurezza informatica",
            "password",
            "phishing",
            "backup",
        ]

        expanded = (
            f"Fammi una sintesi utile del documento su {domain}, "
            f"evidenziando {join_concepts(used, used)}."
        )

    else:
        if is_generic_query(original):
            used = concepts or [
                "sicurezza informatica",
                "password",
                "phishing",
                "backup",
            ]

            expanded = (
                f"{original} Rispondi nel contesto di {domain}, "
                f"considerando {join_concepts(used, used)}."
            )
        else:
            expanded = original

    return {
        "original_query": original,
        "expanded_query": expanded,
        "query_type": qtype,
        "changed": expanded != original,
        "reason": "Domanda contestualizzata con dominio e concetti del documento." if expanded != original else "Domanda già abbastanza specifica.",
        "document_domain": domain,
        "concepts_used": risk_concepts if qtype == "risks" else concepts,
    }


def expand_queries(queries: List[str], document_text: str) -> Dict[str, object]:
    context = detect_document_domain(document_text)

    return {
        "expander": "mini_llm_query_context_expander_v394",
        "document_context": context,
        "queries": [
            expand_query(query, context)
            for query in queries
        ],
        "limits": [
            "Espansione deterministica.",
            "Non inventa contenuti fuori dal documento.",
            "Serve a migliorare domanda, retrieval e comprensione umana.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Espande domande generiche con contesto documento.")
    parser.add_argument("document_text_file")
    parser.add_argument("--query", action="append", required=True)
    parser.add_argument("--out", default="")
    args = parser.parse_args()

    path = Path(args.document_text_file).expanduser().resolve()

    if not path.exists():
        print(json.dumps({"status": "ERROR", "error": f"File non trovato: {path}"}, ensure_ascii=False, indent=2))
        return 1

    text = path.read_text(encoding="utf-8")
    result = expand_queries(args.query, text)

    output = json.dumps(result, ensure_ascii=False, indent=2)
    print(output)

    if args.out:
        out = Path(args.out).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(output + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
