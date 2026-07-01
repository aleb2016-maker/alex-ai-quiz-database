# Report Knowledge Dataset Builder V2.1 Natural

## Stato
built

## Obiettivo
Creare un dataset naturale più severo per rimuovere metadati, ID, codici e frasi progettuali.

## Input
```json
{
  "knowledge_engine_v14": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v14_semantic_output.json",
  "knowledge_dataset_v2_clean": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v2_clean.jsonl"
}
```

## Output
```json
{
  "full": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v21_natural.jsonl",
  "train": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v21_natural_train.jsonl",
  "val": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v21_natural_val.jsonl",
  "test": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v21_natural_test.jsonl",
  "manifest": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/training/knowledge_dataset_v21_natural_manifest.json",
  "report": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/reports/knowledge_dataset_builder_v21_natural_report.md"
}
```

## Record
```json
{
  "full": 98,
  "train": 80,
  "val": 9,
  "test": 9
}
```

## Pulizia
```json
{
  "dirty_tokens": [
    "#",
    "alessandro",
    "alex",
    "analizzato",
    "answer",
    "area",
    "aree_operative",
    "barbarossa",
    "builder",
    "clean",
    "clean_id",
    "collegata",
    "collegate",
    "collegato",
    "completa",
    "complete",
    "completion",
    "crea",
    "creare",
    "dataset",
    "domanda",
    "forma",
    "frasi_rilevanti",
    "genera",
    "generare",
    "input",
    "instruction",
    "istruzione",
    "json",
    "knowledge_engine",
    "knowledge_engine_v14",
    "manifest",
    "micro",
    "micro_informazioni",
    "operativa",
    "operative",
    "output",
    "prompt",
    "pulita",
    "pulite",
    "question",
    "record",
    "relazione_operativa",
    "relazioni_operative",
    "richiesta",
    "richiesto",
    "riscrivi",
    "risposta",
    "source",
    "source_clean_id",
    "source_record",
    "source_split",
    "source_task",
    "training",
    "training_originale",
    "trasforma",
    "vectorizer"
  ],
  "dirty_phrases": [
    "area operativa",
    "dataset builder",
    "domanda studio",
    "e collegata a",
    "e collegato a",
    "frase chiara",
    "frase utile",
    "in forma chiara",
    "informazione operativa richiesta",
    "knowledge engine",
    "micro forma",
    "neural model",
    "per un riassunto",
    "quale informazione",
    "relazione operativa",
    "relazioni operative",
    "riscrivi usando",
    "risposta guida",
    "testo analizzato",
    "token vectorizer",
    "training originale",
    "trasforma usando",
    "è collegata a",
    "è collegato a"
  ],
  "min_words": 4,
  "max_words": 34,
  "stats": {
    "source_records_total": 579,
    "candidate_texts_total": 579,
    "accepted_texts_total": 98,
    "discarded_empty": 6,
    "discarded_short": 254,
    "discarded_too_long": 24,
    "discarded_dirty": 112,
    "discarded_not_natural": 28,
    "discarded_duplicate": 57,
    "synthetic_natural_added": 16
  }
}
```

## Qualità
```json
{
  "records": 98,
  "dirty_token_hits": 0,
  "numeric_code_hits": 0,
  "metadata_shape_hits": 0,
  "punctuation_start": 0,
  "immediate_duplicates": 0,
  "repeated_bigrams": 0,
  "avg_word_count": 16.92,
  "min_word_count": 4,
  "max_word_count": 34,
  "top_tokens": [
    [
      ".",
      163
    ],
    [
      ",",
      103
    ],
    [
      "e",
      61
    ],
    [
      "un",
      44
    ],
    [
      "dati",
      43
    ],
    [
      "una",
      41
    ],
    [
      "password",
      41
    ],
    [
      "il",
      35
    ],
    [
      "l",
      35
    ],
    [
      "'",
      35
    ],
    [
      "di",
      33
    ],
    [
      "in",
      33
    ],
    [
      "è",
      32
    ],
    [
      "a",
      28
    ],
    [
      "o",
      28
    ],
    [
      "ransomware",
      28
    ],
    [
      "account",
      27
    ],
    [
      "la",
      26
    ],
    [
      "per",
      26
    ],
    [
      "sensibili",
      23
    ],
    [
      "voce",
      22
    ],
    [
      "sicurezza",
      21
    ],
    [
      "malware",
      18
    ],
    [
      "software",
      18
    ],
    [
      "questa",
      18
    ]
  ]
}
```

## Nota
Questo dataset è più piccolo ma più naturale.
Serve per rigenerare Vectorizer V2.1, Neural Model V3.1 e Inference V3.1.
