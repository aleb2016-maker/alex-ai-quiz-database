# Report diagnosi rottura generatori RAG

## 1. Sintesi breve

La rottura principale non risulta introdotta da un commit gia' registrato: e' nel working tree corrente, dopo `HEAD` (`4877388 Merge V2A16 blocco motori obbligatori RAG`).

Nel working tree sono stati rimossi i collegamenti a `demo-rag/rag-quality-summary-cards-v34a.js` e introdotto/caricato `demo-rag/rag-motori-intelligenti-browser-v2a19.js`. Inoltre `demo-rag/universal-document-learning-engine.js` e' stato modificato pesantemente con blocchi V2A.17, V2A.18, V2A.19, V2A.20, V2A.21 e V2A.22.

Conclusione diagnostica: si', i generatori originali sono stati scavalcati nella pagina universale. La catena attuale passa da wrapper e binding forzati a una pipeline browser-only V2A19. Il riassunto attuale e' estrattivo: seleziona frasi originali pesate e le concatena. Non fonde davvero concetti. Test e domande studio funzionano perche' la pipeline produce array semplici da keyword, ma per questo le domande studio assomigliano troppo a quiz/domande keyword-based.

## 2. File modificati rilevanti

Da `git status --short`:

```text
 M demo-rag/index.html
D  demo-rag/rag-quality-summary-cards-v34a.js
 M demo-rag/test-documenti-universale.html
 M demo-rag/universal-document-learning-engine.js
 M scripts/verifica_rag_documenti_lunghi_v1.py
D  scripts/verifica_rag_summary_cards_v34a.py
?? demo-rag/rag-motori-intelligenti-browser-v2a19.js
?? demo-rag/test-documenti-universale-pulito-v2a24.html
?? scripts/verifica_binding_forzato_pulsanti_v2a21.py
?? scripts/verifica_blocco_riassunto_demo_v2a17.py
?? scripts/verifica_collegamenti_effettivi_motori_v35_v2a18.py
?? scripts/verifica_file_vecchio_riassunto_v34a_eliminato_v2a17.py
?? scripts/verifica_fix_v35g_riassunto_card_v2a25b.py
?? scripts/verifica_generatori_non_bloccanti_v2a20.py
?? scripts/verifica_lettura_testo_non_bloccante_v2a22.py
?? scripts/verifica_motori_browser_v2a19.py
?? scripts/verifica_motori_linguistici_universali_v2a17.py
?? scripts/verifica_riassunto_reale_lungo_v2a17.py
```

Da `git diff --stat`:

```text
demo-rag/index.html                            |    2 +-
demo-rag/test-documenti-universale.html        |    4 +-
demo-rag/universal-document-learning-engine.js | 1567 ++++++++++++++++++++++--
scripts/verifica_rag_documenti_lunghi_v1.py    |    3 +-
4 files changed, 1445 insertions(+), 131 deletions(-)
```

Da `git diff --cached --stat`:

```text
demo-rag/rag-quality-summary-cards-v34a.js | 948 -----------------------------
scripts/verifica_rag_summary_cards_v34a.py |  55 --
2 files changed, 1003 deletions(-)
```

Modifiche piu' rilevanti:

- `demo-rag/test-documenti-universale.html`: rimosso `<script src="rag-quality-summary-cards-v34a.js"></script>`; aggiunto `rag-motori-intelligenti-browser-v2a19.js?v=v2a22-lettura-differita` prima di `universal-document-learning-engine.js?v=v2a22-lettura-differita`.
- `demo-rag/index.html`: rimosso `rag-quality-summary-cards-v34a.js`; aggiunto `rag-motori-intelligenti-browser-v2a19.js`.
- `demo-rag/rag-quality-summary-cards-v34a.js`: cancellato/staged delete. Era dichiarato come miglioratore solo per riassunto e card.
- `demo-rag/rag-motori-intelligenti-browser-v2a19.js`: nuovo file non tracciato. Contiene generatori browser-only, renderer, controllo V35G e fix V2A.25B.
- `demo-rag/test-documenti-universale-pulito-v2a24.html`: nuova pagina pulita non tracciata. Usa direttamente `window.eseguiPipelineMotoriBrowserV2A19`.
- `demo-rag/universal-document-learning-engine.js`: diff enorme. Inserisce wrapper non bloccanti V2A20, lettura differita V2A22, binding forzato V2A21, ponte V2A18 verso V2A19, blocchi V2A17.

