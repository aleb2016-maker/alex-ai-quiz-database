# Fase 5.9.4 — Existing Quiz Quality Motors Map V1

- Status: `PASS_DIAGNOSTIC`
- Motori registry totali: `9`
- Motori registry target quiz: `3`
- Candidati Python trovati: `1417`
- Candidati frontend trovati: `57`

## Capability summary Python

| Capability | Candidati | Già registrati | Non registrati |
|---|---:|---:|---:|
| `quiz_question_naturalness` | 927 | 4 | 923 |
| `strong_distractors` | 567 | 3 | 564 |
| `grammar_accents_text_quality` | 204 | 3 | 201 |
| `quiz_explanation_quality` | 797 | 5 | 792 |
| `interactive_quiz_frontend` | 324 | 1 | 323 |

## Motori target quiz già nel registry

| Motor ID | Adapter | Target kind |
|---|---|---|
| `backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1` | `quiz_list` | `quiz` |
| `backend.main.pulisci_qualita_linguistica_quiz` | `dict_test_quiz` | `quiz` |
| `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests` | `legacy_answers_dict` | `quiz` |

## Candidati Python non registrati più forti

| Score | File | Funzione | Capability |
|---:|---|---|---|
| 161 | `scripts/create_quiz_package.py:727` | `crea_demo_web` | `quiz_question_naturalness, interactive_quiz_frontend, quiz_explanation_quality, strong_distractors` |
| 95 | `scripts/review_logica_visiva_strict.py:104` | `controlla_domanda` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` |
| 80 | `scripts/rag_prepara_review_quiz.py:77` | `valida_domanda` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 77 | `backend/motori_scrittura.py:3296` | `qg_validate_quiz` | `strong_distractors, interactive_quiz_frontend, quiz_question_naturalness, quiz_explanation_quality` |
| 75 | `scripts/rag_genera_quiz_json.py:19` | `crea_prompt_quiz_json` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, grammar_accents_text_quality` |
| 74 | `scripts/motore_qualita_generale.py:276` | `analizza_domanda` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` |
| 73 | `backend/test_phase5_study_quiz_v1.py:13` | `run_test` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 73 | `scripts/rag_adapter_quiz_ufficiale_v43.py:308` | `adatta_domande_esistenti` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, grammar_accents_text_quality` |
| 71 | `backend/motori_scrittura.py:5644` | `q52_validate_quiz` | `quiz_question_naturalness, strong_distractors, interactive_quiz_frontend` |
| 70 | `scripts/rag_valida_distrattori_forti.py:100` | `valuta_domanda_distrattori_forti` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` |
| 63 | `scripts/review_matematica_quick.py:127` | `controlla_domanda` | `quiz_explanation_quality, quiz_question_naturalness, strong_distractors, grammar_accents_text_quality, interactive_quiz_frontend` |
| 63 | `scripts/motore_distrattori_ai.py:141` | `analizza_domanda` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` |
| 61 | `scripts/motore_traduzione_inglese.py:69` | `main` | `quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` |
| 61 | `scripts/motore_qualita_logica_visiva_base.py:256` | `analizza_domanda_visiva` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend` |
| 58 | `scripts/verifica_adapter_refine_tests_fase5_v1.py:326` | `_normalize_back_to_phase5` | `strong_distractors, interactive_quiz_frontend, quiz_question_naturalness, quiz_explanation_quality` |
| 56 | `scripts/audit_motori_scientifici.py:240` | `valuta_domanda` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` |
| 56 | `scripts/validatore_rag_distrattori_forti_v2.py:52` | `valuta_domanda` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 55 | `scripts/rag_prepara_import_approvati.py:70` | `valida_domanda_approvata` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 55 | `scripts/validatore_core_database.py:210` | `validate_question` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` |
| 54 | `backend/legacy_quality_motor_registry_v1.py:515` | `_legacy_output_to_phase5` | `strong_distractors, interactive_quiz_frontend, quiz_explanation_quality, quiz_question_naturalness` |
| 54 | `backend/phase5_live_quality_bridge_v1.py:273` | `_legacy_refine_output_to_phase5` | `strong_distractors, interactive_quiz_frontend, quiz_explanation_quality, quiz_question_naturalness` |
| 54 | `scripts/review_inglese_quick.py:91` | `controlla_domanda` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend` |
| 53 | `scripts/estrai_motore_scientifico_da_migliorare.py:211` | `crea_file_lavoro` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` |
| 52 | `scripts/diagnosi_logica_visiva_dettagliata.py:47` | `main` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend` |
| 52 | `scripts/review_engine_quality.py:67` | `analizza_domanda` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend, grammar_accents_text_quality` |
| 52 | `scripts/estrai_biologia_da_migliorare.py:186` | `main` | `strong_distractors, quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend` |
| 52 | `scripts/audit_motori_scientifici_sorgenti.py:129` | `valuta_domanda` | `strong_distractors, quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend` |
| 48 | `backend/main_backup_fix_informatica_finale_sicura.py:1135` | `controlla_errori_tecnici_informatica` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` |
| 48 | `backend/main_backup_fix_timeout_finale_informatica.py:1135` | `controlla_errori_tecnici_informatica` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` |
| 48 | `backend/main_backup_informatica_safe_topics.py:1103` | `controlla_errori_tecnici_informatica` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` |
| 48 | `backend/main_backup_endpoint_finale_informatica.py:1135` | `controlla_errori_tecnici_informatica` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` |
| 48 | `backend/main.py:1135` | `controlla_errori_tecnici_informatica` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors` |
| 47 | `scripts/valida_mini_llm_study_pack_cli_v2.py:143` | `main` | `quiz_explanation_quality, quiz_question_naturalness, interactive_quiz_frontend, strong_distractors` |
| 46 | `scripts/migliora_logica_quarto_blocco_distrattori_forti.py:371` | `main` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 46 | `scripts/migliora_inglese_terzo_blocco_distrattori_forti.py:374` | `main` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 46 | `scripts/migliora_inglese_quarto_blocco_distrattori_forti.py:375` | `main` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 46 | `scripts/migliora_logica_secondo_blocco_distrattori_forti.py:347` | `main` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 46 | `scripts/migliora_inglese_secondo_blocco_distrattori_forti.py:376` | `main` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 46 | `scripts/migliora_logica_terzo_blocco_distrattori_forti.py:396` | `main` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |
| 46 | `scripts/migliora_inglese_primo_blocco_distrattori_forti.py:385` | `main` | `quiz_question_naturalness, strong_distractors, quiz_explanation_quality, interactive_quiz_frontend` |

