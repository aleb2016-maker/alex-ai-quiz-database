# FASE 5.13A.3 — CARD ROUTE 60 STRICT CONNECTOR

Status: `PASS - Fase 5.13A.3: CARD_ROUTE_60_STRICT_CONNECTOR_READY`

## Sintesi

- Controlli attesi: `60`
- Controlli collegati: `60`
- Controlli eseguiti: `60`
- Controlli passati: `60`
- Controlli falliti: `0`
- Card controllate: `4`

## Route Card 60

| Slot | QM | Nome | Gruppo | Executor |
|---:|---|---|---|---|
| 1 | `qm_001` | Grammatica italiana corretta | Controlli qualità testuale | `exec_grammar` |
| 2 | `qm_002` | Accenti corretti | Controlli qualità testuale | `exec_accents` |
| 3 | `qm_003` | Apostrofi corretti | Controlli qualità testuale | `exec_apostrophes` |
| 4 | `qm_004` | Punteggiatura corretta | Controlli qualità testuale | `exec_punctuation` |
| 5 | `qm_005` | Spazi corretti prima/dopo punteggiatura | Controlli qualità testuale | `exec_spacing` |
| 6 | `qm_006` | Frasi complete | Controlli qualità testuale | `exec_complete_sentences` |
| 7 | `qm_007` | Assenza di frasi spezzate | Controlli qualità testuale | `exec_broken_sentences` |
| 8 | `qm_008` | Assenza di frasi non terminate | Controlli qualità testuale | `exec_unfinished_sentences` |
| 9 | `qm_009` | Assenza di finali sospetti | Controlli qualità testuale | `exec_suspicious_endings` |
| 10 | `qm_010` | Assenza di frasi riempitive | Controlli qualità testuale | `exec_no_filler` |
| 11 | `qm_011` | Assenza di testo generico | Controlli qualità testuale | `exec_no_generic` |
| 12 | `qm_012` | Assenza di vecchi fallback/demo/test | Controlli qualità testuale | `exec_no_fallback` |
| 13 | `qm_013` | Domande studio naturali | Controlli qualità didattica | `exec_didactic_natural` |
| 14 | `qm_014` | Domande studio utili per ripassare | Controlli qualità didattica | `exec_useful_for_review` |
| 15 | `qm_015` | Risposte guida specifiche | Controlli qualità didattica | `exec_specific_guidance` |
| 16 | `qm_017` | Spiegazioni non troppo corte | Controlli qualità didattica | `exec_not_too_short_explanations` |
| 17 | `qm_018` | Tono didattico finale | Controlli qualità didattica | `exec_final_didactic_tone` |
| 18 | `qm_019` | Categorie presenti | Controlli qualità didattica | `exec_categories_present` |
| 19 | `qm_020` | Sottocategorie presenti | Controlli qualità didattica | `exec_subcategories_present` |
| 20 | `qm_021` | Coerenza tra domanda, risposta e contenuto | Controlli qualità didattica | `exec_question_answer_content_coherence` |
| 21 | `qm_022` | Niente risposte vaghe | Controlli qualità didattica | `exec_no_vague_answers` |
| 22 | `qm_023` | Card scritte bene | Controlli card / riassunto / fonti | `exec_cards_well_written` |
| 23 | `qm_024` | Card non troppo corte | Controlli card / riassunto / fonti | `exec_cards_not_short` |
| 24 | `qm_025` | Card non troppo compresse | Controlli card / riassunto / fonti | `exec_cards_not_compressed` |
| 25 | `qm_026` | Messaggio chiave completo | Controlli card / riassunto / fonti | `exec_key_message_complete` |
| 26 | `qm_027` | Riassunto chiaro | Controlli card / riassunto / fonti | `exec_summary_clear_for_card` |
| 27 | `qm_028` | Punti chiave leggibili | Controlli card / riassunto / fonti | `exec_key_points_legible` |
| 28 | `qm_029` | Fonti visibili belle | Controlli card / riassunto / fonti | `exec_sources_visible_beautiful` |
| 29 | `qm_030` | Fonti coerenti | Controlli card / riassunto / fonti | `exec_sources_coherent` |
| 30 | `qm_031` | Niente fonti brutte | Controlli card / riassunto / fonti | `exec_no_ugly_sources` |
| 31 | `qm_032` | Layout grafico controllato | Controlli card / riassunto / fonti | `exec_layout_controlled` |
| 32 | `qm_033` | Test separato da card/riassunto/domande studio | Controlli test separati | `exec_test_separated` |
| 33 | `qm_034` | Opzioni interne validate | Controlli test separati | `exec_options_internal_validated` |
| 34 | `qm_035` | Opzioni visibili pulite | Controlli test separati | `exec_visible_options_clean` |
| 35 | `qm_038` | Mappa sicura tra risposta interna e visibile | Controlli test separati | `exec_safe_answer_map` |
| 36 | `qm_039` | 4 opzioni per domanda | Controlli test separati | `exec_four_options` |
| 37 | `qm_040` | Risposta corretta presente tra le opzioni | Controlli test separati | `exec_correct_in_options` |
| 38 | `qm_042` | Niente opzioni duplicate nella stessa domanda | Controlli test separati | `exec_no_duplicate_options` |
| 39 | `qm_043` | Niente ripetizioni globali eccessive | Controlli test separati | `exec_no_global_repetitions` |
| 40 | `qm_044` | Compatibilità obbligatoria col bridge motori quiz V3.5B | Controlli test separati | `exec_bridge_compatibility` |
| 41 | `qm_045` | Duplicati esatti | Controlli duplicati e ripetizioni | `exec_exact_duplicates` |
| 42 | `qm_046` | Quasi duplicati | Controlli duplicati e ripetizioni | `exec_near_duplicates` |
| 43 | `qm_047` | Ripetizioni inutili | Controlli duplicati e ripetizioni | `exec_useless_repetitions` |
| 44 | `qm_048` | Ripetizioni meccaniche tra domande | Controlli duplicati e ripetizioni | `exec_mechanical_repetitions_between_questions` |
| 45 | `qm_049` | Frasi troppo simili | Controlli duplicati e ripetizioni | `exec_too_similar_sentences` |
| 46 | `qm_050` | Stesso contenuto ripetuto senza motivo | Controlli duplicati e ripetizioni | `exec_same_content_without_reason` |
| 47 | `qm_051` | Il compito richiesto deve selezionare i motori giusti | Controlli selezionatore / orchestratore | `exec_select_right_motors` |
| 48 | `qm_052` | Riassunto → motore didattico | Controlli selezionatore / orchestratore | `exec_summary_route_not_required` |
| 49 | `qm_053` | Card → motore didattico + layout | Controlli selezionatore / orchestratore | `exec_card_didactic_layout_route` |
| 50 | `qm_054` | Domande studio → motore didattico | Controlli selezionatore / orchestratore | `exec_study_route_not_required` |
| 51 | `qm_055` | Test → bridge quiz + motore test + bridge quiz | Controlli selezionatore / orchestratore | `exec_test_route_not_required` |
| 52 | `qm_056` | Completo/PDF/app/web → orchestratore | Controlli selezionatore / orchestratore | `exec_full_output_orchestrator` |
| 53 | `qm_057` | Niente motori inutili | Controlli selezionatore / orchestratore | `exec_no_useless_motors` |
| 54 | `qm_058` | Niente output non richiesto | Controlli selezionatore / orchestratore | `exec_no_unrequested_output` |
| 55 | `qm_059` | Output finale pronto per UI/PDF/app | Controlli selezionatore / orchestratore | `exec_final_output_ready` |
| 56 | `qm_060` | Report qualità sempre leggibile | Controlli selezionatore / orchestratore | `exec_quality_report_readable` |
| 57 | `qm_061` | Naturalezza linguistica anti-keyword | Controlli linguistici avanzati / repair | `exec_natural_language_antikeyword` |
| 58 | `qm_062` | Accordo grammaticale e pronomi | Controlli linguistici avanzati / repair | `exec_agreement_pronouns` |
| 59 | `qm_063` | Correzione frasi non finite con contesto | Controlli linguistici avanzati / repair | `exec_repair_unfinished_context` |
| 60 | `qm_064` | Correzione parole scritte male con lettere invertite | Controlli linguistici avanzati / repair | `exec_repair_inverted_letters` |

