# backend/test_map_phase_json_corrotto_v1.py
# =============================================================================
# TEST FASE 1 — MAP — JSON CORROTTO
#
# Verifica che la Fase MAP non si blocchi se il LLM restituisce:
# - un JSON valido per un chunk normale
# - un JSON corrotto/non parsabile per un chunk problematico
#
# Questo file NON tocca UI, CSS, pulsanti o grafica.
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


class CorruptedJsonMockLLM:
    """
    Mock LLM controllato.

    Simula:
    - output JSON valido per chunk_normale
    - output JSON corrotto per chunk_json_corrotto
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

        # Caso problematico: il modello restituisce testo non JSON.
        # La MAP deve registrare l'errore, non far crollare tutto.
        if chunk_id == "chunk_json_corrotto":
            return """
            Questo NON è JSON valido.
            {
              domain: technical,
              facts: [
                "fatto senza chiusura corretta"
            """

        # Caso normale: JSON valido.
        return json.dumps(
            {
                "domain": "technical",
                "facts": [
                    "Il controllo degli accessi limita l'utilizzo dei sistemi aziendali agli utenti autorizzati.",
                    "Le credenziali devono essere protette e aggiornate periodicamente."
                ],
                "micro_concepts": [
                    "controllo accessi",
                    "protezione credenziali"
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
                    }
                ],
            },
            ensure_ascii=False,
        )


def contains_text(values, expected: str) -> bool:
    """
    Cerca una sottostringa dentro una lista di warning/errori.
    """
    joined = "\n".join(str(v) for v in values)
    return expected in joined


def run_test() -> int:
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
                chunk_id="chunk_json_corrotto",
                text=(
                    "Questo chunk simula un caso in cui il modello risponde male "
                    "e restituisce JSON corrotto."
                ),
                page_start=2,
                page_end=2,
            ),
        ]

        output = run_map_phase(
            document_id="test_map_phase_json_corrotto_v1",
            chunks=chunks,
            llm_client=CorruptedJsonMockLLM(),
            config=MapPhaseConfig(domain_hint="technical"),
        )

        print(map_phase_output_to_json(output))

        results_by_id = {result.chunk_id: result for result in output.results}

        normale = results_by_id.get("chunk_normale")
        corrotto = results_by_id.get("chunk_json_corrotto")

        errors = []

        # ---------------------------------------------------------------------
        # Controlli generali
        # ---------------------------------------------------------------------
        if output.total_chunks != 2:
            errors.append(f"Attesi 2 chunk, trovati {output.total_chunks}")

        if output.processed_chunks != 1:
            errors.append(f"Atteso 1 chunk processato, trovati {output.processed_chunks}")

        if output.failed_chunks != 1:
            errors.append(f"Atteso 1 chunk fallito, trovati {output.failed_chunks}")

        if output.blocked_chunks != 0:
            errors.append(f"Attesi 0 chunk bloccati, trovati {output.blocked_chunks}")

        # ---------------------------------------------------------------------
        # Chunk normale
        # ---------------------------------------------------------------------
        if normale is None:
            errors.append("Manca risultato per chunk_normale")
        else:
            if not normale.processed:
                errors.append("chunk_normale dovrebbe essere processed=True")

            if normale.errors:
                errors.append(f"chunk_normale non dovrebbe avere errori: {normale.errors}")

            if not normale.facts:
                errors.append("chunk_normale dovrebbe avere facts estratti")

        # ---------------------------------------------------------------------
        # Chunk JSON corrotto
        # ---------------------------------------------------------------------
        if corrotto is None:
            errors.append("Manca risultato per chunk_json_corrotto")
        else:
            if corrotto.processed:
                errors.append("chunk_json_corrotto dovrebbe essere processed=False")

            if corrotto.blocked:
                errors.append("chunk_json_corrotto non dovrebbe essere blocked=True")

            if not contains_text(corrotto.errors, "MAP_JSON_PARSE_FAILED"):
                errors.append("chunk_json_corrotto dovrebbe avere errore MAP_JSON_PARSE_FAILED")

            if not contains_text(corrotto.warnings, "JSON_PARSE_FAILED"):
                errors.append("chunk_json_corrotto dovrebbe avere warning JSON_PARSE_FAILED")

            if corrotto.extraction_score != 0.0:
                errors.append(
                    f"chunk_json_corrotto dovrebbe avere extraction_score=0.0, trovato {corrotto.extraction_score}"
                )

        if errors:
            print("\n❌ TEST MAP JSON CORROTTO V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST MAP JSON CORROTTO V1 PASSATO")
        print("La Fase 1 MAP non si blocca se un chunk restituisce JSON corrotto.")
        return 0

    except Exception as exc:
        print("\n❌ TEST MAP JSON CORROTTO V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())