# Fase 5.10.2 — Final Registry Quality Snapshot V1

- Status: `PASS`
- Registry motors count: `11`
- Raw total defects: `11`
- Final total defects: `0`
- Improvement total: `11`
- Correct option map preserved: `True`

## Difetti misurati

| Area | Raw | Final |
|---|---:|---:|
| `summary_card_bad_patterns` | 10 | 0 |
| `study_mechanical_questions` | 0 | 0 |
| `quiz_mechanical_questions` | 0 | 0 |
| `quiz_true_fact_distractors` | 0 | 0 |
| `quiz_duplicate_questions` | 0 | 0 |
| `quiz_rough_explanations` | 1 | 0 |
| `micro_concepts_sentence_punctuation` | 0 | 0 |
| `total` | 11 | 0 |

## Motori registry

| # | Motor ID | Adapter | Target |
|---:|---|---|---|
| 1 | `backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1` | `quiz_list` | `quiz` |
| 2 | `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1` | `quiz_list` | `quiz` |
| 3 | `scripts.rag_cleaner_finale_universale_v35k.clean_output` | `summary_dict` | `summary` |
| 4 | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions` | `cards_list` | `study` |
| 5 | `scripts.rag_motore_test_riutilizzabile_v35d.refine_output` | `summary_dict` | `summary` |
| 6 | `scripts.rag_revisore_accordo_pronomi_v35j.improve_output` | `summary_dict` | `summary` |
| 7 | `scripts.rag_revisore_qualita_testuale_v35g.refine_output` | `summary_dict` | `summary` |
| 8 | `scripts.rag_revisore_qualita_testuale_v35g.refine_study` | `phase5_full_output` | `full_output` |
| 9 | `backend.main.pulisci_qualita_linguistica_quiz` | `dict_test_quiz` | `quiz` |
| 10 | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests` | `legacy_answers_dict` | `quiz` |
| 11 | `backend.phase5_universal_text_cleaner_summary_cards_v1.universal_text_cleaner_summary_cards_payload_target_v1` | `payload` | `full_output` |