## Execution results

| Slot | QM | Executed | Passed | Defects |
|---:|---|---|---|---|
| 1 | `qm_001` | True | True | nessuno |
| 2 | `qm_002` | True | True | nessuno |
| 3 | `qm_003` | True | True | nessuno |
| 4 | `qm_004` | True | True | nessuno |
| 5 | `qm_005` | True | True | nessuno |
| 6 | `qm_006` | True | True | nessuno |
| 7 | `qm_007` | True | True | nessuno |
| 8 | `qm_008` | True | True | nessuno |
| 9 | `qm_009` | True | True | nessuno |
| 10 | `qm_010` | True | True | nessuno |
| 11 | `qm_011` | True | True | nessuno |
| 12 | `qm_012` | True | True | nessuno |
| 13 | `qm_013` | True | True | nessuno |
| 14 | `qm_014` | True | True | nessuno |
| 15 | `qm_015` | True | True | nessuno |
| 16 | `qm_017` | True | True | nessuno |
| 17 | `qm_018` | True | True | nessuno |
| 18 | `qm_019` | True | True | nessuno |
| 19 | `qm_020` | True | True | nessuno |
| 20 | `qm_021` | True | True | nessuno |
| 21 | `qm_022` | True | True | nessuno |
| 22 | `qm_023` | True | True | nessuno |
| 23 | `qm_024` | True | True | nessuno |
| 24 | `qm_025` | True | True | nessuno |
| 25 | `qm_026` | True | True | nessuno |
| 26 | `qm_027` | True | True | nessuno |
| 27 | `qm_028` | True | True | nessuno |
| 28 | `qm_029` | True | True | nessuno |
| 29 | `qm_030` | True | True | nessuno |
| 30 | `qm_031` | True | True | nessuno |
| 31 | `qm_032` | True | True | nessuno |
| 32 | `qm_033` | True | True | nessuno |
| 33 | `qm_034` | True | True | nessuno |
| 34 | `qm_035` | True | True | nessuno |
| 35 | `qm_038` | True | True | nessuno |
| 36 | `qm_039` | True | True | nessuno |
| 37 | `qm_040` | True | True | nessuno |
| 38 | `qm_042` | True | True | nessuno |
| 39 | `qm_043` | True | True | nessuno |
| 40 | `qm_044` | True | True | nessuno |
| 41 | `qm_045` | True | True | nessuno |
| 42 | `qm_046` | True | True | nessuno |
| 43 | `qm_047` | True | True | nessuno |
| 44 | `qm_048` | True | True | nessuno |
| 45 | `qm_049` | True | True | nessuno |
| 46 | `qm_050` | True | True | nessuno |
| 47 | `qm_051` | True | True | nessuno |
| 48 | `qm_052` | True | True | nessuno |
| 49 | `qm_053` | True | True | nessuno |
| 50 | `qm_054` | True | True | nessuno |
| 51 | `qm_055` | True | True | nessuno |
| 52 | `qm_056` | True | True | nessuno |
| 53 | `qm_057` | True | True | nessuno |
| 54 | `qm_058` | True | True | nessuno |
| 55 | `qm_059` | True | True | nessuno |
| 56 | `qm_060` | True | True | nessuno |
| 57 | `qm_061` | True | True | nessuno |
| 58 | `qm_062` | True | True | nessuno |
| 59 | `qm_063` | True | True | nessuno |
| 60 | `qm_064` | True | True | nessuno |

## Defects

- Nessuno

## Warnings

- Nessuno

## Note

- Questo report non accetta PASS se i 60 controlli Card non sono tutti collegati.
- Ogni controllo della route Card deve avere executor reale.
- Ogni executor viene eseguito sulle card finali generate.
- Se un titolo resta keyword-based, qm_013/qm_023/qm_061 falliscono.
