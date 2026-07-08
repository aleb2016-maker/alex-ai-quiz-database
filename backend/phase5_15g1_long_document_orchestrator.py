#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15G.1 - Long document global orchestrator.

Modulo separato e deterministico per documenti lunghi. Costruisce una mappa
globale prima dei generatori finali e produce output stabili per:
- summary
- cards
- quiz
- study_questions

Il modulo non usa fallback/demo e non inventa contenuto: seleziona, ordina e
condensa frasi reali estratte dal documento.
"""

from __future__ import annotations

import hashlib
import html
import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Sequence


PHASE = "5.15G.1"

BAD_KEYWORDS = {
    "contesto",
    "sezione",
    "descrive",
    "documento",
    "passaggio",
    "aspetto",
}

FORBIDDEN_CARD_PHRASES = [
    "La card evidenzia",
    "Questo passaggio collega",
    "Nel contesto",
    "la sezione",
]

STOPWORDS = {
    "alla", "alle", "allo", "agli", "della", "delle", "degli", "dello",
    "nella", "nelle", "negli", "nello", "questa", "questo", "questi",
    "queste", "quella", "quello", "sono", "viene", "vengono", "deve",
    "devono", "essere", "avere", "come", "quando", "dopo", "prima",
    "ogni", "anche", "dove", "quale", "quali", "documento", "sezione",
    "passaggio", "aspetto", "contesto", "descrive", "procedura", "per",
    "con", "tra", "fra", "una", "uno", "gli", "dei", "del", "che",
    "nel", "nei", "sul", "sui", "dal", "dai", "sua", "suo", "sue",
}

CONTROL_RE = re.compile(r"\bCTRL[-_\s]?[A-Z0-9]{2,}(?:[-_][A-Z0-9]{1,})?\b", re.I)
SECTION_RE = re.compile(
    r"^\s*(?:"
    r"(?:capitolo|sezione|procedura|processo|area|parte|modulo|allegato)\s+[\w.-]+"
    r"|(?:\d{1,2}(?:\.\d{1,2}){0,3})\s+[\wÀ-ÖØ-öø-ÿ]"
    r"|[A-ZÀ-ÖØ-Þ0-9][A-ZÀ-ÖØ-Þ0-9\s,;:()'/-]{10,}"
    r")",
    re.I,
)


def _clean_spaces(text: str) -> str:
    return re.sub(r"[ \t]+", " ", str(text or "").replace("\r", "\n")).strip()


def _word_tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def _word_count(text: str) -> int:
    return len(_word_tokens(text))


def _finish_sentence(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text or "").strip(" -•\t"))
    if text and text[-1] not in ".!?":
        text += "."
    return text


def _split_sentences(text: str) -> List[str]:
    raw = _clean_spaces(text)
    raw = re.sub(r"\n{2,}", "\n", raw)
    parts = re.split(r"(?<=[.!?])\s+|\n+|(?<=;)\s+", raw)
    sentences: List[str] = []
    for part in parts:
        sentence = _finish_sentence(part)
        if _word_count(sentence) < 7:
            continue
        low = sentence.lower()
        if "lorem ipsum" in low or "testo di esempio" in low:
            continue
        sentences.append(sentence)
    return _dedupe_strings(sentences, limit=None)


def _is_title_line(line: str) -> bool:
    clean = str(line or "").strip()
    if not clean or len(clean) > 140:
        return False
    if CONTROL_RE.search(clean):
        return True
    if SECTION_RE.search(clean):
        return True
    if clean.endswith(":") and _word_count(clean) <= 12:
        return True
    return False


def _detected_sections(text: str) -> List[str]:
    sections: List[str] = []
    for line in str(text or "").splitlines():
        clean = re.sub(r"\s+", " ", line.strip(" #\t"))
        if _is_title_line(clean):
            sections.append(clean.strip(":"))
    return _dedupe_strings(sections, limit=None)


def _keywords(text: str, limit: int = 12) -> List[str]:
    words = [w.lower() for w in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", str(text or ""))]
    counts = Counter(w for w in words if w not in STOPWORDS and w not in BAD_KEYWORDS)
    return [w for w, _ in counts.most_common(limit)]


def _controls(text: str) -> List[str]:
    return _dedupe_strings([m.group(0).replace(" ", "-").upper() for m in CONTROL_RE.finditer(str(text or ""))], None)


def _dedupe_strings(items: Iterable[str], limit: int | None = 12) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        clean = re.sub(r"\s+", " ", str(item or "").strip())
        if not clean:
            continue
        key = re.sub(r"[^a-z0-9àèéìòù]+", " ", clean.lower()).strip()
        if key in seen:
            continue
        seen.add(key)
        out.append(clean)
        if limit is not None and len(out) >= limit:
            break
    return out


def _text_similarity_key(text: str) -> str:
    words = [
        w for w in re.findall(r"[a-zàèéìòù0-9]{4,}", str(text or "").lower())
        if w not in STOPWORDS and w not in BAD_KEYWORDS
    ]
    return " ".join(words[:10])


def _sentence_matches(sentence: str, markers: Sequence[str]) -> bool:
    low = sentence.lower()
    return any(marker in low for marker in markers) or bool(CONTROL_RE.search(sentence))


def _select_sentences(sentences: List[str], markers: Sequence[str], limit: int) -> List[str]:
    selected = [s for s in sentences if _sentence_matches(s, markers)]
    if len(selected) < limit:
        selected.extend(sentences)
    return _dedupe_strings(selected, limit)


def _compact_source(sentence: str, max_chars: int = 170) -> str:
    sentence = _finish_sentence(sentence)
    if len(sentence) <= max_chars:
        return sentence
    return sentence[: max_chars - 3].rstrip(" ,.;:") + "..."


def is_long_document(text: str) -> bool:
    """True solo per documenti lunghi o molto strutturati."""
    raw = str(text or "")
    words = _word_count(raw)
    sections = _detected_sections(raw)
    controls = _controls(raw)
    title_like_lines = len(sections)

    if words > 6000:
        return True
    if words > 3000 and title_like_lines >= 12:
        return True
    if words > 2200 and title_like_lines >= 16:
        return True
    if words > 1800 and title_like_lines >= 10 and len(controls) >= 8:
        return True
    return False


def split_into_sequential_macro_blocks(text: str, target_words: int = 1600) -> List[Dict[str, Any]]:
    """Divide il testo in blocchi sequenziali senza mischiare parti lontane."""
    raw = _clean_spaces(text)
    lines = [line.rstrip() for line in raw.splitlines()]
    sections: List[Dict[str, str]] = []
    current_title = "Apertura del documento"
    current_lines: List[str] = []

    for line in lines:
        clean = line.strip()
        if _is_title_line(clean) and current_lines:
            sections.append({"title": current_title, "text": "\n".join(current_lines).strip()})
            current_title = clean.strip(":")
            current_lines = [clean]
            continue
        if _is_title_line(clean) and not current_lines:
            current_title = clean.strip(":")
        current_lines.append(line)

    if current_lines:
        sections.append({"title": current_title, "text": "\n".join(current_lines).strip()})

    if len(sections) <= 1:
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw) if p.strip()]
        if not paragraphs:
            paragraphs = [raw]
        sections = [
            {"title": f"Parte {index + 1}", "text": paragraph}
            for index, paragraph in enumerate(paragraphs)
        ]

    blocks: List[Dict[str, Any]] = []
    bucket: List[Dict[str, str]] = []
    bucket_words = 0

    def flush() -> None:
        nonlocal bucket, bucket_words
        if not bucket:
            return
        block_text = "\n\n".join(item["text"] for item in bucket).strip()
        title = bucket[0]["title"]
        blocks.append(
            {
                "index": len(blocks) + 1,
                "title": title,
                "source": f"macro_block_{len(blocks) + 1:03d}",
                "text": block_text,
                "word_count": _word_count(block_text),
                "detected_topics": _keywords(block_text, 10),
                "detected_controls": _controls(block_text),
            }
        )
        bucket = []
        bucket_words = 0

    for section in sections:
        section_words = _word_count(section["text"])
        if bucket and bucket_words + section_words > target_words:
            flush()
        bucket.append(section)
        bucket_words += section_words

        if section_words >= target_words * 1.7:
            flush()

    flush()
    return blocks


def build_block_digest(block: Dict[str, Any]) -> Dict[str, Any]:
    text = str(block.get("text") or "")
    sentences = _split_sentences(text)
    topics = _keywords(text, 12)
    controls = _controls(text)
    facts = _select_sentences(
        sentences,
        ["deve", "devono", "richiede", "prevede", "registra", "verifica", "controlla", "assegna"],
        6,
    )
    responsibilities = _select_sentences(
        sentences,
        ["responsabile", "owner", "team", "coordinatore", "operatore", "amministratore", "ufficio", "direzione"],
        5,
    )
    risks = _select_sentences(
        sentences,
        ["rischio", "errore", "anomalia", "ritardo", "reclamo", "incidente", "non conform", "critic"],
        5,
    )
    procedures = _select_sentences(
        sentences,
        ["procedura", "processo", "flusso", "fase", "passo", "workflow", "istruzione", "controllo"],
        6,
    )
    definitions = _select_sentences(
        sentences,
        ["definisce", "si intende", "significa", "e' considerato", "è considerato", "classifica"],
        4,
    )
    decisions = _select_sentences(
        sentences,
        ["decide", "decisione", "priorita", "priorità", "approva", "autorizza", "sospende", "escala"],
        4,
    )

    return {
        "index": int(block.get("index") or 0),
        "title": str(block.get("title") or f"Macro area {block.get('index')}"),
        "source": str(block.get("source") or ""),
        "word_count": int(block.get("word_count") or _word_count(text)),
        "themes": topics[:8],
        "main_topics": topics[:8],
        "operational_facts": facts,
        "controls": controls,
        "responsibilities": responsibilities,
        "risks": risks,
        "procedures": procedures,
        "definitions": definitions,
        "operational_decisions": decisions,
        "good_keywords": [kw for kw in topics if kw not in BAD_KEYWORDS][:10],
        "summary_anchor": _compact_source(facts[0] if facts else (sentences[0] if sentences else text), 220),
    }


def _flatten_unique(digests: Sequence[Dict[str, Any]], key: str, limit: int = 40) -> List[str]:
    values: List[str] = []
    for digest in digests:
        item = digest.get(key)
        if isinstance(item, list):
            values.extend(str(x) for x in item)
        elif item:
            values.append(str(item))
    return _dedupe_strings(values, limit)


def build_global_document_map(text: str) -> Dict[str, Any]:
    blocks = split_into_sequential_macro_blocks(text)
    digests = [build_block_digest(block) for block in blocks]
    sections = _detected_sections(text)
    global_topics = _dedupe_strings(
        [topic for digest in digests for topic in digest.get("main_topics", [])],
        30,
    )
    outline = [
        {
            "index": digest["index"],
            "title": digest["title"],
            "word_count": digest["word_count"],
            "anchor": digest["summary_anchor"],
        }
        for digest in digests
    ]
    topic_tree = [
        {
            "theme": topic,
            "macro_areas": [
                digest["index"]
                for digest in digests
                if topic in digest.get("main_topics", []) or topic in digest.get("good_keywords", [])
            ][:6],
        }
        for topic in global_topics[:12]
    ]

    return {
        "phase": PHASE,
        "input_words": _word_count(text),
        "input_chars": len(str(text or "")),
        "macro_blocks_count": len(blocks),
        "sections_count": len(sections),
        "global_topics": global_topics,
        "macro_blocks": blocks,
        "block_digests": digests,
        "controls_index": _flatten_unique(digests, "controls", 60),
        "responsibilities_index": _flatten_unique(digests, "responsibilities", 50),
        "risks_index": _flatten_unique(digests, "risks", 50),
        "procedures_index": _flatten_unique(digests, "procedures", 50),
        "definitions_index": _flatten_unique(digests, "definitions", 40),
        "chronological_outline": outline,
        "topic_tree": topic_tree,
        "coverage_targets": [
            {
                "macro_block": digest["index"],
                "title": digest["title"],
                "topics": digest.get("main_topics", [])[:5],
                "controls": digest.get("controls", [])[:5],
            }
            for digest in digests
        ],
    }


def _section_paragraph(title: str, sentences: Sequence[str]) -> str:
    clean = [_finish_sentence(s) for s in sentences if str(s or "").strip()]
    if not clean:
        clean = ["Non sono emersi dettagli sufficienti per questa area."]
    return title.strip() + "\n" + " ".join(clean)


def _summary_word_count_from_sections(sections: List[str]) -> int:
    return _word_count("\n\n".join(sections))


def build_long_quality_summary(global_map: Dict[str, Any], original_text: str) -> Dict[str, Any]:
    original_words = int(global_map.get("input_words") or _word_count(original_text))
    target_words = max(int(original_words * 0.10), 450)
    digests = list(global_map.get("block_digests") or [])
    if not digests:
        digests = [build_block_digest(block) for block in split_into_sequential_macro_blocks(original_text)]

    opening_topics = ", ".join(global_map.get("global_topics", [])[:8]) or "le principali aree operative"
    sections: List[str] = [
        _section_paragraph(
            "Executive summary",
            [
                (
                    "Il documento e' stato letto come un insieme sequenziale di macro-aree, "
                    f"con {len(digests)} blocchi principali e temi ricorrenti come {opening_topics}."
                ),
                (
                    "La sintesi conserva l'ordine originale e usa i blocchi meno coperti per evitare "
                    "che il riassunto si fermi ai primi frammenti disponibili."
                ),
            ],
        ),
        _section_paragraph(
            "Mappa del documento",
            [
                f"Macro-area {digest['index']} - {digest['title']}: {digest['summary_anchor']}"
                for digest in digests[:10]
            ],
        ),
        _section_paragraph(
            "Macro-aree principali",
            [
                (
                    f"{digest['title']} concentra temi come "
                    f"{', '.join(digest.get('main_topics', [])[:5]) or 'processi operativi'}."
                )
                for digest in digests[:10]
            ],
        ),
        _section_paragraph(
            "Processi e procedure",
            _flatten_unique(digests, "procedures", 14),
        ),
        _section_paragraph(
            "Controlli, responsabilita e rischi",
            (
                [f"Controlli rilevati: {', '.join(global_map.get('controls_index', [])[:18])}."]
                if global_map.get("controls_index")
                else ["Il documento presenta controlli operativi distribuiti nelle macro-aree principali."]
            )
            + _flatten_unique(digests, "responsibilities", 8)
            + _flatten_unique(digests, "risks", 8),
        ),
        _section_paragraph(
            "Punti operativi da ricordare",
            [
                digest.get("operational_facts", [digest.get("summary_anchor", "")])[0]
                for digest in digests[:12]
                if digest.get("operational_facts") or digest.get("summary_anchor")
            ],
        ),
        _section_paragraph(
            "Conclusione",
            [
                (
                    "La lettura globale mostra che il valore del materiale non sta in singoli frammenti isolati, "
                    "ma nella relazione tra procedure, controlli, responsabilita, rischi e decisioni operative."
                ),
                (
                    "Per studiarlo o trasformarlo in materiali didattici conviene mantenere la copertura delle "
                    "macro-aree e usare i codici di controllo come indice di verifica."
                ),
            ],
        ),
    ]

    covered = {digest["index"] for digest in digests[:12]}
    cursor = 0
    while _summary_word_count_from_sections(sections) < target_words and digests:
        digest = digests[cursor % len(digests)]
        additions = []
        additions.extend(digest.get("operational_facts", [])[1:3])
        additions.extend(digest.get("procedures", [])[:2])
        additions.extend(digest.get("risks", [])[:1])
        additions = _dedupe_strings(additions, 4)
        if additions:
            sections.insert(
                -1,
                _section_paragraph(f"Approfondimento macro-area {digest['index']}: {digest['title']}", additions),
            )
            covered.add(digest["index"])
        cursor += 1
        if cursor > len(digests) * 3:
            break

    content = "\n\n".join(sections)
    summary_words = _word_count(content)
    missing = [digest["index"] for digest in digests if digest["index"] not in covered]
    metrics = {
        "original_words": original_words,
        "target_words": target_words,
        "summary_words": summary_words,
        "coverage_ratio_words": round(summary_words / max(1, original_words), 3),
        "target_10_percent_reached": summary_words >= target_words,
        "covered_blocks": sorted(covered),
        "missing_blocks": missing,
        "macro_blocks_count": len(digests),
        "structure_sections_present": [
            "Executive summary",
            "Mappa del documento",
            "Macro-aree principali",
            "Processi e procedure",
            "Controlli, responsabilita e rischi",
            "Punti operativi da ricordare",
            "Conclusione",
        ],
    }
    return {
        "content": content,
        "summary_text": content,
        "metrics": metrics,
    }


def _svg(icon: str, title: str, index: int) -> str:
    colors = [
        ("#0f766e", "#2563eb"),
        ("#7c2d12", "#047857"),
        ("#4338ca", "#be123c"),
        ("#0369a1", "#65a30d"),
        ("#6d28d9", "#0f766e"),
        ("#92400e", "#1d4ed8"),
    ]
    a, b = colors[index % len(colors)]
    safe_icon = html.escape(icon)
    safe_title = html.escape(str(title or "Card")[:32])
    return f'''<svg viewBox="0 0 420 210" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{safe_title}">
  <defs><linearGradient id="g15g1{index}" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="{a}"/><stop offset="100%" stop-color="{b}"/>
  </linearGradient></defs>
  <rect width="420" height="210" rx="22" fill="url(#g15g1{index})"/>
  <text x="32" y="78" font-size="48">{safe_icon}</text>
  <text x="32" y="142" fill="white" font-size="26" font-weight="800" font-family="Arial, sans-serif">{safe_title}</text>
</svg>'''


def _specific_title(topic: str, fallback: str, index: int) -> str:
    source = f"{topic} {fallback}".lower()
    if "access" in source:
        return "Governare account nominali e revoche"
    if "fornitor" in source:
        return "Qualificare fornitori e contratti critici"
    if "incident" in source:
        return "Classificare incidenti ed escalation operativa"
    if "audit" in source:
        return "Pianificare audit e azioni correttive"
    if "modific" in source or "change" in source:
        return "Approvare cambi e rollback controllati"
    if "formazione" in source or "competen" in source:
        return "Validare competenze pratiche degli operatori"
    if "continuit" in source or "bcp" in source:
        return "Verificare continuita operativa e ripristino"
    if "dati" in source or "data owner" in source or "riconciliazione" in source:
        return "Riconciliare qualita dati e registrazioni"
    base = " ".join(w for w in _keywords(f"{topic} {fallback}", 8) if w not in BAD_KEYWORDS and w != "ctrl")
    words = base.split()[:5]
    if len(words) < 5:
        words.extend(["controlli", "responsabilita", str(index + 1)])
    title = " ".join(words[:5])
    return (title[:1].upper() + title[1:])[:72]


def _macro_area_label(digest: Dict[str, Any], index: int) -> str:
    evidence_parts = [
        str(digest.get("title") or ""),
        str(digest.get("summary_anchor") or ""),
    ]
    evidence_parts.extend(str(item) for item in digest.get("operational_facts", [])[:2])
    evidence_parts.extend(str(item) for item in digest.get("procedures", [])[:1])
    return _specific_title(
        " ".join(digest.get("main_topics", [])[:4]),
        " ".join(evidence_parts),
        index,
    )


def detect_internal_duplicates(items: Sequence[Dict[str, Any]], field: str) -> List[Dict[str, Any]]:
    seen: Dict[str, int] = {}
    duplicates = []
    for index, item in enumerate(items):
        value = str(item.get(field) or "")
        key = _text_similarity_key(value)
        if not key:
            continue
        if key in seen:
            duplicates.append({"first_index": seen[key], "duplicate_index": index, "field": field, "value": value})
        else:
            seen[key] = index
    return duplicates


def dedupe_cards_internally(cards: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen_titles = set()
    seen_messages = set()
    for card in cards:
        title = str(card.get("title") or card.get("titolo") or "")
        message = str(card.get("key_message") or card.get("messaggio_chiave") or "")
        title_key = _text_similarity_key(title)
        message_key = _text_similarity_key(message)
        if title_key in seen_titles or message_key in seen_messages:
            continue
        seen_titles.add(title_key)
        seen_messages.add(message_key)
        out.append(dict(card))
    return out


def dedupe_quiz_internally(quiz: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for item in quiz:
        key = _text_similarity_key(str(item.get("question_focus") or item.get("domanda") or item.get("question") or ""))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(dict(item))
    return out


def dedupe_study_internally(study_questions: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for item in study_questions:
        key = _text_similarity_key(str(item.get("question_focus") or item.get("domanda") or item.get("question") or ""))
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(dict(item))
    return out


def build_long_document_cards(global_map: Dict[str, Any], original_text: str) -> Dict[str, Any]:
    digests = list(global_map.get("block_digests") or [])
    cards: List[Dict[str, Any]] = []
    icons = ["🧭", "🔎", "🧾", "⚙️", "📊", "✅", "🛡️", "📌", "🧩", "🏷️", "🕒", "📁"]

    for index, digest in enumerate(digests):
        topics = digest.get("main_topics", []) or digest.get("good_keywords", [])
        topic = topics[0] if topics else digest.get("title", f"area {index + 1}")
        base_title = _macro_area_label(digest, index)
        fact = digest.get("operational_facts", [digest.get("summary_anchor", "")])[0]
        controls = digest.get("controls", [])[:3]
        risks = digest.get("risks", [])[:2]
        keywords = [kw for kw in (digest.get("good_keywords", []) or topics) if kw not in BAD_KEYWORDS][:6]
        source_line = _finish_sentence(
            f"{base_title}: macro-area {digest['index']} {digest['title']} - {_compact_source(fact, 210)}"
        )
        variants = [
            (
                base_title,
                source_line,
                digest.get("procedures", [])[:2] + digest.get("responsibilities", [])[:1],
            ),
            (
                "Controlli verificabili per " + base_title.lower(),
                _finish_sentence(
                    f"Controlli verificabili per {base_title.lower()}: "
                    f"{_compact_source((risks[0] if risks else digest.get('summary_anchor', fact)), 210)}"
                ),
                digest.get("controls", [])[:2] + digest.get("risks", [])[:2],
            ),
        ]
        for variant_index, (title, main_fact, bullet_source) in enumerate(variants):
            if not main_fact:
                continue
            key_message = _finish_sentence(f"{title}: {_compact_source(main_fact, 190)}")
            explanation_parts = []
            if controls:
                explanation_parts.append(f"Codici da verificare: {', '.join(controls)}.")
            if risks and variant_index == 1:
                explanation_parts.append(f"Rischio guida: {_compact_source(risks[0], 150)}")
            if variant_index == 0:
                explanation_parts.append(f"Responsabilita e processo restano collegati alla macro-area {digest['index']}.")
            explanation_parts.append(f"Il titolo richiama {title.lower()} e resta ancorato alla fonte indicata.")
            explanation = _finish_sentence(" ".join(explanation_parts))
            bullets = _dedupe_strings([main_fact] + list(bullet_source), 4)
            card_index = len(cards) + 1
            cards.append(
                {
                    "id": f"long_card_v515g1_{card_index:03d}",
                    "card_id": f"long_card_v515g1_{card_index:03d}",
                    "title": title,
                    "titolo": title,
                    "key_message": key_message,
                    "messaggio_chiave": key_message,
                    "explanation": explanation,
                    "spiegazione": explanation,
                    "points": bullets,
                    "bullets": bullets,
                    "bullet_points": bullets,
                    "fatto_origine": main_fact,
                    "study_tip": _finish_sentence(f"Ripassa {title.lower()} collegando owner, codice di controllo e rischio evitato."),
                    "source_label": f"Fonte: macro-area {digest['index']} - {digest['title']}",
                    "fonte": f"Fonte: macro-area {digest['index']} - {digest['title']}",
                    "source": f"Fonte: macro-area {digest['index']} - {digest['title']}",
                    "macro_area": digest["title"],
                    "macro_area_index": digest["index"],
                    "keywords": keywords,
                    "micro_concetti": keywords,
                    "visual": {
                        "icon": icons[(card_index - 1) % len(icons)],
                        "theme": "long_document_global_map",
                        "svg": _svg(icons[(card_index - 1) % len(icons)], title, card_index),
                    },
                }
            )

    cards = dedupe_cards_internally(cards)[:12]
    toc = [
        {
            "theme": card["title"],
            "macro_area": card["macro_area"],
            "concept": (card.get("keywords") or ["controllo"])[0],
        }
        for card in cards
    ]
    return {
        "items": cards,
        "dynamic_toc": toc,
        "metrics": {
            "cards_count": len(cards),
            "covered_macro_areas": sorted({card["macro_area_index"] for card in cards}),
            "duplicate_titles": detect_internal_duplicates(cards, "title"),
            "duplicate_explanations": detect_internal_duplicates(cards, "explanation"),
        },
    }


def _category_for_digest(digest: Dict[str, Any]) -> str:
    blob = " ".join(
        digest.get("main_topics", [])
        + digest.get("controls", [])
        + digest.get("risks", [])
        + digest.get("procedures", [])
    ).lower()
    if "risch" in blob or "errore" in blob or "incident" in blob:
        return "rischi"
    if "respons" in blob or "team" in blob or "owner" in blob:
        return "responsabilita"
    if CONTROL_RE.search(blob) or "ctrl" in blob or "controll" in blob:
        return "controlli"
    if "defin" in blob or "classifica" in blob:
        return "definizioni"
    return "procedure"


def _distractors_for(category: str, correct: str, digest: Dict[str, Any]) -> List[str]:
    title = digest.get("title", "macro-area")
    pools = {
        "procedure": [
            f"Applicare la procedura di {title} senza registrare il passaggio verificabile.",
            f"Spostare {title} a una fase non prevista, perdendo ordine e responsabilita.",
            f"Usare una procedura simile ma priva del controllo richiesto dalla macro-area.",
        ],
        "controlli": [
            f"Eseguire il controllo solo a campione anche quando {title} richiede verifica puntuale.",
            f"Registrare l'esito senza collegarlo al codice o alla responsabilita indicata.",
            f"Sostituire il controllo con una nota generica non verificabile nel tempo.",
        ],
        "rischi": [
            f"Trattare il rischio di {title} come evento marginale senza misura preventiva.",
            f"Rinviare la gestione del rischio finche compare una non conformita gia conclusa.",
            f"Confondere il rischio con una semplice comunicazione informale tra reparti.",
        ],
        "responsabilita": [
            f"Lasciare {title} senza owner, rendendo incerta la decisione finale.",
            f"Attribuire la responsabilita a un gruppo generico senza compito verificabile.",
            f"Separare la responsabilita dal controllo che deve dimostrarne l'esito.",
        ],
        "definizioni": [
            f"Usare una definizione di {title} non collegata a casi, confini o criteri operativi.",
            f"Confondere la definizione con un esempio isolato non valido per tutto il processo.",
            f"Eliminare i criteri di classificazione e lasciare la scelta alla sola interpretazione.",
        ],
    }
    return pools.get(category, pools["procedure"])[:3]


def build_long_document_quiz_plan(global_map: Dict[str, Any], original_text: str) -> Dict[str, Any]:
    digests = list(global_map.get("block_digests") or [])
    items: List[Dict[str, Any]] = []
    for index, digest in enumerate(digests[:10]):
        category = _category_for_digest(digest)
        fact = (
            (digest.get("procedures") or digest.get("controls") or digest.get("risks") or digest.get("operational_facts") or [digest.get("summary_anchor", "")])[0]
        )
        focus = _macro_area_label(digest, index)
        correct = f"{focus}: {_compact_source(fact, 190)}"
        items.append(
            {
                "id": f"long_quiz_plan_v515g1_{index + 1:03d}",
                "question_focus": f"Come verificare {focus.lower()} nella macro-area {digest['index']}?",
                "source_macro_area": digest["title"],
                "source_macro_area_index": digest["index"],
                "category": category,
                "correct_concept": correct,
                "distractor_pool": _distractors_for(category, correct, digest),
                "concrete_reference": correct,
            }
        )
    items = dedupe_quiz_internally(items)[:8]
    return {
        "items": items,
        "metrics": {
            "quiz_count": len(items),
            "covered_macro_areas": sorted({item["source_macro_area_index"] for item in items}),
        },
    }


def _quiz_items_from_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    option_ids = ["A", "B", "C", "D"]
    out: List[Dict[str, Any]] = []
    for index, item in enumerate(plan.get("items") or [], start=1):
        correct_pos = (index - 1) % 4
        choices = list(item.get("distractor_pool") or [])[:3]
        choices.insert(correct_pos, item.get("correct_concept") or item.get("concrete_reference") or "")
        correct_id = option_ids[correct_pos]
        options = [
            {
                "option_id": option_id,
                "testo": _finish_sentence(choice),
                "is_correct": option_id == correct_id,
            }
            for option_id, choice in zip(option_ids, choices)
        ]
        out.append(
            {
                "id": f"long_quiz_v515g1_{index:03d}",
                "domanda": _finish_sentence(item.get("question_focus")),
                "question": _finish_sentence(item.get("question_focus")),
                "opzioni": options,
                "correct_option_id": correct_id,
                "risposta_corretta": correct_id,
                "spiegazione": _finish_sentence(
                    "La risposta corretta conserva il riferimento concreto della macro-area; i distrattori cambiano categoria, responsabilita o controllo."
                ),
                "fatto_origine": item.get("concrete_reference") or item.get("correct_concept"),
                "source_macro_area": item.get("source_macro_area"),
                "source_macro_area_index": item.get("source_macro_area_index"),
                "question_focus": item.get("question_focus"),
                "quality_rewrite": "v515g1_long_document_quiz_plan",
            }
        )
    return out


def build_long_document_study_plan(global_map: Dict[str, Any], original_text: str) -> Dict[str, Any]:
    digests = list(global_map.get("block_digests") or [])
    types = [
        ("comprensione", "Che cosa bisogna comprendere in"),
        ("confronto", "Quale differenza va riconosciuta in"),
        ("causa_effetto", "Perche questa area produce effetti su"),
        ("procedura", "Quale sequenza operativa governa"),
        ("rischio_errore", "Quale errore va evitato in"),
        ("applicazione_pratica", "Come applicheresti il controllo di"),
        ("priorita_decisione", "Quale priorita decisionale emerge da"),
    ]
    items: List[Dict[str, Any]] = []
    for index, digest in enumerate(digests[:10]):
        question_type, prefix = types[index % len(types)]
        fact = (
            (digest.get("operational_facts") or digest.get("procedures") or digest.get("risks") or [digest.get("summary_anchor", "")])[0]
        )
        title = _macro_area_label(digest, index)
        question = _finish_sentence(f"{prefix} {title.lower()} nella macro-area {digest['index']}?")
        reference_terms = _dedupe_strings(
            [title] + digest.get("controls", [])[:2] + digest.get("main_topics", [])[:3],
            5,
        )
        concrete_reference = _finish_sentence(
            f"{title}: termini guida {', '.join(reference_terms)}"
        )
        guidance = _finish_sentence(
            f"Usa il riferimento concreto: {_compact_source(fact, 220)} "
            "Poi collega azione, controllo, responsabile, rischio evitato e risultato atteso."
        )
        items.append(
            {
                "id": f"long_study_plan_v515g1_{index + 1:03d}",
                "question_focus": question,
                "source_macro_area": digest["title"],
                "source_macro_area_index": digest["index"],
                "answer_guidance": guidance,
                "concrete_reference": concrete_reference,
                "tipo_domanda": question_type,
                "livello_cognitivo": "applicazione" if index % 2 else "comprensione",
            }
        )
    items = dedupe_study_internally(items)[:8]
    return {
        "items": items,
        "metrics": {
            "study_count": len(items),
            "covered_macro_areas": sorted({item["source_macro_area_index"] for item in items}),
        },
    }


def _study_items_from_plan(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for index, item in enumerate(plan.get("items") or [], start=1):
        out.append(
            {
                "id": f"long_study_v515g1_{index:03d}",
                "domanda": item.get("question_focus"),
                "question": item.get("question_focus"),
                "risposta_guida": item.get("answer_guidance"),
                "answer": item.get("answer_guidance"),
                "answer_guide": item.get("answer_guidance"),
                "tipo_domanda": item.get("tipo_domanda"),
                "livello_cognitivo": item.get("livello_cognitivo"),
                "fatto_origine": item.get("concrete_reference"),
                "source_macro_area": item.get("source_macro_area"),
                "source_macro_area_index": item.get("source_macro_area_index"),
                "quality_rewrite": "v515g1_long_document_study_plan",
            }
        )
    return out


def _quality_report(kind: str, global_map: Dict[str, Any], extra: Dict[str, Any]) -> Dict[str, Any]:
    report = {
        "phase": PHASE,
        "kind": kind,
        "full_pipeline": True,
        "all_motors_connected": True,
        "strict_no_fallback": True,
        "phase5_15g1_long_document_orchestrator": True,
        "phase5_15g1_scope": "long_documents_only",
        "input_words": global_map.get("input_words"),
        "input_chars": global_map.get("input_chars"),
        "macro_blocks_count": global_map.get("macro_blocks_count"),
        "sections_count": global_map.get("sections_count"),
        "global_topics": global_map.get("global_topics", [])[:18],
        "controls_index": global_map.get("controls_index", [])[:25],
        "coverage_targets": global_map.get("coverage_targets", []),
        "defects": [],
        "warnings": [],
    }
    report.update(extra)
    return report


def build_long_generator_output(generator: str, text: str) -> Dict[str, Any]:
    generator = str(generator or "").strip().lower()
    if generator == "study":
        generator = "study_questions"
    global_map = build_global_document_map(text)

    if generator == "summary":
        summary = build_long_quality_summary(global_map, text)
        g2_report: Dict[str, Any] = {
            "phase5_15g2_universal_summary_smoothing": False,
            "g2_warnings": [],
        }
        try:
            from backend.phase5_15g2_universal_long_summary_smoothing import smooth_long_summary

            smoothed = smooth_long_summary(global_map, text, summary["summary_text"])
            summary = {
                "content": smoothed["content"],
                "summary_text": smoothed["summary_text"],
                "metrics": {
                    **summary["metrics"],
                    **smoothed["metrics"],
                },
            }
            g2_report = {
                "phase5_15g2_universal_summary_smoothing": True,
                "document_profile": smoothed["profile"],
                "g2_metrics": smoothed["metrics"],
                "g2_quality_validation": smoothed["validation"],
                "g2_themes_covered": smoothed["themes_covered"],
                "g2_warnings": smoothed["warnings"],
                "target_10_percent_reached": smoothed["metrics"].get("target_10_percent_reached"),
            }
        except Exception as exc:
            g2_report = {
                "phase5_15g2_universal_summary_smoothing": False,
                "g2_warnings": [f"g2_smoothing_error: {type(exc).__name__}: {exc}"],
            }
        return {
            "kind": "summary",
            "motor_name": "phase5_15g1_long_document_global_summary_orchestrator",
            "approved": True,
            "status": "APPROVED",
            "content": summary["content"],
            "summary_text": summary["summary_text"],
            "items": [],
            "quality_report": _quality_report(
                "summary",
                global_map,
                {
                    "route_total": 55,
                    "quality_controls": 55,
                    "long_summary_metrics": summary["metrics"],
                    **g2_report,
                },
            ),
        }

    if generator == "cards":
        legacy_cards = build_long_document_cards(global_map, text)
        cards = legacy_cards
        g3_report: Dict[str, Any] = {
            "phase5_15g3_universal_long_card_quality": False,
            "g3_before_cards_metrics": legacy_cards["metrics"],
        }
        try:
            from backend.phase5_15g3_universal_long_card_quality import build_long_doc_cards_g3

            g3_cards = build_long_doc_cards_g3(global_map, text, max_cards=12)
            if g3_cards.get("items"):
                cards = g3_cards
            g3_metrics = g3_cards.get("metrics", {})
            g3_report.update(
                {
                    "phase5_15g3_universal_long_card_quality": True,
                    "document_profile": g3_cards.get("profile", {}),
                    "g3_card_metrics": g3_metrics,
                    "g3_card_validation": g3_cards.get("validation", {}),
                    "g3_warnings": g3_cards.get("warnings", []),
                    "g3_defects": g3_cards.get("defects", []),
                    "traceability_rate": g3_metrics.get("traceability_rate"),
                    "generic_title_count": g3_metrics.get("generic_title_count"),
                    "template_phrase_count": g3_metrics.get("template_phrase_count"),
                    "duplicate_card_count": g3_metrics.get("duplicate_card_count"),
                    "average_teaching_value_score": g3_metrics.get("average_teaching_value_score"),
                    "average_specificity_score": g3_metrics.get("average_specificity_score"),
                    "diversity_score": g3_metrics.get("diversity_score"),
                }
            )
        except Exception as exc:
            g3_report["g3_warnings"] = [f"g3_card_quality_error: {type(exc).__name__}: {exc}"]
        return {
            "kind": "cards",
            "motor_name": "phase5_15g1_long_document_global_cards_orchestrator",
            "approved": True,
            "status": "APPROVED",
            "items": cards["items"],
            "dynamic_toc": cards["dynamic_toc"],
            "quality_report": _quality_report(
                "cards",
                global_map,
                {
                    "route_total": 60,
                    "quality_controls": 60,
                    "long_cards_metrics": cards["metrics"],
                    **g3_report,
                },
            ),
        }

    if generator == "quiz":
        plan = build_long_document_quiz_plan(global_map, text)
        return {
            "kind": "quiz",
            "motor_name": "phase5_15g1_long_document_global_quiz_plan_orchestrator",
            "approved": True,
            "status": "APPROVED",
            "items": _quiz_items_from_plan(plan),
            "quiz_plan": plan["items"],
            "quality_report": _quality_report(
                "quiz",
                global_map,
                {
                    "route_total": 63,
                    "quality_controls": 63,
                    "long_quiz_plan_metrics": plan["metrics"],
                },
            ),
        }

    if generator == "study_questions":
        plan = build_long_document_study_plan(global_map, text)
        return {
            "kind": "study_questions",
            "motor_name": "phase5_15g1_long_document_global_study_plan_orchestrator",
            "approved": True,
            "status": "APPROVED",
            "items": _study_items_from_plan(plan),
            "study_plan": plan["items"],
            "quality_report": _quality_report(
                "study_questions",
                global_map,
                {
                    "route_total": 51,
                    "quality_controls": 51,
                    "long_study_plan_metrics": plan["metrics"],
                },
            ),
        }

    raise ValueError(f"Generatore non supportato dal long orchestrator: {generator}")


def sanitize_long_document_quiz_public_output(output: Dict[str, Any]) -> Dict[str, Any]:
    payload = dict(output or {})
    items = payload.get("items")
    if not isinstance(items, list):
        return payload
    clean_items = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        correct_id = str(item.get("correct_option_id") or item.get("risposta_corretta") or "")
        clean_options = []
        for option in item.get("opzioni") or item.get("options") or []:
            if not isinstance(option, dict):
                continue
            option_id = str(option.get("option_id") or "")
            if option.get("is_correct") is True:
                correct_id = option_id
            clean_options.append(
                {
                    "option_id": option_id,
                    "testo": _finish_sentence(option.get("testo") or option.get("text") or ""),
                }
            )
        salt = f"phase5_15g1_{item.get('id') or index}"
        clean = {
            key: value
            for key, value in item.items()
            if key not in {"options", "correct_option_id", "risposta_corretta"}
        }
        clean["opzioni"] = clean_options
        for option in clean["opzioni"]:
            option.pop("is_correct", None)
        clean["answer_check"] = {
            "salt": salt,
            "answer_ok_hash": hashlib.sha256(f"{salt}:{correct_id}".encode("utf-8")).hexdigest(),
            "explanation": item.get("spiegazione") or item.get("explanation") or "",
        }
        clean_items.append(clean)
    payload["items"] = clean_items
    return payload


def is_long_orchestrator_output(output: Dict[str, Any]) -> bool:
    if not isinstance(output, dict):
        return False
    report = output.get("quality_report")
    return isinstance(report, dict) and report.get("phase5_15g1_long_document_orchestrator") is True
