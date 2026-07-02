#!/usr/bin/env python3
from __future__ import annotations

import importlib
import re
import time
from typing import Any, Dict, List

from mini_llm.python.runtime.mini_llm_universal_llm_bridge_v395 import (
    MiniLLMUniversalLLMBridgeV395,
)

DEFAULT_QUERIES = [
    "Quali sono i punti principali del documento?",
    "Che cosa devo ricordare?",
    "Quali rischi o problemi vengono spiegati nel documento?",
]

BAD_QUESTION_PATTERNS = [
    r"^che cosa usa quando\b",
    r"^quale informazione importante viene data su\b",
    r"\bsu\s+(quando si|possono|può dire|se un|è meglio)\b",
]

BAD_TITLE_STARTS = {
    "quando si",
    "possono",
    "può dire",
    "è meglio",
    "se un",
    "se una",
}

BAD_OPTION_ENDINGS = {
    "di", "del", "della", "dello", "dei", "degli", "delle",
    "a", "al", "alla", "allo", "agli", "alle",
    "con", "per", "tra", "fra",
    "su", "sul", "sulla", "sui", "sugli", "sulle",
    "e", "o", "che",
}


def normalize(text: Any) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").strip().split())


def last_word(text: str) -> str:
    words = normalize(text).split()
    if not words:
        return ""
    return words[-1].lower().strip(".,;:!?\"'“”‘’)]}")


