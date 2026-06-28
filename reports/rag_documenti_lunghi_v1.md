# Report RAG documenti lunghi V1

## Cosa e stato creato

- Manager isolato: runtime/web/rag-large-document-manager-v1.js
- Pagina test isolata: demo-rag/test-rag-documenti-lunghi-v1.html
- Generatore documento: scripts/crea_documento_lungo_test_rag_v1.py
- Validatori: scripts/verifica_rag_documenti_lunghi_v1.py e scripts/test_rag_documento_lungo_generato_v1.py
- Documento MD e TXT in rag/documenti con 120 pagine logiche.

## Cosa e stato testato

- Riconoscimento marker pagina TXT/MD.
- Selezioni: tutto, 1-10, 1,5,9, 20-30,40.
- Chunk progressivi con metadati pagina e indice globale.
- Batch con limiti su pagine, chunk e caratteri.
- Isolamento dalla demo ufficiale e dagli export.

## Metriche documento generato

- Caratteri totali: 644652
- Pagine logiche: 120
- Chunk prodotti: 240
- Batch prodotti: 30

## Limiti iniziali impostati

- Max caratteri per chunk: 4000
- Overlap chunk: 400
- Max pagine per batch: 5
- Max chunk per batch: 8
- Max caratteri per batch: 28000

## Cosa NON e stato toccato

- Non e stata collegata la demo ufficiale.
- Non sono stati modificati i pulsanti esistenti.
- Non e stato modificato PDF export.
- Non sono stati modificati TXT/HTML/JSON export.
- Non sono state modificate grafica o card ufficiali.
