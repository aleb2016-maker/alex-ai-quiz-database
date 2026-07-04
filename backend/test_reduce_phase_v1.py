# backend/test_reduce_phase_v1.py
# =============================================================================
# TEST FASE 2 — REDUCE V1
#
# Verifica:
# - uso dei MapChunkResult
# - esclusione chunk vuoti/falliti/bloccati
# - deduplica facts
# - conservazione causa-effetto
# - creazione MacroRawDocument
#
# Nessuna UI/CSS/pulsanti.
# =============================================================================

from __future__ import annotations

import sys
import traceback

from motori_scrittura import (
    MapChunkResult,
    MapPhaseOutput,
    RelationItem,
    TreeReduceConfig,
    run_tree_reduce_phase,
    tree_reduce_output_to_json,
)


def contains_all(text: str, terms: list[str]) -> bool:
    lowered = text.lower()
    return all(term.lower() in lowered for term in terms)


def run_test() -> int:
    try:
        map_output = MapPhaseOutput(
            document_id="test_reduce_phase_v1",
            total_chunks=5,
            processed_chunks=4,
            failed_chunks=1,
            blocked_chunks=1,
            results=[
                MapChunkResult(
                    chunk_id="chunk_001",
                    page_start=1,
                    page_end=1,
                    domain="technical",
                    facts=[
                        "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                        "Ogni account deve essere associato a una persona identificabile.",
                    ],
                    micro_concepts=[
                        "controllo accessi",
                        "account utente",
                    ],
                    entities=[
                        "sistemi interni",
                        "account",
                    ],
                    relations=[
                        RelationItem(
                            subject="controllo degli accessi",
                            predicate="limita",
                            object="utilizzo dei sistemi interni",
                            evidence="Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                        )
                    ],
                    processed=True,
                    blocked=False,
                ),
                MapChunkResult(
                    chunk_id="chunk_002",
                    page_start=2,
                    page_end=2,
                    domain="technical",
                    facts=[
                        "Le credenziali non devono essere condivise tra più operatori.",
                        "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
                    ],
                    micro_concepts=[
                        "credenziali",
                        "revisione periodica",
                        "permessi attivi",
                    ],
                    entities=[
                        "credenziali",
                        "operatori",
                        "accessi",
                    ],
                    relations=[
                        RelationItem(
                            subject="revisione periodica degli accessi",
                            predicate="riduce il rischio che",
                            object="utenti non più autorizzati mantengano permessi attivi",
                            evidence="La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
                        )
                    ],
                    processed=True,
                    blocked=False,
                ),
                # Duplicato intenzionale: deve essere deduplicato.
                MapChunkResult(
                    chunk_id="chunk_003",
                    page_start=3,
                    page_end=3,
                    domain="technical",
                    facts=[
                        "Le credenziali non devono essere condivise tra più operatori.",
                    ],
                    micro_concepts=[
                        "credenziali",
                    ],
                    entities=[
                        "operatori",
                    ],
                    relations=[],
                    processed=True,
                    blocked=False,
                ),
                # Chunk fallito: deve essere escluso.
                MapChunkResult(
                    chunk_id="chunk_failed",
                    page_start=4,
                    page_end=4,
                    domain="unknown",
                    facts=[],
                    micro_concepts=[],
                    entities=[],
                    relations=[],
                    warnings=["CHUNK_TEXT_EMPTY"],
                    errors=["MAP_SKIPPED_EMPTY_CHUNK"],
                    processed=False,
                    blocked=False,
                ),
                # Chunk bloccato: deve essere escluso.
                MapChunkResult(
                    chunk_id="chunk_blocked",
                    page_start=5,
                    page_end=5,
                    domain="technical",
                    facts=[
                        "Il testo contiene la stringa demo sicurezza informatica aziendale."
                    ],
                    micro_concepts=[
                        "contenuto demo"
                    ],
                    entities=[
                        "documento di esempio"
                    ],
                    relations=[],
                    warnings=["EXTRACTION_CONTAINS_DEMO_OR_FALLBACK_SIGNATURES"],
                    errors=[],
                    processed=True,
                    blocked=True,
                ),
            ],
        )

        reduce_output = run_tree_reduce_phase(
            map_output=map_output,
            config=TreeReduceConfig(
                group_size=2,
                max_levels=10,
            ),
        )

        print(tree_reduce_output_to_json(reduce_output))

        errors: list[str] = []

        if reduce_output.total_map_results != 5:
            errors.append(f"Attesi 5 map results, trovati {reduce_output.total_map_results}")

        if reduce_output.usable_map_results != 3:
            errors.append(f"Attesi 3 usable map results, trovati {reduce_output.usable_map_results}")

        if reduce_output.skipped_map_results != 2:
            errors.append(f"Attesi 2 skipped map results, trovati {reduce_output.skipped_map_results}")

        if reduce_output.root_group is None:
            errors.append("root_group non creato")

        if reduce_output.macro_document is None:
            errors.append("macro_document non creato")
        else:
            macro = reduce_output.macro_document
            facts_text = "\n".join(macro.global_facts).lower()
            relations_text = "\n".join(
                [
                    f"{r.get('subject', '')} {r.get('predicate', '')} {r.get('object', '')} {r.get('evidence', '')}"
                    for r in macro.global_relations
                ]
            ).lower()

            if not macro.global_facts:
                errors.append("macro.global_facts vuoto")

            if not macro.section_blocks:
                errors.append("macro.section_blocks vuoto")

            if not contains_all(
                facts_text,
                ["revisione", "periodica", "accessi", "riduce", "rischio"],
            ):
                errors.append("Il fatto causa-effetto sulla revisione periodica è stato perso nei global_facts")

            if not contains_all(
                relations_text,
                ["revisione", "periodica", "accessi", "riduce", "rischio"],
            ):
                errors.append("La relation causa-effetto sulla revisione periodica è stata persa nei global_relations")

            if "sicurezza informatica aziendale" in facts_text:
                errors.append("Il chunk demo/fallback bloccato è entrato nel macro documento")

            count_credenziali = facts_text.count("le credenziali non devono essere condivise")
            if count_credenziali != 1:
                errors.append(
                    f"Deduplica facts non corretta: frase credenziali presente {count_credenziali} volte"
                )

            coverage = macro.coverage_report
            if coverage.get("usable_map_results") != 3:
                errors.append("coverage_report usable_map_results non corretto")

            if coverage.get("skipped_map_results") != 2:
                errors.append("coverage_report skipped_map_results non corretto")

        if errors:
            print("\n❌ TEST REDUCE PHASE V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST REDUCE PHASE V1 PASSATO")
        print("La Fase 2 REDUCE crea un macro-grezzo strutturato, deduplicato e tracciabile.")
        return 0

    except Exception as exc:
        print("\n❌ TEST REDUCE PHASE V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())