Cache-buster/versioni osservate:

- `v2a22-lettura-differita` nella pagina universale.
- `v2a25b-fix-v35g-riassunto-card` nella pagina pulita V2A24.
- Blocchi e script citano V2A17, V2A18, V2A19, V2A20, V2A21, V2A22, V2A24, V2A25B. Non ho trovato blocchi V2A23 o V2A26 nei file principali controllati.

## 3. Generator chain attuale

Pagina universale `demo-rag/test-documenti-universale.html`:

1. Carica `rag-motori-intelligenti-browser-v2a19.js`.
2. Carica `universal-document-learning-engine.js`.
3. `universal-document-learning-engine.js` collega i pulsanti in `avvia()`:
   - `btnRiassunto` -> `generaRiassunto`
   - `btnCard` -> `generaCardVisive`
   - `btnTest` -> `generaTest`
   - `btnStudio` -> `generaDomandeStudio`
4. In fondo attiva anche `attivaBindingForzatoPulsantiV2A21()`, che intercetta i click in capture, usa `stopImmediatePropagation`, rimuove `onclick` vecchi e forza:
   - `riassunto` -> `generaRiassunto()`
   - `card` -> `generaCardVisive()`
   - `test` -> `generaTest()`
   - `domande` -> `generaDomandeStudio()`
5. Le funzioni attuali chiamano `eseguiMotoriIntelligentiUniversaliV35V2A18(azione, { testo })`.
6. In browser, `eseguiMotoriIntelligentiUniversaliV35V2A18` richiede `window.eseguiPipelineMotoriBrowserV2A19` e delega a quella pipeline.
7. La pipeline V2A19 genera output con:
   - riassunto: `creaRiassuntoReale(testoOriginale, contesto)`
   - card: `creaCardBrowser(testoOriginale, contesto)`
   - test: `creaTestBrowser(testoOriginale, contesto)`
   - domande studio: `creaDomandeStudioBrowser(testoOriginale, contesto)`
8. Il rendering finale passa da `window.mostraOutputMotoriBrowserV2A19(azione, report)` oppure dalla pagina pulita V2A24 con renderer propri.

Pagina pulita `demo-rag/test-documenti-universale-pulito-v2a24.html`:

1. Carica solo `rag-motori-intelligenti-browser-v2a19.js?v=v2a25b-fix-v35g-riassunto-card`.
2. Al click chiama direttamente `window.eseguiPipelineMotoriBrowserV2A19(azione, { testo })`.
3. Applica `window.correggiReportV35GRiassuntoCardV2A25B(report, azione)` se presente.
4. Se `report.ok !== true`, blocca con `Generazione non completata: [...]`.

## 4. Generator chain precedente/probabile buona

Punto probabile prima della rottura: `HEAD` / commit `4877388` dopo merge V2A16, oppure direttamente `8689ed5 Blocca pulsanti RAG sui motori obbligatori V2A16`.

Nel `HEAD` tracciato, la pagina universale caricava:

```html
<script src="rag-quality-summary-cards-v34a.js"></script>
<script src="./universal-document-learning-engine.js?v=export-fix-280626"></script>
```

Nel `HEAD`, `generaRiassunto()` in `universal-document-learning-engine.js` faceva:

- `verificaMotoriObbligatoriV2A16("riassunto")`
- `leggiTesto()`
- `riconosciTema(testo)`
- `creaParagrafiRiassunto(testo, profilo)`
- render di paragrafi con titolo e testo.

`creaParagrafiRiassunto` usava:

- `frasiRiassuntoEsteso(testo)`
- `parolePerSezioneRiassunto(profilo, sezione)`
- `prendiFrasi(...)` e `prendiExtra(...)`
- output per sezioni/profilo.

Nel `HEAD`, `generaCardVisive()` usava `creaCards(testo)` e renderizzava card con `card.descrizione`, `card.originale`, `disegnoSvg(card)`.

