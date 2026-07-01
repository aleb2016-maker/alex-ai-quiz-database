# Report Neural Model V3.1 Natural

## Stato
trained

## Obiettivo
Addestrare un modello neurale sulla catena V2.1 Natural.

## Input
```json
{
  "vocab": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v21_natural/token_vocab_v21_natural.json",
  "embeddings": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v21_natural/token_embeddings_v21_natural.json",
  "train_sequences": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v21_natural/token_sequences_v21_natural_train.jsonl",
  "val_sequences": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v21_natural/token_sequences_v21_natural_val.jsonl",
  "test_sequences": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/vectorized_v21_natural/token_sequences_v21_natural_test.jsonl"
}
```

## Output
```json
{
  "weights": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/model_v31_natural/neural_model_v31_natural_weights.json",
  "manifest": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/model_v31_natural/neural_model_v31_natural_manifest.json",
  "sample_predictions": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/model_v31_natural/neural_model_v31_natural_sample_predictions.json",
  "report": "/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/reports/neural_model_v31_natural_report.md"
}
```

## Impostazioni
```json
{
  "context_size": 8,
  "epochs": 10,
  "learning_rate": 0.035,
  "negative_samples": 14,
  "seed": 42,
  "uses_vectorizer_v21_natural": true,
  "uses_dataset_v21_natural": true
}
```

## Modello
```json
{
  "vocab_size": 252,
  "vector_dim": 96,
  "trainable_output_embeddings": true,
  "trainable_output_bias": true,
  "input_embeddings_trainable": false,
  "architecture": "weighted_context_negative_sampling"
}
```

## Esempi
```json
{
  "train": 1731,
  "val": 152,
  "test": 180
}
```

## Loss
```json
{
  "train_sampled_final": 0.233658,
  "val_full_softmax_final": 5.728071,
  "test_full_softmax_final": 5.727027,
  "epoch_history": [
    {
      "epoch": 1,
      "learning_rate": 0.035,
      "train_sampled_loss": 0.450437,
      "val_full_softmax_loss": 6.125505
    },
    {
      "epoch": 2,
      "learning_rate": 0.0322,
      "train_sampled_loss": 0.318617,
      "val_full_softmax_loss": 6.0945
    },
    {
      "epoch": 3,
      "learning_rate": 0.029624,
      "train_sampled_loss": 0.28354,
      "val_full_softmax_loss": 6.013711
    },
    {
      "epoch": 4,
      "learning_rate": 0.02725408,
      "train_sampled_loss": 0.266122,
      "val_full_softmax_loss": 5.954925
    },
    {
      "epoch": 5,
      "learning_rate": 0.02507375,
      "train_sampled_loss": 0.256119,
      "val_full_softmax_loss": 5.906703
    },
    {
      "epoch": 6,
      "learning_rate": 0.02306785,
      "train_sampled_loss": 0.249517,
      "val_full_softmax_loss": 5.847087
    },
    {
      "epoch": 7,
      "learning_rate": 0.02122243,
      "train_sampled_loss": 0.244174,
      "val_full_softmax_loss": 5.823147
    },
    {
      "epoch": 8,
      "learning_rate": 0.01952463,
      "train_sampled_loss": 0.240557,
      "val_full_softmax_loss": 5.772786
    },
    {
      "epoch": 9,
      "learning_rate": 0.01796266,
      "train_sampled_loss": 0.237385,
      "val_full_softmax_loss": 5.746562
    },
    {
      "epoch": 10,
      "learning_rate": 0.01652565,
      "train_sampled_loss": 0.235005,
      "val_full_softmax_loss": 5.728071
    }
  ]
}
```

## Qualità
```json
{
  "sample_predictions": 8,
  "empty_predictions": 0,
  "dirty_prediction_tokens": [],
  "numeric_prediction_tokens": [],
  "metadata_prediction_tokens": []
}
```

