#!/usr/bin/env python3
"""
Mini LLM Universal LLM Bridge V3.9.5.

Scopo:
- collegare il lavoro V3.9.4U al flusso LLM/RAG;
- usare il core universale per lingua, domande e pertinenza;
- usare profili specialistici separati per dominio e vocabolario;
- evitare fix su singola domanda o singola risposta.

Questo modulo NON contiene vocabolari specialistici.
I profili stanno in mini_llm/python/runtime/domain_profiles/.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from mini_llm.python.runtime.domain_profiles.mini_llm_domain_profile_registry_v394u import detect_profile
from mini_llm.python.runtime.universal.mini_llm_universal_question_core_v394u import expand_queries
from mini_llm.python.runtime.universal.mini_llm_universal_relevance_core_v394u import (
    build_answer,
    validate_report,
)
from mini_llm.python.runtime.universal.mini_llm_universal_linguistic_core_v394u import (
    normalize,
    check_text,
)


DEFAULT_QUERIES = [
    "Quali sono i punti principali del documento?",
    "Che cosa devo ricordare?",
    "Quali rischi o problemi vengono spiegati nel documento?",
]


class MiniLLMUniversalLLMBridgeV395:
    """
    Bridge universale per interrogare un documento.

    Input:
    - testo del documento;
    - lista domande opzionali.

    Output:
    - profilo rilevato;
    - domande contestualizzate;
    - risposte con contesto;
    - gate linguistico;
    - gate pertinenza.
    """

    def __init__(self, document_text: str):
        self.document_text = normalize(document_text)
        self.profile = detect_profile(self.document_text)

    def diagnostics(self) -> Dict[str, Any]:
        words = self.document_text.split()

        return {
            "engine": "mini_llm_universal_llm_bridge_v395",
            "status": "OK" if self.document_text else "EMPTY",
            "words": len(words),
            "chars": len(self.document_text),
            "profile_id": self.profile.get("profile_id"),
            "domain_name": self.profile.get("domain_name"),
            "detection_score": self.profile.get("detection_score"),
            "architecture": {
                "universal_core": [
                    "linguistic_core",
                    "question_core",
                    "relevance_core",
                ],
                "domain_profiles": "separated",
            },
            "limits": [
                "Bridge universale V3.9.5.",
                "Non è ancora LLM neurale generativo.",
                "Non contiene vocabolari specialistici nel core.",
                "Usa profili separati.",
            ],
        }

    def answer_queries(self, queries: List[str] | None = None) -> Dict[str, Any]:
        start = time.perf_counter()

        selected_queries = queries or DEFAULT_QUERIES
        expansion = expand_queries(selected_queries, self.profile)

        answers = []

        for row in expansion.get("queries", []):
            answers.append(
                build_answer(
                    row.get("original_query", ""),
                    row.get("expanded_query", ""),
                    self.document_text,
                    self.profile,
                )
            )

        relevance_gate = validate_report({"answers": answers}, self.profile)

        answer_text = " ".join(answer.get("answer", "") for answer in answers)
        linguistic_errors = check_text(answer_text, self.profile)

        errors = []

        if relevance_gate.get("status") != "PASS":
            errors.append(f"relevance_gate:{relevance_gate.get('errors')}")

        if linguistic_errors:
            errors.append(f"linguistic_gate:{linguistic_errors}")

        return {
            "engine": "mini_llm_universal_llm_bridge_v395",
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
            "diagnostics": self.diagnostics(),
            "profile": self.profile,
            "query_expansion": expansion,
            "answers": answers,
            "gates": {
                "relevance": relevance_gate,
                "linguistic_errors": linguistic_errors,
            },
            "elapsed_ms": (time.perf_counter() - start) * 1000.0,
            "limits": [
                "Bridge tra mini LLM e core universale.",
                "Domande migliorate dal core universale.",
                "Risposte validate dal core universale.",
                "Profili specialistici separati.",
            ],
        }


def answer_document(document_text: str, queries: List[str] | None = None) -> Dict[str, Any]:
    return MiniLLMUniversalLLMBridgeV395(document_text).answer_queries(queries)
