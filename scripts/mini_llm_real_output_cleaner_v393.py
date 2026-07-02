#!/usr/bin/env python3
"""
Mini LLM Real Output Cleaner V3.9.3.1.

Pulisce il testo reale prima del RAG e prima dello Study Pack.

Corregge:
- heading Markdown usati come contenuto;
- metadati di test/progetto;
- frammenti da elenco;
- frasi che finiscono spezzate;
- frasi pericolose per generare domande brutte;
- candidate troppo complesse per Q&A/test.

Non è LLM neurale.
È cleaner strutturale/linguistico.
"""

from __future__ import annotations

import re
from typing import Dict, List


METADATA_PATTERNS = [
    r"documento\s+rag\s+di\s+test",
    r"scopo\s+del\s+documento",
    r"fonte\s+di\s+prova",
    r"progetto\s+quiz",
    r"motore\s+rag\s+del\s+progetto",
    r"non\s+è\s+pensato\s+come\s+manuale\s+tecnico\s+avanzato",
    r"materiale\s+formativo\s+chiaro\s+da\s+cui",
    r"rag/documenti",
    r"può\s+essere\s+inserito\s+nella\s+cartella",
    r"l'obiettivo\s+è\s+spiegare",
]


BAD_FRAGMENT_PATTERNS = [
    r"^al\s+dominio\s+reale\b",
    r"^da\s+cui\b",
    r"^codici\s+o\s+dati\b",
    r"^tono\s+minaccioso\b",
    r"^allegati\s+inattesi\b",
    r"^errori\s+grammaticali\b",
    r"^richiesta\s+di\s+password\b",
]


BAD_STARTS = {
    "al", "della", "dello", "delle", "degli", "dei", "del",
    "pagina", "e", "o", "ma", "con", "per",
}


BAD_ENDINGS = {
    "alla", "allo", "alle", "agli", "al", "a", "di", "del",
    "della", "dello", "delle", "e", "o", "ma", "che", "con",
    "per", "tra", "fra", "cui", "dati",
}


def normalize(text: str) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").strip().split())


