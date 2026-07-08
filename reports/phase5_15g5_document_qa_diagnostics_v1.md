# FASE 5.15G.5 - Document QA diagnostics

Status: **PASS**
Documents tested: `5`
Questions tested: `20`
Answered / not found: `15` / `5`
Fallback/demo/template/unsupported: `0` / `0` / `0`
Quiz-like / study-question-like outputs: `0` / `0`

## Scope confirmations

- Interroga Documento is a new isolated engine.
- Study Questions were not deleted or replaced.
- No UI route/button was linked in this diagnostic phase.
- Summary, Cards and Test/Quiz generators are not invoked by this script.

## audit_effetti_premi_ai_its - PASS

- File: `reports/audit_effetti_premi_ai_its.md`
- Type: `real_long_audit`; words: `106264`; long_doc: `True`
- Questions: `4`; answered: `3`; not_found: `1`
- Noise metrics: fallback `0`, template `0`, unsupported `0`, quizlike `0`, study_question_like `0`
- Defects: `[]`
- Warnings: `[]`

### present_answer - PASS

- Question: Qual è il tema principale del documento?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Secondo il documento: Obiettivo: trovare dove sono già presenti effetti, premi finali, frasi motivazionali, giudizi variabili e coriandoli. Keyword: confetti, coriandoli, premio, premi, reward, giudizio, giudizi, motivaz, frase, finale, risultato, voto, badge, corretta, risposta corretta, success.
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0001` score `1.1`: Obiettivo: trovare dove sono già presenti effetti, premi finali, frasi motivazionali, giudizi variabili e coriandoli.
  - Evidence `chunk_0002` score `1.07`: L28: `<img src="https://img.shields.io/badge/SCARICA%20WEB%20AI%20ITS-HTML%20DATABASE%20JS-00bcd4?style=for-the-badge&labelColor=00bcd4" alt="Scarica Web AI ITS">`. L32: `<a href="https://github.com/aleb2016-maker/alex-ai-quiz-database/raw/main/downloads/pacchetto-android-ai-i...

### responsibilities_procedures_risks - PASS

- Question: Quali responsabilità, procedure o rischi vengono citati?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Nel documento le responsabilità risultano collegate a questi passaggi: L17: `"Separare recupero, generazione e controllo finale rende la pipeline più osservabile e permette di capire meglio dove nasce un errore. L18: `"Non basta correggere alla fine, perché un errore nel recupero può influenzare la generazione; inoltre le fasi non sono indipendenti e il c...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0318` score `0.4919`: L14: `"Per distinguere retrieval, generazione e controllo, ma usando il controllo finale principalmente per salvare la risposta prodotta"`. L17: `"Separare recupero, generazione e controllo finale rende la pipeline più osservabile e permette di capire meglio dove nasce un erro...
  - Evidence `chunk_0358` score `0.4526`: L19: `"Il passaggio successivo è 13 + 3 = 16. L33: `"Nelle posizioni dispari compaiono 2, 4, 6, quindi il valore successivo in quella sotto-sequenza è 8. L49: `"Il passo successivo è 40 × 2 = 80. L65: `"20 × 2 + 1 = 41, quindi il passaggio successivo è 41 - 1 = 40. L80: `"16 s...

### simple_explanation - PASS

- Question: Spiegami questo documento in modo semplice.
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: In modo semplice, dal documento emerge questo: Obiettivo: trovare dove sono già presenti effetti, premi finali, frasi motivazionali, giudizi variabili e coriandoli. Keyword: confetti, coriandoli, premio, premi, reward, giudizio, giudizi, motivaz, frase, finale, risultato, voto, badge, corretta, risposta corretta, success.
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0001` score `1.1`: Obiettivo: trovare dove sono già presenti effetti, premi finali, frasi motivazionali, giudizi variabili e coriandoli.
  - Evidence `chunk_0002` score `1.07`: L28: `<img src="https://img.shields.io/badge/SCARICA%20WEB%20AI%20ITS-HTML%20DATABASE%20JS-00bcd4?style=for-the-badge&labelColor=00bcd4" alt="Scarica Web AI ITS">`. L32: `<a href="https://github.com/aleb2016-maker/alex-ai-quiz-database/raw/main/downloads/pacchetto-android-ai-i...

