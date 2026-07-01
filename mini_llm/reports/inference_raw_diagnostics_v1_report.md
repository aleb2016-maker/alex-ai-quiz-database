# Report Inference Raw Diagnostics V1

## Stato
diagnosed

## Regola
Nessun fallback, nessuna frase hardcoded, nessuna ancora, nessun sentence bank.

## Impostazioni
```json
{
  "generation_mode": "raw_model_only",
  "fallback_enabled": false,
  "hardcoded_sentences_enabled": false,
  "sentence_bank_enabled": false,
  "anchor_retrieval_enabled": false,
  "filters_enabled": false,
  "max_new_tokens": 20,
  "top_k_trace": 10,
  "temperature": 1.0
}
```

## Sintesi
```json
{
  "prompts_total": 8,
  "empty_generations": 0,
  "generations_with_repetition": 8,
  "generations_with_dirty_tokens": 0,
  "generations_with_numeric_tokens": 0,
  "generations_with_metadata_tokens": 0,
  "generations_without_domain_tokens": 8,
  "avg_generated_tokens": 20.0
}
```

## Diagnostica globale
```json
{
  "empty_generations": 0,
  "generations_with_repetition": 8,
  "generations_with_dirty_tokens": 0,
  "generations_with_numeric_tokens": 0,
  "generations_with_metadata_tokens": 0,
  "generations_without_domain_tokens": 8,
  "avg_generated_tokens": 20.0,
  "probable_causes_summary": {
    "La generazione non contiene concetti di dominio.": 8,
    "Il modello tende a ripetere token o gruppi di token.": 8
  }
}
```

## Generazioni raw

### Prompt: password

Output raw: stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata",
  "stata"
]
```

### Prompt: password sicure

Output raw: venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga",
  "venga"
]
```

### Prompt: sicurezza informatica

Output raw: privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi",
  "privilegi"
]
```

### Prompt: backup regolari

Output raw: rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata",
  "rubata"
]
```

### Prompt: phishing

Output raw: <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS>

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>",
  "<BOS>"
]
```

### Prompt: dati sensibili

Output raw: questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo",
  "questo"
]
```

### Prompt: autenticazione a due fattori

Output raw: violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato",
  "violato"
]
```

### Prompt: attacco ransomware

Output raw: perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché

Problemi rilevati:
- La generazione non contiene concetti di dominio.
- Il modello tende a ripetere token o gruppi di token.

Token raw:
```json
[
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché",
  "perché"
]
```
