#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12C — DIDACTIC QUALITY MOTORS V1

Motori atomici ricostruiti:
13. Domande studio naturali
14. Domande studio utili per ripassare
15. Risposte guida specifiche
16. Spiegazioni test chiare
17. Spiegazioni non troppo corte
18. Tono didattico finale
19. Categorie presenti
20. Sottocategorie presenti
21. Coerenza tra domanda, risposta e contenuto
22. Niente risposte vaghe

Questo modulo NON modifica i 23 motori già collegati.
Questo modulo NON modifica la pipeline 5.11.
Questo modulo NON tocca UI/PDF/CSS/app.
Questo modulo è standalone, universale e testabile.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Callable, Optional, Set


PHASE = "5.12C"
VERSION = "v1"
READY_LABEL = "DIDACTIC_QUALITY_MOTORS_V512C_READY"


@dataclass
class DidacticQualityIssue:
    motor_id: str
    severity: str
    message: str
    excerpt: str
    suggestion: str = ""


@dataclass
class DidacticMotorResult:
    motor_id: str
    title: str
    status: str
    issues: List[DidacticQualityIssue]


@dataclass
class DidacticQualityReport:
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
    results: List[DidacticMotorResult]


STOPWORDS = {
    "il", "lo", "la", "i", "gli", "le", "un", "una", "uno",
    "di", "a", "da", "in", "con", "su", "per", "tra", "fra",
    "e", "o", "che", "del", "della", "dei", "degli", "delle",
    "nel", "nella", "nei", "nelle", "questo", "questa", "questi",
    "queste", "come", "cosa", "quale", "quali", "perche", "perché",
    "quando", "dove", "puo", "può", "sono", "essere", "viene",
    "serve", "spiega", "indica", "descrivi", "risposta", "domanda",
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
]


VAGUE_ANSWER_PHRASES = [
    "dipende",
    "è importante",
    "serve a capire",
    "aiuta molto",
    "varie cose",
    "diversi aspetti",
    "elementi importanti",
    "concetti principali",
    "si parla di",
    "riguarda il tema",
    "è utile",
    "punto centrale",
    "informazioni principali",
]


BAD_TONE_PHRASES = [
    "boh",
    "ovvio",
    "facile",
    "basta leggere",
    "come già detto",
    "non serve spiegare",
    "questa è semplice",
    "risposta banale",
]


