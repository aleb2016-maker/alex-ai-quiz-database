# Validazione Inference Engine V3.11 Human Aligned Decoder

- Stato finale: **PASS**
- Codice inference: `0`
- Codice semantic gate V3.8.4: `0`
- Semantic Gate status: `PASS`
- Output controllati dal gate: `8`
- Output falliti dal gate: `0`

## File generati

- Output inferenza: `mini_llm/data/inference_v311_human_aligned_decoder/inference_engine_v311_human_aligned_decoder_outputs.json`
- Report inferenza: `mini_llm/reports/inference_engine_v311_human_aligned_decoder_report.md`
- Report gate: `mini_llm/reports/model_semantic_gate_v384_report.md`

## Regola di accettazione

La V3.11 è accettabile solo se:

- l'inference interna è PASS;
- il Semantic Gate V3.8.4 è PASS;
- gli output sono buoni anche a controllo umano;
- non ci sono sostituzioni cieche del soggetto;
- non ci sono liste senza separatori o verbi accostati male.

Se passa formalmente ma le frasi sono brutte, non va committata come motore valido.