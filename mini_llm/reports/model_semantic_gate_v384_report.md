# Model Semantic Gate V3.8.4 Report

- Status: **PASS**
- Output controllati: **8**
- Passati: **8**
- Falliti: **0**

## Nuove regole V3.8.2

- Richiede un verbo finito reale, non solo infinito o participio.
- Rimuove il falso positivo dei suffissi generici tipo `ano`, quindi `umano` non vale come verbo.
- Boccia frasi con `quando` senza proposizione principale prima.
- Boccia liste di parole/keyword senza struttura.
- Boccia primo verbo troppo lontano dall'inizio.
- Boccia troppi concetti pieni consecutivi prima del verbo.
- Boccia copula + infinito, es. `sono usare`.
- Boccia accordi falsi, es. `sono collegato` con soggetto plurale.
- Boccia definizioni del tema sbagliato, es. dati sensibili definiti come phishing.
- Boccia ruoli semantici invertiti, es. ransomware che serve a recuperare.
- Boccia soggetti sostituiti male da una sorgente di altro dominio, es. password che eredita il ruolo del password manager.
- Boccia sorgenti da sezioni operative numerate, es. `sezione 001.1 descrive`.
- Boccia verbi d'azione consecutivi senza connettivo, es. `blocca cifra`.
- Boccia liste lunghe senza separatori leggibili.

## Output falliti

Nessun output fallito.