def _clean_excerpt(text: Any, max_len: int = 140) -> str:
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
) -> DidacticQualityIssue:
    return DidacticQualityIssue(
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


def _content_terms(payload: Any) -> Set[str]:
    texts = _collect_text_values(payload)
    words: Set[str] = set()
    for t in texts:
        words.update(_words(t))
    return words


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


def _extract_study_questions(payload: Any) -> List[Dict[str, str]]:
    """
    Estrae solo domande studio.
    Non deve confondere le domande quiz/test con domande studio.
    Regola:
    - accetta dict con question/domanda + answer/guide_answer/risposta_guida
    - accetta chiavi esplicite study_question/domanda_studio
    - ignora dict che hanno options/opzioni/correct_answer/explanation, perché sono quiz/test
    """
    questions: List[Dict[str, str]] = []

    def scan(x: Any, context: str = "") -> None:
        if isinstance(x, dict):
            lower_keys = {str(k).lower(): k for k in x.keys()}

            quiz_like_keys = {
                "options",
                "opzioni",
                "answers",
                "risposte",
                "correct_answer",
                "risposta_corretta",
                "correct",
                "explanation",
                "spiegazione",
                "feedback",
            }

            is_quiz_like = any(k in lower_keys for k in quiz_like_keys)

            q_key = None
            a_key = None
            explicit_study_question = False

            for key in lower_keys:
                if key in {"study_question", "domanda_studio"}:
                    q_key = lower_keys[key]
                    explicit_study_question = True
                elif key in {"question", "domanda"}:
                    q_key = lower_keys[key]

                if key in {"answer", "risposta", "guide_answer", "risposta_guida"}:
                    a_key = lower_keys[key]

            # Se è un item quiz/test, non va contato come domanda studio.
            if q_key and not is_quiz_like and (a_key or explicit_study_question or context == "study"):
                questions.append({
                    "question": str(x.get(q_key, "")).strip(),
                    "answer": str(x.get(a_key, "")).strip() if a_key else "",
                })

            for k, v in x.items():
                key = str(k).lower()
                next_context = context
                if key in {"study_questions", "domande_studio", "study", "studio"}:
                    next_context = "study"
                elif key in {"quiz", "test", "questions", "domande"} and is_quiz_like:
                    next_context = "quiz"

                scan(v, next_context)

        elif isinstance(x, list):
            for item in x:
                scan(item, context)

        elif isinstance(x, str) and context == "study":
            for line in x.splitlines():
                line = line.strip()
                if "?" in line and len(line) >= 8:
                    questions.append({"question": line, "answer": ""})

    scan(payload)

    seen = set()
    clean: List[Dict[str, str]] = []
    for q in questions:
        key = _norm(q.get("question", ""))
        if key and key not in seen:
            seen.add(key)
            clean.append(q)

    return clean


def _extract_quiz_items(payload: Any) -> List[Dict[str, Any]]:
    items: List[Dict[str, Any]] = []

    def scan(x: Any) -> None:
        if isinstance(x, dict):
            lower_keys = {str(k).lower(): k for k in x.keys()}
            q_key = None
            exp_key = None
            opt_key = None
            correct_key = None

            for key in lower_keys:
                if key in {"question", "domanda", "quiz_question"}:
                    q_key = lower_keys[key]
                if key in {"explanation", "spiegazione", "feedback"}:
                    exp_key = lower_keys[key]
                if key in {"options", "opzioni", "answers", "risposte"}:
                    opt_key = lower_keys[key]
                if key in {"correct_answer", "risposta_corretta", "correct"}:
                    correct_key = lower_keys[key]

            if q_key and (exp_key or opt_key or correct_key):
                items.append({
                    "question": str(x.get(q_key, "")).strip(),
                    "explanation": str(x.get(exp_key, "")).strip() if exp_key else "",
                    "options": x.get(opt_key, []) if opt_key else [],
                    "correct_answer": str(x.get(correct_key, "")).strip() if correct_key else "",
                })

            for v in x.values():
                scan(v)

        elif isinstance(x, list):
            for item in x:
                scan(item)

    scan(payload)
    return items


def _extract_categories(payload: Any) -> List[str]:
    found: List[str] = []

    def scan(x: Any) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                key = str(k).lower()
                if key in {"category", "categoria", "categories", "categorie"}:
                    if isinstance(v, list):
                        found.extend([str(i).strip() for i in v if str(i).strip()])
                    else:
                        found.append(str(v).strip())
                scan(v)
        elif isinstance(x, list):
            for item in x:
                scan(item)

    scan(payload)
    return sorted(set([x for x in found if x]))


def _extract_subcategories(payload: Any) -> List[str]:
    found: List[str] = []

    def scan(x: Any) -> None:
        if isinstance(x, dict):
            for k, v in x.items():
                key = str(k).lower()
                if key in {"subcategory", "sottocategoria", "subcategories", "sottocategorie"}:
                    if isinstance(v, list):
                        found.extend([str(i).strip() for i in v if str(i).strip()])
                    else:
                        found.append(str(v).strip())
                scan(v)
        elif isinstance(x, list):
            for item in x:
                scan(item)

    scan(payload)
    return sorted(set([x for x in found if x]))


def _contains_generic(text: str) -> bool:
    low = _norm(text)
    return any(_norm(p) in low for p in GENERIC_PHRASES)


def _word_count(text: Any) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", str(text or "")))


def _overlap_score(a: Any, b: Any) -> int:
    return len(set(_words(a)) & set(_words(b)))


def _question_is_natural(question: str) -> bool:
    q = question.strip()
    low = _norm(q)

    if not q.endswith("?"):
        return False

    if _word_count(q) < 6:
        return False

    bad_starts = [
        "domanda",
        "documento analizzato",
        "contenuto generato",
        "cosa dice il testo",
        "di cosa parla",
        "qual e il punto centrale",
    ]

    if any(low.startswith(_norm(x)) for x in bad_starts):
        return False

    natural_starts = [
        "perche",
        "perché",
        "come",
        "quale",
        "quali",
        "in che modo",
        "quando",
        "che cosa",
        "cosa",
        "descrivi",
        "spiega",
        "confronta",
    ]

    return any(low.startswith(_norm(x)) for x in natural_starts)


def motor_013_study_questions_natural(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_013_qualita_didattica_domande_studio_naturali"
    title = "Domande studio naturali"
    issues: List[DidacticQualityIssue] = []

    questions = _extract_study_questions(payload)

    if not questions:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna domanda studio rilevata.",
            payload,
            "Generare domande studio esplicite e naturali.",
        ))
    else:
        for item in questions:
            q = item.get("question", "")
            if not _question_is_natural(q):
                issues.append(_issue(
                    motor_id,
                    "blocking",
                    "Domanda studio poco naturale o formulata in modo meccanico.",
                    q,
                    "Usare una domanda naturale, completa e utile per lo studio.",
                ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_014_study_questions_useful(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_014_qualita_didattica_domande_studio_utili_per_ripassare"
    title = "Domande studio utili per ripassare"
    issues: List[DidacticQualityIssue] = []

    questions = _extract_study_questions(payload)
    terms = _content_terms(payload)

    useful_verbs = [
        "perche", "perché", "come", "spiega", "descrivi", "confronta",
        "quale", "quali", "in che modo", "a cosa serve", "che ruolo",
    ]

    for item in questions:
        q = item.get("question", "")
        low = _norm(q)

        if not any(_norm(v) in low for v in useful_verbs):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Domanda poco utile al ripasso: non chiede relazione, funzione, causa o spiegazione.",
                q,
                "Riformulare chiedendo perché, come, funzione, confronto o conseguenza.",
            ))

        q_terms = set(_words(q))
        if terms and len(q_terms & terms) < 2:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Domanda poco collegata al contenuto reale.",
                q,
                "Inserire concetti specifici del contenuto.",
            ))

        if re.match(r"^\s*(è vero che|vero o falso|sì o no|si o no)\b", q, re.IGNORECASE):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Domanda troppo chiusa o povera per il ripasso.",
                q,
                "Preferire domande aperte e ragionate.",
            ))

    if not questions:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna domanda studio utile rilevata.",
            payload,
            "Aggiungere domande studio utili per ripassare.",
        ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_015_specific_guide_answers(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_015_qualita_didattica_risposte_guida_specifiche"
    title = "Risposte guida specifiche"
    issues: List[DidacticQualityIssue] = []

    questions = _extract_study_questions(payload)
    blob = _payload_blob(payload)

    for item in questions:
        answer = item.get("answer", "")

        if not answer:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Domanda studio senza risposta guida.",
                item.get("question", ""),
                "Aggiungere una risposta guida specifica.",
            ))
            continue

        if _word_count(answer) < 12:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta guida troppo corta per essere specifica.",
                answer,
                "Espandere con concetti, funzione e contesto.",
            ))

        if _contains_generic(answer):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta guida generica.",
                answer,
                "Sostituire formule generiche con dettagli del contenuto.",
            ))

        if _overlap_score(answer, blob) < 3:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta guida poco collegata al contenuto.",
                answer,
                "Usare termini e relazioni presenti nel contenuto reale.",
            ))

    if not questions:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna risposta guida rilevata.",
            payload,
            "Aggiungere risposte guida collegate alle domande studio.",
        ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_016_clear_test_explanations(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_016_qualita_didattica_spiegazioni_test_chiare"
    title = "Spiegazioni test chiare"
    issues: List[DidacticQualityIssue] = []

    quiz_items = _extract_quiz_items(payload)

    if not quiz_items:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessun item test/quiz con spiegazione rilevato.",
            payload,
            "Aggiungere spiegazioni test chiare quando è presente un test.",
        ))

    for item in quiz_items:
        explanation = item.get("explanation", "")
        correct = item.get("correct_answer", "")

        if not explanation:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Spiegazione test mancante.",
                item.get("question", ""),
                "Aggiungere una spiegazione che motivi la risposta corretta.",
            ))
            continue

        low = _norm(explanation)
        clarity_markers = ["perche", "perché", "infatti", "poiche", "poiché", "quindi", "significa"]

        if not any(_norm(x) in low for x in clarity_markers):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Spiegazione poco chiara: manca una motivazione esplicita.",
                explanation,
                "Spiegare perché la risposta è corretta.",
            ))

        if correct and _overlap_score(explanation, correct) < 1:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Spiegazione non collegata alla risposta corretta.",
                explanation,
                "Collegare la spiegazione alla risposta corretta.",
            ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_017_explanations_not_too_short(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_017_qualita_didattica_spiegazioni_non_troppo_corte"
    title = "Spiegazioni non troppo corte"
    issues: List[DidacticQualityIssue] = []

    quiz_items = _extract_quiz_items(payload)

    if not quiz_items:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna spiegazione test da valutare.",
            payload,
            "Aggiungere spiegazioni test non troppo corte.",
        ))

    for item in quiz_items:
        explanation = item.get("explanation", "")
        if _word_count(explanation) < 10:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Spiegazione troppo corta.",
                explanation or item.get("question", ""),
                "Scrivere almeno una spiegazione completa con motivazione.",
            ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_018_didactic_tone(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_018_qualita_didattica_tono_didattico_finale"
    title = "Tono didattico finale"
    issues: List[DidacticQualityIssue] = []

    blob = _payload_blob(payload)
    low = _norm(blob)

    for phrase in BAD_TONE_PHRASES:
        if _norm(phrase) in low:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Tono non didattico o troppo colloquiale.",
                phrase,
                "Usare un tono chiaro, neutro e formativo.",
            ))

    didactic_markers = [
        "perche", "perché", "serve", "permette", "aiuta", "significa",
        "in questo modo", "ad esempio", "la risposta", "il concetto",
        "ripasso", "studio", "spiega",
    ]

    if not any(_norm(x) in low for x in didactic_markers):
        issues.append(_issue(
            motor_id,
            "blocking",
            "Tono didattico non riconoscibile.",
            blob,
            "Aggiungere spiegazioni formative e orientate al ripasso.",
        ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_019_categories_present(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_019_qualita_didattica_categorie_presenti"
    title = "Categorie presenti"
    issues: List[DidacticQualityIssue] = []

    categories = _extract_categories(payload)

    if not categories:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Categorie mancanti.",
            payload,
            "Aggiungere una categoria didattica per organizzare l'output.",
        ))

    for cat in categories:
        if _word_count(cat) < 1 or _contains_generic(cat):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Categoria generica o non leggibile.",
                cat,
                "Usare una categoria specifica e leggibile.",
            ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_020_subcategories_present(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_020_qualita_didattica_sottocategorie_presenti"
    title = "Sottocategorie presenti"
    issues: List[DidacticQualityIssue] = []

    subcategories = _extract_subcategories(payload)

    if not subcategories:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Sottocategorie mancanti.",
            payload,
            "Aggiungere sottocategorie utili per tema, sottotema o funzione.",
        ))

    for sub in subcategories:
        if _word_count(sub) < 1 or _contains_generic(sub):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Sottocategoria generica o non leggibile.",
                sub,
                "Usare una sottocategoria specifica.",
            ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


