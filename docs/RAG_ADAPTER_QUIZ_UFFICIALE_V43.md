# RAG Adapter Quiz Ufficiale V4.3

Questo blocco risolve il problema alla radice: prima produce dati quiz nel formato ufficiale del progetto, poi usa i controlli già presenti.

Non aggiunge una nuova demo e non genera PDF.

## File aggiunti

- `scripts/rag_adapter_quiz_ufficiale_v43.py`
- `scripts/verifica_rag_adapter_quiz_ufficiale_v43.py`
- `docs/RAG_ADAPTER_QUIZ_UFFICIALE_V43.md`
- `reports/rag_adapter_quiz_ufficiale_v43.md` dopo esecuzione

## Output

- `dist/generated/rag_quiz_bridge_v43.json`
- `dist/generated/rag_quiz_bridge_v43_container.json`

## Comando esempio

```bash
python3 scripts/rag_adapter_quiz_ufficiale_v43.py \
  --documento rag/documenti/documento_rag_sicurezza_informatica_aziendale.md \
  --categoria informatica \
  --sottocategoria sicurezza_informatica \
  --numero-domande 6 \
  --output dist/generated/rag_quiz_bridge_v43.json

python3 scripts/verifica_rag_adapter_quiz_ufficiale_v43.py .
```

## Motori già presenti riusati

- `scripts/qualita_linguistica.py`
- `scripts/rag_valida_quiz_json.py`
- `scripts/rag_valida_distrattori_forti.py`
- formato ufficiale di `data/ai.json`, `data/informatica.json`, `data/matematica.json`, `data/inglese.json`
- regola `tre_distrattori_forti`

Il collegamento alla UI/card/PDF deve arrivare solo dopo il superamento di questi controlli.
