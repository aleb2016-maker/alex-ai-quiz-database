# Fase 5.9.10 — Quality Capability Matrix V1

- Status: `PASS_DIAGNOSTIC`
- Motori registry: `10`
- Capacità mappate: `32`

## Conteggi

| Stato | Conteggio |
|---|---:|
| `CONNECTED_IN_REGISTRY` | 10 |
| `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | 21 |
| `TEST_OR_VALIDATOR_ONLY` | 1 |

## Matrice capacità

| Area | Capacità | Stato | Registry hit | Source hit principali |
|---|---|---|---|---|
| `qualita_testuale` | `grammatica_italiana_corretta` | `CONNECTED_IN_REGISTRY` | `backend.main.pulisci_qualita_linguistica_quiz` | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/verifica_rag_revisore_qualita_testuale_v35g.py`, `scripts/installa_rag_adapter_quiz_ufficiale_v43.py` |
| `qualita_testuale` | `accenti_corretti` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_lucidatore_linguistico_universale_v35m.py`, `scripts/rag_revisore_qualita_testuale_v35g.py` |
| `qualita_testuale` | `apostrofi_corretti` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_lucidatore_linguistico_universale_v35m.py`, `scripts/rag_revisore_qualita_testuale_v35g.py` |
| `qualita_testuale` | `punteggiatura_spazi` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `scripts/rag_micro_rifinitura_universale_v35l.py` |
| `qualita_testuale` | `frasi_complete_non_spezzate` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_revisore_qualita_testuale_v35g.py`, `scripts/verifica_rag_revisore_qualita_testuale_v35g.py` |
| `qualita_testuale` | `no_riempitivi_generico_fallback` | `CONNECTED_IN_REGISTRY` | `scripts.rag_motore_test_riutilizzabile_v35d.refine_output`, `scripts.rag_revisore_qualita_testuale_v35g.refine_output`, `scripts.rag_revisore_qualita_testuale_v35g.refine_study` | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_revisore_qualita_testuale_v35g.py`, `backend/motori_scrittura.py` |
| `qualita_testuale` | `naturalezza_anti_keyword` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_revisore_naturalezza_antikeyword_v35i.py`, `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/applica_v35k_reale.py` |
| `qualita_testuale` | `accordo_grammaticale_pronomi` | `CONNECTED_IN_REGISTRY` | `scripts.rag_revisore_accordo_pronomi_v35j.improve_output` | `scripts/verifica_rag_revisore_accordo_pronomi_v35j.py`, `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_revisore_accordo_pronomi_v35j.py` |
| `qualita_testuale` | `correzione_frasi_non_finite_con_contesto` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_completatore_linguistico_probabile_v35n.py`, `scripts/rag_contesto_semantico_universale_v35o.py` |
| `qualita_didattica` | `domande_studio_naturali_utili` | `CONNECTED_IN_REGISTRY` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions` | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `scripts/patch_phase5_study_quiz_v1.py` |
| `qualita_didattica` | `risposte_guida_specifiche` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `scripts/patch_phase5_study_quiz_v1.py` |
| `qualita_didattica` | `spiegazioni_test_chiare_non_corte` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/phase5_universal_quiz_quality_adapter_v1.py`, `scripts/mappa_phase5_9_4_existing_quiz_quality_motors_v1.py` |
| `qualita_didattica` | `tono_didattico_categorie_sottocategorie` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_micro_rifinitura_universale_v35l.py`, `scripts/rag_revisore_qualita_testuale_v35g.py` |
| `qualita_didattica` | `coerenza_domanda_risposta_contenuto` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/main_backup_prima_regole_tcp_finali.py`, `backend/main_backup_fix_informatica_finale_sicura.py` |
| `card_riassunto_fonti` | `card_scritte_bene_non_corte` | `CONNECTED_IN_REGISTRY` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions` | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `backend/test_phase5_quality_summary_cards_v1.py` |
| `card_riassunto_fonti` | `messaggio_chiave_completo` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `backend/test_phase5_quality_summary_cards_v1.py` |
| `card_riassunto_fonti` | `riassunto_chiaro_punti_chiave` | `CONNECTED_IN_REGISTRY` | `scripts.rag_cleaner_finale_universale_v35k.clean_output`, `scripts.rag_motore_test_riutilizzabile_v35d.refine_output`, `scripts.rag_revisore_accordo_pronomi_v35j.improve_output` | `backend/motori_scrittura.py`, `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/test_phase5_quality_summary_cards_v1.py` |
| `card_riassunto_fonti` | `fonti_visibili_coerenti_belle` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_motore_didattico_riutilizzabile_v35c.py`, `scripts/rag_revisore_qualita_testuale_v35g.py` |
| `card_riassunto_fonti` | `layout_grafico_controllato` | `CONNECTED_IN_REGISTRY` | `backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1`, `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1`, `backend.main.pulisci_qualita_linguistica_quiz` | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `scripts/rag_motore_didattico_riutilizzabile_v35c.py` |
| `quiz_test` | `test_separato_da_altri_output` | `CONNECTED_IN_REGISTRY` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions`, `backend.main.pulisci_qualita_linguistica_quiz` | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/legacy_quality_motor_registry_v1.py`, `backend/motori_scrittura.py` |
| `quiz_test` | `opzioni_interne_visibili_validate` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/rag_motore_test_riutilizzabile_v35d.py`, `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_revisore_qualita_testuale_v35g.py` |
| `quiz_test` | `risposta_corretta_interna_visibile_mappa_sicura` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `backend/test_phase5_live_quality_bridge_v1.py` |
| `quiz_test` | `quattro_opzioni_risposta_presente` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `backend/test_phase5_study_quiz_v1.py` |
| `quiz_test` | `distrattori_forti` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/phase5_quiz_true_distractor_repair_v1.py`, `backend/motori_scrittura.py` |
| `quiz_test` | `no_opzioni_duplicate` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/correggi_duplicati_logica_visiva.py`, `scripts/check_duplicates_base.py` |
| `quiz_test` | `compatibilita_bridge_quiz` | `CONNECTED_IN_REGISTRY` | `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1` | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/verifica_rag_motore_test_riutilizzabile_v35d.py`, `scripts/verifica_rag_bridge_motori_qualita_esistenti_v35b.py` |
| `duplicati_ripetizioni` | `duplicati_per_tipo_output_e_contesto` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/main_backup_fix_informatica_finale_sicura.py`, `backend/main_backup_fix_tecnico_informatica.py` |
| `duplicati_ripetizioni` | `ripetizioni_meccaniche_domande` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `scripts/patch_super_quality_gate_phase_v1.py` |
| `selezionatore_orchestratore` | `seleziona_motori_giusti_per_compito` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/rag_selezionatore_motori_riutilizzabile_v35f.py`, `scripts/verifica_rag_selezionatore_motori_riutilizzabile_v35f.py` |
| `selezionatore_orchestratore` | `niente_output_non_richiesto` | `TEST_OR_VALIDATOR_ONLY` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py` |
| `selezionatore_orchestratore` | `output_pronto_ui_pdf_app` | `CONNECTED_IN_REGISTRY` | `backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1`, `backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1`, `backend.main.pulisci_qualita_linguistica_quiz` | `scripts/rag_selezionatore_motori_riutilizzabile_v35f.py`, `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `scripts/sistema_bottone_rag_vicino_pacchetto.py` |
| `selezionatore_orchestratore` | `report_qualita_leggibile` | `EXISTS_NEEDS_ADAPTER_OR_REVIEW` | - | `scripts/verifica_phase5_9_10_quality_capability_matrix_v1.py`, `backend/motori_scrittura.py`, `scripts/patch_phase5_quality_summary_cards_v1.py` |

## Lettura operativa

- `CONNECTED_IN_REGISTRY`: capacità già collegata a un motore registry.
- `EXISTS_NEEDS_ADAPTER_OR_REVIEW`: codice presente, ma da trasformare/validare prima di collegarlo.
- `TEST_OR_VALIDATOR_ONLY`: utile come gate, ma non migliora direttamente l'output.
- `FRONTEND_OR_UI_ONLY`: riguarda UI, PDF, app o comportamento browser.
- `NOT_FOUND`: capacità non trovata con la ricerca keyword, oppure nome diverso.