## Predizioni campione
```json
[
  {
    "prompt": "password",
    "context_tokens": [
      "password"
    ],
    "top_predictions": [
      {
        "token_id": 245,
        "token": "stata",
        "score": 0.254399,
        "probability_topk": 0.159859
      },
      {
        "token_id": 228,
        "token": "privilegi",
        "score": 0.07788,
        "probability_topk": 0.133991
      },
      {
        "token_id": 248,
        "token": "venga",
        "score": 0.04441,
        "probability_topk": 0.12958
      },
      {
        "token_id": 239,
        "token": "rubata",
        "score": -0.025218,
        "probability_topk": 0.120865
      },
      {
        "token_id": 226,
        "token": "perché",
        "score": -0.039119,
        "probability_topk": 0.119196
      },
      {
        "token_id": 251,
        "token": "violato",
        "score": -0.047538,
        "probability_topk": 0.118197
      },
      {
        "token_id": 232,
        "token": "prova",
        "score": -0.118691,
        "probability_topk": 0.110079
      },
      {
        "token_id": 233,
        "token": "questo",
        "score": -0.135609,
        "probability_topk": 0.108233
      }
    ]
  },
  {
    "prompt": "password sicure",
    "context_tokens": [
      "password",
      "sicure"
    ],
    "top_predictions": [
      {
        "token_id": 248,
        "token": "venga",
        "score": 0.047447,
        "probability_topk": 0.132175
      },
      {
        "token_id": 245,
        "token": "stata",
        "score": 0.045474,
        "probability_topk": 0.131915
      },
      {
        "token_id": 239,
        "token": "rubata",
        "score": 0.012804,
        "probability_topk": 0.127675
      },
      {
        "token_id": 241,
        "token": "servono",
        "score": 0.005797,
        "probability_topk": 0.126783
      },
      {
        "token_id": 226,
        "token": "perché",
        "score": -0.033091,
        "probability_topk": 0.121947
      },
      {
        "token_id": 228,
        "token": "privilegi",
        "score": -0.039155,
        "probability_topk": 0.12121
      },
      {
        "token_id": 233,
        "token": "questo",
        "score": -0.056185,
        "probability_topk": 0.119163
      },
      {
        "token_id": 251,
        "token": "violato",
        "score": -0.056455,
        "probability_topk": 0.119131
      }
    ]
  },
  {
    "prompt": "sicurezza informatica",
    "context_tokens": [
      "sicurezza",
      "informatica"
    ],
    "top_predictions": [
      {
        "token_id": 228,
        "token": "privilegi",
        "score": 0.180013,
        "probability_topk": 0.146869
      },
      {
        "token_id": 241,
        "token": "servono",
        "score": 0.117886,
        "probability_topk": 0.138022
      },
      {
        "token_id": 251,
        "token": "violato",
        "score": -0.012952,
        "probability_topk": 0.121095
      },
      {
        "token_id": 226,
        "token": "perché",
        "score": -0.015729,
        "probability_topk": 0.120759
      },
      {
        "token_id": 239,
        "token": "rubata",
        "score": -0.026448,
        "probability_topk": 0.119472
      },
      {
        "token_id": 245,
        "token": "stata",
        "score": -0.030558,
        "probability_topk": 0.118982
      },
      {
        "token_id": 232,
        "token": "prova",
        "score": -0.034053,
        "probability_topk": 0.118567
      },
      {
        "token_id": 248,
        "token": "venga",
        "score": -0.053923,
        "probability_topk": 0.116234
      }
    ]
  },
  {
    "prompt": "backup regolari",
    "context_tokens": [
      "backup",
      "regolari"
    ],
    "top_predictions": [
      {
        "token_id": 239,
        "token": "rubata",
        "score": 0.094424,
        "probability_topk": 0.132569
      },
      {
        "token_id": 241,
        "token": "servono",
        "score": 0.073618,
        "probability_topk": 0.129839
      },
      {
        "token_id": 245,
        "token": "stata",
        "score": 0.053516,
        "probability_topk": 0.127255
      },
      {
        "token_id": 251,
        "token": "violato",
        "score": 0.029012,
        "probability_topk": 0.124175
      },
      {
        "token_id": 228,
        "token": "privilegi",
        "score": 0.021087,
        "probability_topk": 0.123195
      },
      {
        "token_id": 219,
        "token": "elevati",
        "score": 0.007793,
        "probability_topk": 0.121568
      },
      {
        "token_id": 226,
        "token": "perché",
        "score": 0.001544,
        "probability_topk": 0.12081
      },
      {
        "token_id": 233,
        "token": "questo",
        "score": -0.00028,
        "probability_topk": 0.12059
      }
    ]
  },
  {
    "prompt": "phishing",
    "context_tokens": [
      "phishing"
    ],
    "top_predictions": [
      {
        "token_id": 226,
        "token": "perché",
        "score": 0.089204,
        "probability_topk": 0.137677
      },
      {
        "token_id": 232,
        "token": "prova",
        "score": 0.074411,
        "probability_topk": 0.135656
      },
      {
        "token_id": 248,
        "token": "venga",
        "score": -0.003497,
        "probability_topk": 0.125488
      },
      {
        "token_id": 245,
        "token": "stata",
        "score": -0.015239,
        "probability_topk": 0.124023
      },
      {
        "token_id": 228,
        "token": "privilegi",
        "score": -0.026216,
        "probability_topk": 0.122669
      },
      {
        "token_id": 219,
        "token": "elevati",
        "score": -0.042749,
        "probability_topk": 0.120658
      },
      {
        "token_id": 233,
        "token": "questo",
        "score": -0.072717,
        "probability_topk": 0.117096
      },
      {
        "token_id": 239,
        "token": "rubata",
        "score": -0.075818,
        "probability_topk": 0.116733
      }
    ]
  },
  {
    "prompt": "dati sensibili",
    "context_tokens": [
      "dati",
      "sensibili"
    ],
    "top_predictions": [
      {
        "token_id": 233,
        "token": "questo",
        "score": 0.1565,
        "probability_topk": 0.136836
      },
      {
        "token_id": 219,
        "token": "elevati",
        "score": 0.098758,
        "probability_topk": 0.129158
      },
      {
        "token_id": 241,
        "token": "servono",
        "score": 0.073809,
        "probability_topk": 0.125976
      },
      {
        "token_id": 245,
        "token": "stata",
        "score": 0.0601,
        "probability_topk": 0.12426
      },
      {
        "token_id": 232,
        "token": "prova",
        "score": 0.051903,
        "probability_topk": 0.123246
      },
      {
        "token_id": 226,
        "token": "perché",
        "score": 0.039593,
        "probability_topk": 0.121738
      },
      {
        "token_id": 251,
        "token": "violato",
        "score": 0.035605,
        "probability_topk": 0.121254
      },
      {
        "token_id": 239,
        "token": "rubata",
        "score": 0.004436,
        "probability_topk": 0.117533
      }
    ]
  },
  {
    "prompt": "autenticazione a due fattori",
    "context_tokens": [
      "autenticazione",
      "a",
      "due",
      "fattori"
    ],
    "top_predictions": [
      {
        "token_id": 251,
        "token": "violato",
        "score": 0.073363,
        "probability_topk": 0.132998
      },
      {
        "token_id": 248,
        "token": "venga",
        "score": 0.050468,
        "probability_topk": 0.129988
      },
      {
        "token_id": 245,
        "token": "stata",
        "score": 0.043286,
        "probability_topk": 0.129058
      },
      {
        "token_id": 233,
        "token": "questo",
        "score": 0.005848,
        "probability_topk": 0.124315
      },
      {
        "token_id": 232,
        "token": "prova",
        "score": -0.005168,
        "probability_topk": 0.122953
      },
      {
        "token_id": 226,
        "token": "perché",
        "score": -0.021966,
        "probability_topk": 0.120905
      },
      {
        "token_id": 241,
        "token": "servono",
        "score": -0.023602,
        "probability_topk": 0.120708
      },
      {
        "token_id": 228,
        "token": "privilegi",
        "score": -0.037229,
        "probability_topk": 0.119074
      }
    ]
  },
  {
    "prompt": "attacco ransomware",
    "context_tokens": [
      "attacco",
      "ransomware"
    ],
    "top_predictions": [
      {
        "token_id": 226,
        "token": "perché",
        "score": 0.156485,
        "probability_topk": 0.144184
      },
      {
        "token_id": 219,
        "token": "elevati",
        "score": 0.086222,
        "probability_topk": 0.1344
      },
      {
        "token_id": 248,
        "token": "venga",
        "score": 0.035338,
        "probability_topk": 0.127733
      },
      {
        "token_id": 232,
        "token": "prova",
        "score": 0.005241,
        "probability_topk": 0.123946
      },
      {
        "token_id": 228,
        "token": "privilegi",
        "score": -0.01767,
        "probability_topk": 0.121138
      },
      {
        "token_id": 233,
        "token": "questo",
        "score": -0.037631,
        "probability_topk": 0.118744
      },
      {
        "token_id": 245,
        "token": "stata",
        "score": -0.04569,
        "probability_topk": 0.117791
      },
      {
        "token_id": 241,
        "token": "servono",
        "score": -0.095531,
        "probability_topk": 0.112064
      }
    ]
  }
]
```

## Nota
Questo è un modello neurale pratico iniziale, non ancora un Transformer.
Serve come base per Inference Engine V3.1 Natural.
