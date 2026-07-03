# Mini LLM V400.4 - Produzione multi-documento

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
- Concetti: intelligenza artificiale generativa, modelli linguistici, documenti reali, controlli qualità, diagnostica chiara, fallback nascosti, applicazioni aziendali, materiali di studio, rischi principali, uso del rag
- Summary: `GENERATED` errori `[]`
- Answer: `GENERATED` errori `[]`
- Cards: `GENERATED` errori `[]` count `6`
- Tempo: `163` ms
- Output MD: `reports/mini_llm_v4004/ai_generativa.md`

### informatica_sicurezza_rag

- Source: `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- Status suite: `PRODUCED`
- Titolo: Documento RAG di test: Sicurezza informatica aziendale
- Dominio: sicurezza informatica
- Parole input: `1673`
- Sezioni: `13`
- Concetti: sicurezza informatica, password sicure, autenticazione a due fattori, phishing, malware, ransomware, backup, aggiornamenti software, dati sensibili, credenziali
- Summary: `QUALITY_BLOCKED` errori `['RIASSUNTO_SOTTO_SOGLIA']`
- Answer: `GENERATED` errori `[]`
- Cards: `GENERATED` errori `[]` count `5`
- Tempo: `184` ms
- Output MD: `reports/mini_llm_v4004/informatica_sicurezza_rag.md`

### business_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/business.md`
- Status suite: `PRODUCED`
- Titolo: business
- Dominio: documento aziendale
- Parole input: `23`
- Sezioni: `1`
- Concetti: processo aziendale, responsabilità, scadenze, comunicazione, errori operativi, chiarezza delle procedure
- Summary: `GENERATED_SHORT` errori `[]`
- Answer: `GENERATED_SHORT` errori `[]`
- Cards: `GENERATED_SHORT` errori `[]` count `1`
- Tempo: `1` ms
- Output MD: `reports/mini_llm_v4004/business_v396.md`

### curriculum_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/curriculum.md`
- Status suite: `PRODUCED`
- Titolo: curriculum
- Dominio: curriculum vitae
- Parole input: `25`
- Sezioni: `1`
- Concetti: esperienze, formazione, competenze tecniche, profilo professionale, ruolo, obiettivo professionale
- Summary: `GENERATED_SHORT` errori `[]`
- Answer: `GENERATED_SHORT` errori `[]`
- Cards: `GENERATED_SHORT` errori `[]` count `1`
- Tempo: `0` ms
- Output MD: `reports/mini_llm_v4004/curriculum_v396.md`

### informatics_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/informatics.md`
- Status suite: `PRODUCED`
- Titolo: informatics
- Dominio: sicurezza informatica
- Parole input: `30`
- Sezioni: `1`
- Concetti: sicurezza informatica, phishing, ransomware, account
- Summary: `GENERATED_SHORT` errori `[]`
- Answer: `GENERATED` errori `[]`
- Cards: `GENERATED` errori `[]` count `5`
- Tempo: `0` ms
- Output MD: `reports/mini_llm_v4004/informatics_v396.md`

### science_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/science.txt`
- Status suite: `PRODUCED`
- Titolo: science
- Dominio: scientifico
- Parole input: `26`
- Sezioni: `1`
- Concetti: ipotesi, metodo sperimentale, risultati, campione, solidità, limiti dello studio
- Summary: `GENERATED_SHORT` errori `[]`
- Answer: `GENERATED_SHORT` errori `[]`
- Cards: `GENERATED_SHORT` errori `[]` count `1`
- Tempo: `1` ms
- Output MD: `reports/mini_llm_v4004/science_v396.md`

### sport_v396

- Source: `mini_llm/data/real_tests/test_v396_current_engine/sport.txt`
- Status suite: `PRODUCED`
- Titolo: sport
- Dominio: sport e allenamento
- Parole input: `26`
- Sezioni: `1`
- Concetti: programma di allenamento, esercizi di forza, serie, ripetizioni, recupero, adattamento del carico
- Summary: `GENERATED_SHORT` errori `[]`
- Answer: `GENERATED_SHORT` errori `[]`
- Cards: `GENERATED_SHORT` errori `[]` count `1`
- Tempo: `1` ms
- Output MD: `reports/mini_llm_v4004/sport_v396.md`
