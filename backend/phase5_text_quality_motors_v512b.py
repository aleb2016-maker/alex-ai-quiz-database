#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.12B — TEXT QUALITY MOTORS V1

Motori atomici ricostruiti:
1. Grammatica italiana corretta
2. Accenti corretti
3. Apostrofi corretti
4. Punteggiatura corretta
5. Spazi corretti prima/dopo punteggiatura
6. Frasi complete
7. Assenza di frasi spezzate
8. Assenza di frasi non terminate
9. Assenza di finali sospetti
10. Assenza di frasi riempitive
11. Assenza di testo generico
12. Assenza di vecchi fallback/demo/test

Questo modulo NON usa fallback.
Questo modulo NON contiene demo output.
Questo modulo NON dipende da UI/PDF/CSS.
Questo modulo è rule-based, universale e testabile.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Callable, Optional


PHASE = "5.12B"
VERSION = "v1"
READY_LABEL = "TEXT_QUALITY_MOTORS_V512B_READY"


@dataclass
class TextQualityIssue:
    motor_id: str
    severity: str
    message: str
    excerpt: str
    suggestion: str = ""


@dataclass
class TextQualityMotorResult:
    motor_id: str
    title: str
    status: str
    issues: List[TextQualityIssue]
    repaired_text: Optional[str] = None


@dataclass
class TextQualityReport:
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
    results: List[TextQualityMotorResult]
    repaired_text: str


def _clean_excerpt(text: str, max_len: int = 120) -> str:
    text = re.sub(r"\s+", " ", text or "").strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3] + "..."


def _split_sentences(text: str) -> List[str]:
    chunks = re.split(r"(?<=[.!?])\s+", text.strip())
    return [c.strip() for c in chunks if c.strip()]


def _split_lines(text: str) -> List[str]:
    return [x.rstrip() for x in text.splitlines()]


def _has_probable_verb(sentence: str) -> bool:
    """
    Euristica leggera, non parser grammaticale completo.
    Serve a intercettare frammenti palesemente non frasali.
    """
    low = sentence.lower()
    verb_patterns = [
        r"\bè\b", r"\bsono\b", r"\bsi\b", r"\bha\b", r"\bhanno\b",
        r"\bpuò\b", r"\bpossono\b", r"\bdeve\b", r"\bdevono\b",
        r"\bserve\b", r"\bservono\b", r"\bpermette\b", r"\bpermettono\b",
        r"\bspiega\b", r"\bdescrive\b", r"\bindica\b", r"\bmostra\b",
        r"\bcontiene\b", r"\binclude\b", r"\briguarda\b",
        r"\borganizza\b", r"\baiuta\b", r"\bprotegg(e|ono)\b",
        r"\bgestisce\b", r"\bcollega\b", r"\bverifica\b",
        r"\bcorregge\b", r"\bmigliora\b", r"\brende\b",
        r"\b[a-zàèéìòù]+(are|ere|ire)\b",
        r"\b[a-zàèéìòù]+(ato|ata|ati|ate|ito|ita|iti|ite|uto|uta|uti|ute)\b",
    ]
    return any(re.search(p, low, re.IGNORECASE) for p in verb_patterns)


def _issue(
    motor_id: str,
    severity: str,
    message: str,
    excerpt: str,
    suggestion: str = "",
) -> TextQualityIssue:
    return TextQualityIssue(
        motor_id=motor_id,
        severity=severity,
        message=message,
        excerpt=_clean_excerpt(excerpt),
        suggestion=suggestion,
    )