### out_of_document_petrolio - PASS

- Question: Qual è il prezzo del petrolio indicato nel documento?
- Expected/status/confidence: `NOT_FOUND_IN_DOCUMENT` / `NOT_FOUND_IN_DOCUMENT` / `low`
- Answer: Nel documento non ho trovato informazioni sufficienti per rispondere a questa domanda.
- Evidence chunks: `0`
- Defects: `[]`

## synthetic_long_business_doc - PASS

- File: `rag/documenti/test_documento_lungo_aziendale_120_pagine.txt`
- Type: `synthetic_long_stress`; words: `93418`; long_doc: `True`
- Questions: `4`; answered: `3`; not_found: `1`
- Noise metrics: fallback `0`, template `0`, unsupported `0`, quizlike `0`, study_question_like `0`
- Defects: `[]`
- Warnings: `[]`

### present_answer - PASS

- Question: Qual è il tema principale del documento?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Secondo il documento: Nel contesto IT Operations, la sezione 001.1 descrive come gestire sicurezza informatica quando un sistema critico mostra tempi di risposta anomali. Il riferimento principale e firewall, collegato a segmentazione rete e monitoraggio accessi. La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0002` score `1.1`: Nel contesto IT Operations, la sezione 001.1 descrive come gestire sicurezza informatica quando un sistema critico mostra tempi di risposta anomali. Il riferimento principale e firewall, collegato a segmentazione rete e monitoraggio accessi. La procedura richiede una verifica...
  - Evidence `chunk_0003` score `1.07`: Nel contesto Sicurezza, la sezione 001.2 descrive come gestire sicurezza informatica quando un audit interno richiede evidenze entro la giornata. Il riferimento principale e firewall, collegato a segmentazione rete e monitoraggio accessi. La procedura richiede una verifica men...

### responsibilities_procedures_risks - PASS

- Question: Quali responsabilità, procedure o rischi vengono citati?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Nel documento le responsabilità risultano collegate a questi passaggi: La procedura richiede una verifica trimestrale, una traccia scritta nel registro operativo e una conferma del responsabile di processo. La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo. Ogni attività...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0079` score `1.0036`: Nel contesto Legal e Compliance, la sezione 010.2 descrive come gestire documentazione tecnica quando una email sospetta viene inoltrata al team sicurezza. Il riferimento principale e documentazione tecnica, collegato a runbook e versionamento procedure. La procedura richiede...
  - Evidence `chunk_0081` score `1.0036`: Nel contesto Amministrazione, la sezione 010.4 descrive come gestire documentazione tecnica quando un reparto aggiorna una procedura usata da molte persone. Il riferimento principale e documentazione tecnica, collegato a runbook e versionamento procedure. La procedura richiede...

### simple_explanation - PASS

- Question: Spiegami questo documento in modo semplice.
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: In modo semplice, dal documento emerge questo: Nel contesto IT Operations, la sezione 001.1 descrive come gestire sicurezza informatica quando un sistema critico mostra tempi di risposta anomali. Il riferimento principale e firewall, collegato a segmentazione rete e monitoraggio accessi. La procedura richiede una verifica settimanale, una traccia scritta...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0002` score `1.1`: Nel contesto IT Operations, la sezione 001.1 descrive come gestire sicurezza informatica quando un sistema critico mostra tempi di risposta anomali. Il riferimento principale e firewall, collegato a segmentazione rete e monitoraggio accessi. La procedura richiede una verifica...
  - Evidence `chunk_0003` score `1.07`: Nel contesto Sicurezza, la sezione 001.2 descrive come gestire sicurezza informatica quando un audit interno richiede evidenze entro la giornata. Il riferimento principale e firewall, collegato a segmentazione rete e monitoraggio accessi. La procedura richiede una verifica men...

### out_of_document_petrolio - PASS

- Question: Qual è il prezzo del petrolio indicato nel documento?
- Expected/status/confidence: `NOT_FOUND_IN_DOCUMENT` / `NOT_FOUND_IN_DOCUMENT` / `low`
- Answer: Nel documento non ho trovato informazioni sufficienti per rispondere a questa domanda.
- Evidence chunks: `0`
- Defects: `[]`

## security_training_doc - PASS

- File: `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- Type: `medium_security`; words: `1673`; long_doc: `False`
- Questions: `4`; answered: `3`; not_found: `1`
- Noise metrics: fallback `0`, template `0`, unsupported `0`, quizlike `0`, study_question_like `0`
- Defects: `[]`
- Warnings: `[]`

