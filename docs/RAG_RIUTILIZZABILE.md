# Motore RAG riutilizzabile

Questo progetto include un primo motore RAG locale.

## A cosa serve

Il RAG permette di usare documenti caricati dall'utente come base per creare:

- quiz
- test
- mini-corsi
- slide
- percorsi formativi
- demo aziendali
- contenuti per app web o Android

## Flusso base

1. Inserisci documenti in:

rag/documenti/

2. Crea l'indice:

python3 scripts/rag_build_index.py

3. Cerca informazioni nei documenti:

python3 scripts/rag_test_query.py "crea un quiz sulla fotosintesi"

4. Crea un prompt quiz basato sui documenti:

python3 scripts/rag_crea_prompt_quiz.py "fotosintesi"

5. Crea un prompt mini-corso basato sui documenti:

python3 scripts/rag_crea_prompt_minicorso.py "fotosintesi"

## Versione attuale

La versione iniziale supporta:

- TXT
- Markdown
- JSON

## Evoluzioni previste

- supporto PDF
- supporto DOCX
- supporto slide
- collegamento diretto al generatore quiz
- collegamento diretto al mini-corso interattivo
- scelta stile grafico
- esportazione pacchetto web
- esportazione pacchetto Android
