# Fast Q&A + Summary Current Benchmark

- Stato: **PASS**
- Base engine: `inference_engine_v315_extended_safe_decoder`
- Elementi indicizzati: `26`

## Q&A

- Domande testate: `10`
- Risposte OK: `10`
- Load engine: `0.538833` ms
- Q&A media: `0.014746` ms
- Q&A mediana: `0.013979` ms
- Q&A P95: `0.030333` ms
- Q&A max: `0.030333` ms

## Summary

- Summary status: `OK`
- Frasi usate: `8`
- Summary time interno: `0.098000` ms
- Summary time totale: `0.098917` ms

## Esempi Q&A

### Che cosa fa il phishing?

- Status: `OK`
- Tempo: `0.012125` ms
- Risposta: `Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.`

### A cosa serve un backup?

- Status: `OK`
- Tempo: `0.009334` ms
- Risposta: `I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.`

### Come funziona l'autenticazione a due fattori?

- Status: `OK`
- Tempo: `0.008625` ms
- Risposta: `L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.`

### Che cos'è il ransomware?

- Status: `OK`
- Tempo: `0.013041` ms
- Risposta: `Un attacco ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.`

### Perché sono importanti gli aggiornamenti software?

- Status: `OK`
- Tempo: `0.008333` ms
- Risposta: `Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.`

### Che cosa sono i dati sensibili?

- Status: `OK`
- Tempo: `0.030333` ms
- Risposta: `I dati sensibili possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`

### Come si proteggono le credenziali rubate?

- Status: `OK`
- Tempo: `0.019917` ms
- Risposta: `Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.`

### Che cosa fa un password manager?

- Status: `OK`
- Tempo: `0.015917` ms
- Risposta: `Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.`

### Che cosa sono gli account amministrativi?

- Status: `OK`
- Tempo: `0.014917` ms
- Risposta: `Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi.`

### Perché è pericolosa una password rubata?

- Status: `OK`
- Tempo: `0.014917` ms
- Risposta: `Una password rubata può esporre un account se non viene protetta da controlli aggiuntivi.`

## Riassunto generato

I dati sensibili possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti. La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti. Un backup offline aiuta a proteggere i dati perché resta separato dal computer o dalla rete principale. I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale. Il social engineering usa tecniche di inganno per convincere le persone a fornire dati sensibili o credenziali. Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte. Il malware è un software dannoso che può danneggiare sistemi, rubare informazioni o bloccare l'accesso ai dati. Il ripristino dati serve a recuperare informazioni dopo errore umano, guasto o cancellazione accidentale.

## Limiti

- Questo è un motore fast Q&A/summary V1 su materiale già validato.
- Non è ancora il motore RAG finale su PDF/documenti lunghi.
- Non usa ancora cache persistente documentale.
- Non produce ancora riassunti al 10% delle pagine o sinossi all'1%.
