# V3.9.7 Study Pack Universale V4 - SP5 qualità concetti/domande

Questa patch sostituisce solo il runtime Study Pack e il relativo test.
Non modifica UI, pulsanti, pagina RAG o motore riassunto.

File inclusi:
- `mini_llm/python/runtime/mini_llm_universal_study_pack_v4.py`
- `scripts/test_study_pack_universale_v397.py`

Comando test:

```bash
python3 scripts/test_study_pack_universale_v397.py
```

Generazione documento reale:

```bash
mkdir -p reports/study_pack_universale_v397
python3 mini_llm/python/runtime/mini_llm_universal_study_pack_v4.py \
  --input rag/documenti/documento_rag_sicurezza_informatica_aziendale.md \
  --out-json reports/study_pack_universale_v397/documento_reale_study_pack.json \
  --out-md reports/study_pack_universale_v397/documento_reale_study_pack.md
```

## Correzioni già incluse

SP1:
- alza la soglia minima delle frasi sorgente usate come evidenza;
- impedisce card/risposte guida troppo corte;
- non aggiunge fallback, demo, sentence bank o vecchie liste.

SP2:
- blocca concetti chiave non naturali generati da pezzi casuali di frase;
- vieta concetti tipo `significa dati devono`, `dati riservati senza`, `servizio viene violato`, `utenti usano password`, `dati dispositivi account`.

SP5:
- filtra frasi tecniche/meta tipo `rag/documenti`, cartelle, generazione quiz/test e mini-corsi quando finiscono nel documento sorgente;
- non attraversa più stopword, congiunzioni e preposizioni per creare micro-concetti artificiali;
- blocca concetti come `strumenti comportamenti dati`, `solo password`, `chiaro sistema recuperare`, `password altri account`, `aziendale account online`;
- elimina il doppio punto interrogativo nelle domande guida;
- elimina domande meccaniche tipo `Quale ruolo ha ... rispetto a ...?`;
- aggiunge regressione automatica sul caso sicurezza informatica con frase meta di installazione.

Regola: se i concetti chiave, le domande o il materiale studio non sono leggibili come contenuto reale, il test deve fallire o il motore deve restituire `QUALITY_BLOCKED`.


## Nota SP5

SP5 aggiunge filtri contro concetti incompleti come `buona password dovrebbe`, `password dovrebbe contenere` e frasi meta come `nuovi utenti aziendali`. Inoltre separa la spiegazione del quiz dalle 4 opzioni nel Markdown.


## Nota SP5

SP5 blocca concetti verbali o meta-tecnici rimasti nello Study Pack, come `manuale tecnico avanzato`, `salvare password lunghe`, riferimenti a `sistema RAG`, `materiale formativo chiaro` e `domande controllate`. Non tocca UI, pulsanti o riassunto.


## SP7

- Limita i concetti chiave esposti ai migliori 10.
- Blocca concetti orfani/spuri come `secondo controllo`.
- Non tocca UI, pulsanti o riassunto.


## Nota SP7

SP7 corregge il validatore: `salvare password lunghe e uniche` è ammesso come frase sorgente del password manager, ma resta vietato come concetto chiave/titolo.

Controllo corretto dei concetti:

```bash
sed -n '/## Concetti chiave/,/## Sintesi/p' reports/study_pack_universale_v397/documento_reale_study_pack.md
```

Non usare un grep globale su `password lunghe`, perché quella frase può comparire correttamente nella fonte testuale del password manager.
