# Validatore distrattori forti RAG

Questo blocco aggiunge un controllo automatico sui distrattori generati dal RAG.

## Perché serve

Il prompt può chiedere distrattori forti, ma un modello locale piccolo può comunque generare opzioni troppo facili o troppo lontane dalla risposta corretta.

Il validatore controlla automaticamente:

- distrattori troppo lontani dalla risposta corretta
- opzioni generiche o fuori tema
- formule deboli
- opzioni troppo scollegate dalla domanda
- lunghezze molto sbilanciate

## Comando

python3 scripts/rag_valida_distrattori_forti.py dist/generated/rag_quiz_generato.json

## Report

reports/rag_validazione_distrattori_forti.md

## Integrazione

La pipeline sicura RAG ora esegue anche questo controllo prima di preparare la review.

Flusso:

RAG
↓
quiz JSON temporaneo
↓
validazione struttura
↓
validazione distrattori forti
↓
review
↓
eventuale approvazione manuale
↓
import controllato futuro
