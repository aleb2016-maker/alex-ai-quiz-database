# scripts/patch_super_quality_gate_phase_v1.py
# =============================================================================
# PATCH SUPER QUALITY GATE PHASE V1
#
# Modifica SOLO backend:
# - target: backend/motori_scrittura.py
# - aggiunge Fase 4 SUPER QUALITY GATE V1
# - nessuna modifica a UI, CSS, pulsanti o grafica
#
# Fase 4 V1:
# - controlla le bozze della Fase 3
# - blocca fallback/demo
# - segnala formule meccaniche
# - controlla duplicati
# - controlla quiz con opzioni tutte vere
# - produce clean_output strutturato e quality_report
#
# Non inventa contenuto nuovo.
# Non chiama LLM.
# Non genera HTML/CSS/UI.
# =============================================================================

from __future__ import annotations

import shutil
import sys
from pathlib import Path


TARGET_FILE = Path("backend/motori_scrittura.py")
PATCH_MARKER = "FASE 4 — SUPER QUALITY GATE V1"


SUPER_QUALITY_GATE_CODE = r'''

# =============================================================================
# FASE 4 — SUPER QUALITY GATE V1
# RAG GERARCHICO MAP-REDUCE AD ALBERO
#
# Obiettivo:
# - prendere le bozze della Fase 3 OUTPUT BUILDER
# - verificare qualità, sicurezza, fallback/demo, ripetizioni e quiz
# - produrre un pacchetto pulito o marcare/bloccare le aree non pronte
#
# Questa fase NON deve:
# - toccare UI/CSS/pulsanti
# - inventare contenuto nuovo
# - aggiungere fatti non presenti nelle bozze
# - trasformare quiz grezzi in quiz finali se i distrattori non sono validi
# =============================================================================


@dataclass
class SuperQualityGateConfig:
    """
    Configurazione universale Fase 4.

    Tutti i controlli sono parametrici.
    Nessun valore è specifico di un singolo documento.
    """

    min_summary_points: int = 1
    min_cards: int = 1
    min_study_questions: int = 1
    min_study_pack_sections: int = 1
    expected_quiz_options: int = 4

    block_on_forbidden_signatures: bool = True
    block_on_quiz_all_source_facts: bool = True
    warn_on_mechanical_phrases: bool = True
    warn_on_duplicate_ratio_above: float = 0.35

    mechanical_phrases: List[str] = field(default_factory=lambda: [
        "in sintesi",
        "in conclusione",
        "il documento parla",
        "il documento tratta",
        "questo testo",
        "questo chunk",
        "tema principale",
        "aspetti importanti",
        "riassunto",
        "qual è",
        "quale regola o informazione emerge da",
        "quale affermazione è supportata dal documento",
    ])

    extra_forbidden_signatures: List[str] = field(default_factory=lambda: [
        "contenuto demo",
        "documento di esempio",
        "testo di esempio",
        "fallback",
        "lorem ipsum",
        "knowledge_base_json",
        "sicurezza informatica aziendale",
    ])


@dataclass
class QualityIssue:
    """
    Problema rilevato dal Super Quality Gate.

    severity:
    - warning: problema da rifinire
    - error: problema serio ma non necessariamente bloccante globale
    - blocker: area non pronta per output finale
    """

    issue_id: str
    severity: str
    area: str
    message: str
    evidence: str = ""


@dataclass
class SuperQualityGateResult:
    """
    Output Fase 4.

    approved:
    - True solo se non ci sono blocker né errori critici.
    """

    document_id: str
    phase_name: str = "SUPER_QUALITY_GATE"
    approved: bool = False
    status: str = "PENDING"

    issues: List[QualityIssue] = field(default_factory=list)
    blocked_areas: List[str] = field(default_factory=list)

    clean_output: Dict[str, Any] = field(default_factory=dict)
    quality_report: Dict[str, Any] = field(default_factory=dict)

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def qg_make_issue(
    issue_id: str,
    severity: str,
    area: str,
    message: str,
    evidence: str = "",
) -> QualityIssue:
    """
    Crea un problema qualità normalizzato.
    """

    try:
        return QualityIssue(
            issue_id=normalize_text(issue_id) or "QUALITY_ISSUE",
            severity=normalize_text(severity) or "warning",
            area=normalize_text(area) or "global",
            message=normalize_text(message) or "Problema qualità rilevato.",
            evidence=output_trim_text(evidence, 400) if "output_trim_text" in globals() else normalize_text(evidence),
        )
    except Exception:
        return QualityIssue(
            issue_id="QUALITY_ISSUE_BUILD_FAILED",
            severity="warning",
            area="global",
            message="Errore durante la costruzione di un issue qualità.",
            evidence="",
        )


def qg_normalize_for_compare(text: Any) -> str:
    """
    Normalizzazione prudente per confronti qualità.
    """

    try:
        value = normalize_text(text).lower()
        value = re.sub(r"[^\w\sàèéìòù]", " ", value, flags=re.IGNORECASE)
        value = re.sub(r"\s+", " ", value).strip()
        return value
    except Exception:
        return ""


def qg_find_forbidden(text: Any, config: SuperQualityGateConfig) -> List[str]:
    """
    Trova firme demo/fallback/preconfezionate.
    """

    found: List[str] = []

    try:
        value = normalize_text(text)
        lowered = value.lower()

        try:
            found.extend(find_forbidden_signatures(value))
        except Exception:
            pass

        for signature in config.extra_forbidden_signatures:
            sig = normalize_text(signature)
            if sig and sig.lower() in lowered:
                found.append(sig)

        return reduce_unique_strings(found)

    except Exception:
        return found


def qg_find_mechanical_phrases(text: Any, config: SuperQualityGateConfig) -> List[str]:
    """
    Trova formule meccaniche o da bozza grezza.
    """

    found: List[str] = []

    try:
        lowered = normalize_text(text).lower()

        for phrase in config.mechanical_phrases:
            clean_phrase = normalize_text(phrase).lower()
            if clean_phrase and clean_phrase in lowered:
                found.append(clean_phrase)

        return reduce_unique_strings(found)

    except Exception:
        return found


def qg_duplicate_ratio(texts: List[str]) -> float:
    """
    Calcola rapporto duplicati.

    0.0 = nessun duplicato.
    1.0 = tutto duplicato.
    """

    try:
        cleaned = [
            qg_normalize_for_compare(text)
            for text in texts
            if qg_normalize_for_compare(text)
        ]

        if not cleaned:
            return 0.0

        unique_count = len(set(cleaned))
        duplicate_count = max(0, len(cleaned) - unique_count)
        return duplicate_count / max(1, len(cleaned))

    except Exception:
        return 0.0


def qg_validate_text_block(
    area: str,
    text: Any,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Controllo qualità base su un testo.
    """

    issues: List[QualityIssue] = []

    try:
        clean_text = normalize_text(text)

        if not clean_text:
            issues.append(
                qg_make_issue(
                    issue_id="EMPTY_TEXT_BLOCK",
                    severity="error",
                    area=area,
                    message="Blocco testuale vuoto.",
                )
            )
            return issues

        forbidden = qg_find_forbidden(clean_text, config)
        if forbidden:
            issues.append(
                qg_make_issue(
                    issue_id="FORBIDDEN_SIGNATURE_FOUND",
                    severity="blocker" if config.block_on_forbidden_signatures else "error",
                    area=area,
                    message="Rilevate firme demo/fallback/preconfezionate.",
                    evidence=", ".join(forbidden),
                )
            )

        if config.warn_on_mechanical_phrases:
            mechanical = qg_find_mechanical_phrases(clean_text, config)
            if mechanical:
                issues.append(
                    qg_make_issue(
                        issue_id="MECHANICAL_PHRASE_FOUND",
                        severity="warning",
                        area=area,
                        message="Rilevata formula meccanica o da bozza grezza.",
                        evidence=", ".join(mechanical),
                    )
                )

        return issues

    except Exception as exc:
        issues.append(
            qg_make_issue(
                issue_id="TEXT_BLOCK_VALIDATION_EXCEPTION",
                severity="error",
                area=area,
                message=f"Errore controllo testo: {type(exc).__name__}: {exc}",
            )
        )
        return issues


def qg_collect_source_facts(output_result: OutputBuilderResult) -> List[str]:
    """
    Raccoglie tutti i facts presenti nelle bozze.

    Serve a capire se un quiz usa come distrattori affermazioni vere.
    """

    facts: List[str] = []

    try:
        summary = getattr(output_result, "summary_draft", None)
        if summary is not None:
            facts.extend(getattr(summary, "key_points", []) or [])

        for card in getattr(output_result, "cards_draft", []) or []:
            facts.extend(getattr(card, "source_facts", []) or [])
            message = normalize_text(getattr(card, "message_key", ""))
            if message:
                facts.append(message)

        for question in getattr(output_result, "study_questions_draft", []) or []:
            answer = normalize_text(getattr(question, "answer_guide", ""))
            if answer:
                facts.append(answer)
            facts.extend(getattr(question, "source_facts", []) or [])

        pack = getattr(output_result, "study_pack_draft", None)
        if pack is not None:
            for section in getattr(pack, "sections", []) or []:
                facts.extend(getattr(section, "key_facts", []) or [])

        return reduce_unique_strings(facts)

    except Exception:
        return reduce_unique_strings(facts)


def qg_validate_summary(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida summary_draft.
    """

    issues: List[QualityIssue] = []

    try:
        summary = getattr(output_result, "summary_draft", None)

        if summary is None:
            return [
                qg_make_issue(
                    issue_id="SUMMARY_DRAFT_MISSING",
                    severity="blocker",
                    area="summary",
                    message="summary_draft mancante.",
                )
            ]

        points = list(getattr(summary, "key_points", []) or [])

        if len(points) < config.min_summary_points:
            issues.append(
                qg_make_issue(
                    issue_id="SUMMARY_TOO_SHORT",
                    severity="error",
                    area="summary",
                    message="Il riassunto bozza ha troppo pochi punti chiave.",
                    evidence=f"points={len(points)}",
                )
            )

        for index, point in enumerate(points, start=1):
            issues.extend(
                qg_validate_text_block(
                    area=f"summary.point_{index}",
                    text=point,
                    config=config,
                )
            )

        ratio = qg_duplicate_ratio(points)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="SUMMARY_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="summary",
                    message="Rapporto duplicati alto nel riassunto bozza.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="SUMMARY_VALIDATION_EXCEPTION",
                severity="error",
                area="summary",
                message=f"Errore validazione summary: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_cards(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida cards_draft.
    """

    issues: List[QualityIssue] = []

    try:
        cards = list(getattr(output_result, "cards_draft", []) or [])

        if len(cards) < config.min_cards:
            issues.append(
                qg_make_issue(
                    issue_id="CARDS_DRAFT_MISSING_OR_TOO_SHORT",
                    severity="error",
                    area="cards",
                    message="cards_draft mancante o troppo corto.",
                    evidence=f"cards={len(cards)}",
                )
            )

        messages: List[str] = []

        for index, card in enumerate(cards, start=1):
            title = normalize_text(getattr(card, "title", ""))
            message_key = normalize_text(getattr(card, "message_key", ""))
            messages.append(message_key)

            issues.extend(qg_validate_text_block(f"cards.card_{index}.title", title, config))
            issues.extend(qg_validate_text_block(f"cards.card_{index}.message_key", message_key, config))

            for fact_index, fact in enumerate(getattr(card, "source_facts", []) or [], start=1):
                issues.extend(
                    qg_validate_text_block(
                        f"cards.card_{index}.source_fact_{fact_index}",
                        fact,
                        config,
                    )
                )

        ratio = qg_duplicate_ratio(messages)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="CARDS_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="cards",
                    message="Rapporto duplicati alto nelle card bozza.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="CARDS_VALIDATION_EXCEPTION",
                severity="error",
                area="cards",
                message=f"Errore validazione cards: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_study_questions(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida study_questions_draft.
    """

    issues: List[QualityIssue] = []

    try:
        questions = list(getattr(output_result, "study_questions_draft", []) or [])

        if len(questions) < config.min_study_questions:
            issues.append(
                qg_make_issue(
                    issue_id="STUDY_QUESTIONS_MISSING_OR_TOO_SHORT",
                    severity="error",
                    area="study_questions",
                    message="Domande studio mancanti o troppo poche.",
                    evidence=f"questions={len(questions)}",
                )
            )

        question_texts: List[str] = []

        for index, question in enumerate(questions, start=1):
            question_text = normalize_text(getattr(question, "question", ""))
            answer_guide = normalize_text(getattr(question, "answer_guide", ""))

            question_texts.append(question_text)

            issues.extend(
                qg_validate_text_block(
                    f"study_questions.question_{index}.question",
                    question_text,
                    config,
                )
            )
            issues.extend(
                qg_validate_text_block(
                    f"study_questions.question_{index}.answer_guide",
                    answer_guide,
                    config,
                )
            )

        ratio = qg_duplicate_ratio(question_texts)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="STUDY_QUESTIONS_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="study_questions",
                    message="Rapporto duplicati alto nelle domande studio.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="STUDY_QUESTIONS_VALIDATION_EXCEPTION",
                severity="error",
                area="study_questions",
                message=f"Errore validazione domande studio: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_quiz(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida quiz_draft.

    Controllo fondamentale:
    se i distrattori sono facts reali del documento, il quiz non è finale.
    """

    issues: List[QualityIssue] = []

    try:
        quiz = list(getattr(output_result, "quiz_draft", []) or [])
        source_facts = qg_collect_source_facts(output_result)
        source_fact_keys = set(qg_normalize_for_compare(fact) for fact in source_facts)

        if not quiz:
            issues.append(
                qg_make_issue(
                    issue_id="QUIZ_DRAFT_MISSING",
                    severity="warning",
                    area="quiz",
                    message="quiz_draft mancante. Può essere accettabile se il documento non contiene abbastanza facts.",
                )
            )
            return issues

        question_texts: List[str] = []

        for index, quiz_question in enumerate(quiz, start=1):
            area_prefix = f"quiz.question_{index}"
            question_text = normalize_text(getattr(quiz_question, "question", ""))
            options = list(getattr(quiz_question, "options", []) or [])
            correct_option_id = normalize_text(getattr(quiz_question, "correct_option_id", ""))

            question_texts.append(question_text)

            issues.extend(qg_validate_text_block(f"{area_prefix}.question", question_text, config))

            if len(options) != config.expected_quiz_options:
                issues.append(
                    qg_make_issue(
                        issue_id="QUIZ_OPTIONS_COUNT_INVALID",
                        severity="blocker",
                        area="quiz",
                        message="Numero opzioni quiz non valido.",
                        evidence=f"question={index} options={len(options)} expected={config.expected_quiz_options}",
                    )
                )

            correct_options = [
                option for option in options
                if bool(getattr(option, "is_correct", False))
            ]

            if len(correct_options) != 1:
                issues.append(
                    qg_make_issue(
                        issue_id="QUIZ_CORRECT_OPTION_COUNT_INVALID",
                        severity="blocker",
                        area="quiz",
                        message="Ogni domanda quiz deve avere esattamente una risposta corretta.",
                        evidence=f"question={index} correct_options={len(correct_options)}",
                    )
                )

            if correct_options:
                expected_correct_id = normalize_text(getattr(correct_options[0], "option_id", ""))
                if correct_option_id and correct_option_id != expected_correct_id:
                    issues.append(
                        qg_make_issue(
                            issue_id="QUIZ_CORRECT_OPTION_ID_MISMATCH",
                            severity="blocker",
                            area="quiz",
                            message="correct_option_id non coincide con l'opzione marcata corretta.",
                            evidence=f"question={index} correct_option_id={correct_option_id} expected={expected_correct_id}",
                        )
                    )

            non_correct_options = [
                option for option in options
                if not bool(getattr(option, "is_correct", False))
            ]

            non_correct_source_fact_count = 0

            for option_index, option in enumerate(options, start=1):
                option_text = normalize_text(getattr(option, "text", ""))
                issues.extend(
                    qg_validate_text_block(
                        f"{area_prefix}.option_{option_index}",
                        option_text,
                        config,
                    )
                )

                if not bool(getattr(option, "is_correct", False)):
                    option_key = qg_normalize_for_compare(option_text)
                    if option_key and option_key in source_fact_keys:
                        non_correct_source_fact_count += 1

            if (
                config.block_on_quiz_all_source_facts
                and non_correct_options
                and non_correct_source_fact_count == len(non_correct_options)
            ):
                issues.append(
                    qg_make_issue(
                        issue_id="QUIZ_DISTRACTORS_ARE_SOURCE_FACTS",
                        severity="blocker",
                        area="quiz",
                        message=(
                            "I distrattori risultano fatti veri presenti nel documento. "
                            "La bozza quiz non è valida come quiz finale."
                        ),
                        evidence=f"question={index} distractors_true={non_correct_source_fact_count}/{len(non_correct_options)}",
                    )
                )

        ratio = qg_duplicate_ratio(question_texts)
        if ratio > config.warn_on_duplicate_ratio_above:
            issues.append(
                qg_make_issue(
                    issue_id="QUIZ_QUESTIONS_DUPLICATE_RATIO_HIGH",
                    severity="warning",
                    area="quiz",
                    message="Domande quiz troppo ripetitive.",
                    evidence=str(ratio),
                )
            )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="QUIZ_VALIDATION_EXCEPTION",
                severity="error",
                area="quiz",
                message=f"Errore validazione quiz: {type(exc).__name__}: {exc}",
            )
        ]


def qg_validate_study_pack(
    output_result: OutputBuilderResult,
    config: SuperQualityGateConfig,
) -> List[QualityIssue]:
    """
    Valida study_pack_draft.
    """

    issues: List[QualityIssue] = []

    try:
        pack = getattr(output_result, "study_pack_draft", None)

        if pack is None:
            return [
                qg_make_issue(
                    issue_id="STUDY_PACK_DRAFT_MISSING",
                    severity="error",
                    area="study_pack",
                    message="study_pack_draft mancante.",
                )
            ]

        sections = list(getattr(pack, "sections", []) or [])

        if len(sections) < config.min_study_pack_sections:
            issues.append(
                qg_make_issue(
                    issue_id="STUDY_PACK_SECTIONS_TOO_SHORT",
                    severity="error",
                    area="study_pack",
                    message="Study pack con troppe poche sezioni.",
                    evidence=f"sections={len(sections)}",
                )
            )

        for section_index, section in enumerate(sections, start=1):
            title = normalize_text(getattr(section, "title", ""))
            issues.extend(
                qg_validate_text_block(
                    f"study_pack.section_{section_index}.title",
                    title,
                    config,
                )
            )

            for fact_index, fact in enumerate(getattr(section, "key_facts", []) or [], start=1):
                issues.extend(
                    qg_validate_text_block(
                        f"study_pack.section_{section_index}.fact_{fact_index}",
                        fact,
                        config,
                    )
                )

        return issues

    except Exception as exc:
        return [
            qg_make_issue(
                issue_id="STUDY_PACK_VALIDATION_EXCEPTION",
                severity="error",
                area="study_pack",
                message=f"Errore validazione study pack: {type(exc).__name__}: {exc}",
            )
        ]


def qg_clean_output_bundle(output_result: OutputBuilderResult) -> Dict[str, Any]:
    """
    Crea pacchetto pulito ma ancora strutturato.

    Non riscrive i contenuti.
    Pulisce solo spazi, serializza e conserva struttura.
    """

    clean: Dict[str, Any] = {}

    try:
        summary = getattr(output_result, "summary_draft", None)
        if summary is not None:
            clean["summary"] = {
                "title": normalize_text(getattr(summary, "title", "")),
                "key_points": [
                    normalize_text(point)
                    for point in getattr(summary, "key_points", []) or []
                    if normalize_text(point)
                ],
                "source_pages": list(getattr(summary, "source_pages", []) or []),
            }

        clean["cards"] = []
        for card in getattr(output_result, "cards_draft", []) or []:
            clean["cards"].append(
                {
                    "card_id": normalize_text(getattr(card, "card_id", "")),
                    "title": normalize_text(getattr(card, "title", "")),
                    "message_key": normalize_text(getattr(card, "message_key", "")),
                    "source_facts": [
                        normalize_text(fact)
                        for fact in getattr(card, "source_facts", []) or []
                        if normalize_text(fact)
                    ],
                    "micro_concepts": [
                        normalize_text(concept)
                        for concept in getattr(card, "micro_concepts", []) or []
                        if normalize_text(concept)
                    ],
                    "source_pages": list(getattr(card, "source_pages", []) or []),
                }
            )

        clean["study_questions"] = []
        for question in getattr(output_result, "study_questions_draft", []) or []:
            clean["study_questions"].append(
                {
                    "question_id": normalize_text(getattr(question, "question_id", "")),
                    "question": normalize_text(getattr(question, "question", "")),
                    "answer_guide": normalize_text(getattr(question, "answer_guide", "")),
                    "source_facts": [
                        normalize_text(fact)
                        for fact in getattr(question, "source_facts", []) or []
                        if normalize_text(fact)
                    ],
                    "source_pages": list(getattr(question, "source_pages", []) or []),
                }
            )

        clean["quiz"] = []
        for quiz_question in getattr(output_result, "quiz_draft", []) or []:
            clean["quiz"].append(
                {
                    "question_id": normalize_text(getattr(quiz_question, "question_id", "")),
                    "question": normalize_text(getattr(quiz_question, "question", "")),
                    "options": [
                        {
                            "option_id": normalize_text(getattr(option, "option_id", "")),
                            "text": normalize_text(getattr(option, "text", "")),
                            "is_correct": bool(getattr(option, "is_correct", False)),
                        }
                        for option in getattr(quiz_question, "options", []) or []
                    ],
                    "correct_option_id": normalize_text(getattr(quiz_question, "correct_option_id", "")),
                    "explanation_draft": normalize_text(getattr(quiz_question, "explanation_draft", "")),
                    "source_pages": list(getattr(quiz_question, "source_pages", []) or []),
                }
            )

        pack = getattr(output_result, "study_pack_draft", None)
        if pack is not None:
            clean["study_pack"] = {
                "title": normalize_text(getattr(pack, "title", "")),
                "sections": [
                    {
                        "section_id": normalize_text(getattr(section, "section_id", "")),
                        "title": normalize_text(getattr(section, "title", "")),
                        "key_facts": [
                            normalize_text(fact)
                            for fact in getattr(section, "key_facts", []) or []
                            if normalize_text(fact)
                        ],
                        "micro_concepts": [
                            normalize_text(concept)
                            for concept in getattr(section, "micro_concepts", []) or []
                            if normalize_text(concept)
                        ],
                        "entities": [
                            normalize_text(entity)
                            for entity in getattr(section, "entities", []) or []
                            if normalize_text(entity)
                        ],
                        "source_pages": list(getattr(section, "source_pages", []) or []),
                    }
                    for section in getattr(pack, "sections", []) or []
                ],
                "global_micro_concepts": [
                    normalize_text(concept)
                    for concept in getattr(pack, "global_micro_concepts", []) or []
                    if normalize_text(concept)
                ],
                "global_entities": [
                    normalize_text(entity)
                    for entity in getattr(pack, "global_entities", []) or []
                    if normalize_text(entity)
                ],
            }

        return clean

    except Exception as exc:
        return {
            "clean_output_error": f"{type(exc).__name__}: {exc}"
        }


def run_super_quality_gate(
    output_result: OutputBuilderResult,
    config: Optional[SuperQualityGateConfig] = None,
) -> SuperQualityGateResult:
    """
    Funzione madre Fase 4 — SUPER QUALITY GATE.

    Input:
    - OutputBuilderResult della Fase 3

    Output:
    - SuperQualityGateResult con:
      - approved/status
      - issues
      - blocked_areas
      - clean_output
      - quality_report
    """

    cfg = config or SuperQualityGateConfig()

    result = SuperQualityGateResult(
        document_id=normalize_text(getattr(output_result, "document_id", "")) or "unknown_document",
    )

    try:
        issues: List[QualityIssue] = []

        issues.extend(qg_validate_summary(output_result, cfg))
        issues.extend(qg_validate_cards(output_result, cfg))
        issues.extend(qg_validate_study_questions(output_result, cfg))
        issues.extend(qg_validate_quiz(output_result, cfg))
        issues.extend(qg_validate_study_pack(output_result, cfg))

        result.issues = issues

        blockers = [issue for issue in issues if issue.severity == "blocker"]
        errors = [issue for issue in issues if issue.severity == "error"]
        warnings = [issue for issue in issues if issue.severity == "warning"]

        result.blocked_areas = reduce_unique_strings(
            [issue.area.split(".")[0] for issue in blockers]
        )

        result.clean_output = qg_clean_output_bundle(output_result)

        result.quality_report = {
            "issues_count": len(issues),
            "blockers_count": len(blockers),
            "errors_count": len(errors),
            "warnings_count": len(warnings),
            "blocked_areas": list(result.blocked_areas),
            "summary_points": len(result.clean_output.get("summary", {}).get("key_points", [])),
            "cards_count": len(result.clean_output.get("cards", [])),
            "study_questions_count": len(result.clean_output.get("study_questions", [])),
            "quiz_questions_count": len(result.clean_output.get("quiz", [])),
            "study_pack_sections_count": len(result.clean_output.get("study_pack", {}).get("sections", [])),
        }

        if blockers:
            result.status = "BLOCKED"
            result.approved = False
        elif errors:
            result.status = "NEEDS_REVIEW"
            result.approved = False
        else:
            result.status = "APPROVED"
            result.approved = True

        return result

    except Exception as exc:
        result.status = "ERROR"
        result.approved = False
        result.errors.append(f"SUPER_QUALITY_GATE_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def super_quality_gate_result_to_dict(result: SuperQualityGateResult) -> Dict[str, Any]:
    """
    Serializza SuperQualityGateResult in dict.
    """

    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "SUPER_QUALITY_GATE",
            "approved": False,
            "status": "SERIALIZATION_ERROR",
            "errors": ["SUPER_QUALITY_GATE_RESULT_SERIALIZATION_FAILED"],
        }


def super_quality_gate_result_to_json(result: SuperQualityGateResult, indent: int = 2) -> str:
    """
    Serializza SuperQualityGateResult in JSON.
    """

    try:
        return json.dumps(
            super_quality_gate_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "SUPER_QUALITY_GATE",
                "approved": False,
                "status": "JSON_SERIALIZATION_ERROR",
                "errors": [
                    f"SUPER_QUALITY_GATE_JSON_SERIALIZATION_FAILED: {type(exc).__name__}: {exc}"
                ],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 4 — SUPER QUALITY GATE V1
# =============================================================================
'''


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if PATCH_MARKER in original:
            print("✅ SUPER QUALITY GATE V1 già presente. Nessuna modifica necessaria.")
            return 0

        backup = TARGET_FILE.with_suffix(".py.bak_super_quality_gate_phase_v1")
        shutil.copy2(TARGET_FILE, backup)

        patched = original.rstrip() + "\n\n" + SUPER_QUALITY_GATE_CODE + "\n"

        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Patch SUPER QUALITY GATE PHASE V1 applicata con successo.")
        print(f"Backup creato: {backup}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore patch SUPER QUALITY GATE PHASE V1: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())