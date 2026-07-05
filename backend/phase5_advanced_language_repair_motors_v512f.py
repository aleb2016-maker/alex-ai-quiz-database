#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12F — ADVANCED LANGUAGE / REPAIR QUALITY MOTORS V1

Motori atomici ricostruiti:
61. Naturalezza linguistica anti-keyword
62. Accordo grammaticale e pronomi
63. Repair contestuale frasi non finite usando contesto/tema/sottotema/categorie
64. Repair ortografico parole con lettere invertite

Questo modulo NON modifica i 55 motori già collegati.
Questo modulo NON modifica la pipeline 5.11.
Questo modulo NON tocca UI/PDF/CSS/app.
Questo modulo controlla e suggerisce repair, ma non applica modifiche automatiche alla pipeline.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Callable, Dict, List, Optional


PHASE = "5.12F"
VERSION = "v1"
READY_LABEL = "ADVANCED_LANGUAGE_REPAIR_MOTORS_V512F_READY"


@dataclass
class AdvancedLanguageIssue:
    motor_id: str
    severity: str
    message: str
    excerpt: str
    suggestion: str = ""
    repaired_text: Optional[str] = None


@dataclass
class AdvancedLanguageMotorResult:
    motor_id: str
    title: str
    status: str
    issues: List[AdvancedLanguageIssue]


@dataclass
class AdvancedLanguageReport:
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
    results: List[AdvancedLanguageMotorResult]


COMMON_VERBS = {
    "è", "sono", "ha", "hanno", "serve", "permette", "consente", "aiuta",
    "spiega", "mostra", "riduce", "aumenta", "protegge", "collega",
    "descrive", "indica", "richiede", "controlla", "verifica", "usa",
    "migliora", "evita", "corregge", "seleziona", "genera", "produce",
}

ROBOTIC_PATTERNS = [
    r"\btema\s*:\s*[^.]+sottotema\s*:",
    r"\bcategoria\s*:\s*[^.]+sottocategoria\s*:",
    r"\bkeyword\s*:",
    r"\bparole\s+chiave\s*:",
    r"\b(lista|elenco)\s+(grezza|keyword|parole)",
    r"\bargomento\s*:\s*[^.]+concetto\s*:",
]

AGREEMENT_BAD_PATTERNS = [
    (
        r"\b(regola|procedura|funzione|categoria|sezione|card)\s+([a-zàèéìòù']+\s+){0,4}viene\s+presentato\b",
        "Accordo genere errato: soggetto femminile con participio maschile.",
        "Usare 'presentata' se il soggetto è femminile.",
    ),
    (
        r"\b(obiettivi|punti|contenuti|elementi|dati|risultati)\s+([a-zàèéìòù']+\s+){0,5}senza\s+copiarlo\b",
        "Pronome non coerente con un referente plurale.",
        "Usare 'copiarli' se il referente è plurale.",
    ),
    (
        r"\b(la|una)\s+[a-zàèéìòù']+\s+operativo\b",
        "Aggettivo maschile collegato a nome femminile.",
        "Usare accordo femminile, ad esempio 'operativa'.",
    ),
    (
        r"\b(il|un)\s+[a-zàèéìòù']+\s+operativa\b",
        "Aggettivo femminile collegato a nome maschile.",
        "Usare accordo maschile, ad esempio 'operativo'.",
    ),
    (
        r"\b(regole|procedure|categorie|sezioni)\s+([a-zàèéìòù']+\s+){0,4}sono\s+presentato\b",
        "Accordo plurale errato con participio singolare/maschile.",
        "Usare 'presentate' per soggetto femminile plurale.",
    ),
]

UNFINISHED_ENDINGS = {
    "di", "a", "da", "con", "per", "tra", "fra", "che", "del", "della",
    "dei", "degli", "delle", "nel", "nella", "nei", "nelle", "e", "o",
    "usando", "tramite", "attraverso", "senza", "verso", "sul", "sulla",
}

INVERTED_OR_BAD_WORDS = {
    "sotttotema": "sottotema",
    "sotottema": "sottotema",
    "sottotmea": "sottotema",
    "conrollare": "controllare",
    "controlalre": "controllare",
    "selezioa": "seleziona",
    "selezioan": "seleziona",
    "oricostruire": "o ricostruire",
    "ricotruire": "ricostruire",
    "qualita'": "qualità",
    "perche'": "perché",
    "puo'": "può",
    "piu'": "più",
    "gia'": "già",
}


