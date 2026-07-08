#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15G.2 - Universal long summary thematic smoothing.

Secondo passaggio deterministico per i soli riassunti di documenti lunghi.
Prende la mappa globale G.1 e il riassunto grezzo, rimuove rumore/template,
ricostruisce temi dinamici e produce una sintesi piu' narrativa senza toccare
il Quality Manager comune.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, Iterable, List, Sequence, Tuple


PHASE = "5.15G.2"

STOPWORDS = {
    "alla", "alle", "allo", "agli", "della", "delle", "degli", "dello",
    "nella", "nelle", "negli", "nello", "questa", "questo", "questi",
    "queste", "quella", "quello", "sono", "viene", "vengono", "deve",
    "devono", "essere", "avere", "come", "quando", "dopo", "prima",
    "ogni", "anche", "dove", "quale", "quali", "documento", "sezione",
    "passaggio", "aspetto", "contesto", "descrive", "procedura", "per",
    "con", "tra", "fra", "una", "uno", "gli", "dei", "del", "che",
    "nel", "nei", "sul", "sui", "dal", "dai", "sua", "suo", "sue",
    "un", "il", "lo", "la", "le", "i", "e", "o", "a", "di", "da",
    "in", "su", "al", "ai", "ad", "ed", "piu", "piu'", "più",
}

SYSTEM_NOISE_PATTERNS = [
    "non contiene dati reali",
    "collegato alla demo",
    "demo",
    "fallback",
    "script",
    "test tecnico",
    "documento fixture",
    "fixture tecnica",
    "debug",
    "log di sistema",
    "nota di sistema",
    "system note",
]

TEMPLATE_PATTERNS = [
    r"\bla procedura richiede\b",
    r"\bogni attivit[aà] deve\b",
    r"\bnel contesto\b",
    r"\bla sezione\b",
    r"\bquesto passaggio\b",
    r"\bil controllo\s+ctrl\b",
    r"\bmacro-area\s+\d+\b",
]

VOCABULARY: Dict[str, Dict[str, str]] = {
    "manuale_aziendale": {
        "overview": "Executive summary",
        "map": "Mappa dei processi",
        "themes": "Controlli",
        "development": "Responsabilita",
        "key_takeaways": "Rischi e audit",
        "connections": "Collegamenti operativi",
        "conclusion": "Sintesi conclusiva",
    },
    "dispensa_scolastica_universitaria": {
        "overview": "Panoramica",
        "map": "Mappa concettuale",
        "themes": "Concetti chiave",
        "development": "Definizioni e spiegazioni",
        "key_takeaways": "Esempi",
        "connections": "Collegamenti tra concetti",
        "conclusion": "Conclusione didattica",
    },
    "documento_tecnico": {
        "overview": "Sintesi tecnica",
        "map": "Mappa dell'architettura",
        "themes": "Componenti",
        "development": "Procedure e configurazioni",
        "key_takeaways": "Errori",
        "connections": "Dipendenze e flussi",
        "conclusion": "Chiusura tecnica",
    },
    "documento_legale_amministrativo": {
        "overview": "Quadro generale",
        "map": "Mappa degli adempimenti",
        "themes": "Soggetti",
        "development": "Obblighi e scadenze",
        "key_takeaways": "Vincoli",
        "connections": "Relazioni normative",
        "conclusion": "Conclusione amministrativa",
    },
    "cv_profilo_professionale": {
        "overview": "Profilo esecutivo",
        "map": "Mappa delle competenze",
        "themes": "Esperienze",
        "development": "Risultati",
        "key_takeaways": "Obiettivi",
        "connections": "Coerenza del profilo",
        "conclusion": "Sintesi professionale",
    },
    "storia_racconto": {
        "overview": "Introduzione",
        "map": "Arco narrativo",
        "themes": "Trama",
        "development": "Personaggi",
        "key_takeaways": "Conflitto ed evoluzione",
        "connections": "Snodi narrativi",
        "conclusion": "Lettura conclusiva",
    },
    "poesia_testo_letterario": {
        "overview": "Introduzione critica",
        "map": "Struttura metrica",
        "themes": "Temi",
        "development": "Immagini e figure",
        "key_takeaways": "Interpretazione",
        "connections": "Risonanze interne",
        "conclusion": "Conclusione critica",
    },
    "sport_allenamento": {
        "overview": "Obiettivi della scheda",
        "map": "Progressioni",
        "themes": "Esercizi",
        "development": "Tecnica",
        "key_takeaways": "Recupero e nutrizione",
        "connections": "Equilibrio del programma",
        "conclusion": "Sintesi dell'allenamento",
    },
    "appunti_misti": {
        "overview": "Quadro d'insieme",
        "map": "Argomenti principali",
        "themes": "Sotto-argomenti",
        "development": "Priorita",
        "key_takeaways": "Domande aperte",
        "connections": "Collegamenti utili",
        "conclusion": "Chiusura ragionata",
    },
}

