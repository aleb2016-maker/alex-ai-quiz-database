# Import controllato domande RAG approvate

- File review sorgente: `review/rag/quiz_da_revisionare.json`
- File preparazione import: `review/rag/domande_approvate_pronte_per_import.json`
- Domande approvate trovate: 0
- Stato: OK
- Scrittura database ufficiale: no

## Nota

Non ci sono ancora domande approvate. Questo è normale se la pipeline è stata eseguita in modalità sicura.

## Regola di sicurezza

Questo script prepara l'importazione ma non scrive nei database ufficiali, salvo uso esplicito di `--scrivi-database --confermo-scrittura-data`.
