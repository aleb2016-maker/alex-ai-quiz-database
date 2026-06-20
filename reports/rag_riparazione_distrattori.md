# Riparazione automatica distrattori RAG

- File input: `dist/generated/rag_quiz_generato.json`
- File output: `dist/generated/rag_quiz_generato.json`
- Avvisi iniziali: 11
- Avvisi finali: 10
- Stato: MIGLIORATO

## Metodo

Il riparatore usa regole guidate per tema.
Non si limita a chiedere al modello di correggere: riscrive direttamente i distrattori usando schemi vicini alla risposta corretta.

## Sicurezza

Il riparatore lavora solo sul JSON temporaneo RAG.
Non modifica i database ufficiali dentro `data/`.
