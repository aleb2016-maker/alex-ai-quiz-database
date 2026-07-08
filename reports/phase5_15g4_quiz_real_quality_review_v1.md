# FASE 5.15G.4 - Real quality review quiz/test

Status: **PASS**

## Sintesi

- Documenti testati: `5`
- Quiz 63/63 su documenti APPROVED: `True`
- Runtime/generatori modificati: `False`
- Target 10% applicato: `False`

## real_long_audit_doc - PASS

- Filepath: `reports/audit_effetti_premi_ai_its.md`
- Type: `real_long`; input_words: `106264`; long_doc: `True`; quiz_active: `True`
- Domande: `8`; 4 opzioni: `8`; 1 corretta inferita: `8`; 3 distrattori: `8`
- QM quiz: `63/63`; approved: `True`; status: `APPROVED`
- Distrattori forti/deboli: `24` / `0`
- Spiegazioni presenti/corte/generiche: `8` / `0` / `0`
- Duplicati domande/opzioni: `0` / `0`; quasi duplicati: `0` / `0`
- Noise/template/grammar/broken: `0` / `0` / `0` / `0`
- Score source/coverage/didactic/linguistic/overall: `0.966` / `1.0` / `0.992` / `1.0` / `0.993`
- Severity: `NON_BLOCKING`; utilità stimata: `utile`
- Difetti: `[]`
- Warning: `[]`

### Esempi

#### Domanda 1 - WARNING

Domanda: Come verificare motivazione ripeti test nella macro-area 1?

Opzioni:
- 1. motivazione ripeti test: Nella pagina GitHub che si apre, premi **Run workflow** in alto a destra. (corretta inferita)
- 2. Eseguire il controllo solo a campione anche quando Apertura del documento richiede verifica puntuale.
- 3. Registrare l'esito senza collegarlo al codice o alla responsabilità indicata.
- 4. Sostituire il controllo con una nota generica non verificabile nel tempo.

Risposta corretta: motivazione ripeti test: Nella pagina GitHub che si apre, premi **Run workflow** in alto a destra.
Spiegazione: La scelta più adatta mantiene motivazione ripeti pagina github collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio documentale.
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 2 - WARNING

Domanda: Come verificare validare competenze pratiche degli operatori nella macro-area 2?

Opzioni:
- 1. Eseguire il controllo solo a campione anche quando Keyword: giudizio, giudizi, finale, risultato, risultati, stelle, corretta,, success richiede verifica puntuale.
- 2. Validare competenze pratiche degli operatori: L’energia cinetica si conserva solo in urti elastici. (corretta inferita)
- 3. Registrare l'esito senza collegarlo al codice o alla responsabilità indicata.
- 4. Sostituire il controllo con una nota generica non verificabile nel tempo.

Risposta corretta: Validare competenze pratiche degli operatori: L’energia cinetica si conserva solo in urti elastici.
Spiegazione: Il punto da riconoscere è validare competenze pratiche operatori: la soluzione selezionata conserva il legame con il contenuto fonte. Un distrattore modifica fase, responsabilità o tracciabilità e per questo perde coerenza con il documento.
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 3 - WARNING

Domanda: Come verificare contenere controllare molte nella macro-area 3?

Opzioni:
- 1. Eseguire il controllo solo a campione anche quando Keyword: corretta, richiede verifica puntuale.
- 2. Registrare l'esito senza collegarlo al codice o alla responsabilità indicata.
- 3. contenere controllare molte: frase: Hai risposto a tutto correttamente: controllo, memoria e ragionamento hanno lavorato insieme. (corretta inferita)
- 4. Sostituire il controllo con una nota generica non verificabile nel tempo.

Risposta corretta: contenere controllare molte: frase: Hai risposto a tutto correttamente: controllo, memoria e ragionamento hanno lavorato insieme.
Spiegazione: Per rispondere bisogna tenere insieme concetto, prova e conseguenza operativa. L'opzione più adatta riprende contenere controllare molte frase, mentre una scelta generica non chiarisce chi verifica il passaggio e con quale evidenza. In p...
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 4 - WARNING

Domanda: Come verificare frase finale risultato nella macro-area 4?

Opzioni:
- 1. Trattare il rischio di Keyword: frase, finale, risultato, risultati, corretta, come evento marginale senza misura preventiva.
- 2. Rinviare la gestione del rischio finché compare una non conformità gia conclusa.
- 3. Confondere il rischio con una semplice comunicazione informale tra reparti.
- 4. frase finale risultato: Per saltare completamente il controllo del risultato finale. (corretta inferita)