def _clean_excerpt(value: Any, max_len: int = 180) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _issue(
    motor_id: str,
    severity: str,
    message: str,
    excerpt: Any,
    suggestion: str = "",
    repaired_text: Optional[str] = None,
) -> AdvancedLanguageIssue:
    return AdvancedLanguageIssue(
        motor_id=motor_id,
        severity=severity,
        message=message,
        excerpt=_clean_excerpt(excerpt),
        suggestion=suggestion,
        repaired_text=repaired_text,
    )


def _norm(value: Any) -> str:
    text = str(value or "").lower()
    text = text.replace("à", "a").replace("è", "e").replace("é", "e")
    text = text.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    text = re.sub(r"[^a-z0-9']+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _word_count(value: Any) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", str(value or "")))


def _sentences(text: str) -> List[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", str(text or "").strip()) if s.strip()]


def _collect_text_values(payload: Any) -> List[str]:
    out: List[str] = []

    def walk(x: Any, key: str = "") -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                lk = str(k).lower()
                if lk in {"context", "metadata", "layout", "source_report", "report_files"}:
                    continue
                walk(v, lk)
        elif isinstance(x, list):
            for item in x:
                walk(item, key)
        elif x is not None:
            value = str(x).strip()
            if value:
                out.append(value)

    walk(payload)
    return out


def _payload_text(payload: Any) -> str:
    if isinstance(payload, dict):
        for key in ["text", "output", "content", "body", "summary", "riassunto"]:
            value = payload.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return "\n".join(_collect_text_values(payload)).strip()


def _context(payload: Any) -> Dict[str, Any]:
    if isinstance(payload, dict):
        ctx = payload.get("context")
        if isinstance(ctx, dict):
            return ctx
    return {}


def _context_terms(payload: Any) -> Dict[str, str]:
    ctx = _context(payload)

    def pick(*keys: str) -> str:
        for key in keys:
            value = ctx.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
            if isinstance(value, list) and value:
                return str(value[0]).strip()
        return ""

    return {
        "theme": pick("theme", "tema", "topic"),
        "subtheme": pick("subtheme", "sottotema", "subtopic"),
        "category": pick("category", "categoria"),
        "subcategory": pick("subcategory", "sottocategoria"),
    }


def _has_verb(text: str) -> bool:
    low = str(text or "").lower()
    tokens = set(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", low))
    if tokens & COMMON_VERBS:
        return True
    return bool(re.search(r"\b[a-zàèéìòù']+(are|ere|ire|ato|ata|ati|ate|ano|ono|iamo)\b", low))


def _looks_like_keyword_list(text: str) -> bool:
    t = str(text or "").strip()
    if not t:
        return False

    wc = _word_count(t)
    delimiter_count = len(re.findall(r"[,;|•\n]", t))
    sentence_count = len(_sentences(t))

    chunks = [c.strip() for c in re.split(r"[,;|•\n]+", t) if c.strip()]
    short_chunks = sum(1 for c in chunks if _word_count(c) <= 3)

    # Regola 1: lista breve/media con molte virgole e senza vero sviluppo discorsivo.
    if len(chunks) >= 6 and delimiter_count >= 5:
        if short_chunks / max(1, len(chunks)) >= 0.70:
            return True

    # Regola 2: molte parole isolate e pochissima struttura fraseologica.
    if wc <= 55 and delimiter_count >= 5 and sentence_count <= 2:
        if short_chunks >= 6:
            return True

    # Regola 3: elenco esplicito di keyword/parole chiave.
    low = t.lower()
    if re.search(r"\b(keyword|parole chiave|lista grezza|elenco grezzo)\b", low):
        if delimiter_count >= 2 or len(chunks) >= 4:
            return True

    # Regola 4: fallback più prudente, solo se manca del tutto un verbo riconoscibile.
    if wc <= 45 and delimiter_count >= 5 and sentence_count <= 2 and not _has_verb(t):
        return True

    return False


def _robotic_matches(text: str) -> List[str]:
    low = str(text or "").lower()
    hits = []
    for pattern in ROBOTIC_PATTERNS:
        if re.search(pattern, low):
            hits.append(pattern)
    return hits


def _repair_unfinished_sentence(sentence: str, payload: Any) -> str:
    base = str(sentence or "").strip()
    if not base:
        return base

    terms = _context_terms(payload)
    theme = terms["theme"] or "il tema principale"
    subtheme = terms["subtheme"] or terms["category"] or "il sottotema collegato"
    category = terms["category"] or theme
    subcategory = terms["subcategory"] or subtheme

    stripped = base.rstrip(" .,!?:;")
    last = _norm(stripped).split()[-1] if _norm(stripped).split() else ""

    completions = {
        "di": f"{stripped} {subtheme}, collegandolo al tema {theme}.",
        "a": f"{stripped} {subcategory}, mantenendo il collegamento con {category}.",
        "da": f"{stripped} {category}, usando il contesto disponibile.",
        "con": f"{stripped} {subtheme}, così il messaggio risulta completo.",
        "per": f"{stripped} spiegare {subtheme} in modo chiaro.",
        "che": f"{stripped} riguarda {subtheme} e resta coerente con {theme}.",
        "e": f"{stripped} completa il collegamento con {subtheme}.",
        "usando": f"{stripped} il tema {theme}, il sottotema {subtheme} e le categorie disponibili.",
        "tramite": f"{stripped} {subtheme}, senza lasciare la frase sospesa.",
        "senza": f"{stripped} perdere il riferimento a {theme}.",
    }

    return completions.get(last, f"{stripped}, mantenendo il riferimento a {theme} e {subtheme}.")


def _find_inverted_or_bad_words(text: str) -> Dict[str, str]:
    hits: Dict[str, str] = {}
    tokens = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", str(text or ""))
    for token in tokens:
        key = token.lower()
        if key in INVERTED_OR_BAD_WORDS:
            hits[token] = INVERTED_OR_BAD_WORDS[key]
    return hits


def _apply_word_repairs(text: str, repairs: Dict[str, str]) -> str:
    result = str(text or "")
    for wrong, right in repairs.items():
        result = re.sub(rf"\b{re.escape(wrong)}\b", right, result, flags=re.IGNORECASE)
    return result


def motor_061_naturalness_anti_keyword(payload: Any) -> AdvancedLanguageMotorResult:
    motor_id = "qm_061_naturalezza_linguistica_naturalezza_linguistica_anti_keyword"
    title = "Naturalezza linguistica anti-keyword"
    issues: List[AdvancedLanguageIssue] = []

    texts = [t for t in _collect_text_values(payload) if _word_count(t) >= 4]
    if not texts:
        issues.append(_issue(motor_id, "blocking", "Nessun testo da controllare.", payload))

    for text in texts:
        if _looks_like_keyword_list(text):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Testo simile a lista grezza di keyword, non a frase naturale.",
                text,
                "Trasformare le parole chiave in frasi complete con valore didattico.",
            ))

        robotic = _robotic_matches(text)
        if robotic:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Testo costruito in modo meccanico o robotico.",
                text,
                "Riscrivere il contenuto come spiegazione naturale, non come schema grezzo.",
            ))

    return AdvancedLanguageMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_062_agreement_and_pronouns(payload: Any) -> AdvancedLanguageMotorResult:
    motor_id = "qm_062_accordo_grammaticale_accordo_grammaticale_e_pronomi"
    title = "Accordo grammaticale e pronomi"
    issues: List[AdvancedLanguageIssue] = []

    text = _payload_text(payload)
    if not text:
        issues.append(_issue(motor_id, "blocking", "Nessun testo da controllare.", payload))

    for pattern, message, suggestion in AGREEMENT_BAD_PATTERNS:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            issues.append(_issue(
                motor_id,
                "blocking",
                message,
                match.group(0),
                suggestion,
            ))

    return AdvancedLanguageMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_063_contextual_unfinished_sentence_repair(payload: Any) -> AdvancedLanguageMotorResult:
    motor_id = "qm_063_repair_contestuale_correzione_frasi_non_finite_usando_contesto_tema_sottotema_categorie_e_"
    title = "Repair contestuale frasi non finite con tema/sottotema/categorie"
    issues: List[AdvancedLanguageIssue] = []

    text = _payload_text(payload)
    if not text:
        issues.append(_issue(motor_id, "blocking", "Nessun testo da controllare.", payload))
        return AdvancedLanguageMotorResult(motor_id, title, "FAIL", issues)

    ctx_terms = _context_terms(payload)
    has_context = any(ctx_terms.values())

    for sentence in _sentences(text) or [text]:
        stripped = sentence.strip().rstrip(" .,!?:;")
        words = _norm(stripped).split()
        if not words:
            continue

        last = words[-1]
        if last in UNFINISHED_ENDINGS:
            repaired = _repair_unfinished_sentence(sentence, payload) if has_context else None
            issues.append(_issue(
                motor_id,
                "blocking",
                "Frase non finita rilevata.",
                sentence,
                "Completare la frase usando tema, sottotema, categoria e sottocategoria.",
                repaired_text=repaired,
            ))

    return AdvancedLanguageMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_064_orthographic_inverted_letters_repair(payload: Any) -> AdvancedLanguageMotorResult:
    motor_id = "qm_064_repair_ortografico_correzione_parole_con_lettere_invertite"
    title = "Repair ortografico parole con lettere invertite"
    issues: List[AdvancedLanguageIssue] = []

    text = _payload_text(payload)
    if not text:
        issues.append(_issue(motor_id, "blocking", "Nessun testo da controllare.", payload))
        return AdvancedLanguageMotorResult(motor_id, title, "FAIL", issues)

    repairs = _find_inverted_or_bad_words(text)
    if repairs:
        repaired = _apply_word_repairs(text, repairs)
        issues.append(_issue(
            motor_id,
            "blocking",
            "Parole scritte male o con lettere invertite rilevate.",
            repairs,
            "Applicare le correzioni ortografiche suggerite.",
            repaired_text=repaired,
        ))

    return AdvancedLanguageMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