def motor_001_italian_grammar(text: str) -> TextQualityMotorResult:
    motor_id = "qm_001_qualita_testuale_grammatica_italiana_corretta"
    title = "Grammatica italiana corretta"
    issues: List[TextQualityIssue] = []

    suspicious_patterns = [
        (r"\bregola operativa viene presentato\b", "Accordo errato: “regola” è femminile.", "Regola operativa viene presentata"),
        (r"\bobiettivi principali senza copiarlo\b", "Pronome non coerente con il plurale.", "Obiettivi principali senza copiarli"),
        (r"\ble informazioni è\b", "Accordo soggetto-verbo errato.", "Le informazioni sono"),
        (r"\bi dati è\b", "Accordo soggetto-verbo errato.", "I dati sono"),
        (r"\bla dati\b", "Articolo non coerente con il nome.", "I dati"),
        (r"\bil informazioni\b", "Articolo non coerente con il nome.", "Le informazioni"),
        (r"\buna problema\b", "Articolo non coerente con il genere.", "Un problema"),
        (r"\bun azione\b", "Apostrofo/articolo femminile mancante.", "Un’azione"),
        (r"\bquesti informazione\b", "Dimostrativo non coerente con numero/genere.", "Queste informazioni"),
    ]

    for pattern, message, suggestion in suspicious_patterns:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            issues.append(_issue(motor_id, "blocking", message, m.group(0), suggestion))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_002_accents(text: str) -> TextQualityMotorResult:
    motor_id = "qm_002_qualita_testuale_accenti_corretti"
    title = "Accenti corretti"
    issues: List[TextQualityIssue] = []

    replacements = {
        r"\bperche\b": "perché",
        r"\bperchè\b": "perché",
        r"\bpuo\b": "può",
        r"\bpiu\b": "più",
        r"\bgia\b": "già",
        r"\bcioe\b": "cioè",
        r"\bcosi\b": "così",
        r"\bpero\b": "però",
        r"\bqual['’`´]e\b": "qual è",
        r"\bqual e\b": "qual è",
    }

    repaired = text

    for pattern, replacement in replacements.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Accento o forma grafica italiana non corretta.",
                m.group(0),
                replacement,
            ))
        repaired = re.sub(pattern, replacement, repaired, flags=re.IGNORECASE)

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues, repaired)


def motor_003_apostrophes(text: str) -> TextQualityMotorResult:
    motor_id = "qm_003_qualita_testuale_apostrofi_corretti"
    title = "Apostrofi corretti"
    issues: List[TextQualityIssue] = []

    replacements = {
        r"\bun informazione\b": "un’informazione",
        r"\bun idea\b": "un’idea",
        r"\bun azione\b": "un’azione",
        r"\bl utente\b": "l’utente",
        r"\bd accordo\b": "d’accordo",
        r"\bun['’`] altra\b": "un’altra",
        r"\bun['’`] informazione\b": "un’informazione",
    }

    repaired = text

    for pattern, replacement in replacements.items():
        for m in re.finditer(pattern, text, re.IGNORECASE):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Apostrofo mancante o forma elisa non corretta.",
                m.group(0),
                replacement,
            ))
        repaired = re.sub(pattern, replacement, repaired, flags=re.IGNORECASE)

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues, repaired)


def motor_004_punctuation(text: str) -> TextQualityMotorResult:
    motor_id = "qm_004_qualita_testuale_punteggiatura_corretta"
    title = "Punteggiatura corretta"
    issues: List[TextQualityIssue] = []

    checks = [
        (r"\.{3,}", "Puntini sospensivi eccessivi o non controllati.", "..."),
        (r",{2,}", "Virgole ripetute.", ","),
        (r";{2,}", "Punto e virgola ripetuto.", ";"),
        (r":{2,}", "Due punti ripetuti.", ":"),
        (r"[!?]{3,}", "Punteggiatura enfatica eccessiva.", "."),
        (r"\(\s*\)", "Parentesi vuote.", ""),
    ]

    for pattern, message, suggestion in checks:
        for m in re.finditer(pattern, text):
            issues.append(_issue(motor_id, "blocking", message, m.group(0), suggestion))

    stripped = text.strip()
    if stripped and not re.search(r"[.!?…»”\)]$", stripped):
        issues.append(_issue(
            motor_id,
            "blocking",
            "Il testo non termina con punteggiatura conclusiva.",
            stripped[-80:],
            "Chiudere con punto, punto interrogativo o punto esclamativo se appropriato.",
        ))

    if text.count("(") != text.count(")"):
        issues.append(_issue(
            motor_id,
            "blocking",
            "Parentesi non bilanciate.",
            text,
            "Bilanciare parentesi aperte e chiuse.",
        ))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_005_punctuation_spacing(text: str) -> TextQualityMotorResult:
    motor_id = "qm_005_qualita_testuale_spazi_corretti_prima_e_dopo_punteggiatura"
    title = "Spazi corretti prima e dopo punteggiatura"
    issues: List[TextQualityIssue] = []

    repaired = text

    before_punct = r"\s+([,.;:!?])"
    after_punct = r"([,.;:!?])(?=[^\s\]\)\}\"'»])"

    for m in re.finditer(before_punct, text):
        issues.append(_issue(
            motor_id,
            "blocking",
            "Spazio errato prima della punteggiatura.",
            m.group(0),
            m.group(1),
        ))

    for m in re.finditer(after_punct, text):
        # evita numeri decimali semplici tipo 3.5
        start = m.start()
        end = m.end()
        if start > 0 and end < len(text) and text[start - 1].isdigit() and text[end].isdigit():
            continue
        issues.append(_issue(
            motor_id,
            "blocking",
            "Spazio mancante dopo la punteggiatura.",
            text[m.start(): min(len(text), m.start() + 20)],
            m.group(1) + " ",
        ))

    repaired = re.sub(before_punct, r"\1", repaired)
    repaired = re.sub(r"([,.;:!?])(?=[A-Za-zÀ-ÖØ-öø-ÿ])", r"\1 ", repaired)

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues, repaired)


