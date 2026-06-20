# Pipeline materiale formativo

Questa pipeline completa i pezzi mancanti dopo la base RAG.

## Comando principale

python3 scripts/pipeline_formazione_completa.py rag/documenti/documento_rag_sicurezza_informatica_aziendale.md --titolo "Sicurezza informatica aziendale"

## Flusso

File PDF/TXT/MD/JSON
↓
testo estratto
↓
documento corretto
↓
validazione documento
↓
mini-corso interattivo HTML/JSON
↓
pacchetto ZIP riutilizzabile
↓
report finale

## Output principali

- dist/formazione/testo_estratto.md
- dist/formazione/documento_corretto.md
- dist/formazione/minicorso_interattivo.json
- dist/formazione/minicorso_interattivo.html
- downloads/pacchetto-formazione-*.zip

## Nota

La pipeline non modifica automaticamente i database ufficiali dentro data/.
