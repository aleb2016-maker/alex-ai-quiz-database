# Fase 5.9.6 — Quiz Motor Compatibility Inspection V1

- Status: `PASS_DIAGNOSTIC`
- Candidati READY 5.9.5 analizzati: `60`

## Conteggi

| Verdetto | Conteggio |
|---|---:|
| `COMPAT_TEST_READY` | 35 |
| `MANUAL_REVIEW_MIXED` | 11 |
| `REVIEW_SIDE_EFFECT_RISK` | 5 |
| `VALIDATOR_OR_REPORT_ONLY` | 3 |
| `LOW_CONFIDENCE` | 6 |
| `REJECT` | 0 |

## COMPAT_TEST_READY

| Original score | File | Funzione | Args | Quiz score | Transform score | Note |
|---:|---|---|---|---:|---:|---|
| 74 | `scripts/motore_qualita_generale.py:276` | `analizza_domanda` | `nome_motore, indice, domanda` | 59 | 87 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 73 | `scripts/rag_adapter_quiz_ufficiale_v43.py:308` | `adatta_domande_esistenti` | `domande, categoria, sottocategoria` | 57 | 59 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 61 | `scripts/motore_qualita_logica_visiva_base.py:256` | `analizza_domanda_visiva` | `indice, domanda` | 50 | 76 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 56 | `scripts/validatore_rag_distrattori_forti_v2.py:52` | `valuta_domanda` | `domanda, indice` | 49 | 48 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 41 | `backend/motori_scrittura.py:3510` | `qg_clean_output_bundle` | `output_result` | 47 | 39 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 54 | `backend/phase5_live_quality_bridge_v1.py:273` | `_legacy_refine_output_to_phase5` | `value, original_value` | 40 | 51 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 36 | `backend/phase5_quiz_true_distractor_repair_v1.py:212` | `repair_quiz_true_distractors_v1` | `quiz` | 36 | 35 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 26 | `scripts/motore_qualita_generale.py:400` | `trova_duplicati_e_simili` | `domande_analizzate, soglia_similarita` | 26 | 29 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 9 | `backend/main.py:469` | `normalizza_quiz_generato` | `dati_quiz` | 24 | 12 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 14 | `backend/phase5_quiz_true_distractor_repair_v1.py:298` | `repair_payload_quiz_true_distractors_v1` | `payload` | 22 | 18 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 21 | `scripts/rag_revisore_qualita_testuale_v35g.py:341` | `refine_tests` | `data` | 18 | 23 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 30 | `scripts/applica_v35k_reale.py:173` | `clean_output` | `data` | 17 | 33 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 17 | `scripts/motore_qualita_logica_visiva_base.py:377` | `analizza_file` | `percorso` | 17 | 22 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 18 | `scripts/rag_prepara_import_approvati.py:137` | `normalizza_per_database` | `domanda, posizione` | 16 | 19 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 23 | `scripts/report_distrattori_scientifici.py:123` | `valuta_qualita_opzioni` | `opzioni, risposta` | 15 | 28 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 17 | `scripts/estrai_biologia_da_migliorare.py:54` | `normalizza_opzioni` | `opzioni_grezze` | 15 | 23 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 17 | `scripts/estrai_motore_scientifico_da_migliorare.py:79` | `normalizza_opzioni` | `opzioni_grezze` | 15 | 23 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 15 | `scripts/rag_bridge_motori_qualita_esistenti_v35b.py:104` | `analizza_domanda_se_possibile` | `self, domanda` | 15 | 18 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 14 | `scripts/improve_answer_options_100.py:504` | `applica_miglioramenti` | `domande` | 13 | 17 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 19 | `scripts/estrai_biologia_da_migliorare.py:127` | `valuta_problemi_qualita` | `opzioni, risposta` | 12 | 24 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 19 | `scripts/estrai_motore_scientifico_da_migliorare.py:152` | `valuta_problemi_qualita` | `opzioni, risposta` | 12 | 24 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 11 | `scripts/report_distrattori_scientifici.py:61` | `normalizza_opzioni` | `opzioni_grezze` | 12 | 15 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 14 | `backend/quiz_generator.py:2` | `genera_quiz_json` | `categoria, difficolta, numero_domande` | 11 | 15 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 14 | `scripts/motore_traduzione_inglese.py:33` | `rimuovi_vecchie_traduzioni` | `spiegazione` | 11 | 14 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 23 | `scripts/rag_adapter_quiz_ufficiale_v43.py:93` | `crea_candidate_sicurezza` | `testo` | 10 | 8 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 13 | `scripts/rag_genera_output_da_kb_clean_v34e.py:545` | `valida_output` | `output, numero` | 9 | 26 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 8 | `scripts/validatore_rag_distrattori_forti_v2.py:43` | `estrai_opzioni` | `domanda` | 8 | 11 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 10 | `scripts/mini_llm_study_pack_cli_v1.py:101` | `format_markdown` | `payload` | 7 | 34 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 18 | `scripts/applica_v35k_reale.py:111` | `clean_text` | `value` | 7 | 13 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 12 | `scripts/rag_revisore_qualita_testuale_v35g.py:407` | `collect_visible_records` | `data` | 7 | 13 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 14 | `scripts/rag_revisore_naturalezza_antikeyword_v35i.py:238` | `natural_test_explanation` | `title, correct, idx` | 7 | 8 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 11 | `scripts/rag_motore_didattico_riutilizzabile_v35c.py:266` | `visible_texts` | `output` | 6 | 17 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 15 | `scripts/report_distrattori_scientifici.py:81` | `normalizza_risposta` | `risposta_grezza, opzioni` | 5 | 19 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 15 | `scripts/estrai_biologia_da_migliorare.py:85` | `normalizza_risposta` | `risposta_grezza, opzioni` | 4 | 19 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 15 | `scripts/estrai_motore_scientifico_da_migliorare.py:110` | `normalizza_risposta` | `risposta_grezza, opzioni` | 4 | 19 | Sembra trasformativo, orientato al quiz e con firma adattabile.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |

