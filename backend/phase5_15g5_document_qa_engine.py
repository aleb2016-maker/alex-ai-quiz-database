#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.5 - Motore locale Interroga Documento.

Q&A/RAG deterministico su un singolo documento caricato. Non genera quiz,
non genera domande studio e non usa conoscenza esterna.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Sequence

PHASE = "5.15G.5"

NOT_FOUND_ANSWER = "Nel documento non ho trovato informazioni sufficienti per rispondere a questa domanda."

ACCENT_FIXES = {
    "responsabilita": "responsabilità",
    "qualita": "qualità",
    "finche": "finché",
    "attivita": "attività",
    "criticita": "criticità",
    "continuita": "continuità",
    "possibilita": "possibilità",
    "modalita": "modalità",
    "priorita": "priorità",
    "necessita": "necessità",
    "capacita": "capacità",
    "validita": "validità",
    "tracciabilita": "tracciabilità",
    "conformita": "conformità",
}

STOPWORDS = {
    "alla", "alle", "allo", "agli", "della", "delle", "degli", "dello",
    "nella", "nelle", "negli", "nello", "questa", "questo", "questi", "queste",
    "quella", "quello", "sono", "viene", "vengono", "deve", "devono",
    "essere", "avere", "come", "quando", "dopo", "prima", "ogni", "anche",
    "dove", "quale", "quali", "quanto", "cosa", "dice", "documento",
    "spiegami", "spiega", "modo", "semplice", "tema", "principale",
    "punti", "importanti", "indicato", "indicate", "indicati", "per", "con",
    "tra", "fra", "una", "uno", "gli", "dei", "del", "che", "nel", "nei",
    "sul", "sui", "dal", "dai", "sua", "suo", "sue", "il", "lo", "la",
    "le", "e", "o", "a", "di", "da", "in", "su", "al", "ai", "ad", "ed",
    "qual", "quali",
}

QUESTION_EXPANSIONS = {
    "respons": ["responsabilità", "responsabile", "owner", "referente", "team", "ruolo", "autorizzato"],
    "procedur": ["procedura", "processo", "passaggio", "verifica", "controllo", "evidenza"],
    "risch": ["rischio", "rischi", "errore", "incident", "anomalia", "criticità"],
    "scadenz": ["scadenza", "scadenze", "entro", "giornata", "mensile", "trimestrale", "settimanale"],
    "concett": ["concetto", "definizione", "tema", "punto", "argomento"],
}

FALLBACK_DEMO_TERMS = [
    "fallback",
    "demo",
    "fixture",
    "script",
    "raw_output",
    "generator",
    "come ai",
    "non posso accedere al documento",
]

TEMPLATE_PHRASES = [
    "il documento parla di aspetti importanti",
    "questo concetto è importante",
    "la sezione descrive",
    "il documento evidenzia aspetti",
]

METADATA_NOISE_HINTS = [
    "non contiene dati reali",
    "demo ufficiale",
    "fonte di prova",
    "progetto quiz",
    "generare quiz",
    "generare test",
    "documento sintetico lungo per testare",
]

ANSWER_NOISE_HINTS = [
    "http://",
    "https://",
    "<img",
    "<a href",
    "github.com",
    "shields.io",
    "const ",
    "function ",
    "database_quiz",
    "\"opzioni\"",
    "\"risposta_corretta\"",
    "run workflow",
    "summary → artifacts",
    "scarica lo zip",
]

EXTERNAL_QUESTION_HINTS = {
    "petrolio",
    "borsa",
    "meteo",
    "bitcoin",
    "dollaro",
    "euro",
    "presidente",
    "oggi",
}


def _clean_spaces(text: Any) -> str:
    return re.sub(r"[ \t]+", " ", str(text or "").replace("\r", "\n")).strip()


def _finish_sentence(text: Any) -> str:
    clean = re.sub(r"\s+", " ", str(text or "").strip(" \t\r\n-;"))
    if clean and clean[-1] not in ".?!":
        clean += "."
    return clean


def _word_tokens(text: Any) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def _word_count(text: Any) -> int:
    return len(_word_tokens(text))


