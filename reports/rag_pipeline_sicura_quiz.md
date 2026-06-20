# Pipeline sicura RAG → Quiz → Review

## Stato

OK: pipeline completata.

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
- Report review: reports/rag_review_quiz.md
- File review locale: review/rag/quiz_da_revisionare.json

## Regola di sicurezza

La pipeline non modifica i database ufficiali dentro data/.