def motor_006_complete_sentences(text: str) -> TextQualityMotorResult:
    motor_id = "qm_006_qualita_testuale_frasi_complete"
    title = "Frasi complete"
    issues: List[TextQualityIssue] = []

    sentences = _split_sentences(text)

    for s in sentences:
        plain = re.sub(r"^[\-\*\d\.\)\s]+", "", s).strip()
        words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ']+", plain)

        if len(words) >= 5 and not _has_probable_verb(plain):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Possibile frase non completa: manca un verbo o una struttura frasale chiara.",
                plain,
                "Trasformare il frammento in una frase completa con soggetto e verbo.",
            ))

        if len(words) <= 2 and plain and not plain.endswith(":"):
            issues.append(_issue(
                motor_id,
                "warning",
                "Frammento molto corto: potrebbe non essere una frase completa.",
                plain,
                "Espandere il frammento se deve essere una frase autonoma.",
            ))

    status = "PASS" if not any(i.severity == "blocking" for i in issues) else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_007_broken_sentences(text: str) -> TextQualityMotorResult:
    motor_id = "qm_007_qualita_testuale_assenza_di_frasi_spezzate"
    title = "Assenza di frasi spezzate"
    issues: List[TextQualityIssue] = []

    lines = _split_lines(text)

    for i in range(len(lines) - 1):
        current = lines[i].strip()
        nxt = lines[i + 1].strip()

        if not current or not nxt:
            continue

        current_is_bullet = bool(re.match(r"^[-*•\d]+[.)]?\s+", current))
        next_is_bullet = bool(re.match(r"^[-*•\d]+[.)]?\s+", nxt))

        if current_is_bullet or next_is_bullet:
            continue

        if not re.search(r"[.!?:;]$", current) and re.match(r"^[a-zàèéìòù]", nxt):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Possibile frase spezzata da un ritorno a capo non necessario.",
                current + " / " + nxt,
                "Unire le due righe o chiudere correttamente la frase.",
            ))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_008_unfinished_sentences(text: str) -> TextQualityMotorResult:
    motor_id = "qm_008_qualita_testuale_assenza_di_frasi_non_terminate"
    title = "Assenza di frasi non terminate"
    issues: List[TextQualityIssue] = []

    lines = [l.strip() for l in _split_lines(text) if l.strip()]
    suspicious_tail = r"\b(e|di|con|per|che|del|della|dello|dei|degli|delle|un|una|il|la|lo|gli|le|a|da|in|su|tra|fra)$"

    for line in lines:
        low = line.lower().strip(" .,!?:;")
        if re.search(suspicious_tail, low):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Frase probabilmente non terminata.",
                line,
                "Completare la frase usando il contesto, il tema e il sottotema.",
            ))

    stripped = text.strip()
    if stripped and not re.search(r"[.!?…»”\)]$", stripped):
        issues.append(_issue(
            motor_id,
            "blocking",
            "Output finale non chiuso da punteggiatura conclusiva.",
            stripped[-100:],
            "Completare o chiudere la frase finale.",
        ))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_009_suspicious_endings(text: str) -> TextQualityMotorResult:
    motor_id = "qm_009_qualita_testuale_assenza_di_finali_sospetti"
    title = "Assenza di finali sospetti"
    issues: List[TextQualityIssue] = []

    suspicious_words = ["e", "di", "con", "per", "che", "del", "della"]
    pattern = r"\b(" + "|".join(map(re.escape, suspicious_words)) + r")\s*([.!?])?$"

    for sentence in _split_sentences(text):
        low = sentence.lower().strip()
        low = re.sub(r"[.!?]+$", "", low).strip()
        if re.search(pattern, low):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Finale sospetto: la frase finisce con connettivo, preposizione o articolo.",
                sentence,
                "Completare la frase con il contenuto mancante.",
            ))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_010_filler_sentences(text: str) -> TextQualityMotorResult:
    motor_id = "qm_010_qualita_testuale_assenza_di_frasi_riempitive"
    title = "Assenza di frasi riempitive"
    issues: List[TextQualityIssue] = []

    fillers = [
        r"\bin questo documento viene (presentato|spiegato|analizzato)\b",
        r"\bè importante sottolineare\b",
        r"\bcome abbiamo visto\b",
        r"\bin conclusione possiamo dire\b",
        r"\bquesto contenuto è utile\b",
        r"\bil tema è molto importante\b",
        r"\bsi parla di vari aspetti\b",
        r"\bdiversi elementi importanti\b",
    ]

    for pattern in fillers:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Frase riempitiva o poco informativa.",
                m.group(0),
                "Sostituire con un'informazione specifica tratta dal contenuto.",
            ))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_011_generic_text(text: str) -> TextQualityMotorResult:
    motor_id = "qm_011_qualita_testuale_assenza_di_testo_generico"
    title = "Assenza di testo generico"
    issues: List[TextQualityIssue] = []

    generic_phrases = [
        "documento analizzato",
        "contenuti generati",
        "punto centrale",
        "testo fornito",
        "informazioni principali",
        "contenuto principale",
        "argomento trattato",
        "elementi importanti",
        "sezione generica",
        "output prodotto",
    ]

    for phrase in generic_phrases:
        for m in re.finditer(re.escape(phrase), text, re.IGNORECASE):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Testo generico non accettabile nell'output finale.",
                m.group(0),
                "Usare una formulazione specifica collegata al contenuto reale.",
            ))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


