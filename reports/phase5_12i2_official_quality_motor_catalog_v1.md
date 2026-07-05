# FASE 5.12I.2 — CATALOGO UFFICIALE MOTORI QUALITÀ DA LISTA SALVATA

Status: `PASS - Fase 5.12I.2: OFFICIAL_QUALITY_MOTOR_CATALOG_READY`

## Sintesi corretta

- Motori qualità ufficiali spiegati: `64`
- Registry totale dopo H.2: `73`
- Nota: Il registry H.2 conta 73 elementi di orchestrazione/route; la lista ufficiale salvata dei motori qualità contiene 64 motori QM spiegati.

## Route per sezione

| Sezione | Controlli qualità G.2 | Selector/orchestrator | Totale route | Selector/orchestrator IDs |
|---|---:|---:|---:|---|
| Card | 52 | 8 | 60 | `qm_051`, `qm_052`, `qm_053`, `qm_054`, `qm_055`, `qm_056`, `qm_057`, `qm_058` |
| Riassunto | 47 | 8 | 55 | `qm_051`, `qm_052`, `qm_053`, `qm_054`, `qm_055`, `qm_056`, `qm_057`, `qm_058` |
| Domande studio | 43 | 8 | 51 | `qm_051`, `qm_052`, `qm_053`, `qm_054`, `qm_055`, `qm_056`, `qm_057`, `qm_058` |
| Test/Quiz | 55 | 8 | 63 | `qm_051`, `qm_052`, `qm_053`, `qm_054`, `qm_055`, `qm_056`, `qm_057`, `qm_058` |

## Lista ufficiale completa dei motori qualità

