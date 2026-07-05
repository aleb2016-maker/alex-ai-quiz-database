from __future__ import annotations

import copy
import re
from typing import Any, Dict, List, Tuple


# FASE 5.10 — UNIVERSAL TEXT CLEANER SUMMARY/CARDS V1
#
# Scopo:
# - pulire testi di riassunto e card;
# - eliminare formule brutte residue tipo "Inoltre, sì,";
# - correggere piccoli difetti di accenti, spazi, punteggiatura;
# - proteggere micro-concetti: niente maiuscola forzata, niente punto finale;
# - non toccare quiz, study questions, opzioni o risposte corrette.
#
# Stato:
# - motore reale separato;
# - non collegato al registry;
# - nessun effetto collaterale su file.


FINAL_BAD_ENDINGS = {
    "e",
    "di",
    "con",
    "per",
    "che",
    "del",
    "della",
    "dello",
    "dei",
    "degli",
    "delle",
}


def normalize_space_v1(value: Any) -> str:
    text = str(value or "").strip()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_basic_text_v1(value: Any) -> str:
    text = str(value or "")

    replacements = [
        (r"\bperchè\b", "perché"),
        (r"\bqual e\b", "qual è"),
        (r"\bpuo\b", "può"),
        (r"\bpiu\b", "più"),
        (r"\bgia\b", "già"),
        (r"\bcioe\b", "cioè"),
        (r"\bcosi\b", "così"),
        (r"\bpero\b", "però"),
        (r"\bqualita\b", "qualità"),
        (r"\bnon\s+non\b", "non"),
        (r"\s+([,.!?;:])", r"\1"),
        (r"([,.!?;:])([^\s])", r"\1 \2"),
        (r"\s{2,}", " "),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return normalize_space_v1(text)


def remove_bad_summary_card_phrases_v1(value: Any) -> str:
    text = clean_basic_text_v1(value)

    # Pattern lunghi prima: così evitiamo residui tipo "al il controllo".
    ordered_patterns = [
        (r"^\s*Questo elemento si collega anche al fatto che\s+sì,\s*", ""),
        (r"^\s*Questo elemento si collega anche al fatto che\s*", ""),
        (r"^\s*Un altro punto da considerare è questo:\s*", ""),
        (r"\bInoltre,\s*sì,\s*", ""),
        (r"\binoltre,\s*sì,\s*", ""),
        (r"\bfatto che\s+sì,\s*", ""),
        (r":\s*sì,\s*", ": "),
        (r"\bche\s+sì,\s+", "che "),
    ]

    for pattern, replacement in ordered_patterns:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return clean_basic_text_v1(text)


def fix_article_collisions_v1(value: Any) -> str:
    text = str(value or "")

    replacements = [
        (r"\bal\s+il\b", "al"),
        (r"\bdel\s+il\b", "del"),
        (r"\bnel\s+il\b", "nel"),
        (r"\bsul\s+il\b", "sul"),
        (r"\balla\s+la\b", "alla"),
        (r"\bdella\s+la\b", "della"),
        (r"\bnella\s+la\b", "nella"),
        (r"\bsulla\s+la\b", "sulla"),
    ]

    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    return text


def capitalize_sentence_starts_v1(value: Any) -> str:
    text = str(value or "")

    def repl(match):
        return match.group(1) + match.group(2).upper()

    return re.sub(r"(^|[.!?]\s+)([a-zàèéìòù])", repl, text)


def remove_suspicious_final_v1(value: Any) -> str:
    text = normalize_space_v1(value)

    if not text:
        return text

    words = re.findall(r"[A-Za-zÀ-ÿ']+", text)

    if not words:
        return text

    last = words[-1].lower().strip("'")

    if last in FINAL_BAD_ENDINGS:
        text = re.sub(r"\b" + re.escape(words[-1]) + r"\s*$", "", text).strip()
        text = text.rstrip(" ,;:")

        if text and text[-1] not in ".!?":
            text += "."

    return text


def clean_summary_card_text_v1(value: Any) -> str:
    text = remove_bad_summary_card_phrases_v1(value)
    text = fix_article_collisions_v1(text)
    text = clean_basic_text_v1(text)
    text = remove_suspicious_final_v1(text)
    text = capitalize_sentence_starts_v1(text)

    if text and text[-1] not in ".!?":
        text += "."

    return text


def clean_plain_label_v1(value: Any) -> str:
    # Etichette/micro-concetti: pulizia minima, niente trasformazione in frase.
    text = clean_basic_text_v1(value)
    text = text.rstrip(".!?;:")
    return text.strip()


def clean_sentence_list_v1(values: Any) -> Tuple[Any, int]:
    if not isinstance(values, list):
        return values, 0

    changed = 0
    out: List[Any] = []

    for item in values:
        if isinstance(item, str):
            fixed = clean_summary_card_text_v1(item)

            if fixed != item:
                changed += 1

            out.append(fixed)
        else:
            out.append(item)

    return out, changed


def clean_label_list_v1(values: Any) -> Tuple[Any, int]:
    if not isinstance(values, list):
        return values, 0

    changed = 0
    out: List[Any] = []

    for item in values:
        if isinstance(item, str):
            fixed = clean_plain_label_v1(item)

            if fixed != item:
                changed += 1

            out.append(fixed)
        else:
            out.append(item)

    return out, changed


def clean_summary_like_v1(summary: Any) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(summary, dict):
        return summary, {
            "changed": False,
            "fields_changed": 0,
            "warnings": ["summary_not_dict"],
        }

    fixed = copy.deepcopy(summary)
    fields_changed = 0

    for key in ["title", "titolo"]:
        if isinstance(fixed.get(key), str):
            cleaned = clean_basic_text_v1(fixed[key])

            if cleaned != fixed[key]:
                fixed[key] = cleaned
                fields_changed += 1

    for key in ["testo_completo", "complete_text", "text"]:
        if isinstance(fixed.get(key), str):
            cleaned = clean_summary_card_text_v1(fixed[key])

            if cleaned != fixed[key]:
                fixed[key] = cleaned
                fields_changed += 1

    for key in ["paragrafi", "paragraphs", "key_points", "punti_chiave"]:
        cleaned_list, changed = clean_sentence_list_v1(fixed.get(key))

        if changed:
            fixed[key] = cleaned_list
            fields_changed += changed

    paragraphs = fixed.get("paragrafi")

    if isinstance(paragraphs, list) and all(isinstance(item, str) for item in paragraphs):
        rebuilt = "\n\n".join(paragraphs)

        if fixed.get("testo_completo") != rebuilt:
            fixed["testo_completo"] = rebuilt
            fields_changed += 1

    return fixed, {
        "changed": fields_changed > 0,
        "fields_changed": fields_changed,
        "warnings": [],
    }


def clean_card_like_v1(card: Any) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(card, dict):
        return card, {
            "changed": False,
            "fields_changed": 0,
            "warnings": ["card_not_dict"],
        }

    fixed = copy.deepcopy(card)
    fields_changed = 0

    for key in ["title", "titolo"]:
        if isinstance(fixed.get(key), str):
            cleaned = clean_basic_text_v1(fixed[key])

            if cleaned != fixed[key]:
                fixed[key] = cleaned
                fields_changed += 1

    for key in [
        "contenuto_esplicativo",
        "message_key",
        "messaggio_chiave",
        "content",
        "text",
        "description",
    ]:
        if isinstance(fixed.get(key), str):
            cleaned = clean_summary_card_text_v1(fixed[key])

            if cleaned != fixed[key]:
                fixed[key] = cleaned
                fields_changed += 1

    # Micro-concetti/etichette: non sono frasi.
    for key in ["micro_concetti", "micro_concepts"]:
        cleaned_list, changed = clean_label_list_v1(fixed.get(key))

        if changed:
            fixed[key] = cleaned_list
            fields_changed += changed

    # Fatti/fonte: possono essere frasi.
    for key in ["key_facts", "source_facts"]:
        cleaned_list, changed = clean_sentence_list_v1(fixed.get(key))

        if changed:
            fixed[key] = cleaned_list
            fields_changed += changed

    return fixed, {
        "changed": fields_changed > 0,
        "fields_changed": fields_changed,
        "warnings": [],
    }


def apply_universal_text_cleaner_summary_cards_v1(payload: Any) -> Tuple[Any, Dict[str, Any]]:
    if not isinstance(payload, dict):
        return payload, {
            "changed": False,
            "warnings": ["payload_not_dict"],
        }

    fixed = copy.deepcopy(payload)

    meta: Dict[str, Any] = {
        "changed": False,
        "summary_fields_changed": 0,
        "cards_fields_changed": 0,
        "cards_seen": 0,
        "keys_touched": [],
        "warnings": [],
    }

    summary_keys = ["riassunto_qualita", "summary", "riassunto"]
    card_keys = ["card_concettuali", "cards", "concept_cards"]

    for key in summary_keys:
        if isinstance(fixed.get(key), dict):
            cleaned_summary, summary_meta = clean_summary_like_v1(fixed[key])
            fixed[key] = cleaned_summary

            if summary_meta.get("changed"):
                meta["changed"] = True
                meta["keys_touched"].append(key)
                meta["summary_fields_changed"] += int(summary_meta.get("fields_changed") or 0)

    for key in card_keys:
        if isinstance(fixed.get(key), list):
            cleaned_cards: List[Any] = []
            total_card_changes = 0

            for card in fixed[key]:
                cleaned_card, card_meta = clean_card_like_v1(card)
                cleaned_cards.append(cleaned_card)

                meta["cards_seen"] += 1
                total_card_changes += int(card_meta.get("fields_changed") or 0)

            fixed[key] = cleaned_cards

            if total_card_changes:
                meta["changed"] = True
                meta["keys_touched"].append(key)
                meta["cards_fields_changed"] += total_card_changes

    return fixed, meta


def universal_text_cleaner_summary_cards_payload_target_v1(payload: Any) -> Any:
    fixed, _meta = apply_universal_text_cleaner_summary_cards_v1(payload)
    return fixed
