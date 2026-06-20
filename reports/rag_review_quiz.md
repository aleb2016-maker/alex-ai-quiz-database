# Review quiz generato da RAG

- File sorgente: `dist/generated/rag_quiz_generato.json`
- File review: `review/rag/quiz_da_revisionare.json`
- Domande trovate: 3
- Stato: OK

## Avvisi da revisionare

- Domanda 1: i distrattori sembrano poco vicini alla risposta corretta.
- Domanda 2: i distrattori sembrano poco vicini alla risposta corretta.

## Regola di sicurezza

Questo script non modifica mai i file dentro `data/`.
Le domande generate dal RAG passano prima dalla cartella `review/rag/`.
Solo dopo revisione e approvazione potranno essere importate nei database ufficiali.
