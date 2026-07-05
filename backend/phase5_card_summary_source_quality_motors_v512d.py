#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12D — CARD / SUMMARY / SOURCE QUALITY MOTORS V1

Motori atomici ricostruiti:
23. Card scritte bene
24. Card non troppo corte
25. Card non troppo compresse
26. Messaggio chiave completo
27. Riassunto chiaro
28. Punti chiave leggibili
29. Fonti visibili belle
30. Fonti coerenti
31. Niente fonti brutte
32. Layout grafico controllato

Questo modulo NON modifica i 33 motori già collegati.
Questo modulo NON modifica la pipeline 5.11.
Questo modulo NON tocca UI/PDF/CSS/app.
Questo modulo controlla la qualità dati/struttura delle card, non il CSS reale.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Callable, Optional, Set


PHASE = "5.12D"
VERSION = "v1"
READY_LABEL = "CARD_SUMMARY_SOURCE_QUALITY_MOTORS_V512D_READY"


@dataclass
class CardQualityIssue:
    motor_id: str
    severity: str
    message: str
    excerpt: str
    suggestion: str = ""


@dataclass
class CardQualityMotorResult:
    motor_id: str
    title: str
    status: str
    issues: List[CardQualityIssue]


@dataclass
class CardQualityReport:
    phase: str
    ready_label: str
    approved: bool
    status: str
    total_motors: int
    passed_motors: int
    failed_motors: int
    total_issues: int
    blocking_issues: int
    warning_issues: int
    results: List[CardQualityMotorResult]


STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "una", "uno",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "o", "che", "del", "della", "dei", "degli", "delle",
    "nel", "nella", "nei", "nelle", "questo", "questa", "questi",
    "queste", "come", "cosa", "quale", "quali", "perche", "perché",
    "quando", "dove", "puo", "può", "sono", "essere", "viene",
    "serve", "spiega", "indica", "descrivi", "risposta", "domanda",
    "card", "riassunto", "fonte", "fonti", "sezione",
}


GENERIC_PHRASES = [
    "documento analizzato",
    "contenuto generato",
    "contenuti generati",
    "testo fornito",
    "punto centrale",
    "argomento trattato",
    "informazioni principali",
    "elementi importanti",
    "varie cose",
    "diversi aspetti",
    "concetti principali",
    "tema generale",
    "sezione generica",
    "output prodotto",
]


UGLY_SOURCE_PHRASES = [
    "knowledge_base_json",
    "documento analizzato",
    "contenuti generati",
    "raw",
    "debug",
    "placeholder",
    "fallback",
    "demo",
    "todo",
    "mock",
    "stub",
    "/users/",
    "\\users\\",
    ".json",
    ".tmp",
    ".bak",
    "uuid",
]


def _clean_excerpt(text: Any, max_len: int = 150) -> str:
    value = re.sub(r"\s+", " ", str(text or "")).strip()
    if len(value) <= max_len:
        return value
    return value[: max_len - 3] + "..."


def _issue(
    motor_id: str,
    severity: str,
    message: str,
    excerpt: Any,
    suggestion: str = "",
) -> CardQualityIssue:
    return CardQualityIssue(
        motor_id=motor_id,
        severity=severity,
        message=message,
        excerpt=_clean_excerpt(excerpt),
        suggestion=suggestion,
    )


def _norm(text: Any) -> str:
    value = str(text or "").lower()
    value = value.replace("à", "a").replace("è", "e").replace("é", "e")
    value = value.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def _words(text: Any) -> List[str]:
    return [w for w in _norm(text).split() if len(w) >= 4 and w not in STOPWORDS]


def _word_count(text: Any) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", str(text or "")))


def _contains_generic(text: Any) -> bool:
    low = _norm(text)
    return any(_norm(p) in low for p in GENERIC_PHRASES)


def _contains_ugly_source(text: Any) -> bool:
    low = str(text or "").lower()
    return any(p in low for p in UGLY_SOURCE_PHRASES)


def _collect_text_values(payload: Any) -> List[str]:
    out: List[str] = []

    def walk(x: Any) -> None:
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for item in x:
                walk(item)
        elif x is not None:
            value = str(x).strip()
            if value:
                out.append(value)

    walk(payload)
    return out


def _payload_blob(payload: Any) -> str:
    return "\n".join(_collect_text_values(payload))


def _content_terms_without_sources(payload: Any) -> Set[str]:
    texts: List[str] = []

    def walk(x: Any, in_source: bool = False) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                key = str(k).lower()
                next_in_source = in_source or key in {"source", "fonte", "sources", "fonti"}
                walk(v, next_in_source)
        elif isinstance(x, list):
            for item in x:
                walk(item, in_source)
        elif x is not None and not in_source:
            value = str(x).strip()
            if value:
                texts.append(value)

    walk(payload)

    terms: Set[str] = set()
    for t in texts:
        terms.update(_words(t))
    return terms