def strip_markdown_inline(text: str) -> str:
    text = re.sub(r"`([^`]+)`", r"\1", text)
    text = re.sub(r"\*\*([^*]+)\*\*", r"\1", text)
    text = re.sub(r"\*([^*]+)\*", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return text


def first_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return re.sub(r"^[\"'“”‘’(\[]+", "", words[0]).lower().strip(".,;:!?")


def last_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return words[-1].lower().strip(".,;:!?\"'“”‘’)]}")


def is_metadata_line(line: str) -> bool:
    low = normalize(line).lower()

    return any(re.search(pattern, low) for pattern in METADATA_PATTERNS)


def is_bad_fragment(line: str) -> bool:
    value = normalize(line).lower()

    if not value:
        return True

    if any(re.search(pattern, value) for pattern in BAD_FRAGMENT_PATTERNS):
        return True

    if first_word(value) in BAD_STARTS:
        return True

    if last_word(value) in BAD_ENDINGS:
        return True

    return False


def has_useful_verb_or_concept(line: str) -> bool:
    low = normalize(line).lower()

    markers = [
        "è", "sono", "usa", "usano", "serve", "servono", "permette", "permettono",
        "protegge", "proteggere", "garantisce", "garantire", "mantiene", "mantenere",
        "riduce", "ridurre", "aiuta", "aiutano", "contiene", "contengono",
        "blocca", "cifra", "corregge", "correggono", "chiude", "chiudono",
        "distingue", "evitare", "attivare", "recuperare", "segnalare",
        "password", "phishing", "backup", "malware", "ransomware", "2fa",
        "sicurezza", "dati", "credenziali", "account", "autenticazione",
    ]

    return any(item in low for item in markers)


def ensure_sentence(text: str) -> str:
    value = normalize(text)

    if not value:
        return ""

    if not value.endswith((".", "!", "?")):
        value += "."

    return value


def clean_bullet(line: str) -> str:
    item = re.sub(r"^\s*[-*•]\s*", "", line)
    item = re.sub(r"^\s*\d+[.)]\s*", "", item)
    item = strip_markdown_inline(item)
    item = normalize(item).strip(";:,. ")

    if not item:
        return ""

    if is_metadata_line(item) or is_bad_fragment(item):
        return ""

    if not has_useful_verb_or_concept(item):
        return ""

    low = item.lower()

    if low.startswith(("proteggere ", "garantire ", "mantenere ", "evitare ", "attivare ", "recuperare ", "segnalare ")):
        return ensure_sentence(f"Un punto importante è {item}")

    if first_word(item) in BAD_STARTS:
        return ""

    return ensure_sentence(item)


def clean_plain_line(line: str) -> str:
    value = strip_markdown_inline(line)
    value = normalize(value).strip()

    if not value:
        return ""

    if value.startswith("#"):
        return ""

    if is_metadata_line(value):
        return ""

    if re.match(r"^\s*[-*•]\s+", line) or re.match(r"^\s*\d+[.)]\s+", line):
        return clean_bullet(line)

    if value.endswith(":"):
        return ""

    if is_bad_fragment(value):
        return ""

    if not has_useful_verb_or_concept(value):
        return ""

    return ensure_sentence(value)


def split_into_sentences(text: str) -> List[str]:
    text = normalize(text)

    if not text:
        return []

    return [
        normalize(sentence)
        for sentence in re.split(r"(?<=[.!?])\s+", text)
        if normalize(sentence)
    ]


def is_safe_sentence(sentence: str) -> bool:
    value = normalize(sentence)

    if not value:
        return False

    if "#" in value:
        return False

    if is_metadata_line(value):
        return False

    if is_bad_fragment(value):
        return False

    words = value.split()

    if len(words) < 6:
        return False

    if len(words) > 34:
        return False

    if not value.endswith((".", "!", "?")):
        return False

    if re.search(r"\b(dati|credenziali|backup|informazioni|password)\s+(Il|La|I|Gli|Le|Un|Una|L')\b", value):
        return False

    if ":" in value and len(words) > 18:
        return False

    if value.lower().startswith("non riguarda solo"):
        return False

    if "mentre un file con credenziali" in value.lower():
        return False

    if "usare la stessa password su più siti" in value.lower() and ":" in value:
        return False

    if "piattaforme che contengono" in value.lower() and len(words) > 22:
        return False

    return True


def clean_sentence(sentence: str) -> str:
    value = strip_markdown_inline(sentence)
    value = normalize(value)

    if not is_safe_sentence(value):
        return ""

    return ensure_sentence(value)


def clean_document_text(raw_text: str) -> str:
    lines = str(raw_text or "").splitlines()
    cleaned_lines: List[str] = []

    for line in lines:
        cleaned = clean_plain_line(line)

        if cleaned:
            cleaned_lines.append(cleaned)

    paragraph_text = " ".join(cleaned_lines)

    final_sentences: List[str] = []
    seen = set()

    for sentence in split_into_sentences(paragraph_text):
        cleaned = clean_sentence(sentence)

        if not cleaned:
            continue

        key = cleaned.lower()

        if key in seen:
            continue

        seen.add(key)
        final_sentences.append(cleaned)

    return "\n".join(final_sentences)


def safe_study_context(cleaned_text: str, max_sentences: int = 48) -> str:
    selected: List[str] = []

    for sentence in split_into_sentences(cleaned_text):
        if is_safe_sentence(sentence):
            selected.append(ensure_sentence(sentence))

        if len(selected) >= max_sentences:
            break

    return " ".join(selected)


def cleaner_diagnostics(raw_text: str, cleaned_text: str) -> Dict[str, object]:
    raw_lines = len(str(raw_text or "").splitlines())
    cleaned_lines = len(str(cleaned_text or "").splitlines())
    raw_words = len(str(raw_text or "").split())
    cleaned_words = len(str(cleaned_text or "").split())

    return {
        "cleaner": "mini_llm_real_output_cleaner_v3931",
        "raw_lines": raw_lines,
        "cleaned_lines": cleaned_lines,
        "raw_words": raw_words,
        "cleaned_words": cleaned_words,
        "removed_words": max(0, raw_words - cleaned_words),
        "status": "OK" if cleaned_words >= 80 and cleaned_lines >= 8 else "TOO_SHORT",
        "limits": [
            "Cleaner strutturale.",
            "Rimuove metadati, frammenti e frasi pericolose.",
            "Non genera contenuto nuovo inventato.",
        ],
    }
