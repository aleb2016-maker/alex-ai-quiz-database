# Validazione distrattori forti RAG

- File controllato: `dist/generated/rag_quiz_generato.json`
- Domande controllate: 3
- Avvisi trovati: 10

## Avvisi

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

## Nota

Questo controllo non approva automaticamente le domande. Serve a rendere la review più severa prima di qualsiasi import nei database ufficiali.
