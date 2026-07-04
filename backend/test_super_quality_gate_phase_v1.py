# backend/test_super_quality_gate_phase_v1.py
# =============================================================================
# TEST FASE 4 — SUPER QUALITY GATE V1
#
# Verifica:
# - prende output della Fase 3
# - produce clean_output
# - conserva summary/card/study/study_pack
# - blocca il quiz grezzo perché i distrattori sono facts veri
# - non tocca UI/CSS/pulsanti
# =============================================================================

from __future__ import annotations

import sys
import traceback

from motori_scrittura import (
    MacroRawDocument,
    MacroRawSection,
    OutputBuilderConfig,
    SuperQualityGateConfig,
    build_output_drafts,
    run_super_quality_gate,
    super_quality_gate_result_to_json,
)


def issue_ids(result) -> list[str]:
    return [issue.issue_id for issue in result.issues]


def run_test() -> int:
    try:
        macro = MacroRawDocument(
            document_id="test_super_quality_gate_phase_v1",
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

        phase3_output = build_output_drafts(
            macro_document=macro,
            config=OutputBuilderConfig(
                max_summary_facts=20,
                max_cards=10,
                max_study_questions=10,
                max_quiz_questions=5,
                max_study_pack_sections=10,
            ),
        )

        gate = run_super_quality_gate(
            output_result=phase3_output,
            config=SuperQualityGateConfig(
                block_on_quiz_all_source_facts=True,
            ),
        )

        print(super_quality_gate_result_to_json(gate))

        errors: list[str] = []

        if gate.phase_name != "SUPER_QUALITY_GATE":
            errors.append(f"phase_name errato: {gate.phase_name}")

        if gate.errors:
            errors.append(f"Il quality gate non dovrebbe avere errors tecnici: {gate.errors}")

        # In questo test NON vogliamo approved=True.
        # Vogliamo dimostrare che il gate blocca il quiz grezzo della Fase 3.
        if gate.approved:
            errors.append("Il gate non dovrebbe approvare output con quiz grezzo e distrattori veri.")

        if gate.status != "BLOCKED":
            errors.append(f"Atteso status BLOCKED, trovato {gate.status}")

        if "quiz" not in gate.blocked_areas:
            errors.append(f"Il quiz dovrebbe essere in blocked_areas, trovate: {gate.blocked_areas}")

        ids = issue_ids(gate)

        if "QUIZ_DISTRACTORS_ARE_SOURCE_FACTS" not in ids:
            errors.append("Manca issue QUIZ_DISTRACTORS_ARE_SOURCE_FACTS")

        if not gate.clean_output:
            errors.append("clean_output mancante")

        summary = gate.clean_output.get("summary", {})
        if not summary.get("key_points"):
            errors.append("clean_output.summary.key_points vuoto")

        cards = gate.clean_output.get("cards", [])
        if not cards:
            errors.append("clean_output.cards vuoto")

        study_questions = gate.clean_output.get("study_questions", [])
        if not study_questions:
            errors.append("clean_output.study_questions vuoto")

        study_pack = gate.clean_output.get("study_pack", {})
        if not study_pack.get("sections"):
            errors.append("clean_output.study_pack.sections vuoto")

        report = gate.quality_report

        if report.get("blockers_count", 0) < 1:
            errors.append("quality_report dovrebbe avere almeno 1 blocker")

        if report.get("quiz_questions_count") != 4:
            errors.append(
                f"quality_report quiz_questions_count atteso 4, trovato {report.get('quiz_questions_count')}"
            )

        if errors:
            print("\n❌ TEST SUPER QUALITY GATE PHASE V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST SUPER QUALITY GATE PHASE V1 PASSATO")
        print("La Fase 4 intercetta il quiz grezzo, conserva gli output puliti e marca le aree bloccate.")
        return 0

    except Exception as exc:
        print("\n❌ TEST SUPER QUALITY GATE PHASE V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())