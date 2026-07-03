# Mini LLM Engine Registry V400

Questo report non crea un nuovo motore da zero.

Serve a catalogare il lavoro già fatto sui motori V del mini LLM e a decidere cosa riusare, cosa rafforzare e cosa mettere in quarantena.

## Regole operative

- Non ripartire da zero.
- Non buttare i motori V esistenti.
- Riusare i blocchi buoni.
- Mettere in quarantena i motori che producono output brutto.
- Il PASS finale deve dipendere dall'output generato, non dal file presente.

## Sintesi

- `total_engines_registered`: `14`
- `existing_files`: `14`
- `missing_files`: `0`
- `decisions`: `{'RIUSARE_CON_CONTROLLI': 2, 'RIUSARE_E_RAFFERZARE': 1, 'RIUSARE_CON_REGRESSIONI': 1, 'RIUSARE': 4, 'RIUSARE_COME_ADAPTER': 1, 'RIUSARE_COME_CUORE_CURRENT': 1, 'RIUSARE_PER_CARD_STUDIO_DOMANDE': 1, 'RIUSARE_SE_PASSA_GATE': 1, 'RIUSARE_PER_VELOCITA': 1, 'QUARANTENA_TEST_NEGATIVO': 1}`

## Motori registrati

### long_document_rag_v39

- File: `mini_llm/python/runtime/mini_llm_long_document_rag_v39.py`
- Stato file: `PRESENTE`
- Ruolo: RAG documenti lunghi base
- Decisione: `RIUSARE_CON_CONTROLLI`
- Motivo: Base storica per documenti lunghi; non deve essere buttata, ma va passata da quality gate finale.

### long_document_rag_v391_semantic_repair

- File: `mini_llm/python/runtime/mini_llm_long_document_rag_v391_semantic_repair.py`
- Stato file: `PRESENTE`
- Ruolo: Riparazione semantica RAG documenti lunghi
- Decisione: `RIUSARE_CON_CONTROLLI`
- Motivo: Motore successivo al V3.9; utile per recupero/semantica, ma non basta da solo a certificare qualità output.

### real_quality_gate_v392

- File: `mini_llm/data/fast_runtime/mini_llm_real_quality_gate_v392_validation.json`
- Stato file: `PRESENTE`
- Ruolo: Quality gate reale V3.9.2
- Decisione: `RIUSARE_E_RAFFERZARE`
- Motivo: Checkpoint qualità reale già presente; va rafforzato su output visibile finale.

### real_output_cleaner_v3931

- File: `mini_llm/data/fast_runtime/mini_llm_practical_real_test_v393_clean_validation.json`
- Stato file: `PRESENTE`
- Ruolo: Pulizia output reale V3.9.3.1
- Decisione: `RIUSARE_CON_REGRESSIONI`
- Motivo: Pulizia utile, ma deve evitare di distruggere segnali di dominio nei testi corti.

### universal_core_split_v394u

- File: `mini_llm/python/runtime/universal/mini_llm_universal_linguistic_core_v394u.py`
- Stato file: `PRESENTE`
- Ruolo: Core linguistico universale separato
- Decisione: `RIUSARE`
- Motivo: Blocco universale già separato; deve diventare parte dell'orchestratore.

### universal_relevance_core_v394u

- File: `mini_llm/python/runtime/universal/mini_llm_universal_relevance_core_v394u.py`
- Stato file: `PRESENTE`
- Ruolo: Core rilevanza universale
- Decisione: `RIUSARE`
- Motivo: Serve per domanda-risposta e recupero passaggi rilevanti.

### universal_question_core_v394u

- File: `mini_llm/python/runtime/universal/mini_llm_universal_question_core_v394u.py`
- Stato file: `PRESENTE`
- Ruolo: Core domande universale
- Decisione: `RIUSARE`
- Motivo: Serve per domande studio, quiz e risposta guidata.