def _normalize_word(word: str) -> str:
    return str(word or "").lower().strip()


def _keywords(text: Any, keep_question_words: bool = False) -> List[str]:
    words = [_normalize_word(word) for word in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{3,}", str(text or ""))]
    out = []
    for word in words:
        if not keep_question_words and word in STOPWORDS:
            continue
        if len(word) <= 2:
            continue
        out.append(word)
    return out


def _question_terms(question: str) -> List[str]:
    terms = _keywords(question)
    expanded = list(terms)
    question_low = question.lower()
    for marker, extra_terms in QUESTION_EXPANSIONS.items():
        if marker in question_low:
            expanded.extend(extra_terms)
    return list(dict.fromkeys(expanded))


def _fix_accents(text: Any) -> str:
    clean = str(text or "")
    for raw, fixed in ACCENT_FIXES.items():
        clean = re.sub(rf"\b{raw}\b", fixed, clean, flags=re.I)
    return clean


def _split_sentences(text: Any) -> List[str]:
    raw = _clean_spaces(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", raw)
    return [_finish_sentence(part) for part in parts if _word_count(part) >= 5]


def _split_document_chunks(document_text: str, document_title: str = "", max_words: int = 140) -> List[Dict[str, Any]]:
    raw = str(document_text or "").replace("\r", "\n")
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n+", raw) if _word_count(p) >= 8]
    if not paragraphs:
        paragraphs = _split_sentences(raw)

    chunks: List[Dict[str, Any]] = []
    chunk_index = 1
    for paragraph in paragraphs:
        sentences = _split_sentences(paragraph)
        if not sentences:
            continue
        buffer: List[str] = []
        count = 0
        for sentence in sentences:
            sentence_words = _word_count(sentence)
            if buffer and count + sentence_words > max_words:
                text = _finish_sentence(" ".join(buffer))
                chunks.append(
                    {
                        "chunk_id": f"chunk_{chunk_index:04d}",
                        "text": text,
                        "score": 0.0,
                        "document_title": document_title,
                        "word_count": _word_count(text),
                    }
                )
                chunk_index += 1
                buffer = []
                count = 0
            buffer.append(sentence)
            count += sentence_words
        if buffer:
            text = _finish_sentence(" ".join(buffer))
            chunks.append(
                {
                    "chunk_id": f"chunk_{chunk_index:04d}",
                    "text": text,
                    "score": 0.0,
                    "document_title": document_title,
                    "word_count": _word_count(text),
                }
            )
            chunk_index += 1
    return chunks


def _is_overview_question(question: str) -> bool:
    low = question.lower()
    return any(
        marker in low
        for marker in [
            "tema principale",
            "punti più importanti",
            "punti piu importanti",
            "spiegami",
            "in modo semplice",
            "riassumi",
            "di cosa parla",
        ]
    )


def _looks_external_question(question: str, document_text: str) -> bool:
    q_terms = set(_keywords(question))
    doc_low = document_text.lower()
    return bool(q_terms & EXTERNAL_QUESTION_HINTS) and not any(term in doc_low for term in q_terms & EXTERNAL_QUESTION_HINTS)


def _is_metadata_noise_chunk(text: Any) -> bool:
    low = str(text or "").lower()
    return any(hint in low for hint in METADATA_NOISE_HINTS)


def _is_answer_noise_sentence(text: Any) -> bool:
    clean = str(text or "")
    low = clean.lower()
    if any(hint in low for hint in ANSWER_NOISE_HINTS):
        return True
    if '",' in clean or '",`' in clean:
        return True
    code_marks = clean.count("`") + clean.count("{") + clean.count("}") + clean.count("[") + clean.count("]")
    return code_marks >= 8


def _score_chunk(question_terms: Sequence[str], chunk: Dict[str, Any], rare_terms: Iterable[str]) -> float:
    text = str(chunk.get("text") or "")
    chunk_terms = _keywords(text)
    if not question_terms or not chunk_terms:
        return 0.0
    q_counter = Counter(question_terms)
    c_counter = Counter(chunk_terms)
    common = set(q_counter) & set(c_counter)
    overlap = sum(q_counter[word] * c_counter[word] for word in common)
    rare_boost = sum(1.2 for word in common if word in rare_terms)
    phrase_boost = 0.0
    low = text.lower()
    for word in question_terms:
        if len(word) >= 5 and word in low:
            phrase_boost += 0.15
    norm = max(1.0, len(set(question_terms)) ** 0.5 * len(set(chunk_terms)) ** 0.25)
    return round((overlap + rare_boost + phrase_boost) / norm, 4)


def retrieve_document_evidence(document_text: str, user_question: str, *, document_title: str = "", max_context_chunks: int = 8) -> List[Dict[str, Any]]:
    chunks = _split_document_chunks(document_text, document_title)
    if not chunks:
        return []
    if _looks_external_question(user_question, document_text):
        return []

    question_terms = _question_terms(user_question)
    document_terms = Counter(_keywords(document_text))
    rare_terms = {word for word, count in document_terms.items() if count <= 4}

    if _is_overview_question(user_question):
        scored = []
        overview_pool = chunks[: max(24, max_context_chunks * 3)]
        filtered_pool = [chunk for chunk in overview_pool if not _is_metadata_noise_chunk(chunk.get("text"))]
        if len(filtered_pool) >= max(3, min(max_context_chunks, len(overview_pool))):
            overview_pool = filtered_pool
        for index, chunk in enumerate(overview_pool):
            terms = set(_keywords(chunk["text"]))
            density = len(terms) / max(1, chunk.get("word_count") or 1)
            score = 0.55 + max(0, 10 - index) * 0.03 + min(0.25, density)
            item = dict(chunk)
            item["score"] = round(score, 4)
            scored.append(item)
        return sorted(scored, key=lambda item: item["score"], reverse=True)[:max_context_chunks]

    scored_chunks: List[Dict[str, Any]] = []
    for chunk in chunks:
        score = _score_chunk(question_terms, chunk, rare_terms)
        if score <= 0:
            continue
        item = dict(chunk)
        item["score"] = score
        scored_chunks.append(item)
    scored_chunks.sort(key=lambda item: item["score"], reverse=True)

    threshold = 0.18 if len(question_terms) <= 3 else 0.12
    return [chunk for chunk in scored_chunks if float(chunk["score"]) >= threshold][:max_context_chunks]


def _select_answer_sentences(evidence: Sequence[Dict[str, Any]], question: str, limit: int = 4) -> List[str]:
    q_terms = set(_question_terms(question))
    sentences: List[Dict[str, Any]] = []
    for ev_index, chunk in enumerate(evidence):
        for sentence in _split_sentences(chunk.get("text", "")):
            if _is_answer_noise_sentence(sentence):
                continue
            if _is_overview_question(question) and re.match(r"^L\d+:", sentence.strip()):
                continue
            s_terms = set(_keywords(sentence))
            overlap = len(q_terms & s_terms)
            score = overlap + max(0, 4 - ev_index) * 0.15
            if _is_overview_question(question):
                score += 0.6 if ev_index <= 2 else 0.0
            if overlap or _is_overview_question(question):
                sentences.append({"text": sentence, "score": score})
    sentences.sort(key=lambda item: item["score"], reverse=True)
    out: List[str] = []
    seen = set()
    for item in sentences:
        text = _finish_sentence(_fix_accents(item["text"]))
        key = re.sub(r"[^a-z0-9àèéìòù]+", " ", text.lower()).strip()[:120]
        if key and key not in seen:
            out.append(text)
            seen.add(key)
        if len(out) >= limit:
            break
    return out


def _build_answer(question: str, evidence: Sequence[Dict[str, Any]], answer_style: str = "balanced") -> str:
    selected = _select_answer_sentences(evidence, question, 5 if answer_style == "detailed" else 4)
    if not selected:
        return NOT_FOUND_ANSWER
    question_low = question.lower()
    if "spiegami" in question_low or "modo semplice" in question_low:
        prefix = "In modo semplice, dal documento emerge questo: "
    elif "respons" in question_low:
        prefix = "Nel documento le responsabilità risultano collegate a questi passaggi: "
    elif "procedur" in question_low or "verific" in question_low:
        prefix = "Le procedure o verifiche indicate dal documento sono queste: "
    elif "risch" in question_low:
        prefix = "I rischi citati o implicati nel documento sono collegati a questi punti: "
    elif "scadenz" in question_low:
        prefix = "Le scadenze o frequenze indicate nel documento emergono da questi passaggi: "
    else:
        prefix = "Secondo il documento: "
    answer = prefix + " ".join(selected[:4])
    return _finish_sentence(_fix_accents(answer))


def _count_fallback_demo(text: str) -> int:
    low = text.lower()
    return sum(low.count(term) for term in FALLBACK_DEMO_TERMS)


def _count_template_phrases(text: str) -> int:
    low = text.lower()
    return sum(low.count(term) for term in TEMPLATE_PHRASES)


def _unsupported_claim_count(answer: str, evidence: Sequence[Dict[str, Any]], status: str) -> int:
    if status != "ANSWERED":
        return 0
    evidence_blob = _fix_accents(" ".join(str(item.get("text") or "") for item in evidence)).lower()
    allowed_bridge_terms = {
        "secondo",
        "documento",
        "questo",
        "questi",
        "queste",
        "responsabilità",
        "risultano",
        "collegate",
        "collegati",
        "passaggi",
        "procedure",
        "verifiche",
        "indicate",
        "rischi",
        "citati",
        "implicati",
        "collegati",
        "punti",
        "modo",
        "semplice",
        "emerge",
        "emergono",
        "scadenze",
        "frequenze",
        "informazioni",
        "sufficienti",
        "rispondere",
        "domanda",
        "primo",
        "secondo",
        "terzo",
        "quarto",
    }
    answer_terms = [
        word for word in _keywords(answer)
        if len(word) >= 6 and word not in allowed_bridge_terms
    ]
    unsupported = 0
    for word in dict.fromkeys(answer_terms):
        if word not in evidence_blob:
            unsupported += 1
    return unsupported


def validate_grounded_document_answer(result: Dict[str, Any], document_text: str, user_question: str) -> Dict[str, Any]:
    answer = str(result.get("answer") or "")
    evidence = result.get("evidence") if isinstance(result.get("evidence"), list) else []
    status = str(result.get("status") or "")
    defects: List[str] = []
    warnings: List[str] = []

    if not str(user_question or "").strip():
        defects.append("question_empty")
    if not str(document_text or "").strip():
        defects.append("document_empty")
    if not answer.strip():
        defects.append("answer_empty")
    if status == "ANSWERED" and not evidence:
        defects.append("answered_without_evidence")
    if not evidence and status != "NOT_FOUND_IN_DOCUMENT":
        defects.append("missing_evidence_without_not_found")
    if status == "NOT_FOUND_IN_DOCUMENT" and not result.get("not_found"):
        defects.append("not_found_flag_missing")
    if _count_fallback_demo(answer):
        defects.append("fallback_demo_visible")
    if "non posso accedere al documento" in answer.lower():
        defects.append("claims_no_document_access")
    if "come ai" in answer.lower() or "modello linguistico" in answer.lower():
        defects.append("ai_formula_visible")
    if status == "ANSWERED" and _word_count(answer) < 18:
        warnings.append("answer_short")
    if _count_template_phrases(answer):
        warnings.append("template_phrase_present")

    unsupported = _unsupported_claim_count(answer, evidence, status)
    if unsupported > 2:
        defects.append("unsupported_claims_present")
    elif unsupported:
        warnings.append("minor_unsupported_terms")

    metrics = {
        "question_present": bool(str(user_question or "").strip()),
        "document_present": bool(str(document_text or "").strip()),
        "evidence_chunks": len(evidence),
        "grounded_answer": status == "NOT_FOUND_IN_DOCUMENT" or (status == "ANSWERED" and bool(evidence) and unsupported <= 2),
        "unsupported_claim_count": unsupported,
        "fallback_demo_count": _count_fallback_demo(answer),
        "template_phrase_count": _count_template_phrases(answer),
        "answer_words": _word_count(answer),
        "empty_answer_count": 0 if answer.strip() else 1,
        "generic_answer_count": 1 if status == "ANSWERED" and _word_count(answer) < 18 else 0,
    }
    return {
        "pass": not defects,
        "defects": defects,
        "warnings": warnings,
        "metrics": metrics,
    }


def _confidence_from_evidence(evidence: Sequence[Dict[str, Any]], status: str) -> str:
    if status != "ANSWERED" or not evidence:
        return "low"
    top = max(float(item.get("score") or 0.0) for item in evidence)
    if top >= 1.0 or len(evidence) >= 4:
        return "high"
    if top >= 0.35 or len(evidence) >= 2:
        return "medium"
    return "low"


def answer_document_question(
    document_text: str,
    user_question: str,
    *,
    document_title: str = "",
    max_context_chunks: int = 8,
    answer_style: str = "balanced",
) -> Dict[str, Any]:
    question = _clean_spaces(user_question)
    document = str(document_text or "")
    warnings: List[str] = []

    if not question:
        result = {
            "ok": False,
            "status": "INVALID_QUESTION",
            "question": question,
            "answer": "Scrivi una domanda sul documento per ricevere una risposta basata sul testo caricato.",
            "evidence": [],
            "confidence": "low",
            "not_found": True,
            "warnings": ["question_empty"],
            "metrics": {
                "question_present": False,
                "document_present": bool(document.strip()),
                "evidence_chunks": 0,
                "grounded_answer": False,
                "unsupported_claim_count": 0,
                "fallback_demo_count": 0,
                "template_phrase_count": 0,
                "answer_words": 15,
            },
        }
        return result
    if not document.strip():
        result = {
            "ok": False,
            "status": "INVALID_DOCUMENT",
            "question": question,
            "answer": NOT_FOUND_ANSWER,
            "evidence": [],
            "confidence": "low",
            "not_found": True,
            "warnings": ["document_empty"],
            "metrics": {
                "question_present": True,
                "document_present": False,
                "evidence_chunks": 0,
                "grounded_answer": False,
                "unsupported_claim_count": 0,
                "fallback_demo_count": 0,
                "template_phrase_count": 0,
                "answer_words": _word_count(NOT_FOUND_ANSWER),
            },
        }
        return result

    evidence = retrieve_document_evidence(document, question, document_title=document_title, max_context_chunks=max_context_chunks)
    if not evidence:
        answer = NOT_FOUND_ANSWER
        status = "NOT_FOUND_IN_DOCUMENT"
        not_found = True
    else:
        answer = _build_answer(question, evidence, answer_style)
        status = "ANSWERED" if answer != NOT_FOUND_ANSWER else "NOT_FOUND_IN_DOCUMENT"
        not_found = status != "ANSWERED"
        if not_found:
            evidence = []

    result: Dict[str, Any] = {
        "ok": True,
        "status": status,
        "question": question,
        "answer": answer,
        "evidence": [
            {
                "chunk_id": item.get("chunk_id"),
                "text": _finish_sentence(_fix_accents(item.get("text") or "")),
                "score": float(item.get("score") or 0.0),
            }
            for item in evidence
        ],
        "confidence": _confidence_from_evidence(evidence, status),
        "not_found": not_found,
        "warnings": warnings,
        "metrics": {},
    }
    validation = validate_grounded_document_answer(result, document, question)
    result["warnings"] = list(dict.fromkeys(warnings + validation.get("warnings", [])))
    result["metrics"] = validation["metrics"]
    result["metrics"].update(
        {
            "question_present": True,
            "document_present": True,
            "evidence_chunks": len(result["evidence"]),
            "answer_words": _word_count(result["answer"]),
        }
    )
    if validation.get("defects"):
        result["warnings"].extend(validation["defects"])
    return result


def run_interroga_documento(document_text: str, user_question: str) -> Dict[str, Any]:
    return answer_document_question(document_text, user_question)
