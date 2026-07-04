from pathlib import Path
import shutil
import sys

TARGET_FILE = Path("backend/motori_scrittura.py")
REQUIRED_MARKER = "FASE 5.1 — MICRO CONCEPTS CARDS QUALITY PATCH"
PATCH_MARKER = "FASE 5.2 — QUALITY STUDY QUESTIONS QUIZ V1"

PATCH_CODE = r'''

# =============================================================================
# FASE 5.2 — QUALITY STUDY QUESTIONS QUIZ V1
#
# Completa la Fase 5 per:
# - Genera Domande Studio
# - Genera Test / Quiz
#
# Questa fase usa l'output pulito della Fase 4:
# - SuperQualityGateResult.clean_output
#
# E produce:
# - domande studio naturali, non meccaniche
# - risposte guida chiare
# - quiz con 1 risposta corretta e 3 distrattori falsi/plausibili
# - validazione anti-distrattori veri
#
# Divieti:
# - non modifica Fasi 1–4
# - non modifica Fase 5 summary/card
# - non tocca UI/CSS/pulsanti/layout
# - non approva quiz con distrattori che coincidono con fatti veri
# =============================================================================


@dataclass
class Phase5StudyQuizConfig:
    max_study_questions: int = 12
    max_quiz_questions: int = 10
    quiz_options_count: int = 4
    max_fact_chars: int = 700
    max_micro_concepts_per_item: int = 5
    require_phase4_study_quiz_not_blocked: bool = False


@dataclass
class QualityStudyQuestionFinal:
    question_id: str
    domanda: str
    risposta_guida: str
    tipo_domanda: str
    livello_cognitivo: str
    fatto_origine: str
    micro_concetti: List[str] = field(default_factory=list)
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class QualityQuizOptionFinal:
    option_id: str
    testo: str
    is_correct: bool = False


@dataclass
class QualityQuizQuestionFinal:
    question_id: str
    domanda: str
    opzioni: List[QualityQuizOptionFinal] = field(default_factory=list)
    correct_option_id: str = ""
    spiegazione: str = ""
    fatto_origine: str = ""
    micro_concetti: List[str] = field(default_factory=list)
    fonte_pagine: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class Phase5QualityStudyQuizResult:
    document_id: str
    phase_name: str = "QUALITY_STUDY_QUIZ"
    approved: bool = False
    status: str = "PENDING"

    domande_studio: List[QualityStudyQuestionFinal] = field(default_factory=list)
    test_quiz: List[QualityQuizQuestionFinal] = field(default_factory=list)

    quality_report: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def q52_clean(value: Any) -> str:
    try:
        if "q5_fix_italian_typography" in globals():
            return q5_fix_italian_typography(value)
        return normalize_text(value)
    except Exception:
        return ""


def q52_sentence(value: Any) -> str:
    try:
        text = q52_clean(value).strip()
        if not text:
            return ""
        if text[-1] not in ".!?":
            text += "."
        return text
    except Exception:
        return ""


def q52_limit(value: Any, max_chars: int = 700) -> str:
    try:
        text = q52_clean(value)
        if max_chars <= 0 or len(text) <= max_chars:
            return text
        return text[:max_chars].rstrip() + "..."
    except Exception:
        return ""


def q52_unique(values: Sequence[Any]) -> List[str]:
    try:
        return q5_unique_strings(values)
    except Exception:
        output: List[str] = []
        seen = set()
        for value in values:
            clean = q52_clean(value)
            key = clean.lower()
            if clean and key not in seen:
                seen.add(key)
                output.append(clean)
        return output


def q52_extract_facts(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
) -> List[str]:
    try:
        facts = q5_extract_facts_from_gate(gate_result, output_result)
        return q52_unique([q52_limit(fact, 900) for fact in facts if q52_clean(fact)])
    except Exception:
        return []


def q52_extract_concepts(gate_result: SuperQualityGateResult) -> List[str]:
    try:
        concepts = q5_extract_concepts_from_gate(gate_result)
        valid = [
            q52_clean(concept).lower()
            for concept in concepts
            if q5_is_valid_micro_concept(q52_clean(concept))
        ]
        return q52_unique(valid)
    except Exception:
        return []


def q52_extract_pages(gate_result: SuperQualityGateResult) -> List[int]:
    try:
        return q5_extract_pages_from_gate(gate_result)
    except Exception:
        return []


def q52_fact_type(fact: str) -> str:
    try:
        lowered = q52_clean(fact).lower()

        if "non devono" in lowered or "non deve" in lowered or "vietato" in lowered:
            return "divieto"

        if "riduce il rischio" in lowered or "previene" in lowered or "rischio" in lowered:
            return "causa_effetto_rischio"

        if "deve" in lowered or "devono" in lowered or "obbligo" in lowered:
            return "obbligo"

        if "controllo" in lowered or "limita" in lowered:
            return "controllo"

        return "informazione_chiave"

    except Exception:
        return "informazione_chiave"


def q52_cognitive_level(fact_type: str) -> str:
    try:
        mapping = {
            "divieto": "applicazione",
            "causa_effetto_rischio": "comprensione",
            "obbligo": "applicazione",
            "controllo": "comprensione",
            "informazione_chiave": "ricordo_comprensione",
        }
        return mapping.get(fact_type, "comprensione")
    except Exception:
        return "comprensione"


def q52_local_concepts(fact: str, preferred_concepts: List[str], limit: int = 5) -> List[str]:
    try:
        concepts = q5_select_micro_concepts(
            preferred_concepts=preferred_concepts,
            text=fact,
            limit=limit,
        )
        return q52_unique([concept for concept in concepts if q5_is_valid_micro_concept(concept)])[:limit]
    except Exception:
        return []


def q52_topic_label(fact: str, concepts: List[str]) -> str:
    try:
        if concepts:
            return concepts[0]
        return q5_title_from_text(fact, fallback="questo punto", max_words=5).lower()
    except Exception:
        return "questo punto"


def q52_build_study_question_text(fact: str, concepts: List[str], index: int) -> str:
    try:
        fact_type = q52_fact_type(fact)
        topic = q52_topic_label(fact, concepts)

        if fact_type == "divieto":
            return f"Quale comportamento deve essere evitato riguardo a {topic}?"

        if fact_type == "causa_effetto_rischio":
            return f"Perché {topic} è collegato alla riduzione del rischio?"

        if fact_type == "obbligo":
            return f"Quale obbligo operativo viene indicato riguardo a {topic}?"

        if fact_type == "controllo":
            return f"Quale funzione svolge {topic} nel contesto del documento?"

        return f"Che cosa bisogna ricordare riguardo a {topic}?"

    except Exception:
        return f"Qual è il punto operativo principale numero {index}?"


def q52_build_answer_guide(fact: str, fact_type: str) -> str:
    try:
        clean_fact = q52_sentence(fact)

        if fact_type == "divieto":
            return q52_clean(
                "La risposta deve evidenziare il divieto operativo indicato dal documento: "
                + q5_lower_first(clean_fact)
            )

        if fact_type == "causa_effetto_rischio":
            return q52_clean(
                "La risposta deve spiegare il rapporto causa-effetto indicato dal documento: "
                + q5_lower_first(clean_fact)
            )

        if fact_type == "obbligo":
            return q52_clean(
                "La risposta deve indicare l'obbligo operativo espresso nel documento: "
                + q5_lower_first(clean_fact)
            )

        if fact_type == "controllo":
            return q52_clean(
                "La risposta deve chiarire la funzione del controllo descritto: "
                + q5_lower_first(clean_fact)
            )

        return q52_clean(
            "La risposta deve richiamare il punto informativo indicato dal documento: "
            + q5_lower_first(clean_fact)
        )

    except Exception:
        return q52_sentence(fact)


def q52_build_quality_study_questions(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5StudyQuizConfig,
) -> List[QualityStudyQuestionFinal]:
    questions: List[QualityStudyQuestionFinal] = []

    try:
        for index, fact in enumerate(facts[: max(0, config.max_study_questions)], start=1):
            clean_fact = q52_limit(fact, config.max_fact_chars)
            fact_type = q52_fact_type(clean_fact)
            concepts = q52_local_concepts(
                clean_fact,
                preferred_concepts,
                limit=config.max_micro_concepts_per_item,
            )

            domanda = q52_build_study_question_text(clean_fact, concepts, index)
            risposta = q52_build_answer_guide(clean_fact, fact_type)

            item = QualityStudyQuestionFinal(
                question_id=f"phase5_study_question_{index:03d}",
                domanda=domanda,
                risposta_guida=risposta,
                tipo_domanda=fact_type,
                livello_cognitivo=q52_cognitive_level(fact_type),
                fatto_origine=clean_fact,
                micro_concetti=concepts,
                fonte_pagine=list(pages),
            )

            lowered = item.domanda.lower()
            if "quale regola o informazione emerge da" in lowered:
                item.warnings.append("PHASE5_STUDY_QUESTION_MECHANICAL_TEMPLATE")

            questions.append(item)

        return questions

    except Exception:
        return questions


def q52_false_distractors_from_fact(fact: str) -> List[str]:
    """
    Genera distrattori falsi ma plausibili.

    Non li usa come facts.
    Servono solo come opzioni errate del quiz.
    """

    distractors: List[str] = []

    try:
        clean = q52_clean(fact).rstrip(".")
        lowered = clean.lower()

        replacements = [
            ("non devono essere condivise", "possono essere condivise liberamente"),
            ("non deve essere condivisa", "può essere condivisa liberamente"),
            ("deve essere associato", "può rimanere non associato"),
            ("deve essere associata", "può rimanere non associata"),
            ("devono essere", "non devono essere necessariamente"),
            ("deve essere", "non deve essere necessariamente"),
            ("limita l'utilizzo", "consente l'utilizzo illimitato"),
            ("limita", "non limita"),
            ("riduce il rischio", "aumenta il rischio"),
            ("evita", "favorisce"),
            ("persona identificabile", "persona non identificabile"),
            ("utenti autorizzati", "qualsiasi utente"),
            ("permessi attivi", "permessi illimitati"),
            ("sistemi interni", "sistemi esterni non controllati"),
        ]

        for old, new in replacements:
            if old in lowered:
                pattern = re.compile(re.escape(old), flags=re.IGNORECASE)
                candidate = pattern.sub(new, clean, count=1)
                candidate = q52_sentence(candidate)
                if candidate and candidate.lower() != q52_sentence(clean).lower():
                    distractors.append(candidate)

        topic = q52_topic_label(clean, q52_domain_micro_concepts_from_text(clean))

        generic_false = [
            f"Il documento indica che {topic} può essere ignorato senza effetti operativi.",
            f"Il documento esclude la necessità di controllare {topic}.",
            f"Il documento presenta {topic} come un aspetto facoltativo e non rilevante.",
            f"Il documento sostiene che {topic} non abbia alcun impatto sui controlli.",
        ]

        distractors.extend(generic_false)

        return q52_unique(distractors)

    except Exception:
        return q52_unique(distractors)


def q52_build_quiz_question_text(fact: str, concepts: List[str], index: int) -> str:
    try:
        fact_type = q52_fact_type(fact)
        topic = q52_topic_label(fact, concepts)

        if fact_type == "divieto":
            return f"Quale affermazione descrive correttamente il divieto su {topic}?"

        if fact_type == "causa_effetto_rischio":
            return f"Quale affermazione descrive correttamente l'effetto di {topic}?"

        if fact_type == "obbligo":
            return f"Quale affermazione descrive correttamente l'obbligo su {topic}?"

        if fact_type == "controllo":
            return f"Quale affermazione descrive correttamente la funzione di {topic}?"

        return f"Quale affermazione descrive correttamente {topic}?"

    except Exception:
        return f"Quale affermazione è corretta nel punto {index}?"


def q52_build_quality_quiz(
    facts: List[str],
    preferred_concepts: List[str],
    pages: List[int],
    config: Phase5StudyQuizConfig,
) -> List[QualityQuizQuestionFinal]:
    quiz: List[QualityQuizQuestionFinal] = []

    try:
        source_keys = set(qg_normalize_for_compare(fact) for fact in facts if q52_clean(fact))
        option_ids = ["A", "B", "C", "D"]

        for index, fact in enumerate(facts[: max(0, config.max_quiz_questions)], start=1):
            correct_fact = q52_limit(fact, config.max_fact_chars)
            concepts = q52_local_concepts(
                correct_fact,
                preferred_concepts,
                limit=config.max_micro_concepts_per_item,
            )

            distractors: List[str] = []
            for candidate in q52_false_distractors_from_fact(correct_fact):
                key = qg_normalize_for_compare(candidate)
                if key and key not in source_keys:
                    distractors.append(candidate)

            distractors = q52_unique(distractors)

            if len(distractors) < 3:
                continue

            correct_position = (index - 1) % 4
            raw_options = distractors[:3]
            raw_options.insert(correct_position, correct_fact)

            options: List[QualityQuizOptionFinal] = []

            for option_index, option_text in enumerate(raw_options[:4]):
                options.append(
                    QualityQuizOptionFinal(
                        option_id=option_ids[option_index],
                        testo=q52_limit(option_text, config.max_fact_chars),
                        is_correct=(option_index == correct_position),
                    )
                )

            question = QualityQuizQuestionFinal(
                question_id=f"phase5_quiz_question_{index:03d}",
                domanda=q52_build_quiz_question_text(correct_fact, concepts, index),
                opzioni=options,
                correct_option_id=option_ids[correct_position],
                spiegazione=q52_clean(
                    "La risposta corretta è quella che riprende il fatto verificato dal documento: "
                    + q5_lower_first(q52_sentence(correct_fact))
                ),
                fatto_origine=correct_fact,
                micro_concetti=concepts,
                fonte_pagine=list(pages),
            )

            quiz.append(question)

        return quiz

    except Exception:
        return quiz


def q52_validate_study_questions(questions: List[QualityStudyQuestionFinal]) -> List[str]:
    errors: List[str] = []

    try:
        forbidden_templates = [
            "quale regola o informazione emerge da",
            "quale affermazione è supportata dal documento",
        ]

        seen = set()

        for item in questions:
            if not q52_clean(item.domanda):
                errors.append(f"{item.question_id}: domanda vuota")

            if not q52_clean(item.risposta_guida):
                errors.append(f"{item.question_id}: risposta_guida vuota")

            lowered = item.domanda.lower()

            for template in forbidden_templates:
                if template in lowered:
                    errors.append(f"{item.question_id}: formula meccanica vietata")

            key = qg_normalize_for_compare(item.domanda)
            if key in seen:
                errors.append(f"{item.question_id}: domanda duplicata")
            seen.add(key)

        return errors

    except Exception as exc:
        return [f"PHASE5_STUDY_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def q52_validate_quiz(quiz: List[QualityQuizQuestionFinal], source_facts: List[str], expected_options: int = 4) -> List[str]:
    errors: List[str] = []

    try:
        source_keys = set(qg_normalize_for_compare(fact) for fact in source_facts if q52_clean(fact))

        forbidden_question_templates = [
            "quale affermazione è supportata dal documento",
            "quale regola o informazione emerge da",
        ]

        seen_questions = set()

        for question in quiz:
            if not q52_clean(question.domanda):
                errors.append(f"{question.question_id}: domanda vuota")

            lowered_question = question.domanda.lower()
            for template in forbidden_question_templates:
                if template in lowered_question:
                    errors.append(f"{question.question_id}: formula quiz meccanica vietata")

            question_key = qg_normalize_for_compare(question.domanda)
            if question_key in seen_questions:
                errors.append(f"{question.question_id}: domanda quiz duplicata")
            seen_questions.add(question_key)

            if len(question.opzioni) != expected_options:
                errors.append(f"{question.question_id}: numero opzioni non valido")

            correct_options = [option for option in question.opzioni if option.is_correct]
            if len(correct_options) != 1:
                errors.append(f"{question.question_id}: deve avere esattamente una corretta")

            if correct_options:
                if q52_clean(correct_options[0].option_id) != q52_clean(question.correct_option_id):
                    errors.append(f"{question.question_id}: correct_option_id non coincide")

            option_keys = set()

            for option in question.opzioni:
                if not q52_clean(option.testo):
                    errors.append(f"{question.question_id}: opzione vuota")

                option_key = qg_normalize_for_compare(option.testo)

                if option_key in option_keys:
                    errors.append(f"{question.question_id}: opzione duplicata")
                option_keys.add(option_key)

                if not option.is_correct and option_key in source_keys:
                    errors.append(f"{question.question_id}: distrattore coincide con fact vero")

            if qg_normalize_for_compare(question.fatto_origine) not in source_keys:
                errors.append(f"{question.question_id}: fatto_origine non tracciabile nei facts")

        return errors

    except Exception as exc:
        return [f"PHASE5_QUIZ_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def q52_validate_phase4_for_study_quiz(
    gate_result: SuperQualityGateResult,
    config: Phase5StudyQuizConfig,
) -> List[str]:
    errors: List[str] = []

    try:
        if not config.require_phase4_study_quiz_not_blocked:
            return errors

        blocked_areas = list(getattr(gate_result, "blocked_areas", []) or [])

        if "study_questions" in blocked_areas:
            errors.append("PHASE5_CANNOT_BUILD_STUDY_PHASE4_BLOCKED_STUDY_QUESTIONS")

        if "quiz" in blocked_areas:
            errors.append("PHASE5_CANNOT_BUILD_QUIZ_PHASE4_BLOCKED_QUIZ")

        return errors

    except Exception as exc:
        return [f"PHASE5_STUDY_QUIZ_PHASE4_VALIDATION_EXCEPTION: {type(exc).__name__}: {exc}"]


def build_phase5_quality_study_quiz(
    gate_result: SuperQualityGateResult,
    output_result: Optional[OutputBuilderResult] = None,
    config: Optional[Phase5StudyQuizConfig] = None,
) -> Phase5QualityStudyQuizResult:
    """
    Funzione madre Fase 5.2.

    Collegamento:
    - input principale: SuperQualityGateResult.clean_output
    - output: domande studio finali + test quiz finale

    Nota:
    se la Fase 4 ha bloccato il quiz grezzo, questa fase può comunque
    ricostruire un quiz nuovo con distrattori falsi/plausibili.
    """

    cfg = config or Phase5StudyQuizConfig()

    result = Phase5QualityStudyQuizResult(
        document_id=q52_clean(getattr(gate_result, "document_id", "")) or "unknown_document",
    )

    try:
        result.errors.extend(q52_validate_phase4_for_study_quiz(gate_result, cfg))

        facts = q52_extract_facts(gate_result, output_result)
        concepts = q52_extract_concepts(gate_result)
        pages = q52_extract_pages(gate_result)

        if not facts:
            result.errors.append("PHASE5_STUDY_QUIZ_NO_FACTS_AVAILABLE")

        result.domande_studio = q52_build_quality_study_questions(
            facts=facts,
            preferred_concepts=concepts,
            pages=pages,
            config=cfg,
        )

        result.test_quiz = q52_build_quality_quiz(
            facts=facts,
            preferred_concepts=concepts,
            pages=pages,
            config=cfg,
        )

        result.errors.extend(q52_validate_study_questions(result.domande_studio))
        result.errors.extend(q52_validate_quiz(result.test_quiz, facts, cfg.quiz_options_count))

        if not result.domande_studio:
            result.errors.append("PHASE5_STUDY_QUESTIONS_EMPTY")

        if not result.test_quiz:
            result.errors.append("PHASE5_TEST_QUIZ_EMPTY")

        result.quality_report = {
            "facts_used": len(facts),
            "concepts_used": len(concepts),
            "study_questions_count": len(result.domande_studio),
            "quiz_questions_count": len(result.test_quiz),
            "source_pages": pages,
            "errors_count": len(result.errors),
            "warnings_count": len(result.warnings),
        }

        if result.errors:
            result.status = "NEEDS_REVIEW"
            result.approved = False
        else:
            result.status = "APPROVED"
            result.approved = True

        return result

    except Exception as exc:
        result.status = "ERROR"
        result.approved = False
        result.errors.append(f"PHASE5_STUDY_QUIZ_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def phase5_quality_study_quiz_result_to_dict(
    result: Phase5QualityStudyQuizResult,
) -> Dict[str, Any]:
    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "QUALITY_STUDY_QUIZ",
            "approved": False,
            "status": "SERIALIZATION_ERROR",
            "errors": ["PHASE5_STUDY_QUIZ_SERIALIZATION_FAILED"],
        }


def phase5_quality_study_quiz_result_to_json(
    result: Phase5QualityStudyQuizResult,
    indent: int = 2,
) -> str:
    try:
        return json.dumps(
            phase5_quality_study_quiz_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "QUALITY_STUDY_QUIZ",
                "approved": False,
                "status": "JSON_SERIALIZATION_ERROR",
                "errors": [f"PHASE5_STUDY_QUIZ_JSON_FAILED: {type(exc).__name__}: {exc}"],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 5.2 — Quality Study Questions Quiz V1
# =============================================================================
'''


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if REQUIRED_MARKER not in original:
            print("❌ Fase 5.1 non trovata. Patch annullata.")
            return 1

        if PATCH_MARKER in original:
            print("✅ FASE 5.2 QUALITY STUDY QUIZ V1 già presente. Nessuna modifica necessaria.")
            return 0

        backup = TARGET_FILE.with_suffix(".py.bak_phase5_study_quiz_v1")
        shutil.copy2(TARGET_FILE, backup)

        patched = original.rstrip() + "\n\n" + PATCH_CODE + "\n"
        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Patch FASE 5.2 QUALITY STUDY QUIZ V1 applicata con successo.")
        print(f"Backup creato: {backup}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore patch FASE 5.2: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