def _as_list(value: Any) -> List[Any]:
    if isinstance(value, list):
        return value
    if value is None:
        return []
    return [value]


def _extract_cards(payload: Any) -> List[Dict[str, Any]]:
    cards: List[Dict[str, Any]] = []

    def scan(x: Any) -> None:
        if isinstance(x, dict):
            lower_keys = {str(k).lower(): k for k in x.keys()}

            title_key = None
            for key in {"title", "titolo"}:
                if key in lower_keys:
                    title_key = lower_keys[key]

            has_card_content = any(
                key in lower_keys
                for key in {
                    "key_message", "messaggio_chiave", "message_key",
                    "body", "text", "content", "contenuto", "description",
                    "bullets", "punti", "key_points", "punti_chiave",
                    "source", "fonte", "layout",
                }
            )

            if title_key and has_card_content:
                cards.append(dict(x))

            for v in x.values():
                scan(v)

        elif isinstance(x, list):
            for item in x:
                scan(item)

    scan(payload)

    seen = set()
    clean: List[Dict[str, Any]] = []
    for card in cards:
        key = _norm(str(card.get("title") or card.get("titolo") or "")) + "|" + _norm(str(card.get("key_message") or card.get("messaggio_chiave") or ""))
        if key not in seen:
            seen.add(key)
            clean.append(card)

    return clean


def _card_title(card: Dict[str, Any]) -> str:
    return str(card.get("title") or card.get("titolo") or "").strip()


def _card_key_message(card: Dict[str, Any]) -> str:
    return str(
        card.get("key_message")
        or card.get("messaggio_chiave")
        or card.get("message_key")
        or ""
    ).strip()


def _card_body(card: Dict[str, Any]) -> str:
    return str(
        card.get("body")
        or card.get("text")
        or card.get("content")
        or card.get("contenuto")
        or card.get("description")
        or ""
    ).strip()


def _card_bullets(card: Dict[str, Any]) -> List[str]:
    for key in ["bullets", "punti", "key_points", "punti_chiave"]:
        if key in card:
            return [str(x).strip() for x in _as_list(card.get(key)) if str(x).strip()]
    return []


def _card_source(card: Dict[str, Any]) -> str:
    return str(card.get("source") or card.get("fonte") or "").strip()


def _card_layout(card: Dict[str, Any]) -> Dict[str, Any]:
    layout = card.get("layout") or {}
    return layout if isinstance(layout, dict) else {}


def _card_text(card: Dict[str, Any]) -> str:
    parts = [
        _card_title(card),
        _card_key_message(card),
        _card_body(card),
        " ".join(_card_bullets(card)),
        _card_source(card),
    ]
    return " ".join([p for p in parts if p]).strip()


def _extract_summary(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        for key in ["summary", "riassunto", "sintesi"]:
            value = payload.get(key)
            if isinstance(value, dict):
                return value
            if isinstance(value, str):
                return {"text": value}

    return {}


def _summary_text(summary: Dict[str, Any]) -> str:
    return str(
        summary.get("text")
        or summary.get("body")
        or summary.get("content")
        or summary.get("riassunto")
        or ""
    ).strip()


def _summary_key_points(summary: Dict[str, Any]) -> List[str]:
    for key in ["key_points", "punti_chiave", "points", "punti"]:
        if key in summary:
            return [str(x).strip() for x in _as_list(summary.get(key)) if str(x).strip()]
    return []


def _extract_sources(payload: Any) -> List[str]:
    sources: List[str] = []

    def scan(x: Any) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                key = str(k).lower()
                if key in {"source", "fonte"}:
                    if isinstance(v, dict):
                        label = v.get("label") or v.get("title") or v.get("name") or v.get("text")
                        if label:
                            sources.append(str(label).strip())
                    else:
                        sources.append(str(v).strip())
                elif key in {"sources", "fonti"}:
                    if isinstance(v, list):
                        for item in v:
                            if isinstance(item, dict):
                                label = item.get("label") or item.get("title") or item.get("name") or item.get("text")
                                if label:
                                    sources.append(str(label).strip())
                            else:
                                sources.append(str(item).strip())
                    elif v:
                        sources.append(str(v).strip())

                scan(v)

        elif isinstance(x, list):
            for item in x:
                scan(item)

    scan(payload)

    clean = []
    seen = set()
    for s in sources:
        s = s.strip()
        if s and s not in seen:
            seen.add(s)
            clean.append(s)

    return clean


def _sentence_count(text: str) -> int:
    sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x.strip()]
    return len(sentences)


