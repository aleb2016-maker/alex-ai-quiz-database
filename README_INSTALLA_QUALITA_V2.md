# RAG Pipeline Qualità V2

Questo pacchetto migliora velocemente la pipeline RAG intelligente V1 senza cambiare la pagina principale e senza censurare documenti.

## Cosa migliora

- Filtra titoli Markdown sporchi come `# Documento` dagli estrattori.
- Esclude frasi introduttive tecniche tipo fonte/progetto/cartella dai concetti didattici.
- Rende più puliti soggetto, predicato e oggetto dei fatti.
- Aggiunge testi leggibili alle relazioni: `questionHint` e `answerText`.
- Le domande studio non mostrano più frecce o tipi tecnici come `problema_soluzione`.
- Le domande test usano modelli più naturali.
- I distrattori vengono accorciati e filtrati.
- Il validatore segnala domande sporche, opzioni troppo lunghe e testo tecnico visibile.

## Installazione

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
unzip -o ~/Downloads/rag_pipeline_qualita_v2.zip
python3 scripts/verifica_rag_pipeline_qualita_v2.py
python3 -m http.server 8000
```

Apri:

```text
http://localhost:8000/demo-rag/test-rag-pipeline-intelligente-v1.html
```

Refresh duro:

```text
Cmd + Shift + R
```

## Nota importante

I nomi dei file restano `*-v1.js` per compatibilità con la pagina test già installata, ma dentro i moduli la versione è V2.