def motor_021_question_answer_content_coherence(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_021_qualita_didattica_coerenza_tra_domanda_risposta_e_contenuto"
    title = "Coerenza tra domanda risposta e contenuto"
    issues: List[DidacticQualityIssue] = []

    blob = _payload_blob(payload)
    questions = _extract_study_questions(payload)
    quiz_items = _extract_quiz_items(payload)

    for item in questions:
        q = item.get("question", "")
        a = item.get("answer", "")

        if a and _overlap_score(q, a) < 1:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Domanda e risposta guida sembrano non coerenti.",
                q + " / " + a,
                "Allineare risposta e domanda sullo stesso concetto.",
            ))

        if a and _overlap_score(a, blob) < 3:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta guida poco coerente con il contenuto complessivo.",
                a,
                "Usare concetti presenti nel contenuto reale.",
            ))

    for item in quiz_items:
        q = item.get("question", "")
        correct = item.get("correct_answer", "")
        explanation = item.get("explanation", "")

        if correct and explanation and _overlap_score(correct, explanation) < 1:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta corretta e spiegazione non sono coerenti.",
                correct + " / " + explanation,
                "Collegare spiegazione e risposta corretta.",
            ))

        if q and correct and _overlap_score(q, correct) < 1:
            issues.append(_issue(
                motor_id,
                "warning",
                "Domanda e risposta corretta hanno pochi termini in comune.",
                q + " / " + correct,
                "Verificare manualmente la coerenza semantica.",
            ))

    if not questions and not quiz_items:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna coppia domanda-risposta da controllare.",
            payload,
            "Aggiungere domande con risposte o quiz con spiegazioni.",
        ))

    status = "PASS" if not any(i.severity == "blocking" for i in issues) else "FAIL"
    return DidacticMotorResult(motor_id, title, status, issues)


