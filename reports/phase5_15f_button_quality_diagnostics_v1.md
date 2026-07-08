# FASE 5.15F.0 - Diagnostica reale pulsanti generatori RAG/LLM

Status diagnostica: **PASS**

## Stato baseline

- 5.15E baseline: **PASS** - conteggi osservati `{'summary': 55, 'cards': 60, 'study_questions': 51, 'quiz': 63}`
- 5.15D baseline: **PASS** - conteggi osservati `{'summary': 55, 'cards': 60, 'study_questions': 51, 'quiz': 63}`

## Stato Git

- Branch: `rag-concept-app-presentabile-v3`
- Commit: `78e2007`
- Tag su HEAD: `checkpoint-mini-llm-document-qa-backend-integration-v515g51`
- Stato git short: `M demo-rag/phase5-14-ui-buttons-real-connector.js
 M demo-rag/test-documenti-universale.html
 M reports/phase5_15e_approved_outputs_report_v1.json
 M reports/phase5_15g5_document_qa_diagnostics_v1.json
?? demo-rag/phase5-14-ui-buttons-real-connector.js.bak_g52_interroga_ui
?? demo-rag/test-documenti-universale.html.bak_g52_interroga_ui
?? reports/phase5_15g52_ui_backend_real_connection_inspection_v1.md
?? reports/phase5_15g52_ui_backend_real_connection_smoke_v1.json
?? reports/phase5_15g52_ui_backend_real_connection_smoke_v1.md
?? reports/phase5_15g52_ui_real_connector_target_context_v1.md
?? scripts/run_phase5_15g52_ui_backend_real_connection_smoke.py`

## Tabella 4 pulsanti

| Pulsante | Generatore | Motore effettivo | QM | Output reali | Approved | Problemi principali |
| --- | --- | --- | ---: | --- | --- | --- |
| Genera Riassunto | `summary` | `full_pipeline_summary_route55_all_motors_v51416` | 55/55 | [1, 1] | True | nessuno bloccante |
| Genera Card | `cards` | `full_pipeline_cards_60_motors_graphic_v51416` | 60/60 | [8, 8] | True | ripetizioni |
| Genera Test/Quiz | `quiz` | `full_pipeline_quiz_route63_language_quality_v51418` | 63/63 | [4, 4] | True | nessuno bloccante |
| Genera Domande studio | `study_questions` | `full_pipeline_study_route51_language_quality_v51418` | 51/51 | [4, 4] | True | nessuno bloccante |

## Problemi trovati per motore

### Genera Riassunto - `full_pipeline_summary_route55_all_motors_v51416`

- Classi problema: nessuna
- Difetti tecnici: nessuno
- Warning: nessuno
- Problemi RAG: nessuno
- Problemi didattici: nessuno
- Sample: Il documento spiega che la gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti. In apertura chiarisce anche che quando arriva una nuova merce, l'operatore verifica il documento di trasporto, controlla quantità e integrità degli articoli e segnala eventuali differenze. Questi elementi introducono il flusso operativo su cui si sviluppano ricezione, controllo e registrazione. La parte centrale approfondisce gli aspetti più operativi: Durante la preparazione degli ordini, il sistema genera una lista di prelievo con codice articolo, quantità richiesta e posizione. L'operatore raccoglie i prodotti, controlla che cor

### Genera Card - `full_pipeline_cards_60_motors_graphic_v51416`

- Classi problema: problema qualità RAG
- Difetti tecnici: nessuno
- Warning: radici_ripetute:analizzat,azione,collega,concreto,contenuto,degli,evidenzia,magazzino
- Problemi RAG: ripetizioni
- Problemi didattici: nessuno
- Sample: [{"card_id": "full_card_v51416_001", "titolo": "Gestione ordinata del magazzino", "messaggio_chiave": "Gestione ordini magazzino moderno: La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti.", "spiegazione": "La card evidenzia che la gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti Questo passaggio collega il contenuto del documento a un'azione operativa o a un controllo concreto.", "micro_concetti": ["gestione", "ordini", "magazzino", "moderno"], "visual": {"icon": "🏢", "theme": "business_presentable", "svg": "<svg viewBo

### Genera Test/Quiz - `full_pipeline_quiz_route63_language_quality_v51418`

- Classi problema: nessuna
- Difetti tecnici: nessuno
- Warning: nessuno
- Problemi RAG: nessuno
- Problemi didattici: nessuno
- Sample: [{"id": "quiz_quality_v51418_001", "domanda": "Quale scelta mantiene verificabile gestione ordini magazzino moderno secondo il documento?", "opzioni": [{"option_id": "A", "testo": "La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti."}, {"option_id": "B", "testo": "Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica."}, {"option_id": "C", "testo": "Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento."}, {"option_id": "D", "testo": "Usare una nota generica sul rischio senza indicare 

### Genera Domande studio - `full_pipeline_study_route51_language_quality_v51418`

- Classi problema: nessuna
- Difetti tecnici: nessuno
- Warning: nessuno
- Problemi RAG: nessuno
- Problemi didattici: nessuno
- Sample: [{"id": "study_quality_v51418_001", "domanda": "Perché la gestione degli ordini richiede una procedura chiara dall'arrivo alla spedizione?", "risposta_guida": "Ricorda il fatto concreto: La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti. La domanda chiede di collegare passaggi, responsabilità e controlli lungo l'intero flusso.", "tipo_domanda": "procedura", "livello_cognitivo": "comprensione", "fatto_origine": "La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti", "quality_rewrite": "v51418_language_quality", "fonte": "D

## Priorità di intervento

| Priorità | Pulsante | Generatore | Motore | Score | Motivo |
| ---: | --- | --- | --- | ---: | --- |
| 1 | Genera Card | `cards` | `full_pipeline_cards_60_motors_graphic_v51416` | 4 | ripetizioni |
| 2 | Genera Riassunto | `summary` | `full_pipeline_summary_route55_all_motors_v51416` | 0 | nessun problema bloccante |
| 3 | Genera Test/Quiz | `quiz` | `full_pipeline_quiz_route63_language_quality_v51418` | 0 | nessun problema bloccante |
| 4 | Genera Domande studio | `study_questions` | `full_pipeline_study_route51_language_quality_v51418` | 0 | nessun problema bloccante |

## Primo motore da migliorare

- Motore/file: `full_pipeline_cards_60_motors_graphic_v51416`
- Generatore: `cards`
- File candidato: `backend/phase5_full_pipeline_runtime_v51416.py`
- Raccomandazione: **patch mirata sui motori linguistici/didattici, nessuna patch a bridge/UI/QM**

## Distinzione problemi

- bug tecnico: nessuno
- problema qualità linguistica: nessuno
- problema qualità RAG: cards:radici_ripetute:analizzat,azione,collega,concreto,contenuto,degli,evidenzia,magazzino, cards:ripetizioni
- problema didattico: nessuno
- problema UI/bridge: nessuno
