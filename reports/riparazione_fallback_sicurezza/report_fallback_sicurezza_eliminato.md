# Report eliminazione fallback sicurezza informatica

## 1. Sintesi

Eliminata la contaminazione demo/fallback "sicurezza informatica aziendale" dalla pagina RAG reale `demo-rag/test-documenti-universale.html`.

Non sono stati creati nuovi motori, non sono stati cambiati i generatori principali, non sono state create demo, non sono stati ripristinati V2A19 o V34A e non e' stato fatto commit.

Backup creati:

- `reports/riparazione_fallback_sicurezza/status_prima_fallback.txt`
- `reports/riparazione_fallback_sicurezza/diff_prima_fallback.patch`
- `reports/riparazione_fallback_sicurezza/diff_cached_prima_fallback.patch`

## 2. Dove e' stato trovato il fallback

Risultati della ricerca esatta richiesta:

```text
rg -n "Sicurezza informatica aziendale|E-mail sospette|Password manager|Aggiornamenti controllati|Rischi e controlli|La sicurezza informatica comprende pratiche|documento_rag_sicurezza_informatica_aziendale" .
```

### Runtime reale o caricato dalla pagina

- `demo-rag/rag-concept-document-engine-v46.js:236`: titolo hardcoded `Sicurezza informatica aziendale`.
- `demo-rag/rag-concept-document-engine-v46.js:238`: frase hardcoded `La sicurezza informatica comprende pratiche...`.
- `demo-rag/rag-concept-document-engine-v46.js:246`: titolo hardcoded `E-mail sospette`.
- `demo-rag/rag-concept-document-engine-v46.js:256`: titolo hardcoded `Password manager`.
- `demo-rag/rag-concept-document-engine-v46.js:266`: titolo hardcoded `Aggiornamenti controllati`.
- `demo-rag/rag-concept-document-engine-v46.js:276`: titolo hardcoded `Rischi e controlli`.
- `demo-rag/universal-document-learning-engine.js:448`: titolo generico `Rischi e controlli`.
- `demo-rag/index.html:22`: placeholder `Esempio: Sicurezza informatica aziendale`.

Il contaminante operativo era `demo-rag/rag-concept-document-engine-v46.js`, perche' e' caricato direttamente da `test-documenti-universale.html` e intercetta i pulsanti `btnRiassunto`, `btnCard`, `btnStudio`, `btnTest`. Quando trovava parole generiche nel testo, generava output con frasi/titoli demo hardcoded.

`universal-document-learning-engine.js` poteva generare almeno il marker `Rischi e controlli` come titolo di sezione anche se la frase non era nel documento caricato.

`index.html` conteneva solo un placeholder, quindi non era input usato come generatore; e' stato comunque neutralizzato.

### Documentazione, report o esempi non caricati dalla pagina reale

- `README.md`
- `docs/PIPELINE_MATERIALE_FORMATIVO.md`
- `docs/RAG_ADAPTER_QUIZ_UFFICIALE_V43.md`
- `reports/rag_pipeline_unica_ufficiale.md`
- `reports/rag_prompt_generazione_quiz_json.md`
- `reports/pipeline_formazione_completa.md`
- `reports/riparazione_generatori_rag/*`
- `reports/riparazione_fallback_sicurezza/*`
- `rag/documenti/documento_rag_sicurezza_informatica_aziendale.md`
- `rag/indice_rag.json`

Questi file non sono caricati da `demo-rag/test-documenti-universale.html`, quindi non contaminano la pagina reale.

### File generati, dist, cache, backup o script non runtime reale

- `dist/formazione/*`
- `dist/pacchetto-rag-riutilizzabile/*`
- `backups/universal-document-learning-engine.*.js`
- script CLI/validator sotto `scripts/` che citano il documento test.

Questi file non sono nella catena runtime della pagina reale. Il nuovo validatore V2A27 tollera marker in questi percorsi, ma fallisce se compaiono negli HTML/JS caricati dalla pagina reale.

## 3. Catena reale controllata

Script locali caricati da `demo-rag/test-documenti-universale.html`:

- `demo-rag/rag-input-reale-guard.js`
- `demo-rag/layout-rigido-rag.js`
- `demo-rag/layout-rigido-generazione-subito.js`
- `demo-rag/buttons-full-row.js`
- `demo-rag/rag-action-icons-v46.js`
- `demo-rag/rag-concept-document-engine-v46.js`
- `demo-rag/pdf-export-browser-v6.js`
- `demo-rag/universal-document-learning-engine.js`

`leggiTesto()` in `universal-document-learning-engine.js` legge solo `documentoInput.value` e, se non esiste input, ritorna stringa vuota. Non contiene fallback demo.

La guardia `rag-input-reale-guard.js` blocca click di generazione quando non trova testo visibile o file selezionato.

Non sono stati trovati recuperi da `localStorage` o `sessionStorage` nella catena reale caricata da `test-documenti-universale.html`. Le occorrenze di `localStorage` sono fuori da questa pagina reale.

## 4. File modificati

- `demo-rag/rag-concept-document-engine-v46.js`
- `demo-rag/universal-document-learning-engine.js`
- `demo-rag/index.html`
- `scripts/verifica_fallback_sicurezza_eliminato_v2a27.py`
- `reports/riparazione_fallback_sicurezza/report_fallback_sicurezza_eliminato.md`

Nota: `demo-rag/test-documenti-universale.html` era gia' modificato dal ripristino precedente e resta senza V2A19/V34A. In questa fase non e' stato necessario aggiungere nuovi script o demo.

## 5. Come e' stato impedito il fallback

In `rag-concept-document-engine-v46.js`:

- rimossi i titoli/frasi demo hardcoded dalla generazione V46;
- aggiunte funzioni leggere `sentences()` ed `evidence()` per prendere la frase direttamente dal testo caricato;
- sostituiti i titoli demo con titoli generici non contaminanti:
  - `Protezione dati e sistemi`
  - `Segnalazione email`
  - `Gestione credenziali`
  - `Gestione aggiornamenti`
  - `Prevenzione rischi`
- cambiato il profilo da `sicurezza informatica aziendale` a `sicurezza digitale`.

In `universal-document-learning-engine.js`:

- rinominato il titolo generico `Rischi e controlli` in `Rischi operativi`.

In `index.html`:

- cambiato il placeholder da `Esempio: Sicurezza informatica aziendale` a `Esempio: Documento aziendale`.

## 6. Comportamento senza testo caricato

La pagina non deve piu' produrre un documento demo.

Con input vuoto:

- `rag-input-reale-guard.js` blocca la generazione e mostra errore;
- `universal-document-learning-engine.js` mostra `Documento mancante` con testo `Incolla o carica prima un documento.`;
- `rag-concept-document-engine-v46.js` mostra `Documento insufficiente` e chiede di caricare contenuti reali.

## 7. Test eseguiti

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

`node --check demo-rag/universal-document-learning-engine.js`

Output: nessun errore.

Controllo aggiuntivo:

`node --check demo-rag/rag-concept-document-engine-v46.js`

Output: nessun errore.

## 8. Cosa provare nel browser

Aprire `demo-rag/test-documenti-universale.html` e verificare:

- premendo i pulsanti senza file/testo compare errore chiaro, non contenuto demo;
- caricando un documento reale non informatico non compaiono i marker demo;
- caricando un documento che parla di rischi/password/email, le card V46 usano frasi del documento caricato e non le frasi hardcoded della demo;
- V2A19 e V34A restano non caricati.

## 9. Commit

Nessun commit eseguito.

HEAD resta:

```text
4877388 Merge V2A16 blocco motori obbligatori RAG
```
