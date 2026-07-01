# Report Neural Model V2 Context

## Stato
trained

## Architettura
- Nome: neural_context_average_negative_sampling_v2
- Usa contesto multi-token: True
- Context size: 6
- Transformer: False

## Dimensioni modello
- Vocabolario: 278
- Dimensione vettori: 64
- Righe embedding input: 278
- Righe embedding output: 278

## Dati training
- Train examples usati: 5693
- Validation examples: 779
- Test examples: 587

## Iperparametri
```json
{
  "context_size": 6,
  "epochs": 7,
  "learning_rate": 0.04,
  "negative_samples": 10,
  "max_train_examples": 10000,
  "seed": 42
}
```

## Storia training
- Epoch 1: train_loss=4.231432, val_loss=2.432486, examples=5693
- Epoch 2: train_loss=2.976756, val_loss=2.204998, examples=5693
- Epoch 3: train_loss=2.66239, val_loss=2.069341, examples=5693
- Epoch 4: train_loss=2.504069, val_loss=1.978829, examples=5693
- Epoch 5: train_loss=2.355701, val_loss=1.857816, examples=5693
- Epoch 6: train_loss=2.231048, val_loss=1.769234, examples=5693
- Epoch 7: train_loss=2.110271, val_loss=1.677924, examples=5693

