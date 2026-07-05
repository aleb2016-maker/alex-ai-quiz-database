# Fase 5.9.7 — Quiz Motor Runtime Test V1

- Status: `PASS_DIAGNOSTIC`
- Candidati runtime testati: `35`

## Conteggi

| Status | Conteggio |
|---|---:|
| `IMPORT_ERROR` | 1 |
| `IMPROVED` | 2 |
| `NEUTRAL_USABLE_OUTPUT` | 4 |
| `NO_USABLE_OUTPUT` | 20 |
| `RUNTIME_ERROR` | 6 |
| `SKIPPED_RUNTIME_SIDE_EFFECT_RISK` | 1 |
| `SKIPPED_UNSAFE_OR_UNSUPPORTED_ARGS` | 1 |

## IMPROVED

| Motore | Adapter migliore | Bad total | Note |
|---|---|---|---|
| `backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_true_distractors_v1` | `quiz` | `5 -> 2` | Migliora true_fact_distractors: 3 -> 0 |
| `backend.phase5_quiz_true_distractor_repair_v1.repair_payload_quiz_true_distractors_v1` | `payload` | `5 -> 2` | Migliora true_fact_distractors: 3 -> 0 |

## NEUTRAL_USABLE_OUTPUT

| Motore | Adapter migliore | Bad total | Note |
|---|---|---|---|
| `backend.phase5_live_quality_bridge_v1._legacy_refine_output_to_phase5` | `payload_original` | `5 -> 5` | Nessun delta misurabile sulle metriche quiz. |
| `backend.main.normalizza_quiz_generato` | `payload` | `5 -> 5` | Nessun delta misurabile sulle metriche quiz. |
| `scripts.rag_revisore_qualita_testuale_v35g.refine_tests` | `payload` | `5 -> 5` | Nessun delta misurabile sulle metriche quiz. |
| `scripts.applica_v35k_reale.clean_output` | `payload` | `5 -> 5` | Nessun delta misurabile sulle metriche quiz. |

## NO_USABLE_OUTPUT / ERROR

| Status | Motore | Note |
|---|---|---|
| `NO_USABLE_OUTPUT` | `scripts.motore_qualita_generale.analizza_domanda` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.motore_qualita_logica_visiva_base.analizza_domanda_visiva` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.validatore_rag_distrattori_forti_v2.valuta_domanda` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `backend.motori_scrittura.qg_clean_output_bundle` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.report_distrattori_scientifici.valuta_qualita_opzioni` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.estrai_biologia_da_migliorare.normalizza_opzioni` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.estrai_motore_scientifico_da_migliorare.normalizza_opzioni` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.estrai_biologia_da_migliorare.valuta_problemi_qualita` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.estrai_motore_scientifico_da_migliorare.valuta_problemi_qualita` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.report_distrattori_scientifici.normalizza_opzioni` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.motore_traduzione_inglese.rimuovi_vecchie_traduzioni` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.rag_adapter_quiz_ufficiale_v43.crea_candidate_sicurezza` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.validatore_rag_distrattori_forti_v2.estrai_opzioni` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.applica_v35k_reale.clean_text` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.rag_revisore_qualita_testuale_v35g.collect_visible_records` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.rag_revisore_naturalezza_antikeyword_v35i.natural_test_explanation` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.rag_motore_didattico_riutilizzabile_v35c.visible_texts` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.report_distrattori_scientifici.normalizza_risposta` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.estrai_biologia_da_migliorare.normalizza_risposta` | Output non riconosciuto come quiz riutilizzabile. |
| `NO_USABLE_OUTPUT` | `scripts.estrai_motore_scientifico_da_migliorare.normalizza_risposta` | Output non riconosciuto come quiz riutilizzabile. |
| `RUNTIME_ERROR` | `scripts.rag_adapter_quiz_ufficiale_v43.adatta_domande_esistenti` |  |
| `RUNTIME_ERROR` | `scripts.motore_qualita_generale.trova_duplicati_e_simili` |  |
| `RUNTIME_ERROR` | `scripts.rag_prepara_import_approvati.normalizza_per_database` |  |
| `RUNTIME_ERROR` | `backend.quiz_generator.genera_quiz_json` |  |
| `RUNTIME_ERROR` | `scripts.rag_genera_output_da_kb_clean_v34e.valida_output` |  |
| `RUNTIME_ERROR` | `scripts.mini_llm_study_pack_cli_v1.format_markdown` |  |
| `IMPORT_ERROR` | `scripts.rag_bridge_motori_qualita_esistenti_v35b.analizza_domanda_se_possibile` | AttributeError: module 'scripts.rag_bridge_motori_qualita_esistenti_v35b' has no attribute 'analizza_domanda_se_possibile' |

## Prossimo step

- Collegare solo candidati `IMPROVED`, se presenti.
- I candidati `NEUTRAL_USABLE_OUTPUT` richiedono adapter migliore o test più specifico.
- I candidati `NO_USABLE_OUTPUT` non sono collegabili direttamente.