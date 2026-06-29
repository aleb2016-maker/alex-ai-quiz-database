# RAG Pipeline Unica Ufficiale

- Creato il: 2026-06-29T17:01:51
- Input: `/Users/alessandrobarbarossa/alex-ai-workspace/rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- Output finale interno V35K: `dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json`
- Output pubblico pacchetto unico: `dist/generated/rag_pipeline_unica_ufficiale/sicurezza_reale_pacchetto_unico/output_finale_rag_pipeline_unica.json`

## Motori collegati automaticamente

- `rag_build_knowledge_base_v34b.py`
- `rag_quality_gate_kb_v34d.py`
- `rag_genera_output_da_kb_clean_v34e.py`
- `rag_bridge_motori_qualita_esistenti_v35b.py`
- `rag_motore_didattico_riutilizzabile_v35c.py`
- `rag_motore_test_riutilizzabile_v35d.py`
- `rag_orchestratore_riutilizzabile_v35e.py`
- `rag_selezionatore_motori_riutilizzabile_v35f.py`
- `rag_revisore_qualita_testuale_v35g.py`
- `rag_revisore_naturalezza_antikeyword_v35i.py`
- `rag_revisore_accordo_pronomi_v35j.py`
- `applica_v35k_universale.py`
- `rag_micro_rifinitura_universale_v35l.py`

## Esito finale

- Riassunto presente: True
- Card: 5
- Domande studio: 5
- Test: 5
- Quality OK: True
- Cleaner V35K OK: True

## Note architetturali

- I motori restano separati solo internamente come moduli riutilizzabili.
- L'uso ufficiale passa da un solo entrypoint.
- Nessun collegamento manuale tra motori è richiesto all'utente.
- Il lane interno `sicurezza_reale` resta solo compatibilità tecnica temporanea con la catena V35 già esistente.
- L'output pubblico viene copiato nello spazio della pipeline unica con slug documento.

## Controlli non bloccanti

- `rag_revisore_accordo_pronomi_v35j.py` ha segnalato un controllo rigido, ma il cleaner finale V35K ha validato l'output.