### present_answer - PASS

- Question: Qual è il tema principale del documento?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Secondo il documento: L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali. Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e trasformarli in domande controllate. La sicurezza informa...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0002` score `1.1`: L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali. Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e...
  - Evidence `chunk_0003` score `1.07`: La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali. Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online c...

### responsibilities_procedures_risks - PASS

- Question: Quali responsabilità, procedure o rischi vengono citati?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Nel documento le responsabilità risultano collegate a questi passaggi: Non lasciare documenti riservati sulla scrivania riduce il rischio di accesso non autorizzato. In azienda, gli aggiornamenti dovrebbero essere gestiti con una procedura controllata. Prima si valuta la compatibilità, poi si distribuisce la correzione, poi si verifica che il sistema funz...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0030` score `0.5212`: In azienda, gli aggiornamenti dovrebbero essere gestiti con una procedura controllata. Prima si valuta la compatibilità, poi si distribuisce la correzione, poi si verifica che il sistema funzioni correttamente.
  - Evidence `chunk_0012` score `0.3982`: La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata. Anche se un attaccante scopre la password, deve superare anche il secondo controllo.

### simple_explanation - PASS

- Question: Spiegami questo documento in modo semplice.
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: In modo semplice, dal documento emerge questo: L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali. Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e trasformarli in domande controll...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0002` score `1.1`: L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali. Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e...
  - Evidence `chunk_0003` score `1.07`: La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali. Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online c...

### out_of_document_petrolio - PASS

- Question: Qual è il prezzo del petrolio indicato nel documento?
- Expected/status/confidence: `NOT_FOUND_IN_DOCUMENT` / `NOT_FOUND_IN_DOCUMENT` / `low`
- Answer: Nel documento non ho trovato informazioni sufficienti per rispondere a questa domanda.
- Evidence chunks: `0`
- Defects: `[]`

## ai_generative_rag_doc - PASS

- File: `rag/documenti/documento_ai_generativa_test_rag.md`
- Type: `ai_rag_domain`; words: `617`; long_doc: `False`
- Questions: `4`; answered: `3`; not_found: `1`
- Noise metrics: fallback `0`, template `0`, unsupported `0`, quizlike `0`, study_question_like `0`
- Defects: `[]`
- Warnings: `[]`

### present_answer - PASS

- Question: Qual è il tema principale del documento?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Secondo il documento: Nelle aziende può essere usata per organizzare documenti, velocizzare attività ripetitive, aiutare nella formazione e supportare la scrittura di procedure. Tuttavia non deve essere considerata infallibile, perché può produrre errori, semplificazioni e risposte non presenti nelle fonti. I modelli linguistici sono sistemi addestrati su...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0002` score `1.1`: Nelle aziende può essere usata per organizzare documenti, velocizzare attività ripetitive, aiutare nella formazione e supportare la scrittura di procedure. Tuttavia non deve essere considerata infallibile, perché può produrre errori, semplificazioni e risposte non presenti nel...
  - Evidence `chunk_0003` score `1.07`: I modelli linguistici sono sistemi addestrati su grandi quantità di testo. Quando ricevono una domanda, generano una risposta probabile in base al contesto disponibile. Possono scrivere in modo naturale, ma non verificano automaticamente ogni affermazione.

### responsibilities_procedures_risks - PASS

