# Fase 5.9.5 — Quiz Quality Motors Shortlist V1

- Status: `PASS_DIAGNOSTIC`
- Candidati totali analizzati: `1419`

## Conteggi

| Categoria | Conteggio |
|---|---:|
| `READY_TO_COMPAT_TEST` | 60 |
| `MAYBE_NEEDS_MANUAL_REVIEW` | 158 |
| `VALIDATOR_ONLY` | 141 |
| `ALREADY_REGISTERED` | 6 |
| `REJECT_NOISE` | 613 |
| `LOW_PRIORITY` | 441 |

## READY_TO_COMPAT_TEST

| Score | File | Funzione | Adapter | Capability | Motivo |
|---:|---|---|---|---|---|
| 73 | `scripts/rag_adapter_quiz_ufficiale_v43.py:308` | `adatta_domande_esistenti` | `medium_multi_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, grammar_accents_text_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 74 | `scripts/motore_qualita_generale.py:276` | `analizza_domanda` | `medium_multi_input` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 71 | `backend/motori_scrittura.py:5644` | `q52_validate_quiz` | `medium_multi_input` | `quiz_question_naturalness, strong_distractors, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 61 | `scripts/motore_qualita_logica_visiva_base.py:256` | `analizza_domanda_visiva` | `medium_multi_input` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 56 | `scripts/validatore_rag_distrattori_forti_v2.py:52` | `valuta_domanda` | `medium_multi_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 53 | `scripts/estrai_motore_scientifico_da_migliorare.py:211` | `crea_file_lavoro` | `easy_single_input` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 41 | `backend/motori_scrittura.py:3510` | `qg_clean_output_bundle` | `easy_single_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend, grammar_accents_text_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 54 | `backend/phase5_live_quality_bridge_v1.py:273` | `_legacy_refine_output_to_phase5` | `medium_multi_input` | `strong_distractors, interactive_quiz_frontend, quiz_explanation_quality, quiz_question_naturalness` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 36 | `backend/phase5_quiz_true_distractor_repair_v1.py:212` | `repair_quiz_true_distractors_v1` | `easy_single_input` | `strong_distractors, quiz_question_naturalness, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 30 | `scripts/applica_v35k_reale.py:173` | `clean_output` | `easy_single_input` | `quiz_explanation_quality, strong_distractors, quiz_question_naturalness, grammar_accents_text_quality, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 29 | `scripts/rag_bridge_motori_qualita_esistenti_v35b.py:196` | `controlla_test_con_motori` | `medium_multi_input` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 31 | `backend/main.py:849` | `crea_prompt_quiz_avanzato` | `medium_multi_input` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, strong_distractors, grammar_accents_text_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 26 | `scripts/motore_qualita_generale.py:400` | `trova_duplicati_e_simili` | `medium_multi_input` | `quiz_question_naturalness` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 26 | `scripts/report_distrattori_scientifici.py:184` | `analizza_motore` | `medium_multi_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 25 | `scripts/motore_qualita_generale.py:441` | `analizza_motore` | `medium_multi_input` | `quiz_question_naturalness, quiz_explanation_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 23 | `scripts/rag_adapter_quiz_ufficiale_v43.py:93` | `crea_candidate_sicurezza` | `easy_single_input` | `grammar_accents_text_quality, quiz_explanation_quality, quiz_question_naturalness, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 23 | `scripts/rag_genera_output_da_kb_clean_v34e.py:415` | `crea_test` | `medium_multi_input` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, grammar_accents_text_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 23 | `scripts/report_distrattori_scientifici.py:123` | `valuta_qualita_opzioni` | `medium_multi_input` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 21 | `scripts/rag_revisore_qualita_testuale_v35g.py:341` | `refine_tests` | `easy_single_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 20 | `backend/main.py:1300` | `controlla_duplicati_informatica` | `easy_single_input` | `quiz_question_naturalness` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 19 | `backend/main.py:2558` | `generate_informatica_final_json` | `easy_single_input` | `quiz_question_naturalness` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 19 | `scripts/estrai_biologia_da_migliorare.py:127` | `valuta_problemi_qualita` | `medium_multi_input` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 19 | `scripts/estrai_motore_scientifico_da_migliorare.py:152` | `valuta_problemi_qualita` | `medium_multi_input` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 18 | `scripts/rag_prepara_import_approvati.py:137` | `normalizza_per_database` | `medium_multi_input` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 17 | `scripts/motore_qualita_logica_visiva_base.py:377` | `analizza_file` | `easy_single_input` | `quiz_question_naturalness` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 18 | `scripts/applica_v35k_reale.py:111` | `clean_text` | `easy_single_input` | `quiz_explanation_quality, grammar_accents_text_quality, quiz_question_naturalness, strong_distractors, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 17 | `scripts/estrai_biologia_da_migliorare.py:54` | `normalizza_opzioni` | `easy_single_input` | `strong_distractors, quiz_explanation_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 17 | `scripts/estrai_motore_scientifico_da_migliorare.py:79` | `normalizza_opzioni` | `easy_single_input` | `strong_distractors, quiz_explanation_quality` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 16 | `scripts/rag_revisore_qualita_testuale_v35g.py:490` | `controlla_duplicati` | `easy_single_input` | `quiz_explanation_quality, quiz_question_naturalness, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 16 | `scripts/motore_qualita_logica_visiva_base.py:432` | `crea_report_markdown` | `easy_single_input` | `quiz_question_naturalness` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 15 | `scripts/rag_bridge_motori_qualita_esistenti_v35b.py:104` | `analizza_domanda_se_possibile` | `medium_multi_input` | `quiz_question_naturalness, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 15 | `scripts/estrai_biologia_da_migliorare.py:85` | `normalizza_risposta` | `medium_multi_input` | `quiz_explanation_quality, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 15 | `scripts/estrai_motore_scientifico_da_migliorare.py:110` | `normalizza_risposta` | `medium_multi_input` | `quiz_explanation_quality, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 15 | `scripts/report_distrattori_scientifici.py:81` | `normalizza_risposta` | `medium_multi_input` | `quiz_explanation_quality, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 14 | `backend/phase5_quiz_true_distractor_repair_v1.py:298` | `repair_payload_quiz_true_distractors_v1` | `easy_single_input` | `strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 14 | `scripts/improve_answer_options_100.py:504` | `applica_miglioramenti` | `easy_single_input` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 14 | `scripts/check_duplicates_base.py:90` | `controlla_opzioni_duplicate` | `easy_single_input` | `strong_distractors, quiz_question_naturalness` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 14 | `scripts/check_text_quality_ai.py:79` | `crea_prompt_revisione` | `easy_single_input` | `quiz_question_naturalness, grammar_accents_text_quality, quiz_explanation_quality, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 14 | `scripts/rag_revisore_naturalezza_antikeyword_v35i.py:238` | `natural_test_explanation` | `medium_multi_input` | `grammar_accents_text_quality, quiz_explanation_quality, quiz_question_naturalness, strong_distractors` | Sembra motore trasformativo con capability quiz e firma adattabile. |
| 14 | `backend/quiz_generator.py:2` | `genera_quiz_json` | `medium_multi_input` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` | Sembra motore trasformativo con capability quiz e firma adattabile. |

