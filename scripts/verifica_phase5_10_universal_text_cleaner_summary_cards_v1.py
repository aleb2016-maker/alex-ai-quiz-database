from __future__ import annotations

import copy
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.phase5_universal_text_cleaner_summary_cards_v1 import (
    apply_universal_text_cleaner_summary_cards_v1,
)


REPORT_JSON = ROOT / "reports" / "phase5_10_universal_text_cleaner_summary_cards_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_10_universal_text_cleaner_summary_cards_v1.md"


BAD_PATTERNS = [
    r"\bInoltre,\s*sì,",
    r"\binoltre,\s*sì,",
    r"\bfatto che\s+sì,",
    r":\s*sì,",
    r"\bal\s+il\b",
    r"\bnon\s+non\b",
    r"\bperchè\b",
    r"\bqualita\b",
    r"\bqual e\b",
    r"\s+[,.!?;:]",
    r"\.\s+[a-zàèéìòù]",
]


def build_test_payload() -> Dict[str, Any]:
    return {
        "riassunto_qualita": {
            "titolo": "Riassunto di qualita",
            "paragrafi": [
                "Il documento evidenzia che il controllo degli accessi limita l'utilizzo dei sistemi interni .",
                "Sul piano operativo emerge che le credenziali non non devono essere condivise tra più operatori. Inoltre, sì, la revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati.",
            ],
            "testo_completo": "TESTO DA RIALLINEARE",
            "fonte_pagine": [1, 2],
        },
        "card_concettuali": [
            {
                "card_id": "phase5_card_001",
                "titolo": "Controllo accessi",
                "contenuto_esplicativo": "Questo elemento si collega anche al fatto che sì, il controllo degli accessi limita l'utilizzo dei sistemi interni .",
                "micro_concetti": ["controllo accessi", "sistemi interni"],
                "fonte_pagine": [1, 2],
            },
            {
                "card_id": "phase5_card_002",
                "titolo": "Revisione periodica",
                "contenuto_esplicativo": "Un punto rilevante riguarda la riduzione del rischio: sì, la revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati.",
                "micro_concetti": ["revisione periodica", "permessi attivi"],
                "fonte_pagine": [1, 2],
            },
        ],
        "quiz_draft": [
            {
                "question_id": "quiz_question_draft_001",
                "question": "Quale regola riguarda la condivisione delle credenziali?",
                "options": [
                    {"option_id": "A", "text": "Le credenziali non devono essere condivise tra più operatori.", "is_correct": True},
                    {"option_id": "B", "text": "Le credenziali possono essere condivise liberamente.", "is_correct": False},
                    {"option_id": "C", "text": "Gli account non devono essere revisionati.", "is_correct": False},
                    {"option_id": "D", "text": "Gli accessi anonimi sono sempre preferibili.", "is_correct": False},
                ],
                "correct_option_id": "A",
                "explanation_draft": "La risposta corretta è stabile.",
            }
        ],
        "study_questions": [
            {
                "question_id": "study_question_001",
                "question": "Perché le credenziali non devono essere condivise?",
                "answer_guide": "Perché la condivisione riduce la responsabilità individuale.",
            }
        ],
    }


def all_summary_card_texts(payload: Dict[str, Any]) -> List[str]:
    texts: List[str] = []

    summary = payload.get("riassunto_qualita")

    if isinstance(summary, dict):
        for key in ["titolo", "testo_completo"]:
            if isinstance(summary.get(key), str):
                texts.append(summary[key])

        paragraphs = summary.get("paragrafi")

        if isinstance(paragraphs, list):
            texts.extend(str(item) for item in paragraphs)

    cards = payload.get("card_concettuali")

    if isinstance(cards, list):
        for card in cards:
            if not isinstance(card, dict):
                continue

            for key in ["titolo", "contenuto_esplicativo"]:
                if isinstance(card.get(key), str):
                    texts.append(card[key])

            concepts = card.get("micro_concetti")

            if isinstance(concepts, list):
                texts.extend(str(item) for item in concepts)

    return texts


def count_bad_patterns(payload: Dict[str, Any]) -> int:
    # Conta per singolo campo, non sul testo unito:
    # altrimenti crea falsi positivi tra titolo/paragrafi/card/micro-concetti.
    total = 0

    for text in all_summary_card_texts(payload):
        for pattern in BAD_PATTERNS:
            # Questo pattern deve essere case-sensitive:
            # ". la" è sospetto, ". La" è corretto.
            flags = 0 if pattern == r"\.\s+[a-zàèéìòù]" else re.IGNORECASE
            total += len(re.findall(pattern, text, flags=flags))

    return total