def motor_012_fallback_demo_contamination(text: str) -> TextQualityMotorResult:
    motor_id = "qm_012_qualita_testuale_assenza_di_vecchi_fallback_demo_test"
    title = "Assenza di vecchi fallback demo test"
    issues: List[TextQualityIssue] = []

    contamination = [
        r"\bfallback\b",
        r"\bdemo\b",
        r"\bplaceholder\b",
        r"\btodo\b",
        r"\blorem ipsum\b",
        r"\btesto di esempio\b",
        r"\bsicurezza informatica aziendale\b",
        r"\bknowledge_base_json\b",
        r"\bmock\b",
        r"\bstub\b",
    ]

    for pattern in contamination:
        for m in re.finditer(pattern, text, re.IGNORECASE):
            issues.append(_issue(
                motor_id,
                "blocking",
                "Contaminazione vecchia/demo/fallback rilevata.",
                m.group(0),
                "Rimuovere la contaminazione e usare solo contenuto reale dell'input.",
            ))

    status = "PASS" if not issues else "FAIL"
    return TextQualityMotorResult(motor_id, title, status, issues)


TEXT_QUALITY_MOTORS: List[Callable[[str], TextQualityMotorResult]] = [
    motor_001_italian_grammar,
    motor_002_accents,
    motor_003_apostrophes,
    motor_004_punctuation,
    motor_005_punctuation_spacing,
    motor_006_complete_sentences,
    motor_007_broken_sentences,
    motor_008_unfinished_sentences,
    motor_009_suspicious_endings,
    motor_010_filler_sentences,
    motor_011_generic_text,
    motor_012_fallback_demo_contamination,
]