def validate_legacy_study_pack_quality(pack: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    if not isinstance(pack, dict):
        return ["study_pack_not_dict"]

    for index, card in enumerate(pack.get("cards", []) or [], start=1):
        title = normalize(card.get("title", ""))
        low = title.lower()

        if not title:
            errors.append(f"card_{index}:empty_title")
            continue

        if len(title.split()) < 2:
            errors.append(f"card_{index}:title_too_short:{title}")

        if len(title.split()) > 7:
            errors.append(f"card_{index}:title_too_long:{title}")

        if any(low.startswith(start) for start in BAD_TITLE_STARTS):
            errors.append(f"card_{index}:weak_title_start:{title}")

        if last_word(title) in BAD_OPTION_ENDINGS:
            errors.append(f"card_{index}:title_bad_ending:{title}")

    for index, qa in enumerate(pack.get("qas", []) or [], start=1):
        question = normalize(qa.get("question", ""))

        if not question:
            errors.append(f"qa_{index}:empty_question")
            continue

        qlow = question.lower()

        if not question.endswith("?"):
            errors.append(f"qa_{index}:question_missing_mark:{question}")

        if len(question.split()) < 5:
            errors.append(f"qa_{index}:question_too_short:{question}")

        if len(question.split()) > 22:
            errors.append(f"qa_{index}:question_too_long:{question}")

        for pattern in BAD_QUESTION_PATTERNS:
            if re.search(pattern, qlow):
                errors.append(f"qa_{index}:weak_question_pattern:{question}")

    for index, item in enumerate(pack.get("test", []) or [], start=1):
        question = normalize(item.get("question", ""))
        options = item.get("options", []) or []

        if not question:
            errors.append(f"test_{index}:empty_question")

        if len(options) != 4:
            errors.append(f"test_{index}:wrong_option_count:{len(options)}")

        for opt_index, option in enumerate(options, start=1):
            clean = normalize(option)

            if not clean:
                errors.append(f"test_{index}:option_{opt_index}:empty")
                continue

            if last_word(clean) in BAD_OPTION_ENDINGS:
                errors.append(f"test_{index}:option_{opt_index}:truncated_or_bad_ending:{clean}")

            if len(clean.split()) < 4:
                errors.append(f"test_{index}:option_{opt_index}:too_short:{clean}")

    return errors


class MiniLLMUniversalCurrentEngineV396:
    def __init__(self, document_text: str, source: str = ""):
        self.document_text = str(document_text or "").strip()
        self.source = source

    def diagnostics(self) -> Dict[str, Any]:
        bridge = MiniLLMUniversalLLMBridgeV395(self.document_text)

        return {
            "engine": "mini_llm_universal_current_engine_v396",
            "version": "V3.9.6.1",
            "status": "OK" if self.document_text else "EMPTY",
            "source": self.source,
            "words": len(self.document_text.split()),
            "chars": len(self.document_text),
            "bridge": bridge.diagnostics(),
            "architecture": {
                "current_engine": "V3.9.6.1",
                "bridge": "V3.9.5",
                "universal_core": "V3.9.4U",
                "domain_profiles": "separated",
                "study_pack": "legacy_quality_gated",
            },
            "limits": [
                "Motore current universale controllato.",
                "Non è ancora generativo neurale.",
                "Non contiene vocabolari specialistici.",
                "Blocca study pack legacy se non supera il gate.",
            ],
        }

    def _study_pack(self) -> Dict[str, Any]:
        try:
            module = importlib.import_module("mini_llm.python.runtime.mini_llm_study_pack_current")
        except Exception as exc:
            return {
                "status": "ERROR",
                "errors": [f"study_pack_import_error:{exc}"],
                "study_pack": None,
            }

        try:
            pack = module.generate_study_pack(self.document_text)
        except Exception as exc:
            return {
                "status": "ERROR",
                "errors": [f"study_pack_generation_error:{exc}"],
                "study_pack": None,
            }

        legacy_status = pack.get("status", "UNKNOWN")
        quality_errors = validate_legacy_study_pack_quality(pack)

        if legacy_status != "OK":
            return {
                "status": "ERROR",
                "errors": pack.get("errors", []),
                "study_pack": None,
                "legacy_status": legacy_status,
            }

        if quality_errors:
            return {
                "status": "QUALITY_BLOCKED",
                "errors": quality_errors,
                "study_pack": None,
                "legacy_status": legacy_status,
                "reason": "Study pack legacy bloccato dal gate universale di qualità.",
            }

        return {
            "status": "OK",
            "errors": [],
            "study_pack": pack,
            "legacy_status": legacy_status,
        }

    def run(
        self,
        queries: List[str] | None = None,
        include_study_pack: bool = True,
    ) -> Dict[str, Any]:
        start = time.perf_counter()

        selected_queries = queries or DEFAULT_QUERIES
        bridge = MiniLLMUniversalLLMBridgeV395(self.document_text)
        bridge_result = bridge.answer_queries(selected_queries)

        errors: List[str] = []

        if bridge_result.get("status") != "PASS":
            errors.append(f"bridge_not_pass:{bridge_result.get('errors')}")

        study_result: Dict[str, Any] = {
            "status": "SKIPPED",
            "reason": "include_study_pack=false",
            "study_pack": None,
            "errors": [],
        }

        if include_study_pack:
            study_result = self._study_pack()
            if study_result.get("status") == "ERROR":
                errors.append(f"study_pack_error:{study_result.get('errors')}")

        return {
            "engine": "mini_llm_universal_current_engine_v396",
            "version": "V3.9.6.1",
            "status": "PASS" if not errors else "FAIL",
            "errors": errors,
            "source": self.source,
            "diagnostics": self.diagnostics(),
            "queries": selected_queries,
            "bridge_result": bridge_result,
            "answers": bridge_result.get("answers", []),
            "query_expansion": bridge_result.get("query_expansion", {}),
            "profile": bridge_result.get("profile", {}),
            "gates": bridge_result.get("gates", {}),
            "study_pack": study_result,
            "elapsed_ms": (time.perf_counter() - start) * 1000.0,
            "limits": [
                "Current Engine V3.9.6.1.",
                "Usa bridge universale V3.9.5.",
                "Core universale separato dai profili.",
                "Study pack legacy protetto da gate qualità.",
                "No fix su domanda singola.",
            ],
        }


def run_document(
    document_text: str,
    queries: List[str] | None = None,
    include_study_pack: bool = True,
    source: str = "",
) -> Dict[str, Any]:
    return MiniLLMUniversalCurrentEngineV396(document_text, source=source).run(
        queries=queries,
        include_study_pack=include_study_pack,
    )