Risposta corretta: frase finale risultato: Per saltare completamente il controllo del risultato finale.
Spiegazione: La domanda verifica frase finale risultato saltare come passaggio concreto, non come formula astratta. La scelta migliore resta ancorata al contenuto; un distrattore confonde contesto o controllo e riduce il valore didattico. In pratica,...
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 5 - WARNING

Domanda: Come verificare sommiamo spiegazione unità scriviamo riportiamo nella macro-area 5?

Opzioni:
- 1. Sommiamo spiegazione unità scriviamo riportiamo: spiegazione: Sommiamo prima le unità: 5 + 8 = 13, scriviamo 3 e riportiamo 1. (corretta inferita)
- 2. Applicare la procedura di Keyword: risultato, corretta senza registrare il passaggio verificabile.
- 3. Spostare Keyword: risultato, corretta a una fase non prevista, perdendo ordine e responsabilità.
- 4. Usare una procedura simile ma priva del controllo richiesto dalla macro-area.

Risposta corretta: Sommiamo spiegazione unità scriviamo riportiamo: spiegazione: Sommiamo prima le unità: 5 + 8 = 13, scriviamo 3 e riportiamo 1.
Spiegazione: La scelta più adatta mantiene sommiamo spiegazione unità scriviamo collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio documen...
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

## synthetic_long_business_doc - PASS

- Filepath: `rag/documenti/test_documento_lungo_aziendale_120_pagine.txt`
- Type: `synthetic_long_stress`; input_words: `93418`; long_doc: `True`; quiz_active: `True`
- Domande: `7`; 4 opzioni: `7`; 1 corretta inferita: `7`; 3 distrattori: `7`
- QM quiz: `63/63`; approved: `True`; status: `APPROVED`
- Distrattori forti/deboli: `21` / `0`
- Spiegazioni presenti/corte/generiche: `7` / `0` / `0`
- Duplicati domande/opzioni: `0` / `0`; quasi duplicati: `0` / `0`
- Noise/template/grammar/broken: `0` / `0` / `0` / `0`
- Score source/coverage/didactic/linguistic/overall: `0.9` / `1.0` / `0.975` / `1.0` / `0.977`
- Severity: `NON_BLOCKING`; utilità stimata: `utile`
- Difetti: `[]`
- Warning: `[]`

### Esempi

#### Domanda 1 - WARNING

Domanda: Come verificare riconciliare qualità dati e registrazioni nella macro-area 1?

Opzioni:
- 1. Riconciliare qualità dati e registrazioni: La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo. (corretta inferita)
- 2. Lasciare Apertura del documento senza owner, rendendo incerta la decisione finale.
- 3. Attribuire la responsabilità a un gruppo generico senza compito verificabile.
- 4. Separare la responsabilità dal controllo che deve dimostrarne l'esito.

Risposta corretta: Riconciliare qualità dati e registrazioni: La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo.
Spiegazione: La scelta più adatta mantiene riconciliare qualità registrazioni procedura collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio...
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 2 - WARNING

Domanda: Come verificare classificare incidenti ed escalation operativa nella macro-area 2?

Opzioni:
- 1. Trattare il rischio di Riferimento sezione: MAN-AZI-01.03 come evento marginale senza misura preventiva.
- 2. Classificare incidenti ed escalation operativa: La procedura richiede una verifica trimestrale, una traccia scritta nel registro operativo e una conferma del responsabile di processo. (corretta inferita)
- 3. Rinviare la gestione del rischio finché compare una non conformità gia conclusa.
- 4. Confondere il rischio con una semplice comunicazione informale tra reparti.

Risposta corretta: Classificare incidenti ed escalation operativa: La procedura richiede una verifica trimestrale, una traccia scritta nel registro operativo e una conferma del responsabile di processo.
Spiegazione: Il punto da riconoscere è classificare incidenti escalation operativa: la soluzione selezionata conserva il legame con il contenuto fonte. Un distrattore modifica fase, responsabilità o tracciabilità e per questo perde coerenza con il do...
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 3 - WARNING

Domanda: Come verificare registro richiede verifica settimanale traccia nella macro-area 3?

