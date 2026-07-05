# FASE 5.14.0 — UI BUTTONS PROBE

Status: `PASS - Fase 5.14.0: UI_BUTTONS_PROBE_READY`

- Pagina: `demo-rag/test-documenti-universale.html`
- Pagina esiste: `True`

## Pulsanti

| Key | Found | Match |
|---|---:|---|
| `summary` | `True` | `genera riassunto, riassunto` |
| `cards` | `True` | `genera card, card` |
| `quiz` | `True` | `genera test, test, quiz` |
| `study` | `True` | `genera domande studio, domande studio` |

## Script caricati

| Script | Exists | Size | Keywords | Forbidden |
|---|---:|---:|---|---|
| `demo-rag/phase5-14-2-dom-safety-guard.js` | `True` | `1189` | `genera` | `` |
| `demo-rag/rag-input-reale-guard.js` | `True` | `4239` | `test, genera, addeventlistener` | `` |
| `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js` | `False` | `0` | `` | `` |
| `https://cdn.jsdelivr.net/npm/tesseract.js@5/dist/tesseract.min.js` | `False` | `0` | `` | `` |
| `https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js` | `False` | `0` | `` | `` |
| `demo-rag/layout-rigido-rag.js` | `True` | `14305` | `riassunto, card, test, domande, studio, generate, genera, addeventlistener` | `` |
| `demo-rag/layout-rigido-generazione-subito.js` | `True` | `7825` | `riassunto, summary, card, test, domande, studio, generate, genera, addeventlistener` | `` |
| `demo-rag/buttons-full-row.js` | `True` | `5912` | `riassunto, summary, card, test, domande, studio, genera, addeventlistener` | `` |
| `demo-rag/rag-action-icons-v46.js` | `True` | `11201` | `riassunto, card, test, domande, studio, genera, addeventlistener` | `` |
| `demo-rag/rag-concept-document-engine-v46.js` | `True` | `19383` | `riassunto, summary, card, quiz, test, domande, studio, genera, addeventlistener` | `sicurezza informatica aziendale` |
| `demo-rag/pdf-export-browser-v6.js` | `True` | `10505` | `riassunto, summary, card, quiz, test, domande, studio, generate, genera, addeventlistener` | `` |
| `demo-rag/rag-quality-summary-cards-v34a.js` | `True` | `28602` | `riassunto, summary, card, test, domande, studio, generate, genera, addeventlistener` | `fallback, sicurezza informatica aziendale` |
| `demo-rag/universal-document-learning-engine.js` | `True` | `82074` | `riassunto, summary, card, quiz, test, domande, studio, generate, genera, addeventlistener` | `fallback` |
| `demo-rag/phase5-14-ui-buttons-real-connector.js` | `True` | `8156` | `riassunto, summary, card, quiz, test, domande, studio, generate, genera, addeventlistener` | `fallback` |
| `demo-rag/phase5-14-2-runtime-visible-panel.js` | `True` | `4864` | `riassunto, summary, card, quiz, test, domande, studio, generate, genera, addeventlistener` | `fallback` |

## Defects

- Nessuno

## Warnings

- `Possibili frammenti demo/fallback in demo-rag/rag-concept-document-engine-v46.js: ['sicurezza informatica aziendale']`
- `Possibili frammenti demo/fallback in demo-rag/rag-quality-summary-cards-v34a.js: ['fallback', 'sicurezza informatica aziendale']`
- `Possibili frammenti demo/fallback in demo-rag/universal-document-learning-engine.js: ['fallback']`
- `Possibili frammenti demo/fallback in demo-rag/phase5-14-ui-buttons-real-connector.js: ['fallback']`
- `Possibili frammenti demo/fallback in demo-rag/phase5-14-2-runtime-visible-panel.js: ['fallback']`

## Note

- Questa fase non collega ancora i motori.
- Serve a mappare pagina, pulsanti e script reali prima della patch UI.
- Nessuna UI/PDF/app viene modificata.
