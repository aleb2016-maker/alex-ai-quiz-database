# Review quiz generato da RAG

- File sorgente: `dist/generated/rag_quiz_generato.json`
- File review: `review/rag/quiz_da_revisionare.json`
- Domande trovate: 3
- Stato: OK

## Avvisi da revisionare

- Domanda 1: opzione B: distrattore troppo lontano dal nucleo della domanda.
- Domanda 1: opzione C: distrattore troppo lontano dal nucleo della domanda.
- Domanda 1: opzione D: distrattore troppo lontano dal nucleo della domanda.
- Domanda 1: almeno due distrattori sembrano troppo lontani: la risposta corretta potrebbe essere individuabile per eliminazione.
- Domanda 2: opzione B: distrattore troppo lontano dal nucleo della domanda.
- Domanda 2: opzione D: distrattore troppo lontano dal nucleo della domanda.
- Domanda 2: almeno due distrattori sembrano troppo lontani: la risposta corretta potrebbe essere individuabile per eliminazione.
- Domanda 3: opzione C: distrattore troppo lontano dal nucleo della domanda.
- Domanda 3: opzione D: distrattore troppo lontano dal nucleo della domanda.
- Domanda 3: almeno due distrattori sembrano troppo lontani: la risposta corretta potrebbe essere individuabile per eliminazione.

## Regola di sicurezza

Questo script non modifica mai i file dentro `data/`.
Le domande generate dal RAG passano prima dalla cartella `review/rag/`.
Solo dopo revisione e approvazione potranno essere importate nei database ufficiali.
