import sys
import traceback

from motori_scrittura import (
    SuperQualityGateResult,
    Phase5StudyQuizConfig,
    build_phase5_quality_study_quiz,
    phase5_quality_study_quiz_result_to_json,
    qg_normalize_for_compare,
)


def run_test() -> int:
    try:
        source_facts = [
            "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
            "Ogni account deve essere associato a una persona identificabile.",
            "Le credenziali non devono essere condivise tra più operatori.",
            "La revisione periodica degli accessi riduce il rischio che utenti non più autorizzati mantengano permessi attivi.",
        ]

        gate = SuperQualityGateResult(
            document_id="test_phase5_study_quiz_v1",
            approved=False,
            status="BLOCKED",
            blocked_areas=["quiz"],
            clean_output={
                "summary": {
                    "title": "Bozza riassunto macro-grezzo",
                    "key_points": source_facts,
                    "source_pages": [1, 2],
                },
                "cards": [
                    {
                        "card_id": "card_draft_001",
                        "title": "Controllo accessi",
                        "message_key": source_facts[0],
                        "source_facts": source_facts,
                        "micro_concepts": [
                            "controllo accessi",
                            "account utente",
                            "protezione credenziali",
                            "revisione periodica",
                            "riduzione rischio",
                            "permessi attivi",
                        ],
                        "source_pages": [1, 2],
                    }
                ],
                "study_questions": [],
                "quiz": [],
                "study_pack": {
                    "title": "Bozza study pack",
                    "sections": [
                        {
                            "section_id": "section_001",
                            "title": "Blocco 1",
                            "key_facts": source_facts,
                            "micro_concepts": [
                                "controllo accessi",
                                "account utente",
                                "protezione credenziali",
                                "revisione periodica",
                                "riduzione rischio",
                                "permessi attivi",
                            ],
                            "source_pages": [1, 2],
                        }
                    ],
                    "global_micro_concepts": [
                        "controllo accessi",
                        "account utente",
                        "protezione credenziali",
                        "revisione periodica",
                        "riduzione rischio",
                        "permessi attivi",
                    ],
                },
            },
            quality_report={
                "blocked_areas": ["quiz"],
                "summary_points": 4,
                "cards_count": 1,
            },
        )

        result = build_phase5_quality_study_quiz(
            gate_result=gate,
            output_result=None,
            config=Phase5StudyQuizConfig(
                max_study_questions=8,
                max_quiz_questions=4,
                quiz_options_count=4,
                max_micro_concepts_per_item=5,
                require_phase4_study_quiz_not_blocked=False,
            ),
        )

        print(phase5_quality_study_quiz_result_to_json(result))

        errors = []

        if result.phase_name != "QUALITY_STUDY_QUIZ":
            errors.append(f"phase_name errato: {result.phase_name}")

        if not result.approved:
            errors.append(f"Fase 5.2 dovrebbe essere approved=True, status={result.status}, errors={result.errors}")

        if result.errors:
            errors.append(f"result.errors non dovrebbe contenere errori: {result.errors}")

        if len(result.domande_studio) < 4:
            errors.append(f"Attese almeno 4 domande studio, trovate {len(result.domande_studio)}")

        if len(result.test_quiz) < 4:
            errors.append(f"Attese almeno 4 domande quiz, trovate {len(result.test_quiz)}")

        forbidden_templates = [
            "quale regola o informazione emerge da",
            "quale affermazione è supportata dal documento",
        ]

        for item in result.domande_studio:
            lowered = item.domanda.lower()

            for template in forbidden_templates:
                if template in lowered:
                    errors.append(f"{item.question_id}: domanda studio meccanica: {item.domanda}")

            if not item.risposta_guida:
                errors.append(f"{item.question_id}: risposta guida vuota")

            if not item.fatto_origine:
                errors.append(f"{item.question_id}: fatto origine vuoto")

            if not item.micro_concetti:
                errors.append(f"{item.question_id}: micro_concetti vuoti")

        source_keys = set(qg_normalize_for_compare(fact) for fact in source_facts)

        for quiz_question in result.test_quiz:
            lowered = quiz_question.domanda.lower()

            for template in forbidden_templates:
                if template in lowered:
                    errors.append(f"{quiz_question.question_id}: domanda quiz meccanica: {quiz_question.domanda}")

            if len(quiz_question.opzioni) != 4:
                errors.append(f"{quiz_question.question_id}: deve avere 4 opzioni")

            correct = [opt for opt in quiz_question.opzioni if opt.is_correct]
            if len(correct) != 1:
                errors.append(f"{quiz_question.question_id}: deve avere esattamente 1 corretta")

            if correct and correct[0].option_id != quiz_question.correct_option_id:
                errors.append(f"{quiz_question.question_id}: correct_option_id non coincide")

            option_texts = [opt.testo for opt in quiz_question.opzioni]
            if len(set(qg_normalize_for_compare(t) for t in option_texts)) != len(option_texts):
                errors.append(f"{quiz_question.question_id}: opzioni duplicate")

            for option in quiz_question.opzioni:
                if not option.is_correct:
                    if qg_normalize_for_compare(option.testo) in source_keys:
                        errors.append(
                            f"{quiz_question.question_id}: distrattore coincide con fact vero: {option.testo}"
                        )

            if not quiz_question.spiegazione:
                errors.append(f"{quiz_question.question_id}: spiegazione vuota")

            if not quiz_question.fatto_origine:
                errors.append(f"{quiz_question.question_id}: fatto origine vuoto")

        report = result.quality_report

        if report.get("study_questions_count", 0) < 4:
            errors.append("quality_report study_questions_count non valido")

        if report.get("quiz_questions_count", 0) < 4:
            errors.append("quality_report quiz_questions_count non valido")

        if errors:
            print("\n❌ TEST FASE 5.2 STUDY QUIZ V1 FALLITO")
            for error in errors:
                print(f"- {error}")
            return 1

        print("\n✅ TEST FASE 5.2 STUDY QUIZ V1 PASSATO")
        print("Domande studio e test finali generati con motori dedicati e validazione anti-distrattori veri.")
        return 0

    except Exception as exc:
        print("\n❌ TEST FASE 5.2 STUDY QUIZ V1 ERRORE NON GESTITO")
        print(f"{type(exc).__name__}: {exc}")
        print(traceback.format_exc())
        return 1


if __name__ == "__main__":
    sys.exit(run_test())
