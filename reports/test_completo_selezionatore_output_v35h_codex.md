# Test completo selezionatore output RAG V3.5H - Codex

Data test: 2026-06-28
Pagina testata: `demo-rag/test-selezionatore-output-v35h.html`
URL browser: `http://localhost:8080/demo-rag/test-selezionatore-output-v35h.html`

## 1. Stato git

Branch corrente: `rag-collega-qualita-quiz-v34b`

`git status --short` durante il test:

```text
 M demo-rag/test-selezionatore-output-v35h.html
 M reports/rag_demo_selezionatore_output_v35h.md
 M scripts/verifica_rag_demo_selezionatore_output_v35h.py
?? README_INSTALLA_V35K_REALE.md
?? reports/rag_cleaner_finale_visibile_v35k.md
?? reports/rag_revisore_accordo_pronomi_v35j.md
?? reports/test_completo_selezionatore_output_v35h_codex.md
?? scripts/applica_v35k_reale.py
?? scripts/rag_cleaner_finale_visibile_v35k.py
?? scripts/rag_revisore_accordo_pronomi_v35j.py
?? scripts/verifica_rag_revisore_accordo_pronomi_v35j.py
```

Note operative: non sono stati eseguiti commit, push, reset o cancellazioni. Non sono stati toccati `main`, README o pulsanti ufficiali.

## 2. Controlli obbligatori iniziali

### `grep -n "rag_output_" demo-rag/test-selezionatore-output-v35h.html`

Risultato: la pagina carica solo `rag_output_cleaner_finale_v35k`.
Non carica più `rag_output_accordo_pronomi_v35j`.

```text
357:        output: "../dist/generated/rag_output_cleaner_finale_v35k/solo_riassunto/sicurezza_reale/output_cleaner_finale_v35k.json"
363:        output: "../dist/generated/rag_output_cleaner_finale_v35k/solo_card/sicurezza_reale/output_cleaner_finale_v35k.json"
369:        output: "../dist/generated/rag_output_cleaner_finale_v35k/solo_domande_studio/sicurezza_reale/output_cleaner_finale_v35k.json"
375:        output: "../dist/generated/rag_output_cleaner_finale_v35k/solo_test/sicurezza_reale/output_cleaner_finale_v35k.json"
381:        output: "../dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json"
```

### `find dist/generated/rag_output_cleaner_finale_v35k -type f | sort`

Risultato: gli output V3.5K esistono per tutti e 5 i casi.

```text
dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json
dist/generated/rag_output_cleaner_finale_v35k/solo_card/sicurezza_reale/output_cleaner_finale_v35k.json
dist/generated/rag_output_cleaner_finale_v35k/solo_domande_studio/sicurezza_reale/output_cleaner_finale_v35k.json
dist/generated/rag_output_cleaner_finale_v35k/solo_riassunto/sicurezza_reale/output_cleaner_finale_v35k.json
dist/generated/rag_output_cleaner_finale_v35k/solo_test/sicurezza_reale/output_cleaner_finale_v35k.json
```

### `python3 scripts/verifica_rag_demo_selezionatore_output_v35h.py`

Risultato: verifica pagina con `ESITO: OK`.

```text
OK: pagina controllata
OK: output V3.5K dist/generated/rag_output_cleaner_finale_v35k/solo_riassunto/sicurezza_reale/output_cleaner_finale_v35k.json
OK: output V3.5K dist/generated/rag_output_cleaner_finale_v35k/solo_card/sicurezza_reale/output_cleaner_finale_v35k.json
OK: output V3.5K dist/generated/rag_output_cleaner_finale_v35k/solo_domande_studio/sicurezza_reale/output_cleaner_finale_v35k.json
OK: output V3.5K dist/generated/rag_output_cleaner_finale_v35k/solo_test/sicurezza_reale/output_cleaner_finale_v35k.json
OK: output V3.5K dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json
Errori totali: 0
ESITO: OK
```

## 3. Setup browser

- Server locale avviato con `python3 -m http.server 8080`.
- `curl -I http://localhost:8080/demo-rag/test-selezionatore-output-v35h.html`: `HTTP/1.0 200 OK`.
- Pagina aperta nel browser integrato.
- Hard refresh eseguito con `Cmd + Shift + R`.
- Log browser error/warning: nessun errore rilevato.
- Nel DOM della pagina caricata: `rag_output_cleaner_finale_v35k` presente, `rag_output_accordo_pronomi_v35j` assente.

Nota UI: lo status visibile dice ancora `output accordo/pronomi V3.5J`, ma il sorgente della pagina e le richieste effettive puntano ai JSON V3.5K. È quindi una label obsoleta, non un caricamento del vecchio output.

## 4. Esito dei 5 pulsanti

### Solo riassunto

Esito browser: `DA CORREGGERE`.

- La pagina carica senza errori.
- Stato visibile: `✅ Caricato: Solo riassunto · output accordo/pronomi V3.5J`.
- Piano coerente: `solo_riassunto`.
- Motore selezionato: `didattico_v35c`.
- Qualità finale UI: `OK`.
- Sezioni mostrate: categorie didattiche e riassunto.
- Non mostra card, domande studio o test.
- Fonti leggibili, categorie e sottocategorie presenti.
- Problema reale: resta una frase tagliata male.

### Solo card

Esito browser: `OK`.

- La pagina carica senza errori.
- Stato visibile: `✅ Caricato: Solo card · output accordo/pronomi V3.5J`.
- Piano coerente: `solo_card`.
- Motore selezionato: `didattico_v35c`.
- Qualità finale UI: `OK`.
- Mostra solo card studio, senza riassunto, domande studio o test.
- Le card hanno concetti distinti e non sembrano copia-incolla.
- Il problema precedente `ruolo di il rischio` risulta corretto in `ruolo del rischio`.
- Fonti leggibili, categorie e sottocategorie presenti.

