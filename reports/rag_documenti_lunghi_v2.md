# Report RAG documenti lunghi V2A

## Stato

- V2A separata creata.
- Usa il manager V1 per pagine, chunk e batch.
- Genera riassunti parziali batch per batch.
- Genera un riassunto finale progressivo.
- Riconosce il profilo del documento e usa keyword adatte al tema.
- Le keyword finali devono essere micro-concetti di 2 o 3 parole, non parole singole isolate.
- Non collega la demo ufficiale.
- Non tocca PDF export.
- Non tocca TXT/HTML/JSON export.
- Non tocca grafica.

## Metriche test

- Pagine logiche: 120
- Chunk: 240
- Batch: 30
- Riassunti parziali: 30
- Caratteri riassunto finale: 2264
- Profilo riconosciuto: Documento aziendale (business)
- Keyword finali: procedure aziendali, responsabilità operative, workflow e responsabilità, audit e controlli, documentazione tecnica, fornitori e terze parti, continuità operativa, onboarding e formazione, sicurezza informatica, backup e recupero, incidenti e risposta, privacy e dati

## Prossimo passo

V2B: aggiungere generazione progressiva delle card, sempre su pagina separata.
