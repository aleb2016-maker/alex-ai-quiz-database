# Report Inference Engine V3.1 Natural

## Stato
completed

## Obiettivo
Generare testo usando Neural Model V3.1 Natural e la catena V2.1 Natural.

## Input
```json
{
  "weights": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/model_v31_natural/neural_model_v31_natural_weights.json",
  "embeddings": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v21_natural/token_embeddings_v21_natural.json"
}
```

## Output
```json
{
  "outputs": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/inference_v31_natural/inference_engine_v31_natural_outputs.json",
  "manifest": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/inference_v31_natural/inference_engine_v31_natural_manifest.json",
  "report": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/reports/inference_engine_v31_natural_report.md"
}
```

## Impostazioni
```json
{
  "context_size": 8,
  "max_new_tokens": 18,
  "min_new_tokens": 6,
  "top_k": 45,
  "temperature": 0.65,
  "repetition_limit": 2,
  "uses_neural_model_v31_natural": true,
  "uses_vectorizer_v21_natural": true,
  "uses_dataset_v21_natural": true,
  "quality_fallback_enabled": true
}
```

## Modello
```json
{
  "vocab_size": 252,
  "vector_dim": 96
}
```

## Sintesi
```json
{
  "generations_total": 8,
  "non_empty_generations": 8,
  "avg_generated_tokens": 14.38
}
```

## Qualità
```json
{
  "dirty_tokens_found": [],
  "dirty_tokens_count": 0,
  "numeric_tokens_found": [],
  "numeric_tokens_count": 0,
  "metadata_tokens_found": [],
  "metadata_tokens_count": 0,
  "immediate_duplicate_generations": 0,
  "repeated_bigram_generations": 0,
  "punctuation_start": 0,
  "empty_generations": 0,
  "too_short_generations": 0,
  "no_domain_generations": 0,
  "fallback_used": 8
}
```

## Generazioni

### Prompt: password

una password sicura deve essere lunga, unica e difficile da indovinare.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 1,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

### Prompt: password sicure

un password manager aiuta a usare password sicure e diverse per ogni servizio.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 1,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

### Prompt: sicurezza informatica

la sicurezza informatica protegge dati, account e dispositivi da accessi non autorizzati.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 0,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

### Prompt: backup regolari

i backup regolari aiutano a recuperare informazioni dopo errori, guasti o attacchi ransomware.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 0,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

### Prompt: phishing

il phishing prova a ingannare l'utente per rubare credenziali o dati sensibili.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 0,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

### Prompt: dati sensibili

i dati sensibili devono essere protetti con attenzione e condivisi solo quando necessario.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 0,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

### Prompt: autenticazione a due fattori

l'autenticazione a due fattori aggiunge una protezione ulteriore agli account online.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 1,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

### Prompt: attacco ransomware

un attacco ransomware può cifrare i dati e rendere necessario il recupero da backup sicuri.

```json
{
  "blocked_dirty": 0,
  "blocked_numeric_code": 0,
  "blocked_metadata": 0,
  "blocked_special": 54,
  "blocked_repetition": 38,
  "blocked_punctuation": 0,
  "blocked_weak_chain": 0,
  "fallback_used": true,
  "fallback_reason": "no_domain_token",
  "early_stop": false
}
```

## Nota
Questo è codice pratico iniziale di inferenza locale.
Il fallback semantico è dichiarato quando viene usato.
