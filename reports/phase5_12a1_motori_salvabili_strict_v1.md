# Fase 5.12A.1 — Motori salvabili strict

- Status: **PASS**
- Ready label: `MOTORI_SALVABILI_STRICT_MAP_READY`
- Generated at: `2026-07-05T10:08:02.590790+00:00`

## Risultato

- Motori reali salvabili trovati: `11`
- Controlli atomici richiesti: `64`
- Classificazione controlli atomici: `{'DA_VERIFICARE': 1, 'DA_RICREARE': 63}`

## Motori reali salvabili

- `salvable_phase5_pipeline_5_fasi` — **Regressione pipeline 5 fasi**
  - Confidence: `HIGH`
  - Aree coperte: `['pipeline', 'orchestrator']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json']`

- `salvable_pipeline_output_ready_gate_v511` — **Gate finale Pipeline Output Ready Fase 5.11**
  - Confidence: `HIGH`
  - Aree coperte: `['summary', 'card', 'quiz', 'study', 'registry']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/motori_qualita_esistenti_v1.json']`

- `salvable_final_registry_quality_snapshot_v5102` — **Snapshot qualità registry finale Fase 5.10.2**
  - Confidence: `HIGH`
  - Aree coperte: `['registry', 'quality_snapshot']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json']`

- `salvable_summary_card_cleaner_registry_v5101` — **Cleaner summary/card collegato al registry Fase 5.10.1**
  - Confidence: `HIGH`
  - Aree coperte: `['summary', 'card', 'cleaner']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/motori_qualita_esistenti_v1.json']`

- `salvable_universal_quiz_quality_registry_v599` — **Registry qualità quiz universale Fase 5.9.9**
  - Confidence: `HIGH`
  - Aree coperte: `['quiz', 'test']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json']`

- `salvable_quiz_repair_registry_integration_v593` — **Integrazione registry riparatore quiz Fase 5.9.3**
  - Confidence: `HIGH`
  - Aree coperte: `['quiz', 'repair']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json']`

- `salvable_legacy_quality_motors_registry_ready` — **Registry motori qualità legacy ready**
  - Confidence: `HIGH`
  - Aree coperte: `['registry', 'legacy_quality']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json']`

- `salvable_phase5_live_quality_bridge` — **Bridge qualità live Fase 5**
  - Confidence: `HIGH`
  - Aree coperte: `['bridge', 'orchestrator']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json', 'reports/motori_qualita_esistenti_v1.json']`

- `salvable_mini_llm_engine_registry_v400` — **Mini LLM engine registry V400**
  - Confidence: `HIGH`
  - Aree coperte: `['engine_registry']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/phase5_9_3_quiz_repair_registry_integration_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/motori_qualita_esistenti_v1.json']`

- `salvable_general_quality_motor` — **Motore qualità generale**
  - Confidence: `HIGH`
  - Aree coperte: `['general_quality']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/phase5_10_1_summary_card_cleaner_registry_v1.json', 'reports/phase5_9_9_universal_quiz_quality_registry_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json', 'reports/motori_qualita_esistenti_v1.json']`

- `salvable_visual_logic_quality_motor` — **Motore qualità logica visiva**
  - Confidence: `HIGH`
  - Aree coperte: `['visual_logic']`
  - Evidenze: `['reports/phase5_11_pipeline_output_ready_report.json', 'reports/phase5_10_2_final_registry_quality_snapshot_v1.json', 'reports/legacy_quality_motors_registry_ready_v1.json', 'reports/legacy_quality_motor_registry_v1_report.json', 'reports/compatibilita_motori_qualita_fase5_v1.json', 'reports/motori_qualita_esistenti_v1.json', 'reports/mini_llm_v400_registry/mini_llm_engine_registry_v400.json']`

## Controlli atomici da verificare

- `qm_059_selettore_orchestratore_output_finale_pronto_per_ui_pdf_app` — **Output finale pronto per UI PDF app**
  - Area: `selettore_orchestratore`
  - Motivo: Possibile copertura indiretta nei motori salvabili, ma non ancora dimostrata come controllo atomico autonomo con test dedicato.

## Controlli atomici da ricreare da zero