## MAYBE_NEEDS_MANUAL_REVIEW

| Score | File | Funzione | Adapter | Capability | Motivo |
|---:|---|---|---|---|---|
| 75 | `scripts/rag_genera_quiz_json.py:19` | `crea_prompt_quiz_json` | `hard_many_inputs` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, grammar_accents_text_quality` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 61 | `scripts/motore_traduzione_inglese.py:69` | `main` | `hard_no_input` | `quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 63 | `scripts/motore_distrattori_ai.py:141` | `analizza_domanda` | `medium_multi_input` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 52 | `scripts/estrai_biologia_da_migliorare.py:186` | `main` | `hard_no_input` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 46 | `scripts/migliora_logica_quarto_blocco_distrattori_forti.py:371` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 46 | `scripts/migliora_inglese_terzo_blocco_distrattori_forti.py:374` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 46 | `scripts/migliora_inglese_quarto_blocco_distrattori_forti.py:375` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 46 | `scripts/migliora_logica_secondo_blocco_distrattori_forti.py:347` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 46 | `scripts/migliora_inglese_secondo_blocco_distrattori_forti.py:376` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 46 | `scripts/migliora_logica_terzo_blocco_distrattori_forti.py:396` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 46 | `scripts/migliora_inglese_primo_blocco_distrattori_forti.py:385` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 45 | `scripts/migliora_matematica_terzo_blocco_distrattori_forti.py:335` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 45 | `scripts/migliora_matematica_quarto_blocco_distrattori_forti.py:336` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 45 | `scripts/migliora_matematica_secondo_blocco_distrattori_forti.py:337` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 45 | `scripts/migliora_logica_primo_blocco_distrattori_forti.py:356` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 45 | `scripts/migliora_matematica_primo_blocco_distrattori_forti.py:334` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 45 | `scripts/migliora_ai_secondo_blocco_distrattori_forti.py:213` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 44 | `scripts/migliora_ai_primo_blocco_distrattori_forti.py:220` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 43 | `scripts/migliora_ai_quarto_blocco_distrattori_forti.py:254` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 43 | `scripts/migliora_informatica_primo_blocco_distrattori_forti.py:314` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 43 | `scripts/migliora_informatica_quarto_blocco_distrattori_forti.py:314` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 43 | `scripts/migliora_informatica_terzo_blocco_distrattori_forti.py:314` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 43 | `scripts/migliora_ai_quinto_blocco_distrattori_forti.py:262` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 43 | `scripts/migliora_ai_terzo_blocco_distrattori_forti.py:317` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 43 | `scripts/migliora_informatica_secondo_blocco_distrattori_forti.py:314` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 41 | `scripts/motore_distrattori_ai_tre_forti.py:138` | `analizza_domanda` | `medium_multi_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 54 | `backend/legacy_quality_motor_registry_v1.py:515` | `_legacy_output_to_phase5` | `medium_multi_input` | `strong_distractors, interactive_quiz_frontend, quiz_explanation_quality, quiz_question_naturalness` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 35 | `scripts/corregge_avvisi_ai_terzo_blocco.py:122` | `main` | `hard_no_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 35 | `scripts/check_text_quality_ai.py:39` | `crea_testo_da_revisionare` | `easy_single_input` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` | Possibile motore utile, ma serve controllo manuale/adapter. |
| 28 | `scripts/correzione_rapida_logica_visiva.py:267` | `main` | `hard_no_input` | `quiz_question_naturalness, quiz_explanation_quality` | Possibile motore utile, ma serve controllo manuale/adapter. |

## VALIDATOR_ONLY più forti

| Score | File | Funzione | Capability |
|---:|---|---|---|
| 77 | `backend/motori_scrittura.py:3296` | `qg_validate_quiz` | `strong_distractors, interactive_quiz_frontend, quiz_question_naturalness, quiz_explanation_quality` |
| 55 | `scripts/validatore_core_database.py:210` | `validate_question` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` |
| 55 | `scripts/rag_prepara_import_approvati.py:70` | `valida_domanda_approvata` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 48 | `backend/main.py:1135` | `controlla_errori_tecnici_informatica` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` |
| 47 | `scripts/valida_mini_llm_study_pack_cli_v2.py:143` | `main` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, strong_distractors` |
| 37 | `scripts/rag_valida_quiz_json.py:23` | `valida_domanda` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality` |
| 39 | `scripts/validatore_duplicati_database.py:114` | `main` | `quiz_question_naturalness, strong_distractors, interactive_quiz_frontend` |
| 35 | `backend/motori_scrittura.py:3224` | `qg_validate_study_questions` | `quiz_question_naturalness, quiz_explanation_quality` |
| 35 | `scripts/rag_adapter_quiz_ufficiale_v43.py:344` | `valida_struttura_ufficiale` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality` |
| 34 | `scripts/validatore_coerenza_logica_visiva.py:108` | `main` | `quiz_explanation_quality, quiz_question_naturalness` |
| 32 | `scripts/benchmark_mini_llm_study_pack_v3_quality_gate.py:71` | `validate_pack` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` |
| 35 | `scripts/visual_logic_validator.py:379` | `validate_visual_logic_question` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, strong_distractors` |
| 29 | `scripts/valida_mini_llm_query_context_expander_v394.py:14` | `main` | `quiz_explanation_quality, quiz_question_naturalness` |
| 29 | `scripts/check_duplicates_base.py:170` | `main` | `quiz_question_naturalness, strong_distractors` |
| 26 | `scripts/benchmark_mini_llm_study_pack_v2_quality.py:76` | `validate_pack` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality` |
| 26 | `scripts/valida_mini_llm_output_modes_v1.py:141` | `main` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, strong_distractors` |
| 25 | `scripts/rag_revisore_qualita_testuale_v35g.py:599` | `validate_quality` | `quiz_question_naturalness, strong_distractors, grammar_accents_text_quality, quiz_explanation_quality, interactive_quiz_frontend` |
| 23 | `backend/main.py:602` | `controlla_domanda_ambigua` | `quiz_question_naturalness, quiz_explanation_quality` |
| 27 | `backend/main.py:1357` | `revisiona_quiz_con_ollama` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, strong_distractors` |
| 22 | `scripts/mini_llm_real_quality_gate_v392.py:253` | `validate_report` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness` |
| 23 | `scripts/valida_mini_llm_universal_core_split_v394u.py:19` | `main` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` |
| 22 | `scripts/validatore_core_database.py:298` | `main` | `quiz_question_naturalness` |
| 21 | `backend/main.py:784` | `controlla_qualita_quiz` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality` |
| 21 | `scripts/qualita_linguistica.py:96` | `controlla_lingua_testo` | `grammar_accents_text_quality, quiz_question_naturalness, strong_distractors` |
| 22 | `scripts/motore_distrattori_ai_tre_forti.py:249` | `main` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` |

## Prossimo step

- Fase 5.9.6: test compatibilità sui candidati `READY_TO_COMPAT_TEST`.
- Nessun collegamento automatico al registry.
- Ogni candidato deve dimostrare almeno un miglioramento misurabile e zero peggioramenti.