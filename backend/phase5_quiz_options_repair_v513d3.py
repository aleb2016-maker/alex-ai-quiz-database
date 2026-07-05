#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.3 — QUIZ OPTIONS REPAIR

Riparatore produttivo leggero per opzioni Test/Quiz:
- elimina "non non";
- sostituisce distrattori quasi uguali alla corretta;
- evita duplicati;
- non cambia la risposta corretta;
- mantiene struttura e numero opzioni.

Funziona sia con dict sia con dataclass/oggetti.
"""

from __future__ import annotations

from difflib import SequenceMatcher
from typing import Any, List


def _get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _set(obj: Any, key: str, value: Any) -> None:
    if isinstance(obj, dict):
        obj[key] = value
    elif hasattr(obj, key):
        setattr(obj, key, value)


def _text(value: Any) -> str:
    return str(value or "").strip()


def _norm(value: Any) -> str:
    return " ".join(_text(value).lower().split())


def _similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, _norm(a), _norm(b)).ratio()


def _options(question: Any) -> List[Any]:
    value = _get(question, "opzioni", None)
    if value is None:
        value = _get(question, "options", [])
    return list(value or [])


def _option_id(option: Any) -> str:
    return _text(_get(option, "option_id", None) or _get(option, "id", ""))


def _option_text(option: Any) -> str:
    return _text(_get(option, "testo", None) or _get(option, "text", ""))


def _set_option_text(option: Any, value: str) -> None:
    if isinstance(option, dict):
        if "testo" in option or "text" not in option:
            option["testo"] = value
        if "text" in option:
            option["text"] = value
    else:
        if hasattr(option, "testo"):
            setattr(option, "testo", value)
        elif hasattr(option, "text"):
            setattr(option, "text", value)


def _is_correct(option: Any, correct_option_id: str) -> bool:
    if bool(_get(option, "is_correct", False)):
        return True
    oid = _option_id(option)
    return bool(correct_option_id and oid == correct_option_id)


def _needs_repair(option_text: str, correct_text: str, used_texts: set[str]) -> bool:
    low = _norm(option_text)

    if not option_text:
        return True

    if "non non" in low or "non  non" in low:
        return True

    if low in used_texts:
        return True

    if correct_text and _similarity(option_text, correct_text) >= 0.94:
        return True

    return False


def _candidate_pool(correct_text: str, question: Any) -> List[str]:
    low = _norm(correct_text)

    if "limita l'utilizzo" in low and "sistemi interni" in low:
        return [
            "Il controllo degli accessi serve solo a produrre statistiche e non governa i permessi sui sistemi.",
            "Il controllo degli accessi riguarda solo l'aspetto grafico dei sistemi e non l'autorizzazione operativa.",
            "Il controllo degli accessi permette a ogni utente di usare qualunque sistema senza vincoli specifici.",
        ]

    if "persona identificabile" in low and "account" in low:
        return [
            "Ogni account può essere condiviso da un gruppo senza collegamento a un responsabile individuale.",
            "Gli account possono restare anonimi quando vengono usati solo per attività interne.",
            "Un account può essere assegnato a un reparto senza indicare una persona responsabile.",
        ]

    if "credenziali" in low and "non devono essere condivise" in low:
        return [
            "Le credenziali possono essere riutilizzate da più operatori se appartengono allo stesso reparto.",
            "La condivisione delle credenziali è ammessa quando velocizza l'accesso ai sistemi comuni.",
            "Più operatori possono usare la stessa credenziale se lavorano sulla stessa procedura.",
        ]

    if "revisione periodica" in low and "riduce il rischio" in low:
        return [
            "La revisione periodica serve solo ad archiviare documenti e non incide sui permessi degli utenti.",
            "La revisione periodica aumenta il rischio perché mantiene attivi tutti i permessi esistenti.",
            "La revisione periodica riguarda solo la descrizione degli utenti e non controlla le autorizzazioni.",
        ]

    concepts = _get(question, "micro_concetti", []) or []
    concept = "controllo operativo"
    if isinstance(concepts, list) and concepts:
        concept = str(concepts[0])

    return [
        f"{concept} viene trattato come un dettaglio descrittivo e non come un vincolo operativo reale.",
        f"{concept} può essere ignorato senza effetti sui controlli indicati dal documento.",
        f"{concept} riguarda solo una nota accessoria e non modifica le responsabilità operative.",
    ]


def _choose_replacement(correct_text: str, question: Any, used_texts: set[str]) -> str:
    for candidate in _candidate_pool(correct_text, question):
        key = _norm(candidate)
        if key in used_texts:
            continue
        if correct_text and _similarity(candidate, correct_text) >= 0.90:
            continue
        used_texts.add(key)
        return candidate

    fallback = "Questa risposta cambia il vincolo operativo indicato dal documento e porta a una conclusione errata."
    counter = 2
    candidate = fallback
    while _norm(candidate) in used_texts:
        candidate = f"{fallback} Variante {counter}."
        counter += 1

    used_texts.add(_norm(candidate))
    return candidate


def repair_test_quiz_options_v513d3(test_quiz: Any) -> Any:
    questions = list(test_quiz or [])

    for question in questions:
        options = _options(question)
        correct_option_id = _text(
            _get(question, "correct_option_id", None)
            or _get(question, "risposta_corretta", "")
        )

        correct_text = ""
        for option in options:
            if _is_correct(option, correct_option_id):
                correct_text = _option_text(option)
                break

        used_texts: set[str] = set()

        for option in options:
            if _is_correct(option, correct_option_id):
                used_texts.add(_norm(_option_text(option)))
                continue

            current = _option_text(option)
            if _needs_repair(current, correct_text, used_texts):
                replacement = _choose_replacement(correct_text, question, used_texts)
                _set_option_text(option, replacement)
            else:
                used_texts.add(_norm(current))

    return test_quiz
