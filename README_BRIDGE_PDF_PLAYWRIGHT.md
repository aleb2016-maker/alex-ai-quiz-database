# Bridge PDF Playwright per demo RAG

Questo pacchetto collega il pulsante "Scarica PDF" della pagina:

```text
demo-rag/test-documenti-universale.html
```

al motore Python Playwright già salvato in:

```text
scripts/pdf_engine_playwright.py
```

## File inclusi

```text
scripts/rag_pdf_playwright_server.py
scripts/installa_bridge_pdf_playwright.py
demo-rag/pdf-playwright-bridge.js
```

## Installazione nel progetto

Dalla cartella principale del progetto:

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace

unzip ~/Downloads/rag_pdf_playwright_bridge_pack.zip -d .
python scripts/installa_bridge_pdf_playwright.py
```

## Controllo

```bash
python3 -m py_compile scripts/rag_pdf_playwright_server.py
grep -n "pdf-playwright-bridge" demo-rag/test-documenti-universale.html
```

## Avvio server

Chiudi eventuali server vecchi con `Ctrl + C`.

Poi avvia:

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
python scripts/rag_pdf_playwright_server.py --port 8020
```

## URL da aprire

```text
http://127.0.0.1:8020/demo-rag/test-documenti-universale.html?v=20260622-playwright-pdf
```

Refresh duro:

```text
Cmd + Shift + R
```

## Test

1. Incolla testo.
2. Genera card.
3. Premi Scarica PDF.

Il PDF deve essere generato dal backend Playwright e deve mantenere card, layout, sfondo scuro, SVG/disegni e colori.
