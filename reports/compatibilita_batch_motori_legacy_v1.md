# Compatibilità batch motori legacy V1

- Creato: `2026-07-05T10:05:35`
- Totale testati: `18`
- Accettati per studio adapter: `9`
- Cambiano senza peggiorare: `7`

| Accettato | Best | Payload | Peggiora in qualche caso | Funzione |
|---|---|---|---|---|
| ✅ | `changed_no_worse` | `phase5_full_output` | ⚠️ | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_output` |
|  | `exception` | `plain_text` | ⚠️ | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_summary` |
|  | `exception` | `plain_text` | ⚠️ | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_cards` |
| ✅ | `changed_no_worse` | `cards_list` |  | `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions` |
| ✅ | `changed_no_worse` | `summary_dict` |  | `scripts.rag_revisore_qualita_testuale_v35g.refine_output` |
| ✅ | `unchanged_no_worse` | `plain_text` |  | `scripts.rag_revisore_qualita_testuale_v35g.refine_summary` |
| ✅ | `unchanged_no_worse` | `summary_dict` |  | `scripts.rag_revisore_qualita_testuale_v35g.refine_cards` |
| ✅ | `changed_no_worse` | `phase5_full_output` |  | `scripts.rag_revisore_qualita_testuale_v35g.refine_study` |
|  | `none` | `None` |  | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_output` |
|  | `none` | `None` |  | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_summary` |
|  | `none` | `None` |  | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_cards` |
|  | `none` | `None` |  | `scripts.rag_revisore_naturalezza_antikeyword_v35i.improve_study` |
| ✅ | `changed_no_worse` | `summary_dict` |  | `scripts.rag_revisore_accordo_pronomi_v35j.improve_output` |
|  | `none_output` | `summary_dict` |  | `scripts.rag_revisore_accordo_pronomi_v35j.improve_summary` |
|  | `none_output` | `summary_dict` |  | `scripts.rag_revisore_accordo_pronomi_v35j.improve_cards` |
|  | `none_output` | `summary_dict` |  | `scripts.rag_revisore_accordo_pronomi_v35j.improve_study` |
| ✅ | `changed_no_worse` | `summary_dict` |  | `scripts.rag_cleaner_finale_universale_v35k.clean_output` |
| ✅ | `changed_no_worse` | `summary_dict` |  | `scripts.rag_motore_test_riutilizzabile_v35d.refine_output` |