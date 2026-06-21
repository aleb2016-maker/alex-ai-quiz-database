# Pacchetto RAG riutilizzabile

Questo pacchetto trasforma documenti TXT, Markdown o PDF in riassunti, tabelle, card, quiz, minicorsi, report e grafici.

## Uso rapido

1. Metti il file dentro documenti/.
2. Apri il terminale dentro questa cartella.
3. Esegui:

    python3 scripts/rag_motore_documenti_completo.py documenti/tuo_file.md --titolo "Titolo documento"

Per PDF:

    python3 scripts/rag_motore_documenti_completo.py documenti/tuo_file.pdf --titolo "Titolo documento"

Gli output vengono creati dentro output_generati/.

## Demo browser

Apri demo-rag/index.html.


## Output leggibili

Dopo la generazione apri prima:

```text
output_generati/NOME-DOCUMENTO/index.html
```

oppure direttamente:

```text
output_generati/NOME-DOCUMENTO/riassunto.html
```

I file `.md`, `.json` e `.csv` sono output tecnici esportabili.
