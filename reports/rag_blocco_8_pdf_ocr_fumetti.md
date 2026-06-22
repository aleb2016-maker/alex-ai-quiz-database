# Blocco 8 - OCR per PDF immagine e fumetti

- Migliorata la lettura PDF.
- Prima il motore prova a leggere il testo selezionabile del PDF.
- Se il PDF non contiene testo selezionabile, renderizza le pagine come immagini.
- Applica OCR con Tesseract.js alle pagine renderizzate.
- Supporta meglio PDF scansionati, immagini dentro PDF e fumetti con balloon leggibili.
- Limite OCR: prime 8 pagine, per evitare tempi troppo lunghi nel browser.
- Se il testo OCR è spazzatura o troppo frammentato, viene bloccato.
