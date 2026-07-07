# FASE 5.15F.0 - Diagnostica reale pulsanti generatori RAG/LLM

Status diagnostica: **PASS**

## Stato baseline

- 5.15E baseline: **PASS** - conteggi osservati `{'summary': 55, 'cards': 60, 'study_questions': 51, 'quiz': 63}`
- 5.15D baseline: **PASS** - conteggi osservati `{'summary': 55, 'cards': 60, 'study_questions': 51, 'quiz': 63}`

## Stato Git

- Branch: `rag-concept-app-presentabile-v3`
- Commit: `0444d0d`
- Tag su HEAD: `checkpoint-mini-llm-approved-generators-v515e`
- Stato git short: `M backend/phase5_15b_quality_checked_generators.py
 M reports/phase5_15d_real_page_generators_trace_v1.json
 M reports/phase5_15e_approved_outputs_report_v1.json
?? reports/phase5_15f1_quiz_patch_safety_review_v1.md
?? reports/phase5_15f_button_quality_diagnostics_v1.json
?? reports/phase5_15f_button_quality_diagnostics_v1.md
?? scripts/run_phase5_15f_button_quality_diagnostics.py`

## Tabella 4 pulsanti

| Pulsante | Generatore | Motore effettivo | QM | Output reali | Approved | Problemi principali |
| --- | --- | --- | ---: | --- | --- | --- |
| Genera Riassunto | `summary` | `full_pipeline_summary_route55_all_motors_v51416` | 55/55 | [1, 1] | True | riassunto non abbastanza profondo |
| Genera Card | `cards` | `full_pipeline_cards_60_motors_graphic_v51416` | 60/60 | [8, 8] | False | approved_non_true:False; status_non_approved:QUALITY_BLOCKED; ripetizioni |
| Genera Test/Quiz | `quiz` | `full_pipeline_quiz_route63_language_quality_v51418` | 63/63 | [4, 4] | True | nessuno bloccante |
| Genera Domande studio | `study_questions` | `full_pipeline_study_route51_language_quality_v51418` | 51/51 | [4, 4] | False | approved_non_true:False; status_non_approved:QUALITY_BLOCKED; domande innaturali; genericità; perdita contesto; domande_formulaiche:4 |

## Problemi trovati per motore

### Genera Riassunto - `full_pipeline_summary_route55_all_motors_v51416`

- Classi problema: problema qualità linguistica
- Difetti tecnici: nessuno
- Warning: riassunto_non_copre_abbastanza_sezioni
- Problemi RAG: riassunto non abbastanza profondo
- Problemi didattici: nessuno
- Sample: Il documento spiega che la gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti. In apertura chiarisce anche che quando arriva una nuova merce, l'operatore verifica il documento di trasporto, controlla quantità e integrità degli articoli e segnala eventuali differenze. Questi elementi introducono il flusso operativo su cui si sviluppano ricezione, controllo e registrazione. La parte centrale approfondisce gli aspetti più operativi: Durante la preparazione degli ordini, il sistema genera una lista di prelievo con codice articolo, quantità richiesta e posizione. L'operatore raccoglie i prodotti, controlla che cor

### Genera Card - `full_pipeline_cards_60_motors_graphic_v51416`