def _avg_sentence_words(text: str) -> float:
    sentences = [x.strip() for x in re.split(r"(?<=[.!?])\s+", text.strip()) if x.strip()]
    if not sentences:
        return float(_word_count(text))
    return sum(_word_count(s) for s in sentences) / max(1, len(sentences))


def motor_023_cards_well_written(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_023_card_riassunto_fonti_card_scritte_bene"
    title = "Card scritte bene"
    issues: List[CardQualityIssue] = []

    cards = _extract_cards(payload)

    if not cards:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna card rilevata.",
            payload,
            "Generare card strutturate con titolo, messaggio chiave, corpo, punti e fonte.",
        ))

    for card in cards:
        card_text = _card_text(card)
        title_text = _card_title(card)
        key_message = _card_key_message(card)
        body = _card_body(card)

        if _word_count(title_text) < 2:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Titolo card troppo povero o mancante.",
                title_text,
                "Usare un titolo specifico e leggibile.",
            ))

        if not key_message and not body:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Card senza testo principale.",
                card,
                "Aggiungere messaggio chiave o corpo della card.",
            ))

        if _contains_generic(card_text):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Card generica o poco specifica.",
                card_text,
                "Sostituire formule generiche con contenuto reale.",
            ))

        if re.search(r"\b(e|di|con|per|che|del|della)\s*$", card_text.lower().strip(" .,!?:;")):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Card con finale sospetto o frase incompleta.",
                card_text,
                "Completare la frase o il messaggio.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_024_cards_not_too_short(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_024_card_riassunto_fonti_card_non_troppo_corte"
    title = "Card non troppo corte"
    issues: List[CardQualityIssue] = []

    cards = _extract_cards(payload)

    if not cards:
        issues.append(_issue(motor_id, "blocking", "Nessuna card da controllare.", payload))

    for card in cards:
        text = _card_text(card)
        count = _word_count(text)

        if count < 35:
            issues.append(_issue(
                motor_id,
                "blocking",
                f"Card troppo corta: {count} parole.",
                text,
                "Espandere la card con messaggio chiave, spiegazione breve, punti e fonte.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_025_cards_not_too_compressed(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_025_card_riassunto_fonti_card_non_troppo_compresse"
    title = "Card non troppo compresse"
    issues: List[CardQualityIssue] = []

    cards = _extract_cards(payload)

    if not cards:
        issues.append(_issue(motor_id, "blocking", "Nessuna card da controllare.", payload))

    for card in cards:
        body = _card_body(card)
        bullets = _card_bullets(card)
        total_text = _card_text(card)

        body_words = _word_count(body)
        total_words = _word_count(total_text)
        avg_sentence_words = _avg_sentence_words(total_text)

        # Regola 1: molto testo nel corpo senza punti chiave = card compressa.
        # Soglia volutamente più severa della prima versione: una card didattica
        # con oltre 45 parole nel corpo e zero punti diventa difficile da leggere.
        if body_words > 45 and len(bullets) == 0:
            issues.append(_issue(
                motor_id,
                "blocking",
                f"Card troppo compressa: corpo da {body_words} parole senza punti leggibili.",
                body,
                "Dividere il contenuto in punti chiave o sezioni brevi.",
            ))

        # Regola 2: card lunga senza struttura a punti.
        if total_words > 65 and len(bullets) < 2:
            issues.append(_issue(
                motor_id,
                "blocking",
                f"Card lunga ma poco strutturata: {total_words} parole e meno di 2 punti.",
                total_text,
                "Aggiungere almeno due punti chiave leggibili.",
            ))

        # Regola 3: frasi troppo lunghe e dense.
        if avg_sentence_words > 32:
            issues.append(_issue(
                motor_id,
                "blocking",
                f"Card con frasi troppo lunghe e dense: media {avg_sentence_words:.1f} parole per frase.",
                total_text,
                "Spezzare le frasi e rendere la card più leggibile.",
            ))

        # Regola 4: punti chiave troppo lunghi.
        for bullet in bullets:
            if _word_count(bullet) > 24:
                issues.append(_issue(
                    motor_id,
                    "blocking",
                    "Punto della card troppo lungo e compresso.",
                    bullet,
                    "Accorciare il punto o dividerlo in due punti separati.",
                ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_026_key_message_complete(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_026_card_riassunto_fonti_messaggio_chiave_completo"
    title = "Messaggio chiave completo"
    issues: List[CardQualityIssue] = []

    cards = _extract_cards(payload)

    if not cards:
        issues.append(_issue(motor_id, "blocking", "Nessuna card da controllare.", payload))

    for card in cards:
        key_message = _card_key_message(card)

        if not key_message:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Messaggio chiave mancante.",
                card,
                "Aggiungere un messaggio chiave completo.",
            ))
            continue

        if _word_count(key_message) < 8:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Messaggio chiave troppo corto.",
                key_message,
                "Espandere il messaggio con soggetto, funzione e valore.",
            ))

        if _contains_generic(key_message):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Messaggio chiave generico.",
                key_message,
                "Usare un messaggio specifico del contenuto reale.",
            ))

        if not re.search(r"[.!?]$", key_message.strip()):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Messaggio chiave non chiuso da punteggiatura conclusiva.",
                key_message,
                "Chiudere il messaggio con punteggiatura corretta.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_027_summary_clear(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_027_card_riassunto_fonti_riassunto_chiaro"
    title = "Riassunto chiaro"
    issues: List[CardQualityIssue] = []

    summary = _extract_summary(payload)
    text = _summary_text(summary)

    if not text:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Riassunto mancante.",
            payload,
            "Aggiungere un riassunto chiaro.",
        ))
    else:
        if _word_count(text) < 35:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Riassunto troppo corto per essere chiaro.",
                text,
                "Aggiungere contesto, concetti principali e relazione tra i punti.",
            ))

        if _contains_generic(text):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Riassunto generico.",
                text,
                "Usare contenuto specifico invece di formule generiche.",
            ))

        if _sentence_count(text) < 2:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Riassunto poco articolato.",
                text,
                "Scrivere almeno due frasi chiare e collegate.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_028_key_points_legible(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_028_card_riassunto_fonti_punti_chiave_leggibili"
    title = "Punti chiave leggibili"
    issues: List[CardQualityIssue] = []

    summary = _extract_summary(payload)
    points = _summary_key_points(summary)

    if len(points) < 2:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Punti chiave mancanti o insufficienti.",
            summary,
            "Aggiungere almeno due punti chiave leggibili.",
        ))

    for point in points:
        wc = _word_count(point)

        if wc < 5:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Punto chiave troppo corto.",
                point,
                "Espandere il punto con un concetto comprensibile.",
            ))

        if wc > 24:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Punto chiave troppo lungo.",
                point,
                "Accorciare il punto e lasciare una sola idea principale.",
            ))

        if _contains_generic(point):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Punto chiave generico.",
                point,
                "Sostituire con un punto specifico del contenuto.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_029_sources_visible_beautiful(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_029_card_riassunto_fonti_fonti_visibili_belle"
    title = "Fonti visibili belle"
    issues: List[CardQualityIssue] = []

    sources = _extract_sources(payload)

    if not sources:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Fonti mancanti.",
            payload,
            "Aggiungere fonti visibili e leggibili.",
        ))

    for source in sources:
        if not source.lower().startswith("fonte:"):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Fonte non formattata in modo visibile.",
                source,
                "Usare formato leggibile, ad esempio: Fonte: sezione Backup periodico.",
            ))

        if _word_count(source) < 4:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Fonte troppo corta o poco descrittiva.",
                source,
                "Indicare sezione, tema o sottotema della fonte.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_030_sources_coherent(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_030_card_riassunto_fonti_fonti_coerenti"
    title = "Fonti coerenti"
    issues: List[CardQualityIssue] = []

    sources = _extract_sources(payload)
    terms = _content_terms_without_sources(payload)

    if not sources:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Fonti mancanti: impossibile verificarne la coerenza.",
            payload,
            "Aggiungere fonti coerenti con il contenuto.",
        ))

    for source in sources:
        source_terms = set(_words(source))

        if terms and len(source_terms & terms) < 1:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Fonte non coerente con contenuto, card o riassunto.",
                source,
                "Usare una fonte collegata a sezione, tema o sottotema reali.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_031_no_ugly_sources(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_031_card_riassunto_fonti_niente_fonti_brutte"
    title = "Niente fonti brutte"
    issues: List[CardQualityIssue] = []

    sources = _extract_sources(payload)

    if not sources:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Fonti mancanti.",
            payload,
            "Aggiungere fonti leggibili, non tecniche e non grezze.",
        ))

    for source in sources:
        if _contains_ugly_source(source):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Fonte brutta, tecnica, demo o grezza rilevata.",
                source,
                "Mostrare una fonte pulita, ad esempio: Fonte: sezione Sicurezza dei dati.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_032_graphic_layout_controlled(payload: Any) -> CardQualityMotorResult:
    motor_id = "qm_032_card_riassunto_fonti_layout_grafico_controllato"
    title = "Layout grafico controllato"
    issues: List[CardQualityIssue] = []

    cards = _extract_cards(payload)

    top_layout = {}
    if isinstance(payload, dict):
        value = payload.get("card_layout") or payload.get("layout_card") or payload.get("layout")
        if isinstance(value, dict):
            top_layout = value

    if not cards:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna card da controllare lato layout.",
            payload,
            "Aggiungere card con metadati layout controllati.",
        ))

    if not top_layout and not any(_card_layout(c) for c in cards):
        issues.append(_issue(
            motor_id,
            "blocking",
            "Metadati layout card mancanti.",
            payload,
            "Aggiungere metadati di layout controllati. Non è CSS: è controllo struttura dati.",
        ))

    for card in cards:
        layout = _card_layout(card)

        if not layout and not top_layout:
            continue

        effective = dict(top_layout)
        effective.update(layout)

        required_any = ["variant", "template", "style", "density", "icon"]
        if not any(k in effective and str(effective.get(k)).strip() for k in required_any):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Layout card non descrittivo.",
                effective,
                "Indicare almeno variante/template/stile/densità/icona.",
            ))

        title_value = _card_title(card)
        if not title_value:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Layout non controllabile perché manca il titolo card.",
                card,
                "Ogni card deve avere un titolo leggibile.",
            ))

    return CardQualityMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


