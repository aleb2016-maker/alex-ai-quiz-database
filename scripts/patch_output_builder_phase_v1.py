# scripts/patch_output_builder_phase_v1.py
# =============================================================================
# PATCH OUTPUT BUILDER PHASE V1
#
# Modifica SOLO backend:
# - target: backend/motori_scrittura.py
# - aggiunge Fase 3 OUTPUT BUILDER V1
# - nessuna modifica a UI, CSS, pulsanti o grafica
#
# Fase 3 V1:
# - prende MacroRawDocument dalla REDUCE
# - genera bozze strutturate:
#   summary_draft
#   cards_draft
#   study_questions_draft
#   quiz_draft
#   study_pack_draft
#
# Non fa Super Quality Gate.
# Non riscrive in stile finale.
# Non tocca la UI.
# =============================================================================

from __future__ import annotations

import shutil
import sys
from pathlib import Path


TARGET_FILE = Path("backend/motori_scrittura.py")
PATCH_MARKER = "FASE 3 — OUTPUT BUILDER V1"


OUTPUT_BUILDER_CODE = r'''

# =============================================================================
# FASE 3 — OUTPUT BUILDER V1
# RAG GERARCHICO MAP-REDUCE AD ALBERO
#
# Obiettivo:
# - prendere il MacroRawDocument della Fase 2 REDUCE
# - generare bozze strutturate di output
#
# Questa fase NON deve:
# - applicare il Super Quality Gate finale
# - fare rifinitura linguistica forte
# - toccare UI/CSS/pulsanti
# - generare HTML, card grafiche o layout
#
# Output prodotti:
# - summary_draft
# - cards_draft
# - study_questions_draft
# - quiz_draft
# - study_pack_draft
# =============================================================================


@dataclass
class OutputBuilderConfig:
    """
    Configurazione universale della Fase 3.

    Tutti i limiti sono parametrici.
    Nessun valore è legato a un documento specifico.
    """

    max_summary_facts: int = 30
    max_cards: int = 12
    max_study_questions: int = 12
    max_quiz_questions: int = 8
    max_study_pack_sections: int = 20
    max_fact_chars: int = 500
    min_quiz_options: int = 4
    include_source_pages: bool = True


@dataclass
class SummaryDraft:
    """
    Bozza di riassunto.

    Non è ancora il testo finale elegante.
    È una struttura ordinata basata sui fatti consolidati.
    """

    title: str
    key_points: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    source_facts_count: int = 0
    warnings: List[str] = field(default_factory=list)


@dataclass
class CardDraft:
    """
    Bozza testuale di una card.

    Non contiene grafica, CSS, layout o pulsanti.
    """

    card_id: str
    title: str
    message_key: str
    source_facts: List[str] = field(default_factory=list)
    micro_concepts: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StudyQuestionDraft:
    """
    Bozza di domanda studio.

    La Fase 4 potrà poi rifinire tono, fluidità e qualità didattica.
    """

    question_id: str
    question: str
    answer_guide: str
    source_facts: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class QuizOptionDraft:
    """
    Opzione bozza per quiz.

    Non è ancora validazione finale dei distrattori forti.
    """

    option_id: str
    text: str
    is_correct: bool = False


@dataclass
class QuizQuestionDraft:
    """
    Bozza di domanda quiz.

    La Fase 4 o un validatore quiz dedicato controllerà:
    - distrattori forti
    - naturalezza
    - non ambiguità
    - spiegazione finale
    """

    question_id: str
    question: str
    options: List[QuizOptionDraft] = field(default_factory=list)
    correct_option_id: str = ""
    explanation_draft: str = ""
    source_facts: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StudyPackSectionDraft:
    """
    Sezione bozza dello study pack.
    """

    section_id: str
    title: str
    key_facts: List[str] = field(default_factory=list)
    micro_concepts: List[str] = field(default_factory=list)
    entities: List[str] = field(default_factory=list)
    source_pages: List[int] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class StudyPackDraft:
    """
    Bozza study pack.

    Non è ancora libro bianco finale.
    È una struttura ordinata pronta per il Super Quality Gate.
    """

    title: str
    sections: List[StudyPackSectionDraft] = field(default_factory=list)
    global_micro_concepts: List[str] = field(default_factory=list)
    global_entities: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


@dataclass
class OutputBuilderResult:
    """
    Output complessivo della Fase 3.
    """

    document_id: str
    phase_name: str = "OUTPUT_BUILDER"

    summary_draft: Optional[SummaryDraft] = None
    cards_draft: List[CardDraft] = field(default_factory=list)
    study_questions_draft: List[StudyQuestionDraft] = field(default_factory=list)
    quiz_draft: List[QuizQuestionDraft] = field(default_factory=list)
    study_pack_draft: Optional[StudyPackDraft] = None

    input_global_facts_count: int = 0
    input_sections_count: int = 0

    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


def output_trim_text(text: Any, max_chars: int = 500) -> str:
    """
    Taglio prudente di testo troppo lungo.

    Non riscrive.
    Non abbellisce.
    Serve solo a evitare bozze ingestibili.
    """

    try:
        value = normalize_text(text)
        if max_chars <= 0:
            return value

        if len(value) <= max_chars:
            return value

        return value[:max_chars].rstrip() + "..."

    except Exception:
        return ""


def output_make_title_from_fact(fact: str, fallback: str, max_words: int = 8) -> str:
    """
    Crea un titolo tecnico breve da un fatto.

    Non è titolo grafico finale.
    """

    try:
        text = normalize_text(fact).rstrip(".")
        words = text.split()

        if not words:
            return fallback

        title = " ".join(words[:max_words]).strip()

        if len(words) > max_words:
            title += "..."

        return title[0].upper() + title[1:] if title else fallback

    except Exception:
        return fallback


def output_collect_macro_pages(macro_document: MacroRawDocument) -> List[int]:
    """
    Raccoglie pagine dalle sezioni macro.
    """

    pages: List[int] = []

    try:
        for section in getattr(macro_document, "section_blocks", []) or []:
            for page in getattr(section, "source_pages", []) or []:
                try:
                    pages.append(int(page))
                except Exception:
                    pass

        return sorted(set(pages))

    except Exception:
        return []


def output_get_global_facts(macro_document: MacroRawDocument) -> List[str]:
    """
    Recupera facts globali deduplicati.
    """

    try:
        return reduce_unique_strings(getattr(macro_document, "global_facts", []) or [])
    except Exception:
        return []


def output_get_global_concepts(macro_document: MacroRawDocument) -> List[str]:
    """
    Recupera micro-concepts globali deduplicati.
    """

    try:
        return reduce_unique_strings(getattr(macro_document, "global_micro_concepts", []) or [])
    except Exception:
        return []


def output_get_global_entities(macro_document: MacroRawDocument) -> List[str]:
    """
    Recupera entities globali deduplicate.
    """

    try:
        return reduce_unique_strings(getattr(macro_document, "global_entities", []) or [])
    except Exception:
        return []


def build_summary_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> SummaryDraft:
    """
    Costruisce una bozza di riassunto.

    Importante:
    - non produce prosa finale elegante
    - non fonde tutto in un testo lungo
    - conserva punti chiave ordinati
    """

    cfg = config or OutputBuilderConfig()

    draft = SummaryDraft(
        title="Bozza riassunto macro-grezzo",
    )

    try:
        facts = output_get_global_facts(macro_document)
        pages = output_collect_macro_pages(macro_document)

        selected_facts = facts[: max(0, cfg.max_summary_facts)]

        draft.key_points = [
            output_trim_text(fact, cfg.max_fact_chars)
            for fact in selected_facts
            if normalize_text(fact)
        ]

        draft.source_pages = pages if cfg.include_source_pages else []
        draft.source_facts_count = len(facts)

        if not draft.key_points:
            draft.warnings.append("SUMMARY_DRAFT_NO_KEY_POINTS")

        if len(facts) > len(draft.key_points):
            draft.warnings.append(
                f"SUMMARY_DRAFT_TRUNCATED_FACTS: selected={len(draft.key_points)} total={len(facts)}"
            )

        return draft

    except Exception as exc:
        draft.warnings.append(f"SUMMARY_DRAFT_EXCEPTION: {type(exc).__name__}: {exc}")
        return draft


def build_cards_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> List[CardDraft]:
    """
    Costruisce bozze card testuali.

    Non genera grafica.
    Non genera CSS.
    Non genera layout.
    """

    cfg = config or OutputBuilderConfig()
    cards: List[CardDraft] = []

    try:
        sections = list(getattr(macro_document, "section_blocks", []) or [])
        global_concepts = output_get_global_concepts(macro_document)

        for index, section in enumerate(sections[: max(0, cfg.max_cards)], start=1):
            section_facts = reduce_unique_strings(getattr(section, "facts", []) or [])
            section_concepts = reduce_unique_strings(getattr(section, "micro_concepts", []) or [])

            if not section_facts and not section_concepts:
                continue

            main_fact = section_facts[0] if section_facts else ""
            title_source = section_concepts[0] if section_concepts else main_fact

            card = CardDraft(
                card_id=f"card_draft_{index:03d}",
                title=output_make_title_from_fact(
                    title_source,
                    fallback=f"Card bozza {index}",
                    max_words=6,
                ),
                message_key=output_trim_text(main_fact or title_source, cfg.max_fact_chars),
                source_facts=[
                    output_trim_text(fact, cfg.max_fact_chars)
                    for fact in section_facts[:5]
                ],
                micro_concepts=section_concepts[:8] or global_concepts[:8],
                source_pages=list(getattr(section, "source_pages", []) or []) if cfg.include_source_pages else [],
            )

            if not card.message_key:
                card.warnings.append("CARD_DRAFT_EMPTY_MESSAGE_KEY")

            cards.append(card)

        if not cards:
            facts = output_get_global_facts(macro_document)

            for index, fact in enumerate(facts[: max(0, cfg.max_cards)], start=1):
                card = CardDraft(
                    card_id=f"card_draft_{index:03d}",
                    title=output_make_title_from_fact(fact, fallback=f"Card bozza {index}", max_words=6),
                    message_key=output_trim_text(fact, cfg.max_fact_chars),
                    source_facts=[output_trim_text(fact, cfg.max_fact_chars)],
                    micro_concepts=global_concepts[:8],
                    source_pages=output_collect_macro_pages(macro_document) if cfg.include_source_pages else [],
                )
                cards.append(card)

        return cards

    except Exception:
        return cards


def build_study_questions_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> List[StudyQuestionDraft]:
    """
    Costruisce bozze di domande studio.

    Non è ancora quality gate didattico finale.
    """

    cfg = config or OutputBuilderConfig()
    questions: List[StudyQuestionDraft] = []

    try:
        facts = output_get_global_facts(macro_document)
        pages = output_collect_macro_pages(macro_document)

        for index, fact in enumerate(facts[: max(0, cfg.max_study_questions)], start=1):
            trimmed_fact = output_trim_text(fact, cfg.max_fact_chars)
            short_title = output_make_title_from_fact(trimmed_fact, fallback="questo punto", max_words=7)

            question = StudyQuestionDraft(
                question_id=f"study_question_draft_{index:03d}",
                question=f"Quale regola o informazione emerge da: {short_title}?",
                answer_guide=trimmed_fact,
                source_facts=[trimmed_fact],
                source_pages=pages if cfg.include_source_pages else [],
            )

            questions.append(question)

        return questions

    except Exception:
        return questions


def build_quiz_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> List[QuizQuestionDraft]:
    """
    Costruisce bozze quiz da fatti reali.

    Regola:
    - non inventa distrattori fuori documento
    - usa altri facts come opzioni alternative
    - se non ci sono abbastanza facts, non forza quiz finto
    """

    cfg = config or OutputBuilderConfig()
    quiz: List[QuizQuestionDraft] = []

    try:
        facts = output_get_global_facts(macro_document)
        pages = output_collect_macro_pages(macro_document)

        if len(facts) < cfg.min_quiz_options:
            return quiz

        max_questions = min(max(0, cfg.max_quiz_questions), len(facts))

        option_ids = ["A", "B", "C", "D"]

        for index in range(max_questions):
            correct_fact = output_trim_text(facts[index], cfg.max_fact_chars)

            distractor_pool = [
                output_trim_text(fact, cfg.max_fact_chars)
                for pos, fact in enumerate(facts)
                if pos != index
            ]

            if len(distractor_pool) < 3:
                continue

            correct_position = index % 4
            raw_options = distractor_pool[:3]
            raw_options.insert(correct_position, correct_fact)

            options: List[QuizOptionDraft] = []

            for option_index, option_text in enumerate(raw_options[:4]):
                option_id = option_ids[option_index]
                options.append(
                    QuizOptionDraft(
                        option_id=option_id,
                        text=option_text,
                        is_correct=(option_index == correct_position),
                    )
                )

            correct_option_id = option_ids[correct_position]

            question = QuizQuestionDraft(
                question_id=f"quiz_question_draft_{index + 1:03d}",
                question="Quale affermazione è supportata dal documento?",
                options=options,
                correct_option_id=correct_option_id,
                explanation_draft=correct_fact,
                source_facts=[correct_fact],
                source_pages=pages if cfg.include_source_pages else [],
            )

            if len(options) != 4:
                question.warnings.append("QUIZ_DRAFT_OPTIONS_COUNT_NOT_4")

            quiz.append(question)

        return quiz

    except Exception:
        return quiz


def build_study_pack_draft(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> StudyPackDraft:
    """
    Costruisce bozza study pack.

    Usa le section_blocks della REDUCE.
    Non produce ancora testo finale da libro bianco.
    """

    cfg = config or OutputBuilderConfig()

    draft = StudyPackDraft(
        title="Bozza study pack macro-grezzo",
    )

    try:
        sections = list(getattr(macro_document, "section_blocks", []) or [])

        for index, section in enumerate(sections[: max(0, cfg.max_study_pack_sections)], start=1):
            section_draft = StudyPackSectionDraft(
                section_id=normalize_text(getattr(section, "section_id", "")) or f"study_pack_section_{index:03d}",
                title=normalize_text(getattr(section, "title", "")) or f"Sezione bozza {index}",
                key_facts=[
                    output_trim_text(fact, cfg.max_fact_chars)
                    for fact in reduce_unique_strings(getattr(section, "facts", []) or [])
                ],
                micro_concepts=reduce_unique_strings(getattr(section, "micro_concepts", []) or []),
                entities=reduce_unique_strings(getattr(section, "entities", []) or []),
                source_pages=list(getattr(section, "source_pages", []) or []) if cfg.include_source_pages else [],
            )

            if not section_draft.key_facts:
                section_draft.warnings.append("STUDY_PACK_SECTION_NO_FACTS")

            draft.sections.append(section_draft)

        draft.global_micro_concepts = output_get_global_concepts(macro_document)
        draft.global_entities = output_get_global_entities(macro_document)

        if not draft.sections:
            draft.warnings.append("STUDY_PACK_DRAFT_NO_SECTIONS")

        return draft

    except Exception as exc:
        draft.warnings.append(f"STUDY_PACK_DRAFT_EXCEPTION: {type(exc).__name__}: {exc}")
        return draft


def build_output_drafts(
    macro_document: MacroRawDocument,
    config: Optional[OutputBuilderConfig] = None,
) -> OutputBuilderResult:
    """
    Funzione madre Fase 3 — OUTPUT BUILDER.

    Input:
    - MacroRawDocument prodotto da REDUCE

    Output:
    - OutputBuilderResult con bozze strutturate

    Questa funzione non chiama LLM.
    È deterministica e protetta.
    """

    cfg = config or OutputBuilderConfig()

    result = OutputBuilderResult(
        document_id=normalize_text(getattr(macro_document, "document_id", "")) or "unknown_document",
    )

    try:
        facts = output_get_global_facts(macro_document)
        sections = list(getattr(macro_document, "section_blocks", []) or [])

        result.input_global_facts_count = len(facts)
        result.input_sections_count = len(sections)

        if not facts:
            result.warnings.append("OUTPUT_BUILDER_NO_GLOBAL_FACTS")

        if not sections:
            result.warnings.append("OUTPUT_BUILDER_NO_SECTION_BLOCKS")

        result.summary_draft = build_summary_draft(macro_document, cfg)
        result.cards_draft = build_cards_draft(macro_document, cfg)
        result.study_questions_draft = build_study_questions_draft(macro_document, cfg)
        result.quiz_draft = build_quiz_draft(macro_document, cfg)
        result.study_pack_draft = build_study_pack_draft(macro_document, cfg)

        if not result.cards_draft:
            result.warnings.append("OUTPUT_BUILDER_NO_CARDS_DRAFT")

        if not result.study_questions_draft:
            result.warnings.append("OUTPUT_BUILDER_NO_STUDY_QUESTIONS_DRAFT")

        if not result.quiz_draft:
            result.warnings.append("OUTPUT_BUILDER_NO_QUIZ_DRAFT")

        return result

    except Exception as exc:
        result.errors.append(f"OUTPUT_BUILDER_EXCEPTION: {type(exc).__name__}: {exc}")
        result.warnings.append(traceback.format_exc(limit=5))
        return result


def output_builder_result_to_dict(result: OutputBuilderResult) -> Dict[str, Any]:
    """
    Serializza OutputBuilderResult in dict.
    """

    try:
        return asdict(result)
    except Exception:
        return {
            "document_id": getattr(result, "document_id", "unknown_document"),
            "phase_name": "OUTPUT_BUILDER",
            "errors": ["OUTPUT_BUILDER_RESULT_SERIALIZATION_FAILED"],
        }


def output_builder_result_to_json(result: OutputBuilderResult, indent: int = 2) -> str:
    """
    Serializza OutputBuilderResult in JSON.
    """

    try:
        return json.dumps(
            output_builder_result_to_dict(result),
            ensure_ascii=False,
            indent=indent,
        )
    except Exception as exc:
        return json.dumps(
            {
                "document_id": getattr(result, "document_id", "unknown_document"),
                "phase_name": "OUTPUT_BUILDER",
                "errors": [
                    f"OUTPUT_BUILDER_JSON_SERIALIZATION_FAILED: {type(exc).__name__}: {exc}"
                ],
            },
            ensure_ascii=False,
            indent=indent,
        )

# =============================================================================
# Fine Fase 3 — OUTPUT BUILDER V1
# =============================================================================
'''


def main() -> int:
    try:
        if not TARGET_FILE.exists():
            print(f"❌ File non trovato: {TARGET_FILE}")
            return 1

        original = TARGET_FILE.read_text(encoding="utf-8")

        if PATCH_MARKER in original:
            print("✅ OUTPUT BUILDER V1 già presente. Nessuna modifica necessaria.")
            return 0

        backup = TARGET_FILE.with_suffix(".py.bak_output_builder_phase_v1")
        shutil.copy2(TARGET_FILE, backup)

        patched = original.rstrip() + "\n\n" + OUTPUT_BUILDER_CODE + "\n"

        TARGET_FILE.write_text(patched, encoding="utf-8")

        print("✅ Patch OUTPUT BUILDER PHASE V1 applicata con successo.")
        print(f"Backup creato: {backup}")
        print(f"File aggiornato: {TARGET_FILE}")
        return 0

    except Exception as exc:
        print(f"❌ Errore patch OUTPUT BUILDER PHASE V1: {type(exc).__name__}: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main())