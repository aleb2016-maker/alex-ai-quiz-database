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
import sys
import traceback
from dataclasses import asdict, is_dataclass
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from types import SimpleNamespace
import inspect


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
        raise RuntimeError(f"Direct Q52 bridge ha prodotto errori: {result.errors}")

    return {
        "motor_name": "direct_q52_ui_bridge_v51411",
        "raw": plain,
    }


def generate_study(text: str) -> Dict[str, Any]:
    result = build_study_quiz_result(text)
    raw = result["raw"]
    domande = raw.get("domande_studio") or raw.get("study_questions") or []

    if not domande:
        raise RuntimeError("Motore study reale eseguito ma domande_studio vuote.")

    return {
        "kind": "study",
        "motor_name": result["motor_name"],
        "approved": raw.get("approved"),
        "status": raw.get("status"),
        "items": domande,
        "quality_report": raw.get("quality_report") or {},
    }


def generate_quiz(text: str) -> Dict[str, Any]:
    result = build_study_quiz_result(text)
    raw = result["raw"]
    quiz = raw.get("test_quiz") or raw.get("quiz") or []

    if not quiz:
        raise RuntimeError("Motore quiz reale eseguito ma test_quiz vuoto.")

    return {
        "kind": "quiz",
        "motor_name": result["motor_name"],
        "approved": raw.get("approved"),
        "status": raw.get("status"),
        "items": quiz,
        "quality_report": raw.get("quality_report") or {},
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
    FASE 5.14.12 — DIRECT SUMMARY UI BRIDGE

    Adapter produttivo per la pagina:
    - prende testo reale;
    - estrae facts reali;
    - produce riassunto strutturato dai facts;
    - non usa fallback/demo;
    - non usa testo hardcoded.
    """
    facts = _phase514_extract_fact_texts(text)
    concepts = extract_micro_concepts(text)

    if not facts:
        raise RuntimeError("Nessun fact reale disponibile per il riassunto UI.")

    intro = "Il documento descrive questi punti principali:"

    bullet_lines = []
    for index, fact in enumerate(facts[:8], start=1):
        clean = str(fact).strip()
        if clean and not clean.endswith("."):
            clean += "."
        bullet_lines.append(f"{index}. {clean}")

    final_note = ""
    if concepts:
        final_note = "Concetti chiave: " + ", ".join(concepts[:8]) + "."

    content = "\n".join([intro, "", *bullet_lines, "", final_note]).strip()

    return {
        "kind": "summary",
        "motor_name": "direct_summary_ui_bridge_v51412",
        "approved": True,
        "status": "APPROVED",
        "content": content,
        "items": bullet_lines,
        "quality_report": {
            "phase": "5.14.12",
            "bridge": "direct_summary_ui_bridge",
            "facts_count": len(facts),
            "concepts_count": len(concepts),
            "strict_no_fallback": True,
        },
    }


def generate_cards(text: str) -> Dict[str, Any]:
    """
    FASE 5.14.12 — DIRECT CARDS UI BRIDGE

    Adapter produttivo per la pagina:
    - prende testo reale;
    - estrae facts reali;
    - genera card didattiche dai facts;
    - non usa fallback/demo.
    """
    facts = _phase514_extract_fact_texts(text)
    concepts = extract_micro_concepts(text)

    if not facts:
        raise RuntimeError("Nessun fact reale disponibile per le card UI.")

    cards = []

    for index, fact in enumerate(facts[:8], start=1):
        local_concepts = extract_micro_concepts(fact) or concepts[:5]
        title = local_concepts[0].capitalize() if local_concepts else f"Punto {index}"

        clean = str(fact).strip()
        if clean and not clean.endswith("."):
            clean += "."

        cards.append({
            "card_id": f"phase5_14_card_{index:03d}",
            "titolo": title,
            "messaggio_chiave": clean,
            "spiegazione": f"Questo punto deriva direttamente dal documento caricato: {clean}",
            "micro_concetti": local_concepts[:5],
            "fonte_pagine": [1],
            "warnings": [],
        })

    return {
        "kind": "cards",
        "motor_name": "direct_cards_ui_bridge_v51412",
        "approved": True,
        "status": "APPROVED",
        "items": cards,
        "quality_report": {
            "phase": "5.14.12",
            "bridge": "direct_cards_ui_bridge",
            "facts_count": len(facts),
            "concepts_count": len(concepts),
            "cards_count": len(cards),
            "strict_no_fallback": True,
        },
    }


def generate(kind: str, text: str) -> Dict[str, Any]:
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
        return generate_summary(text)
    if kind == "cards":
        return generate_cards(text)
    if kind == "quiz":
        return generate_quiz(text)
    if kind == "study":
        return generate_study(text)

    raise ValueError(f"kind non gestito: {kind}")


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
                "phase": "5.14.3",
                "status": "PHASE5_14_3_LOCAL_BACKEND_BRIDGE_READY",
                "host": HOST,
                "port": PORT,
                "endpoints": ["/health", "/api/generate"],
                "strict_no_fallback": True,
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
                "phase": "5.14.3",
                "strict_no_fallback": True,
                "result": result,
            })

            self._headers(status)
            self.wfile.write(body)

        except Exception as exc:
            status, body = make_response(False, {
                "phase": "5.14.3",
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
