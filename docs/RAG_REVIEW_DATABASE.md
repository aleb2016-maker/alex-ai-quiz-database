# Filtro review per quiz generati da RAG

Questo blocco aggiunge un passaggio di sicurezza tra il quiz generato dal RAG e i database ufficiali.

## Obiettivo

Evitare che domande generate automaticamente entrino subito nei file ufficiali dentro data/.

Prima devono passare da:

1. generazione temporanea
2. validazione struttura
3. filtro review
4. controllo manuale
5. eventuale importazione controllata futura

## Cartella review

Le domande da controllare vengono preparate in:

review/rag/quiz_da_revisionare.json

Questo file è locale e non viene salvato su GitHub.

## Comando review

python3 scripts/rag_prepara_review_quiz.py --input dist/generated/rag_quiz_generato.json

## Pipeline completa sicura

python3 scripts/rag_pipeline_sicura_quiz.py "argomento" --categoria ai --livello intermedio --numero-domande 10

## Uso con Ollama

python3 scripts/rag_pipeline_sicura_quiz.py "argomento" --categoria ai --livello intermedio --numero-domande 5 --usa-ollama --modello gemma3:4b

## Regola fondamentale

Il filtro review non modifica mai i database ufficiali.

Il flusso corretto è:

RAG
↓
quiz JSON temporaneo
↓
validazione
↓
review
↓
approvazione
↓
importazione controllata futura
↓
database ufficiale
