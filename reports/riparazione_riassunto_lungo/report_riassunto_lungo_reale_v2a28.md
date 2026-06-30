# Report riassunto lungo reale V2A28

## 1. Sintesi

Corretto solo il problema del riassunto troppo corto sui documenti lunghi.

Il pulsante `Genera riassunto` ora resta sulla catena compatta per testi brevi, ma sopra soglia usa i motori documenti lunghi gia' presenti:

- `runtime/web/rag-large-document-manager-v1.js`
- `runtime/web/rag-large-document-progressive-summary-v2.js`

Non sono stati ripristinati V2A19, V2A24 o V34A. Non sono stati creati nuovi motori o nuove demo. Nessun commit eseguito.

Backup creati:

- `reports/riparazione_riassunto_lungo/status_prima_riassunto_lungo.txt`
- `reports/riparazione_riassunto_lungo/diff_prima_riassunto_lungo.patch`
- `reports/riparazione_riassunto_lungo/diff_cached_prima_riassunto_lungo.patch`

## 2. Perche' prima uscivano solo 5 righe

Dopo il ripristino generatori reali, `generaRiassunto()` era tornato alla catena compatta:

```text
generaRiassunto -> creaParagrafiRiassunto
```

Questa catena e' adatta a testi brevi/medi, ma non lavora per chunk e batch. Su documenti molto lunghi seleziona poche sezioni/paragrafi e tende a mostrare un output breve rispetto alla dimensione del documento.

In piu', nella pagina reale `rag-concept-document-engine-v46.js` intercettava `btnRiassunto` in capture tramite `replaceButton("btnRiassunto", renderSummary)`, quindi il click poteva non arrivare al motore universale. E' stata rimossa solo quell'intercettazione del riassunto; card, test e domande studio restano gestiti come prima.

## 3. Motori lunghi esistenti trovati

Motori browser-compatible:

- `runtime/web/rag-large-document-manager-v1.js`
  - UMD/browser + Node.
  - Espone `window.RagLargeDocumentManagerV1`.
  - Divide testo in pagine logiche, chunk e batch.
- `runtime/web/rag-large-document-progressive-summary-v2.js`
  - UMD/browser + Node.
  - Espone `window.RagLargeDocumentProgressiveSummaryV2`.
  - Crea riassunti parziali per batch e sintesi progressiva.

Pagine/demo gia' esistenti che li usano:

- `demo-rag/rag-app-aziendale-v2a9-output.html`
- `demo-rag/rag-app-aziendale-v2a10-output-dinamici.html`
- `demo-rag/test-rag-documenti-lunghi-v1.html`
- `demo-rag/test-rag-documenti-lunghi-v2.html`

Validator e prove gia' presenti:

- `scripts/verifica_rag_documenti_lunghi_v2a4_espansione.py`
- `scripts/verifica_rag_documenti_lunghi_v2a6_500_pagine_stabile.py`
- `scripts/verifica_rag_documenti_lunghi_v2a10_output_dinamici.py`
- `scripts/verifica_rag_documenti_lunghi_v2a11_ux_finale.py`

Stabilita' documentata:

- `reports/rag_documenti_lunghi_v2a10_output_dinamici.md`: stabilita' confermata V2A.6 fino a 500 pagine.
- `reports/rag_documenti_lunghi_v2a6_500_stabile_riepilogo.json`: prova 400/500 pagine con 800/1000 chunk, 100/125 batch, 100/125 parziali, esito `ok: true`.

Il migliore da collegare al pulsante riassunto e' la coppia runtime/web V1+V2, perche' e' gia' browser-compatible e gia' validata su documenti lunghi.

## 4. Collegamento al solo riassunto

Modifiche applicate:

- `demo-rag/test-documenti-universale.html`
  - caricati i due runtime esistenti prima di `universal-document-learning-engine.js`:
    - `../runtime/web/rag-large-document-manager-v1.js`
    - `../runtime/web/rag-large-document-progressive-summary-v2.js`
- `demo-rag/rag-concept-document-engine-v46.js`
  - rimossa solo l'intercettazione `replaceButton("btnRiassunto", renderSummary)`.
  - lasciate invariate le intercettazioni di card, domande studio e test.