def apply_safe_text_repairs(text: str) -> str:
    """
    Riparazioni sicure e deterministiche:
    - accenti noti
    - apostrofi noti
    - spazi prima/dopo punteggiatura

    Non riscrive contenuto semantico.
    Non inventa frasi.
    Non completa frasi usando fantasia.
    """
    repaired = text

    for motor in [
        motor_002_accents,
        motor_003_apostrophes,
        motor_005_punctuation_spacing,
    ]:
        result = motor(repaired)
        if result.repaired_text is not None:
            repaired = result.repaired_text

    repaired = re.sub(r"[ \t]{2,}", " ", repaired)
    repaired = re.sub(r"\n{3,}", "\n\n", repaired)
    return repaired.strip()


def analyze_text_quality(text: str, apply_repairs: bool = True) -> TextQualityReport:
    working_text = text or ""
    repaired_text = apply_safe_text_repairs(working_text) if apply_repairs else working_text

    results: List[TextQualityMotorResult] = []

    # Analizza il testo riparato per evitare che errori banali di accento/spazio falsino tutti gli altri controlli.
    # I motori accenti/apostrofi/spazi vengono comunque eseguiti sul testo originale per rilevare l'errore.
    for motor in TEXT_QUALITY_MOTORS:
        if motor in [motor_002_accents, motor_003_apostrophes, motor_005_punctuation_spacing]:
            result = motor(working_text)
        else:
            result = motor(repaired_text)
        results.append(result)

    total_issues = sum(len(r.issues) for r in results)
    blocking_issues = sum(1 for r in results for i in r.issues if i.severity == "blocking")
    warning_issues = sum(1 for r in results for i in r.issues if i.severity == "warning")
    failed_motors = sum(1 for r in results if r.status == "FAIL")
    passed_motors = len(results) - failed_motors
    approved = blocking_issues == 0

    return TextQualityReport(
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
        repaired_text=repaired_text,
    )


def report_to_dict(report: TextQualityReport) -> Dict[str, Any]:
    return asdict(report)


def registry_entry() -> Dict[str, Any]:
    return {
        "phase": PHASE,
        "version": VERSION,
        "ready_label": READY_LABEL,
        "total_motors": len(TEXT_QUALITY_MOTORS),
        "motors": [
            {
                "id": "qm_001_qualita_testuale_grammatica_italiana_corretta",
                "title": "Grammatica italiana corretta",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_002_qualita_testuale_accenti_corretti",
                "title": "Accenti corretti",
                "type": "validator_repair",
                "severity": "blocking",
            },
            {
                "id": "qm_003_qualita_testuale_apostrofi_corretti",
                "title": "Apostrofi corretti",
                "type": "validator_repair",
                "severity": "blocking",
            },
            {
                "id": "qm_004_qualita_testuale_punteggiatura_corretta",
                "title": "Punteggiatura corretta",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_005_qualita_testuale_spazi_corretti_prima_e_dopo_punteggiatura",
                "title": "Spazi corretti prima e dopo punteggiatura",
                "type": "validator_repair",
                "severity": "blocking",
            },
            {
                "id": "qm_006_qualita_testuale_frasi_complete",
                "title": "Frasi complete",
                "type": "validator",
                "severity": "blocking_warning",
            },
            {
                "id": "qm_007_qualita_testuale_assenza_di_frasi_spezzate",
                "title": "Assenza di frasi spezzate",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_008_qualita_testuale_assenza_di_frasi_non_terminate",
                "title": "Assenza di frasi non terminate",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_009_qualita_testuale_assenza_di_finali_sospetti",
                "title": "Assenza di finali sospetti",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_010_qualita_testuale_assenza_di_frasi_riempitive",
                "title": "Assenza di frasi riempitive",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_011_qualita_testuale_assenza_di_testo_generico",
                "title": "Assenza di testo generico",
                "type": "validator",
                "severity": "blocking",
            },
            {
                "id": "qm_012_qualita_testuale_assenza_di_vecchi_fallback_demo_test",
                "title": "Assenza di vecchi fallback demo test",
                "type": "validator",
                "severity": "blocking",
            },
        ],
        "safe_repairs": [
            "accenti",
            "apostrofi",
            "spazi_punteggiatura",
        ],
        "scope_guard": {
            "ui_pdf_css_app_touched": False,
            "pipeline_5_11_changed": False,
            "standalone_first": True,
            "no_fallback": True,
            "no_demo_output": True,
        },
    }