Opzioni:
- 1. Lasciare Riferimento sezione: MAN-AZI-01.05 senza owner, rendendo incerta la decisione finale.
- 2. Attribuire la responsabilità a un gruppo generico senza compito verificabile.
- 3. Registro richiede verifica settimanale traccia: La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo. (corretta inferita)
- 4. Separare la responsabilità dal controllo che deve dimostrarne l'esito.

Risposta corretta: Registro richiede verifica settimanale traccia: La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo.
Spiegazione: Per rispondere bisogna tenere insieme concetto, prova e conseguenza operativa. L'opzione più adatta riprende registro richiede settimanale traccia, mentre una scelta generica non chiarisce chi verifica il passaggio e con quale evidenza....
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 4 - WARNING

Domanda: Come verificare pianificare audit e azioni correttive nella macro-area 4?

Opzioni:
- 1. Lasciare Riferimento sezione: MAN-AZI-01.07 senza owner, rendendo incerta la decisione finale.
- 2. Attribuire la responsabilità a un gruppo generico senza compito verificabile.
- 3. Separare la responsabilità dal controllo che deve dimostrarne l'esito.
- 4. Pianificare audit e azioni correttive: La procedura richiede una verifica trimestrale, una traccia scritta nel registro operativo e una conferma del responsabile di processo. (corretta inferita)

Risposta corretta: Pianificare audit e azioni correttive: La procedura richiede una verifica trimestrale, una traccia scritta nel registro operativo e una conferma del responsabile di processo.
Spiegazione: La domanda verifica pianificare audit azioni correttive come passaggio concreto, non come formula astratta. La scelta migliore resta ancorata al contenuto; un distrattore confonde contesto o controllo e riduce il valore didattico. In pra...
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

#### Domanda 5 - WARNING

Domanda: Come verificare verificare continuità operativa e ripristino nella macro-area 5?

Opzioni:
- 1. Verificare continuità operativa e ripristino: La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo. (corretta inferita)
- 2. Lasciare Riferimento sezione: MAN-AZI-01.09 senza owner, rendendo incerta la decisione finale.
- 3. Attribuire la responsabilità a un gruppo generico senza compito verificabile.
- 4. Separare la responsabilità dal controllo che deve dimostrarne l'esito.

Risposta corretta: Verificare continuità operativa e ripristino: La procedura richiede una verifica settimanale, una traccia scritta nel registro operativo e una conferma del responsabile di processo.
Spiegazione: La scelta più adatta mantiene continuità operativa ripristino procedura collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio do...
Giudizio qualità: `WARNING`
Difetti item: `[]`
Warning item: `['domanda_generica_o_template']`

## security_training_doc - PASS

