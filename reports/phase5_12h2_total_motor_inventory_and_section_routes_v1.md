# INVENTARIO MOTORI TOTALI E ROUTE SEZIONI DOPO 5.12H.2

- Registry totale ufficiale: `73`
- Motori con dettaglio rilevato nei report: `8`

## Route per sezione

### Card

- Controlli qualità dalla matrice 5.12G.2: `52`
- Selector/orchestrator universali aggiunti: `8`
- Totale route sezione dopo 5.12H.2: `60`
- Fonte conteggio G.2: `g2.sections.card.expected_active_count`

Selector/orchestrator usati:

- `qm_051`
- `qm_052`
- `qm_053`
- `qm_054`
- `qm_055`
- `qm_056`
- `qm_057`
- `qm_058`

ID qualità G.2 esplicitamente esposti nel report:

- Non esposti come lista completa nel report G.2; usato conteggio ufficiale validato.

### Riassunto

- Controlli qualità dalla matrice 5.12G.2: `47`
- Selector/orchestrator universali aggiunti: `8`
- Totale route sezione dopo 5.12H.2: `55`
- Fonte conteggio G.2: `g2.sections.summary.expected_active_count`

Selector/orchestrator usati:

- `qm_051`
- `qm_052`
- `qm_053`
- `qm_054`
- `qm_055`
- `qm_056`
- `qm_057`
- `qm_058`

ID qualità G.2 esplicitamente esposti nel report:

- Non esposti come lista completa nel report G.2; usato conteggio ufficiale validato.

### Domande studio

- Controlli qualità dalla matrice 5.12G.2: `43`
- Selector/orchestrator universali aggiunti: `8`
- Totale route sezione dopo 5.12H.2: `51`
- Fonte conteggio G.2: `g2.sections.study_questions.expected_active_count`

Selector/orchestrator usati:

- `qm_051`
- `qm_052`
- `qm_053`
- `qm_054`
- `qm_055`
- `qm_056`
- `qm_057`
- `qm_058`

ID qualità G.2 esplicitamente esposti nel report:

- `qm_048`

### Test/Quiz

- Controlli qualità dalla matrice 5.12G.2: `55`
- Selector/orchestrator universali aggiunti: `8`
- Totale route sezione dopo 5.12H.2: `63`
- Fonte conteggio G.2: `g2.sections.test_quiz.expected_active_count`

Selector/orchestrator usati:

- `qm_051`
- `qm_052`
- `qm_053`
- `qm_054`
- `qm_055`
- `qm_056`
- `qm_057`
- `qm_058`

ID qualità G.2 esplicitamente esposti nel report:

- `qm_048`

## Motori selector/orchestrator universali aggiunti

| Motore | Nome | Ruolo | Universale | Usato da |
|---|---|---|---|---|
| `qm_051` | section_intent_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz |
| `qm_052` | section_capability_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz |
| `qm_053` | contextual_duplicate_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz |
| `qm_054` | quality_route_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz |
| `qm_055` | section_execution_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz |
| `qm_056` | quality_conflict_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz |
| `qm_057` | section_readiness_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz |
| `qm_058` | orchestration_audit_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz |

## Inventario motori rilevati nei report

| Motore | Nome | Ruolo | Universale | Usato da | Fonte |
|---|---|---|---|---|---|
| `qm_051` | section_intent_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |
| `qm_052` | section_capability_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |
| `qm_053` | contextual_duplicate_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |
| `qm_054` | quality_route_selector | selector | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |
| `qm_055` | section_execution_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |
| `qm_056` | quality_conflict_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |
| `qm_057` | section_readiness_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |
| `qm_058` | orchestration_audit_orchestrator | orchestrator | sì | Card, Riassunto, Domande studio, Test/Quiz | `reports/phase5_12h1_registry_connector_65_to_73_qm_051_qm_058_v1.json` |

## Note trasparenza

- Il totale registry ufficiale dopo H.1/H.2 è 73.
- I motori qm_051–qm_058 sono dettagliati perché ricostruiti e collegati nelle fasi 5.12H e 5.12H.1.
- Per i motori storici precedenti, il report mostra tutti i metadati realmente trovati nei JSON disponibili; non inventa nomi o descrizioni mancanti.
- Le route sezione usano i conteggi ufficiali della matrice 5.12G.2 più gli 8 selector/orchestrator universali aggiunti.
