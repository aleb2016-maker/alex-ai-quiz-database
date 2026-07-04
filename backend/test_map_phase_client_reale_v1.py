# backend/test_map_phase_client_reale_v1.py
# =============================================================================
# TEST REALE FASE 1 — MAP CON CLIENT LLM DEL BACKEND
#
# Obiettivo:
# - usare un client reale compatibile con il backend attuale
# - passarlo alla Fase 1 MAP tramite llm_client.generate(...)
# - verificare JSON valido
# - verificare facts[] grezzi
# - verificare micro_concepts[] non narrativi
#
# Questo file NON tocca UI, CSS, pulsanti, main.py o grafica.
# =============================================================================

from __future__ import annotations

import os
import sys
import traceback
from typing import Any, Dict, Optional

import ollama

from motori_scrittura import (
    ChunkInput,
    MapPhaseConfig,
    run_map_phase,
    map_phase_output_to_json,
)


class BackendOllamaChatClient:
    """
    Adapter minimale verso il motore reale già presente nel backend.

    Importante:
    - motori_scrittura.py resta astratto
    - questo adapter vive solo nel test
    - il modello è parametrico via MAP_TEST_MODEL
    """

    def __init__(self, model: str) -> None:
        self.model = model

    def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        response_format: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        max_tokens: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Converte il contratto astratto llm_client.generate(...)
        in una chiamata reale ollama.chat(...).

        Se il modello non restituisce JSON valido, non correggiamo qui:
        deve essere la MAP a gestire il problema con warnings/errors.
        """

        try:
            options: Dict[str, Any] = {
                "temperature": temperature,
            }

            if max_tokens:
                options["num_predict"] = max_tokens

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],
                format="json",
                options=options,
            )

            # Compatibilità con risposte dict-like.
            if isinstance(response, dict):
                message = response.get("message", {})
                if isinstance(message, dict):
                    content = message.get("content", "")
                    return str(content)

            # Compatibilità con oggetti Ollama recenti.
            message_obj = getattr(response, "message", None)
            if message_obj is not None:
                content = getattr(message_obj, "content", "")
                return str(content)

            raise RuntimeError(f"Formato risposta Ollama non riconosciuto: {response}")

        except Exception as exc:
            raise RuntimeError(
                f"Errore chiamata modello reale '{self.model}': "
                f"{type(exc).__name__}: {exc}"
            ) from exc


def contiene_formula_meccanica(testi: list[str]) -> list[str]:
    """
    Cerca formule da riassunto elegante/meccanico nei facts[].

    In MAP i facts devono essere grezzi, non frasi tipo:
    - in sintesi
    - il documento parla di
    - questo testo tratta
    """

    formule_vietate = [
        "in sintesi",
        "in conclusione",
        "il documento parla",
        "il documento tratta",
        "questo testo",
        "questo chunk",
        "tema principale",
        "aspetti importanti",
        "riassunto",
        "vengono affrontati",
    ]

    unito = "\n".join(str(t).lower() for t in testi)
    trovate = []

    for formula in formule_vietate:
        if formula in unito:
            trovate.append(formula)

    return trovate


def run_test() -> int:
    try:
        model_name = os.environ.get("MAP_TEST_MODEL", "gemma3:4b")

        print(f"Modello reale usato: {model_name}")

        client = BackendOllamaChatClient(model=model_name)

        chunks = [
            ChunkInput(
                chunk_id="chunk_reale_001",
                text=(
                    "Il controllo degli accessi limita l'utilizzo dei sistemi interni "
                    "agli utenti autorizzati. Ogni account deve essere associato a una "
                    "persona identificabile. Le credenziali non devono essere condivise "
                    "tra più operatori. La revisione periodica degli accessi riduce il "
                    "rischio che utenti non più autorizzati mantengano permessi attivi."
                ),
                page_start=1,
                page_end=1,
            )
        ]

        output = run_map_phase(
            document_id="test_map_phase_client_reale_v1",
            chunks=chunks,
            llm_client=client,
            config=MapPhaseConfig(
                domain_hint="technical",
                temperature=0.0,
                max_tokens=1600,
                max_facts=20,
                max_micro_concepts=20,
                max_entities=20,
                max_relations=20,
            ),
        )

        print(map_phase_output_to_json(output))

        errors: list[str] = []

        if output.total_chunks != 1:
            errors.append(f"Atteso total_chunks=1, trovato {output.total_chunks}")

        if output.processed_chunks != 1:
            errors.append(f"Atteso processed_chunks=1, trovato {output.processed_chunks}")

        if output.failed_chunks != 0:
            errors.append(f"Atteso failed_chunks=0, trovato {output.failed_chunks}")

        if output.blocked_chunks != 0:
            errors.append(f"Atteso blocked_chunks=0, trovato {output.blocked_chunks}")

        if not output.results:
            errors.append("Nessun MapChunkResult prodotto")
        else:
            result = output.results[0]

            if not result.processed:
                errors.append("Il chunk reale dovrebbe essere processed=True")

            if result.errors:
                errors.append(f"Il chunk reale non dovrebbe avere errors[]: {result.errors}")

            if result.blocked:
                errors.append(f"Il chunk reale non dovrebbe essere blocked=True: {result.warnings}")

            if not result.facts:
                errors.append("facts[] vuoto: il modello reale non ha estratto fatti")

            if not result.micro_concepts:
                errors.append("micro_concepts[] vuoto: il modello reale non ha estratto micro-concetti")

            if not result.entities:
                errors.append("entities[] vuoto: il modello reale non ha estratto entità")

            formule = contiene_formula_meccanica(result.facts)
            if formule:
                errors.append(
                    "facts[] contiene formule da riassunto/meccaniche vietate in MAP: "
                    + ", ".join(formule)
                )

            micro_concepts_troppo_lunghi = [
                concept
                for concept in result.micro_concepts
                if len(str(concept).split()) > 6
            ]

            if micro_concepts_troppo_lunghi:
                errors.append(
                    "micro_concepts[] contiene elementi troppo lunghi, sembrano frasi: "
                    + " | ".join(micro_concepts_troppo_lunghi[:5])
                )

        if errors:
            print("\n❌ TEST MAP CLIENT REALE V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST MAP CLIENT REALE V1 PASSATO")
        print("Il client reale produce JSON valido e materiale MAP grezzo utilizzabile.")
        return 0

    except Exception as exc:
        print("\n❌ TEST MAP CLIENT REALE V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())