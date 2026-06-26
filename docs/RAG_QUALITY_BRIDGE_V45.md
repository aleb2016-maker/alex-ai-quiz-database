# RAG Quality Bridge V4.5

## Obiettivo

La V4.5 collega il RAG ai motori qualità già presenti nel progetto senza riscriverli.

Regola principale:

```text
RAG = legge, spezza, organizza
Motori qualità = validano
Motori grafici = disegnano
Export = scarica
```

## File aggiunti

```text
scripts/rag_large_input_manager_v45.py
scripts/rag_quality_bridge_v45.py
scripts/rag_pipeline_documenti_grandi_v45.py
scripts/test_rag_quality_large_input_v45.py
```

## Cosa fa

- legge TXT, MD, PDF;
- limita il numero di pagine con `--max-pages`;
- crea `testo_estratto.md`;
- crea `chunks.jsonl`;
- crea `manifest.json`;
- cerca i validatori già esistenti;
- produce `report_qualita.json`;
- non inventa un validatore nuovo.

## Comando esempio

```bash
python3 scripts/rag_pipeline_documenti_grandi_v45.py \
  --input rag/documenti/documento_grande.pdf \
  --output dist/rag_documenti_grandi_v45 \
  --max-pages 120 \
  --chunk-size 1800 \
  --overlap 250
```

## Regola di sicurezza

Se un validatore esiste, il bridge prova a usarlo.

Se manca, lo segnala.

Se fallisce, lo scrive nel report.

Il RAG non decide da solo che una domanda è buona.
