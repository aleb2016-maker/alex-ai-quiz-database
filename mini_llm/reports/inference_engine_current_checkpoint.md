# Mini LLM Current Stable Checkpoint

## Motore corrente

- Current stable engine: `inference_engine_v315_extended_safe_decoder`
- Wrapper: `mini_llm/python/inference/inference_engine_current.py`
- Validatore current: `scripts/valida_inference_engine_current.py`
- Checkpoint tag: `checkpoint-mini-llm-v315-extended-safe`
- Commit: `40b18cf`

## Stato qualità

V3.15 è il checkpoint corrente perché:

- passa la validazione interna;
- passa il Semantic Gate V3.8.6;
- produce 26 output OK su 28 prompt;
- produce 0 output falliti dal gate;
- non promuove i due prompt senza sorgente sicura:
  - `password sicure`
  - `protezione endpoint`

## Regola operativa

Il motore current deve puntare solo a una versione già:

1. validata;
2. committata;
3. pushata;
4. taggata;
5. con repository pulito.

V3.16 non è current perché non è stata completata né committata.