PROFILE_MARKERS: Dict[str, Sequence[str]] = {
    "manuale_aziendale": (
        "processo", "procedura", "controllo", "audit", "responsabile",
        "responsabilita", "rischio", "workflow", "owner", "operativo",
        "conformita", "cliente", "reclamo",
    ),
    "dispensa_scolastica_universitaria": (
        "definizione", "concetto", "esempio", "lezione", "capitolo",
        "studente", "universita", "scolastico", "teoria", "esercizio",
        "spiega", "apprendimento",
    ),
    "documento_tecnico": (
        "architettura", "configurazione", "database", "server", "api",
        "componente", "modulo", "errore", "sistema", "versione",
        "installazione", "parametro", "endpoint",
    ),
    "documento_legale_amministrativo": (
        "articolo", "comma", "decreto", "legge", "obbligo", "scadenza",
        "amministrativo", "contratto", "norma", "autorizzazione",
        "sanzione", "ente", "istanza",
    ),
    "cv_profilo_professionale": (
        "curriculum", "profilo", "esperienza", "competenze", "ruolo",
        "azienda", "progetto", "risultati", "obiettivi", "professionale",
        "formazione", "certificazione",
    ),
    "storia_racconto": (
        "personaggio", "trama", "racconto", "romanzo", "scena", "capitolo",
        "narratore", "conflitto", "dialogo", "protagonista", "finale",
    ),
    "poesia_testo_letterario": (
        "poesia", "verso", "strofa", "metrica", "ritmo", "simbolo",
        "immagine", "figura", "tono", "lirico", "metafora",
    ),
    "sport_allenamento": (
        "allenamento", "esercizio", "serie", "ripetizioni", "recupero",
        "nutrizione", "tecnica", "carico", "progressione", "scheda",
        "mobilita",
    ),
    "appunti_misti": (
        "appunti", "nota", "schema", "promemoria", "argomento",
        "domanda", "priorita", "bozza", "riepilogo",
    ),
}

DETAIL_KEYS_BY_PROFILE: Dict[str, Sequence[str]] = {
    "manuale_aziendale": ("procedures", "responsibilities", "risks", "operational_facts", "definitions"),
    "dispensa_scolastica_universitaria": ("definitions", "operational_facts", "procedures", "operational_decisions"),
    "documento_tecnico": ("procedures", "definitions", "operational_facts", "risks"),
    "documento_legale_amministrativo": ("definitions", "responsibilities", "procedures", "risks", "operational_facts"),
    "cv_profilo_professionale": ("responsibilities", "operational_facts", "operational_decisions", "definitions"),
    "storia_racconto": ("operational_facts", "operational_decisions", "definitions", "risks"),
    "poesia_testo_letterario": ("definitions", "operational_facts", "operational_decisions"),
    "sport_allenamento": ("procedures", "operational_facts", "risks", "definitions"),
    "appunti_misti": ("operational_facts", "definitions", "procedures", "operational_decisions", "risks"),
}


def _clean_spaces(text: str) -> str:
    return re.sub(r"[ \t]+", " ", str(text or "").replace("\r", "\n")).strip()


def _word_tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def _word_count(text: str) -> int:
    return len(_word_tokens(text))


def _finish_sentence(text: str) -> str:
    clean = re.sub(r"\s+", " ", str(text or "").strip(" -•\t"))
    if clean and clean[-1] not in ".!?":
        clean += "."
    return clean


def _split_sentences(text: str) -> List[str]:
    raw = _clean_spaces(text)
    parts = re.split(r"(?<=[.!?])\s+|\n+", raw)
    return [_finish_sentence(part) for part in parts if _word_count(part) >= 6]


def _normal_key(text: str) -> str:
    words = [
        w.lower()
        for w in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{4,}", str(text or ""))
        if w.lower() not in STOPWORDS
    ]
    return " ".join(words[:12])


def _dedupe_strings(items: Iterable[str], limit: int | None = None) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        clean = _finish_sentence(str(item or ""))
        if not clean:
            continue
        key = _normal_key(clean)
        if not key or key in seen:
            continue
        seen.add(key)
        out.append(clean)
        if limit is not None and len(out) >= limit:
            break
    return out


def _keywords(text: str, limit: int = 14) -> List[str]:
    words = [
        w.lower()
        for w in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ]{4,}", str(text or ""))
        if w.lower() not in STOPWORDS
    ]
    counts = Counter(words)
    return [word for word, _ in counts.most_common(limit)]


def _topic_tokens(value: str) -> set[str]:
    return {
        w.lower()
        for w in re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]{4,}", str(value or ""))
        if w.lower() not in STOPWORDS
    }


def _as_list(value: Any) -> List[str]:
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    if value:
        return [str(value).strip()]
    return []


def _join_natural(items: Sequence[str], limit: int = 5) -> str:
    clean = [str(item).strip(" .") for item in items if str(item).strip()]
    clean = clean[:limit]
    if not clean:
        return ""
    if len(clean) == 1:
        return clean[0]
    return ", ".join(clean[:-1]) + " e " + clean[-1]


def _clean_display_title(title: str) -> str:
    clean = re.sub(r"\s+", " ", str(title or "").strip(" .:-"))
    clean = re.sub(r"^\d{1,4}(?:\.\d{1,3})*\s*[-.)]?\s*", "", clean)
    return clean.strip(" .:-") or "Tema"


def _sentence_has_noise(sentence: str) -> bool:
    low = str(sentence or "").lower()
    return any(pattern in low for pattern in SYSTEM_NOISE_PATTERNS)


