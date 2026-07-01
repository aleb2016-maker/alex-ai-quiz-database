# Report Model Quality Gate V1

## Stato
FAILED

## Regola
Il modello fallisce se usa pezze o se collassa nella generazione.

## Input
```json
{
  "outputs": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/diagnostics/inference_raw_diagnostics_v1/inference_raw_diagnostics_v1_outputs.json",
  "manifest": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/diagnostics/inference_raw_diagnostics_v1/inference_raw_diagnostics_v1_manifest.json"
}
```

## Regole applicate
```json
{
  "min_words": 6,
  "max_same_token_ratio": 0.35,
  "max_single_token_count": 3,
  "require_domain": true,
  "forbid_sentence_bank": true,
  "forbid_anchor_retrieval": true,
  "forbid_fallback": true,
  "forbid_hardcoded": true,
  "forbid_special_tokens": [
    "<BOS>",
    "<PAD>",
    "<UNK>",
    "<bos>",
    "<pad>",
    "<unk>"
  ]
}
```

## Sintesi
```json
{
  "outputs_total": 8,
  "failed_outputs": 8,
  "passed_outputs": 0,
  "manifest_errors": 0,
  "errors_total": 41,
  "warnings_total": 0
}
```

## Errori

- Output senza concetti di dominio.
- Collasso token: token 'stata' ripetuto 20 volte.
- Collasso ratio: token 'stata' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['stata'].
- Bigrammi ripetuti vietati: ['stata stata'].
- Output senza concetti di dominio.
- Collasso token: token 'venga' ripetuto 20 volte.
- Collasso ratio: token 'venga' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['venga'].
- Bigrammi ripetuti vietati: ['venga venga'].
- Output senza concetti di dominio.
- Collasso token: token 'privilegi' ripetuto 20 volte.
- Collasso ratio: token 'privilegi' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['privilegi'].
- Bigrammi ripetuti vietati: ['privilegi privilegi'].
- Output senza concetti di dominio.
- Collasso token: token 'rubata' ripetuto 20 volte.
- Collasso ratio: token 'rubata' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['rubata'].
- Bigrammi ripetuti vietati: ['rubata rubata'].
- Token speciali vietati in output: ['<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>'].
- Output senza concetti di dominio.
- Collasso token: token '<bos>' ripetuto 20 volte.
- Collasso ratio: token '<bos>' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['<bos>'].
- Bigrammi ripetuti vietati: ['<bos> <bos>'].
- Output senza concetti di dominio.
- Collasso token: token 'questo' ripetuto 20 volte.
- Collasso ratio: token 'questo' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['questo'].
- Bigrammi ripetuti vietati: ['questo questo'].
- Output senza concetti di dominio.
- Collasso token: token 'violato' ripetuto 20 volte.
- Collasso ratio: token 'violato' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['violato'].
- Bigrammi ripetuti vietati: ['violato violato'].
- Output senza concetti di dominio.
- Collasso token: token 'perché' ripetuto 20 volte.
- Collasso ratio: token 'perché' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['perché'].
- Bigrammi ripetuti vietati: ['perché perché'].

## Controlli per output

### 1. password

Stato: ERRORE

Testo: stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata stata

Errori:
- Output senza concetti di dominio.
- Collasso token: token 'stata' ripetuto 20 volte.
- Collasso ratio: token 'stata' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['stata'].
- Bigrammi ripetuti vietati: ['stata stata'].

### 2. password sicure

Stato: ERRORE

Testo: venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga venga

Errori:
- Output senza concetti di dominio.
- Collasso token: token 'venga' ripetuto 20 volte.
- Collasso ratio: token 'venga' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['venga'].
- Bigrammi ripetuti vietati: ['venga venga'].

### 3. sicurezza informatica

Stato: ERRORE

Testo: privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi privilegi

Errori:
- Output senza concetti di dominio.
- Collasso token: token 'privilegi' ripetuto 20 volte.
- Collasso ratio: token 'privilegi' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['privilegi'].
- Bigrammi ripetuti vietati: ['privilegi privilegi'].

### 4. backup regolari

Stato: ERRORE

Testo: rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata rubata

Errori:
- Output senza concetti di dominio.
- Collasso token: token 'rubata' ripetuto 20 volte.
- Collasso ratio: token 'rubata' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['rubata'].
- Bigrammi ripetuti vietati: ['rubata rubata'].

### 5. phishing

Stato: ERRORE

Testo: <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS> <BOS>

Errori:
- Token speciali vietati in output: ['<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>', '<BOS>'].
- Output senza concetti di dominio.
- Collasso token: token '<bos>' ripetuto 20 volte.
- Collasso ratio: token '<bos>' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['<bos>'].
- Bigrammi ripetuti vietati: ['<bos> <bos>'].

### 6. dati sensibili

Stato: ERRORE

Testo: questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo questo

Errori:
- Output senza concetti di dominio.
- Collasso token: token 'questo' ripetuto 20 volte.
- Collasso ratio: token 'questo' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['questo'].
- Bigrammi ripetuti vietati: ['questo questo'].

### 7. autenticazione a due fattori

Stato: ERRORE

Testo: violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato violato

Errori:
- Output senza concetti di dominio.
- Collasso token: token 'violato' ripetuto 20 volte.
- Collasso ratio: token 'violato' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['violato'].
- Bigrammi ripetuti vietati: ['violato violato'].

### 8. attacco ransomware

Stato: ERRORE

Testo: perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché perché

Errori:
- Output senza concetti di dominio.
- Collasso token: token 'perché' ripetuto 20 volte.
- Collasso ratio: token 'perché' occupa 1.00 dell'output.
- Duplicati immediati vietati: ['perché'].
- Bigrammi ripetuti vietati: ['perché perché'].
