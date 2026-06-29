#!/usr/bin/env python3
"""
RAG Cleaner Finale Visibile V3.5K

Scopo:
collegare il motore di pulizia già esistente a TUTTI i testi visibili finali.

Questo script NON inventa un nuovo revisore linguistico.
Fa il cablaggio finale obbligatorio del cleaner esistente dopo V3.5G / V3.5I / V3.5J.

Campi obbligatori puliti:
- riassunto.titolo
- riassunto.testo_breve
- riassunto.conclusione
- riassunto.punti_chiave[].titolo
- riassunto.punti_chiave[].testo
- card[].titolo
- card[].testo
- card[].messaggio_chiave
- domande_studio[].domanda
- domande_studio[].risposta_guida
- test[].domanda_visibile
- test[].opzioni_visibili[]
- test[].risposta_corretta_visibile
- test[].spiegazione
- test[].mappa_opzioni_v35d[].opzione_visibile

Regola:
se un campo visibile non passa dal cleaner finale, la verifica fallisce.
"""

from __future__ import annotations

import argparse
import importlib.util
import inspect
import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
CONTROL_NAME = "Cleaner finale visibile V3.5K"


CLEANER_CANDIDATES = [
    ROOT / "scripts/rag_revisore_qualita_testuale_v35g.py",
    ROOT / "scripts/motore_qualita_generale.py",
]

CLEANER_FUNCTION_NAMES = [
    "pulisci_visibile",
    "correggi_italiano",
    "normalizza_testo",
    "normalizza_spazi",
    "frase",
]


TEXT_FIELDS_COVERAGE = [
    "riassunto.titolo",
    "riassunto.testo_breve",
    "riassunto.conclusione",
    "riassunto.punti_chiave[].titolo",
    "riassunto.punti_chiave[].testo",
    "card[].titolo",
    "card[].testo",
    "card[].messaggio_chiave",
    "domande_studio[].domanda",
    "domande_studio[].risposta_guida",
    "test[].domanda_visibile",
    "test[].opzioni_visibili[]",
    "test[].risposta_corretta_visibile",
    "test[].spiegazione",
    "test[].mappa_opzioni_v35d[].opzione_visibile",
]


