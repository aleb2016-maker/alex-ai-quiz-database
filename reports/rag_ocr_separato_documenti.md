# Motore OCR separato documenti

- Creata pagina `demo-rag/test-ocr-documenti.html`.
- Creato motore `demo-rag/ocr-document-reader-engine.js`.
- Supporta TXT, PDF con testo selezionabile, PDF immagine, JPG, PNG, WEBP.
- PDF immagine/fumetti: renderizza le pagine e applica OCR.
- Immagini senza testo documentale vengono riconosciute come non documentali, non classificate come Sport.
- Il motore OCR è separato dal motore universale principale ma collegato con un pulsante.
