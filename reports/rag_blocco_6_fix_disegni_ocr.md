# Blocco 6 - Fix disegni per ramo e OCR immagini

- Corretto il motore disegni: ora il disegno viene scelto prima dal ramo della card, non da parole generiche del testo.
- Curriculum: profilo, esperienze, competenze tecniche, competenze trasversali, formazione, obiettivo e punti forti hanno disegni distinti.
- Ridotto il rischio che sezioni diverse finiscano con lo stesso SVG.
- Aggiunto OCR immagini con Tesseract.js.
- Ora il caricamento file accetta TXT, PDF, PNG, JPG, JPEG e WEBP.
- PDF con testo selezionabile continua a usare PDF.js; immagini e foto usano OCR.
