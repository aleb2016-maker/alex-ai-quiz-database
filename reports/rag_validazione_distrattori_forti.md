# Validazione distrattori forti RAG

- File controllato: `dist/generated/rag_quiz_generato.json`
- Domande controllate: 3
- Avvisi trovati: 10

## Avvisi

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

## Nota

Il controllo usa agganci tecnici tra domanda, risposta, spiegazione e distrattori. Non si basa solo su parole identiche nella risposta corretta.
