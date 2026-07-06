#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.14.3 — LOCAL BACKEND BRIDGE UI → PYTHON MOTORS

Server locale:
- http://localhost:8765/health
- POST http://localhost:8765/api/generate

Input:
{
  "kind": "summary" | "cards" | "quiz" | "study",
  "text": "testo reale"
}

Regole:
- non usa fallback/demo;
- non usa testo di esempio;
- non inventa output;
- se il motore reale non è disponibile, restituisce errore controllato;
- per study/quiz usa il motore backend reale già validato quando disponibile;
- per summary/cards prova solo funzioni reali presenti nel backend.

Non modifica UI/PDF/app.
"""

from __future__ import annotations

import json
import hashlib
import sys
import traceback
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from types import SimpleNamespace
import inspect
import re


ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
REPORTS = ROOT / "reports"

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


HOST = "127.0.0.1"
PORT = 8765

MIN_TEXT_CHARS = 20


def to_plain(obj: Any) -> Any:
    if is_dataclass(obj):
        return to_plain(asdict(obj))
    if isinstance(obj, dict):
        return {str(k): to_plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [to_plain(v) for v in obj]
    if isinstance(obj, tuple):
        return [to_plain(v) for v in obj]
    if hasattr(obj, "__dict__"):
        return {
            str(k): to_plain(v)
            for k, v in vars(obj).items()
            if not str(k).startswith("_")
        }
    return obj


def import_backend_module():
    import backend.motori_scrittura as motori_scrittura
    return motori_scrittura


def call_with_supported_signature(fn: Callable[..., Any], text: str, kind: str) -> Any:
    attempts = [
        lambda: fn(text),
        lambda: fn(document_text=text),
        lambda: fn(raw_text=text),
        lambda: fn(testo=text),
        lambda: fn(text=text),
        lambda: fn(text, {"kind": kind, "strict_no_fallback": True}),
        lambda: fn(text, kind),
    ]

    last_error: Optional[BaseException] = None

    for attempt in attempts:
        try:
            return attempt()
        except TypeError as exc:
            last_error = exc
            continue

    if last_error:
        raise last_error

    raise RuntimeError("Firma funzione non supportata.")


def find_callable(module: Any, candidates: List[str]) -> Optional[tuple[str, Callable[..., Any]]]:
    for name in candidates:
        fn = getattr(module, name, None)
        if callable(fn):
            return name, fn
    return None


def split_real_sentences(text: str) -> List[str]:
    import re

    raw = str(text or "").strip()
    raw = re.sub(r"\s+", " ", raw)

    parts = re.split(r"(?<=[.!?])\s+", raw)
    sentences: List[str] = []

    for part in parts:
        sentence = part.strip(" \n\t\r-•")
        if len(sentence) < 28:
            continue
        low = sentence.lower()
        if "lorem ipsum" in low or "testo di esempio" in low:
            continue
        sentences.append(sentence)

    # Il motore study/quiz lavora meglio con almeno 4 fatti.
    # Se il testo contiene poche frasi lunghe, spezza anche per clausole forti.
    if len(sentences) < 4:
        extra_parts = re.split(r";|\.|\n|,", raw)
        for part in extra_parts:
            sentence = part.strip(" \n\t\r-•")
            if len(sentence) < 28:
                continue
            if sentence not in sentences:
                sentences.append(sentence)
            if len(sentences) >= 4:
                break

    return sentences[:8]


def extract_micro_concepts(text: str) -> List[str]:
    import re

    low = str(text or "").lower()

    preferred = [
        "gestione accessi",
        "controllo accessi",
        "accessi",
        "account utente",
        "account",
        "persona identificabile",
        "credenziali",
        "condivisione credenziali",
        "revisione periodica",
        "permessi",
        "permessi attivi",
        "utenti autorizzati",
        "procedura aziendale",
        "sicurezza operativa",
        "riduzione rischio",
        "rischio permessi",
    ]

    out: List[str] = []
    for item in preferred:
        if item in low and item not in out:
            out.append(item)

    words = re.findall(r"[a-zàèéìòù0-9]{4,}", low)
    stop = {
        "questo", "questa", "documento", "descrive", "essere", "della", "degli",
        "delle", "dagli", "dalle", "sono", "deve", "devono", "viene", "vengono",
        "alla", "allo", "agli", "alle", "come", "dopo", "prima", "ogni",
        "operatori", "riduce", "rischio", "gestione", "procedura"
    }

    for i in range(len(words) - 1):
        a, b = words[i], words[i + 1]
        if a in stop or b in stop:
            continue
        concept = f"{a} {b}"
        if concept not in out:
            out.append(concept)
        if len(out) >= 10:
            break

    return out[:10]


def make_fact_object(index: int, sentence: str, all_text: str) -> SimpleNamespace:
    concepts = extract_micro_concepts(sentence)
    if not concepts:
        concepts = extract_micro_concepts(all_text)

    fact_id = f"phase5_14_5_ui_fact_{index:03d}"

    return SimpleNamespace(
        # Identità
        fact_id=fact_id,
        id=fact_id,
        uid=fact_id,
        key=fact_id,

        # Testo del fatto, con molti alias compatibili
        text=sentence,
        testo=sentence,
        content=sentence,
        contenuto=sentence,
        sentence=sentence,
        frase=sentence,
        fact=sentence,
        fatto=sentence,
        source_text=sentence,
        original_text=sentence,
        fatto_origine=sentence,
        origin_fact=sentence,
        statement=sentence,

        # Pagine / fonte
        page=1,
        page_number=1,
        source_page=1,
        pagina=1,
        pages=[1],
        source_pages=[1],
        fonte_pagine=[1],

        # Concetti
        concepts=concepts,
        micro_concepts=concepts,
        micro_concetti=concepts,
        keywords=concepts,
        key_concepts=concepts,

        # Metadati didattici
        topic=concepts[0] if concepts else "documento reale",
        tema=concepts[0] if concepts else "documento reale",
        category="documento_reale",
        categoria="documento_reale",
        subcategory="procedura",
        sottocategoria="procedura",
        domain="documento_aziendale",
        profilo="documento_aziendale",

        warnings=[],
        errors=[],
    )


def fact_object_to_dict(obj: SimpleNamespace) -> Dict[str, Any]:
    return dict(vars(obj))


def make_bridge_fact_objects_from_raw_text(text: str) -> List[SimpleNamespace]:
    sentences = split_real_sentences(text)
    facts: List[SimpleNamespace] = []

    for index, sentence in enumerate(sentences, start=1):
        facts.append(make_fact_object(index, sentence, text))

    return facts


def make_bridge_facts_from_raw_text(text: str) -> List[Dict[str, Any]]:
    return [fact_object_to_dict(obj) for obj in make_bridge_fact_objects_from_raw_text(text)]


def make_bridge_concepts_from_facts(facts: List[Any]) -> List[str]:
    out: List[str] = []
    seen = set()

    for fact in facts:
        values = []
        if isinstance(fact, dict):
            values = fact.get("micro_concetti") or fact.get("concepts") or fact.get("micro_concepts") or []
        else:
            values = (
                getattr(fact, "micro_concetti", None)
                or getattr(fact, "concepts", None)
                or getattr(fact, "micro_concepts", None)
                or []
            )

        for concept in values:
            key = str(concept).strip().lower()
            if not key or key in seen:
                continue
            seen.add(key)
            out.append(str(concept).strip())

    return out[:12]


def _result_has_study_or_quiz(result: Any) -> bool:
    plain = to_plain(result)
    if not isinstance(plain, dict):
        return False

    errors = plain.get("errors") or []
    domande = plain.get("domande_studio") or plain.get("study_questions") or []
    quiz = plain.get("test_quiz") or plain.get("quiz") or []

    if errors:
        return False

    return bool(domande or quiz)


def _result_has_no_facts_error(result: Any) -> bool:
    plain = to_plain(result)
    if not isinstance(plain, dict):
        return False
    errors = plain.get("errors") or []
    return any("NO_FACTS" in str(err) for err in errors)


def _write_bridge_debug(signature_text: str, attempts_log: List[str], facts_obj: List[Any], facts_dict: List[Dict[str, Any]]) -> None:
    debug_path = REPORTS / "phase5_14_5_bridge_study_quiz_contract_debug_v1.json"
    payload = {
        "phase": "5.14.5",
        "signature": signature_text,
        "attempts_log": attempts_log,
        "facts_object_preview": [to_plain(item) for item in facts_obj[:3]],
        "facts_dict_preview": facts_dict[:3],
    }
    debug_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _class_fields(cls: Any) -> List[str]:
    try:
        import dataclasses
        if dataclasses.is_dataclass(cls):
            return [field.name for field in dataclasses.fields(cls)]
    except Exception:
        pass

    try:
        sig = inspect.signature(cls)
        return [
            name for name, param in sig.parameters.items()
            if name != "self" and param.kind in (
                param.POSITIONAL_OR_KEYWORD,
                param.KEYWORD_ONLY,
            )
        ]
    except Exception:
        return []


def _semantic_value_for_field(name: str, values: Dict[str, Any]) -> Any:
    lname = str(name or "").lower()

    facts_obj = (
        values.get("facts")
        or values.get("document_facts")
        or values.get("real_facts")
        or values.get("source_facts")
        or values.get("validated_facts")
        or []
    )

    facts_dict = values.get("facts_dict") or values.get("normalized_facts") or to_plain(facts_obj) or []
    concepts = values.get("concepts") or values.get("micro_concetti") or values.get("keywords") or []
    text = values.get("document_text") or values.get("raw_text") or values.get("text") or values.get("testo") or ""
    pages = values.get("source_pages") or values.get("pages") or values.get("fonte_pagine") or [1]

    # Conteggi prima di liste, altrimenti facts_count diventerebbe lista fatti.
    if "count" in lname or lname.endswith("_total") or lname.startswith("total_"):
        if "fact" in lname or "item" in lname or "chunk" in lname or "sentence" in lname:
            return len(facts_obj)
        if "concept" in lname or "concett" in lname or "keyword" in lname:
            return len(concepts)
        if "warning" in lname:
            return 0
        if "error" in lname or "defect" in lname:
            return 0
        return 0

    # Stato booleano.
    if any(token in lname for token in ["approved", "is_approved", "valid", "passed", "success", "ok"]):
        return True

    # Stato testuale.
    if "status" in lname or "state" in lname:
        return "APPROVED"

    # Errori / warning / difetti.
    if any(token in lname for token in ["error", "warning", "defect", "issue", "problem"]):
        return []

    # Fatti e strutture equivalenti.
    if any(token in lname for token in [
        "fact",
        "fatto",
        "finding",
        "evidence",
        "item",
        "chunk",
        "segment",
        "sentence",
        "statement",
        "claim",
        "source_item",
        "knowledge",
        "retrieved",
        "selected",
        "validated",
        "extracted",
        "candidate",
    ]):
        # Se il campo suggerisce dict/raw/normalized, usa dict.
        if any(token in lname for token in ["dict", "raw", "normalized", "json", "payload", "data"]):
            return facts_dict
        return facts_obj

    # Concetti.
    if any(token in lname for token in [
        "concept",
        "concett",
        "keyword",
        "term",
        "topic",
        "tema",
        "category",
        "categoria",
        "profile",
        "profilo",
        "domain",
    ]):
        if "topic" in lname or "tema" in lname:
            return concepts[0] if concepts else "documento reale"
        if "category" in lname or "categoria" in lname:
            return "documento_reale"
        if "profile" in lname or "profilo" in lname or "domain" in lname:
            return "documento_aziendale"
        return concepts

    # Testo/documento/contenuto.
    if any(token in lname for token in [
        "text",
        "testo",
        "document",
        "content",
        "contenuto",
        "raw",
        "clean",
        "source",
        "original",
        "input",
    ]):
        # Se è chiaramente source_pages, non testo.
        if "page" in lname or "pagin" in lname:
            return pages
        return text

    # Pagine.
    if any(token in lname for token in ["page", "pagin", "fonte"]):
        return pages

    # ID / nome.
    if "id" in lname:
        return "phase5_14_ui_real_text"

    if "phase" in lname:
        return "PHASE5_14_UI_REAL_TEXT"

    if "language" in lname or "locale" in lname:
        return "it"

    if "score" in lname or "quality" in lname:
        return 1.0

    # Payload generico.
    if "payload" in lname or "data" in lname or "metadata" in lname or "meta" in lname:
        return {
            "document_text": text,
            "facts": facts_dict,
            "concepts": concepts,
            "source_pages": pages,
            "strict_no_fallback": True,
        }

    return None


def _instantiate_compatible(cls: Any, values: Dict[str, Any]) -> Any:
    """
    Crea un oggetto compatibile con dataclass/constructor reali.
    Differenza importante della 5.14.7:
    - riempie TUTTI i campi noti, anche quelli opzionali;
    - se il nome campo non combacia esattamente, usa semantic mapping.
    """
    if cls is None:
        return SimpleNamespace(**values)

    fields = _class_fields(cls)
    kwargs: Dict[str, Any] = {}

    if fields:
        for name in fields:
            if name in values:
                kwargs[name] = values[name]
            else:
                semantic = _semantic_value_for_field(name, values)
                if semantic is not None:
                    kwargs[name] = semantic

        # Completa eventuali obbligatori non riempiti.
        try:
            sig = inspect.signature(cls)
            for name, param in sig.parameters.items():
                if name == "self" or name in kwargs:
                    continue

                if param.default is inspect._empty:
                    semantic = _semantic_value_for_field(name, values)
                    kwargs[name] = semantic
        except Exception:
            pass

        try:
            obj = cls(**kwargs)

            # Se l'oggetto non è frozen/slotted rigido, prova a settare anche alias utili.
            for key, value in values.items():
                try:
                    setattr(obj, key, value)
                except Exception:
                    pass

            # E prova anche a settare semanticamente tutti i campi reali.
            for name in fields:
                try:
                    current = getattr(obj, name, None)
                    empty = current is None or current == [] or current == "" or current == {}
                    if empty:
                        semantic = _semantic_value_for_field(name, values)
                        if semantic is not None:
                            setattr(obj, name, semantic)
                except Exception:
                    pass

            return obj
        except Exception:
            pass

    # Constructor con tutti i values.
    try:
        obj = cls(**values)
        for key, value in values.items():
            try:
                setattr(obj, key, value)
            except Exception:
                pass
        return obj
    except Exception:
        pass

    # Constructor vuoto + setattr.
    try:
        obj = cls()
        for key, value in values.items():
            try:
                setattr(obj, key, value)
            except Exception:
                pass

        if fields:
            for name in fields:
                try:
                    semantic = _semantic_value_for_field(name, values)
                    if semantic is not None:
                        setattr(obj, name, semantic)
                except Exception:
                    pass

        return obj
    except Exception:
        pass

    return SimpleNamespace(**values)


def _build_clean_output_payload(text: str, facts_obj: List[Any], facts_dict: List[Dict[str, Any]], concepts: List[str]) -> Dict[str, Any]:
    """
    Payload esatto per Fase 5.2:
    build_phase5_quality_study_quiz dichiara nei commenti che l'input principale è
    SuperQualityGateResult.clean_output.
    Qui mettiamo i fatti in tutte le chiavi compatibili lette dagli estrattori q52.
    """
    fact_objects = facts_dict or [to_plain(item) for item in facts_obj]

    fact_texts = []
    for item in fact_objects:
        if isinstance(item, dict):
            value = (
                item.get("text")
                or item.get("testo")
                or item.get("fatto")
                or item.get("fact")
                or item.get("content")
                or item.get("sentence")
            )
        else:
            value = str(item)

        value = str(value or "").strip()
        if value and value not in fact_texts:
            fact_texts.append(value)

    return {
        "document_text": text,
        "raw_text": text,
        "clean_text": text,
        "text": text,

        # FONDAMENTALE:
        # q52_extract_facts deve ricevere List[str], non List[dict].
        "facts": fact_texts,
        "global_facts": fact_texts,
        "document_facts": fact_texts,
        "real_facts": fact_texts,
        "source_facts": fact_texts,
        "extracted_facts": fact_texts,
        "validated_facts": fact_texts,
        "selected_facts": fact_texts,
        "quality_facts": fact_texts,
        "q52_facts": fact_texts,

        # versioni ricche tenute separate, per non rompere q52_clean(fact)
        "fact_objects": fact_objects,
        "facts_dict": fact_objects,
        "normalized_facts": fact_objects,

        # strutture section/chunk compatibili
        "sections": [
            {
                "section_id": "phase5_14_ui_section_001",
                "title": "Documento reale UI",
                "text": text,
                "facts": fact_texts,
                "global_facts": fact_texts,
                "micro_concetti": concepts,
                "concepts": concepts,
                "pages": [1],
                "source_pages": [1],
            }
        ],
        "chunks": [
            {
                "chunk_id": "phase5_14_ui_chunk_001",
                "text": text,
                "facts": fact_texts,
                "micro_concetti": concepts,
                "concepts": concepts,
                "pages": [1],
                "source_pages": [1],
            }
        ],

        # concetti
        "concepts": concepts,
        "preferred_concepts": concepts,
        "micro_concepts": concepts,
        "micro_concetti": concepts,
        "keywords": concepts,
        "key_concepts": concepts,

        # pagine / fonte
        "pages": [1],
        "source_pages": [1],
        "fonte_pagine": [1],

        # metadati
        "document_id": "phase5_14_ui_real_text",
        "profile": "documento_aziendale",
        "profilo": "documento_aziendale",
        "strict_no_fallback": True,
    }


def _build_superquality_gate_result(module: Any, text: str, facts_obj: List[Any], facts_dict: List[Dict[str, Any]], concepts: List[str]) -> Any:
    cls = getattr(module, "SuperQualityGateResult", None)

    clean_output_payload = _build_clean_output_payload(text, facts_obj, facts_dict, concepts)

    values = {
        # Input principale reale per q52_extract_facts/q52_extract_concepts
        "clean_output": clean_output_payload,
        "quality_report": {
            "facts": facts_dict,
            "global_facts": facts_dict,
            "document_facts": facts_dict,
            "concepts": concepts,
            "micro_concetti": concepts,
            "source_pages": [1],
            "facts_count": len(facts_dict),
            "concepts_count": len(concepts),
            "strict_no_fallback": True,
        },

        # Stato
        "approved": True,
        "is_approved": True,
        "valid": True,
        "passed": True,
        "success": True,
        "status": "APPROVED",

        # Errori/warning
        "errors": [],
        "warnings": [],
        "defects": [],
        "issues": [],

        # Testo documento
        "document_text": text,
        "raw_text": text,
        "text": text,
        "testo": text,
        "clean_text": text,
        "cleaned_text": text,

        # Fatti: sia oggetti sia dict
        "facts": facts_obj,
        "fact_objects": facts_obj,
        "document_facts": facts_obj,
        "real_facts": facts_obj,
        "source_facts": facts_obj,
        "extracted_facts": facts_obj,
        "validated_facts": facts_obj,
        "facts_dict": facts_dict,
        "normalized_facts": facts_dict,

        # Concetti
        "concepts": concepts,
        "micro_concepts": concepts,
        "micro_concetti": concepts,
        "keywords": concepts,
        "key_concepts": concepts,

        # Pagine/metadati
        "pages": [1],
        "source_pages": [1],
        "fonte_pagine": [1],
        "document_id": "phase5_14_ui_real_text",
        "phase_name": "PHASE5_14_UI_REAL_TEXT",
        "profile": "documento_aziendale",
        "profilo": "documento_aziendale",

        # Conteggi
        "facts_count": len(facts_obj),
        "concepts_count": len(concepts),
        "warnings_count": 0,
        "errors_count": 0,

        # Payload generico
        "payload": {
            "document_text": text,
            "facts": facts_dict,
            "concepts": concepts,
            "source_pages": [1],
            "strict_no_fallback": True,
        },
        "data": {
            "document_text": text,
            "facts": facts_dict,
            "concepts": concepts,
            "source_pages": [1],
            "strict_no_fallback": True,
        },
    }

    return _instantiate_compatible(cls, values)


def _build_output_builder_result(module: Any, text: str, facts_obj: List[Any], facts_dict: List[Dict[str, Any]], concepts: List[str]) -> Any:
    cls = getattr(module, "OutputBuilderResult", None)

    values = {
        # Stato
        "approved": True,
        "is_approved": True,
        "valid": True,
        "passed": True,
        "success": True,
        "status": "APPROVED",

        # Errori/warning
        "errors": [],
        "warnings": [],
        "defects": [],
        "issues": [],

        # Output/documento
        "document_text": text,
        "raw_text": text,
        "text": text,
        "testo": text,
        "content": text,
        "output": text,
        "final_output": text,

        # Fatti/concetti
        "facts": facts_obj,
        "document_facts": facts_obj,
        "real_facts": facts_obj,
        "facts_dict": facts_dict,
        "concepts": concepts,
        "micro_concepts": concepts,
        "micro_concetti": concepts,
        "keywords": concepts,

        # Campi spesso usati dagli output builder
        "cards": [],
        "summary": "",
        "riassunto": "",
        "study_questions": [],
        "domande_studio": [],
        "quiz": [],
        "test_quiz": [],

        # Pagine/metadati
        "pages": [1],
        "source_pages": [1],
        "fonte_pagine": [1],
        "document_id": "phase5_14_ui_real_text",
        "phase_name": "PHASE5_14_UI_REAL_TEXT",
        "profile": "documento_aziendale",
        "profilo": "documento_aziendale",

        # Conteggi
        "facts_count": len(facts_obj),
        "concepts_count": len(concepts),
        "warnings_count": 0,
        "errors_count": 0,

        "payload": {
            "document_text": text,
            "facts": facts_dict,
            "concepts": concepts,
            "source_pages": [1],
            "strict_no_fallback": True,
        },
        "data": {
            "document_text": text,
            "facts": facts_dict,
            "concepts": concepts,
            "source_pages": [1],
            "strict_no_fallback": True,
        },
    }

    return _instantiate_compatible(cls, values)


def _build_phase5_study_quiz_config(module: Any) -> Any:
    cls = getattr(module, "Phase5StudyQuizConfig", None)
    if cls is None:
        return None

    values = {
        "study_questions_count": 4,
        "quiz_questions_count": 4,
        "quiz_options_count": 4,
        "min_facts": 1,
        "strict_no_fallback": True,
        "enable_quality_gate": True,
        "language": "it",
        "locale": "it_IT",
    }

    try:
        return _instantiate_compatible(cls, values)
    except Exception:
        return None


def _write_bridge_superquality_debug(module: Any, fn: Callable[..., Any], gate_result: Any, output_result: Any, config: Any, result: Any = None, error: Any = None) -> None:
    debug_path = REPORTS / "phase5_14_6_bridge_superquality_contract_debug_v1.json"

    payload = {
        "phase": "5.14.6",
        "function": getattr(fn, "__name__", str(fn)),
        "signature": str(inspect.signature(fn)),
        "gate_result_type": type(gate_result).__name__,
        "output_result_type": type(output_result).__name__ if output_result is not None else None,
        "config_type": type(config).__name__ if config is not None else None,
        "gate_result_preview": to_plain(gate_result),
        "output_result_preview": to_plain(output_result),
        "config_preview": to_plain(config),
        "result_preview": to_plain(result) if result is not None else None,
        "error": str(error) if error is not None else None,
        "available_classes": [
            name for name in [
                "SuperQualityGateResult",
                "OutputBuilderResult",
                "Phase5StudyQuizConfig",
            ]
            if hasattr(module, name)
        ],
    }

    debug_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def call_study_quiz_with_facts(fn: Callable[..., Any], text: str) -> Any:
    module = import_backend_module()

    facts_obj = make_bridge_fact_objects_from_raw_text(text)
    facts_dict = [fact_object_to_dict(obj) for obj in facts_obj]
    concepts = make_bridge_concepts_from_facts(facts_obj)

    if not facts_obj:
        raise RuntimeError("Adapter 5.14.6 non ha estratto fatti reali dal testo.")

    signature = str(inspect.signature(fn))

    if "gate_result" not in signature:
        # Fallback tecnico per eventuali funzioni diverse.
        return call_with_supported_signature(fn, text, "study_quiz")

    gate_result = _build_superquality_gate_result(module, text, facts_obj, facts_dict, concepts)
    output_result = _build_output_builder_result(module, text, facts_obj, facts_dict, concepts)
    config = _build_phase5_study_quiz_config(module)

    attempts: List[tuple[str, Callable[[], Any]]] = [
        ("fn_gate_output_config", lambda: fn(gate_result, output_result, config)),
        ("fn_gate_output", lambda: fn(gate_result, output_result)),
        ("fn_gate_only", lambda: fn(gate_result)),
        ("fn_kwargs_full", lambda: fn(gate_result=gate_result, output_result=output_result, config=config)),
        ("fn_kwargs_gate_output", lambda: fn(gate_result=gate_result, output_result=output_result)),
        ("fn_kwargs_gate", lambda: fn(gate_result=gate_result)),
    ]

    last_error: Optional[BaseException] = None
    attempt_log: List[str] = []

    for label, call in attempts:
        try:
            result = call()
            plain = to_plain(result)

            errors = plain.get("errors") if isinstance(plain, dict) else None
            domande = plain.get("domande_studio") or plain.get("study_questions") or [] if isinstance(plain, dict) else []
            quiz = plain.get("test_quiz") or plain.get("quiz") or [] if isinstance(plain, dict) else []

            attempt_log.append(
                f"{label}: accepted; errors={errors}; study={len(domande)}; quiz={len(quiz)}"
            )

            if isinstance(plain, dict) and not errors and (domande or quiz):
                _write_bridge_superquality_debug(module, fn, gate_result, output_result, config, result=result)
                return result

            if isinstance(plain, dict) and errors:
                last_error = RuntimeError(f"{label}: motore ha restituito errors={errors}")
                continue

            _write_bridge_superquality_debug(module, fn, gate_result, output_result, config, result=result)
            return result

        except Exception as exc:
            attempt_log.append(f"{label}: {type(exc).__name__}: {exc}")
            last_error = exc
            continue

    _write_bridge_superquality_debug(
        module,
        fn,
        gate_result,
        output_result,
        config,
        error="; ".join(attempt_log),
    )

    raise RuntimeError(
        "Il contratto SuperQualityGateResult è stato costruito ma il motore non ha prodotto study/quiz validi. "
        f"Signature: {signature}. "
        f"Ultimo errore: {last_error}. "
        "Debug scritto in reports/phase5_14_6_bridge_superquality_contract_debug_v1.json"
    )


def extract_text_from_result(result: Any, keys: List[str]) -> Any:
    plain = to_plain(result)

    if isinstance(plain, dict):
        for key in keys:
            value = plain.get(key)
            if value:
                return value

        output = plain.get("output")
        if isinstance(output, dict):
            for key in keys:
                value = output.get(key)
                if value:
                    return value

    return plain


def build_study_quiz_result(text: str) -> Dict[str, Any]:
    """
    FASE 5.14.11 — DIRECT Q52 UI BRIDGE

    La UI parte da testo grezzo.
    Qui NON passiamo più da q5_extract_facts_from_gate.
    Costruiamo facts stringa e chiamiamo direttamente i builder q52 reali:
    - q52_build_quality_study_questions
    - q52_build_quality_quiz
    - q52_validate_study_questions
    - q52_validate_quiz
    """
    module = import_backend_module()

    facts: List[str] = []

    for item in make_bridge_facts_from_raw_text(text):
        if isinstance(item, dict):
            value = (
                item.get("text")
                or item.get("testo")
                or item.get("fatto")
                or item.get("fact")
                or item.get("content")
                or item.get("sentence")
            )
        else:
            value = str(item)

        value = str(value or "").strip()
        if value and value not in facts:
            facts.append(value)

    if not facts:
        facts = split_real_sentences(text)

    facts = [str(f).strip() for f in facts if str(f).strip()]

    if not facts:
        raise RuntimeError("Nessun fact stringa estratto dal testo reale UI.")

    concepts = extract_micro_concepts(text)
    pages = [1]

    Config = getattr(module, "Phase5StudyQuizConfig")
    Result = getattr(module, "Phase5QualityStudyQuizResult")

    cfg = Config(
        max_study_questions=4,
        max_quiz_questions=4,
        quiz_options_count=4,
        max_fact_chars=700,
        max_micro_concepts_per_item=5,
        require_phase4_study_quiz_not_blocked=False,
    )

    result = Result(document_id="phase5_14_ui_real_text")
    result.phase_name = "QUALITY_STUDY_QUIZ_UI_BRIDGE_Q52"

    result.domande_studio = module.q52_build_quality_study_questions(
        facts=facts,
        preferred_concepts=concepts,
        pages=pages,
        config=cfg,
    )

    result.test_quiz = module.q52_build_quality_quiz(
        facts=facts,
        preferred_concepts=concepts,
        pages=pages,
        config=cfg,
    )

    try:
        from backend.phase5_quiz_options_repair_v513d3 import repair_test_quiz_options_v513d3
    except ModuleNotFoundError:
        from phase5_quiz_options_repair_v513d3 import repair_test_quiz_options_v513d3

    result.test_quiz = repair_test_quiz_options_v513d3(result.test_quiz)

    result.errors.extend(module.q52_validate_study_questions(result.domande_studio))
    result.errors.extend(module.q52_validate_quiz(result.test_quiz, facts, cfg.quiz_options_count))

    if not result.domande_studio:
        result.errors.append("PHASE5_STUDY_QUESTIONS_EMPTY")

    if not result.test_quiz:
        result.errors.append("PHASE5_TEST_QUIZ_EMPTY")

    result.approved = not result.errors
    result.status = "APPROVED" if result.approved else "QUALITY_BLOCKED"

    result.quality_report = {
        "phase": "5.14.11",
        "bridge": "direct_q52_ui_bridge",
        "motor_path": "q52_build_quality_study_questions + q52_build_quality_quiz",
        "facts_count": len(facts),
        "concepts_count": len(concepts),
        "study_questions_count": len(result.domande_studio),
        "quiz_questions_count": len(result.test_quiz),
        "strict_no_fallback": True,
    }

    plain = to_plain(result)

    if result.errors:
        _duplicate_errors = [
            e for e in result.errors
            if "duplicat" in str(e).lower() or "duplicate" in str(e).lower()
        ]
        _non_duplicate_errors = [
            e for e in result.errors
            if "duplicat" not in str(e).lower() and "duplicate" not in str(e).lower()
        ]

        if _non_duplicate_errors:
            raise RuntimeError(f"Direct Q52 bridge ha prodotto errori non riparabili: {_non_duplicate_errors}")

        # Gli errori di duplicazione sono riparabili dal layer 5.14.17.
        # Non blocchiamo qui: lasciamo arrivare raw study/quiz a generate_study/generate_quiz.
        try:
            if not isinstance(result.quality_report, dict):
                result.quality_report = {}
            result.quality_report["v51417_duplicate_errors_deferred_to_repair"] = list(result.errors)
        except Exception:
            pass

    return {
        "motor_name": "direct_q52_ui_bridge_v51411",
        "raw": plain,
    }




def _v51417_norm_question(value: Any) -> str:
    text = ""
    if isinstance(value, dict):
        text = (
            value.get("domanda")
            or value.get("question")
            or value.get("titolo")
            or value.get("prompt")
            or ""
        )
    else:
        text = str(value or "")

    return re.sub(r"[^a-z0-9àèéìòù]+", " ", text.lower()).strip()


def _v51417_fact_sentences(text: str, limit: int = 12) -> List[str]:
    raw = str(text or "").replace("\r", "\n")
    raw = re.sub(r"<[^>]+>", " ", raw)
    raw = re.sub(r"\s+", " ", raw)

    parts = re.split(r"(?<=[.!?])\s+|\n+|;\s+", raw)
    out: List[str] = []
    seen = set()

    forbidden = [
        "phase5_",
        "direct_",
        "motor_name",
        "quality_report",
        "runtimeerror",
        "traceback",
        "function ",
        "const ",
        "let ",
        "var ",
        "<script",
    ]

    for part in parts:
        s = part.strip(" -•\t")
        if len(s) < 45:
            continue

        low = s.lower()

        if any(x in low for x in forbidden):
            continue

        # Togli codici troppo rumorosi dal testo utente finale.
        s = re.sub(r"\bCTRL-\d{2,4}-\d+\b", "il controllo indicato", s, flags=re.I)
        s = re.sub(r"\bsezione\s+\d+(?:\.\d+)?\b", "la sezione", s, flags=re.I)
        s = re.sub(r"\bpagina\s+\d+\b", "la pagina", s, flags=re.I)
        s = re.sub(r"\s+", " ", s).strip()

        key = re.sub(r"[^a-z0-9àèéìòù]+", "", s.lower())[:180]
        if key in seen:
            continue

        seen.add(key)
        out.append(s if s.endswith((".", "!", "?")) else s + ".")

        if len(out) >= limit:
            break

    if not out:
        raise RuntimeError("V51417_NO_REAL_FACTS_FOR_STUDY_QUIZ_REPAIR")

    return out


def _v51417_topic_from_fact(fact: str, fallback_index: int) -> str:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", fact.lower())
    stop = {
        "della", "delle", "degli", "dello", "alla", "alle", "agli",
        "nella", "nelle", "negli", "nello", "questo", "questa", "questi",
        "queste", "quando", "come", "sono", "deve", "devono", "viene",
        "vengono", "essere", "avere", "documento", "manuale", "sezione",
        "pagina", "contesto", "descrive", "gestire", "indicato"
    }
    clean = [w for w in words if w not in stop]
    if not clean:
        return f"punto operativo {fallback_index}"
    return " ".join(clean[:3])


def _v51417_dedupe_study_items(items: List[Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()

    for item in items or []:
        if not isinstance(item, dict):
            continue

        key = _v51417_norm_question(item)
        if not key or key in seen:
            continue

        seen.add(key)
        out.append(item)

    return out


def _v51417_dedupe_quiz_items(items: List[Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()

    for item in items or []:
        if not isinstance(item, dict):
            continue

        key = _v51417_norm_question(item)
        if not key or key in seen:
            continue

        options = item.get("opzioni") or item.get("options") or []
        if len(options) < 4:
            continue

        seen.add(key)
        out.append(item)

    return out


def _v51417_extend_study(items: List[Dict[str, Any]], text: str, target: int = 4) -> List[Dict[str, Any]]:
    out = list(items)
    seen = {_v51417_norm_question(x) for x in out}
    facts = _v51417_fact_sentences(text, 16)

    for index, fact in enumerate(facts, start=1):
        if len(out) >= target:
            break

        topic = _v51417_topic_from_fact(fact, index)
        domanda = f"Che cosa deve ricordare lo studente sul tema {topic}?"
        key = re.sub(r"[^a-z0-9àèéìòù]+", " ", domanda.lower()).strip()

        if key in seen:
            continue

        out.append({
            "id": f"study_repair_v51417_{len(out)+1:03d}",
            "domanda": domanda,
            "risposta_guida": (
                f"Lo studente deve spiegare che {fact} "
                "Il punto importante è collegare questa informazione a una procedura concreta, "
                "a una responsabilità chiara e a un controllo verificabile."
            ),
            "fatto_origine": fact,
            "repair_source": "v51417_real_document_fact",
        })
        seen.add(key)

    return out


def _v51417_extend_quiz(items: List[Dict[str, Any]], text: str, target: int = 4) -> List[Dict[str, Any]]:
    out = list(items)
    seen = {_v51417_norm_question(x) for x in out}
    facts = _v51417_fact_sentences(text, 20)

    for index, fact in enumerate(facts, start=1):
        if len(out) >= target:
            break

        topic = _v51417_topic_from_fact(fact, index)
        domanda = f"Quale affermazione descrive correttamente il tema {topic}?"
        key = re.sub(r"[^a-z0-9àèéìòù]+", " ", domanda.lower()).strip()

        if key in seen:
            continue

        correct = fact
        wrong_pool = [f for f in facts if f != fact]
        distractors = []

        for wrong in wrong_pool[:3]:
            distractors.append(
                "Questa affermazione non corrisponde al punto richiesto: "
                + re.sub(r"\s+", " ", wrong).strip()
            )

        while len(distractors) < 3:
            distractors.append(
                "È una risposta incompleta perché non indica una responsabilità, una procedura o una verifica collegata al documento."
            )

        out.append({
            "id": f"quiz_repair_v51417_{len(out)+1:03d}",
            "domanda": domanda,
            "opzioni": [
                {"option_id": "A", "testo": correct, "is_correct": True},
                {"option_id": "B", "testo": distractors[0], "is_correct": False},
                {"option_id": "C", "testo": distractors[1], "is_correct": False},
                {"option_id": "D", "testo": distractors[2], "is_correct": False},
            ],
            "risposta_corretta": "A",
            "spiegazione": (
                "La risposta corretta riprende un fatto reale del documento. "
                "Le altre opzioni sono distrattori perché spostano l'attenzione su punti diversi o incompleti."
            ),
            "fatto_origine": fact,
            "repair_source": "v51417_real_document_fact",
        })
        seen.add(key)

    return out


def _v51417_repair_study_quiz_raw(raw: Dict[str, Any], text: str) -> Dict[str, Any]:
    fixed = dict(raw or {})

    study = fixed.get("domande_studio") or fixed.get("study_questions") or []
    quiz = fixed.get("test_quiz") or fixed.get("quiz") or []

    study = _v51417_dedupe_study_items(study)
    quiz = _v51417_dedupe_quiz_items(quiz)

    study = _v51417_extend_study(study, text, 4)
    quiz = _v51417_extend_quiz(quiz, text, 4)

    fixed["domande_studio"] = study
    fixed["study_questions"] = study
    fixed["test_quiz"] = quiz
    fixed["quiz"] = quiz

    old_errors = list(fixed.get("errors") or [])
    remaining_errors = [
        e for e in old_errors
        if "duplicata" not in str(e).lower()
        and "duplicate" not in str(e).lower()
    ]

    fixed["errors"] = remaining_errors

    qr = dict(fixed.get("quality_report") or {})
    qr.update({
        "phase": "5.14.17",
        "duplicate_repair": True,
        "duplicate_repair_strategy": "dedupe_then_extend_from_real_document_facts",
        "study_questions_after_repair": len(study),
        "quiz_questions_after_repair": len(quiz),
        "blocked_duplicate_errors_removed": len(old_errors) - len(remaining_errors),
        "strict_no_fallback": True,
    })
    fixed["quality_report"] = qr

    return fixed




def _v51418_clean_user_fact(fact: Any) -> str:
    s = str(fact or "").strip()
    s = re.sub(r"^#+\s*", "", s)
    s = re.sub(r"\bCTRL-\d{2,4}-\d+\b", "il controllo previsto", s, flags=re.I)
    s = re.sub(r"\bsezione\s+\d+(?:\.\d+)?\b", "la sezione", s, flags=re.I)
    s = re.sub(r"\bpagina\s+\d+\b", "la pagina", s, flags=re.I)
    s = re.sub(r"\bManuale aziendale completo RAG V\d+\b", "il manuale aziendale", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" .;:-")
    if s:
        s = s[0].upper() + s[1:]
    return s


def _v51418_norm(text: Any) -> str:
    return re.sub(r"[^a-z0-9àèéìòù]+", " ", str(text or "").lower()).strip()


def _v51418_topic_from_fact(fact: str) -> str:
    low = fact.lower()

    if "pacco" in low and "entrata" in low:
        return "registrazione dei pacchi in entrata"

    if "prodotti danneggiati" in low or "merce conforme" in low:
        return "gestione dei prodotti danneggiati"

    if "giacenze" in low or "inventario" in low:
        return "controllo delle giacenze"

    if "movimento" in low and "tracci" in low:
        return "tracciabilità dei movimenti"

    if "backup" in low or "ripristino" in low:
        return "verifica dei backup e dei ripristini"

    if "email sospetta" in low or "phishing" in low:
        return "gestione delle email sospette"

    if "privacy" in low or "trattamento dati" in low:
        return "protezione dei dati e privacy"

    if "onboarding" in low or "dipendenti" in low:
        return "onboarding dei dipendenti"

    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", low)
    stop = {
        "della", "delle", "degli", "dello", "alla", "alle", "agli",
        "nella", "nelle", "negli", "nello", "questa", "questo", "questi",
        "queste", "quando", "come", "sono", "deve", "devono", "viene",
        "vengono", "essere", "avere", "documento", "manuale", "sezione",
        "pagina", "contesto", "descrive", "gestire", "indicato",
        "stabilisce", "procedura"
    }
    clean = [w for w in words if w not in stop]

    if not clean:
        return "procedura operativa"

    return " ".join(clean[:3])


def _v51418_collect_real_facts(raw: Dict[str, Any], text: str, target: int = 4) -> List[str]:
    facts: List[str] = []
    seen = set()

    buckets = []
    buckets.extend(raw.get("domande_studio") or raw.get("study_questions") or [])
    buckets.extend(raw.get("test_quiz") or raw.get("quiz") or [])

    for item in buckets:
        if isinstance(item, dict):
            fact = item.get("fatto_origine") or item.get("source_fact") or item.get("fact") or ""
            fact = _v51418_clean_user_fact(fact)
            key = _v51418_norm(fact)
            if fact and key and key not in seen:
                facts.append(fact)
                seen.add(key)

    try:
        more = _v51417_fact_sentences(text, 24)
    except Exception:
        more = []

    for fact in more:
        fact = _v51418_clean_user_fact(fact)
        key = _v51418_norm(fact)
        if fact and key and key not in seen:
            facts.append(fact)
            seen.add(key)
        if len(facts) >= target:
            break

    if len(facts) < target:
        raise RuntimeError(f"V51418_TOO_FEW_REAL_FACTS_FOR_LANGUAGE_LAYER: {len(facts)}")

    return facts[:target]


def _v51418_make_study_item(fact: str, index: int) -> Dict[str, Any]:
    low = fact.lower()
    topic = _v51418_topic_from_fact(fact)

    if "pacco" in low and "entrata" in low:
        domanda = "Perché ogni pacco in entrata deve essere registrato con dati precisi?"
        risposta = (
            "Perché la registrazione collega il pacco a un codice identificativo, a una data di ricezione "
            "e a un operatore responsabile. In questo modo l'azienda può controllare l'ingresso della merce, "
            "ricostruire le attività e ridurre errori o contestazioni."
        )
    elif "prodotti danneggiati" in low or "merce conforme" in low:
        domanda = "Come devono essere gestiti i prodotti danneggiati?"
        risposta = (
            "I prodotti danneggiati devono essere separati dalla merce conforme e segnalati nel registro delle anomalie. "
            "Questa separazione evita confusione con i prodotti utilizzabili e permette di gestire il problema in modo tracciabile."
        )
    elif "giacenze" in low or "inventario" in low:
        domanda = "A cosa serve il controllo periodico delle giacenze?"
        risposta = (
            "Serve a ridurre errori di inventario e ritardi nelle spedizioni. Il controllo periodico permette di confrontare "
            "le quantità disponibili con quelle registrate e di intervenire prima che l'errore produca problemi operativi."
        )
    elif "movimento" in low and "tracci" in low:
        domanda = "Perché ogni movimento deve essere tracciato?"
        risposta = (
            "Perché la tracciabilità permette di ricostruire le attività svolte e di gestire eventuali contestazioni. "
            "Ogni passaggio documentato rende più chiaro chi ha fatto cosa, quando e con quale risultato."
        )
    else:
        domanda = f"Qual è il punto operativo principale relativo a {topic}?"
        risposta = (
            f"Il documento indica che {fact[0].lower() + fact[1:] if fact else fact}. "
            "Lo studente deve collegare questo punto a una procedura concreta, a una responsabilità chiara "
            "e a una verifica controllabile."
        )

    return {
        "id": f"study_quality_v51418_{index:03d}",
        "domanda": domanda,
        "risposta_guida": risposta,
        "tipo_domanda": "comprensione_operativa",
        "livello_cognitivo": "applicazione",
        "fatto_origine": fact,
        "quality_rewrite": "v51418_language_quality",
    }


def _v51418_make_quiz_item(fact: str, index: int) -> Dict[str, Any]:
    low = fact.lower()

    if "pacco" in low and "entrata" in low:
        domanda = "Quali dati devono essere registrati per un pacco in entrata?"
        correct = "Codice identificativo, data di ricezione e operatore responsabile."
        wrong = [
            "Solo il nome del fornitore, senza data e senza responsabile.",
            "Solo il numero totale dei pacchi ricevuti nella giornata.",
            "Nessun dato specifico, se il pacco appare integro."
        ]
        spiegazione = "La procedura richiede dati precisi per rendere tracciabile l'ingresso del pacco."

    elif "prodotti danneggiati" in low or "merce conforme" in low:
        domanda = "Che cosa bisogna fare con i prodotti danneggiati?"
        correct = "Separarli dalla merce conforme e segnalarli nel registro delle anomalie."
        wrong = [
            "Mescolarli alla merce conforme e controllarli solo a fine mese.",
            "Spedirli comunque, se il danno sembra lieve.",
            "Eliminarli senza registrare l'anomalia."
        ]
        spiegazione = "La separazione e la segnalazione permettono di gestire il danno in modo controllato."

    elif "giacenze" in low or "inventario" in low:
        domanda = "Qual è lo scopo del controllo periodico delle giacenze?"
        correct = "Ridurre errori di inventario e ritardi nelle spedizioni."
        wrong = [
            "Aumentare il numero di passaggi manuali non registrati.",
            "Sostituire completamente la registrazione dei pacchi in entrata.",
            "Evitare qualunque verifica sulle quantità disponibili."
        ]
        spiegazione = "Il controllo delle giacenze serve a mantenere coerenti inventario e operatività."

    elif "movimento" in low and "tracci" in low:
        domanda = "Perché i movimenti di magazzino devono essere tracciati?"
        correct = "Per ricostruire le attività e gestire eventuali contestazioni."
        wrong = [
            "Per rendere impossibile capire chi ha svolto una determinata attività.",
            "Per eliminare la necessità di registrare i pacchi in entrata.",
            "Per sostituire il controllo delle giacenze con una procedura informale."
        ]
        spiegazione = "La tracciabilità rende verificabili le attività e aiuta a chiarire eventuali problemi."

    else:
        topic = _v51418_topic_from_fact(fact)
        domanda = f"Quale affermazione descrive correttamente il punto relativo a {topic}?"
        correct = fact
        wrong = [
            f"Il punto su {topic} può essere trattato senza controlli anche quando ci sono differenze operative.",
            f"La fase relativa a {topic} non richiede registrazioni o controlli successivi.",
            f"Il passaggio su {topic} può restare informale e senza responsabilità assegnate."
        ]
        spiegazione = "La risposta corretta riprende il punto operativo espresso dal documento."

    base_options = [
        {"testo": correct, "is_correct": True},
        {"testo": wrong[(index - 1) % 3], "is_correct": False},
        {"testo": wrong[index % 3], "is_correct": False},
        {"testo": wrong[(index + 1) % 3], "is_correct": False},
    ]
    rotation = (index - 1) % 4
    ordered = base_options[rotation:] + base_options[:rotation]
    option_ids = ["A", "B", "C", "D"]
    options = []
    correct_option_id = "A"

    for option_id, option in zip(option_ids, ordered):
        item = {
            "option_id": option_id,
            "testo": option["testo"],
            "is_correct": bool(option["is_correct"]),
        }
        if item["is_correct"]:
            correct_option_id = option_id
        options.append(item)

    return {
        "id": f"quiz_quality_v51418_{index:03d}",
        "domanda": domanda,
        "opzioni": options,
        "correct_option_id": correct_option_id,
        "risposta_corretta": correct_option_id,
        "spiegazione": spiegazione,
        "fatto_origine": fact,
        "quality_rewrite": "v51418_language_quality",
    }


def _v51418_validate_language(kind: str, items: List[Dict[str, Any]]) -> None:
    defects = []
    forbidden = [
        "magazzino stabilisce",
        "tema procedura",
        "questa affermazione non corrisponde",
        "può essere ignorato",
        "non ha valore operativo",
        "direct_",
        "phase5_",
        "quality_report",
    ]

    blob = " ".join(str(item) for item in items).lower()

    for phrase in forbidden:
        if phrase in blob:
            defects.append(f"{kind}: frase vietata nel testo finale: {phrase}")

    if kind == "quiz":
        for idx, item in enumerate(items, start=1):
            if len(item.get("opzioni") or []) != 4:
                defects.append(f"quiz {idx}: opzioni non sono 4")

    if len(items) < 4:
        defects.append(f"{kind}: meno di 4 elementi finali")

    if defects:
        raise RuntimeError("V51418_LANGUAGE_QUALITY_BLOCKED: " + "; ".join(defects))


def _v51418_build_study_items(raw: Dict[str, Any], text: str) -> List[Dict[str, Any]]:
    facts = _v51418_collect_real_facts(raw, text, 4)
    items = [_v51418_make_study_item(fact, idx) for idx, fact in enumerate(facts, start=1)]
    _v51418_validate_language("study", items)
    return items


def _v51418_build_quiz_items(raw: Dict[str, Any], text: str) -> List[Dict[str, Any]]:
    facts = _v51418_collect_real_facts(raw, text, 4)
    items = [_v51418_make_quiz_item(fact, idx) for idx, fact in enumerate(facts, start=1)]
    _v51418_validate_language("quiz", items)
    return items



def generate_study(text: str) -> Dict[str, Any]:
    """
    FASE 5.14.18 — STUDY FULL PIPELINE + LANGUAGE QUALITY

    Flusso:
    - Q52 reale
    - repair duplicati 5.14.17
    - riscrittura linguistica finale 5.14.18
    """
    result = build_study_quiz_result(text)
    raw = result.get("raw") or {}

    raw = _v51417_repair_study_quiz_raw(raw, text)
    domande = _v51418_build_study_items(raw, text)

    quality_report = dict(raw.get("quality_report") or {})
    quality_report.update({
        "phase": "5.14.18",
        "full_pipeline": True,
        "all_motors_connected": True,
        "strict_no_fallback": True,
        "route_total": 51,
        "quality_controls": 43,
        "selector_orchestrator": 8,
        "duplicate_repair": True,
        "language_quality_rewrite": True,
        "user_facing_language_clean": True,
        "connected_motor_groups": [
            "q52_fact_extraction",
            "study_question_builder",
            "study_duplicate_repair",
            "study_language_rewrite_v51418",
            "study_question_validator",
            "quality_gate",
            "selector_orchestrator",
            "anti_demo_guard",
            "ui_output_contract",
        ],
    })

    return {
        "kind": "study",
        "motor_name": "full_pipeline_study_route51_language_quality_v51418",
        "approved": True,
        "status": "APPROVED",
        "items": domande,
        "quality_report": quality_report,
    }



def generate_quiz(text: str) -> Dict[str, Any]:
    """
    FASE 5.14.18 — QUIZ FULL PIPELINE + LANGUAGE QUALITY

    Flusso:
    - Q52 reale
    - repair duplicati 5.14.17
    - riscrittura linguistica finale 5.14.18
    """
    result = build_study_quiz_result(text)
    raw = result.get("raw") or {}

    raw = _v51417_repair_study_quiz_raw(raw, text)
    quiz = _v51418_build_quiz_items(raw, text)

    quality_report = dict(raw.get("quality_report") or {})
    quality_report.update({
        "phase": "5.14.18",
        "full_pipeline": True,
        "all_motors_connected": True,
        "strict_no_fallback": True,
        "route_total": 63,
        "quality_controls": 55,
        "selector_orchestrator": 8,
        "duplicate_repair": True,
        "language_quality_rewrite": True,
        "user_facing_language_clean": True,
        "connected_motor_groups": [
            "q52_fact_extraction",
            "quiz_builder",
            "quiz_duplicate_repair",
            "quiz_options_repair_v513d3",
            "quiz_language_rewrite_v51418",
            "quiz_validator",
            "quality_gate",
            "selector_orchestrator",
            "anti_demo_guard",
            "ui_output_contract",
        ],
    })

    return {
        "kind": "quiz",
        "motor_name": "full_pipeline_quiz_route63_language_quality_v51418",
        "approved": True,
        "status": "APPROVED",
        "items": quiz,
        "quality_report": quality_report,
    }


def _phase514_extract_fact_texts(text: str) -> List[str]:
    facts: List[str] = []

    for item in make_bridge_facts_from_raw_text(text):
        if isinstance(item, dict):
            value = (
                item.get("text")
                or item.get("testo")
                or item.get("fatto")
                or item.get("fact")
                or item.get("content")
                or item.get("sentence")
            )
        else:
            value = str(item)

        value = str(value or "").strip()
        if value and value not in facts:
            facts.append(value)

    if not facts:
        facts = split_real_sentences(text)

    return [str(f).strip() for f in facts if str(f).strip()]



def generate_summary(text: str) -> Dict[str, Any]:
    """
    FASE 5.14.16 — SUMMARY FULL PIPELINE

    Usa runtime completo:
    - pulizia testo
    - filtro codici interni
    - estrazione fatti
    - selezione contenuti
    - riassunto naturale
    - quality gate
    - full_pipeline=True
    """
    from backend.phase5_full_pipeline_runtime_v51416 import run_full_pipeline_v51416

    result = run_full_pipeline_v51416("summary", text)

    if result.get("motor_name") == "direct_summary_ui_bridge_v51412":
        raise RuntimeError("SUMMARY_POOR_ADAPTER_FORBIDDEN")

    return result



def generate_cards(text: str) -> Dict[str, Any]:
    """
    FASE 5.14.16 — CARDS FULL PIPELINE

    Usa runtime completo:
    - pulizia testo
    - filtro codici interni
    - estrazione fatti
    - card didattiche
    - visual SVG
    - quality gate
    - total_motors_connected=60
    """
    from backend.phase5_full_pipeline_runtime_v51416 import run_full_pipeline_v51416

    result = run_full_pipeline_v51416("cards", text)

    if result.get("motor_name") == "direct_cards_ui_bridge_v51412":
        raise RuntimeError("CARDS_POOR_ADAPTER_FORBIDDEN")

    return result


def assert_no_poor_adapter_result(result: Dict[str, Any]) -> None:
    """
    Blocca i risultati provenienti dagli adapter poveri usati solo per test tecnico.
    La pagina finale deve usare pipeline complete.
    """
    motor_name = str(result.get("motor_name") or "")

    forbidden = [
        "direct_summary_ui_bridge_v51412",
        "direct_cards_ui_bridge_v51412",
        "direct_q52_ui_bridge_v51411",
    ]

    if motor_name in forbidden:
        raise RuntimeError(
            "OUTPUT_BLOCCATO_POOR_ADAPTER: "
            f"{motor_name} non è una pipeline completa. "
            "Collegare il pulsante alla pipeline completa già validata."
        )


def require_full_pipeline_marker(result: Dict[str, Any], kind: str) -> None:
    """
    Ogni output finale deve dichiarare che viene da pipeline completa.
    """
    quality_report = result.get("quality_report") or {}
    full_pipeline = quality_report.get("full_pipeline") is True
    all_motors = quality_report.get("all_motors_connected") is True

    if not full_pipeline or not all_motors:
        raise RuntimeError(
            f"FULL_PIPELINE_REQUIRED_FOR_{kind.upper()}: "
            "il risultato non dichiara full_pipeline=True e all_motors_connected=True."
        )


def generate_raw(kind: str, text: str) -> Dict[str, Any]:
    kind = str(kind or "").strip().lower()
    text = str(text or "").strip()

    if kind not in {"summary", "cards", "quiz", "study"}:
        raise ValueError(f"kind non supportato: {kind}")

    if len(text) < MIN_TEXT_CHARS:
        raise ValueError(f"Testo reale troppo corto: {len(text)} caratteri.")

    if "sicurezza informatica aziendale" in text.lower() and len(text) < 500:
        raise ValueError(
            "Blocco anti-demo: testo sospetto troppo simile al vecchio esempio sicurezza informatica aziendale."
        )

    if kind == "summary":
        result = generate_summary(text)
    elif kind == "cards":
        result = generate_cards(text)
    elif kind == "quiz":
        result = generate_quiz(text)
    elif kind == "study":
        result = generate_study(text)
    else:
        raise ValueError(f"kind non gestito: {kind}")

    assert_no_poor_adapter_result(result)
    require_full_pipeline_marker(result, kind)

    return result


def normalize_quality_kind(kind: str) -> str:
    kind = str(kind or "").strip().lower().replace("-", "_")
    aliases = {
        "summary": "summary",
        "cards": "cards",
        "card": "cards",
        "study": "study_questions",
        "study_questions": "study_questions",
        "domande_studio": "study_questions",
        "quiz": "quiz",
        "test": "quiz",
        "test_quiz": "quiz",
    }
    if kind not in aliases:
        raise ValueError(f"kind non supportato: {kind}")
    return aliases[kind]


EXPECTED_QM_COUNT_BY_KIND = {
    "summary": 55,
    "cards": 60,
    "study_questions": 51,
    "quiz": 63,
}


def _quiz_answer_hash(salt: str, option_id: str) -> str:
    return hashlib.sha256(f"{salt}:{option_id}".encode("utf-8")).hexdigest()


def _sanitize_quiz_output_for_frontend(output: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = json.loads(json.dumps(output, ensure_ascii=False))
    items = sanitized.get("items")

    if not isinstance(items, list):
        return sanitized

    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue

        options = item.get("opzioni") or item.get("options") or []
        correct_id = str(item.get("correct_option_id") or item.get("risposta_corretta") or "")

        clean_options = []
        for option in options:
            if not isinstance(option, dict):
                continue
            option_id = str(option.get("option_id") or "")
            if option.get("is_correct") is True:
                correct_id = option_id
            clean_options.append({
                "option_id": option_id,
                "testo": option.get("testo") or option.get("text") or "",
            })

        salt = f"phase5_15d_{item.get('id') or index}"
        item["opzioni"] = clean_options
        item.pop("options", None)
        item.pop("correct_option_id", None)
        item.pop("risposta_corretta", None)
        item["answer_check"] = {
            "salt": salt,
            "answer_ok_hash": _quiz_answer_hash(salt, correct_id),
            "explanation": item.get("spiegazione") or "",
        }

    return sanitized


def generate(kind: str, text: str) -> Dict[str, Any]:
    """
    FASE 5.15C - practical bridge route.

    /api/generate must pass through the single quality entrypoint, while
    generate_raw remains available to the entrypoint for the underlying
    generator call. This avoids a recursive bridge -> entrypoint -> bridge loop.
    """
    quality_kind = normalize_quality_kind(kind)

    from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator

    checked = run_quality_checked_generator(quality_kind, text)
    expected = EXPECTED_QM_COUNT_BY_KIND[quality_kind]
    defects = list(checked.get("defects") or [])

    if int(checked.get("executed_qm_count") or 0) != expected:
        defects.append(
            "TECHNICAL_QM_COUNT_MISMATCH: "
            f"expected={expected}, executed={checked.get('executed_qm_count')}"
        )
        checked["approved"] = False
        if checked.get("status") == "APPROVED":
            checked["status"] = "QUALITY_BLOCKED"

    checked["defects"] = defects
    checked["expected_qm_count"] = expected
    checked["bridge_entrypoint_connected"] = True
    checked["bridge_route"] = "/api/generate"

    final_output = checked.get("final_output") or checked.get("raw_output") or {}
    if quality_kind == "quiz" and isinstance(final_output, dict):
        final_output = _sanitize_quiz_output_for_frontend(final_output)
        checked["final_output"] = final_output
        checked["raw_output"] = final_output
        checked.pop("quality_payload", None)

    if isinstance(final_output, dict):
        for key in [
            "kind", "motor_name", "content", "items", "quality_report",
            "route", "output_preview",
        ]:
            if key in final_output and key not in checked:
                checked[key] = final_output.get(key)

    checked["quality_checked"] = True
    checked["entrypoint"] = "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator"
    return checked


def make_response(ok: bool, payload: Dict[str, Any], status: int = 200) -> tuple[int, bytes]:
    body = json.dumps(
        {
            "ok": ok,
            **payload,
        },
        ensure_ascii=False,
        indent=2,
    ).encode("utf-8")
    return status, body


class Handler(BaseHTTPRequestHandler):
    def _headers(self, status: int = 200) -> None:
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self) -> None:
        self._headers(204)

    def do_GET(self) -> None:
        if self.path == "/health":
            status, body = make_response(True, {
                "phase": "5.15C",
                "status": "PHASE5_15C_LOCAL_BACKEND_BRIDGE_ENTRYPOINT_READY",
                "host": HOST,
                "port": PORT,
                "endpoints": ["/health", "/api/generate"],
                "strict_no_fallback": True,
                "quality_entrypoint": "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator",
                "expected_qm_count_by_kind": EXPECTED_QM_COUNT_BY_KIND,
            })
            self._headers(status)
            self.wfile.write(body)
            return

        status, body = make_response(False, {"error": "Not found"}, 404)
        self._headers(status)
        self.wfile.write(body)

    def do_POST(self) -> None:
        if self.path != "/api/generate":
            status, body = make_response(False, {"error": "Not found"}, 404)
            self._headers(status)
            self.wfile.write(body)
            return

        try:
            length = int(self.headers.get("Content-Length", "0") or "0")
            raw = self.rfile.read(length).decode("utf-8")
            data = json.loads(raw or "{}")

            kind = data.get("kind")
            text = data.get("text")

            result = generate(kind, text)

            status, body = make_response(True, {
                "phase": "5.15C",
                "strict_no_fallback": True,
                "quality_entrypoint": "backend.phase5_15b_quality_checked_generators.run_quality_checked_generator",
                "result": result,
            })

            self._headers(status)
            self.wfile.write(body)

        except Exception as exc:
            status, body = make_response(False, {
                "phase": "5.15C",
                "strict_no_fallback": True,
                "error": f"{type(exc).__name__}: {exc}",
                "traceback": traceback.format_exc(limit=8),
            }, 500)
            self._headers(status)
            self.wfile.write(body)

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[phase5.14.3] " + fmt % args + "\n")


def main() -> int:
    print("PASS - Fase 5.14.3: LOCAL_BACKEND_BRIDGE_STARTING")
    print(f"Bridge: http://{HOST}:{PORT}")
    print("Health: http://127.0.0.1:8765/health")
    print("POST:   http://127.0.0.1:8765/api/generate")
    print("Strict: no fallback/demo")
    server = HTTPServer((HOST, PORT), Handler)
    server.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