- `qm_001_qualita_testuale_grammatica_italiana_corretta` — **Grammatica italiana corretta**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_002_qualita_testuale_accenti_corretti` — **Accenti corretti**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_003_qualita_testuale_apostrofi_corretti` — **Apostrofi corretti**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_004_qualita_testuale_punteggiatura_corretta` — **Punteggiatura corretta**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_005_qualita_testuale_spazi_corretti_prima_e_dopo_punteggiatura` — **Spazi corretti prima e dopo punteggiatura**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_006_qualita_testuale_frasi_complete` — **Frasi complete**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_007_qualita_testuale_assenza_di_frasi_spezzate` — **Assenza di frasi spezzate**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_008_qualita_testuale_assenza_di_frasi_non_terminate` — **Assenza di frasi non terminate**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_009_qualita_testuale_assenza_di_finali_sospetti` — **Assenza di finali sospetti**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_010_qualita_testuale_assenza_di_frasi_riempitive` — **Assenza di frasi riempitive**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_011_qualita_testuale_assenza_di_testo_generico` — **Assenza di testo generico**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_012_qualita_testuale_assenza_di_vecchi_fallback_demo_test` — **Assenza di vecchi fallback demo test**
  - Area: `qualita_testuale`
  - Severità: `blocking`

- `qm_013_qualita_didattica_domande_studio_naturali` — **Domande studio naturali**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_014_qualita_didattica_domande_studio_utili_per_ripassare` — **Domande studio utili per ripassare**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_015_qualita_didattica_risposte_guida_specifiche` — **Risposte guida specifiche**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_016_qualita_didattica_spiegazioni_test_chiare` — **Spiegazioni test chiare**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_017_qualita_didattica_spiegazioni_non_troppo_corte` — **Spiegazioni non troppo corte**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_018_qualita_didattica_tono_didattico_finale` — **Tono didattico finale**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_019_qualita_didattica_categorie_presenti` — **Categorie presenti**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_020_qualita_didattica_sottocategorie_presenti` — **Sottocategorie presenti**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_021_qualita_didattica_coerenza_tra_domanda_risposta_e_contenuto` — **Coerenza tra domanda risposta e contenuto**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_022_qualita_didattica_niente_risposte_vaghe` — **Niente risposte vaghe**
  - Area: `qualita_didattica`
  - Severità: `blocking`

- `qm_023_card_riassunto_fonti_card_scritte_bene` — **Card scritte bene**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_024_card_riassunto_fonti_card_non_troppo_corte` — **Card non troppo corte**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_025_card_riassunto_fonti_card_non_troppo_compresse` — **Card non troppo compresse**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_026_card_riassunto_fonti_messaggio_chiave_completo` — **Messaggio chiave completo**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_027_card_riassunto_fonti_riassunto_chiaro` — **Riassunto chiaro**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_028_card_riassunto_fonti_punti_chiave_leggibili` — **Punti chiave leggibili**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_029_card_riassunto_fonti_fonti_visibili_belle` — **Fonti visibili belle**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_030_card_riassunto_fonti_fonti_coerenti` — **Fonti coerenti**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_031_card_riassunto_fonti_niente_fonti_brutte` — **Niente fonti brutte**
  - Area: `card_riassunto_fonti`
  - Severità: `blocking`

- `qm_032_card_riassunto_fonti_layout_grafico_controllato` — **Layout grafico controllato**
  - Area: `card_riassunto_fonti`
  - Severità: `warning`

