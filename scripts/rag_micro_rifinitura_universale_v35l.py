#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG V3.5L - micro-rifinitura universale visibile.

Scopo:
- NON corregge frasi specifiche.
- Applica regole generali ai campi visibili dei JSON V3.5K.
- Elimina duplicazioni di etichette tipo "X · X".
- Elimina ripetizioni generiche di apertura tipo "Per verificare...: Per verificare...".
- Non modifica metadati tecnici, id interni o chiavi di controllo.
"""

from __future__ import annotations

import json
import re
from copy import deepcopy
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "dist" / "generated" / "rag_output_cleaner_finale_v35k"
REPORT = ROOT / "reports" / "rag_micro_rifinitura_universale_v35l.md"

VISIBLE_KEYS = {
    "titolo", "title", "sottotitolo", "subtitle",
    "testo", "text", "contenuto", "content", "descrizione", "description",
    "riassunto", "summary", "paragrafo", "paragraph",
    "domanda", "question", "risposta", "answer", "risposta_guida",
    "spiegazione", "explanation", "feedback",
    "opzione", "opzioni", "options", "opzioni_visibili", "risposte", "choices",
    "categoria", "categorie", "categoria_didattica", "categorie_didattiche",
    "sottocategoria", "sottocategorie", "tag", "tags", "badge", "label", "etichette",
    "fonte", "fonti", "source", "sources",
    "messaggio", "message", "note", "nota",
}

# Chiavi tecniche da non toccare, anche se contengono parole come "copiarlo" in un id interno.
TECHNICAL_KEYS = {
    "id", "slug", "key", "chiave", "codice", "code", "tipo", "type",
    "path", "file", "source_file", "engine", "motore", "script",
    "mappa", "mappa_opzioni", "mappa_opzioni_v35d",
    "controlli", "checks", "quality", "qualita", "debug", "metadata", "meta",
    "hash", "score", "ok", "valid", "errore", "errori", "warnings",
}

OPENING_STEMS = [
    "Per verificare di aver capito",
    "Per rispondere bene",
    "Durante il ripasso",
    "Una buona risposta",
    "Per studiare il documento",
    "Per ripassare",
    "Nel riassunto",
    "Il riassunto usa",
]

SEPARATORS = ["·", "-", "–", "—", "|", "/"]


def normalize_for_compare(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[«»\"'“”‘’.,;:!?()\[\]{}]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def collapse_duplicate_label(value: str) -> str:
    """Trasforma genericamente 'X · X' in 'X' solo se le due parti sono davvero uguali."""
    text = value.strip()
    for sep in SEPARATORS:
        if sep not in text:
            continue
        parts = [p.strip() for p in text.split(sep)]
        if len(parts) < 2:
            continue
        normalized = [normalize_for_compare(p) for p in parts if p.strip()]
        if normalized and len(set(normalized)) == 1:
            return parts[0]
    return value


def remove_repeated_opening(value: str) -> str:
    """Rimuove introduzioni ripetute in forma generale: 'stem ...: stem ...'."""
    text = value
    for stem in OPENING_STEMS:
        stem_re = re.escape(stem)
        # Caso: "Per verificare..., ...: Per verificare..." -> conserva la seconda frase.
        pattern = re.compile(
            rf"\b{stem_re}\b[^:.!?]{{0,180}}:\s*(?=\b{stem_re}\b)",
            flags=re.IGNORECASE,
        )
        text = pattern.sub("", text)

        # Caso più semplice: "stem stem" o "stem, stem".
        pattern2 = re.compile(
            rf"\b({stem_re})\b\s*[,;:-]?\s*\b{stem_re}\b",
            flags=re.IGNORECASE,
        )
        text = pattern2.sub(lambda m: m.group(1), text)
    return text


def clean_spacing(value: str) -> str:
    text = value
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:!?])", r"\1", text)
    text = re.sub(r"([¿¡])\s+", r"\1", text)
    text = re.sub(r"([.!?]){2,}", r"\1", text)
    text = re.sub(r"\?\s+\?", "?", text)
    return text.strip()


def clean_visible_text(value: str) -> str:
    before = value
    value = collapse_duplicate_label(value)
    value = remove_repeated_opening(value)
    value = clean_spacing(value)
    return value if value else before


def is_visible_key(key: str) -> bool:
    k = key.strip().lower()
    if k in TECHNICAL_KEYS:
        return False
    if k in VISIBLE_KEYS:
        return True
    # Campo composto visibile: es. risposta_corretta_visibile, testo_card, fonte_visibile.
    visible_fragments = ("titolo", "testo", "domanda", "risposta", "spiegazione", "opzion", "categoria", "tag", "badge", "fonte", "label", "messaggio")
    technical_fragments = ("id", "slug", "path", "file", "hash", "debug", "mappa")
    return any(f in k for f in visible_fragments) and not any(t in k for t in technical_fragments)


def clean_node(node: Any, parent_key: str = "") -> tuple[Any, int]:
    changes = 0
    if isinstance(node, dict):
        out = {}
        for key, value in node.items():
            cleaned, n = clean_node(value, key)
            out[key] = cleaned
            changes += n
        return out, changes

    if isinstance(node, list):
        out_list = []
        for item in node:
            cleaned, n = clean_node(item, parent_key)
            out_list.append(cleaned)
            changes += n
        return out_list, changes

    if isinstance(node, str) and is_visible_key(parent_key):
        cleaned = clean_visible_text(node)
        if cleaned != node:
            changes += 1
        return cleaned, changes

    return node, changes


def iter_visible_strings(node: Any, parent_key: str = "") -> Iterable[str]:
    if isinstance(node, dict):
        for key, value in node.items():
            yield from iter_visible_strings(value, key)
    elif isinstance(node, list):
        for item in node:
            yield from iter_visible_strings(item, parent_key)
    elif isinstance(node, str) and is_visible_key(parent_key):
        yield node


def has_duplicate_label(value: str) -> bool:
    for sep in SEPARATORS:
        if sep not in value:
            continue
        parts = [p.strip() for p in value.split(sep)]
        if len(parts) >= 2:
            normalized = [normalize_for_compare(p) for p in parts if p.strip()]
            if normalized and len(set(normalized)) == 1:
                return True
    return False


def has_repeated_opening(value: str) -> bool:
    for stem in OPENING_STEMS:
        stem_re = re.escape(stem)
        if re.search(rf"\b{stem_re}\b[^:.!?]{{0,180}}:\s*\b{stem_re}\b", value, re.IGNORECASE):
            return True
        if re.search(rf"\b{stem_re}\b\s*[,;:-]?\s*\b{stem_re}\b", value, re.IGNORECASE):
            return True
    return False


def validate_visible(data: Any) -> list[str]:
    errors: list[str] = []
    for value in iter_visible_strings(data):
        if has_duplicate_label(value):
            errors.append(f"tag duplicato visibile: {value[:160]}")
        if has_repeated_opening(value):
            errors.append(f"apertura ripetuta visibile: {value[:160]}")
    return errors


def main() -> int:
    print("=== MICRO RIFINITURA UNIVERSALE RAG V3.5L ===")
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(OUTPUT_DIR.glob("**/output_cleaner_finale_v35k.json"))
    results: list[str] = []
    all_errors: list[str] = []

    if not files:
        msg = f"ERRORE: nessun output trovato in {OUTPUT_DIR}"
        print(msg)
        results.append(msg)
        all_errors.append(msg)

    for path in files:
        rel = path.relative_to(ROOT)
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except Exception as exc:
            msg = f"ERRORE: JSON non leggibile {rel}: {exc}"
            print(msg)
            results.append(msg)
            all_errors.append(msg)
            continue

        original = deepcopy(data)
        cleaned, changes = clean_node(data)
        errors = validate_visible(cleaned)

        if errors:
            for err in errors:
                all_errors.append(f"{rel}: {err}")
            msg = f"ERRORE: {rel} contiene ancora micro-ripetizioni visibili"
            print(msg)
            results.append(msg)
            continue

        if cleaned != original:
            path.write_text(json.dumps(cleaned, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        msg = f"OK: {rel} - modifiche visibili {changes}"
        print(msg)
        results.append(msg)

    report = [
        "# Report RAG Micro Rifinitura Universale V3.5L",
        "",
        "Scopo: micro-correzioni generali sui campi visibili, non patch su frasi specifiche.",
        "",
        "## Regole universali applicate",
        "- tag/categorie duplicate tipo `X · X` -> `X` quando le parti sono davvero uguali",
        "- aperture ripetute tipo `Per verificare...: Per verificare...` rimosse in modo generale",
        "- spazi e punteggiatura visibile normalizzati",
        "- metadati tecnici e id interni ignorati",
        "",
        "## Risultati",
    ]
    report.extend(f"- {line}" for line in results)
    report.extend(["", f"Errori totali: {len(all_errors)}"])
    if all_errors:
        report.append("")
        report.append("## Errori")
        report.extend(f"- {err}" for err in all_errors[:80])
    report.append("")
    report.append("ESITO: " + ("DA CORREGGERE" if all_errors else "OK"))
    REPORT.write_text("\n".join(report) + "\n", encoding="utf-8")

    print(f"Report: {REPORT.relative_to(ROOT)}")
    print("ESITO:", "DA CORREGGERE" if all_errors else "OK")
    return 1 if all_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
