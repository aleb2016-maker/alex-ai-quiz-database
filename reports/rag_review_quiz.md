# Review quiz generato da RAG

- File sorgente: `dist/generated/rag_quiz_generato.json`
- File review: `review/rag/quiz_da_revisionare.json`
- Domande trovate: 3
- Stato: OK

## Avvisi da revisionare

- Domanda 1: opzione A: distrattore troppo lontano dalla risposta corretta (similarità 0.06).
- Domanda 1: opzione C: distrattore troppo lontano dalla risposta corretta (similarità 0.05).
- Domanda 1: almeno due distrattori sembrano troppo lontani: la risposta corretta potrebbe essere individuabile per eliminazione.
- Domanda 3: opzione A: distrattore troppo lontano dalla risposta corretta (similarità 0.06).
- Domanda 3: opzione D: distrattore troppo lontano dalla risposta corretta (similarità 0.00).
- Domanda 3: opzione D: sembra generica o fuori tema (semplificare).
- Domanda 3: almeno due distrattori sembrano troppo lontani: la risposta corretta potrebbe essere individuabile per eliminazione.
- Domanda 3: opzione A: distrattore poco collegato al testo della domanda.
- Domanda 3: opzione C: distrattore poco collegato al testo della domanda.
- Domanda 3: opzione D: distrattore poco collegato al testo della domanda.

## Regola di sicurezza

Questo script non modifica mai i file dentro `data/`.
Le domande generate dal RAG passano prima dalla cartella `review/rag/`.
Solo dopo revisione e approvazione potranno essere importate nei database ufficiali.
