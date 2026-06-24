# RAG documenti lunghi V4.2 final-fix

Questa versione chiude i micro-difetti rimasti nella V4.1.

## Correzioni principali

- `su il` diventa `sul`.
- `di le` diventa `delle`.
- `di il` diventa `del`.
- `rag`, `pdf`, `ocr` diventano `RAG`, `PDF`, `OCR`.
- Le domande usano accordi più corretti:
  - `Le card riassuntive sono importanti`;
  - `Le parole chiave sono importanti`;
  - `Il motore RAG è importante`.
- Le risposte stampate nel PDF restano visibili.
- Le card vengono generate prima dai concetti principali, così si riducono duplicati e titoli brutti.
- Il numero massimo di card predefinito scende a 6 per evitare pagine quasi vuote nel PDF.

## Nota Chrome

Se nella stampa compaiono ancora data, URL o numero pagina, è Chrome che sta stampando le sue intestazioni automatiche.

Per un PDF pulito:

```text
Stampa > Altre impostazioni > togli spunta a "Intestazioni e piè di pagina"
```

## Avvio

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
python3 -m http.server 8000
```

Aprire:

```text
http://localhost:8000/demo-rag/test-rag-documenti-lunghi-v42-final-fix.html?v=42
```

Hard refresh:

```text
Cmd + Shift + R
```
