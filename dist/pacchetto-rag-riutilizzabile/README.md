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


## Demo browser scaricabile

La demo `demo-rag/index.html` permette di leggere gli output direttamente nella pagina e di scaricare:

- ZIP completo degli output;
- `index.html`;
- `riassunto.html`;
- `riassunto.md`;
- `tabelle_concetti.md`;
- `tabelle_concetti.csv`;
- `cards.html`;
- `cards.json`;
- `quiz_interattivo.html`;
- `quiz.json`;
- `minicorso_interattivo.html`;
- `analisi_completa.json`;
- `statistiche.json`;
- `report_rag.md`.



## Demo browser con scelta output

La demo `demo-rag/index.html` permette di scegliere cosa generare:

- riassunto;
- tabelle;
- card;
- quiz;
- minicorso;
- dati tecnici.

Dopo la generazione mostra pulsanti separati per scaricare ogni file e un pulsante ZIP per scaricare tutti gli output selezionati.


## OCR e card grafiche nella demo RAG

La demo `demo-rag/index.html` ora permette anche di:

- attivare OCR per PDF scansionati e immagini;
- generare card di ripasso colorate con illustrazioni SVG;
- scaricare soprattutto riassunti, tabelle e card;
- scaricare uno ZIP con gli output selezionati.

Nota: nella demo web i file vengono salvati nella cartella Download del browser, salvo impostazioni diverse del dispositivo.