### Domande studio

Esito browser: `DA CORREGGERE`.

- La pagina carica senza errori.
- Stato visibile: `✅ Caricato: Domande studio · output accordo/pronomi V3.5J`.
- Piano coerente: `solo_domande_studio`.
- Motore selezionato: `didattico_v35c`.
- Qualità finale UI: `OK`.
- Mostra solo domande studio, senza riassunto, card o test.
- Le risposte guida sono migliorate e aiutano davvero a ripassare.
- Il problema precedente `chiarisce «Azione consigliata» e poi lo collega` non compare più.
- Fonti leggibili, categorie e sottocategorie presenti.
- Problema reale: tutte le domande hanno doppio punto interrogativo finale `? ?`.

### Test interattivo

Esito browser: `DA CORREGGERE`.

- La pagina carica senza errori.
- Stato visibile: `✅ Caricato: Test interattivo · output accordo/pronomi V3.5J`.
- Piano coerente: `solo_test`.
- Motori selezionati: `bridge_quiz_v35b`, `didattico_v35c`, `test_v35d`, `bridge_quiz_v35b`.
- Qualità finale UI: `OK`.
- 5 domande presenti.
- Ogni domanda ha 4 opzioni visibili.
- La risposta corretta visibile è sempre tra le opzioni.
- Non sono state rilevate opzioni duplicate nella stessa domanda.
- Click su risposta sbagliata: mostra `❌ Riprova. La risposta corretta viene evidenziata.` e marca la corretta.
- Click su risposta corretta: mostra `✅ Corretto`.
- Le spiegazioni sono migliori e non contengono più `gli obiettivi principali è`.
- Problemi reali: tutte le domande hanno `? ?`; una opzione inizia con minuscola: `situazione da valutare.`

### Completo

Esito browser: `DA CORREGGERE`.

- La pagina carica senza errori.
- Stato visibile: `✅ Caricato: Completo · output accordo/pronomi V3.5J`.
- Piano coerente: `output_completo`.
- Motore selezionato: `orchestratore_v35e`.
- Qualità finale UI: `OK`.
- Mostra riassunto, card, domande studio e test.
- Fonti leggibili, categorie e sottocategorie presenti.
- Il materiale è coerente e le sezioni hanno funzioni diverse: riassunto sintetizza, card spiegano, domande fanno ripassare, test verifica.
- Problemi reali ereditati: frase tagliata del riassunto e doppio punto interrogativo nelle domande.

## 5. Problemi trovati con testo esatto

### Frase ancora tagliata male

Presente in `solo_riassunto` e `output_completo`:

```text
Per studiare il documento, «Regola operativa» va letto come passaggio autonomo: una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono.
```

### Doppio punto interrogativo nelle domande studio

Presente in `solo_domande_studio` e `output_completo`:

```text
Che cosa devi saper spiegare su «Sicurezza informatica»? ?
```

```text
Perché «Rischio e conseguenza» è utile per capire il documento? ?
```

```text
Quale collegamento principale devi ricordare su «Regola operativa»? ?
```

```text
Come spiegheresti «Azione consigliata» senza copiare il testo? ?
```

```text
Quale ruolo ha «Obiettivi principali» nel materiale di studio? ?
```

### Doppio punto interrogativo nel quiz

Presente in `solo_test` e `output_completo`:

```text
Quale risposta spiega meglio «Sicurezza informatica»? ?
```

```text
Quale opzione è più coerente con «Rischio e conseguenza»? ?
```

```text
Che cosa devi riconoscere su «Regola operativa»? ?
```

```text
Quale scelta interpreta correttamente «Azione consigliata»? ?
```

```text
Quale affermazione riassume meglio «Obiettivi principali»? ?
```

### Opzione con maiuscola mancante

Presente in `solo_test` e `output_completo`:

```text
situazione da valutare. Quando si usa una rete pubblica è meglio evitare operazioni sensibili, come accesso a conti bancari, sistemi aziendali o pannelli amministrativi.
```

### Label UI obsoleta

La pagina carica V3.5K, ma lo status visibile continua a dire:

```text
output accordo/pronomi V3.5J
```

Questo può confondere la lettura manuale del test.

## 6. Problemi risolti rispetto al giro precedente

Non compaiono più:

- `chiarisce «Azione consigliata» e poi lo collega`
- `Punto chiave: riconosci il ruolo di il rischio`
- `La spiegazione corretta mostra perché gli obiettivi principali è`
- le opzioni robotiche con formula ripetuta `Nel contesto di ...`
- gli errori qualità V3.5J visibili nella UI

## 7. Correzioni consigliate

1. Sistemare la frase troncata su `piattaforme che contengono.` completandola o usando la versione completa già presente nelle card/test: `piattaforme che contengono dati sensibili`.
2. Rimuovere il doppio punto interrogativo `? ?` da domande studio e quiz.
3. Capitalizzare `situazione da valutare.` quando appare come inizio opzione.
4. Aggiornare lo status UI da `output accordo/pronomi V3.5J` a una label coerente con V3.5K.
5. Valutare se deduplicare `bridge_quiz_v35b` nel piano `solo_test`, perché compare due volte.

## 8. Conclusione

ESITO: DA CORREGGERE

La migrazione a V3.5K è corretta: la pagina carica solo `rag_output_cleaner_finale_v35k`, non carica più `rag_output_accordo_pronomi_v35j`, i cinque output V3.5K esistono e la verifica pagina dà `ESITO: OK`.

Il test umano però trova ancora problemi reali nei testi visibili: una frase tagliata, doppio punto interrogativo nelle domande, una maiuscola mancante in un'opzione e una label UI obsoleta.
