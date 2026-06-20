# Pipeline completa sicura RAG

## Stato

OK: pipeline completa eseguita.

## Flusso coperto

RAG
↓
quiz JSON temporaneo
↓
validazione
↓
review
↓
preparazione import domande approvate
↓
eventuale controllo qualità completo

## Argomento

motore RAG riutilizzabile

## Categoria

ai

## Livello

intermedio

## Numero domande richieste

3

## Modalità generazione

Modalità sicura senza modello AI

## Output principali

- Prompt generazione: reports/rag_prompt_generazione_quiz_json.md
- JSON temporaneo locale: dist/generated/rag_quiz_generato.json
- Report validazione: reports/rag_validazione_quiz_json.md
- Review locale: review/rag/quiz_da_revisionare.json
- Preparazione import locale: review/rag/domande_approvate_pronte_per_import.json
- Report import approvati: reports/rag_import_approvati.md

## Sicurezza

La pipeline non modifica i file dentro data/.
Per scrivere davvero nei database ufficiali serve un comando esplicito separato con conferma.
