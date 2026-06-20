# Inserimento documenti nel motore RAG

Il progetto ora include un cruscotto visuale in `demo-rag/index.html` per mostrare il flusso:

**documento → RAG → quiz/test/minicorso → revisione → pacchetto scaricabile**.

## Tipi di documento previsti

La pipeline è pensata per lavorare con materiali come:

- `.md`
- `.txt`
- `.json`
- `.csv`
- `.pdf`
- `.docx`

La pagina web statica può selezionare il file e mostrare il comando consigliato, ma non può caricarlo davvero su GitHub da sola.

Per usare il documento nella pipeline reale bisogna copiarlo nella cartella:

```bash
rag/documenti/
```

## Esempio

```bash
cp ~/Downloads/documento_azienda.md rag/documenti/documento_azienda.md
python3 scripts/pipeline_formazione_completa.py rag/documenti/documento_azienda.md --titolo "Documento aziendale"
```

## Sicurezza del flusso

Le domande generate dal RAG non entrano direttamente nei database ufficiali. Passano prima da:

1. generazione temporanea;
2. validazione JSON;
3. revisione;
4. controlli qualità;
5. import controllato solo se approvate.

Questo protegge il progetto da domande deboli, duplicate, troppo intuitive o non coerenti con il documento originale.
