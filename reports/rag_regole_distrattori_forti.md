# Report aggiornamento prompt RAG

Il prompt di `scripts/rag_genera_quiz_json.py` è stato aggiornato per rendere più forti i distrattori generati dal RAG.

## Obiettivo

Ridurre domande troppo facili e opzioni eliminabili per intuizione.

## Nuova richiesta al modello

Ogni distrattore deve:

- condividere il tema della risposta corretta
- sembrare plausibile
- essere sbagliato per un dettaglio preciso
- non essere assurdo
- non essere fuori tema
- non far risaltare troppo la risposta corretta

## Stato

Pronto per nuovo test con Ollama.
