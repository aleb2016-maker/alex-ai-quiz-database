# Mini LLM V400.3 - Produzione multi-documento

Questo report produce output reali su più documenti già presenti nel progetto.

Non modifica UI, pulsanti, PDF o grafica.

## Sintesi

- Documenti testati: `7`
- Documenti prodotti: `7`

## Risultati

### ai_generativa

- Source: `rag/documenti/documento_ai_generativa_test_rag.md`
- Status suite: `PRODUCED`
- Titolo: Documento di prova RAG - Intelligenza Artificiale Generativa
- Dominio: intelligenza artificiale generativa e RAG
- Parole input: `617`
- Sezioni: `8`
- Concetti: intelligenza artificiale generativa, modelli linguistici, documenti reali, controlli qualità, diagnostica chiara, diagnostica utile, fallback nascosti, applicazioni aziendali, materiali di studio, card studio
- Summary: `GENERATED` errori `[]`
- Answer: `GENERATED` errori `[]`
- Cards: `GENERATED` errori `[]` count `6`
- Tempo: `146` ms
- Output MD: `reports/mini_llm_v4003/ai_generativa.md`

### informatica_sicurezza_rag

- Source: `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- Status suite: `PRODUCED`
- Titolo: Documento RAG di test: Sicurezza informatica aziendale
- Dominio: intelligenza artificiale generativa e RAG
- Parole input: `1673`
- Sezioni: `13`
- Concetti: quiz, errori, scopo del documento, 2. password sicure, 3. autenticazione a due fattori, 4. phishing, 5. malware e allegati pericolosi, 6. backup, 7. aggiornamenti software, 8. dati sensibili
- Summary: `QUALITY_BLOCKED` errori `['PARAGRAFI_RIASSUNTO_INSUFFICIENTI', 'RIASSUNTO_SOTTO_SOGLIA']`
- Answer: `GENERATED` errori `[]`
- Cards: `NO_CARD_CONTEXT` errori `[]` count `0`
- Tempo: `100` ms
- Output MD: `reports/mini_llm_v4003/informatica_sicurezza_rag.md`

### business_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/business.md`
- Status suite: `PRODUCED`
- Titolo: business
- Dominio: errori
- Parole input: `23`
- Sezioni: `1`
- Concetti: errori, aziendale, definisce, processo, responsabilità, scadenze, comunicazione, insufficiente, generare, operativi
- Summary: `SOURCE_TOO_SHORT` errori `[]`
- Answer: `GENERATED` errori `[]`
- Cards: `NO_CARD_CONTEXT` errori `[]` count `0`
- Tempo: `2` ms
- Output MD: `reports/mini_llm_v4003/business_v396.md`

### curriculum_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/curriculum.md`
- Status suite: `PRODUCED`
- Titolo: curriculum
- Dominio: curriculum vitae
- Parole input: `25`
- Sezioni: `1`
- Concetti: curriculum, presenta, esperienze, formazione, competenze, tecniche, profilo, professionale, chiarire, ruolo
- Summary: `SOURCE_TOO_SHORT` errori `[]`
- Answer: `GENERATED` errori `[]`
- Cards: `NO_CARD_CONTEXT` errori `[]` count `0`
- Tempo: `2` ms
- Output MD: `reports/mini_llm_v4003/curriculum_v396.md`

### informatics_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/informatics.md`
- Status suite: `PRODUCED`
- Titolo: informatics
- Dominio: sicurezza informatica
- Parole input: `30`
- Sezioni: `1`
- Concetti: sicurezza, informatica, protegge, account, sistemi, digitali, phishing, messaggi, ingannevoli, ransomware
- Summary: `SOURCE_TOO_SHORT` errori `[]`
- Answer: `GENERATED` errori `[]`
- Cards: `NO_CARD_CONTEXT` errori `[]` count `0`
- Tempo: `1` ms
- Output MD: `reports/mini_llm_v4003/informatics_v396.md`

### science_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/science.txt`
- Status suite: `PRODUCED`
- Titolo: science
- Dominio: scientifico
- Parole input: `26`
- Sezioni: `1`
- Concetti: scientifico, descrive, ipotesi, metodo, sperimentale, risultati, campione, limitato, ridurre, solidità
- Summary: `SOURCE_TOO_SHORT` errori `[]`
- Answer: `NO_RELEVANT_CONTEXT` errori `[]`
- Cards: `NO_CARD_CONTEXT` errori `[]` count `0`
- Tempo: `1` ms
- Output MD: `reports/mini_llm_v4003/science_v396.md`

### sport_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/sport.txt`
- Status suite: `PRODUCED`
- Titolo: sport
- Dominio: sport e allenamento
- Parole input: `26`
- Sezioni: `1`
- Concetti: programma, allenamento, prevede, esercizi, forza, serie, ripetizioni, recupero, aiuta, adattare
- Summary: `SOURCE_TOO_SHORT` errori `[]`
- Answer: `NO_RELEVANT_CONTEXT` errori `[]`
- Cards: `NO_CARD_CONTEXT` errori `[]` count `0`
- Tempo: `1` ms
- Output MD: `reports/mini_llm_v4003/sport_v396.md`
