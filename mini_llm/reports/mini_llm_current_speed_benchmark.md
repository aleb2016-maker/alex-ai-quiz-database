# Mini LLM Current Speed Benchmark

- Stato: **PASS**
- Motore current: `inference_engine_v315_extended_safe_decoder`
- Checkpoint current: `checkpoint-mini-llm-current-v315-stable`

## Validazione

- Codice validatore: `0`
- Tempo validazione current: `0.6721` secondi

## Caricamento output validati

- Output totali: `28`
- Output OK caricati: `26`
- Tempo caricamento JSON: `0.000152` secondi

## Hot path risposte validate

- Round benchmark: `2000`
- Tempo medio risposta: `0.000254` ms
- Mediana risposta: `0.000250` ms
- P95 risposta: `0.000292` ms
- Max risposta: `0.000541` ms

## Limiti

- Questo benchmark misura il percorso veloce su prompt già validati.
- Non misura ancora domande libere su documenti lunghi.
- Non misura ancora riassunti progressivi.
- Serve come base tecnica per costruire il motore veloce di domande e riassunti.

## Prossimo passo tecnico

Per domande libere e riassunti veloci servono:

1. indicizzazione documento;
2. retrieval dei chunk rilevanti;
3. cache risposte;
4. cache riassunti;
5. benchmark separato per Q&A e riassunti.