def _rewrite_template_sentence(sentence: str) -> str:
    text = _finish_sentence(sentence)
    text = re.sub(r"\bLa procedura richiede(?: che)?\s+", "Occorre ", text, flags=re.I)
    text = re.sub(r"\bOgni attivit[aà] deve\s+", "Le attivita prevedono di ", text, flags=re.I)
    text = re.sub(
        r"\bNel contesto\s+[^,]{1,100},\s+la sezione\s+[^,]{1,100}\s+descrive\s+",
        "Il testo presenta ",
        text,
        flags=re.I,
    )
    text = re.sub(r"\bLa sezione\s+[^,]{1,100}\s+descrive\s+", "Il testo presenta ", text, flags=re.I)
    text = re.sub(r"\bQuesto passaggio\b", "Questa parte", text, flags=re.I)
    text = re.sub(
        r"\bIl controllo\s+(CTRL[-_\s]?[A-Z0-9_-]+)\s+evita passaggi informali\b",
        r"\1 rafforza tracciabilita e coerenza",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"\bIl codice\s+(CTRL[-_\s]?[A-Z0-9_-]+)\s+richiede che\s+",
        r"Per \1, occorre ",
        text,
        flags=re.I,
    )
    text = re.sub(
        r"\bLa macro-area\s+([^,.]{1,80})\s+stabilisce come\s+",
        r"\1 chiarisce come ",
        text,
        flags=re.I,
    )
    text = re.sub(r"\bMacro-area\s+\d+\s*[-:]\s*", "", text, flags=re.I)
    text = re.sub(r"\s+\d{1,4}\.$", ".", text)
    text = re.sub(r"\s+", " ", text).strip()
    return _finish_sentence(text)


def detect_document_profile(global_map: Dict[str, Any], original_text_sample: str) -> Dict[str, Any]:
    """Riconosce il profilo del documento e restituisce lessico adattivo."""
    topics = " ".join(_as_list(global_map.get("global_topics")))
    outline = " ".join(str(item.get("title") or "") for item in global_map.get("chronological_outline", [])[:20])
    sample = f"{topics} {outline} {str(original_text_sample or '')[:12000]}".lower()

    scores: Dict[str, int] = {}
    for profile, markers in PROFILE_MARKERS.items():
        scores[profile] = sum(1 for marker in markers if marker in sample)

    tipo_testo = max(scores, key=lambda key: (scores[key], key))
    best_score = scores.get(tipo_testo, 0)
    if best_score <= 1:
        tipo_testo = "appunti_misti"
    confidence = min(0.95, 0.35 + (best_score * 0.08))
    if tipo_testo == "appunti_misti" and best_score <= 1:
        confidence = 0.45

    focus_keywords = _as_list(global_map.get("global_topics"))[:12]
    if len(focus_keywords) < 6:
        focus_keywords.extend(_keywords(sample, 12))
    focus_keywords = _dedupe_plain(focus_keywords, 12)

    style_by_profile = {
        "manuale_aziendale": "sintesi operativa, fluida e orientata a responsabilita, controlli e rischi",
        "dispensa_scolastica_universitaria": "spiegazione didattica progressiva, con concetti collegati tra loro",
        "documento_tecnico": "sintesi tecnica ordinata, centrata su componenti, flussi e condizioni operative",
        "documento_legale_amministrativo": "lettura normativa chiara, con soggetti, obblighi e vincoli in relazione",
        "cv_profilo_professionale": "profilo professionale narrativo, centrato su competenze, esperienze e risultati",
        "storia_racconto": "lettura narrativa, attenta ad arco, personaggi e trasformazioni",
        "poesia_testo_letterario": "commento critico, attento a immagini, tono e interpretazione",
        "sport_allenamento": "sintesi pratica, orientata a obiettivi, tecnica, progressione e recupero",
        "appunti_misti": "quadro ragionato che ordina argomenti, priorita e domande aperte",
    }

    return {
        "tipo_testo": tipo_testo,
        "confidence": round(confidence, 2),
        "focus_keywords": focus_keywords,
        "vocabolario_sezioni": dict(VOCABULARY[tipo_testo]),
        "stile_narrativo": style_by_profile[tipo_testo],
    }


def _dedupe_plain(items: Iterable[str], limit: int | None = None) -> List[str]:
    out: List[str] = []
    seen = set()
    for item in items:
        clean = re.sub(r"\s+", " ", str(item or "").strip(" .,:;"))
        if not clean:
            continue
        key = clean.lower()
        if key in seen:
            continue
        seen.add(key)
        out.append(clean)
        if limit is not None and len(out) >= limit:
            break
    return out


def _extract_digest_details(digest: Dict[str, Any], profile: str) -> List[str]:
    details: List[str] = []
    for key in DETAIL_KEYS_BY_PROFILE.get(profile, DETAIL_KEYS_BY_PROFILE["appunti_misti"]):
        details.extend(_as_list(digest.get(key)))
    details.append(str(digest.get("summary_anchor") or ""))
    return _dedupe_strings((remove_template_noise(item) for item in details), 8)


