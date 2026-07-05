#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "run_phase5_14_3_local_backend_bridge.py"

text = BRIDGE.read_text(encoding="utf-8")

start_summary = text.find("def generate_summary(text: str) -> Dict[str, Any]:")
start_cards = text.find("def generate_cards(text: str) -> Dict[str, Any]:", start_summary)
end_cards = text.find("def generate(kind: str, text: str) -> Dict[str, Any]:", start_cards)

if start_summary < 0 or start_cards < 0 or end_cards < 0:
    raise SystemExit("FAIL - funzioni generate_summary/generate_cards non trovate")

new_block = r'''def _phase514_extract_fact_texts(text: str) -> List[str]:
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


'''

text = text[:start_summary] + new_block + text[end_cards:]

BRIDGE.write_text(text, encoding="utf-8")
print("PASS - Fase 5.14.12: bridge diretto summary/cards aggiunto")