def count_micro_concepts_with_sentence_punctuation(payload: Dict[str, Any]) -> int:
    total = 0

    cards = payload.get("card_concettuali")

    if not isinstance(cards, list):
        return total

    for card in cards:
        if not isinstance(card, dict):
            continue

        concepts = card.get("micro_concetti")

        if not isinstance(concepts, list):
            continue

        for concept in concepts:
            text = str(concept or "").strip()

            if text.endswith((".", "!", "?")):
                total += 1

    return total


def snapshot_protected_outputs(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "quiz_draft": copy.deepcopy(payload.get("quiz_draft")),
        "study_questions": copy.deepcopy(payload.get("study_questions")),
    }


def changed_rows(before: Dict[str, Any], after: Dict[str, Any]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []

    before_texts = all_summary_card_texts(before)
    after_texts = all_summary_card_texts(after)

    for index, before_text in enumerate(before_texts):
        if index >= len(after_texts):
            continue

        after_text = after_texts[index]

        if before_text != after_text:
            rows.append(
                {
                    "index": index,
                    "before": before_text,
                    "after": after_text,
                }
            )

    return rows


def main() -> int:
    before_payload = build_test_payload()
    after_payload, meta = apply_universal_text_cleaner_summary_cards_v1(copy.deepcopy(before_payload))

    before_bad = count_bad_patterns(before_payload)
    after_bad = count_bad_patterns(after_payload)
    micro_concept_sentence_punctuation_after = count_micro_concepts_with_sentence_punctuation(after_payload)

    protected_before = snapshot_protected_outputs(before_payload)
    protected_after = snapshot_protected_outputs(after_payload)

    rows = changed_rows(before_payload, after_payload)

    errors: List[str] = []

    if before_bad <= 0:
        errors.append("Il payload test non contiene bad pattern iniziali.")

    if after_bad != 0:
        errors.append(f"Bad pattern summary/cards non azzerati: {before_bad} -> {after_bad}")

    if protected_before != protected_after:
        errors.append("Quiz o study questions sono cambiati, ma dovevano restare invariati.")

    if micro_concept_sentence_punctuation_after != 0:
        errors.append(
            f"I micro-concetti sono stati trasformati in frasi: {micro_concept_sentence_punctuation_after}"
        )

    if not meta.get("changed"):
        errors.append("Il cleaner non dichiara modifiche.")

    if meta.get("summary_fields_changed", 0) <= 0:
        errors.append("Il cleaner non ha modificato il riassunto.")

    if meta.get("cards_fields_changed", 0) <= 0:
        errors.append("Il cleaner non ha modificato le card.")

    status = "PASS" if not errors else "FAIL"

    report = {
        "report_name": "phase5_10_universal_text_cleaner_summary_cards_v1",
        "status": status,
        "bad_patterns_before": before_bad,
        "bad_patterns_after": after_bad,
        "protected_outputs_unchanged": protected_before == protected_after,
        "micro_concept_sentence_punctuation_after": micro_concept_sentence_punctuation_after,
        "cleaner_meta": meta,
        "changed_rows": rows,
        "errors": errors,
        "notes": [
            "Test separato: non collega il cleaner al registry.",
            "Il cleaner deve toccare solo riassunto e card.",
            "Quiz e study questions devono restare invariati.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.10 — Universal Text Cleaner Summary/Cards V1\n")
    lines.append(f"- Status: `{status}`")
    lines.append(f"- Bad pattern summary/cards: `{before_bad} -> {after_bad}`")
    lines.append(f"- Protected outputs unchanged: `{protected_before == protected_after}`")
    lines.append(f"- Micro-concepts sentence punctuation after: `{micro_concept_sentence_punctuation_after}`")
    lines.append(f"- Summary fields changed: `{meta.get('summary_fields_changed')}`")
    lines.append(f"- Cards fields changed: `{meta.get('cards_fields_changed')}`")
    lines.append("")
    lines.append("## Modifiche osservate\n")
    lines.append("| # | Prima | Dopo |")
    lines.append("|---:|---|---|")

    for item in rows:
        lines.append(f"| {item['index']} | {item['before']} | {item['after']} |")

    if errors:
        lines.append("")
        lines.append("## Errori\n")

        for error in errors:
            lines.append(f"- {error}")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.10 UNIVERSAL TEXT CLEANER SUMMARY/CARDS PASS" if status == "PASS" else "❌ FASE 5.10 FAIL")
    print(f"Bad pattern summary/cards: {before_bad} -> {after_bad}")
    print(f"Protected outputs unchanged: {protected_before == protected_after}")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    if status != "PASS":
        print(json.dumps({"errors": errors}, ensure_ascii=False, indent=2))
        raise AssertionError("Fase 5.10 fallita: vedi report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
