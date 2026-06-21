# Motore RAG completo funzionante

Il motore RAG ora lavora sia nella demo browser sia nel pacchetto scaricabile.

## Output generati

- testo estratto;
- riassunto;
- tabella concetti in Markdown e CSV;
- card JSON e HTML;
- quiz JSON e HTML interattivo;
- minicorso HTML;
- grafico SVG parole chiave;
- statistiche JSON;
- report finale.

## Uso locale

Dalla cartella principale del progetto:

    python3 scripts/rag_motore_documenti_completo.py rag/documenti/esempio_documento_aziendale_formazione.md --titolo "Formazione aziendale"

Dal pacchetto scaricato:

    python3 scripts/rag_motore_documenti_completo.py documenti/tuo_file.pdf --titolo "Titolo documento"

Il comando termina da solo e crea gli output dentro output_generati/.
