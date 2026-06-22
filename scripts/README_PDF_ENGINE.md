# Motore PDF Playwright per progetto RAG

## File inclusi

- `pdf_engine_playwright.py`
- `test_pdf_engine_playwright.py`
- `fastapi_pdf_endpoint_example.py`

## Installazione

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
pip install playwright
python -m playwright install chromium
```

## Dove copiare i file

Copia i file Python dentro:

```text
scripts/
```

## Test rapido

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
python scripts/test_pdf_engine_playwright.py
```

Output:

```text
dist/pdf/materiale_rag_demo.pdf
```

## Regole fondamentali

Il PDF deve ricevere HTML pulito dal motore RAG, non pezzi presi dalla schermata.

Classi principali:

```html
<article class="blocco-esercizio">
  <div class="card-grafica">...</div>
  <div class="testo-affiancato">...</div>
</article>

<section class="riassunto-lungo">...</section>

<article class="blocco-quiz">...</article>

<article class="domanda-studio">...</article>
```