- `demo-rag/universal-document-learning-engine.js`
  - `generaRiassunto()` ora sceglie tra compatto e lungo.
  - aggiunti helper V2A28 solo per riassunto lungo.

Catena breve:

```text
generaRiassunto -> creaParagrafiRiassunto
```

Catena lunga:

```text
generaRiassunto
-> deveUsareRiassuntoLungoV2A28
-> RagLargeDocumentManagerV1
-> chunk/batch
-> RagLargeDocumentProgressiveSummaryV2.createProgressiveSummary
-> sezioni lunghe da riassunti parziali
-> rendering riassunto lungo
```

## 5. Soglia usata

Il riassunto lungo parte quando almeno una condizione e' vera:

- testo >= 10.000 caratteri;
- almeno 80 frasi significative;
- almeno 20 paragrafi significativi.

Sotto soglia resta la catena compatta esistente.

## 6. Cosa resta invariato

Non sono stati modificati i comportamenti di:

- `generaCardVisive()`;
- `generaTest()`;
- `generaDomandeStudio()`.

Restano invariati anche:

- V34A eliminato e non caricato;
- V2A19 non caricato;
- V2A24 non ripristinato;
- correzione fallback sicurezza V2A27;
- V35G come correttore spazi prima della punteggiatura.

## 7. Validatore aggiunto

Creato:

```text
scripts/verifica_riassunto_lungo_reale_v2a28.py
```

Controlla:

- pagina reale senza V2A19/V34A;
- runtime lunghi caricati;
- `btnRiassunto` non intercettato da V46;
- `generaRiassunto()` usa soglia breve/lungo;
- `creaParagrafiRiassunto` resta fallback per testi brevi;
- card/test/domande studio non contengono V2A28/RagLargeDocument;
- fixture lunga da 120 pagine produce chunk, batch, parziali e molte righe;
- V35G continua a correggere punteggiatura.

## 8. Test eseguiti

`node --check demo-rag/universal-document-learning-engine.js`

Output: nessun errore.

`python3 scripts/verifica_riassunto_lungo_reale_v2a28.py`

```text
RIASSUNTO LUNGO V2A28: OK
- pagina reale senza V2A19/V34A
- btnRiassunto libero dall'intercettazione V46
- generaRiassunto usa soglia breve/lungo e motore progressivo esistente
- card/test/domande studio senza V2A28
- fixture lunga produce chunk, batch e molte righe di sintesi
```

`python3 scripts/verifica_fallback_sicurezza_eliminato_v2a27.py`

```text
FALLBACK SICUREZZA V2A27: OK
- pagina reale senza marker demo sicurezza
- script runtime caricati senza fallback demo utilizzabile
- input vuoto produce errore/nessun contenuto, non fallback
- V34A e V2A19 restano non caricati
```

`python3 scripts/verifica_ripristino_generatori_reali_rag.py`

```text
RIPRISTINO GENERATORI REALI RAG: OK
- pagine reali senza V2A19/V34A
- catena riassunto/card/test/domande tornata ai generatori ufficiali
- V35G corregge gli spazi prima della punteggiatura senza bloccare
- V34A resta eliminato
```

`python3 scripts/verifica_file_vecchio_riassunto_v34a_eliminato_v2a17.py`

```text
OK V2A.17 FILE VECCHIO:
- rag-quality-summary-cards-v34a.js eliminato
- nessuna pagina demo-rag lo carica
- nessun riferimento al file vecchio resta negli HTML
- la pagina universale non carica script con il vecchio riassunto demo
```

## 9. Cosa provare nel browser

Aprire `demo-rag/test-documenti-universale.html`.

Prove consigliate:

- incollare un testo breve e premere `Genera riassunto`: deve restare il riassunto compatto esistente;
- caricare/incollare un documento lungo, circa 120 pagine o comunque sopra 10.000 caratteri;
- premere `Genera riassunto`;
- verificare che l'output mostri:
  - conteggio chunk/batch/parziali;
  - sintesi generale;
  - sezioni progressive;
  - punti chiave ricorrenti;
  - dettagli importanti per batch;
  - conclusione;
- verificare che non sia piu' un output da circa 5 righe.

## 10. Commit

Nessun commit eseguito.

HEAD resta:

```text
4877388 Merge V2A16 blocco motori obbligatori RAG
```