- Filepath: `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- Type: `medium_security`; input_words: `1673`; long_doc: `False`; quiz_active: `True`
- Domande: `4`; 4 opzioni: `4`; 1 corretta inferita: `4`; 3 distrattori: `4`
- QM quiz: `63/63`; approved: `True`; status: `APPROVED`
- Distrattori forti/deboli: `12` / `0`
- Spiegazioni presenti/corte/generiche: `4` / `0` / `0`
- Duplicati domande/opzioni: `0` / `0`; quasi duplicati: `0` / `0`
- Noise/template/grammar/broken: `0` / `0` / `0` / `0`
- Score source/coverage/didactic/linguistic/overall: `0.925` / `1.0` / `0.981` / `1.0` / `0.983`
- Severity: `NON_BLOCKING`; utilità stimata: `utile`
- Difetti: `[]`
- Warning: `[]`

### Esempi

#### Domanda 1 - PASS

Domanda: Quale scelta mantiene verificabile sicurezza informatica aziendale scopo secondo il documento?

Opzioni:
- 1. Sicurezza informatica aziendale Scopo del documento Questo documento è stato creato come fonte documentale per il percorso di studio. (corretta inferita)
- 2. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 3. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: Sicurezza informatica aziendale Scopo del documento Questo documento è stato creato come fonte documentale per il percorso di studio.
Spiegazione: La scelta più adatta mantiene sicurezza informatica aziendale scopo collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio docume...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 2 - PASS

Domanda: Quale scelta mantiene verificabile essere inserito cartella documenti secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 3. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.
- 4. Può essere inserito nella cartella rag/documenti/ per costruire esercizi e percorsi di studio sulla sicurezza informatica aziendale. (corretta inferita)

Risposta corretta: Può essere inserito nella cartella rag/documenti/ per costruire esercizi e percorsi di studio sulla sicurezza informatica aziendale.
Spiegazione: Il punto da riconoscere è essere inserito cartella documenti: la soluzione selezionata conserva il legame con il contenuto fonte. Un distrattore modifica fase, responsabilità o tracciabilità e per questo perde coerenza con il documento.
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 3 - PASS

Domanda: Quale scelta mantiene verificabile obiettivo spiegare semplice concetti secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 3. L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali. (corretta inferita)
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali.
Spiegazione: Per rispondere bisogna tenere insieme concetto, prova e conseguenza operativa. L'opzione più adatta riprende obiettivo spiegare semplice concetti, mentre una scelta generica non chiarisce chi verifica il passaggio e con quale evidenza. I...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 4 - PASS

Domanda: Quale scelta mantiene verificabile pensato manuale tecnico avanzato secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e trasformarli in domande controllate. (corretta inferita)
- 3. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e trasformarli in domande controllate.
Spiegazione: La domanda verifica pensato manuale tecnico avanzato come passaggio concreto, non come formula astratta. La scelta migliore resta ancorata al contenuto; un distrattore confonde contesto o controllo e riduce il valore didattico. In pratic...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

## ai_generative_rag_doc - PASS

- Filepath: `rag/documenti/documento_ai_generativa_test_rag.md`
- Type: `different_domain_ai`; input_words: `617`; long_doc: `False`; quiz_active: `True`
- Domande: `4`; 4 opzioni: `4`; 1 corretta inferita: `4`; 3 distrattori: `4`
- QM quiz: `63/63`; approved: `True`; status: `APPROVED`
- Distrattori forti/deboli: `12` / `0`
- Spiegazioni presenti/corte/generiche: `4` / `0` / `0`
- Duplicati domande/opzioni: `0` / `0`; quasi duplicati: `0` / `0`
- Noise/template/grammar/broken: `0` / `0` / `0` / `0`
- Score source/coverage/didactic/linguistic/overall: `0.925` / `1.0` / `0.981` / `1.0` / `0.983`
- Severity: `NON_BLOCKING`; utilità stimata: `utile`
- Difetti: `[]`
- Warning: `[]`

### Esempi

#### Domanda 1 - PASS

Domanda: Quale scelta mantiene verificabile prova intelligenza artificiale generativa secondo il documento?

Opzioni:
- 1. Documento di prova RAG - Intelligenza Artificiale Generativa Introduzione L'intelligenza artificiale generativa è una tecnologia che permette a un sistema informatico di produrre contenuti nuovi partendo da dati, istruzioni e contesto. (corretta inferita)
- 2. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 3. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: Documento di prova RAG - Intelligenza Artificiale Generativa Introduzione L'intelligenza artificiale generativa è una tecnologia che permette a un sistema informatico di produrre contenuti nuovi partendo da dati, istruzioni e contesto.
Spiegazione: La scelta più adatta mantiene prova intelligenza artificiale generativa collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio do...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 2 - PASS

Domanda: Quale scelta mantiene verificabile tuttavia essere considerata infallibile secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 3. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.
- 4. Tuttavia non deve essere considerata infallibile, perché può produrre errori, semplificazioni e risposte non presenti nelle fonti. (corretta inferita)

Risposta corretta: Tuttavia non deve essere considerata infallibile, perché può produrre errori, semplificazioni e risposte non presenti nelle fonti.
Spiegazione: Il punto da riconoscere è tuttavia essere considerata infallibile: la soluzione selezionata conserva il legame con il contenuto fonte. Un distrattore modifica fase, responsabilità o tracciabilità e per questo perde coerenza con il docume...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 3 - PASS

Domanda: Quale scelta mantiene verificabile generare testi riassunti domande secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 3. Può generare testi, riassunti, domande, risposte, codice, tabelle, spiegazioni e materiali di studio. (corretta inferita)
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: Può generare testi, riassunti, domande, risposte, codice, tabelle, spiegazioni e materiali di studio.
Spiegazione: Per rispondere bisogna tenere insieme concetto, prova e conseguenza operativa. L'opzione più adatta riprende generare testi riassunti domande, mentre una scelta generica non chiarisce chi verifica il passaggio e con quale evidenza. In pr...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 4 - PASS

Domanda: Quale scelta mantiene verificabile aziende essere usata nelle secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Nelle aziende può essere usata per organizzare documenti, velocizzare attività ripetitive, aiutare nella formazione e supportare la scrittura di procedure. (corretta inferita)
- 3. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: Nelle aziende può essere usata per organizzare documenti, velocizzare attività ripetitive, aiutare nella formazione e supportare la scrittura di procedure.
Spiegazione: La domanda verifica nelle aziende essere usata come passaggio concreto, non come formula astratta. La scelta migliore resta ancorata al contenuto; un distrattore confonde contesto o controllo e riduce il valore didattico. In pratica, Nel...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

## business_training_short_doc - PASS

- Filepath: `rag/documenti/esempio_documento_aziendale_formazione.md`
- Type: `short_business`; input_words: `137`; long_doc: `False`; quiz_active: `True`
- Domande: `4`; 4 opzioni: `4`; 1 corretta inferita: `4`; 3 distrattori: `4`
- QM quiz: `63/63`; approved: `True`; status: `APPROVED`
- Distrattori forti/deboli: `12` / `0`
- Spiegazioni presenti/corte/generiche: `4` / `0` / `0`
- Duplicati domande/opzioni: `0` / `0`; quasi duplicati: `0` / `0`
- Noise/template/grammar/broken: `0` / `0` / `0` / `0`
- Score source/coverage/didactic/linguistic/overall: `0.925` / `1.0` / `0.981` / `1.0` / `0.983`
- Severity: `NON_BLOCKING`; utilità stimata: `utile`
- Difetti: `[]`
- Warning: `[]`

### Esempi

#### Domanda 1 - PASS

Domanda: Quale scelta mantiene verificabile esempio aziendale formazione dipendente secondo il documento?

Opzioni:
- 1. Esempio documento aziendale per formazione Ogni dipendente deve proteggere le credenziali personali e non deve condividere password o codici di accesso. (corretta inferita)
- 2. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 3. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: Esempio documento aziendale per formazione Ogni dipendente deve proteggere le credenziali personali e non deve condividere password o codici di accesso.
Spiegazione: La scelta più adatta mantiene esempio aziendale formazione dipendente collegato a evidenza, responsabilità e verifica. L'alternativa più debole sposta il controllo o lo rende generico, quindi non permette di ricostruire il passaggio docu...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 2 - PASS

Domanda: Quale scelta mantiene verificabile cliccare ricevuto prima email secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 3. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.
- 4. Prima di cliccare su un link ricevuto via email, è necessario verificare mittente, dominio e contenuto del messaggio. (corretta inferita)

Risposta corretta: Prima di cliccare su un link ricevuto via email, è necessario verificare mittente, dominio e contenuto del messaggio.
Spiegazione: Il punto da riconoscere è prima cliccare ricevuto email: la soluzione selezionata conserva il legame con il contenuto fonte. Un distrattore modifica fase, responsabilità o tracciabilità e per questo perde coerenza con il documento.
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 3 - PASS

Domanda: Quale scelta mantiene verificabile aziendali essere devono trattati secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 3. I dati aziendali devono essere trattati solo per finalità autorizzate e conservati in strumenti approvati dall'organizzazione. (corretta inferita)
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: I dati aziendali devono essere trattati solo per finalità autorizzate e conservati in strumenti approvati dall'organizzazione.
Spiegazione: Per rispondere bisogna tenere insieme concetto, prova e conseguenza operativa. L'opzione più adatta riprende aziendali devono essere trattati, mentre una scelta generica non chiarisce chi verifica il passaggio e con quale evidenza. In pr...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`

#### Domanda 4 - PASS

Domanda: Quale scelta mantiene verificabile allegati provenienti fonti verificate secondo il documento?

Opzioni:
- 1. Scegliere una fase operativa diversa e registrare il controllo senza collegarlo a evidenza, responsabilità e verifica.
- 2. Gli allegati provenienti da fonti non verificate possono contenere malware o tentativi di phishing. (corretta inferita)
- 3. Conservare una registrazione parziale dell'attività, lasciando non controllabile l'esito richiesto dal documento.
- 4. Usare una nota generica sul rischio senza indicare decisione, fonte documentale e responsabilità verificabile.

Risposta corretta: Gli allegati provenienti da fonti non verificate possono contenere malware o tentativi di phishing.
Spiegazione: La domanda verifica allegati provenienti fonti verificate come passaggio concreto, non come formula astratta. La scelta migliore resta ancorata al contenuto; un distrattore confonde contesto o controllo e riduce il valore didattico. In p...
Giudizio qualità: `PASS`
Difetti item: `[]`
Warning item: `[]`
