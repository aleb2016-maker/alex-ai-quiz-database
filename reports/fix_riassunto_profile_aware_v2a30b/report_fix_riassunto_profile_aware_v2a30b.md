# Fix riassunto profile-aware V2A30

Modificati solo i motori riassunto:

- `demo-rag/universal-document-learning-engine.js`
- `runtime/web/rag-large-document-progressive-summary-v2.js`

## Obiettivo

- Riassunto breve/medio senza collage forzato a 2500 caratteri.
- Riassunto lungo con topic dipendenti dal profilo documento.
- Niente frasi universali aziendali/cybersecurity per sport, poesia, racconto, CV, personale o hobby.
- Nessun intervento su HTML, CSS, pulsanti, PDF, card, test o domande studio.