Nel `HEAD`, `generaTest()` usava `creaQuiz()`, che a sua volta usava `creaCards(testo)` e `creaDistrattoriForti(card, cards)`.

Nel `HEAD`, `generaDomandeStudio()` usava `creaCards(testo)` e produceva domande aperte con:

- `card.domandaStudio`
- `card.descrizione` come risposta/study answer
- riferimento al testo originale.

`rag-quality-summary-cards-v34a.js`, oggi cancellato, dichiarava esplicitamente:

- migliora solo riassunto e card;
- non tocca test;
- non tocca domande studio;
- rende testi piu' naturali, completi e leggibili.

Questo file conteneva anche logica piu' ricca per riassunto/card: `bestSentences`, `uniqueConceptFacts`, `enrichByContext`, `enrichConceptFact`, `renderSummary`, `renderCards`, e listener sui click di riassunto/card.

## 5. Dove i generatori originali sono stati scavalcati

Risposta chiara:

- I generatori originali sono ancora presenti? Parzialmente si'. Funzioni come `riconosciTema`, `creaCards`, `creaQuiz`, `creaParagrafiRiassunto` esistono ancora nel file o nel `HEAD`, ma nella catena browser attuale non sono piu' la sorgente finale dell'output.
- I generatori originali sono ancora usati dalla pagina universale per l'output finale? No, non per riassunto/card/test/domande nella catena attuale. I pulsanti finiscono dentro V2A18 -> V2A19.
- Sono stati sostituiti da pipeline provvisoria/browser? Si'. La sostituzione effettiva e' `demo-rag/rag-motori-intelligenti-browser-v2a19.js` chiamato da `eseguiMotoriIntelligentiUniversaliV35V2A18` in `universal-document-learning-engine.js`.
- Quale file/funzione li ha sostituiti? `demo-rag/universal-document-learning-engine.js`, funzioni `generaRiassunto`, `generaCardVisive`, `generaTest`, `generaDomandeStudio`, che chiamano `eseguiMotoriIntelligentiUniversaliV35V2A18`. Questa funzione delega a `window.eseguiPipelineMotoriBrowserV2A19`. I generatori specifici sostitutivi sono in `demo-rag/rag-motori-intelligenti-browser-v2a19.js`: `creaRiassuntoReale`, `creaCardBrowser`, `creaTestBrowser`, `creaDomandeStudioBrowser`.

Nota importante: nel working tree `generaRiassunto` e' definita due volte. La prima versione V2A20 chiama `generaRiassuntoLungoNonBloccanteV2A20`, ma piu' sotto c'e' una seconda `function generaRiassunto()` che sovrascrive la prima e chiama V2A18/V2A19. Quindi la variante lunga non bloccante non e' quella effettivamente vincente come definizione finale.

In piu', V2A21 intercetta i click prima dei listener vecchi e li forza sulle funzioni correnti. Questo rende ancora piu' difficile che un generatore precedente possa agire.

## 6. Perche' riassunto e card falliscono o producono output scarso

Riassunto:

`creaRiassuntoReale` in V2A19 e' estrattivo. La funzione:

- divide il testo in frasi;
- calcola keyword per frequenza;
- assegna score alle frasi con `frasiPesate`;
- ordina per score;
- seleziona frasi finche' raggiunge 15%-25% del testo;
- rimette le frasi in ordine originale;
- le concatena.

Non c'e' una vera fase di sintesi concettuale. Non fonde concetti, non riscrive in modo astratto, non raggruppa procedure simili con frequenze diverse. La deduplica e' praticamente assente nel nuovo riassunto: non c'e' `seen`, non c'e' similarita' semantica, non c'e' controllo anti-ripetizione reale sulle frasi scelte. Se un documento lungo contiene procedure ripetitive con piccole variazioni, molte frasi simili ottengono score alto e vengono copiate.

Card:

`creaCardBrowser` usa la stessa base `frasiPesate`: prende frasi pesate e le trasforma in card con titolo da keyword. Anche qui non usa la logica originale `creaCards(testo)` basata su profili/sezioni e `card.descrizione`, ne' il miglioratore V34A. Il risultato puo' essere meccanico: titolo keyword + frase originale.