def motor_022_no_vague_answers(payload: Any) -> DidacticMotorResult:
    motor_id = "qm_022_qualita_didattica_niente_risposte_vaghe"
    title = "Niente risposte vaghe"
    issues: List[DidacticQualityIssue] = []

    answers: List[str] = []

    for item in _extract_study_questions(payload):
        if item.get("answer"):
            answers.append(item["answer"])

    for item in _extract_quiz_items(payload):
        if item.get("explanation"):
            answers.append(item["explanation"])

    if not answers:
        issues.append(_issue(
            motor_id,
            "blocking",
            "Nessuna risposta o spiegazione da controllare.",
            payload,
            "Aggiungere risposte e spiegazioni specifiche.",
        ))

    for answer in answers:
        low = _norm(answer)

        for phrase in VAGUE_ANSWER_PHRASES:
            if _norm(phrase) in low:
                issues.append(_issue(
                    motor_id,
                    "blocking",
                    "Risposta vaga o poco informativa.",
                    answer,
                    "Sostituire formule vaghe con dettagli specifici.",
                ))
                break

        if _word_count(answer) < 8:
            issues.append(_issue(
                motor_id,
                "blocking",
                "Risposta troppo corta e probabilmente vaga.",
                answer,
                "Espandere con concetti specifici del contenuto.",
            ))

    return DidacticMotorResult(motor_id, title, "PASS" if not issues else "FAIL", issues)


