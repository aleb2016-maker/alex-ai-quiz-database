# Report Neural Model V1

## Stato
trained

## Architettura
- Nome: neural_bigram_negative_sampling_v1
- Primo modello neurale: True
- Transformer: False

## Dimensioni modello
- Vocabolario: 278
- Dimensione vettori: 64
- Righe embedding input: 278
- Righe embedding output: 278

## Dati training
- Train pairs usate: 5693
- Validation pairs: 779
- Test pairs: 587

## Iperparametri
```json
{
  "epochs": 6,
  "learning_rate": 0.05,
  "negative_samples": 8,
  "max_train_pairs": 8000,
  "seed": 42
}
```

## Storia training
- Epoch 1: train_loss=3.438585, val_loss=1.898368, pairs=5693
- Epoch 2: train_loss=2.268234, val_loss=1.529262, pairs=5693
- Epoch 3: train_loss=1.843962, val_loss=1.281706, pairs=5693
- Epoch 4: train_loss=1.568754, val_loss=1.133826, pairs=5693
- Epoch 5: train_loss=1.369689, val_loss=1.011109, pairs=5693
- Epoch 6: train_loss=1.229281, val_loss=0.960692, pairs=5693

## Valutazione
```json
{
  "train_loss": 0.905087,
  "val_loss": 0.945451,
  "test_loss": 0.970253,
  "sample_predictions": [
    {
      "input_token": "password",
      "input_id": 22,
      "top_predictions": [
        {
          "token": "manager",
          "token_id": 70,
          "score": 1.593149,
          "probability_sigmoid": 0.831059
        },
        {
          "token": "sicure",
          "token_id": 95,
          "score": 1.152189,
          "probability_sigmoid": 0.759911
        },
        {
          "token": ".",
          "token_id": 5,
          "score": 0.282675,
          "probability_sigmoid": 0.570202
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": 0.024937,
          "probability_sigmoid": 0.506234
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 0.004125,
          "probability_sigmoid": 0.501031
        },
        {
          "token": "sicura",
          "token_id": 226,
          "score": -0.447139,
          "probability_sigmoid": 0.390041
        },
        {
          "token": "principale",
          "token_id": 218,
          "score": -0.466017,
          "probability_sigmoid": 0.385559
        },
        {
          "token": "lunghe",
          "token_id": 245,
          "score": -0.771551,
          "probability_sigmoid": 0.316144
        }
      ]
    },
    {
      "input_token": "sicurezza",
      "input_id": 39,
      "top_predictions": [
        {
          "token": "informatica",
          "token_id": 51,
          "score": 1.788637,
          "probability_sigmoid": 0.85676
        },
        {
          "token": ".",
          "token_id": 5,
          "score": 0.027491,
          "probability_sigmoid": 0.506872
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 0.011458,
          "probability_sigmoid": 0.502864
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.004782,
          "probability_sigmoid": 0.498805
        },
        {
          "token": "generale",
          "token_id": 76,
          "score": -0.29229,
          "probability_sigmoid": 0.427443
        },
        {
          "token": "o",
          "token_id": 32,
          "score": -1.084079,
          "probability_sigmoid": 0.252735
        },
        {
          "token": "operativo",
          "token_id": 102,
          "score": -1.250638,
          "probability_sigmoid": 0.22259
        },
        {
          "token": "con",
          "token_id": 275,
          "score": -1.387392,
          "probability_sigmoid": 0.199824
        }
      ]
    },
    {
      "input_token": "backup",
      "input_id": 82,
      "top_predictions": [
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 0.009137,
          "probability_sigmoid": 0.502284
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.005152,
          "probability_sigmoid": 0.498712
        },
        {
          "token": "è",
          "token_id": 14,
          "score": -0.061457,
          "probability_sigmoid": 0.484641
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -1.024352,
          "probability_sigmoid": 0.264181
        },
        {
          "token": "regolari",
          "token_id": 223,
          "score": -1.111174,
          "probability_sigmoid": 0.247652
        },
        {
          "token": "serve",
          "token_id": 256,
          "score": -1.191503,
          "probability_sigmoid": 0.23299
        },
        {
          "token": "?",
          "token_id": 36,
          "score": -1.258451,
          "probability_sigmoid": 0.221241
        },
        {
          "token": "con",
          "token_id": 275,
          "score": -1.265398,
          "probability_sigmoid": 0.220046
        }
      ]
    },
    {
      "input_token": "phishing",
      "input_id": 55,
      "top_predictions": [
        {
          "token": "è",
          "token_id": 14,
          "score": 1.109618,
          "probability_sigmoid": 0.752058
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 6.9e-05,
          "probability_sigmoid": 0.500017
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.027873,
          "probability_sigmoid": 0.493032
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -0.260353,
          "probability_sigmoid": 0.435277
        },
        {
          "token": "?",
          "token_id": 36,
          "score": -0.378655,
          "probability_sigmoid": 0.406451
        },
        {
          "token": "<EOS>",
          "token_id": 3,
          "score": -1.003366,
          "probability_sigmoid": 0.26828
        },
        {
          "token": "#",
          "token_id": 4,
          "score": -1.021903,
          "probability_sigmoid": 0.264657
        },
        {
          "token": "può",
          "token_id": 189,
          "score": -1.284075,
          "probability_sigmoid": 0.216857
        }
      ]
    },
    {
      "input_token": "dati",
      "input_id": 18,
      "top_predictions": [
        {
          "token": "sensibili",
          "token_id": 33,
          "score": 2.381475,
          "probability_sigmoid": 0.915404
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": 0.010368,
          "probability_sigmoid": 0.502592
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": -0.003466,
          "probability_sigmoid": 0.499133
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -0.064225,
          "probability_sigmoid": 0.483949
        },
        {
          "token": "e",
          "token_id": 16,
          "score": -0.213221,
          "probability_sigmoid": 0.446896
        },
        {
          "token": ".",
          "token_id": 5,
          "score": -1.062182,
          "probability_sigmoid": 0.256893
        },
        {
          "token": "pulite",
          "token_id": 277,
          "score": -1.472542,
          "probability_sigmoid": 0.186557
        },
        {
          "token": "complete",
          "token_id": 274,
          "score": -1.610218,
          "probability_sigmoid": 0.166558
        }
      ]
    },
    {
      "input_token": "ransomware",
      "input_id": 31,
      "top_predictions": [
        {
          "token": ".",
          "token_id": 5,
          "score": 0.636832,
          "probability_sigmoid": 0.654037
        },
        {
          "token": "?",
          "token_id": 36,
          "score": 0.198989,
          "probability_sigmoid": 0.549584
        },
        {
          "token": "<BOS>",
          "token_id": 2,
          "score": 0.009301,
          "probability_sigmoid": 0.502325
        },
        {
          "token": "<UNK>",
          "token_id": 1,
          "score": -0.021308,
          "probability_sigmoid": 0.494673
        },
        {
          "token": "blocca",
          "token_id": 133,
          "score": -0.291806,
          "probability_sigmoid": 0.427562
        },
        {
          "token": "potrebbe",
          "token_id": 173,
          "score": -0.479693,
          "probability_sigmoid": 0.382325
        },
        {
          "token": "<EOS>",
          "token_id": 3,
          "score": -1.3052,
          "probability_sigmoid": 0.213291
        },
        {
          "token": ",",
          "token_id": 6,
          "score": -1.37046,
          "probability_sigmoid": 0.202545
        }
      ]
    }
  ]
}
```