Fattore V35G:

Il blocco `V35G: spazio prima della punteggiatura` e' stato prodotto dal controllo qualita' testuale quando nel testo finale rimaneva un pattern tipo `testo .`. Questo e' un errore correggibile, ma prima del fix V2A25B veniva trattato come problema bloccante per `report.ok`.

## 7. Perche' test e domande studio funzionano ma domande studio risultano troppo simili ai test

Test V2A19:

`creaTestBrowser(testo, contesto)` usa `contesto.keyword.slice(0, 10)` e genera domande del tipo:

- domanda: `Quale aspetto e' collegato a "keyword" nel documento?`
- opzioni: `[keyword, "un dettaglio non centrale", "un elemento non citato", "una scelta generica"]`
- rispostaCorretta: `keyword`
- spiegazione generica.

Domande studio V2A19:

`creaDomandeStudioBrowser(testo, contesto)` usa `contesto.keyword.slice(0, 16)` e genera domande del tipo:

- domanda: `Perche' il concetto "keyword" e' importante nel documento?`
- rispostaGuida: frase generica sul collegare il tema con procedure, rischi, esempi o obiettivi.

Quindi test e domande studio non condividono la stessa funzione, ma condividono la stessa sorgente logica povera: keyword/frequenze e template generici. Le domande studio non sono quiz con opzioni, quindi formalmente sono aperte, ma semanticamente sono molto simili ai test perche' partono dalle stesse keyword e da template quasi fissi.

Nel generatore precedente (`HEAD`), le domande studio erano separate dal quiz: `generaDomandeStudio()` usava `card.domandaStudio` e `card.descrizione`, mentre `generaTest()` usava `creaQuiz()` con opzioni e distrattori. La separazione da ripristinare e' questa: domande studio aperte con risposta guida specifica per sezione/card, test con opzioni e risposta corretta.

## 8. Analisi errore V35G

Origini trovate:

- `demo-rag/rag-motori-intelligenti-browser-v2a19.js`, `controllaQualita(testo, azione)`: se trova `/\s+[,.!?;:]/`, aggiunge `spazio prima della punteggiatura`; poi la pipeline aggiunge `V35G: ` al problema.
- `demo-rag/universal-document-learning-engine.js`, `eseguiSingoloMotoreV35V2A18`: controllo analogo con messaggio `qualita testuale: spazio prima della punteggiatura`.

Nel percorso V2A19, V35G blocca perche':

1. `controllaQualita` restituisce problemi.
2. La pipeline fa `report.problemi.push("V35G: " + p)`.
3. `report.ok = report.problemi.length === 0`.
4. La pagina pulita e i wrapper lanciano errore se `report.ok !== true`.

Perche' colpiva riassunto/card piu' di test/domande:

- Riassunto e card includono frasi reali copiate dal testo e campi concatenati, quindi e' piu' probabile ereditare o creare `spazio + punteggiatura`.
- Test e domande sono template semplici generati internamente, con meno punteggiatura variabile e meno testo sorgente copiato.

Stato attuale:

- In `rag-motori-intelligenti-browser-v2a19.js` c'e' ora un fix V2A25B: corregge spazi prima della punteggiatura, rimuove solo quel problema V35G per `riassunto` e `card`, e rimette `report.ok = true` se non restano problemi.
- La pagina pulita richiama anche `correggiReportV35GRiassuntoCardV2A25B(report, azione)`.

Diagnosi: V35G dovrebbe stare prima del render come correzione automatica non bloccante per errori meccanici di punteggiatura. Dovrebbe bloccare solo problemi semantici/strutturali gravi, non uno spazio correggibile.

## 9. Lista dei wrapper/demo/prove da NON usare come generatori finali

Da non considerare generatori finali di qualita':