## Valutazione
```json
{
  "train_loss": 1.663659,
  "val_loss": 1.689848,
  "test_loss": 1.698157,
  "sample_predictions": [
    {
      "context_tokens": [
        "<BOS>",
        "password"
      ],
      "context_ids": [
        2,
        22
      ],
      "top_predictions": [
        {
          "token": "#",
          "token_id": 4,
          "score": 4.067935,
          "probability_sigmoid": 0.983175
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.003332,
          "probability_sigmoid": 0.499167
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": -0.006809,
          "probability_sigmoid": 0.498298
        },
        {
          "token": "manager",
          "token_id": 70,
          "score": -1.371964,
          "probability_sigmoid": 0.202303
        },
        {
          "token": "<EOS>",
          "token_id": 3,
          "score": -1.592,
          "probability_sigmoid": 0.169103
        },
        {
          "token": "?",
          "token_id": 36,
          "score": -1.776498,
          "probability_sigmoid": 0.144736
        },
        {
          "token": "complete",
          "token_id": 274,
          "score": -1.785217,
          "probability_sigmoid": 0.14366
        },
        {
          "token": "pulite",
          "token_id": 277,
          "score": -1.837771,
          "probability_sigmoid": 0.137315
        }
      ]
    },
    {
      "context_tokens": [
        "password",
        "sicure"
      ],
      "context_ids": [
        22,
        95
      ],
      "top_predictions": [
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 0.002726,
          "probability_sigmoid": 0.500682
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": 0.001839,
          "probability_sigmoid": 0.50046
        },
        {
          "token": ".",
          "token_id": 5,
          "score": -1.1311,
          "probability_sigmoid": 0.243958
        },
        {
          "token": "manager",
          "token_id": 70,
          "score": -1.297828,
          "probability_sigmoid": 0.214531
        },
        {
          "token": "password",
          "token_id": 22,
          "score": -1.463301,
          "probability_sigmoid": 0.187963
        },
        {
          "token": "complete",
          "token_id": 274,
          "score": -1.534091,
          "probability_sigmoid": 0.177396
        },
        {
          "token": "pulite",
          "token_id": 277,
          "score": -1.554715,
          "probability_sigmoid": 0.174406
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -1.567688,
          "probability_sigmoid": 0.172546
        }
      ]
    },
    {
      "context_tokens": [
        "backup",
        "regolari"
      ],
      "context_ids": [
        82,
        223
      ],
      "top_predictions": [
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.005042,
          "probability_sigmoid": 0.49874
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": -0.005698,
          "probability_sigmoid": 0.498576
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -1.300348,
          "probability_sigmoid": 0.214106
        },
        {
          "token": ".",
          "token_id": 5,
          "score": -1.368399,
          "probability_sigmoid": 0.202879
        },
        {
          "token": ":",
          "token_id": 12,
          "score": -1.50527,
          "probability_sigmoid": 0.181641
        },
        {
          "token": "complete",
          "token_id": 274,
          "score": -1.50531,
          "probability_sigmoid": 0.181635
        },
        {
          "token": "un",
          "token_id": 10,
          "score": -1.519075,
          "probability_sigmoid": 0.179598
        },
        {
          "token": "è",
          "token_id": 14,
          "score": -1.521897,
          "probability_sigmoid": 0.179182
        }
      ]
    },
    {
      "context_tokens": [
        "dati",
        "sensibili"
      ],
      "context_ids": [
        18,
        33
      ],
      "top_predictions": [
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 0.003567,
          "probability_sigmoid": 0.500892
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.002788,
          "probability_sigmoid": 0.499303
        },
        {
          "token": ".",
          "token_id": 5,
          "score": -0.231522,
          "probability_sigmoid": 0.442377
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -0.288503,
          "probability_sigmoid": 0.42837
        },
        {
          "token": "sensibili",
          "token_id": 33,
          "score": -0.653308,
          "probability_sigmoid": 0.342244
        },
        {
          "token": "?",
          "token_id": 36,
          "score": -0.924688,
          "probability_sigmoid": 0.284004
        },
        {
          "token": "#",
          "token_id": 4,
          "score": -1.404418,
          "probability_sigmoid": 0.197116
        },
        {
          "token": "complete",
          "token_id": 274,
          "score": -1.500722,
          "probability_sigmoid": 0.182318
        }
      ]
    },
    {
      "context_tokens": [
        "autenticazione",
        "a",
        "due"
      ],
      "context_ids": [
        53,
        25,
        58
      ],
      "top_predictions": [
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 0.015313,
          "probability_sigmoid": 0.503828
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.005683,
          "probability_sigmoid": 0.498579
        },
        {
          "token": "fattori",
          "token_id": 66,
          "score": -0.711908,
          "probability_sigmoid": 0.329177
        },
        {
          "token": "due",
          "token_id": 58,
          "score": -1.163932,
          "probability_sigmoid": 0.237954
        },
        {
          "token": "dati",
          "token_id": 18,
          "score": -1.178499,
          "probability_sigmoid": 0.235322
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -1.178827,
          "probability_sigmoid": 0.235263
        },
        {
          "token": "e",
          "token_id": 16,
          "score": -1.313232,
          "probability_sigmoid": 0.211947
        },
        {
          "token": "?",
          "token_id": 36,
          "score": -1.480053,
          "probability_sigmoid": 0.185419
        }
      ]
    },
    {
      "context_tokens": [
        "rischio",
        "phishing"
      ],
      "context_ids": [
        155,
        55
      ],
      "top_predictions": [
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.010927,
          "probability_sigmoid": 0.497268
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": -0.015035,
          "probability_sigmoid": 0.496241
        },
        {
          "token": "#",
          "token_id": 4,
          "score": -0.221695,
          "probability_sigmoid": 0.444802
        },
        {
          "token": ".",
          "token_id": 5,
          "score": -1.019591,
          "probability_sigmoid": 0.265107
        },
        {
          "token": "?",
          "token_id": 36,
          "score": -1.265311,
          "probability_sigmoid": 0.220061
        },
        {
          "token": "<EOS>",
          "token_id": 3,
          "score": -1.352322,
          "probability_sigmoid": 0.205491
        },
        {
          "token": "complete",
          "token_id": 274,
          "score": -1.450794,
          "probability_sigmoid": 0.189879
        },
        {
          "token": "pulite",
          "token_id": 277,
          "score": -1.48529,
          "probability_sigmoid": 0.18463
        }
      ]
    },
    {
      "context_tokens": [
        "attacco",
        "ransomware"
      ],
      "context_ids": [
        233,
        31
      ],
      "top_predictions": [
        {
          "token": "#",
          "token_id": 4,
          "score": 0.407592,
          "probability_sigmoid": 0.60051
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": 0.00145,
          "probability_sigmoid": 0.500362
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": -0.005094,
          "probability_sigmoid": 0.498727
        },
        {
          "token": ".",
          "token_id": 5,
          "score": -0.245361,
          "probability_sigmoid": 0.438966
        },
        {
          "token": "?",
          "token_id": 36,
          "score": -0.694595,
          "probability_sigmoid": 0.333012
        },
        {
          "token": "<EOS>",
          "token_id": 3,
          "score": -1.324961,
          "probability_sigmoid": 0.209994
        },
        {
          "token": "complete",
          "token_id": 274,
          "score": -1.474884,
          "probability_sigmoid": 0.186201
        },
        {
          "token": "per",
          "token_id": 15,
          "score": -1.57402,
          "probability_sigmoid": 0.171644
        }
      ]
    }
  ]
}
```