ADVANCED_LANGUAGE_REPAIR_MOTORS: List[Callable[[Any], AdvancedLanguageMotorResult]] = [
    motor_061_naturalness_anti_keyword,
    motor_062_agreement_and_pronouns,
    motor_063_contextual_unfinished_sentence_repair,
    motor_064_orthographic_inverted_letters_repair,
]


def analyze_advanced_language_repair_quality(payload: Any) -> AdvancedLanguageReport:
    results = [motor(payload) for motor in ADVANCED_LANGUAGE_REPAIR_MOTORS]

    total_issues = sum(len(r.issues) for r in results)
    blocking_issues = sum(1 for r in results for i in r.issues if i.severity == "blocking")
    warning_issues = sum(1 for r in results for i in r.issues if i.severity == "warning")
    failed_motors = sum(1 for r in results if r.status == "FAIL")
    passed_motors = len(results) - failed_motors
    approved = blocking_issues == 0

    return AdvancedLanguageReport(
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


def report_to_dict(report: AdvancedLanguageReport) -> Dict[str, Any]:
    return asdict(report)


def registry_entry() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "version": VERSION,
        "ready_label": READY_LABEL,
        "total_motors": len(ADVANCED_LANGUAGE_REPAIR_MOTORS),
        "motors": [
            {
                "id": "qm_061_naturalezza_linguistica_naturalezza_linguistica_anti_keyword",
                "title": "Naturalezza linguistica anti-keyword",
                "type": "validator_repair_suggester",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
            {
                "id": "qm_062_accordo_grammaticale_accordo_grammaticale_e_pronomi",
                "title": "Accordo grammaticale e pronomi",
                "type": "validator",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
            {
                "id": "qm_063_repair_contestuale_correzione_frasi_non_finite_usando_contesto_tema_sottotema_categorie_e_",
                "title": "Repair contestuale frasi non finite usando contesto tema sottotema categorie e sottocategorie",
                "type": "validator_repair_suggester",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
            {
                "id": "qm_064_repair_ortografico_correzione_parole_con_lettere_invertite",
                "title": "Repair ortografico parole con lettere invertite",
                "type": "validator_repair_suggester",
                "severity": "blocking",
                "areas": ["card", "summary", "study_questions", "test_quiz", "general_text"],
            },
        ],
        "scope_guard": {
            "ui_pdf_css_app_touched": False,
            "pipeline_5_11_changed": False,
            "existing_55_motors_changed": False,
            "standalone_first": True,
            "no_fallback": True,
            "no_demo_output": True,
            "repair_suggestions_only": True,
        },
    }