- `demo-rag/rag-motori-intelligenti-browser-v2a19.js`: utile come prova browser-only e bridge, ma i suoi generatori sono template/estrattivi.
- `demo-rag/test-documenti-universale-pulito-v2a24.html`: pagina di test upload reale, non sorgente di generatori finali.
- Blocchi V2A20 in `universal-document-learning-engine.js`: wrapper non bloccanti/stato UI, non generatori qualitativi finali.
- Blocco V2A21 in `universal-document-learning-engine.js`: binding forzato dei pulsanti, non generatore.
- Blocco V2A22 in `universal-document-learning-engine.js`: lettura testo differita, non generatore.
- Fix V2A25B: correzione specifica V35G, non generatore.
- Script `scripts/verifica_*_v2a20.py`, `*_v2a21.py`, `*_v2a22.py`, `*_v2a25b.py`: validator di presenza/stringhe, non prova di qualita' semantica.

## 10. Azione consigliata SENZA applicarla

Cosa ripristinare:

- Ripristinare la catena generatori precedente come sorgente dell'output finale, in particolare `generaRiassunto -> creaParagrafiRiassunto`, `generaCardVisive -> creaCards`, `generaTest -> creaQuiz`, `generaDomandeStudio -> creaCards/card.domandaStudio/card.descrizione`.
- Ripristinare o reintegrare `rag-quality-summary-cards-v34a.js` se era il miglioratore buono per riassunto/card, oppure portarne la logica nel motore ufficiale senza usarlo come patch DOM fragile.

Cosa rimuovere/non usare come output finale:

- Non usare `creaRiassuntoReale`, `creaCardBrowser`, `creaTestBrowser`, `creaDomandeStudioBrowser` come generatori finali.
- Non lasciare che V2A21 blocchi listener/generatori precedenti se questi sono quelli ufficiali.
- Non usare la pagina pulita V2A24 come fonte della logica finale.

Dove collegare i motori qualita' esistenti:

- I motori qualita' V35 dovrebbero ricevere l'output gia' generato dai generatori ufficiali e correggerlo/validarlo prima del render.
- V35G/V35M/V35N dovrebbero fare correzione testuale e completamento prima del render, non rimpiazzare la generazione.
- V35B/V35D devono restare solo sul test/quiz.

Quali generatori lasciare separati:

- Riassunto: generatore di sintesi/paragraphs, non card travestite e non concatenazione di frasi pesate.
- Card: generatore di card/concept/sezioni.
- Test: generatore quiz con opzioni, risposta corretta, distrattori e spiegazione.
- Domande studio: generatore aperto, senza opzioni, con risposta guida specifica e diversa dal quiz.

## 11. Comandi eseguiti

```bash
git status --short
git diff --stat
git diff -- demo-rag/universal-document-learning-engine.js demo-rag/test-documenti-universale.html demo-rag/index.html demo-rag/rag-motori-intelligenti-browser-v2a19.js demo-rag/test-documenti-universale-pulito-v2a24.html
git diff --cached --stat
rg -n "function generaRiassunto|generaRiassunto|creaRiassunto|summary" demo-rag runtime scripts rag
rg -n "function generaCard|generaCard|creaCard|card" demo-rag runtime scripts rag
rg -n "function generaTest|generaTest|creaTest|quiz" demo-rag runtime scripts rag
rg -n "function generaDomande|generaDomande|domandeStudio|Domande studio" demo-rag runtime scripts rag
rg -n "V35G.*spazio prima della punteggiatura|spazio prima della punteggiatura|V35G" demo-rag runtime scripts rag
rg -n "dedup|duplic|ripet|sintesi|riassunto|frasiPesate|frasiUniche|keyword" demo-rag/rag-motori-intelligenti-browser-v2a19.js demo-rag/universal-document-learning-engine.js
rg -n "domande|studio|test|quiz|opzioni|rispostaCorretta|risposta_guida|rispostaGuida" demo-rag runtime scripts rag
git log --oneline --decorate -20
git reflog --date=local -20
git show HEAD:demo-rag/universal-document-learning-engine.js | grep -n "function generaRiassunto" -A90
git show HEAD:demo-rag/universal-document-learning-engine.js | grep -n "function generaDomande" -A80
git show HEAD:demo-rag/universal-document-learning-engine.js | grep -n "function generaCardVisive" -A70
git show HEAD:demo-rag/universal-document-learning-engine.js | grep -n "function generaTest" -A80
git show 04e6984:demo-rag/universal-document-learning-engine.js | grep -n "function generaRiassunto" -A90
git show 8689ed5:demo-rag/universal-document-learning-engine.js | grep -n "function generaRiassunto" -A90
git show HEAD:demo-rag/universal-document-learning-engine.js | grep -n "function creaParagrafiRiassunto" -A80
git show HEAD:demo-rag/rag-quality-summary-cards-v34a.js | sed -n '1,520p'
node --check demo-rag/universal-document-learning-engine.js
node --check demo-rag/rag-motori-intelligenti-browser-v2a19.js
python3 scripts/verifica_motori_browser_v2a19.py
python3 scripts/verifica_fix_v35g_riassunto_card_v2a25b.py
python3 scripts/verifica_generatori_non_bloccanti_v2a20.py
python3 scripts/verifica_binding_forzato_pulsanti_v2a21.py
python3 scripts/verifica_lettura_testo_non_bloccante_v2a22.py
python3 scripts/verifica_collegamenti_effettivi_motori_v35_v2a18.py
```

