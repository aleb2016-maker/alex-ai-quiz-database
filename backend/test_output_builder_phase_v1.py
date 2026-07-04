# backend/test_output_builder_phase_v1.py
# =============================================================================
# TEST FASE 3 — OUTPUT BUILDER V1
#
# Verifica:
# - costruzione SummaryDraft
# - costruzione CardDraft
# - costruzione StudyQuestionDraft
# - costruzione QuizDraft
# - costruzione StudyPackDraft
# - conservazione fatto causa-effetto
#
# Nessuna UI/CSS/pulsanti.
# =============================================================================

from __future__ import annotations

import sys
import traceback

from motori_scrittura import (
    MacroRawDocument,
    MacroRawSection,
    OutputBuilderConfig,
    build_output_drafts,
    output_builder_result_to_json,
)


def contains_all(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def run_test() -> int:
    try:
        macro = MacroRawDocument(
            document_id="test_output_builder_phase_v1",
            domain_profile=["technical"],
            section_blocks=[
                MacroRawSection(
                    section_id="section_001",
                    title="Blocco 1 — pagine 1-2",
                    source_chunk_ids=["chunk_001", "chunk_002"],
                    source_pages=[1, 2],
                    facts=[
                        "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                        "Ogni account deve essere associato a una persona identificabile.",
                        "Le credenziali non devono essere condivise tra più operatori.",
                        "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
                    ],
                    micro_concepts=[
                        "controllo accessi",
                        "account utente",
                        "credenziali",
                        "revisione periodica",
                    ],
                    entities=[
                        "sistemi interni",
                        "account",
                        "credenziali",
                        "accessi",
                    ],
                    relations=[
                        {
                            "subject": "revisione periodica degli accessi",
                            "predicate": "riduce il rischio che",
                            "object": "utenti non più autorizzati mantengano permessi attivi",
                            "evidence": "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
                            "source_chunk_ids": ["chunk_002"],
                            "source_pages": [2],
                            "support_count": 1,
                        }
                    ],
                )
            ],
            global_facts=[
                "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                "Ogni account deve essere associato a una persona identificabile.",
                "Le credenziali non devono essere condivise tra più operatori.",
                "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
            ],
            global_micro_concepts=[
                "controllo accessi",
                "account utente",
                "credenziali",
                "revisione periodica",
                "permessi attivi",
            ],
            global_entities=[
                "sistemi interni",
                "account",
                "credenziali",
                "operatori",
                "accessi",
            ],
            global_relations=[
                {
                    "subject": "revisione periodica degli accessi",
                    "predicate": "riduce il rischio che",
                    "object": "utenti non più autorizzati mantengano permessi attivi",
                    "evidence": "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
                    "source_chunk_ids": ["chunk_002"],
                    "source_pages": [2],
                    "support_count": 1,
                }
            ],
            coverage_report={
                "total_map_results": 3,
                "usable_map_results": 3,
                "skipped_map_results": 0,
                "global_facts_count": 4,
                "global_relations_count": 1,
            },
        )

        output = build_output_drafts(
            macro_document=macro,
            config=OutputBuilderConfig(
                max_summary_facts=20,
                max_cards=10,
                max_study_questions=10,
                max_quiz_questions=5,
                max_study_pack_sections=10,
            ),
        )

        print(output_builder_result_to_json(output))

        errors: list[str] = []

        if output.phase_name != "OUTPUT_BUILDER":
            errors.append(f"phase_name errato: {output.phase_name}")

        if output.errors:
            errors.append(f"Output builder non dovrebbe avere errors: {output.errors}")

        if output.input_global_facts_count != 4:
            errors.append(f"Attesi 4 facts input, trovati {output.input_global_facts_count}")

        if output.input_sections_count != 1:
            errors.append(f"Attesa 1 section input, trovate {output.input_sections_count}")

        if output.summary_draft is None:
            errors.append("summary_draft mancante")
        else:
            summary_text = "\n".join(output.summary_draft.key_points)
            if not contains_all(summary_text, ["revisione", "periodica", "riduce", "rischio"]):
                errors.append("summary_draft non conserva il fatto causa-effetto sulla revisione periodica")

        if not output.cards_draft:
            errors.append("cards_draft vuoto")
        else:
            cards_text = "\n".join(
                [card.message_key + " " + " ".join(card.source_facts) for card in output.cards_draft]
            )
            if not contains_all(cards_text, ["controllo", "accessi"]):
                errors.append("cards_draft non conserva il tema controllo accessi")

        if not output.study_questions_draft:
            errors.append("study_questions_draft vuoto")
        else:
            questions_text = "\n".join(
                [q.question + " " + q.answer_guide for q in output.study_questions_draft]
            )
            if not contains_all(questions_text, ["credenziali", "condivise"]):
                errors.append("study_questions_draft non conserva il divieto sulle credenziali")

        if not output.quiz_draft:
            errors.append("quiz_draft vuoto, ma con 4 facts dovrebbe produrre almeno una domanda")
        else:
            first_quiz = output.quiz_draft[0]
            if len(first_quiz.options) != 4:
                errors.append(f"La prima domanda quiz dovrebbe avere 4 opzioni, trovate {len(first_quiz.options)}")

            correct_options = [opt for opt in first_quiz.options if opt.is_correct]
            if len(correct_options) != 1:
                errors.append("La prima domanda quiz dovrebbe avere esattamente 1 opzione corretta")

        if output.study_pack_draft is None:
            errors.append("study_pack_draft mancante")
        else:
            if not output.study_pack_draft.sections:
                errors.append("study_pack_draft.sections vuoto")

            pack_text = "\n".join(
                [
                    section.title + " " + " ".join(section.key_facts)
                    for section in output.study_pack_draft.sections
                ]
            )
            if not contains_all(pack_text, ["revisione", "periodica", "rischio"]):
                errors.append("study_pack_draft non conserva il fatto sulla revisione periodica")

        if errors:
            print("\n❌ TEST OUTPUT BUILDER PHASE V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST OUTPUT BUILDER PHASE V1 PASSATO")
        print("La Fase 3 genera bozze strutturate per riassunto, card, domande, quiz e study pack.")
        return 0

    except Exception as exc:
        print("\n❌ TEST OUTPUT BUILDER PHASE V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())