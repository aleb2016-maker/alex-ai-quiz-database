# Fase 5.9.10B — Quality Capability Matrix Clean V1

- Status: `PASS_DIAGNOSTIC`
- Capacità mappate: `32`
- Righe riclassificate/ripulite: `32`

## Conteggi puliti

| Stato | Conteggio |
|---|---:|
| `CONNECTED_IN_REGISTRY` | 9 |
| `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | 22 |
| `NOT_FOUND` | 1 |

## Matrice pulita

| Area | Capacità | Stato originale | Stato pulito | Registry hit | Source hit principali |
|---|---|---|---|---|---|
| `qualita_testuale` | `grammatica_italiana_corretta` | `CONNECTED_IN_REGISTRY` | `CONNECTED_IN_REGISTRY` | `backend.main.pulisci_qualita_linguistica_quiz` | `scripts/verifica_rag_revisore_qualita_testuale_v35g.py`, `scripts/installa_rag_adapter_quiz_ufficiale_v43.py`, `scripts/rag_adapter_quiz_ufficiale_v43.py` |
| `qualita_testuale` | `accenti_corretti` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_lucidatore_linguistico_universale_v35m.py`, `scripts/rag_revisore_qualita_testuale_v35g.py`, `backend/motori_scrittura.py` |
| `qualita_testuale` | `apostrofi_corretti` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_lucidatore_linguistico_universale_v35m.py`, `scripts/rag_revisore_qualita_testuale_v35g.py`, `backend/motori_scrittura.py` |
| `qualita_testuale` | `punteggiatura_spazi` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `scripts/rag_micro_rifinitura_universale_v35l.py`, `scripts/mappa_phase5_9_4_existing_quiz_quality_motors_v1.py` |
| `qualita_testuale` | `frasi_complete_non_spezzate` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_revisore_qualita_testuale_v35g.py`, `scripts/verifica_rag_revisore_qualita_testuale_v35g.py`, `scripts/test_modelli_ollama_riassunto_v2a35.py` |
| `qualita_testuale` | `no_riempitivi_generico_fallback` | `CONNECTED_IN_REGISTRY` | `CONNECTED_IN_REGISTRY` | `scripts.rag_motore_test_riutilizzabile_v35d.refine_output`, `scripts.rag_revisore_qualita_testuale_v35g.refine_output`, `scripts.rag_revisore_qualita_testuale_v35g.refine_study` | `scripts/rag_revisore_qualita_testuale_v35g.py`, `backend/motori_scrittura.py`, `scripts/rag_motore_didattico_riutilizzabile_v35c.py` |
| `qualita_testuale` | `naturalezza_anti_keyword` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_revisore_naturalezza_antikeyword_v35i.py`, `scripts/applica_v35k_reale.py`, `scripts/verifica_rag_revisore_naturalezza_antikeyword_v35i.py` |
| `qualita_testuale` | `accordo_grammaticale_pronomi` | `CONNECTED_IN_REGISTRY` | `CONNECTED_IN_REGISTRY` | `scripts.rag_revisore_accordo_pronomi_v35j.improve_output` | `scripts/verifica_rag_revisore_accordo_pronomi_v35j.py`, `scripts/rag_revisore_accordo_pronomi_v35j.py`, `scripts/rag_cleaner_finale_universale_v35k.py` |
| `qualita_testuale` | `correzione_frasi_non_finite_con_contesto` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_completatore_linguistico_probabile_v35n.py`, `scripts/rag_contesto_semantico_universale_v35o.py`, `backend/main_backup_prima_regole_tcp_finali.py` |
| `qualita_didattica` | `domande_studio_naturali_utili` | `CONNECTED_IN_REGISTRY` | `CONNECTED_IN_REGISTRY` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions` | `backend/motori_scrittura.py`, `scripts/patch_phase5_study_quiz_v1.py`, `scripts/verifica_rag_selezionatore_motori_riutilizzabile_v35f.py` |
| `qualita_didattica` | `risposte_guida_specifiche` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `scripts/patch_phase5_study_quiz_v1.py`, `backend/test_output_builder_phase_v1.py` |
| `qualita_didattica` | `spiegazioni_test_chiare_non_corte` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `CONNECTED_IN_REGISTRY` | `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1` | `backend/phase5_universal_quiz_quality_adapter_v1.py`, `scripts/mappa_phase5_9_4_existing_quiz_quality_motors_v1.py`, `scripts/verifica_phase5_9_8_universal_quiz_quality_adapter_v1.py` |
| `qualita_didattica` | `tono_didattico_categorie_sottocategorie` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_micro_rifinitura_universale_v35l.py`, `scripts/rag_revisore_qualita_testuale_v35g.py`, `scripts/create_quiz_package.py` |
| `qualita_didattica` | `coerenza_domanda_risposta_contenuto` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/main_backup_prima_regole_tcp_finali.py`, `backend/main_backup_fix_informatica_finale_sicura.py`, `backend/main_backup_prima_pulizia_linguistica.py` |
| `card_riassunto_fonti` | `card_scritte_bene_non_corte` | `CONNECTED_IN_REGISTRY` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `backend/test_phase5_quality_summary_cards_v1.py`, `scripts/patch_phase5_quality_summary_cards_v1.py` |
| `card_riassunto_fonti` | `messaggio_chiave_completo` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `backend/test_phase5_quality_summary_cards_v1.py`, `scripts/patch_phase5_quality_summary_cards_v1.py` |
| `card_riassunto_fonti` | `riassunto_chiaro_punti_chiave` | `CONNECTED_IN_REGISTRY` | `CONNECTED_IN_REGISTRY` | `scripts.rag_cleaner_finale_universale_v35k.clean_output`, `scripts.rag_revisore_accordo_pronomi_v35j.improve_output`, `scripts.rag_revisore_qualita_testuale_v35g.refine_output` | `backend/motori_scrittura.py`, `backend/test_phase5_quality_summary_cards_v1.py`, `scripts/patch_output_builder_phase_v1.py` |
| `card_riassunto_fonti` | `fonti_visibili_coerenti_belle` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_motore_didattico_riutilizzabile_v35c.py`, `scripts/rag_revisore_qualita_testuale_v35g.py`, `backend/motori_scrittura.py` |
| `card_riassunto_fonti` | `layout_grafico_controllato` | `CONNECTED_IN_REGISTRY` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `scripts/rag_motore_didattico_riutilizzabile_v35c.py`, `scripts/create_batch_100.py` |
| `quiz_test` | `test_separato_da_altri_output` | `CONNECTED_IN_REGISTRY` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/legacy_quality_motor_registry_v1.py`, `backend/motori_scrittura.py`, `scripts/patch_phase5_6_ready_safe_legacy_motors_v1.py` |
| `quiz_test` | `opzioni_interne_visibili_validate` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_motore_test_riutilizzabile_v35d.py`, `scripts/rag_revisore_qualita_testuale_v35g.py`, `scripts/fix_gate_universale_pagina_v35k.py` |
| `quiz_test` | `risposta_corretta_interna_visibile_mappa_sicura` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `backend/test_phase5_live_quality_bridge_v1.py`, `scripts/patch_phase5_live_quality_bridge_v1.py` |
| `quiz_test` | `quattro_opzioni_risposta_presente` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `backend/test_phase5_study_quiz_v1.py`, `scripts/patch_output_builder_phase_v1.py` |
| `quiz_test` | `distrattori_forti` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `CONNECTED_IN_REGISTRY` | `backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1`, `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1` | `backend/phase5_quiz_true_distractor_repair_v1.py`, `backend/motori_scrittura.py`, `scripts/mappa_phase5_9_4_existing_quiz_quality_motors_v1.py` |
| `quiz_test` | `no_opzioni_duplicate` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/correggi_duplicati_logica_visiva.py`, `scripts/check_duplicates_base.py`, `scripts/rag_revisore_qualita_testuale_v35g.py` |
| `quiz_test` | `compatibilita_bridge_quiz` | `CONNECTED_IN_REGISTRY` | `CONNECTED_IN_REGISTRY` | `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1` | `scripts/verifica_rag_motore_test_riutilizzabile_v35d.py`, `scripts/verifica_rag_bridge_motori_qualita_esistenti_v35b.py`, `scripts/rag_selezionatore_motori_riutilizzabile_v35f.py` |
| `duplicati_ripetizioni` | `duplicati_per_tipo_output_e_contesto` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/main_backup_fix_informatica_finale_sicura.py`, `backend/main_backup_fix_tecnico_informatica.py`, `backend/main_backup_fix_tcp_flow_control.py` |
| `duplicati_ripetizioni` | `ripetizioni_meccaniche_domande` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `CONNECTED_IN_REGISTRY` | `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1` | `backend/motori_scrittura.py`, `scripts/patch_super_quality_gate_phase_v1.py`, `backend/phase5_universal_quiz_quality_adapter_v1.py` |
| `selezionatore_orchestratore` | `seleziona_motori_giusti_per_compito` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_selezionatore_motori_riutilizzabile_v35f.py`, `scripts/verifica_rag_selezionatore_motori_riutilizzabile_v35f.py`, `scripts/rag_pipeline_unica_ufficiale.py` |
| `selezionatore_orchestratore` | `niente_output_non_richiesto` | `TEST_OR_VALIDATOR_ONLY` | `NOT_FOUND` | - | - |
| `selezionatore_orchestratore` | `output_pronto_ui_pdf_app` | `CONNECTED_IN_REGISTRY` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_selezionatore_motori_riutilizzabile_v35f.py`, `scripts/sistema_bottone_rag_vicino_pacchetto.py`, `scripts/rag_pipeline_unica_ufficiale.py` |
| `selezionatore_orchestratore` | `report_qualita_leggibile` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `backend/motori_scrittura.py`, `scripts/patch_phase5_quality_summary_cards_v1.py`, `scripts/patch_phase5_study_quiz_v1.py` |

## Lettura operativa corretta

- `CONNECTED_IN_REGISTRY`: capacità davvero coperta da un motore registry conosciuto.
- `EXISTS_NEEDS_ADAPTER_OR_REVIEW`: codice presente, ma non ancora trasformato in motore universale collegato.
- `FRONTEND_OR_UI_ONLY`: riguarda UI/PDF/app/browser, non registry backend.
- `TEST_OR_VALIDATOR_ONLY`: utile come gate, non come motore trasformativo.
- `NOT_FOUND`: non trovato o nome diverso.