## 12. Output rilevanti

`node --check`:

```text
node --check demo-rag/universal-document-learning-engine.js: OK, nessun output
node --check demo-rag/rag-motori-intelligenti-browser-v2a19.js: OK, nessun output
```

Validator:

```text
OK V2A.19 MOTORI BROWSER:
- motore browser-only creato
- nessuna API a pagamento
- pagina universale carica V2A19 prima del motore universale
- V2A18 blocca se V2A19 non e' caricato
- i 4 pulsanti generano output tramite V2A19
```

```text
OK V2A.25B FIX V35G RIASSUNTO/CARD:
- V35G corregge gli spazi prima della punteggiatura
- il fix si applica a riassunto e card
- test e domande studio non vengono alterati
- se resta solo V35G, report.ok torna true
- pagina upload rinforzata prima del blocco
```

```text
OK V2A.20 GENERATORI NON BLOCCANTI:
- riassunto non bloccante
- card non bloccante con V2A16/V2A17/V2A18/V2A19 espliciti
- test non bloccante con V2A16/V2A17/V2A18/V2A19 espliciti
- domande studio non bloccante con V2A16/V2A17/V2A18/V2A19 espliciti
- tutti i generatori mostrano stato o errore visibile
```

```text
OK V2A.21 BINDING FORZATO:
- i click dei 4 pulsanti vengono intercettati in capture
- i vecchi listener vengono bloccati con stopImmediatePropagation
- onclick vecchi rimossi
- i pulsanti vengono forzati sui generatori V2A.20
```

```text
OK V2A.22 LETTURA TESTO NON BLOCCANTE:
- i 4 generatori mostrano stato prima di leggere il testo
- leggiTesto() non viene piu' chiamato direttamente nel click
- la lettura testo e' differita dopo setTimeout
```

```text
OK V2A.18 COLLEGAMENTI EFFETTIVI:
- i file motore V35 esistono
- i 4 pulsanti esistono
- i 4 pulsanti chiamano V2A16 e V2A17
- esiste un registro/ponte runtime per i motori intelligenti
- V34A non e' piu' presente nella pagina universale
```

Commit/reflog rilevanti:

```text
4877388 (HEAD -> collega-motori-linguistici-universali-v2a17, origin/main, origin/HEAD, main) Merge V2A16 blocco motori obbligatori RAG
8689ed5 Blocca pulsanti RAG sui motori obbligatori V2A16
04e6984 Aggiunge contesto semantico e completatore linguistico RAG
b1faad6 Aggiunge lucidatore linguistico universale V35M
4b30da5 Crea pipeline unica ufficiale RAG
1bb31c8 Collega catena qualita V35 al RAG documenti lunghi V2A14
c082bd6 (tag: checkpoint-rag-500-pagine-stabile) Stabilizza RAG documenti lunghi fino a 500 pagine
```

Punto probabile prima della rottura: `4877388`/`8689ed5`, cioe' prima delle modifiche non committate che cancellano V34A, aggiungono V2A19 browser-only e riscrivono `universal-document-learning-engine.js`.
