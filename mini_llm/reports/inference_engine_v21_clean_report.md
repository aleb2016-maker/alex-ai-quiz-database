# Report Inference Engine V2.1 Clean

## Stato
generated

## Modello usato
- Architettura: neural_context_average_negative_sampling_v2
- Usa contesto multi-token: True
- Context size: 6
- Vocabolario: 278
- Dimensione vettori: 64

## Parametri generazione
- Max nuovi token: 16
- Min nuovi token: 3
- Top K: 40
- Temperature: 0.5
- Clean decoding: True

## Sintesi
```json
{
  "total_generations": 8,
  "non_empty_generations": 8,
  "average_generated_tokens": 5.12,
  "average_removed_candidates": 24.5,
  "quality": {
    "dirty_tokens_found": 0,
    "immediate_duplicates_found": 0,
    "punctuation_start_found": 0
  }
}
```

## Filtri attivi
```json
{
  "blocked_generation_tokens": [
    "<BOS>",
    "<PAD>",
    "<UNK>"
  ],
  "dirty_tokens": [
    "#",
    "analizzato",
    "area",
    "collegate",
    "completa",
    "complete",
    "domanda",
    "forma",
    "input",
    "istruzione",
    "micro",
    "operativa",
    "output",
    "pulita",
    "pulite",
    "richiesta",
    "riscrivi",
    "risposta",
    "trasforma"
  ],
  "soft_dirty_tokens": [
    "chiara",
    "chiare",
    "frase",
    "riassunto",
    "utile"
  ],
  "punctuation_tokens": [
    "!",
    "'",
    "(",
    ")",
    ",",
    "-",
    ".",
    ":",
    ";",
    "?",
    "’"
  ],
  "rules": [
    "no dirty tokens",
    "no immediate duplicate tokens",
    "no punctuation as first generated token",
    "no excessive punctuation",
    "early stop after useful sentence end",
    "shorter generation than raw V2"
  ]
}
```

## Esempi inferenza pulita
### Prompt: password

**Generato pulito:** manager, strumenti account amministrativi sistemi

**Testo completo:** password manager, strumenti account amministrativi sistemi

**Context size:** 6

**Filtri applicati:** removed=36, dirty=23, repeat=6, punct=7, semantic_fallback=False

---
### Prompt: password sicure

**Generato pulito:** manager, strumenti un account online.

**Testo completo:** password sicure manager, strumenti un account online.

**Context size:** 6

**Filtri applicati:** removed=34, dirty=22, repeat=6, punct=6, semantic_fallback=False

---
### Prompt: sicurezza informatica

**Generato pulito:** sicurezza informatica dati account

**Testo completo:** sicurezza informatica sicurezza informatica dati account

**Context size:** 6

**Filtri applicati:** removed=9, dirty=5, repeat=0, punct=4, semantic_fallback=True

---
### Prompt: backup regolari

**Generato pulito:** è un password attenzione manager.

**Testo completo:** backup regolari è un password attenzione manager.

**Context size:** 6

**Filtri applicati:** removed=30, dirty=19, repeat=4, punct=7, semantic_fallback=False

---
### Prompt: phishing

**Generato pulito:** phishing dati sensibili credenziali

**Testo completo:** phishing phishing dati sensibili credenziali

**Context size:** 6

**Filtri applicati:** removed=10, dirty=5, repeat=0, punct=5, semantic_fallback=True

---
### Prompt: dati sensibili

**Generato pulito:** sensibili, sistemi, account strumenti attenzione e.

**Testo completo:** dati sensibili sensibili, sistemi, account strumenti attenzione e.

**Context size:** 6

**Filtri applicati:** removed=50, dirty=30, repeat=12, punct=8, semantic_fallback=False

---
### Prompt: autenticazione a due fattori

**Generato pulito:** fattori

**Testo completo:** autenticazione a due fattori fattori

**Context size:** 6

**Filtri applicati:** removed=16, dirty=8, repeat=1, punct=7, semantic_fallback=False

---
### Prompt: attacco ransomware

**Generato pulito:** ransomware malware dati backup

**Testo completo:** attacco ransomware ransomware malware dati backup

**Context size:** 6

**Filtri applicati:** removed=11, dirty=6, repeat=0, punct=5, semantic_fallback=True


## Nota
Questo blocco non riaddestra il modello.
Migliora il decoding dei pesi V2 con filtri qualità e stop anticipato.