- Question: Quali responsabilità, procedure o rischi vengono citati?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Nel documento le responsabilità risultano collegate a questi passaggi: Il quarto rischio è la dipendenza eccessiva. Il primo rischio è l'invenzione di informazioni. Il secondo rischio è l'uso di fonti non pertinenti. Il terzo rischio riguarda la privacy.
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0013` score `0.315`: Il quarto rischio è la dipendenza eccessiva. L'AI deve essere uno strumento di supporto, non un'autorità assoluta.
  - Evidence `chunk_0010` score `0.2873`: Il primo rischio è l'invenzione di informazioni. Se il modello non trova dati sufficienti, può completare i vuoti con supposizioni.

### simple_explanation - PASS

- Question: Spiegami questo documento in modo semplice.
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: In modo semplice, dal documento emerge questo: Nelle aziende può essere usata per organizzare documenti, velocizzare attività ripetitive, aiutare nella formazione e supportare la scrittura di procedure. Tuttavia non deve essere considerata infallibile, perché può produrre errori, semplificazioni e risposte non presenti nelle fonti. I modelli linguistici s...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0002` score `1.1`: Nelle aziende può essere usata per organizzare documenti, velocizzare attività ripetitive, aiutare nella formazione e supportare la scrittura di procedure. Tuttavia non deve essere considerata infallibile, perché può produrre errori, semplificazioni e risposte non presenti nel...
  - Evidence `chunk_0003` score `1.07`: I modelli linguistici sono sistemi addestrati su grandi quantità di testo. Quando ricevono una domanda, generano una risposta probabile in base al contesto disponibile. Possono scrivere in modo naturale, ma non verificano automaticamente ogni affermazione.

### out_of_document_petrolio - PASS

- Question: Qual è il prezzo del petrolio indicato nel documento?
- Expected/status/confidence: `NOT_FOUND_IN_DOCUMENT` / `NOT_FOUND_IN_DOCUMENT` / `low`
- Answer: Nel documento non ho trovato informazioni sufficienti per rispondere a questa domanda.
- Evidence chunks: `0`
- Defects: `[]`

## business_training_short_doc - PASS

- File: `rag/documenti/esempio_documento_aziendale_formazione.md`
- Type: `short_business`; words: `137`; long_doc: `False`
- Questions: `4`; answered: `3`; not_found: `1`
- Noise metrics: fallback `0`, template `0`, unsupported `0`, quizlike `0`, study_question_like `0`
- Defects: `[]`
- Warnings: `[]`

### present_answer - PASS

- Question: Qual è il tema principale del documento?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: Secondo il documento: Ogni dipendente deve proteggere le credenziali personali e non deve condividere password o codici di accesso. Prima di cliccare su un link ricevuto via email, è necessario verificare mittente, dominio e contenuto del messaggio. Gli allegati provenienti da fonti non verificate possono contenere malware o tentativi di phishing. I dati...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0001` score `1.1`: Ogni dipendente deve proteggere le credenziali personali e non deve condividere password o codici di accesso.
  - Evidence `chunk_0002` score `1.07`: Prima di cliccare su un link ricevuto via email, è necessario verificare mittente, dominio e contenuto del messaggio.

### responsibilities_procedures_risks - PASS

- Question: Quali responsabilità, procedure o rischi vengono citati?
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `low`
- Answer: Nel documento le responsabilità risultano collegate a questi passaggi: In caso di dubbio, il dipendente deve chiedere conferma al responsabile o al reparto IT prima di procedere.
- Evidence chunks: `1`
- Defects: `[]`

  - Evidence `chunk_0006` score `0.3049`: In caso di dubbio, il dipendente deve chiedere conferma al responsabile o al reparto IT prima di procedere.

### simple_explanation - PASS

- Question: Spiegami questo documento in modo semplice.
- Expected/status/confidence: `ANSWERED` / `ANSWERED` / `high`
- Answer: In modo semplice, dal documento emerge questo: Ogni dipendente deve proteggere le credenziali personali e non deve condividere password o codici di accesso. Prima di cliccare su un link ricevuto via email, è necessario verificare mittente, dominio e contenuto del messaggio. Gli allegati provenienti da fonti non verificate possono contenere malware o tenta...
- Evidence chunks: `8`
- Defects: `[]`

  - Evidence `chunk_0001` score `1.1`: Ogni dipendente deve proteggere le credenziali personali e non deve condividere password o codici di accesso.
  - Evidence `chunk_0002` score `1.07`: Prima di cliccare su un link ricevuto via email, è necessario verificare mittente, dominio e contenuto del messaggio.

### out_of_document_petrolio - PASS

- Question: Qual è il prezzo del petrolio indicato nel documento?
- Expected/status/confidence: `NOT_FOUND_IN_DOCUMENT` / `NOT_FOUND_IN_DOCUMENT` / `low`
- Answer: Nel documento non ho trovato informazioni sufficienti per rispondere a questa domanda.
- Evidence chunks: `0`
- Defects: `[]`
