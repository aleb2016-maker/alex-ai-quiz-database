# Retry generazione RAG

Questo blocco aggiunge un retry automatico alla generazione RAG.

## Problema

Durante un test reale, Ollama può generare un JSON formalmente presente ma vuoto o incompleto, per esempio una domanda senza campi.

## Soluzione

La pipeline ora usa `scripts/rag_genera_quiz_json_retry.py`.

Lo script:

- chiama il generatore RAG;
- valida subito il JSON generato;
- se il JSON non è valido, riprova;
- dopo 3 tentativi blocca la pipeline;
- non manda domande difettose alla review.

## Comando manuale

python3 scripts/rag_genera_quiz_json_retry.py "sicurezza informatica aziendale" --categoria informatica --livello intermedio --numero-domande 3 --usa-ollama --modello gemma3:4b

## Regola

Se il modello genera male, il sistema non accetta il risultato e non lo importa nei database ufficiali.
