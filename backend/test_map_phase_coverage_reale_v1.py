# backend/test_map_phase_coverage_reale_v1.py
# =============================================================================
# TEST REALE MAP COVERAGE V1
#
# Obiettivo:
# - verificare che MAP_COVERAGE_V1 non perda fatti importanti
# - bloccare regressioni future sul prompt MAP
# - controllare che obblighi, divieti e causa-effetto diventino facts/relations
#
# Questo file NON tocca UI, CSS, pulsanti, grafica o main.py.
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
    Adapter minimale verso il client reale già usato dal backend.

    Questo adapter resta dentro il test:
    - non modifica motori_scrittura.py
    - non modifica main.py
    - non modifica UI/CSS/pulsanti
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

            if isinstance(response, dict):
                message = response.get("message", {})
                if isinstance(message, dict):
                    return str(message.get("content", ""))

            message_obj = getattr(response, "message", None)
            if message_obj is not None:
                return str(getattr(message_obj, "content", ""))

            raise RuntimeError(f"Formato risposta Ollama non riconosciuto: {response}")

        except Exception as exc:
            raise RuntimeError(
                f"Errore chiamata modello reale '{self.model}': "
                f"{type(exc).__name__}: {exc}"
            ) from exc


def text_join(values) -> str:
    return "\n".join(str(v).lower() for v in values)


def relation_join(relations) -> str:
    parts = []

    for relation in relations:
        parts.extend(
            [
                getattr(relation, "subject", ""),
                getattr(relation, "predicate", ""),
                getattr(relation, "object", ""),
                getattr(relation, "evidence", ""),
            ]
        )

    return "\n".join(str(p).lower() for p in parts)


def contains_all(text: str, required_terms: list[str]) -> bool:
    return all(term.lower() in text.lower() for term in required_terms)


def run_test() -> int:
    try:
        model_name = os.environ.get("MAP_TEST_MODEL", "gemma3:4b")
        print(f"Modello reale usato: {model_name}")

        client = BackendOllamaChatClient(model=model_name)

        chunk_text = (
            "Il controllo degli accessi limita l'utilizzo dei sistemi interni "
            "agli utenti autorizzati. Ogni account deve essere associato a una "
            "persona identificabile. Le credenziali non devono essere condivise "
            "tra più operatori. La revisione periodica degli accessi riduce il "
            "rischio che utenti non più autorizzati mantengano permessi attivi."
        )

        output = run_map_phase(
            document_id="test_map_phase_coverage_reale_v1",
            chunks=[
                ChunkInput(
                    chunk_id="chunk_coverage_reale_001",
                    text=chunk_text,
                    page_start=1,
                    page_end=1,
                )
            ],
            llm_client=client,
            config=MapPhaseConfig(
                domain_hint="technical",
                temperature=0.0,
                max_tokens=1800,
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
            errors.append("Nessun risultato MAP prodotto")
        else:
            result = output.results[0]

            facts_text = text_join(result.facts)
            concepts_text = text_join(result.micro_concepts)
            relations_text = relation_join(result.relations)

            if result.errors:
                errors.append(f"errors[] non dovrebbe contenere errori: {result.errors}")

            if result.warnings:
                errors.append(f"warnings[] non dovrebbe contenere warning: {result.warnings}")

            if not result.processed:
                errors.append("Il chunk dovrebbe essere processed=True")

            if result.blocked:
                errors.append("Il chunk non dovrebbe essere blocked=True")

            # -----------------------------------------------------------------
            # REGRESSIONE PRINCIPALE:
            # Il fatto sulla revisione periodica non deve più sparire.
            # -----------------------------------------------------------------
            if not contains_all(
                facts_text,
                ["revisione", "periodica", "accessi", "riduce", "rischio"],
            ):
                errors.append(
                    "facts[] non contiene il fatto completo sulla revisione periodica "
                    "degli accessi che riduce il rischio."
                )

            if not contains_all(
                relations_text,
                ["revisione", "periodica", "accessi", "riduce", "rischio"],
            ):
                errors.append(
                    "relations[] non contiene la relazione causa-effetto sulla revisione "
                    "periodica degli accessi che riduce il rischio."
                )

            # -----------------------------------------------------------------
            # Obbligo: ogni account associato a persona identificabile.
            # -----------------------------------------------------------------
            if not contains_all(
                facts_text,
                ["account", "associato", "persona", "identificabile"],
            ):
                errors.append(
                    "facts[] non contiene l'obbligo: account associato a persona identificabile."
                )

            # -----------------------------------------------------------------
            # Divieto: credenziali non condivise.
            # -----------------------------------------------------------------
            if not contains_all(
                facts_text,
                ["credenziali", "non", "condivise"],
            ):
                errors.append(
                    "facts[] non contiene il divieto: credenziali non condivise."
                )

            # -----------------------------------------------------------------
            # Micro-concetto minimo atteso.
            # Non pretendiamo frase esatta, ma deve esserci il tema.
            # -----------------------------------------------------------------
            if "revisione" not in concepts_text:
                errors.append(
                    "micro_concepts[] non contiene il concetto di revisione periodica."
                )

            # -----------------------------------------------------------------
            # Anti-riassunto meccanico.
            # -----------------------------------------------------------------
            formule_meccaniche = [
                "in sintesi",
                "in conclusione",
                "il documento parla",
                "il documento tratta",
                "questo testo",
                "questo chunk",
                "tema principale",
                "aspetti importanti",
                "riassunto",
            ]

            facts_lower = facts_text.lower()
            trovate = [
                formula for formula in formule_meccaniche
                if formula in facts_lower
            ]

            if trovate:
                errors.append(
                    "facts[] contiene formule da riassunto/meccaniche vietate: "
                    + ", ".join(trovate)
                )

        if errors:
            print("\n❌ TEST MAP COVERAGE REALE V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST MAP COVERAGE REALE V1 PASSATO")
        print("MAP_COVERAGE_V1 protegge obblighi, divieti e causa-effetto nei facts/relations.")
        return 0

    except Exception as exc:
        print("\n❌ TEST MAP COVERAGE REALE V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())