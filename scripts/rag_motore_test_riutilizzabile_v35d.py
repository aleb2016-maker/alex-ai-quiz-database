#!/usr/bin/env python3
"""
RAG Motore Test Riutilizzabile V3.5D

Modulo separato per il ramo TEST.

Regola architetturale:
- card / riassunti / domande studio = motore didattico V3.5C
- test / opzioni / distrattori / risposta corretta = motore test V3.5D

Il motore mantiene i campi interni validati dai motori quiz:
- opzioni
- risposta_corretta

E genera campi visibili puliti per UI/PDF/app:
- opzioni_visibili
- risposta_corretta_visibile
- mappa_opzioni_v35d
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


BAD_PREFIXES = [
    "Concetto:",
    "Aspetto:",
    "Focus:",
    "Punto del documento:",
    "Informazione:",
    "Riepilogo:",
]


def normalizza_spazi(value: str) -> str:
    text = " ".join(str(value or "").split()).strip()
    text = text.replace(" .", ".")
    text = text.replace(" ,", ",")
    text = text.replace(" ;", ";")
    text = text.replace(" :", ":")
    text = text.replace("..", ".")
    return text


def normalize_key(value: str) -> str:
    text = normalizza_spazi(value).lower()
    text = re.sub(r"[^\wàèéìòùç]+", " ", text)
    return " ".join(text.split())


def sentence(value: str) -> str:
    text = normalizza_spazi(value)
    if text and text[-1] not in ".!?":
        text += "."
    return text


def extract_question_title(question: str, fallback: str) -> str:
    match = re.search(r"«([^»]+)»", question or "")
    if match:
        return normalizza_spazi(match.group(1))
    return fallback


def remove_bad_prefix(value: str) -> str:
    text = normalizza_spazi(value)

    for prefix in BAD_PREFIXES:
        if text.startswith(prefix):
            text = text[len(prefix):].strip()

    return sentence(text)


def make_unique_visible_option(base: str, question_title: str, seen_global: Counter[str]) -> str:
    base = sentence(base)
    key = normalize_key(base)

    if seen_global[key] == 0:
        seen_global[key] += 1
        return base

    # Se una opzione visibile torna uguale in un'altra domanda,
    # la rendiamo specifica per il contesto senza toccare l'opzione interna.
    contextual = sentence(f"Nel contesto di «{question_title}», {base[:1].lower() + base[1:]}")
    contextual_key = normalize_key(contextual)

    seen_global[contextual_key] += 1
    return contextual


def refine_single_test(item: dict[str, Any], index: int, seen_global: Counter[str]) -> dict[str, Any]:
    t = dict(item)

    question = normalizza_spazi(t.get("domanda", ""))
    question_title = extract_question_title(question, f"domanda {index}")

    internal_options = list(t.get("opzioni", []) or [])
    internal_correct = t.get("risposta_corretta", "")

    visible_options = []
    option_map = []
    visible_correct = ""

    for opt_index, internal in enumerate(internal_options, start=1):
        base_visible = remove_bad_prefix(internal)
        visible = make_unique_visible_option(base_visible, question_title, seen_global)

        is_correct = internal == internal_correct

        if is_correct:
            visible_correct = visible

        visible_options.append(visible)
        option_map.append({
            "indice": opt_index,
            "opzione_interna": internal,
            "opzione_visibile": visible,
            "corretta": is_correct,
        })

    if not visible_correct and visible_options:
        # fallback protetto: se la corretta interna non è stata trovata,
        # il validatore lo segnalerà; qui evitiamo campo vuoto.
        visible_correct = visible_options[0]

    t["domanda"] = question
    t["domanda_visibile"] = question
    t["opzioni"] = internal_options
    t["risposta_corretta"] = internal_correct
    t["opzioni_visibili"] = visible_options
    t["risposta_corretta_visibile"] = visible_correct
    t["mappa_opzioni_v35d"] = option_map
    t["ramo_output"] = "test_rag_v35d"
    t["fonte_visibile"] = t.get("fonte_visibile") or "Fonte: sezione test."

    return t


def validate_tests(tests: list[dict[str, Any]]) -> dict[str, Any]:
    errors = []
    warnings = []

    visible_global = []
    internal_global = []

    for idx, test in enumerate(tests, start=1):
        internal_options = test.get("opzioni", []) or []
        visible_options = test.get("opzioni_visibili", []) or []
        internal_correct = test.get("risposta_corretta", "")
        visible_correct = test.get("risposta_corretta_visibile", "")
        option_map = test.get("mappa_opzioni_v35d", []) or []

        if len(internal_options) != 4:
            errors.append(f"test {idx}: opzioni interne diverse da 4")

        if len(visible_options) != 4:
            errors.append(f"test {idx}: opzioni visibili diverse da 4")

        if len(option_map) != 4:
            errors.append(f"test {idx}: mappa opzioni diversa da 4")

        if internal_correct not in internal_options:
            errors.append(f"test {idx}: risposta corretta interna assente")

        if visible_correct not in visible_options:
            errors.append(f"test {idx}: risposta corretta visibile assente")

        if len({normalize_key(o) for o in visible_options}) != len(visible_options):
            errors.append(f"test {idx}: opzioni visibili duplicate nella stessa domanda")

        for opt in visible_options:
            for prefix in BAD_PREFIXES:
                if prefix in opt:
                    errors.append(f"test {idx}: prefisso brutto visibile: {prefix}")

        correct_rows = [row for row in option_map if row.get("corretta")]
        if len(correct_rows) != 1:
            errors.append(f"test {idx}: mappa risposta corretta non univoca")

        if correct_rows:
            row = correct_rows[0]
            if row.get("opzione_interna") != internal_correct:
                errors.append(f"test {idx}: mappa corretta interna incoerente")
            if row.get("opzione_visibile") != visible_correct:
                errors.append(f"test {idx}: mappa corretta visibile incoerente")

        visible_global.extend(normalize_key(o) for o in visible_options)
        internal_global.extend(normalize_key(o) for o in internal_options)

    repeated_visible = [k for k, c in Counter(visible_global).items() if c > 1]
    if repeated_visible:
        errors.append(f"opzioni visibili ripetute globalmente: {len(repeated_visible)}")

    repeated_internal = [k for k, c in Counter(internal_global).items() if c > 2]
    if repeated_internal:
        warnings.append(f"opzioni interne ripetute oltre soglia bridge: {len(repeated_internal)}")

    return {
        "ok": not errors,
        "errori": errors,
        "avvisi": warnings,
        "domande_test": len(tests),
        "opzioni_visibili": len(visible_global),
    }


def refine_output(output: dict[str, Any]) -> dict[str, Any]:
    new = dict(output)

    seen_global: Counter[str] = Counter()
    tests = []

    for index, item in enumerate(new.get("test", []) or [], start=1):
        tests.append(refine_single_test(item, index, seen_global))

    new["test"] = tests

    quality_test = validate_tests(tests)

    quality = dict(new.get("controlli_qualita", {}))
    quality["motore_test_v35d"] = quality_test
    quality["ok"] = bool(quality.get("ok", True)) and quality_test["ok"]

    new["controlli_qualita"] = quality
    new["motori_riutilizzabili"] = dict(new.get("motori_riutilizzabili", {}))
    new["motori_riutilizzabili"]["test"] = "rag_motore_test_riutilizzabile_v35d"

    return new


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    data = json.loads(input_path.read_text(encoding="utf-8"))
    refined = refine_output(data)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(refined, ensure_ascii=False, indent=2), encoding="utf-8")

    q = refined["controlli_qualita"]["motore_test_v35d"]

    print("=== RAG MOTORE TEST RIUTILIZZABILE V3.5D ===")
    print("Input:", input_path)
    print("Output:", output_path)
    print("Qualità test OK:", q["ok"])
    print("Domande test:", q["domande_test"])
    print("Opzioni visibili:", q["opzioni_visibili"])

    if q["errori"]:
        print("ERRORI:")
        for e in q["errori"]:
            print("-", e)

    if q["avvisi"]:
        print("AVVISI:")
        for a in q["avvisi"]:
            print("-", a)

    return 0 if q["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