DIDACTIC_QUALITY_MOTORS: List[Callable[[Any], DidacticMotorResult]] = [
    motor_013_study_questions_natural,
    motor_014_study_questions_useful,
    motor_015_specific_guide_answers,
    motor_016_clear_test_explanations,
    motor_017_explanations_not_too_short,
    motor_018_didactic_tone,
    motor_019_categories_present,
    motor_020_subcategories_present,
    motor_021_question_answer_content_coherence,
    motor_022_no_vague_answers,
]


def analyze_didactic_quality(payload: Any) -> DidacticQualityReport:
    results = [motor(payload) for motor in DIDACTIC_QUALITY_MOTORS]

    total_issues = sum(len(r.issues) for r in results)
    blocking_issues = sum(1 for r in results for i in r.issues if i.severity == "blocking")
    warning_issues = sum(1 for r in results for i in r.issues if i.severity == "warning")
    failed_motors = sum(1 for r in results if r.status == "FAIL")
    passed_motors = len(results) - failed_motors
    approved = blocking_issues == 0

    return DidacticQualityReport(
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


def report_to_dict(report: DidacticQualityReport) -> Dict[str, Any]:
    return asdict(report)


def registry_entry() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "version": VERSION,
        "ready_label": READY_LABEL,
        "total_motors": len(DIDACTIC_QUALITY_MOTORS),
        "motors": [
            {
                "id": "qm_013_qualita_didattica_domande_studio_naturali",
                "title": "Domande studio naturali",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_014_qualita_didattica_domande_studio_utili_per_ripassare",
                "title": "Domande studio utili per ripassare",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_015_qualita_didattica_risposte_guida_specifiche",
                "title": "Risposte guida specifiche",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_016_qualita_didattica_spiegazioni_test_chiare",
                "title": "Spiegazioni test chiare",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_017_qualita_didattica_spiegazioni_non_troppo_corte",
                "title": "Spiegazioni non troppo corte",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_018_qualita_didattica_tono_didattico_finale",
                "title": "Tono didattico finale",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_019_qualita_didattica_categorie_presenti",
                "title": "Categorie presenti",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_020_qualita_didattica_sottocategorie_presenti",
                "title": "Sottocategorie presenti",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_021_qualita_didattica_coerenza_tra_domanda_risposta_e_contenuto",
                "title": "Coerenza tra domanda risposta e contenuto",
                "type": "validator",
                "severity": "blocking_warning",
            },
            {
                "id": "qm_022_qualita_didattica_niente_risposte_vaghe",
                "title": "Niente risposte vaghe",
                "type": "validator",
                "severity": "blocking",
            },
        ],
        "scope_guard": {
            "ui_pdf_css_app_touched": False,
            "pipeline_5_11_changed": False,
            "existing_23_motors_changed": False,
            "standalone_first": True,
            "no_fallback": True,
            "no_demo_output": True,
        },
    }