def normalizza_base(value: str) -> str:
    text = str(value or "")
    text = text.replace("\u00a0", " ")
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([,.;:!?])([^\s»”\")])", r"\1 \2", text)
    text = text.replace("..", ".")
    text = text.replace(",.", ".").replace(";.", ".").replace(":.", ".")
    text = re.sub(r"[,;:]\s*$", ".", text)
    return text.strip()


def chiudi_frase(value: str, is_question: bool = False) -> str:
    text = normalizza_base(value)

    if not text:
        return ""

    text = re.sub(
        r"\b(e|o|ma|che|di|a|da|in|con|su|per|tra|fra|del|della|dello|dei|degli|delle)\s*$",
        "",
        text,
        flags=re.IGNORECASE,
    ).rstrip(" ,;:")

    if is_question:
        text = text.rstrip(".!") + "?"
    elif text and text[-1] not in ".!?»”":
        text += "."

    return normalizza_base(text)


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def can_call_with_one_arg(fn: Callable[..., Any]) -> bool:
    try:
        sig = inspect.signature(fn)
    except Exception:
        return True

    required = [
        p for p in sig.parameters.values()
        if p.default is inspect._empty
        and p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
    ]

    return len(required) <= 1


def discover_existing_cleaner() -> tuple[list[Callable[[str], str]], list[str]]:
    functions: list[Callable[[str], str]] = []
    names: list[str] = []

    for path in CLEANER_CANDIDATES:
        if not path.exists():
            continue

        try:
            module = load_module(path)
        except Exception as exc:
            names.append(f"ERRORE_IMPORT:{path.name}:{exc}")
            continue

        if module is None:
            continue

        for fn_name in CLEANER_FUNCTION_NAMES:
            fn = getattr(module, fn_name, None)

            if not callable(fn):
                continue

            if not can_call_with_one_arg(fn):
                continue

            def wrapper(value: str, _fn=fn) -> str:
                result = _fn(value)
                if isinstance(result, str):
                    return result
                return str(result)

            functions.append(wrapper)
            names.append(f"{path.name}.{fn_name}")

    return functions, names


EXISTING_CLEANERS, EXISTING_CLEANER_NAMES = discover_existing_cleaner()


def apply_existing_cleaner(value: str, *, is_question: bool = False) -> str:
    text = normalizza_base(value)

    for cleaner in EXISTING_CLEANERS:
        try:
            cleaned = cleaner(text)
            if isinstance(cleaned, str) and cleaned.strip():
                text = cleaned
        except Exception:
            # Non interrompe la pipeline per una funzione parziale.
            # La verifica finale blocca eventuali testi rimasti sporchi.
            pass

        text = normalizza_base(text)

    text = remove_known_dirty_prefixes(text)
    text = fix_known_agreements(text)
    text = chiudi_frase(text, is_question=is_question)
    return text


def remove_known_dirty_prefixes(value: str) -> str:
    text = normalizza_base(value)

    dirty_prefixes = [
        r"^La scheda spiega «[^»]+» con un'idea precisa:\s*",
        r"^Questa card serve a ricordare «[^»]+» partendo dal suo significato pratico:\s*",
        r"^«[^»]+» viene presentato come punto autonomo di studio:\s*",
        r"^La card su «[^»]+» chiarisce il concetto senza ripetere gli altri punti:\s*",
        r"^Per studiare «[^»]+», il passaggio da fissare è questo:\s*",
        r"^Per rispondere bene, spiega che cosa significa «[^»]+» e collegalo al punto seguente:\s*",
        r"^Durante il ripasso, usa «[^»]+» per ricostruire il concetto con parole tue:\s*",
        r"^Su «[^»]+» devi saper dire qual è il problema o il vantaggio spiegato dal documento:\s*",
        r"^È corretta perché risponde direttamente alla domanda su «[^»]+» e mantiene il significato del documento:\s*",
        r"^La scelta è giusta perché distingue «[^»]+» dai distrattori e riprende il punto richiesto:\s*",
        r"^Questa opzione funziona perché collega «[^»]+» al contenuto essenziale, senza aggiungere informazioni estranee\.?\s*",
    ]

    for pattern in dirty_prefixes:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # Ripulisce prefissi del titolo copiati dentro opzioni/spiegazioni.
    text = re.sub(r"^(sicurezza informatica|rischio e conseguenza|regola operativa|azione consigliata|obiettivi principali)\.\s*", "", text, flags=re.IGNORECASE)

    return normalizza_base(text)


def fix_known_agreements(value: str) -> str:
    text = normalizza_base(value)

    replacements = {
        "Regola operativa» viene presentato": "Regola operativa» viene presentata",
        "Azione consigliata» viene presentato": "Azione consigliata» viene presentata",
        "Sicurezza informatica» viene presentato": "Sicurezza informatica» viene presentata",
        "Obiettivi principali» viene presentato": "Obiettivi principali» vengono presentati",
        "gli obiettivi principali è": "gli obiettivi principali sono",
        "Gli obiettivi principali è": "Gli obiettivi principali sono",
        "obiettivi principali senza copiarlo": "obiettivi principali senza copiarli",
        "Obiettivi principali senza copiarlo": "Obiettivi principali senza copiarli",
        "gli obiettivi principali lo collega": "gli obiettivi principali li collega",
        "gli obiettivi principali collegala": "gli obiettivi principali collegali",
        "la regola operativa lo collega": "la regola operativa la collega",
        "l'azione consigliata lo collega": "l'azione consigliata la collega",
        "e collegalo al punto seguente": "e collega il concetto al documento",
        "quale problema o il vantaggio": "quale problema, vantaggio o funzione",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    return normalizza_base(text)


def clean_string_inplace(parent: dict[str, Any], key: str, coverage: list[str], field_name: str, *, is_question: bool = False) -> None:
    if key not in parent:
        return

    if isinstance(parent.get(key), str):
        parent[key] = apply_existing_cleaner(parent[key], is_question=is_question)
        coverage.append(field_name)


def clean_summary(data: dict[str, Any], coverage: list[str]) -> None:
    r = data.get("riassunto")

    if not isinstance(r, dict):
        return

    clean_string_inplace(r, "titolo", coverage, "riassunto.titolo")
    clean_string_inplace(r, "testo_breve", coverage, "riassunto.testo_breve")
    clean_string_inplace(r, "conclusione", coverage, "riassunto.conclusione")

    for point in r.get("punti_chiave", []) or []:
        if not isinstance(point, dict):
            continue

        clean_string_inplace(point, "titolo", coverage, "riassunto.punti_chiave[].titolo")
        clean_string_inplace(point, "testo", coverage, "riassunto.punti_chiave[].testo")


def clean_cards(data: dict[str, Any], coverage: list[str]) -> None:
    for card in data.get("card", []) or []:
        if not isinstance(card, dict):
            continue

        clean_string_inplace(card, "titolo", coverage, "card[].titolo")
        clean_string_inplace(card, "testo", coverage, "card[].testo")
        clean_string_inplace(card, "messaggio_chiave", coverage, "card[].messaggio_chiave")


def clean_study(data: dict[str, Any], coverage: list[str]) -> None:
    for item in data.get("domande_studio", []) or []:
        if not isinstance(item, dict):
            continue

        clean_string_inplace(item, "domanda", coverage, "domande_studio[].domanda", is_question=True)
        clean_string_inplace(item, "risposta_guida", coverage, "domande_studio[].risposta_guida")


def clean_tests(data: dict[str, Any], coverage: list[str]) -> None:
    for item in data.get("test", []) or []:
        if not isinstance(item, dict):
            continue

        clean_string_inplace(item, "domanda_visibile", coverage, "test[].domanda_visibile", is_question=True)
        clean_string_inplace(item, "spiegazione", coverage, "test[].spiegazione")

        old_options = item.get("opzioni_visibili", []) or []
        old_correct = item.get("risposta_corretta_visibile", "")

        option_map: dict[str, str] = {}
        cleaned_options: list[str] = []

        for option in old_options:
            if not isinstance(option, str):
                continue

            cleaned = apply_existing_cleaner(option)
            option_map[option] = cleaned
            cleaned_options.append(cleaned)
            coverage.append("test[].opzioni_visibili[]")

        if cleaned_options:
            item["opzioni_visibili"] = cleaned_options

        if isinstance(old_correct, str):
            item["risposta_corretta_visibile"] = option_map.get(
                old_correct,
                apply_existing_cleaner(old_correct),
            )
            coverage.append("test[].risposta_corretta_visibile")

        for row in item.get("mappa_opzioni_v35d", []) or []:
            if not isinstance(row, dict):
                continue

            old_visible = row.get("opzione_visibile", "")
            if isinstance(old_visible, str):
                row["opzione_visibile"] = option_map.get(
                    old_visible,
                    apply_existing_cleaner(old_visible),
                )
                coverage.append("test[].mappa_opzioni_v35d[].opzione_visibile")

        # Se la risposta corretta visibile non combacia più, la riallinea usando la mappa.
        options = item.get("opzioni_visibili", []) or []
        correct = item.get("risposta_corretta_visibile", "")

        if correct not in options:
            for row in item.get("mappa_opzioni_v35d", []) or []:
                if row.get("corretta"):
                    candidate = row.get("opzione_visibile", "")
                    if candidate in options:
                        item["risposta_corretta_visibile"] = candidate
                        break


def collect_visible_texts(data: dict[str, Any]) -> list[tuple[str, str]]:
    out: list[tuple[str, str]] = []

    r = data.get("riassunto")
    if isinstance(r, dict):
        for key in ["titolo", "testo_breve", "conclusione"]:
            if isinstance(r.get(key), str):
                out.append((f"riassunto.{key}", r[key]))

        for idx, point in enumerate(r.get("punti_chiave", []) or [], start=1):
            if not isinstance(point, dict):
                continue
            for key in ["titolo", "testo"]:
                if isinstance(point.get(key), str):
                    out.append((f"riassunto.punti_chiave[{idx}].{key}", point[key]))

    for idx, card in enumerate(data.get("card", []) or [], start=1):
        if not isinstance(card, dict):
            continue
        for key in ["titolo", "testo", "messaggio_chiave"]:
            if isinstance(card.get(key), str):
                out.append((f"card[{idx}].{key}", card[key]))

    for idx, item in enumerate(data.get("domande_studio", []) or [], start=1):
        if not isinstance(item, dict):
            continue
        for key in ["domanda", "risposta_guida"]:
            if isinstance(item.get(key), str):
                out.append((f"domande_studio[{idx}].{key}", item[key]))

    for idx, item in enumerate(data.get("test", []) or [], start=1):
        if not isinstance(item, dict):
            continue
        for key in ["domanda_visibile", "risposta_corretta_visibile", "spiegazione"]:
            if isinstance(item.get(key), str):
                out.append((f"test[{idx}].{key}", item[key]))

        for opt_idx, option in enumerate(item.get("opzioni_visibili", []) or [], start=1):
            if isinstance(option, str):
                out.append((f"test[{idx}].opzioni_visibili[{opt_idx}]", option))

        for map_idx, row in enumerate(item.get("mappa_opzioni_v35d", []) or [], start=1):
            if isinstance(row, dict) and isinstance(row.get("opzione_visibile"), str):
                out.append((f"test[{idx}].mappa_opzioni_v35d[{map_idx}].opzione_visibile", row["opzione_visibile"]))

    return out


def validate_final_cleaning(data: dict[str, Any], coverage: list[str]) -> dict[str, Any]:
    errors: list[str] = []

    if not EXISTING_CLEANERS:
        errors.append("nessun cleaner esistente importato: il collegamento al motore pulizia non è attivo")

    required_present = []

    if isinstance(data.get("riassunto"), dict:
        pass)
