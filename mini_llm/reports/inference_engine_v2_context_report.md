# Report Inference Engine V2 Context

## Stato
generated

## Modello usato
- Architettura: neural_context_average_negative_sampling_v2
- Usa contesto multi-token: True
- Context size: 6
- Vocabolario: 278
- Dimensione vettori: 64

## Parametri generazione
- Max nuovi token: 28
- Top K: 8
- Temperature: 0.8
- Prompt testati: 8

## Sintesi
```json
{
  "total_generations": 8,
  "non_empty_generations": 8,
  "average_generated_tokens": 25.62,
  "average_context_steps": 26.0
}
```

## Esempi inferenza V2
### Prompt: password

**Generato:** . # # input: output area operativa operativa. # # # input risposta collegate: password manager, complete pulite e, amministrativi e,,

**Testo completo:** password . # # input: output area operativa operativa. # # # input risposta collegate: password manager, complete pulite e, amministrativi e,,

**Context size:** 6

---
### Prompt: password sicure

**Generato:** con, sistemi strumenti account pulite e pulite attenzione complete con per per un riassunto. # # # risposta input il: è a? complete complete

**Testo completo:** password sicure con, sistemi strumenti account pulite e pulite attenzione complete con per per un riassunto. # # # risposta input il: è a? complete complete

**Context size:** 6

---
### Prompt: sicurezza informatica

**Generato:** # il è ransomware attenzione un attenzione con dati pulite. # # # risposta non trasforma una l un attenzione.

**Testo completo:** sicurezza informatica # il è ransomware attenzione un attenzione con dati pulite. # # # risposta non trasforma una l un attenzione.

**Context size:** 6

---
### Prompt: backup regolari

**Generato:** . # # risposta gli un una con pulite per un riassunto riassunto # # # istruzione alla riscrivi usando in una micro forma - per riassunto.

**Testo completo:** backup regolari . # # risposta gli un una con pulite per un riassunto riassunto # # # istruzione alla riscrivi usando in una micro forma - per riassunto.

**Context size:** 6

---
### Prompt: phishing

**Generato:** # istruzione frase alla domanda la micro operativa pulite pulita complete e. # # trasforma quale informazione operativa: pulita pulite pulite. #

**Testo completo:** phishing # istruzione frase alla domanda la micro operativa pulite pulita complete e. # # trasforma quale informazione operativa: pulita pulite pulite. #

**Context size:** 6

---
### Prompt: dati sensibili

**Generato:** o, account, e amministrativi, sistemi e e pulite e per riassunto complete. # output

**Testo completo:** dati sensibili o, account, e amministrativi, sistemi e e pulite e per riassunto complete. # output

**Context size:** 6

---
### Prompt: autenticazione a due

**Generato:** dati fattori,, account amministrativi,,, sistemi, amministrativi amministrativi,, sistemi,, amministrativi e sistemi di pagamento. # # input area

**Testo completo:** autenticazione a due dati fattori,, account amministrativi,,, sistemi, amministrativi amministrativi,, sistemi,, amministrativi e sistemi di pagamento. # # input area

**Context size:** 6

---
### Prompt: attacco ransomware

**Generato:** ? # # # # risposta una trasforma la la una micro informazione conoscenza operativa in chiara per e pulite con con attenzione. # # input quale

**Testo completo:** attacco ransomware ? # # # # risposta una trasforma la la una micro informazione conoscenza operativa in chiara per e pulite con con attenzione. # # input quale

**Context size:** 6


## Nota
Questo è il motore di inferenza V2 con contesto multi-token.
Non è ancora un Transformer, ma usa gli ultimi token per predire il token successivo.
