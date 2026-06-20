# Riparatore automatico distrattori RAG

Questo modulo aggiunge un ciclo di correzione automatica dopo la generazione RAG.

## Flusso

RAG legge i documenti
↓
Ollama genera quiz JSON
↓
validazione struttura
↓
validazione distrattori
↓
riparazione automatica dei distrattori deboli
↓
nuova validazione struttura
↓
nuova validazione distrattori
↓
review sicura
↓
eventuale import controllato

## Script

- `scripts/rag_ripara_distrattori.py`

## Comando manuale

python3 scripts/rag_ripara_distrattori.py dist/generated/rag_quiz_generato.json --modello gemma3:4b --cicli 2

## Sicurezza

Il riparatore non modifica mai i database ufficiali dentro `data/`.

Lavora solo sul JSON temporaneo generato dal RAG.
Le domande devono comunque passare dalla review prima di qualsiasi import.