- Classi problema: problema qualità RAG, problema qualità linguistica
- Difetti tecnici: approved_non_true:False, status_non_approved:QUALITY_BLOCKED
- Warning: radici_ripetute:analizzat,aspetto,azione,collega,concreto,contenuto,evidenzia,operativa, radici_ripetute:analizzat,azione,collega,concreto,contenuto,degli,evidenzia,magazzino
- Problemi RAG: ripetizioni
- Problemi didattici: nessuno
- Sample: [{"card_id": "full_card_v51416_001", "titolo": "Gestione ordinata del magazzino", "messaggio_chiave": "Gestione ordini magazzino moderno: La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti.", "spiegazione": "La card evidenzia che la gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti Questo passaggio collega il contenuto del documento a un'azione operativa o a un controllo concreto.", "micro_concetti": ["gestione", "ordini", "magazzino", "moderno"], "visual": {"icon": "🏢", "theme": "business_presentable", "svg": "<svg viewBo

### Genera Test/Quiz - `full_pipeline_quiz_route63_language_quality_v51418`

- Classi problema: nessuna
- Difetti tecnici: nessuno
- Warning: nessuno
- Problemi RAG: nessuno
- Problemi didattici: nessuno
- Sample: [{"id": "quiz_quality_v51418_001", "domanda": "Nel passaggio su verificare gestione ordini magazzino, quale opzione conserva il dettaglio documentale essenziale?", "opzioni": [{"option_id": "A", "testo": "La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti"}, {"option_id": "B", "testo": "Spostare il controllo su una fase diversa, senza mantenere responsabilità e verifica del passaggio indicato."}, {"option_id": "C", "testo": "Registrare l'attività in modo parziale, lasciando fuori il dato che permette di controllare l'esito."}, {"option_id": "D", "testo": "Applicare una regola simile ma riferita a un'altra 

### Genera Domande studio - `full_pipeline_study_route51_language_quality_v51418`

- Classi problema: problema didattico, problema qualità RAG, problema qualità linguistica
- Difetti tecnici: approved_non_true:False, status_non_approved:QUALITY_BLOCKED
- Warning: copertura_termini_documento_bassa:0/6, copertura_termini_documento_bassa:1/6
- Problemi RAG: domande innaturali, genericità, perdita contesto
- Problemi didattici: domande_formulaiche:4
- Sample: [{"id": "study_quality_v51418_001", "domanda": "Qual è il punto operativo principale relativo a gestione ordini magazzino?", "risposta_guida": "Il documento indica che la gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti. Lo studente deve collegare questo punto a una procedura concreta, a una responsabilità chiara e a una verifica controllabile.", "tipo_domanda": "comprensione_operativa", "livello_cognitivo": "applicazione", "fatto_origine": "La gestione degli ordini in un magazzino moderno richiede una procedura chiara per ricevere, controllare, registrare e spedire i prodotti", "quality_rewrite": "v51418_l

## Priorità di intervento

| Priorità | Pulsante | Generatore | Motore | Score | Motivo |
| ---: | --- | --- | --- | ---: | --- |
| 1 | Genera Domande studio | `study_questions` | `full_pipeline_study_route51_language_quality_v51418` | 27 | approved_non_true:False; status_non_approved:QUALITY_BLOCKED; domande innaturali; genericità; perdita contesto; domande_formulaiche:4 |
| 2 | Genera Card | `cards` | `full_pipeline_cards_60_motors_graphic_v51416` | 15 | approved_non_true:False; status_non_approved:QUALITY_BLOCKED; ripetizioni |
| 3 | Genera Riassunto | `summary` | `full_pipeline_summary_route55_all_motors_v51416` | 4 | riassunto non abbastanza profondo |
| 4 | Genera Test/Quiz | `quiz` | `full_pipeline_quiz_route63_language_quality_v51418` | 0 | nessun problema bloccante |

## Primo motore da migliorare

- Motore/file: `full_pipeline_study_route51_language_quality_v51418`
- Generatore: `study_questions`
- File candidato: `motore linguistico/didattico v51418 da localizzare senza patch a bridge/UI/QM; candidato principale backend/phase5_full_pipeline_runtime_v51416.py`
- Raccomandazione: **patch mirata sui motori linguistici/didattici, nessuna patch a bridge/UI/QM**

## Distinzione problemi

- bug tecnico: nessuno
- problema qualità linguistica: cards:approved_non_true:False, cards:status_non_approved:QUALITY_BLOCKED, study_questions:approved_non_true:False, study_questions:status_non_approved:QUALITY_BLOCKED, summary:riassunto non abbastanza profondo, summary:riassunto_non_copre_abbastanza_sezioni
- problema qualità RAG: cards:radici_ripetute:analizzat,aspetto,azione,collega,concreto,contenuto,evidenzia,operativa, cards:radici_ripetute:analizzat,azione,collega,concreto,contenuto,degli,evidenzia,magazzino, cards:ripetizioni, study_questions:copertura_termini_documento_bassa:0/6, study_questions:copertura_termini_documento_bassa:1/6, study_questions:genericità, study_questions:perdita contesto
- problema didattico: study_questions:domande innaturali, study_questions:domande_formulaiche:4
- problema UI/bridge: nessuno