## REVIEW_SIDE_EFFECT_RISK

| Original score | File | Funzione | Side effect score | Note |
|---:|---|---|---:|---|
| 19 | `backend/main.py:2558` | `generate_informatica_final_json` | 3 | Possibili effetti collaterali: file, rete, subprocess, print o input.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 53 | `scripts/estrai_motore_scientifico_da_migliorare.py:211` | `crea_file_lavoro` | 11 | Possibili effetti collaterali: file, rete, subprocess, print o input.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 10 | `scripts/mini_llm_v4003_production_suite.py:75` | `run_one` | 3 | Possibili effetti collaterali: file, rete, subprocess, print o input.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 10 | `scripts/mini_llm_v4004_production_suite.py:75` | `run_one` | 3 | Possibili effetti collaterali: file, rete, subprocess, print o input.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 10 | `scripts/mini_llm_v4005_production_suite.py:75` | `run_one` | 3 | Possibili effetti collaterali: file, rete, subprocess, print o input.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |

## VALIDATOR_OR_REPORT_ONLY

| Original score | File | Funzione | Validator score | Transform score | Note |
|---:|---|---|---:|---:|---|
| 14 | `scripts/check_duplicates_base.py:90` | `controlla_opzioni_duplicate` | 5 | 17 | Sembra più validatore/report che motore trasformativo.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |
| 10 | `scripts/rag_revisore_naturalezza_antikeyword_v35i.py:386` | `improve_output` | 2 | 1 | Sembra più validatore/report che motore trasformativo.; Firma a 2-3 argomenti: adattabile con wrapper controllato. |
| 8 | `scripts/rag_ocr_server_locale.py:287` | `analizza_testo` | 0 | 1 | Sembra più validatore/report che motore trasformativo.; Firma a 1 argomento: adattabile facilmente a quiz/payload. |

## Prossimo step

- Fase 5.9.7: runtime test solo sui candidati `COMPAT_TEST_READY`.
- Nessun collegamento al registry finché non dimostrano miglioramento misurabile.
- I validator/report restano utili come gate, ma non come motori trasformativi.