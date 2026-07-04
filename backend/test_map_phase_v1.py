# backend/test_map_phase_v1.py
# =============================================================================
# TEST FASE 1 — MAP
#
# Verifica 3 casi:
# 1. chunk normale
# 2. chunk vuoto
# 3. chunk con stringa demo/fallback
#
# Questo file NON tocca UI, CSS, pulsanti o grafica.
# Serve solo a validare il backend MAP.
# =============================================================================

from __future__ import annotations

import json
import sys
import traceback
from typing import Any, Dict, Optional

from motori_scrittura import (
    ChunkInput,
    MapPhaseConfig,
    run_map_phase,
    map_phase_output_to_json,
)


class ControlledMapMockLLM:
    """
    Mock LLM controllato per testare la Fase MAP.

    Non simula qualità reale.
    Serve solo a verificare:
    - chunk normale processato
    - chunk vuoto saltato
    - demo/fallback rilevato e bloccato
    """

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        chunk_id = ""
        if metadata:
            chunk_id = str(metadata.get("chunk_id", ""))

        # Caso 3: simuliamo un LLM che restituisce anche una stringa demo/fallback.
        # Questo deve attivare il controllo EXTRACTION_CONTAINS_DEMO_OR_FALLBACK_SIGNATURES.
        if chunk_id == "chunk_demo_fallback":
            return json.dumps(
                {
                    "domain": "technical",
                    "facts": [
                        "Il testo contiene la stringa demo sicurezza informatica aziendale."
                    ],
                    "micro_concepts": [
                        "sicurezza informatica aziendale",
                        "contenuto demo"
                    ],
                    "entities": [
                        "documento di esempio"
                    ],
                    "relations": [
                        {
                            "subject": "contenuto demo",
                            "predicate": "contamina",
                            "object": "estrazione MAP",
                            "evidence": "sicurezza informatica aziendale"
                        }
                    ],
                },
                ensure_ascii=False,
            )

        # Caso 1: chunk normale.
        return json.dumps(
            {
                "domain": "technical",
                "facts": [
                    "Il controllo degli accessi limita l'utilizzo dei sistemi aziendali agli utenti autorizzati.",
                    "Le credenziali devono essere protette.",
                    "Le credenziali devono essere aggiornate periodicamente."
                ],
                "micro_concepts": [
                    "controllo accessi",
                    "utenti autorizzati",
                    "protezione credenziali",
                    "aggiornamento credenziali"
                ],
                "entities": [
                    "sistemi aziendali",
                    "utenti autorizzati",
                    "credenziali"
                ],
                "relations": [
                    {
                        "subject": "controllo degli accessi",
                        "predicate": "limita",
                        "object": "utilizzo dei sistemi aziendali",
                        "evidence": "Il controllo degli accessi limita l'utilizzo dei sistemi aziendali agli utenti autorizzati."
                    },
                    {
                        "subject": "credenziali",
                        "predicate": "devono essere",
                        "object": "protette e aggiornate periodicamente",
                        "evidence": "Le credenziali devono essere protette e aggiornate periodicamente."
                    }
                ],
            },
            ensure_ascii=False,
        )


def assert_contains(values, expected_substring: str) -> bool:
    """
    Controlla se una lista di stringhe contiene una sottostringa.
    """
    joined = "\n".join(str(v) for v in values)
    return expected_substring in joined


