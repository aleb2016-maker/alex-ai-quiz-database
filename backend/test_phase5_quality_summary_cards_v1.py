# backend/test_phase5_quality_summary_cards_v1.py
# =============================================================================
# TEST FASE 5 — QUALITY SUMMARY CARDS V1
#
# Verifica:
# - collegamento a SuperQualityGateResult.clean_output
# - riassunto narrativo fluido
# - pulizia tipografica italiana
# - card JSON strutturate
# - micro_concetti veri di 2-3 parole
# - colore_categoria dinamico
#
# Nessuna UI/CSS/pulsanti.
# =============================================================================

from __future__ import annotations

import sys
import traceback

from motori_scrittura import (
    SuperQualityGateResult,
    Phase5QualityConfig,
    build_phase5_quality_summary_cards,
    phase5_quality_summary_cards_result_to_json,
)


def run_test() -> int:
    try:
        gate = SuperQualityGateResult(
            document_id="test_phase5_quality_summary_cards_v1",
            approved=True,
            status="APPROVED",
            blocked_areas=[],
            clean_output={
                "summary": {
                    "title": "Bozza riassunto macro-grezzo",
                    "key_points": [
                        "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                        "Ogni account e' associato a una persona identificabile.",
                        "Le credenziali non devono essere condivise tra piu operatori.",
                        "Si, la revisione periodica degli accessi riduce il rischio perche evita permessi attivi non autorizzati.",
                    ],
                    "source_pages": [1, 2],
                },
                "cards": [
                    {
                        "card_id": "card_draft_001",
                        "title": "Controllo accessi",
                        "message_key": "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                        "source_facts": [
                            "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                            "Ogni account e' associato a una persona identificabile.",
                            "Le credenziali non devono essere condivise tra piu operatori.",
                            "Si, la revisione periodica degli accessi riduce il rischio perche evita permessi attivi non autorizzati.",
                        ],
                        "micro_concepts": [
                            "controllo accessi",
                            "account utente",
                            "revisione periodica",
                            "permessi attivi",
                            "credenziali",  # una parola: deve essere scartata o compensata
                        ],
                        "source_pages": [1, 2],
                    }
                ],
                "study_pack": {
                    "title": "Bozza study pack",
                    "sections": [
                        {
                            "section_id": "section_001",
                            "title": "Blocco 1",
                            "key_facts": [
                                "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                                "Ogni account e' associato a una persona identificabile.",
                                "Le credenziali non devono essere condivise tra piu operatori.",
                                "Si, la revisione periodica degli accessi riduce il rischio perche evita permessi attivi non autorizzati.",
                            ],
                            "micro_concepts": [
                                "controllo accessi",
                                "account utente",
                                "revisione periodica",
                                "permessi attivi",
                            ],
                            "source_pages": [1, 2],
                        }
                    ],
                    "global_micro_concepts": [
                        "controllo accessi",
                        "account utente",
                        "revisione periodica",
                        "permessi attivi",
                    ],
                },
            },
            quality_report={
                "blocked_areas": [],
                "summary_points": 4,
                "cards_count": 1,
            },
        )

        result = build_phase5_quality_summary_cards(
            gate_result=gate,
            output_result=None,
            config=Phase5QualityConfig(
                max_summary_points=12,
                facts_per_paragraph=2,
                max_cards=4,
                max_card_facts=2,
                max_micro_concepts_per_card=5,
            ),
        )

        print(phase5_quality_summary_cards_result_to_json(result))

        errors: list[str] = []

        if result.phase_name != "QUALITY_SUMMARY_CARDS":
            errors.append(f"phase_name errato: {result.phase_name}")

        if result.errors:
            errors.append(f"result.errors non dovrebbe contenere errori: {result.errors}")

        if not result.approved:
            errors.append(f"Fase 5 dovrebbe essere APPROVED, status={result.status}")

        if result.riassunto_qualita is None:
            errors.append("riassunto_qualita mancante")
        else:
            testo = result.riassunto_qualita.testo_completo

            if not result.riassunto_qualita.paragrafi:
                errors.append("riassunto_qualita.paragrafi vuoto")

            if "\n- " in testo or "\n* " in testo:
                errors.append("Il riassunto sembra ancora una lista meccanica")

            if "perche" in testo.lower():
                errors.append("La correzione perche → perché non è avvenuta")

            if " e'" in testo.lower() or "e''" in testo.lower():
                errors.append("La correzione e' → è non è avvenuta")

            if " piu " in testo.lower():
                errors.append("La correzione piu → più non è avvenuta")

            if "perché" not in testo.lower():
                errors.append("Il testo finale dovrebbe contenere perché accentato")

            if "è" not in testo.lower():
                errors.append("Il testo finale dovrebbe contenere è accentata")

        if not result.card_concettuali:
            errors.append("card_concettuali vuoto")
        else:
            for card in result.card_concettuali:
                if not card.titolo:
                    errors.append(f"{card.card_id}: titolo vuoto")

                if not card.contenuto_esplicativo:
                    errors.append(f"{card.card_id}: contenuto_esplicativo vuoto")

                if not card.micro_concetti:
                    errors.append(f"{card.card_id}: micro_concetti vuoti")

                for concept in card.micro_concetti:
                    word_count = len(concept.split())
                    if word_count < 2 or word_count > 3:
                        errors.append(
                            f"{card.card_id}: micro_concetto non valido '{concept}'"
                        )

                if not card.colore_categoria.startswith("#"):
                    errors.append(f"{card.card_id}: colore_categoria non valido")

                if card.dominio_rilevato == "general":
                    errors.append(
                        f"{card.card_id}: dominio_rilevato troppo generico per testo accessi/credenziali"
                    )

        report = result.quality_report

        if report.get("summary_paragraphs", 0) < 1:
            errors.append("quality_report summary_paragraphs non valido")

        if report.get("cards_count", 0) < 1:
            errors.append("quality_report cards_count non valido")

        if errors:
            print("\n❌ TEST FASE 5 QUALITY SUMMARY CARDS V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST FASE 5 QUALITY SUMMARY CARDS V1 PASSATO")
        print("Riassunto di qualità e card concettuali generati come dati puliti.")
        return 0

    except Exception as exc:
        print("\n❌ TEST FASE 5 QUALITY SUMMARY CARDS V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())