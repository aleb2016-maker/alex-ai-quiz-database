# Mini LLM Universal Core Split V3.9.4U.1

- Stato: **PASS**
- Errori: `nessuno`

## Separazione fisica

### Core universale
- `mini_llm/python/runtime/universal/mini_llm_universal_linguistic_core_v394u.py`
- `mini_llm/python/runtime/universal/mini_llm_universal_question_core_v394u.py`
- `mini_llm/python/runtime/universal/mini_llm_universal_relevance_core_v394u.py`

### Profili specialistici
- `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_informatics_v394u.py`
- `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_sport_v394u.py`
- `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_curriculum_v394u.py`
- `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_science_v394u.py`
- `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_business_v394u.py`
- `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_generic_v394u.py`
- `mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py`

## Profili rilevati nei test

- `['business_document_v394u', 'curriculum_profile_v394u', 'informatics_security_v394u', 'science_document_v394u', 'sport_training_v394u']`

## Risultati multi-dominio

### sicurezza informatica aziendale

- Profilo: `informatics_security_v394u`
- Relevance: `PASS`

- Originale: `Quali sono i punti principali del documento?`
  Migliorata: `Quali sono i punti principali su sicurezza informatica aziendale, in particolare sicurezza informatica, phishing, ransomware, malware, password e backup?`
- Originale: `Che cosa devo ricordare?`
  Migliorata: `Che cosa devo ricordare su sicurezza informatica aziendale, in particolare password sicure, phishing, backup, autenticazione a due fattori, credenziali e dati sensibili?`
- Originale: `Quali rischi o problemi vengono spiegati nel documento?`
  Migliorata: `Quali rischi o criticità di sicurezza informatica aziendale, legati a phishing, ransomware, malware, password deboli e furto di credenziali, vengono spiegati?`

### sport e allenamento

- Profilo: `sport_training_v394u`
- Relevance: `PASS`

- Originale: `Quali sono i punti principali del documento?`
  Migliorata: `Quali sono i punti principali su sport e allenamento, in particolare obiettivo atletico, esercizi principali, serie, ripetizioni, recupero e progressione del carico?`
- Originale: `Che cosa devo ricordare?`
  Migliorata: `Che cosa devo ricordare su sport e allenamento, in particolare tecnica corretta, riscaldamento, recupero, progressione e ascolto del corpo?`
- Originale: `Quali rischi o problemi vengono spiegati nel documento?`
  Migliorata: `Quali rischi o criticità di sport e allenamento, legati a sovraccarico, infortunio, tecnica scorretta, recupero insufficiente e carico eccessivo, vengono spiegati?`

### curriculum e profilo professionale

- Profilo: `curriculum_profile_v394u`
- Relevance: `PASS`

- Originale: `Quali sono i punti principali del documento?`
  Migliorata: `Quali sono i punti principali su curriculum e profilo professionale, in particolare esperienze lavorative, competenze tecniche, formazione, progetti e obiettivo professionale?`
- Originale: `Che cosa devo ricordare?`
  Migliorata: `Che cosa devo ricordare su curriculum e profilo professionale, in particolare punti di forza, competenze rilevanti, esperienze principali e obiettivo professionale?`
- Originale: `Quali rischi o problemi vengono spiegati nel documento?`
  Migliorata: `Quali rischi o criticità di curriculum e profilo professionale, legati a informazioni poco chiare, esperienze non contestualizzate, competenze generiche e obiettivo non definito, vengono spiegati?`

### documento scientifico

- Profilo: `science_document_v394u`
- Relevance: `PASS`

- Originale: `Quali sono i punti principali del documento?`
  Migliorata: `Quali sono i punti principali su documento scientifico, in particolare ipotesi, metodo sperimentale, dati raccolti, risultati e conclusioni?`
- Originale: `Che cosa devo ricordare?`
  Migliorata: `Che cosa devo ricordare su documento scientifico, in particolare ipotesi, variabili, campione, metodo e risultati?`
- Originale: `Quali rischi o problemi vengono spiegati nel documento?`
  Migliorata: `Quali rischi o criticità di documento scientifico, legati a errore di misura, campione limitato, dati incompleti, interpretazione errata e variabili non controllate, vengono spiegati?`

### documento aziendale

- Profilo: `business_document_v394u`
- Relevance: `PASS`

- Originale: `Quali sono i punti principali del documento?`
  Migliorata: `Quali sono i punti principali su documento aziendale, in particolare obiettivi aziendali, processi, responsabilità, risorse e scadenze?`
- Originale: `Che cosa devo ricordare?`
  Migliorata: `Che cosa devo ricordare su documento aziendale, in particolare responsabilità, priorità, scadenze, procedure e risultati attesi?`
- Originale: `Quali rischi o problemi vengono spiegati nel documento?`
  Migliorata: `Quali rischi o criticità di documento aziendale, legati a ritardi, errori operativi, mancanza di responsabilità, costi non controllati e comunicazione insufficiente, vengono spiegati?`

## Regola architetturale

- Il core universale controlla lingua, domande e pertinenza.
- I profili specialistici forniscono dominio e vocabolario.
- I fix su domanda singola o risposta singola sono vietati.
- Le specializzazioni sono ammesse solo come layer separati.