CARD_SUMMARY_SOURCE_QUALITY_MOTORS: List[Callable[[Any], CardQualityMotorResult]] = [
    motor_023_cards_well_written,
    motor_024_cards_not_too_short,
    motor_025_cards_not_too_compressed,
    motor_026_key_message_complete,
    motor_027_summary_clear,
    motor_028_key_points_legible,
    motor_029_sources_visible_beautiful,
    motor_030_sources_coherent,
    motor_031_no_ugly_sources,
    motor_032_graphic_layout_controlled,
]


def analyze_card_summary_source_quality(payload: Any) -> CardQualityReport:
    results = [motor(payload) for motor in CARD_SUMMARY_SOURCE_QUALITY_MOTORS]

    total_issues = sum(len(r.issues) for r in results)
    blocking_issues = sum(1 for r in results for i in r.issues if i.severity == "blocking")
    warning_issues = sum(1 for r in results for i in r.issues if i.severity == "warning")
    failed_motors = sum(1 for r in results if r.status == "FAIL")
    passed_motors = len(results) - failed_motors
    approved = blocking_issues == 0

    return CardQualityReport(
        phase=PHASE,
        ready_label=READY_LABEL,
        approved=approved,
        status="PASS" if approved else "FAIL",
        total_motors=len(results),
        passed_motors=passed_motors,
        failed_motors=failed_motors,
        total_issues=total_issues,
        blocking_issues=blocking_issues,
        warning_issues=warning_issues,
        results=results,
    )