## Predizioni di esempio
```json
[
  {
    "context_tokens": [
      "<BOS>",
      "password"
    ],
    "context_ids": [
      2,
      22
    ],
    "top_predictions": [
      {
        "token": "#",
        "token_id": 4,
        "score": 4.067935,
        "probability_sigmoid": 0.983175
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.003332,
        "probability_sigmoid": 0.499167
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": -0.006809,
        "probability_sigmoid": 0.498298
      },
      {
        "token": "manager",
        "token_id": 70,
        "score": -1.371964,
        "probability_sigmoid": 0.202303
      },
      {
        "token": "<EOS>",
        "token_id": 3,
        "score": -1.592,
        "probability_sigmoid": 0.169103
      },
      {
        "token": "?",
        "token_id": 36,
        "score": -1.776498,
        "probability_sigmoid": 0.144736
      },
      {
        "token": "complete",
        "token_id": 274,
        "score": -1.785217,
        "probability_sigmoid": 0.14366
      },
      {
        "token": "pulite",
        "token_id": 277,
        "score": -1.837771,
        "probability_sigmoid": 0.137315
      }
    ]
  },
  {
    "context_tokens": [
      "password",
      "sicure"
    ],
    "context_ids": [
      22,
      95
    ],
    "top_predictions": [
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 0.002726,
        "probability_sigmoid": 0.500682
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": 0.001839,
        "probability_sigmoid": 0.50046
      },
      {
        "token": ".",
        "token_id": 5,
        "score": -1.1311,
        "probability_sigmoid": 0.243958
      },
      {
        "token": "manager",
        "token_id": 70,
        "score": -1.297828,
        "probability_sigmoid": 0.214531
      },
      {
        "token": "password",
        "token_id": 22,
        "score": -1.463301,
        "probability_sigmoid": 0.187963
      },
      {
        "token": "complete",
        "token_id": 274,
        "score": -1.534091,
        "probability_sigmoid": 0.177396
      },
      {
        "token": "pulite",
        "token_id": 277,
        "score": -1.554715,
        "probability_sigmoid": 0.174406
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -1.567688,
        "probability_sigmoid": 0.172546
      }
    ]
  },
  {
    "context_tokens": [
      "backup",
      "regolari"
    ],
    "context_ids": [
      82,
      223
    ],
    "top_predictions": [
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.005042,
        "probability_sigmoid": 0.49874
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": -0.005698,
        "probability_sigmoid": 0.498576
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -1.300348,
        "probability_sigmoid": 0.214106
      },
      {
        "token": ".",
        "token_id": 5,
        "score": -1.368399,
        "probability_sigmoid": 0.202879
      },
      {
        "token": ":",
        "token_id": 12,
        "score": -1.50527,
        "probability_sigmoid": 0.181641
      },
      {
        "token": "complete",
        "token_id": 274,
        "score": -1.50531,
        "probability_sigmoid": 0.181635
      },
      {
        "token": "un",
        "token_id": 10,
        "score": -1.519075,
        "probability_sigmoid": 0.179598
      },
      {
        "token": "è",
        "token_id": 14,
        "score": -1.521897,
        "probability_sigmoid": 0.179182
      }
    ]
  },
  {
    "context_tokens": [
      "dati",
      "sensibili"
    ],
    "context_ids": [
      18,
      33
    ],
    "top_predictions": [
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 0.003567,
        "probability_sigmoid": 0.500892
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.002788,
        "probability_sigmoid": 0.499303
      },
      {
        "token": ".",
        "token_id": 5,
        "score": -0.231522,
        "probability_sigmoid": 0.442377
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -0.288503,
        "probability_sigmoid": 0.42837
      },
      {
        "token": "sensibili",
        "token_id": 33,
        "score": -0.653308,
        "probability_sigmoid": 0.342244
      },
      {
        "token": "?",
        "token_id": 36,
        "score": -0.924688,
        "probability_sigmoid": 0.284004
      },
      {
        "token": "#",
        "token_id": 4,
        "score": -1.404418,
        "probability_sigmoid": 0.197116
      },
      {
        "token": "complete",
        "token_id": 274,
        "score": -1.500722,
        "probability_sigmoid": 0.182318
      }
    ]
  },
  {
    "context_tokens": [
      "autenticazione",
      "a",
      "due"
    ],
    "context_ids": [
      53,
      25,
      58
    ],
    "top_predictions": [
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 0.015313,
        "probability_sigmoid": 0.503828
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.005683,
        "probability_sigmoid": 0.498579
      },
      {
        "token": "fattori",
        "token_id": 66,
        "score": -0.711908,
        "probability_sigmoid": 0.329177
      },
      {
        "token": "due",
        "token_id": 58,
        "score": -1.163932,
        "probability_sigmoid": 0.237954
      },
      {
        "token": "dati",
        "token_id": 18,
        "score": -1.178499,
        "probability_sigmoid": 0.235322
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -1.178827,
        "probability_sigmoid": 0.235263
      },
      {
        "token": "e",
        "token_id": 16,
        "score": -1.313232,
        "probability_sigmoid": 0.211947
      },
      {
        "token": "?",
        "token_id": 36,
        "score": -1.480053,
        "probability_sigmoid": 0.185419
      }
    ]
  },
  {
    "context_tokens": [
      "rischio",
      "phishing"
    ],
    "context_ids": [
      155,
      55
    ],
    "top_predictions": [
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.010927,
        "probability_sigmoid": 0.497268
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": -0.015035,
        "probability_sigmoid": 0.496241
      },
      {
        "token": "#",
        "token_id": 4,
        "score": -0.221695,
        "probability_sigmoid": 0.444802
      },
      {
        "token": ".",
        "token_id": 5,
        "score": -1.019591,
        "probability_sigmoid": 0.265107
      },
      {
        "token": "?",
        "token_id": 36,
        "score": -1.265311,
        "probability_sigmoid": 0.220061
      },
      {
        "token": "<EOS>",
        "token_id": 3,
        "score": -1.352322,
        "probability_sigmoid": 0.205491
      },
      {
        "token": "complete",
        "token_id": 274,
        "score": -1.450794,
        "probability_sigmoid": 0.189879
      },
      {
        "token": "pulite",
        "token_id": 277,
        "score": -1.48529,
        "probability_sigmoid": 0.18463
      }
    ]
  },
  {
    "context_tokens": [
      "attacco",
      "ransomware"
    ],
    "context_ids": [
      233,
      31
    ],
    "top_predictions": [
      {
        "token": "#",
        "token_id": 4,
        "score": 0.407592,
        "probability_sigmoid": 0.60051
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": 0.00145,
        "probability_sigmoid": 0.500362
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": -0.005094,
        "probability_sigmoid": 0.498727
      },
      {
        "token": ".",
        "token_id": 5,
        "score": -0.245361,
        "probability_sigmoid": 0.438966
      },
      {
        "token": "?",
        "token_id": 36,
        "score": -0.694595,
        "probability_sigmoid": 0.333012
      },
      {
        "token": "<EOS>",
        "token_id": 3,
        "score": -1.324961,
        "probability_sigmoid": 0.209994
      },
      {
        "token": "complete",
        "token_id": 274,
        "score": -1.474884,
        "probability_sigmoid": 0.186201
      },
      {
        "token": "per",
        "token_id": 15,
        "score": -1.57402,
        "probability_sigmoid": 0.171644
      }
    ]
  }
]
```

## Nota
Questo è Neural Model V2: introduce contesto multi-token.
Non è ancora un Transformer, ma supera il limite principale del V1 bigram.
