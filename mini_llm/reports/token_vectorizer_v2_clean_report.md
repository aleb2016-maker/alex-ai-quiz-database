# Report Token Vectorizer V2 Clean

## Stato
built

## Obiettivo
Vectorizzare il Dataset V2 Clean senza sovrascrivere il Vectorizer V1.

## Input
```json
{
  "train": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v2_clean_train.jsonl",
  "val": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v2_clean_val.jsonl",
  "test": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v2_clean_test.jsonl"
}
```

## Output
```json
{
  "vocab": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v2/token_vocab_v2_clean.json",
  "embeddings": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v2/token_embeddings_v2_clean.json",
  "train_sequences": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v2/token_sequences_v2_clean_train.jsonl",
  "val_sequences": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v2/token_sequences_v2_clean_val.jsonl",
  "test_sequences": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v2/token_sequences_v2_clean_test.jsonl",
  "manifest": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v2/token_vectorizer_v2_clean_manifest.json",
  "report": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/reports/token_vectorizer_v2_clean_report.md"
}
```

## Impostazioni
```json
{
  "max_length": 128,
  "vector_dim": 96,
  "min_frequency": 1,
  "special_tokens": [
    "<PAD>",
    "<UNK>",
    "<BOS>",
    "<EOS>"
  ],
  "uses_clean_dataset_v2": true
}
```

## Record
```json
{
  "train": 353,
  "val": 65,
  "test": 58,
  "total": 476
}
```

## Vocabolario
```json
{
  "vocab_size": 430,
  "dirty_tokens_in_vocab": [],
  "top_tokens": [
    [
      ".",
      615
    ],
    [
      "-",
      494
    ],
    [
      ",",
      273
    ],
    [
      ":",
      160
    ],
    [
      "v1",
      155
    ],
    [
      "è",
      147
    ],
    [
      "ke",
      144
    ],
    [
      "dataset",
      144
    ],
    [
      "dati",
      121
    ],
    [
      "un",
      114
    ],
    [
      "e",
      110
    ],
    [
      "una",
      101
    ],
    [
      "la",
      100
    ],
    [
      "password",
      96
    ],
    [
      "account",
      94
    ],
    [
      "a",
      93
    ],
    [
      "?",
      89
    ],
    [
      "informazione",
      86
    ],
    [
      "il",
      83
    ],
    [
      "sensibili",
      82
    ],
    [
      "di",
      80
    ],
    [
      "ransomware",
      74
    ],
    [
      "per",
      73
    ],
    [
      "l",
      67
    ],
    [
      "'",
      67
    ],
    [
      "alla",
      67
    ],
    [
      "o",
      67
    ],
    [
      "in",
      64
    ],
    [
      "questa",
      59
    ],
    [
      "rispondi",
      55
    ]
  ]
}
```

## Qualità
```json
{
  "sequences_total": 476,
  "dirty_token_hits": 0,
  "immediate_duplicates": 0,
  "truncated_sequences": 0,
  "unk_count": 0,
  "unk_ratio": 0.0,
  "avg_original_length": 17.05,
  "max_original_length": 72,
  "avg_token_count": 15.05,
  "vocab_unique_raw_tokens": 426
}
```

## Nota
Questo blocco prepara la base numerica pulita per Neural Model V3.