## Candidati frontend/interattività

| Score | File | Capability |
|---:|---|---|
| 1130 | `demo/app.js` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend, grammar_accents_text_quality` |
| 243 | `runtime/web/quiz-engine.js` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend` |
| 231 | `demo-rag/curriculum-card-engine.js` | `quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend, strong_distractors, grammar_accents_text_quality` |
| 214 | `demo-rag/universal-document-learning-engine.js` | `quiz_question_naturalness, interactive_quiz_frontend, quiz_explanation_quality, grammar_accents_text_quality, strong_distractors` |
| 127 | `demo-rag/rag-knowledge-linked-generator-v1.js` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend, grammar_accents_text_quality` |
| 120 | `demo-rag/sport-training-document-engine.js` | `interactive_quiz_frontend, quiz_explanation_quality, quiz_question_naturalness, strong_distractors, grammar_accents_text_quality` |
| 106 | `demo-rag/long-document-rag-v42-final-fix.js` | `quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend, grammar_accents_text_quality, strong_distractors` |
| 94 | `demo-rag/rag-general-validator-v1.js` | `quiz_question_naturalness, interactive_quiz_frontend, strong_distractors, quiz_explanation_quality` |
| 70 | `demo-rag/browser-rag-engine.js` | `quiz_explanation_quality, grammar_accents_text_quality, interactive_quiz_frontend, strong_distractors, quiz_question_naturalness` |
| 63 | `runtime/web/ai-effects.js` | `interactive_quiz_frontend, strong_distractors, quiz_question_naturalness, grammar_accents_text_quality, quiz_explanation_quality` |
| 62 | `demo-rag/rag-knowledge-extractors-v1.js` | `interactive_quiz_frontend, strong_distractors, quiz_explanation_quality, quiz_question_naturalness` |
| 54 | `demo-rag/card-graphic-engine.js` | `grammar_accents_text_quality, interactive_quiz_frontend, quiz_explanation_quality` |
| 54 | `runtime/web/card-graphic-engine.js` | `grammar_accents_text_quality, interactive_quiz_frontend, quiz_explanation_quality` |
| 53 | `runtime/web/rag-large-document-progressive-summary-v2.js` | `interactive_quiz_frontend, strong_distractors, quiz_explanation_quality, quiz_question_naturalness, grammar_accents_text_quality` |
| 52 | `demo-rag/test-selezionatore-output-v35h.html` | `quiz_explanation_quality, interactive_quiz_frontend, quiz_question_naturalness, strong_distractors, grammar_accents_text_quality` |
| 50 | `demo-rag/rag-smart-pipeline-v1.js` | `quiz_question_naturalness, quiz_explanation_quality, strong_distractors, interactive_quiz_frontend` |
| 50 | `demo-rag/document-type-theme-engine.js` | `quiz_explanation_quality, quiz_question_naturalness, grammar_accents_text_quality, interactive_quiz_frontend, strong_distractors` |
| 44 | `demo-rag/rag-concept-document-engine-v46.js` | `quiz_explanation_quality, interactive_quiz_frontend, quiz_question_naturalness, strong_distractors, grammar_accents_text_quality` |
| 41 | `demo-rag/test-output-kb-clean-v34f.html` | `quiz_explanation_quality, interactive_quiz_frontend, strong_distractors, quiz_question_naturalness` |
| 33 | `demo-rag/ocr-document-reader-engine.js` | `interactive_quiz_frontend, strong_distractors, grammar_accents_text_quality` |
| 31 | `demo-rag/style.css` | `quiz_explanation_quality, grammar_accents_text_quality, quiz_question_naturalness, strong_distractors` |
| 25 | `demo-rag/rag-quality-summary-cards-v34a.js` | `interactive_quiz_frontend, quiz_explanation_quality, grammar_accents_text_quality, strong_distractors` |
| 23 | `demo/style.css` | `quiz_question_naturalness, quiz_explanation_quality, interactive_quiz_frontend, strong_distractors` |
| 19 | `runtime/web/rag-large-document-manager-v1.js` | `strong_distractors` |
| 16 | `demo-rag/long-document-rag-v42-final-fix.css` | `quiz_question_naturalness, grammar_accents_text_quality, quiz_explanation_quality` |
| 16 | `runtime/web/final-reward-engine.js` | `strong_distractors, interactive_quiz_frontend, quiz_question_naturalness, quiz_explanation_quality` |
| 13 | `demo-rag/layout-rigido-generazione-subito.js` | `quiz_explanation_quality, interactive_quiz_frontend` |
| 12 | `demo-rag/test-rag-pipeline-intelligente-v1.html` | `interactive_quiz_frontend, quiz_question_naturalness, strong_distractors, grammar_accents_text_quality` |
| 11 | `demo-rag/test-documenti-universale.html` | `interactive_quiz_frontend, quiz_explanation_quality, strong_distractors` |
| 11 | `demo-rag/pdf-export-browser-v6.js` | `quiz_question_naturalness, interactive_quiz_frontend, strong_distractors, grammar_accents_text_quality` |

## Raccomandazioni

- **Priorità 1 — quiz_backend_mapping**: Verificare quali motori quiz già esistenti sono candidati ma non ancora nel registry. Motivo: Il registry ora corregge i distrattori veri, ma restano naturalezza domanda, ripetitività e spiegazioni.
- **Priorità 2 — quiz_question_naturalness**: Creare shortlist e test compatibilità per candidati non registrati. Motivo: Trovati 923 candidati non registrati per capability quiz_question_naturalness.
- **Priorità 2 — strong_distractors**: Creare shortlist e test compatibilità per candidati non registrati. Motivo: Trovati 564 candidati non registrati per capability strong_distractors.
- **Priorità 2 — grammar_accents_text_quality**: Creare shortlist e test compatibilità per candidati non registrati. Motivo: Trovati 201 candidati non registrati per capability grammar_accents_text_quality.
- **Priorità 2 — quiz_explanation_quality**: Creare shortlist e test compatibilità per candidati non registrati. Motivo: Trovati 792 candidati non registrati per capability quiz_explanation_quality.
- **Priorità 2 — interactive_quiz_frontend**: Creare shortlist e test compatibilità per candidati non registrati. Motivo: Trovati 323 candidati non registrati per capability interactive_quiz_frontend.
- **Priorità 3 — interactive_quiz_frontend**: Trattare visibilità risposta corretta, click, feedback e punteggio come test frontend separato. Motivo: La comparsa della risposta corretta dopo il click non è un motore backend: è comportamento UI/JS da validare nella pagina.