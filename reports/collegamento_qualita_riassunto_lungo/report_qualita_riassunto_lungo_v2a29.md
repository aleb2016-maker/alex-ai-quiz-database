# Report qualita' riassunto lungo V2A29

## 1. Sintesi

Collegato solo il riassunto lungo ai controlli qualita' gia' esistenti e browser-compatibili.

La catena lunga resta invariata fino alla generazione grezza:

```text
testo reale -> RagLargeDocumentManagerV1 -> RagLargeDocumentProgressiveSummaryV2 -> sezioni lunghe grezze
```

Poi e' stato aggiunto un ponte leggero:

```text
sezioni lunghe grezze -> applicaQualitaRiassuntoLungoEsistenteV2A29 -> sezioni finali -> render
```

Il ponte non e' un nuovo motore: orchestra funzioni gia' presenti nel browser runtime.

Nessun commit eseguito.

## 2. Inventario motori qualita' esistenti

| Motore/funzione | File | Cosa controlla/corregge | Modifica testo? | Browser-compatible | Uso sul riassunto lungo |
|---|---|---:|---:|---:|---|
| `correggiSpaziPunteggiaturaV35G` | `demo-rag/universal-document-learning-engine.js` | Spazi prima di punteggiatura | Si | Si | Collegato |
| `normalizzaTesto` | `demo-rag/universal-document-learning-engine.js` | Spazi, righe, normalizzazione OCR base | Si | Si | Collegato |
| `RagLargeDocumentProgressiveSummaryV2.normalizeText` | `runtime/web/rag-large-document-progressive-summary-v2.js` | Normalizzazione testo del motore lungo | Si | Si | Collegato |
| `RagLargeDocumentProgressiveSummaryV2.dedupeSentences` | `runtime/web/rag-large-document-progressive-summary-v2.js` | Frasi duplicate/simili | Si | Si | Collegato |
| `RagLargeDocumentProgressiveSummaryV2.areSentencesTooSimilar` | `runtime/web/rag-large-document-progressive-summary-v2.js` | Similarita' residua tra frasi | Segnala/aiuta dedupe | Si | Collegato |
| `rag_revisore_qualita_testuale_v35g.py` | `scripts/` | Qualita' testuale V35G | Si su JSON/file | No, CLI Python | Non collegato direttamente; equivalente browser gia' presente usato |
| `rag_revisore_naturalezza_antikeyword_v35i.py` | `scripts/` | Naturalezza anti-keyword | Si su JSON/file | No, CLI Python | Inventariato, non collegato al browser |
| `rag_revisore_accordo_pronomi_v35j.py` | `scripts/` | Accordo, pronomi, frasi tagliate | Si su JSON/file | No, CLI Python | Inventariato, non collegato al browser |
| `rag_cleaner_finale_visibile_v35k.py` / `applica_v35k_reale.py` | `scripts/` | Cleaner finale testi visibili | Si su JSON/file | No, CLI Python | Inventariato, non collegato al browser |
| `rag_completatore_linguistico_probabile_v35n.py` | `scripts/` | Completamento linguistico probabile | Si su JSON/file | No, CLI Python | Inventariato, non collegato al browser |
| `rag_contesto_semantico_universale_v35o.py` | `scripts/` | Contesto semantico | Arricchisce metadati | No, CLI Python | Inventariato, non collegato al browser |
| `rag_bridge_motori_qualita_esistenti_v35b.py` | `scripts/` | Bridge qualita' quiz | Report/bridge test | No, CLI Python | Escluso: specifico quiz/test |
| `rag_motore_test_riutilizzabile_v35d.py` | `scripts/` | Test, opzioni, risposta corretta | Si su test | No, CLI Python | Escluso: specifico test |

## 3. Motori collegati

Collegati al riassunto lungo:

- `correggiSpaziPunteggiaturaV35G`
- `normalizzaTesto`
- `RagLargeDocumentProgressiveSummaryV2.normalizeText`
- `RagLargeDocumentProgressiveSummaryV2.dedupeSentences`
- `RagLargeDocumentProgressiveSummaryV2.areSentencesTooSimilar`
- fallback locale gia' esistente `deduplicaFrasiRiassuntoLungoV2A28`

