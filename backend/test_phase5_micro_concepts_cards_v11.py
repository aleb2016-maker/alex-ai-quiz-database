import sys
import traceback

from motori_scrittura import (
    SuperQualityGateResult,
    Phase5QualityConfig,
    build_phase5_quality_summary_cards,
    phase5_quality_summary_cards_result_to_json,
    q5_is_valid_micro_concept,
)


def run_test() -> int:
    try:
        gate = SuperQualityGateResult(
            document_id="test_phase5_micro_concepts_cards_v11",
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
                            "credenziali",
                            "accessi limita",
                            "credenziali non",
                            "accessi riduce",
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

        errors = []

        if not result.approved:
            errors.append(f"Fase 5.1 dovrebbe essere approved=True, status={result.status}")

        if result.errors:
            errors.append(f"result.errors non dovrebbe avere errori: {result.errors}")

        bad_concepts = {
            "accessi limita",
            "credenziali non",
            "accessi riduce",
            "controllo degli",
            "devono essere",
        }

        all_concepts = []

        for card in result.card_concettuali:
            all_concepts.extend(card.micro_concetti)

            for concept in card.micro_concetti:
                lowered = concept.lower()

                if lowered in bad_concepts:
                    errors.append(f"{card.card_id}: micro-concetto brutto non filtrato: {concept}")

                if not q5_is_valid_micro_concept(concept):
                    errors.append(f"{card.card_id}: micro-concetto invalido: {concept}")

                if " non" in lowered or lowered.endswith(" non"):
                    errors.append(f"{card.card_id}: micro-concetto contiene negazione sporca: {concept}")

        titles = [card.titolo for card in result.card_concettuali]
        unique_titles = set(title.lower() for title in titles)

        if len(result.card_concettuali) >= 4 and len(unique_titles) < 3:
            errors.append(f"Titoli card ancora troppo ripetitivi: {titles}")

        expected_good_any = {
            "controllo accessi",
            "account utente",
            "protezione credenziali",
            "revisione periodica",
            "riduzione rischio",
            "permessi attivi",
        }

        if not expected_good_any.intersection(set(c.lower() for c in all_concepts)):
            errors.append("Nessun micro-concetto buono atteso trovato")

        if errors:
            print("\n❌ TEST MICRO PATCH FASE 5.1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST MICRO PATCH FASE 5.1 PASSATO")
        print("Micro-concetti più puliti e titoli card meno ripetitivi.")
        return 0

    except Exception as exc:
        print("\n❌ TEST MICRO PATCH FASE 5.1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())
