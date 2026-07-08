# FASE 5.15G.2 - Multi-document real summary review

## 1. Obiettivo fase
Review diagnostica multi-documento del solo ramo `summary` long-doc G.2, senza modificare card, quiz, study_questions, bridge, raw_output comune o Quality Manager comune.

## 2. Checkpoint di partenza
- branch: `rag-concept-app-presentabile-v3`
- commit: `291c6c9 Aggiunge smoothing summary long-doc Fase 5.15G.2`
- tag: `checkpoint-mini-llm-long-summary-smoothing-v515g2`
- initial_state: `working tree clean, branch up to date with origin`

## 3. Documenti analizzati
- `reports/audit_effetti_premi_ai_its.md` - Documento lungo reale di audit effetti/premi presente nei report.
- `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md` - Documento medio formativo cyber-security in rag/documenti.
- `rag/documenti/documento_ai_generativa_test_rag.md` - Documento di dominio diverso: AI generativa e RAG.
- `rag/documenti/esempio_documento_aziendale_formazione.md` - Documento breve aziendale/formazione: controllo non-long.
- `rag/documenti/test_documento_lungo_aziendale_120_pagine.txt` - Stress test lungo gia usato: sintetico, non unico documento della review.

## 4. Tabella risultati per documento
| Documento | Long-doc | Profilo | Input parole | Summary parole | Ratio | Target 10% | G.2 runtime | QM | Rumore | Template | Ripetizioni | Titoli tecnici | Esito |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| `long_real_audit_report` | True | manuale_aziendale | 106264 | 12803 | 0.12 | True | True | 55 | 0 | 0 | 16 | 0 | WARNING |
| `medium_security_training_doc` | False | manuale_aziendale | 1673 | 223 | 0.133 | None | None | 55 | 0 | 0 | 0 | 0 | PASS |
| `different_domain_ai_rag_doc` | False | cv_profilo_professionale | 617 | 199 | 0.323 | None | None | 55 | 0 | 0 | 0 | 0 | PASS |
| `short_business_training_doc` | False | cv_profilo_professionale | 137 | 173 | 1.263 | None | None | 55 | 0 | 0 | 0 | 0 | PASS |
| `synthetic_long_stress_reference` | True | manuale_aziendale | 93418 | 9399 | 0.101 | True | True | 55 | 0 | 0 | 2 | 0 | PASS |

## 5. Confronto sintetico con G.2 precedente
La fase precedente aveva validato G.2 soprattutto sullo stress test lungo aziendale sintetico. Questa review estende il controllo a documenti reali/operativi presenti nel repository, includendo almeno un long-doc, documenti medi/non-long e un dominio diverso.

## 6. Difetti trovati
- `long_real_audit_report`: repeated_patterns_high

## 7. Eventuali correzioni fatte
- Nessuna correzione runtime applicata da questa diagnostica. Sono stati creati solo script/report diagnostici.

## 8. Verifiche finali
- Script diagnostico multi-documento eseguito.
- Le diagnostiche py_compile, G.2 universale e G.1 regressiva vanno eseguite dopo questo script come da prompt.

## 9. Esito finale
**WARNING**
- warning_documents: long_real_audit_report

## 10. Prossimo step consigliato
Passare alla review qualita card solo se la WARNING, se presente, e' considerata non bloccante.

## Dettagli per documento
### long_real_audit_report
- Path: `reports/audit_effetti_premi_ai_its.md`
- Sezioni: 11 -> Sintesi tematica, Executive summary, Mappa dei processi, Controlli, Responsabilita, Rischi e audit, Collegamenti operativi, Sintesi conclusiva, Responsabilita - approfondimento 1, Responsabilita - approfondimento 2
- Sample titoli: Sintesi tematica, Executive summary, Mappa dei processi, Controlli, Responsabilita
- Prime frasi: ["Il testo viene letto come manuale aziendale e richiede uno stile di", "Il baricentro riguarda corretta risposta finale badge risultato frase e distrattori con", "La sintesi mette in relazione le parti invece di accumulare voci isolate", "I temi iniziali aprono il quadro su Corretta e Keyword giudizio giudizi", "La progressione segue l ordine del documento prima introduce il lessico e"]
- Difetti: repeated_patterns_high

### medium_security_training_doc
- Path: `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- Sezioni: 0 -> 
- Sample titoli: 
- Prime frasi: ["Il documento spiega che Documento RAG di test Sicurezza informatica aziendale", "In apertura chiarisce anche che la sicurezza informatica ha tre obiettivi principali", "Questi elementi introducono il flusso operativo su cui si sviluppano ricezione controllo", "La parte centrale approfondisce gli aspetti più operativi Le password non devono", "Gli SMS possono essere esposti a rischi come cambio SIM fraudolento o"]
- Difetti: nessuno

### different_domain_ai_rag_doc
- Path: `rag/documenti/documento_ai_generativa_test_rag.md`
- Sezioni: 0 -> 
- Sample titoli: 
- Prime frasi: ["Il documento spiega che Documento di prova RAG Intelligenza Artificiale Generativa", "In apertura chiarisce anche che nelle aziende può essere usata per organizzare", "Questi elementi introducono il flusso operativo su cui si sviluppano ricezione controllo", "La parte centrale approfondisce gli aspetti più operativi Per questo motivo un", "Il vantaggio del RAG è che l output può restare più vicino"]
- Difetti: nessuno

### short_business_training_doc
- Path: `rag/documenti/esempio_documento_aziendale_formazione.md`
- Sezioni: 0 -> 
- Sample titoli: 
- Prime frasi: ["Il documento spiega che Esempio documento aziendale per formazione", "In apertura chiarisce anche che ogni dipendente deve proteggere le credenziali personali", "Questi elementi introducono il flusso operativo su cui si sviluppano ricezione controllo", "La parte centrale approfondisce gli aspetti più operativi Gli allegati provenienti da", "I dati aziendali devono essere trattati solo per finalità autorizzate e conservati"]
- Difetti: nessuno

### synthetic_long_stress_reference
- Path: `rag/documenti/test_documento_lungo_aziendale_120_pagine.txt`
- Sezioni: 11 -> Sintesi tematica, Executive summary, Mappa dei processi, Controlli, Responsabilita, Rischi e audit, Collegamenti operativi, Sintesi conclusiva, Responsabilita - approfondimento 1, Responsabilita - approfondimento 2
- Sample titoli: Sintesi tematica, Executive summary, Mappa dei processi, Controlli, Responsabilita
- Prime frasi: ["Il testo viene letto come manuale aziendale e richiede uno stile di", "Il baricentro riguarda controllo onboarding evidenze operativo sicurezza riferimento e responsabile con", "La sintesi mette in relazione le parti invece di accumulare voci isolate", "I temi iniziali aprono il quadro su Controllo Gestione incidenti Controllo e", "La progressione segue l ordine del documento prima introduce il lessico e"]
- Difetti: nessuno

