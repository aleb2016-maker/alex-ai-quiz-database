# Pipeline RAG → Quiz JSON

Questo blocco collega il motore RAG alla generazione di quiz JSON temporanei.

## Obiettivo

Permettere al progetto di partire da documenti caricati in:

rag/documenti/

e preparare un quiz JSON basato sui contenuti recuperati dal RAG.

## Flusso

1. Inserisci documenti in rag/documenti/
2. Ricrea l'indice RAG
3. Genera il prompt e il contenitore JSON temporaneo
4. Valida la struttura del JSON
5. In futuro: passa il JSON ai motori qualità
6. In futuro: consolida nel database ufficiale
7. In futuro: rigenera demo e pacchetti

## Comandi base

Ricrea indice:

python3 scripts/rag_build_index.py

Genera quiz JSON temporaneo senza modello AI:

python3 scripts/rag_genera_quiz_json.py "sicurezza informatica" --categoria informatica --livello intermedio --numero-domande 10

Valida il JSON temporaneo:

python3 scripts/rag_valida_quiz_json.py dist/generated/rag_quiz_generato.json

## Uso con Ollama locale

Se Ollama è attivo, puoi provare:

python3 scripts/rag_genera_quiz_json.py "sicurezza informatica" --categoria informatica --livello intermedio --numero-domande 5 --usa-ollama --modello gemma3:4b

Il file generato rimane temporaneo e non entra automaticamente nel database ufficiale.

## Perché è importante

Questo rende il progetto più professionale perché crea un flusso controllato:

documenti reali
↓
RAG
↓
contesto recuperato
↓
quiz JSON temporaneo
↓
validazione
↓
motori qualità
↓
database finale
↓
demo web / pacchetto Android