### domain_profiles_v394u

- File: `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py`
- Stato file: `PRESENTE`
- Ruolo: Registro profili dominio
- Decisione: `RIUSARE`
- Motivo: Serve per riconoscere informatica, business, curriculum, scienza, sport e generico.

### universal_llm_bridge_v395

- File: `mini_llm/python/runtime/mini_llm_universal_llm_bridge_v395.py`
- Stato file: `PRESENTE`
- Ruolo: Bridge universale mini LLM
- Decisione: `RIUSARE_COME_ADAPTER`
- Motivo: Serve come ponte tra core universale e motori di generazione.

### universal_current_engine_v396

- File: `mini_llm/python/runtime/mini_llm_universal_current_engine_v396.py`
- Stato file: `PRESENTE`
- Ruolo: Current engine universale
- Decisione: `RIUSARE_COME_CUORE_CURRENT`
- Motivo: Checkpoint forte: documento reale e multi-dominio già validati; da collegare al quality gate finale.

### study_pack_universal_v397

- File: `mini_llm/python/runtime/mini_llm_universal_study_pack_v4.py`
- Stato file: `PRESENTE`
- Ruolo: Study pack universale V4
- Decisione: `RIUSARE_PER_CARD_STUDIO_DOMANDE`
- Motivo: Checkpoint V3.9.7; utile per card, domande studio e materiale didattico.

### study_pack_current

- File: `mini_llm/python/runtime/mini_llm_study_pack_current.py`
- Stato file: `PRESENTE`
- Ruolo: Study pack current
- Decisione: `RIUSARE_SE_PASSA_GATE`
- Motivo: Motore current già presente; va usato solo se il quality gate finale approva l'output.

### fast_qa_summary_current

- File: `mini_llm/python/runtime/fast_qa_summary_current.py`
- Stato file: `PRESENTE`
- Ruolo: QA/summary veloce current
- Decisione: `RIUSARE_PER_VELOCITA`
- Motivo: Serve per benchmark velocità e risposte rapide, ma deve passare dal controllo qualità.

### natural_sentence_v35_family

- File: `mini_llm/data/inference_v31_natural/inference_engine_v31_natural_outputs.json`
- Stato file: `PRESENTE`
- Ruolo: Vecchia generazione frase naturale
- Decisione: `QUARANTENA_TEST_NEGATIVO`
- Motivo: Famiglia da usare come regressione negativa: non deve più passare output grammaticalmente assurdi.

## Git log rilevante

