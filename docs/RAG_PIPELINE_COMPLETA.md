# Pipeline completa RAG

Questa documentazione descrive il flusso completo e sicuro del sistema RAG.

## Obiettivo

Il progetto può partire da documenti reali e arrivare fino alla preparazione controllata di domande pronte per una futura importazione.

## Flusso completo

RAG
↓
recupero contesto
↓
generazione quiz JSON temporaneo
↓
validazione struttura
↓
review
↓
preparazione import delle sole domande approvate
↓
eventuale import manuale controllato
↓
motori qualità
↓
database ufficiale
↓
demo web e pacchetti

## Comando pipeline completa sicura

python3 scripts/rag_pipeline_completa_sicura.py "argomento" --categoria ai --livello intermedio --numero-domande 10

## Modalità con Ollama

python3 scripts/rag_pipeline_completa_sicura.py "argomento" --categoria ai --livello intermedio --numero-domande 5 --usa-ollama --modello gemma3:4b

## Import controllato delle domande approvate

Prima bisogna modificare manualmente il file:

review/rag/quiz_da_revisionare.json

e mettere a true questi controlli:

- fonte_rag_verificata
- domanda_chiara
- risposta_corretta_verificata
- tre_distrattori_forti
- spiegazione_didattica
- lingua_controllata
- approvata_per_database_ufficiale

Poi si prepara l'import:

python3 scripts/rag_prepara_import_approvati.py

Questo comando non scrive nei database ufficiali.

## Scrittura reale nel database

Solo dopo controllo manuale, si potrà usare:

python3 scripts/rag_prepara_import_approvati.py --scrivi-database --confermo-scrittura-data --target-file data/ai.json

## Regola fondamentale

Il RAG non deve mai sporcare automaticamente i database ufficiali.

La pipeline professionale corretta è:

genera
↓
valida
↓
revisiona
↓
approva
↓
importa con conferma
↓
controlla qualità