def report_to_dict(report: CardQualityReport) -> Dict[str, Any]:
    return asdict(report)


def registry_entry() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "version": VERSION,
        "ready_label": READY_LABEL,
        "total_motors": len(CARD_SUMMARY_SOURCE_QUALITY_MOTORS),
        "motors": [
            {
                "id": "qm_023_card_riassunto_fonti_card_scritte_bene",
                "title": "Card scritte bene",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_024_card_riassunto_fonti_card_non_troppo_corte",
                "title": "Card non troppo corte",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_025_card_riassunto_fonti_card_non_troppo_compresse",
                "title": "Card non troppo compresse",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_026_card_riassunto_fonti_messaggio_chiave_completo",
                "title": "Messaggio chiave completo",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_027_card_riassunto_fonti_riassunto_chiaro",
                "title": "Riassunto chiaro",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_028_card_riassunto_fonti_punti_chiave_leggibili",
                "title": "Punti chiave leggibili",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_029_card_riassunto_fonti_fonti_visibili_belle",
                "title": "Fonti visibili belle",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_030_card_riassunto_fonti_fonti_coerenti",
                "title": "Fonti coerenti",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_031_card_riassunto_fonti_niente_fonti_brutte",
                "title": "Niente fonti brutte",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_032_card_riassunto_fonti_layout_grafico_controllato",
                "title": "Layout grafico controllato",
                "type": "validator",
                "severity": "blocking",
            },
        ],
        "scope_guard": {
            "ui_pdf_css_app_touched": False,
            "pipeline_5_11_changed": False,
            "existing_33_motors_changed": False,
            "standalone_first": True,
            "no_fallback": True,
            "no_demo_output": True,
            "layout_check_is_data_structure_only": True,
        },
    }
