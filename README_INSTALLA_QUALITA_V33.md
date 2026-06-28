# RAG Pipeline Qualità V3.3

Micro-rifinitura didattica finale della pipeline RAG separata.

## Cosa migliora

- Elimina la categoria `Generico` dal riassunto quando esistono categorie reali.
- Filtra concetti-esempio deboli che non devono diventare card principali.
- Riduce card quasi duplicate come `Comportamenti corretti azienda` / `Comportamenti corretti`.
- Rende più naturali le domande studio su password, utente, integrità, disponibilità e autenticazione a due fattori.
- Limita le domande ripetute nel test, soprattutto sul tema password.
- Non censura il contenuto caricato dall'utente.

## Installazione

```bash
cd /Users/alessandrobarbarossa/alex-ai-workspace
unzip -o ~/Downloads/rag_pipeline_qualita_v33.zip
python3 scripts/verifica_rag_pipeline_qualita_v33.py
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