def run_test() -> int:
    """
    Esegue il test MAP V1.
    Ritorna:
    - 0 se passa
    - 1 se fallisce
    """

    try:
        chunks = [
            ChunkInput(
                chunk_id="chunk_normale",
                text=(
                    "Il controllo degli accessi limita l'utilizzo dei sistemi aziendali "
                    "agli utenti autorizzati. Le credenziali devono essere protette "
                    "e aggiornate periodicamente."
                ),
                page_start=1,
                page_end=1,
            ),
            ChunkInput(
                chunk_id="chunk_vuoto",
                text="",
                page_start=2,
                page_end=2,
            ),
            ChunkInput(
                chunk_id="chunk_demo_fallback",
                text=(
                    "Questo chunk contiene una stringa da bloccare: "
                    "sicurezza informatica aziendale. "
                    "Serve a testare il controllo anti-fallback leggero."
                ),
                page_start=3,
                page_end=3,
            ),
        ]

        output = run_map_phase(
            document_id="test_map_phase_v1",
            chunks=chunks,
            llm_client=ControlledMapMockLLM(),
            config=MapPhaseConfig(
                domain_hint="technical",
            ),
        )

        print(map_phase_output_to_json(output))

        results_by_id = {
            result.chunk_id: result
            for result in output.results
        }

        normale = results_by_id.get("chunk_normale")
        vuoto = results_by_id.get("chunk_vuoto")
        demo = results_by_id.get("chunk_demo_fallback")

        errors = []

        # ---------------------------------------------------------------------
        # Controllo generale
        # ---------------------------------------------------------------------
        if output.total_chunks != 3:
            errors.append(f"Attesi 3 chunk, trovati {output.total_chunks}")

        if output.processed_chunks != 2:
            errors.append(f"Attesi 2 chunk processati, trovati {output.processed_chunks}")

        if output.failed_chunks != 1:
            errors.append(f"Atteso 1 chunk fallito/saltato, trovati {output.failed_chunks}")

        if output.blocked_chunks != 1:
            errors.append(f"Atteso 1 chunk bloccato, trovati {output.blocked_chunks}")

        # ---------------------------------------------------------------------
        # Caso 1: chunk normale
        # ---------------------------------------------------------------------
        if normale is None:
            errors.append("Manca risultato per chunk_normale")
        else:
            if not normale.processed:
                errors.append("chunk_normale dovrebbe essere processed=True")

            if normale.blocked:
                errors.append("chunk_normale non dovrebbe essere blocked=True")

            if not normale.facts:
                errors.append("chunk_normale dovrebbe avere facts estratti")

            if not normale.micro_concepts:
                errors.append("chunk_normale dovrebbe avere micro_concepts estratti")

        # ---------------------------------------------------------------------
        # Caso 2: chunk vuoto
        # ---------------------------------------------------------------------
        if vuoto is None:
            errors.append("Manca risultato per chunk_vuoto")
        else:
            if vuoto.processed:
                errors.append("chunk_vuoto dovrebbe essere processed=False")

            if not assert_contains(vuoto.warnings, "CHUNK_TEXT_EMPTY"):
                errors.append("chunk_vuoto dovrebbe contenere warning CHUNK_TEXT_EMPTY")

            if not assert_contains(vuoto.errors, "MAP_SKIPPED_EMPTY_CHUNK"):
                errors.append("chunk_vuoto dovrebbe contenere errore MAP_SKIPPED_EMPTY_CHUNK")

        # ---------------------------------------------------------------------
        # Caso 3: demo/fallback
        # ---------------------------------------------------------------------
        if demo is None:
            errors.append("Manca risultato per chunk_demo_fallback")
        else:
            if not demo.processed:
                errors.append("chunk_demo_fallback dovrebbe essere processed=True")

            if not demo.blocked:
                errors.append("chunk_demo_fallback dovrebbe essere blocked=True")

            if not assert_contains(demo.warnings, "SOURCE_CONTAINS_DEMO_OR_FALLBACK_SIGNATURE"):
                errors.append(
                    "chunk_demo_fallback dovrebbe avere warning SOURCE_CONTAINS_DEMO_OR_FALLBACK_SIGNATURE"
                )

            if not assert_contains(demo.warnings, "EXTRACTION_CONTAINS_DEMO_OR_FALLBACK_SIGNATURES"):
                errors.append(
                    "chunk_demo_fallback dovrebbe avere warning EXTRACTION_CONTAINS_DEMO_OR_FALLBACK_SIGNATURES"
                )

        if errors:
            print("\n❌ TEST MAP V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST MAP V1 PASSATO")
        print("La Fase 1 MAP gestisce correttamente chunk normale, chunk vuoto e demo/fallback.")
        return 0

    except Exception as exc:
        print("\n❌ TEST MAP V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())