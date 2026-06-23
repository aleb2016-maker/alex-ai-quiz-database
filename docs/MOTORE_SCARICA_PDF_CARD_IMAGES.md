# Motore Scarica PDF da immagini card

Questo blocco corregge la logica del PDF.

Il PDF non deve ricostruire la grafica della card.

Flusso corretto:

```text
demo genera card
→ frontend cattura le card come PNG
→ backend salva card_01.png, card_02.png...
→ Python crea JSON imagePath
→ Java PDF stampa le immagini
→ browser scarica il PDF
```

## Avvio server unico

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
source backend/.venv/bin/activate
python3 scripts/rag_pdf_export_server.py --port 8030
```

## URL test

```text
http://127.0.0.1:8030/demo-rag/test-scarica-pdf-card-images.html
```

## URL pagina reale

```text
http://127.0.0.1:8030/demo-rag/test-documenti-universale.html
```

## Hook pagina reale

```bash
python3 scripts/installa_hook_pdf_export_demo.py
```

## Regola

- 1 card immagine = 1 pagina PDF
- niente icone inventate
- niente layout Java interno
- Java stampa solo PNG/JPG già renderizzati