- `qm_033_test_quiz_test_separato_da_card_riassunto_domande_studio` — **Test separato da card riassunto domande studio**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_034_test_quiz_opzioni_interne_validate` — **Opzioni interne validate**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_035_test_quiz_opzioni_visibili_pulite` — **Opzioni visibili pulite**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_036_test_quiz_risposta_corretta_interna` — **Risposta corretta interna**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_037_test_quiz_risposta_corretta_visibile` — **Risposta corretta visibile**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_038_test_quiz_mappa_sicura_tra_risposta_interna_e_visibile` — **Mappa sicura tra risposta interna e visibile**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_039_test_quiz_quattro_opzioni_per_domanda` — **Quattro opzioni per domanda**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_040_test_quiz_risposta_corretta_presente_tra_le_opzioni` — **Risposta corretta presente tra le opzioni**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_041_test_quiz_distrattori_forti` — **Distrattori forti**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_042_test_quiz_niente_opzioni_duplicate_nella_stessa_domanda` — **Niente opzioni duplicate nella stessa domanda**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_043_test_quiz_niente_ripetizioni_globali_eccessive` — **Niente ripetizioni globali eccessive**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_044_test_quiz_compatibilita_bridge_quiz_v3_5b` — **Compatibilità bridge quiz V3.5B**
  - Area: `test_quiz`
  - Severità: `blocking`

- `qm_045_duplicati_contestuali_duplicati_esatti` — **Duplicati esatti**
  - Area: `duplicati_contestuali`
  - Severità: `blocking`

- `qm_046_duplicati_contestuali_quasi_duplicati` — **Quasi duplicati**
  - Area: `duplicati_contestuali`
  - Severità: `blocking`

- `qm_047_duplicati_contestuali_ripetizioni_inutili` — **Ripetizioni inutili**
  - Area: `duplicati_contestuali`
  - Severità: `blocking`

- `qm_048_duplicati_contestuali_ripetizioni_meccaniche_tra_domande` — **Ripetizioni meccaniche tra domande**
  - Area: `duplicati_contestuali`
  - Severità: `blocking`

- `qm_049_duplicati_contestuali_frasi_troppo_simili` — **Frasi troppo simili**
  - Area: `duplicati_contestuali`
  - Severità: `blocking`

- `qm_050_duplicati_contestuali_stesso_contenuto_ripetuto_senza_motivo` — **Stesso contenuto ripetuto senza motivo**
  - Area: `duplicati_contestuali`
  - Severità: `blocking`

- `qm_051_selettore_orchestratore_il_compito_richiesto_deve_selezionare_i_motori_giusti` — **Il compito richiesto deve selezionare i motori giusti**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_052_selettore_orchestratore_riassunto_seleziona_motore_didattico` — **Riassunto seleziona motore didattico**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_053_selettore_orchestratore_card_seleziona_motore_didattico_e_layout` — **Card seleziona motore didattico e layout**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_054_selettore_orchestratore_domande_studio_selezionano_motore_didattico` — **Domande studio selezionano motore didattico**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_055_selettore_orchestratore_test_seleziona_bridge_quiz_e_motore_test` — **Test seleziona bridge quiz e motore test**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_056_selettore_orchestratore_completo_pdf_app_web_seleziona_orchestratore` — **Completo PDF app web seleziona orchestratore**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_057_selettore_orchestratore_niente_motori_inutili` — **Niente motori inutili**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_058_selettore_orchestratore_niente_output_non_richiesto` — **Niente output non richiesto**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_060_selettore_orchestratore_report_qualita_sempre_leggibile` — **Report qualità sempre leggibile**
  - Area: `selettore_orchestratore`
  - Severità: `blocking`

- `qm_061_naturalezza_linguistica_naturalezza_linguistica_anti_keyword` — **Naturalezza linguistica anti-keyword**
  - Area: `naturalezza_linguistica`
  - Severità: `blocking`

- `qm_062_accordo_grammaticale_accordo_grammaticale_e_pronomi` — **Accordo grammaticale e pronomi**
  - Area: `accordo_grammaticale`
  - Severità: `blocking`

- `qm_063_repair_contestuale_correzione_frasi_non_finite_usando_contesto_tema_sottotema_categorie_e_` — **Correzione frasi non finite usando contesto tema sottotema categorie e sottocategorie**
  - Area: `repair_contestuale`
  - Severità: `blocking`

- `qm_064_repair_ortografico_correzione_parole_con_lettere_invertite` — **Correzione parole con lettere invertite**
  - Area: `repair_ortografico`
  - Severità: `blocking`

## Regola duplicati

Il controllo duplicati va ricreato come controllo contestuale.
Non deve bocciare lo stesso concetto quando appare in card, quiz, domande studio e fonti con funzioni diverse.

## Scope guard

- created_new_motors: `False`
- deleted_existing_project_files: `False`
- changed_pipeline_5_11: `False`
- touched_ui_pdf_css_app: `False`
- classification_only: `True`