| QM | Gruppo | Nome | Cosa fa | Universale | Usato da | Stato |
|---|---|---|---|---|---|---|
| `qm_001` | Controlli qualità testuale | Grammatica italiana corretta | Controlla che l’output non contenga errori grammaticali italiani. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_002` | Controlli qualità testuale | Accenti corretti | Controlla accenti su parole come perché, può, più, già, cioè, così, però, qual è. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_003` | Controlli qualità testuale | Apostrofi corretti | Controlla apostrofi in forme come un’informazione, un’idea, un’azione, l’utente, d’accordo. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_004` | Controlli qualità testuale | Punteggiatura corretta | Controlla uso corretto di punti, virgole, due punti, punti interrogativi ed esclamativi. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_005` | Controlli qualità testuale | Spazi corretti prima/dopo punteggiatura | Controlla spazi doppi, spazi mancanti e spazi errati prima o dopo la punteggiatura. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_006` | Controlli qualità testuale | Frasi complete | Verifica che le frasi abbiano senso compiuto e struttura completa. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_007` | Controlli qualità testuale | Assenza di frasi spezzate | Blocca frasi spezzate, tagliate o montate male. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_008` | Controlli qualità testuale | Assenza di frasi non terminate | Blocca frasi che iniziano ma non arrivano a una chiusura logica. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_009` | Controlli qualità testuale | Assenza di finali sospetti | Blocca finali sospetti come frasi che finiscono con e, di, con, per, che, del, della. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_010` | Controlli qualità testuale | Assenza di frasi riempitive | Blocca frasi inutili, decorative, vuote o che allungano senza aggiungere contenuto. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_011` | Controlli qualità testuale | Assenza di testo generico | Blocca frasi generiche come documento analizzato, contenuti generati, punto centrale quando non sono specifiche. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_012` | Controlli qualità testuale | Assenza di vecchi fallback/demo/test | Blocca residui di fallback, demo, esempi di test e testi vecchi non derivati dal documento reale. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_013` | Controlli qualità didattica | Domande studio naturali | Verifica che le domande studio siano naturali e non robotiche. | no | Domande studio | attivo |
| `qm_014` | Controlli qualità didattica | Domande studio utili per ripassare | Verifica che le domande aiutino davvero a ripassare il contenuto. | no | Domande studio | attivo |
| `qm_015` | Controlli qualità didattica | Risposte guida specifiche | Verifica che le risposte guida siano specifiche, concrete e aderenti al contenuto. | no | Domande studio | attivo |
| `qm_016` | Controlli qualità didattica | Spiegazioni test chiare | Verifica che le spiegazioni dei quiz siano chiare e comprensibili. | no | Test/Quiz | attivo |
| `qm_017` | Controlli qualità didattica | Spiegazioni non troppo corte | Blocca spiegazioni troppo brevi, vuote o insufficienti. | no | Test/Quiz, Domande studio | attivo |
| `qm_018` | Controlli qualità didattica | Tono didattico finale | Controlla che il tono sia didattico, utile e adatto allo studio. | no | Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_019` | Controlli qualità didattica | Categorie presenti | Verifica che siano presenti categorie quando servono a organizzare il contenuto. | no | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_020` | Controlli qualità didattica | Sottocategorie presenti | Verifica che siano presenti sottocategorie quando servono a rendere l’output più preciso. | no | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_021` | Controlli qualità didattica | Coerenza tra domanda, risposta e contenuto | Controlla che domanda, risposta e contenuto originale siano coerenti. | no | Domande studio, Test/Quiz | attivo |
| `qm_022` | Controlli qualità didattica | Niente risposte vaghe | Blocca risposte vaghe, generiche o scollegate dal documento. | no | Domande studio, Test/Quiz | attivo |
| `qm_023` | Controlli card / riassunto / fonti | Card scritte bene | Verifica che le card siano scritte bene, leggibili e utili. | no | Card | attivo |
| `qm_024` | Controlli card / riassunto / fonti | Card non troppo corte | Blocca card troppo povere o con contenuto insufficiente. | no | Card | attivo |
| `qm_025` | Controlli card / riassunto / fonti | Card non troppo compresse | Blocca card troppo dense, schiacciate o difficili da leggere. | no | Card | attivo |
| `qm_026` | Controlli card / riassunto / fonti | Messaggio chiave completo | Verifica che il messaggio chiave sia completo e non monco. | no | Card, Riassunto | attivo |
| `qm_027` | Controlli card / riassunto / fonti | Riassunto chiaro | Verifica che il riassunto sia chiaro, ordinato e comprensibile. | no | Riassunto | attivo |
| `qm_028` | Controlli card / riassunto / fonti | Punti chiave leggibili | Verifica che i punti chiave siano leggibili, utili e non confusi. | no | Card, Riassunto | attivo |
| `qm_029` | Controlli card / riassunto / fonti | Fonti visibili belle | Verifica che le fonti siano visibili, pulite e presentate bene. | no | Card, Riassunto | attivo |
| `qm_030` | Controlli card / riassunto / fonti | Fonti coerenti | Verifica fonti coerenti, ad esempio Fonte: sezione “Sicurezza informatica”. | no | Card, Riassunto | attivo |
| `qm_031` | Controlli card / riassunto / fonti | Niente fonti brutte | Blocca fonti brutte o tecniche come knowledge_base_json o Documento analizzato. | no | Card, Riassunto | attivo |
| `qm_032` | Controlli card / riassunto / fonti | Layout grafico controllato | Controlla struttura, layout grafico, leggibilità e ordine visuale. | no | Card | attivo |
| `qm_033` | Controlli test separati | Test separato da card/riassunto/domande studio | Garantisce che il test non venga mischiato con card, riassunto o domande studio. | no | Test/Quiz | attivo |
| `qm_034` | Controlli test separati | Opzioni interne validate | Valida le opzioni interne del quiz prima della visualizzazione. | no | Test/Quiz | attivo |
| `qm_035` | Controlli test separati | Opzioni visibili pulite | Controlla che le opzioni mostrate all’utente siano pulite e leggibili. | no | Test/Quiz | attivo |
| `qm_036` | Controlli test separati | Risposta corretta interna | Verifica che la risposta corretta interna sia presente e valida. | no | Test/Quiz | attivo |
| `qm_037` | Controlli test separati | Risposta corretta visibile | Verifica che la risposta corretta visibile sia coerente con quella interna. | no | Test/Quiz | attivo |
| `qm_038` | Controlli test separati | Mappa sicura tra risposta interna e visibile | Controlla la mappa tra risposta interna, risposta visibile e opzioni. | no | Test/Quiz | attivo |
| `qm_039` | Controlli test separati | 4 opzioni per domanda | Verifica che ogni domanda abbia esattamente quattro opzioni. | no | Test/Quiz | attivo |
| `qm_040` | Controlli test separati | Risposta corretta presente tra le opzioni | Verifica che la risposta corretta sia presente tra le opzioni disponibili. | no | Test/Quiz | attivo |
| `qm_041` | Controlli test separati | Distrattori forti | Verifica che i distrattori siano plausibili, forti e non banali. | no | Test/Quiz | attivo |
| `qm_042` | Controlli test separati | Niente opzioni duplicate nella stessa domanda | Blocca duplicati tra le opzioni della stessa domanda. | no | Test/Quiz | attivo |
| `qm_043` | Controlli test separati | Niente ripetizioni globali eccessive | Blocca ripetizioni eccessive tra domande, risposte e opzioni. | no | Test/Quiz | attivo |
| `qm_044` | Controlli test separati | Compatibilità obbligatoria col bridge motori quiz V3.5B | Verifica che il quiz sia compatibile con il bridge motori quiz V3.5B. | no | Test/Quiz | attivo |
| `qm_045` | Controlli duplicati e ripetizioni | Duplicati esatti | Rileva contenuti esattamente duplicati. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_046` | Controlli duplicati e ripetizioni | Quasi duplicati | Rileva contenuti quasi identici o troppo sovrapponibili. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_047` | Controlli duplicati e ripetizioni | Ripetizioni inutili | Blocca ripetizioni che non aggiungono valore. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_048` | Controlli duplicati e ripetizioni | Ripetizioni meccaniche tra domande | Blocca ripetizioni meccaniche tra domande, soprattutto in domande studio e quiz. | no | Domande studio, Test/Quiz | attivo |
| `qm_049` | Controlli duplicati e ripetizioni | Frasi troppo simili | Rileva frasi troppo simili tra loro. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_050` | Controlli duplicati e ripetizioni | Stesso contenuto ripetuto senza motivo | Blocca lo stesso contenuto ripetuto senza motivo; distingue però ripetizioni legittime tra sezioni diverse. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_051` | Controlli selezionatore / orchestratore | Il compito richiesto deve selezionare i motori giusti | Seleziona i motori corretti in base alla richiesta dell’utente. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_052` | Controlli selezionatore / orchestratore | Riassunto → motore didattico | Quando l’utente chiede un riassunto, instrada verso i motori didattici e di sintesi corretti. | no | Riassunto | attivo |
| `qm_053` | Controlli selezionatore / orchestratore | Card → motore didattico + layout | Quando l’utente chiede card, instrada verso motori didattici e layout. | no | Card | attivo |
| `qm_054` | Controlli selezionatore / orchestratore | Domande studio → motore didattico | Quando l’utente chiede domande studio, instrada verso motori didattici. | no | Domande studio | attivo |
| `qm_055` | Controlli selezionatore / orchestratore | Test → bridge quiz + motore test + bridge quiz | Quando l’utente chiede test, instrada verso bridge quiz, motore test e compatibilità quiz. | no | Test/Quiz | attivo |
| `qm_056` | Controlli selezionatore / orchestratore | Completo/PDF/app/web → orchestratore | Quando l’utente chiede output completo, PDF, app o web, passa dal livello orchestratore. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_057` | Controlli selezionatore / orchestratore | Niente motori inutili | Evita di attivare motori non necessari per il compito richiesto. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_058` | Controlli selezionatore / orchestratore | Niente output non richiesto | Evita output extra non richiesti dall’utente. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_059` | Controlli selezionatore / orchestratore | Output finale pronto per UI/PDF/app | Verifica che l’output finale sia pronto per essere usato in UI, PDF o app. | sì | Card, Riassunto, Domande studio, Test/Quiz | da verificare alla fine |
| `qm_060` | Controlli selezionatore / orchestratore | Report qualità sempre leggibile | Garantisce che il report qualità sia sempre chiaro, leggibile e utile. | sì | Card, Riassunto, Domande studio, Test/Quiz | da ricreare/collegare |
| `qm_061` | Controlli linguistici avanzati / repair | Naturalezza linguistica anti-keyword | Blocca frasi robotiche, liste grezze di parole chiave e testi meccanici; l’output deve sembrare scritto da una persona. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_062` | Controlli linguistici avanzati / repair | Accordo grammaticale e pronomi | Verifica genere, numero, articoli, participi e pronomi collegati a titoli e contenuti. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_063` | Controlli linguistici avanzati / repair | Correzione frasi non finite con contesto | Corregge frasi non finite usando contesto, tema, sottotema e sottocategorie. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |
| `qm_064` | Controlli linguistici avanzati / repair | Correzione parole scritte male con lettere invertite | Corregge parole scritte male, lettere invertite e micro-errori ortografici. | sì | Card, Riassunto, Domande studio, Test/Quiz | attivo |

## Defects

- Nessuno

## Warnings

- Nessuno

## Note

- Catalogo corretto usando la lista ufficiale salvata dall’utente.
- Nessun qm_065–qm_073 viene inventato.
- qm_059 e qm_060 sono inclusi come controlli finali selector/orchestrator.
- La distinzione corretta è: 64 motori qualità QM spiegati; 73 elementi totali nel registry/orchestrazione H.2.
