# Validazione Inference Engine V3.15 Extended Safe Decoder

- Stato finale: **PASS**
- Codice inference: `0`
- Codice semantic gate V3.8.6: `0`
- Output totali: `28`
- Output OK interni: `26`
- Output falliti interni: `2`
- Semantic Gate status: `PASS`
- Output controllati dal gate: `26`
- Output falliti dal gate: `0`

## Regola

V3.15 è accettabile solo se:

- produce almeno 10 output OK;
- non copia identica dal corpus;
- non ha score negativi marcati OK;
- passa Semantic Gate V3.8.6;
- gli output OK sono buoni anche a controllo umano.