def _best_theme_title(digest: Dict[str, Any], fallback_index: int) -> str:
    title = str(digest.get("title") or "").strip(" .:-")
    title_low = title.lower()
    generic = not title or title_low.startswith(("parte ", "macro area", "macro-area", "apertura del documento"))
    topics = _as_list(digest.get("main_topics") or digest.get("themes"))
    if title_low.startswith("riferimento sezione"):
        anchor = str(digest.get("summary_anchor") or "")
        match = re.search(r"\bgestire\s+([^,.]{4,90}?)\s+quando\b", anchor, flags=re.I)
        if match:
            candidate = match.group(1).strip(" .:-")
            if candidate:
                return candidate[:1].upper() + candidate[1:90]
        generic = True
    if generic and topics:
        return " ".join(word.capitalize() for word in topics[0].split()[:5])
    if title:
        return _clean_display_title(title[:90])
    return f"Tema {fallback_index}"


def build_dynamic_theme_tree(global_map: Dict[str, Any], domain_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Costruisce temi dal contenuto G.1, senza macro-aree universali fisse."""
    profile = str(domain_profile.get("tipo_testo") or "appunti_misti")
    digests = list(global_map.get("block_digests") or [])
    themes: List[Dict[str, Any]] = []

    for digest in digests:
        topics = _dedupe_plain(
            _as_list(digest.get("main_topics")) + _as_list(digest.get("themes")) + _as_list(digest.get("good_keywords")),
            10,
        )
        title = _best_theme_title(digest, len(themes) + 1)
        token_set = _topic_tokens(" ".join([title] + topics))
        if not token_set:
            token_set = _topic_tokens(str(digest.get("summary_anchor") or title))

        details = _extract_digest_details(digest, profile)
        block_index = int(digest.get("index") or len(themes) + 1)

        best_theme: Dict[str, Any] | None = None
        best_overlap = 0
        title_tokens = _topic_tokens(title)
        for theme in themes:
            overlap = len(token_set.intersection(theme.get("token_set", set())))
            existing_title_tokens = _topic_tokens(str(theme.get("title") or ""))
            title_overlap = len(title_tokens.intersection(existing_title_tokens))
            if title_overlap >= 2 and overlap > best_overlap:
                best_overlap = overlap
                best_theme = theme

        if best_theme is not None and best_overlap >= 4:
            best_theme["keywords"] = _dedupe_plain(best_theme["keywords"] + topics, 12)
            best_theme["token_set"].update(token_set)
            best_theme["blocks"].append(block_index)
            best_theme["coverage_positions"].append(block_index)
            best_theme["details"] = _dedupe_strings(best_theme["details"] + details, 14)
            best_theme["anchors"] = _dedupe_strings(best_theme["anchors"] + [str(digest.get("summary_anchor") or "")], 8)
        else:
            themes.append(
                {
                    "theme_id": f"theme_{len(themes) + 1:02d}",
                    "title": title,
                    "keywords": topics,
                    "token_set": token_set,
                    "blocks": [block_index],
                    "coverage_positions": [block_index],
                    "details": details,
                    "anchors": _dedupe_strings([str(digest.get("summary_anchor") or "")], 4),
                    "weight": max(1, int(digest.get("word_count") or 0)),
                }
            )

    for target in global_map.get("coverage_targets", []):
        block_index = int(target.get("macro_block") or 0)
        target_topics = _as_list(target.get("topics"))
        if not block_index or not target_topics:
            continue
        if any(block_index in theme.get("blocks", []) for theme in themes):
            continue
        themes.append(
            {
                "theme_id": f"theme_{len(themes) + 1:02d}",
                "title": _best_theme_title({"title": target.get("title"), "main_topics": target_topics}, len(themes) + 1),
                "keywords": target_topics[:8],
                "token_set": _topic_tokens(" ".join(target_topics)),
                "blocks": [block_index],
                "coverage_positions": [block_index],
                "details": [],
                "anchors": [],
                "weight": 1,
            }
        )

    ordered_themes = sorted(
        themes,
        key=lambda item: (min(item.get("coverage_positions") or [9999]), -len(item.get("details") or [])),
    )
    for theme in ordered_themes:
        theme.pop("token_set", None)

    return {
        "phase": PHASE,
        "profile": domain_profile,
        "themes": ordered_themes,
        "coverage": {
            "input_words": global_map.get("input_words"),
            "macro_blocks_count": global_map.get("macro_blocks_count"),
            "covered_blocks": sorted({block for theme in ordered_themes for block in theme.get("blocks", [])}),
        },
        "global_topics": _as_list(global_map.get("global_topics"))[:20],
    }


def remove_template_noise(text: str) -> str:
    """Rimuove rumore di sistema e riscrive formule meccaniche ricorrenti."""
    if not str(text or "").strip():
        return ""
    sentences = _split_sentences(str(text or ""))
    if not sentences:
        sentences = [_finish_sentence(text)]
    cleaned: List[str] = []
    for sentence in sentences:
        if _sentence_has_noise(sentence):
            continue
        rewritten = _rewrite_template_sentence(sentence)
        if rewritten and not _sentence_has_noise(rewritten):
            cleaned.append(rewritten)
    return " ".join(_dedupe_strings(cleaned))


def merge_repetitive_blocks(theme_tree: Dict[str, Any]) -> Dict[str, Any]:
    """Fonde dettagli simili dentro e tra temi, preservando copertura."""
    merged = dict(theme_tree)
    themes = [dict(theme) for theme in theme_tree.get("themes", [])]
    final_themes: List[Dict[str, Any]] = []

    for theme in themes:
        theme["details"] = _dedupe_strings(theme.get("details", []), 14)
        theme["anchors"] = _dedupe_strings(theme.get("anchors", []), 8)
        tokens = _topic_tokens(" ".join([theme.get("title", "")] + theme.get("keywords", [])))
        title_tokens = _topic_tokens(str(theme.get("title") or ""))

        target: Dict[str, Any] | None = None
        for existing in final_themes:
            existing_tokens = _topic_tokens(" ".join([existing.get("title", "")] + existing.get("keywords", [])))
            existing_title_tokens = _topic_tokens(str(existing.get("title") or ""))
            if (
                len(title_tokens.intersection(existing_title_tokens)) >= 2
                and len(tokens.intersection(existing_tokens)) >= 4
            ):
                target = existing
                break
        if target is None:
            final_themes.append(theme)
            continue

        target["keywords"] = _dedupe_plain(target.get("keywords", []) + theme.get("keywords", []), 12)
        target["blocks"] = sorted(set(target.get("blocks", []) + theme.get("blocks", [])))
        target["coverage_positions"] = sorted(set(target.get("coverage_positions", []) + theme.get("coverage_positions", [])))
        target["details"] = _dedupe_strings(target.get("details", []) + theme.get("details", []), 16)
        target["anchors"] = _dedupe_strings(target.get("anchors", []) + theme.get("anchors", []), 10)
        target["weight"] = int(target.get("weight") or 0) + int(theme.get("weight") or 0)

    merged["themes"] = sorted(final_themes, key=lambda item: min(item.get("coverage_positions") or [9999]))
    merged["merge_metrics"] = {
        "themes_before": len(themes),
        "themes_after": len(final_themes),
        "repetitive_themes_merged": max(0, len(themes) - len(final_themes)),
    }
    merged["coverage"] = dict(merged.get("coverage") or {})
    merged["coverage"]["covered_blocks"] = sorted(
        {block for theme in merged["themes"] for block in theme.get("blocks", [])}
    )
    return merged


def _section(title: str, body: str) -> Dict[str, str]:
    return {"title": title, "text": remove_template_noise(body)}


def _theme_sentence(theme: Dict[str, Any], profile: Dict[str, Any], max_details: int = 2) -> str:
    title = _clean_display_title(str(theme.get("title") or "tema"))
    keywords = _join_natural(theme.get("keywords", []), 4)
    details = [
        remove_template_noise(detail).strip(" .!?")
        for detail in _dedupe_strings(theme.get("details", []) + theme.get("anchors", []), max_details)
        if remove_template_noise(detail).strip(" .!?")
    ]
    detail_text = "; ".join(details)
    if keywords and detail_text:
        return (
            f"{title} raccoglie {keywords}; nel percorso del testo questo nucleo viene sviluppato "
            f"attraverso elementi concreti: {detail_text}"
        )
    if detail_text:
        return f"{title} diventa un nucleo importante perche' chiarisce: {detail_text}"
    if keywords:
        return f"{title} organizza temi come {keywords}, dando continuita alla lettura complessiva."
    return f"{title} contribuisce alla struttura generale del contenuto."


def _build_summary_text(sections: Sequence[Dict[str, str]]) -> str:
    parts = []
    for section in sections:
        title = str(section.get("title") or "").strip()
        text = str(section.get("text") or "").strip()
        if title and text:
            parts.append(f"{title}\n{text}")
    return "\n\n".join(parts).strip()


def _coverage_expansion_paragraph(
    pass_index: int,
    themes: Sequence[Dict[str, Any]],
    profile: Dict[str, Any],
) -> str:
    focus = profile.get("focus_keywords") or []
    selected = list(themes)[(pass_index - 1) * 3 : (pass_index - 1) * 3 + 4] or list(themes)[:4]
    titles = [_clean_display_title(str(theme.get("title") or "")) for theme in selected if theme.get("title")]
    keywords = _dedupe_plain(
        [kw for theme in selected for kw in theme.get("keywords", [])] + list(focus),
        10,
    )
    if pass_index == 1:
        lead = "L'approfondimento chiarisce il modo in cui i nuclei principali restano collegati."
    elif pass_index == 2:
        lead = "Una seconda lettura mette in evidenza la continuita tra parti iniziali e sviluppi successivi."
    else:
        lead = "La chiusura dell'approfondimento consolida i passaggi meno visibili ma utili alla comprensione."
    return (
        f"{lead} In particolare, {_join_natural(titles, 4) or 'i temi ricorrenti'} non va letto come "
        f"un elenco separato, perche' richiama {_join_natural(keywords, 7) or 'i riferimenti centrali'} "
        "e li usa per dare ordine al percorso. Questo permette di mantenere copertura anche quando "
        "alcuni contenuti ritornano piu' volte con formulazioni simili, distinguendo cio' che introduce "
        "il quadro, cio' che lo sviluppa e cio' che ne mostra conseguenze o applicazioni."
    )


def _details_expansion_paragraph(pass_index: int, themes: Sequence[Dict[str, Any]]) -> str:
    selected = list(themes)[:5]
    titles = [_clean_display_title(str(theme.get("title") or "")) for theme in selected if theme.get("title")]
    details: List[str] = []
    for theme in selected:
        for detail in _dedupe_strings(theme.get("details", []) + theme.get("anchors", []), 3):
            fragment = remove_template_noise(detail).strip(" .!?")
            if fragment:
                details.append(fragment)
    details = _dedupe_plain(details, 7)
    lead_by_pass = {
        1: "Sul piano dei dettagli, il testo chiarisce perche' i temi principali restano collegati.",
        2: "Nel passaggio successivo, la sintesi recupera elementi distribuiti che rafforzano la copertura.",
        3: "Infine, l'approfondimento mantiene visibili i riferimenti che sostengono la lettura complessiva.",
    }
    return (
        f"{lead_by_pass.get(pass_index, lead_by_pass[3])} "
        f"Il percorso attraversa {_join_natural(titles, 5) or 'le aree centrali'} e mette in relazione "
        f"{'; '.join(details) if details else 'i dettagli ricorrenti del documento'}."
    )


def _theme_cluster_paragraph(
    cluster_index: int,
    themes: Sequence[Dict[str, Any]],
    profile: Dict[str, Any],
) -> str:
    selected = list(themes)
    titles = [_clean_display_title(str(theme.get("title") or "")) for theme in selected if theme.get("title")]
    keywords = _dedupe_plain([kw for theme in selected for kw in theme.get("keywords", [])], 10)
    details: List[str] = []
    for theme in selected:
        theme_details = _dedupe_strings(theme.get("details", []) + theme.get("anchors", []), 4)
        for fragment in theme_details:
            clean_fragment = remove_template_noise(fragment).strip(" .!?")
            if clean_fragment:
                details.append(clean_fragment)
    details = _dedupe_plain(details, 12)
    first_details = "; ".join(details[:4]) or "i controlli e le evidenze collegate ai temi del gruppo"
    second_details = "; ".join(details[4:8]) or "le responsabilita, le verifiche e le conseguenze operative"
    third_details = "; ".join(details[8:12]) or "i casi ricorrenti che rendono il tema applicabile"
    title_text = _join_natural(titles, 6) or "questo gruppo di temi"
    keyword_text = _join_natural(keywords, 8) or "i concetti principali"
    style = str(profile.get("stile_narrativo") or "sintesi ragionata")
    return (
        f"Nel gruppo {cluster_index}, {title_text} viene letto con una {style}: il filo comune riguarda "
        f"{keyword_text}, mette insieme {first_details}, collega {second_details} e chiarisce {third_details}; "
        "questa lettura tiene gli elementi nello stesso paragrafo per evitare un elenco di schede separate, "
        "mostrando come temi vicini si sostengano a vicenda, quali passaggi richiedano evidenze, quali ruoli "
        "rendano stabile la decisione e quali controlli permettano di confrontare reparti, sedi, fornitori "
        "o momenti diversi dello stesso flusso."
    )


def build_universal_thematic_summary(
    theme_tree: Dict[str, Any],
    domain_profile: Dict[str, Any],
    original_text: str,
    g1_summary: str,
) -> Dict[str, Any]:
    """Produce una sintesi tematica universale adattata al profilo documento."""
    vocab = dict(domain_profile.get("vocabolario_sezioni") or VOCABULARY["appunti_misti"])
    themes = list(theme_tree.get("themes") or [])
    focus_keywords = domain_profile.get("focus_keywords") or theme_tree.get("global_topics") or []
    macro_blocks_count = int((theme_tree.get("coverage") or {}).get("macro_blocks_count") or len(themes))
    original_words = _word_count(original_text)

    if not themes and g1_summary:
        themes = [
            {
                "title": "Sintesi del contenuto",
                "keywords": focus_keywords[:8],
                "details": _split_sentences(g1_summary)[:8],
                "anchors": [],
                "blocks": [],
                "coverage_positions": [],
            }
        ]

    opening_focus = _join_natural(focus_keywords, 7) or "i nuclei principali del contenuto"
    first_titles = [theme.get("title", "") for theme in themes[:4]]
    later_titles = [theme.get("title", "") for theme in themes[4:8]]

    sections = [
        _section(
            "Sintesi tematica",
            (
                f"Il testo viene letto come {domain_profile.get('tipo_testo', 'documento')} e richiede "
                f"uno stile di sintesi {domain_profile.get('stile_narrativo', 'ragionato')}. "
                f"Il baricentro riguarda {opening_focus}, con una copertura distribuita lungo "
                f"{macro_blocks_count} blocchi di contenuto."
            ),
        ),
        _section(
            vocab["overview"],
            (
                "La sintesi mette in relazione le parti invece di accumulare voci isolate. "
                f"I temi iniziali aprono il quadro su {_join_natural(first_titles, 4) or opening_focus}; "
                f"le parti successive lo ampliano con {_join_natural(later_titles, 4) or 'sviluppi coerenti'}."
            ),
        ),
        _section(
            vocab["map"],
            (
                "La progressione segue l'ordine del documento: prima introduce il lessico e gli elementi "
                "di base, poi chiarisce come i nuclei centrali si trasformano in scelte, vincoli, esempi "
                "o passaggi applicativi. Questa mappa conserva la distribuzione originale senza ridurre "
                "il testo a un indice di blocchi."
            ),
        ),
        _section(
            vocab["themes"],
            " ".join(_theme_sentence(theme, domain_profile, 1) for theme in themes[:4]),
        ),
        _section(
            vocab["development"],
            " ".join(_theme_sentence(theme, domain_profile, 2) for theme in themes[4:12] or themes[:2]),
        ),
        _section(
            vocab["key_takeaways"],
            (
                "Gli elementi da ricordare sono quelli che ritornano in piu' punti e danno struttura "
                f"al materiale: {_join_natural(focus_keywords, 8) or 'i concetti centrali'}. "
                "Questi nuclei servono sia per ricostruire il contenuto sia per trasformarlo in studio, "
                "ripasso o controllo di comprensione."
            ),
        ),
        _section(
            vocab["connections"],
            (
                "Le parti non funzionano come compartimenti separati: i temi di apertura preparano quelli "
                "successivi, mentre i dettagli ricorrenti rafforzano continuita, priorita e conseguenze. "
                "La lettura complessiva mostra quindi come definizioni, esempi, vincoli o azioni si "
                "sostengano a vicenda."
            ),
        ),
        _section(
            vocab["conclusion"],
            (
                "Il risultato e' una sintesi ragionata che conserva copertura e ordine, ma privilegia "
                "relazioni tematiche e sviluppo naturale. Il documento puo' essere ripreso partendo dai "
                "nuclei centrali e seguendo i collegamenti tra le parti, senza perdere i passaggi meno "
                "visibili della seconda meta del testo."
            ),
        ),
    ]

    sections = [_section(section["title"], section["text"]) for section in sections if section.get("text")]
    summary_text = _build_summary_text(sections)
    covered = [theme.get("title") for theme in themes if theme.get("title")]
    metrics = {
        "original_words": original_words,
        "summary_words": _word_count(summary_text),
        "coverage_ratio_words": round(_word_count(summary_text) / max(1, original_words), 3),
        "themes_available": len(themes),
        "themes_covered": len(covered),
        "target_words_10_percent": int(original_words * 0.10),
    }
    return {
        "summary_text": summary_text,
        "sections": sections,
        "profile": domain_profile,
        "themes_covered": covered,
        "warnings": [],
        "metrics": metrics,
    }


def _sentences_for_theme(original_text: str, theme: Dict[str, Any], limit: int = 4) -> List[str]:
    tokens = _topic_tokens(" ".join([theme.get("title", "")] + theme.get("keywords", [])))
    if not tokens:
        return []
    selected: List[str] = []
    for sentence in _split_sentences(original_text):
        low_tokens = _topic_tokens(sentence)
        if len(tokens.intersection(low_tokens)) >= 1 and not _sentence_has_noise(sentence):
            selected.append(_rewrite_template_sentence(sentence))
        if len(selected) >= limit:
            break
    return _dedupe_strings(selected, limit)


def expand_until_target_ratio(
    summary_result: Dict[str, Any],
    theme_tree: Dict[str, Any],
    original_text: str,
    target_ratio: float = 0.10,
) -> Dict[str, Any]:
    """Espande i temi meno coperti fino al target, con poche passate stabili."""
    result = dict(summary_result)
    sections = [dict(section) for section in result.get("sections", [])]
    original_words = _word_count(original_text)
    target_words = int(original_words * target_ratio)
    target_words = max(target_words, 1)
    themes = list(theme_tree.get("themes") or [])
    warnings = list(result.get("warnings") or [])
    expansion_passes = 0
    used_keys = {_normal_key(section.get("text", "")) for section in sections}

    while _word_count(_build_summary_text(sections)) < target_words and expansion_passes < 3:
        expansion_passes += 1
        current_text = _build_summary_text(sections).lower()
        theme_scores: List[Tuple[int, Dict[str, Any]]] = []
        for theme in themes:
            title = str(theme.get("title") or "")
            keywords = [title] + list(theme.get("keywords") or [])
            score = sum(1 for item in keywords if item and item.lower() in current_text)
            theme_scores.append((score, theme))
        theme_scores.sort(key=lambda item: (item[0], min(item[1].get("coverage_positions") or [9999])))

        additions: List[str] = []
        ordered_themes = [theme for _, theme in theme_scores]
        chunk_size = 2 if len(ordered_themes) >= 24 else 4
        for start in range(0, len(ordered_themes), chunk_size):
            selected_themes = ordered_themes[start : start + chunk_size]
            if not selected_themes:
                continue
            paragraph = _theme_cluster_paragraph(
                (expansion_passes - 1) * max(1, (len(ordered_themes) + chunk_size - 1) // chunk_size)
                + (start // chunk_size)
                + 1,
                selected_themes,
                result.get("profile", {}),
            )
            key = f"cluster_{expansion_passes}_{start}_{_normal_key(' '.join(str(theme.get('title') or '') for theme in selected_themes))}"
            if key and key not in used_keys:
                used_keys.add(key)
                additions.append(paragraph)
            if _word_count(_build_summary_text(sections) + " " + " ".join(additions)) >= target_words:
                break

        current_with_additions = _build_summary_text(sections) + " " + " ".join(additions)
        if _word_count(current_with_additions) < target_words:
            selected_themes = ordered_themes[: max(4, min(8, len(ordered_themes)))]
            paragraph = _coverage_expansion_paragraph(expansion_passes, selected_themes, result.get("profile", {}))
            key = _normal_key(paragraph)
            if key and key not in used_keys:
                used_keys.add(key)
                additions.append(paragraph)
        if not additions:
            break
        title = (result.get("profile", {}).get("vocabolario_sezioni") or {}).get("development", "Sviluppo dei temi")
        cleaned_additions = [remove_template_noise(addition) for addition in additions if str(addition or "").strip()]
        sections.append({"title": f"{title} - approfondimento {expansion_passes}", "text": " ".join(cleaned_additions).strip()})

    sections = [
        {"title": str(section.get("title", "")).strip(), "text": str(section.get("text", "")).strip()}
        for section in sections
        if str(section.get("text", "")).strip()
    ]
    summary_text = _build_summary_text(sections)
    summary_words = _word_count(summary_text)
    reached = summary_words >= target_words
    if not reached:
        warnings.append(
            "target_10_percent_non_raggiunto_con_materiale_tematico_disponibile"
        )

    metrics = dict(result.get("metrics") or {})
    metrics.update(
        {
            "original_words": original_words,
            "target_words_10_percent": target_words,
            "summary_words": summary_words,
            "coverage_ratio_words": round(summary_words / max(1, original_words), 3),
            "target_10_percent_reached": reached,
            "expansion_passes": expansion_passes,
        }
    )
    result.update(
        {
            "summary_text": summary_text,
            "sections": sections,
            "warnings": _dedupe_plain(warnings),
            "metrics": metrics,
        }
    )
    return result


def validate_universal_summary_quality(summary_text: str, domain_profile: Dict[str, Any]) -> Dict[str, Any]:
    """Validazione G.2 locale, separata dal Quality Manager comune."""
    text = str(summary_text or "")
    low = text.lower()
    sentences = _split_sentences(text)
    system_noise_count = sum(low.count(pattern) for pattern in SYSTEM_NOISE_PATTERNS)
    template_phrase_count = sum(len(re.findall(pattern, low, flags=re.I)) for pattern in TEMPLATE_PATTERNS)

    starts = [
        " ".join(_word_tokens(sentence.lower())[:3])
        for sentence in sentences
        if len(_word_tokens(sentence)) >= 5
    ]
    repeated_sentence_patterns = sum(count - 1 for count in Counter(starts).values() if count > 1)
    broken_sentence_count = sum(
        1
        for sentence in sentences
        if _word_count(sentence) >= 8 and sentence[-1] not in ".!?"
    )
    catalog_lines = [
        line for line in text.splitlines()
        if re.match(r"^\s*(?:[-*•]|\d+[.)]|macro-area\s+\d+)", line, flags=re.I)
    ]
    catalog_effect = len(catalog_lines) >= 5

    vocab = domain_profile.get("vocabolario_sezioni") or {}
    section_hits = sum(1 for title in vocab.values() if str(title or "").lower() in low)

    defects: List[str] = []
    warnings: List[str] = []
    if system_noise_count:
        defects.append("system_noise_present")
    if template_phrase_count > 3:
        warnings.append("template_phrase_count_high")
    if repeated_sentence_patterns > 4:
        warnings.append("repeated_sentence_patterns_high")
    if broken_sentence_count:
        defects.append("broken_sentences_present")
    if catalog_effect:
        warnings.append("catalog_effect_possible")
    if section_hits < 4:
        warnings.append("few_profile_sections_detected")
    if _word_count(text) < 120:
        warnings.append("summary_too_short_for_long_document")

    return {
        "approved": not defects,
        "defects": defects,
        "warnings": warnings,
        "metrics": {
            "system_noise_count": system_noise_count,
            "template_phrase_count": template_phrase_count,
            "repeated_sentence_patterns": repeated_sentence_patterns,
            "broken_sentence_count": broken_sentence_count,
            "catalog_effect": catalog_effect,
            "profile_section_hits": section_hits,
            "language_natural": template_phrase_count <= 3 and not catalog_effect,
        },
    }


def smooth_long_summary(global_map: Dict[str, Any], original_text: str, g1_summary: str) -> Dict[str, Any]:
    """Facade usata dall'orchestratore G.1 nel solo ramo summary long-doc."""
    profile = detect_document_profile(global_map, original_text[:14000])
    theme_tree = build_dynamic_theme_tree(global_map, profile)
    theme_tree = merge_repetitive_blocks(theme_tree)
    base = build_universal_thematic_summary(theme_tree, profile, original_text, g1_summary)
    expanded = expand_until_target_ratio(base, theme_tree, original_text, target_ratio=0.10)
    validation = validate_universal_summary_quality(expanded["summary_text"], profile)
    metrics = dict(expanded.get("metrics") or {})
    metrics.update(
        {
            "theme_count": len(theme_tree.get("themes", [])),
            "covered_blocks": (theme_tree.get("coverage") or {}).get("covered_blocks", []),
            "merge_metrics": theme_tree.get("merge_metrics", {}),
            "validation_metrics": validation.get("metrics", {}),
        }
    )
    warnings = _dedupe_plain(list(expanded.get("warnings") or []) + list(validation.get("warnings") or []))
    return {
        "summary_text": expanded["summary_text"],
        "content": expanded["summary_text"],
        "sections": expanded.get("sections", []),
        "profile": profile,
        "theme_tree": theme_tree,
        "themes_covered": expanded.get("themes_covered", []),
        "warnings": warnings,
        "validation": validation,
        "metrics": metrics,
    }