## Esempi predizione token successivo
```json
[
  {
    "input_token": "password",
    "input_id": 22,
    "top_predictions": [
      {
        "token": "manager",
        "token_id": 70,
        "score": 1.593149,
        "probability_sigmoid": 0.831059
      },
      {
        "token": "sicure",
        "token_id": 95,
        "score": 1.152189,
        "probability_sigmoid": 0.759911
      },
      {
        "token": ".",
        "token_id": 5,
        "score": 0.282675,
        "probability_sigmoid": 0.570202
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": 0.024937,
        "probability_sigmoid": 0.506234
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 0.004125,
        "probability_sigmoid": 0.501031
      },
      {
        "token": "sicura",
        "token_id": 226,
        "score": -0.447139,
        "probability_sigmoid": 0.390041
      },
      {
        "token": "principale",
        "token_id": 218,
        "score": -0.466017,
        "probability_sigmoid": 0.385559
      },
      {
        "token": "lunghe",
        "token_id": 245,
        "score": -0.771551,
        "probability_sigmoid": 0.316144
      }
    ]
  },
  {
    "input_token": "sicurezza",
    "input_id": 39,
    "top_predictions": [
      {
        "token": "informatica",
        "token_id": 51,
        "score": 1.788637,
        "probability_sigmoid": 0.85676
      },
      {
        "token": ".",
        "token_id": 5,
        "score": 0.027491,
        "probability_sigmoid": 0.506872
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 0.011458,
        "probability_sigmoid": 0.502864
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.004782,
        "probability_sigmoid": 0.498805
      },
      {
        "token": "generale",
        "token_id": 76,
        "score": -0.29229,
        "probability_sigmoid": 0.427443
      },
      {
        "token": "o",
        "token_id": 32,
        "score": -1.084079,
        "probability_sigmoid": 0.252735
      },
      {
        "token": "operativo",
        "token_id": 102,
        "score": -1.250638,
        "probability_sigmoid": 0.22259
      },
      {
        "token": "con",
        "token_id": 275,
        "score": -1.387392,
        "probability_sigmoid": 0.199824
      }
    ]
  },
  {
    "input_token": "backup",
    "input_id": 82,
    "top_predictions": [
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 0.009137,
        "probability_sigmoid": 0.502284
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.005152,
        "probability_sigmoid": 0.498712
      },
      {
        "token": "è",
        "token_id": 14,
        "score": -0.061457,
        "probability_sigmoid": 0.484641
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -1.024352,
        "probability_sigmoid": 0.264181
      },
      {
        "token": "regolari",
        "token_id": 223,
        "score": -1.111174,
        "probability_sigmoid": 0.247652
      },
      {
        "token": "serve",
        "token_id": 256,
        "score": -1.191503,
        "probability_sigmoid": 0.23299
      },
      {
        "token": "?",
        "token_id": 36,
        "score": -1.258451,
        "probability_sigmoid": 0.221241
      },
      {
        "token": "con",
        "token_id": 275,
        "score": -1.265398,
        "probability_sigmoid": 0.220046
      }
    ]
  },
  {
    "input_token": "phishing",
    "input_id": 55,
    "top_predictions": [
      {
        "token": "è",
        "token_id": 14,
        "score": 1.109618,
        "probability_sigmoid": 0.752058
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 6.9e-05,
        "probability_sigmoid": 0.500017
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.027873,
        "probability_sigmoid": 0.493032
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -0.260353,
        "probability_sigmoid": 0.435277
      },
      {
        "token": "?",
        "token_id": 36,
        "score": -0.378655,
        "probability_sigmoid": 0.406451
      },
      {
        "token": "<EOS>",
        "token_id": 3,
        "score": -1.003366,
        "probability_sigmoid": 0.26828
      },
      {
        "token": "#",
        "token_id": 4,
        "score": -1.021903,
        "probability_sigmoid": 0.264657
      },
      {
        "token": "può",
        "token_id": 189,
        "score": -1.284075,
        "probability_sigmoid": 0.216857
      }
    ]
  },
  {
    "input_token": "dati",
    "input_id": 18,
    "top_predictions": [
      {
        "token": "sensibili",
        "token_id": 33,
        "score": 2.381475,
        "probability_sigmoid": 0.915404
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": 0.010368,
        "probability_sigmoid": 0.502592
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": -0.003466,
        "probability_sigmoid": 0.499133
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -0.064225,
        "probability_sigmoid": 0.483949
      },
      {
        "token": "e",
        "token_id": 16,
        "score": -0.213221,
        "probability_sigmoid": 0.446896
      },
      {
        "token": ".",
        "token_id": 5,
        "score": -1.062182,
        "probability_sigmoid": 0.256893
      },
      {
        "token": "pulite",
        "token_id": 277,
        "score": -1.472542,
        "probability_sigmoid": 0.186557
      },
      {
        "token": "complete",
        "token_id": 274,
        "score": -1.610218,
        "probability_sigmoid": 0.166558
      }
    ]
  },
  {
    "input_token": "ransomware",
    "input_id": 31,
    "top_predictions": [
      {
        "token": ".",
        "token_id": 5,
        "score": 0.636832,
        "probability_sigmoid": 0.654037
      },
      {
        "token": "?",
        "token_id": 36,
        "score": 0.198989,
        "probability_sigmoid": 0.549584
      },
      {
        "token": "<BOS>",
        "token_id": 2,
        "score": 0.009301,
        "probability_sigmoid": 0.502325
      },
      {
        "token": "<UNK>",
        "token_id": 1,
        "score": -0.021308,
        "probability_sigmoid": 0.494673
      },
      {
        "token": "blocca",
        "token_id": 133,
        "score": -0.291806,
        "probability_sigmoid": 0.427562
      },
      {
        "token": "potrebbe",
        "token_id": 173,
        "score": -0.479693,
        "probability_sigmoid": 0.382325
      },
      {
        "token": "<EOS>",
        "token_id": 3,
        "score": -1.3052,
        "probability_sigmoid": 0.213291
      },
      {
        "token": ",",
        "token_id": 6,
        "score": -1.37046,
        "probability_sigmoid": 0.202545
      }
    ]
  }
]
```

## Nota
Questo è un primo modello neurale pratico. Non è ancora un Transformer e non è ancora un LLM completo.
Serve a verificare che la pipeline possa addestrare pesi numerici partendo da token e vettori.
