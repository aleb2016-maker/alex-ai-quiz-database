# OCR locale - formato tabella e fumetto severo

- La modalità tabella/scheda ora trasforma il testo OCR in lista leggibile per giorni.
- Aggiunto selettore del miglior risultato OCR tra macOS Vision e Tesseract con PSM diversi.
- Per tabelle: prova PSM 6 e PSM 4.
- Per fumetti: prova PSM 11, PSM 12 e PSM 6.
- Se il fumetto non produce testo buono, viene dichiarato fumetto non leggibile invece di inventare testo.
