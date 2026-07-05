# Legacy quality motors registry-ready V1

- Creato: `2026-07-05T10:07:18`
- Totale valutati: `18`

## Conteggi

- `READY_SAFE`: `6`
- `GUARDED_ONLY`: `1`
- `NEEDS_ADAPTER`: `4`
- `LOW_PRIORITY`: `2`
- `EXCLUDE_FOR_NOW`: `5`

| Decisione | Adapter hint | Best | Payload | Funzione | Motivo |
|---|---|---|---|---|---|
| `READY_SAFE` | `summary_dict_adapter` | `changed_no_worse` | `summary_dict` | `scripts.rag_cleaner_finale_universale_v35k.clean_output` | Cambia output senza peggiorare sul payload migliore: summary_dict. |
| `READY_SAFE` | `cards_list_adapter` | `changed_no_worse` | `cards_list` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions` | Cambia output senza peggiorare sul payload migliore: cards_list. |
| `READY_SAFE` | `summary_dict_adapter` | `changed_no_worse` | `summary_dict` | `scripts.rag_motore_test_riutilizzabile_v35d.refine_output` | Cambia output senza peggiorare sul payload migliore: summary_dict. |
| `READY_SAFE` | `summary_dict_adapter` | `changed_no_worse` | `summary_dict` | `scripts.rag_revisore_accordo_pronomi_v35j.improve_output` | Cambia output senza peggiorare sul payload migliore: summary_dict. |
| `READY_SAFE` | `summary_dict_adapter` | `changed_no_worse` | `summary_dict` | `scripts.rag_revisore_qualita_testuale_v35g.refine_output` | Cambia output senza peggiorare sul payload migliore: summary_dict. |
| `READY_SAFE` | `phase5_full_output_adapter` | `changed_no_worse` | `phase5_full_output` | `scripts.rag_revisore_qualita_testuale_v35g.refine_study` | Cambia output senza peggiorare sul payload migliore: phase5_full_output. |
| `GUARDED_ONLY` | `phase5_full_output_adapter` | `changed_no_worse` | `phase5_full_output` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_output` | Ha almeno un caso di peggioramento: collegabile solo con guardia anti-peggioramento stretta. |
| `NEEDS_ADAPTER` | `custom_signature_adapter_required` | `none` | `None` | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_cards` | Firma diversa: motore interessante, ma serve adapter dedicato prima del registry. |
| `NEEDS_ADAPTER` | `custom_signature_adapter_required` | `none` | `None` | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_output` | Firma diversa: motore interessante, ma serve adapter dedicato prima del registry. |
| `NEEDS_ADAPTER` | `custom_signature_adapter_required` | `none` | `None` | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_study` | Firma diversa: motore interessante, ma serve adapter dedicato prima del registry. |
| `NEEDS_ADAPTER` | `custom_signature_adapter_required` | `none` | `None` | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_summary` | Firma diversa: motore interessante, ma serve adapter dedicato prima del registry. |
| `LOW_PRIORITY` | `summary_dict_adapter` | `unchanged_no_worse` | `summary_dict` | `scripts.rag_revisore_qualita_testuale_v35g.refine_cards` | Accetta input e non peggiora, ma nel batch non migliora/cambia output. |
| `LOW_PRIORITY` | `unknown_adapter` | `unchanged_no_worse` | `plain_text` | `scripts.rag_revisore_qualita_testuale_v35g.refine_summary` | Accetta input e non peggiora, ma nel batch non migliora/cambia output. |
| `EXCLUDE_FOR_NOW` | `unknown_adapter` | `exception` | `plain_text` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_cards` | Non ha prodotto output utile nel batch standard. |
| `EXCLUDE_FOR_NOW` | `unknown_adapter` | `exception` | `plain_text` | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_summary` | Non ha prodotto output utile nel batch standard. |
| `EXCLUDE_FOR_NOW` | `summary_dict_adapter` | `none_output` | `summary_dict` | `scripts.rag_revisore_accordo_pronomi_v35j.improve_cards` | Non ha prodotto output utile nel batch standard. |
| `EXCLUDE_FOR_NOW` | `summary_dict_adapter` | `none_output` | `summary_dict` | `scripts.rag_revisore_accordo_pronomi_v35j.improve_study` | Non ha prodotto output utile nel batch standard. |
| `EXCLUDE_FOR_NOW` | `summary_dict_adapter` | `none_output` | `summary_dict` | `scripts.rag_revisore_accordo_pronomi_v35j.improve_summary` | Non ha prodotto output utile nel batch standard. |