# RAG Blocchi 2-10 V1

Questo pacchetto aggiunge una pipeline intelligente separata, senza rompere la pagina principale.

## Cosa contiene

- `demo-rag/rag-input-reale-guard.js`  
  Versione corretta BLOCCO 1: pulisce il riquadro iniziale e blocca solo generazione vuota. Non vieta nessun contenuto.

- `demo-rag/rag-document-input-unico-v1.js`  
  BLOCCO 2: formato interno unico per TXT, MD, PDF dove possibile, OCR/testo manuale, metadati, origine, stato lettura, controlli documento lungo/tabelle/OCR.

- `demo-rag/rag-text-cleaner-ocr-v1.js`  
  BLOCCO 3: pulizia righe spezzate, spazi doppi, caratteri strani, rumore OCR, tabelle semplici, testo corto/corrotto.

- `demo-rag/rag-knowledge-extractors-v1.js`  
  BLOCCHI 4-7: estrazione concetti, definizioni, esempi, fatti, relazioni e base conoscenza JSON.

- `demo-rag/rag-didactic-planner-v1.js`  
  BLOCCO 8: planner didattico per card, riassunto, domande studio, test, distrattori, stile grafico e PDF.

- `demo-rag/rag-knowledge-linked-generator-v1.js`  
  BLOCCO 9: generatore collegato alla conoscenza: card dai concetti, test dai fatti, domande dalle relazioni, riassunto dagli argomenti.

- `demo-rag/rag-general-validator-v1.js`  
  BLOCCO 10: validatore generale su duplicati, prove nel documento, risposta corretta nelle opzioni, fiducia e qualità minima.

- `demo-rag/rag-smart-pipeline-v1.js`  
  Orchestratore dei blocchi 2-10.

- `demo-rag/test-rag-pipeline-intelligente-v1.html`  
  Pagina di test separata. Non modifica la pagina universale.

- `scripts/verifica_rag_blocchi_2_10_v1.py`  
  Verifica file e assenza di vecchie logiche censorie.

## Installazione rapida

Dalla cartella del progetto:

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
unzip -o ~/Downloads/rag_blocchi_2_10_v1.zip
python3 scripts/verifica_rag_blocchi_2_10_v1.py
python3 -m http.server 8000
```

Apri:

```text
http://localhost:8000/demo-rag/test-rag-pipeline-intelligente-v1.html
```

Refresh duro:

```text
Cmd + Shift + R
```

## Nota importante

Questa V1 non censura parole o contenuti. L'utente può caricare qualunque documento. Il controllo serve solo a evitare generazione vuota e a validare che gli output abbiano prove nel testo.

La pagina principale `test-documenti-universale.html` non viene collegata automaticamente ai nuovi motori. Prima si testa questa pagina separata; poi, quando è approvata, si collega ai quattro pulsanti ufficiali.
