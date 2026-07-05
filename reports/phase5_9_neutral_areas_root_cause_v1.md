# Fase 5.9 — Neutral Areas Root Cause V1

- Status: `PASS_DIAGNOSTIC`
- Aree neutre analizzate: `summary, quiz`

## Cause per area

| Area | Motori area | Applicati | Cambiati | No-op | Structure reject | Guard reject | Causa sintetica |
|---|---:|---:|---:|---:|---:|---:|---|
| `summary` | 4 | 5 | 4 | 1 | 1 | 0 | Almeno un motore dell'area viene applicato ma non cambia nulla.; Almeno un motore cambia contenuto, ma non riduce le metriche problematiche dell'area.; Almeno un motore viene limitato dalla guardia struttura.; Il riassunto non riduce bad patterns: l'adapter summary non sta normalizzando difetti testuali misurati. |
| `quiz` | 2 | 3 | 1 | 2 | 0 | 0 | Almeno un motore dell'area viene applicato ma non cambia nulla.; Almeno un motore cambia contenuto, ma non riduce le metriche problematiche dell'area.; Il quiz non riduce il rischio distrattori veri: serve motore/adattatore quiz specifico. |

## Motori rilevanti


### summary

| Motore | Target kind | Status | Applied | Changed | Target | Note |
|---|---|---|---:|---:|---|---|
| `scripts.rag_cleaner_finale_universale_v35k.clean_output` | `summary` | `ok` | 1 | 0 | `riassunto_qualita` | Il motore viene applicato ma non modifica il contenuto.; Almeno un output è rifiutato perché non preserva la struttura del target. |
| `scripts.rag_motore_test_riutilizzabile_v35d.refine_output` | `summary` | `ok` | 1 | 1 | `riassunto_qualita` | Il motore modifica contenuto senza rifiuti; va verificato se modifica i difetti giusti. |
| `scripts.rag_revisore_accordo_pronomi_v35j.improve_output` | `summary` | `ok` | 1 | 1 | `riassunto_qualita` | Il motore modifica contenuto senza rifiuti; va verificato se modifica i difetti giusti. |
| `scripts.rag_revisore_qualita_testuale_v35g.refine_output` | `summary` | `ok` | 1 | 1 | `riassunto_qualita` | Il motore modifica contenuto senza rifiuti; va verificato se modifica i difetti giusti. |
| `scripts.rag_revisore_qualita_testuale_v35g.refine_study` | `full_output` | `ok` | 1 | 1 | `phase5_full_output` | Il motore modifica contenuto senza rifiuti; va verificato se modifica i difetti giusti. |

### quiz

| Motore | Target kind | Status | Applied | Changed | Target | Note |
|---|---|---|---:|---:|---|---|
| `backend.main.pulisci_qualita_linguistica_quiz` | `quiz` | `ok` | 1 | 0 | `test_quiz` | Il motore viene applicato ma non modifica il contenuto. |
| `scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests` | `quiz` | `ok` | 1 | 0 | `test_quiz` | Il motore viene applicato ma non modifica il contenuto. |
| `scripts.rag_revisore_qualita_testuale_v35g.refine_study` | `full_output` | `ok` | 1 | 1 | `phase5_full_output` | Il motore modifica contenuto senza rifiuti; va verificato se modifica i difetti giusti. |

## Raccomandazioni

- **Priorità 1 — quiz**: Creare motore/adattatore quiz-specifico per sostituire distrattori che sono fatti veri. Motivo: Il rischio distrattori veri resta invariato.
- **Priorità 2 — summary**: Creare adapter summary più mirato o cleaner summary-specifico. Motivo: I motori summary vengono eseguiti, ma non riducono i bad patterns misurati.