Questi componenti sono gia' presenti e disponibili nella pagina reale.

## 4. Motori esclusi

Esclusi dal riassunto lungo:

- V35B / `rag_bridge_motori_qualita_esistenti_v35b.py`
- V35D / `rag_motore_test_riutilizzabile_v35d.py`

Motivo: sono specifici per quiz/test, opzioni, distrattori, risposta corretta e mappa opzioni. Il ponte V2A29 li dichiara come esclusi e il validatore verifica che non vengano chiamati.

## 5. Punto di inserimento

File modificato:

```text
demo-rag/universal-document-learning-engine.js
```

Punto:

```text
const progressive = await summarizer.createProgressiveSummary(...)
const sezioni = creaSezioniRiassuntoLungoV2A28(progressive)
const qualita = applicaQualitaRiassuntoLungoEsistenteV2A29(sezioni, testo, profilo)
renderizzaRiassuntoLungoV2A28(profilo, progressive, qualita.sezioni, qualita.report)
```

Quindi la qualita' agisce dopo il motore lungo e prima del rendering, come richiesto.

## 6. Catena finale riassunto lungo

```text
leggiTesto()
-> soglia lunga V2A28
-> RagLargeDocumentManagerV1
-> chunk/batch
-> RagLargeDocumentProgressiveSummaryV2.createProgressiveSummary
-> creaSezioniRiassuntoLungoV2A28
-> applicaQualitaRiassuntoLungoEsistenteV2A29
-> renderizzaRiassuntoLungoV2A28
```

Il report qualita' viene salvato anche in:

```text
window.__ragRiassuntoLungoQualitaV2A29
```

Nel render viene mostrato all'utente solo un messaggio discreto:

```text
Controllo qualità: grammatica, punteggiatura, ripetizioni e coerenza verificati.
```

## 7. Cosa resta invariato

Non sono stati modificati:

- `generaCardVisive()`
- `generaTest()`
- `generaDomandeStudio()`
- motore lungo V2A28 gia' collegato
- rimozione V2A19
- rimozione V2A24
- eliminazione V34A
- correzione fallback sicurezza V2A27

## 8. Validatore aggiunto

Creato:

```text
scripts/verifica_qualita_riassunto_lungo_v2a29.py
```

Controlla:

- manager e summarizer lunghi ancora caricati;
- ponte qualita' collegato dopo il motore lungo;
- uso di funzioni esistenti;
- V35G corregge senza bloccare;
- dedupe/similarita' funzionano su fixture ripetitiva;
- V2A19, V34A e V2A24 non caricati;
- card/test/domande studio non contaminati;
- V35B/V35D non applicati al riassunto;
- marker demo sicurezza assente nella pagina reale e nel motore universale.

## 9. Test eseguiti

`node --check demo-rag/universal-document-learning-engine.js`

Output: nessun errore.

`node --check runtime/web/rag-large-document-manager-v1.js`

Output: nessun errore.

`node --check runtime/web/rag-large-document-progressive-summary-v2.js`

Output: nessun errore.

`python3 scripts/verifica_qualita_riassunto_lungo_v2a29.py`

```text
QUALITA RIASSUNTO LUNGO V2A29: OK
- riassunto lungo ancora su manager + progressive summary
- ponte qualita' V2A29 collegato dopo il motore lungo e prima del render
- V35G corregge senza bloccare
- dedupe/coerenza usano funzioni esistenti del summarizer
- motori quiz/test esclusi dal riassunto
```

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

## 10. Cosa provare nel browser

Aprire:

```text
demo-rag/test-documenti-universale.html
```

Provare:

- documento breve: il riassunto deve restare sulla catena compatta;
- documento lungo: il riassunto deve mostrare chunk/batch/parziali e il messaggio discreto di controllo qualita';
- inserire volutamente spazi prima della punteggiatura in parti del documento: il riassunto finale non deve mostrare `parola .`;
- testo lungo ripetitivo: il riassunto finale deve ridurre duplicati e ripetizioni;
- card/test/domande studio: devono continuare a funzionare come prima.

## 11. Commit

Nessun commit eseguito.

HEAD resta:

```text
4877388 Merge V2A16 blocco motori obbligatori RAG
```