- `d1d90b7 (HEAD -> rag-concept-app-presentabile-v3, tag: checkpoint-mini-llm-study-pack-universale-v397, origin/rag-concept-app-presentabile-v3) Aggiunge Study Pack Universale V4 V3.9.7`
- `496fbca (tag: checkpoint-mini-llm-universal-current-engine-v396) Aggiunge current engine universale mini LLM V3.9.6`
- `b4d0b72 (tag: checkpoint-mini-llm-universal-llm-bridge-v395) Collega mini LLM al core universale V3.9.5`
- `a4ccd83 (tag: checkpoint-mini-llm-universal-core-split-v394u) Separa core universale e profili mini LLM V3.9.4U`
- `27e2175 (tag: checkpoint-mini-llm-query-context-expander-v394) Aggiunge context expander domande mini LLM V3.9.4`
- `899e2f2 (tag: checkpoint-mini-llm-real-output-cleaner-v3931) Pulisce test pratico reale mini LLM V3.9.3.1`
- `c08bcdc (tag: checkpoint-mini-llm-real-quality-gate-v392) Aggiunge real quality gate mini LLM V3.9.2`
- `e448e26 (tag: checkpoint-mini-llm-practical-real-test-v391) Aggiunge test pratico reale mini LLM V3.9.1`
- `a6d8e33 (tag: checkpoint-mini-llm-long-document-rag-v391-semantic-repair) Blinda RAG documenti lunghi mini LLM V3.9.1`
- `4e9e571 (tag: checkpoint-mini-llm-long-document-rag-v39) Aggiunge RAG documenti lunghi mini LLM V3.9`
- `e96ba29 (tag: checkpoint-mini-llm-output-modes-v1) Aggiunge output modes al mini LLM`
- `b09e568 (tag: checkpoint-mini-llm-study-pack-current-v3-clean) Imposta study pack current stabile su V3`
- `15b658b (tag: checkpoint-mini-llm-study-pack-cli-v2) Collega study pack V3 alla CLI mini LLM`
- `0858f0d (tag: checkpoint-mini-llm-study-pack-v3-quality-gate) Aggiunge quality gate forte study pack mini LLM V3`
- `64783de (tag: checkpoint-mini-llm-study-pack-cli-v1) Collega study pack mini LLM alla CLI`
- `904465a (tag: checkpoint-mini-llm-study-pack-v2-quality) Migliora qualità study pack mini LLM V2`
- `73b6472 (tag: checkpoint-mini-llm-study-pack-v1) Aggiunge study pack veloce mini LLM V1`
- `89c4c5c (tag: checkpoint-mini-llm-document-cli-pdf-v1-clean) Chiude supporto PDF testuale mini LLM V1`
- `eb0cdcc (tag: checkpoint-mini-llm-document-cli-pdf-v1) Aggiunge supporto PDF testuale alla CLI mini LLM`
- `ca4527f (tag: checkpoint-mini-llm-documentale-integrato-v1) Aggiunge smoke test integrato mini LLM documentale`
- `f3b6851 (tag: checkpoint-mini-llm-document-cli-v1-markdown-clean) Pulisce markdown nei riassunti documentali mini LLM`
- `af61898 (tag: checkpoint-mini-llm-document-cli-v1) Aggiunge CLI documentale mini LLM V1`
- `fb00e32 (tag: checkpoint-mini-llm-fast-qa-summary-current) Aggiunge fast Q&A e summary current`
- `c836207 (tag: checkpoint-mini-llm-current-speed-benchmark) Aggiunge benchmark velocità mini LLM current`
- `328f954 (tag: checkpoint-mini-llm-current-v315-stable) Imposta mini LLM V3.15 come motore current stabile`
- `40b18cf (tag: checkpoint-mini-llm-v315-extended-safe) Estende mini LLM con decoder sicuro V3.15`
- `650db17 (tag: checkpoint-mini-llm-v314-rewrite-only-safe) Aggiunge mini LLM V3.14 rewrite-only safe decoder`
- `810f3bd (tag: checkpoint-mini-llm-v311-human-aligned) Aggiunge mini LLM V3.11 human aligned decoder`
- `4f2272d Aggiunge diagnostica raw e quality gate mini LLM`
- `7dec5e0 Aggiunge inferenza V3.1 naturale per mini LLM`
- `1a685eb Aggiunge modello neurale V3.1 naturale per mini LLM`
- `622a2af Aggiunge vectorizer V2.1 naturale per mini LLM`
- `afb8c84 Aggiunge dataset V2.1 naturale per mini LLM`
- `e7bb2c8 Aggiunge modello neurale V3 pulito per mini LLM`
- `2eea88b Aggiunge vectorizer V2 pulito per mini LLM`
- `1125101 Aggiunge dataset V2 pulito per mini LLM`
- `09aaaa5 Aggiunge filtri pulizia inferenza V2.1 per mini LLM`
- `ab588fb Aggiunge motore inferenza V1 per mini LLM`
- `6647185 Aggiunge primo modello neurale V1 per mini LLM`
- `24791c2 Aggiunge vettorizzazione token V1 per mini LLM`
- `a3fed8c Aggiunge dataset training V1 per mini LLM`
- `8b4355f Aggiunge Knowledge Engine V1 per mini LLM`
