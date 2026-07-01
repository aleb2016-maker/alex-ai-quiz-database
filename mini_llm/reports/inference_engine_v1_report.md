# Report Inference Engine V1

## Stato
generated

## Modello usato
- Architettura: neural_bigram_negative_sampling_v1
- Vocabolario: 278
- Dimensione vettori: 64

## Parametri generazione
- Max nuovi token: 24
- Top K: 8
- Temperature: 0.85
- Prompt testati: 8

## Sintesi
```json
{
  "total_generations": 8,
  "non_empty_generations": 8,
  "average_generated_tokens": 10.88
}
```

## Esempi inferenza
### Prompt: password

**Generato:** sicure, strumenti e chiede con protette con per un riassunto.

**Testo completo:** password sicure, strumenti e chiede con protette con per un riassunto.

---
### Prompt: sicurezza

**Generato:** informatica

**Testo completo:** sicurezza informatica

---
### Prompt: backup

**Generato:** regolari, migliorano riconosci la frase chiara per un computer, account amministrativi? # risposta l'pulite pulite complete protette tra due

**Testo completo:** backup regolari, migliorano riconosci la frase chiara per un computer, account amministrativi? # risposta l'pulite pulite complete protette tra due

---
### Prompt: phishing

**Generato:** è l'area operativa richiesta.

**Testo completo:** phishing è l'area operativa richiesta.

---
### Prompt: dati sensibili

**Generato:** , migliorano le persone e piattaforme siti pulite attenzione.; il ransomware con complete e chiudono protette analizzato, account amministrativi, account

**Testo completo:** dati sensibili , migliorano le persone e piattaforme siti pulite attenzione.; il ransomware con complete e chiudono protette analizzato, account amministrativi, account

---
### Prompt: ransomware

**Generato:** # input quale informazione operativa.

**Testo completo:** ransomware # input quale informazione operativa.

---
### Prompt: autenticazione

**Generato:** a due fattori, migliorano elenca, strumenti viene il ransomware.

**Testo completo:** autenticazione a due fattori, migliorano elenca, strumenti viene il ransomware.

---
### Prompt: aggiornamenti

**Generato:** software

**Testo completo:** aggiornamenti software


## Nota
Questo è il primo motore di inferenza pratico del mini LLM.
Usa un modello neurale bigram, quindi produce sequenze brevi e ancora limitate.
Non è ancora un Transformer e non ha ancora memoria contestuale lunga.
