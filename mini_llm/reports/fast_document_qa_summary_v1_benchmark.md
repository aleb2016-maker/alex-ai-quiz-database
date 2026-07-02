# Fast Document Q&A + Summary V1 Benchmark

- Stato: **PASS**
- Caratteri documento simulato: `62209`
- Chunk creati: `100`

## Performance

- Build indice: `3.604792` ms
- Q&A media: `0.409875` ms
- Q&A mediana: `0.366000` ms
- Q&A P95: `0.538791` ms
- Q&A max: `0.538791` ms
- Summary interno: `3.261833` ms
- Summary totale: `3.270334` ms

## Qualità Q&A

- Domande testate: `10`
- Risposte OK: `10`

## Esempi Q&A

### Che cosa fa il phishing?

- Status: `OK`
- Tempo: `0.311125` ms
- Risposta: `Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.`

### A cosa servono i backup regolari?

- Status: `OK`
- Tempo: `0.326875` ms
- Risposta: `I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.`

### Come funziona l'autenticazione a due fattori?

- Status: `OK`
- Tempo: `0.360459` ms
- Risposta: `L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.`

### Che cos'è il ransomware?

- Status: `OK`
- Tempo: `0.363917` ms
- Risposta: `Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.`

### Perché sono importanti gli aggiornamenti software?

- Status: `OK`
- Tempo: `0.368083` ms
- Risposta: `Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.`

### Che cosa fa un password manager?

- Status: `OK`
- Tempo: `0.471416` ms
- Risposta: `Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.`

### Cosa possono causare le credenziali rubate?

- Status: `OK`
- Tempo: `0.509000` ms
- Risposta: `Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.`

### Che cosa sono gli account amministrativi?

- Status: `OK`
- Tempo: `0.538791` ms
- Risposta: `Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi.`

### Che cosa possono contenere i documenti aziendali?

- Status: `OK`
- Tempo: `0.332750` ms
- Risposta: `I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati.`

### Che cosa protegge la sicurezza informatica?

- Status: `OK`
- Tempo: `0.516333` ms
- Risposta: `La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.`

## Riassunto generato

I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale. La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti. L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password. Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte. Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti. I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati. Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli. Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi. Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi. Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.

## Limiti

- Non legge ancora PDF direttamente.
- Non fa OCR.
- Non produce ancora riassunto 10% pagine o sinossi 1%.
- Non usa ancora cache persistente per documenti caricati.
