# Inference Engine V3.14 Safe Dynamic Decoder Report

- Engine: `inference_engine_v314_rewrite_only_safe_decoder`
- Generation mode: `rewrite_only_safe_semantic_decoder_v314`
- Corpus sentences: **717**
- Prompt testati: **28**
- OK interni: **18**
- Falliti interni: **10**

## Regole

- Nessun fallback.
- Nessuna sentence bank.
- Nessuna anchored memory.
- Nessuna frase finale hardcoded.
- No sostituzione cieca del soggetto.
- Se la sorgente non è sicura, fallisce.
- Validazione finale obbligatoria: Semantic Gate V3.8.6.

## Output

### password

- Status: `OK`
- Score: `65.0`
- Output: `La password deve essere protetta perché può esporre un account se viene rubata.`
- Source sentence: `La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.`
- Notes: `none`

### password sicure

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### sicurezza informatica

- Status: `OK`
- Score: `90.0`
- Output: `La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.`
- Source sentence: `La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.`
- Notes: `none`

### backup regolari

- Status: `OK`
- Score: `70.0`
- Output: `I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.`
- Source sentence: `Il backup serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.`
- Notes: `none`

### phishing

- Status: `OK`
- Score: `65.0`
- Output: `Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.`
- Source sentence: `Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.`
- Notes: `none`

### dati sensibili

- Status: `OK`
- Score: `50.0`
- Output: `I dati sensibili possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`
- Source sentence: `Possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`
- Notes: `none`

### autenticazione a due fattori

- Status: `OK`
- Score: `90.0`
- Output: `L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.`
- Source sentence: `L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.`
- Notes: `none`

### attacco ransomware

- Status: `OK`
- Score: `70.0`
- Output: `Un attacco ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.`
- Source sentence: `Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.`
- Notes: `none`

### password manager

- Status: `OK`
- Score: `50.0`
- Output: `Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.`
- Source sentence: `Un password manager permette di salvare password lunghe e uniche senza doverle ricordare tutte.`
- Notes: `none`

### password rubata

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### credenziali rubate

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### accesso non autorizzato

- Status: `OK`
- Score: `70.0`
- Output: `L'accesso non autorizzato è un rischio che può esporre documenti, credenziali o dati riservati.`
- Source sentence: `Non lasciare documenti riservati sulla scrivania riduce il rischio di accesso non autorizzato.`
- Notes: `none`

### backup offline

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### ripristino dati

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### malware

- Status: `OK`
- Score: `65.0`
- Output: `Il malware è un software dannoso che può danneggiare sistemi, rubare informazioni o bloccare l'accesso ai dati.`
- Source sentence: `Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai.`
- Notes: `none`

### ransomware

- Status: `OK`
- Score: `65.0`
- Output: `Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.`
- Source sentence: `Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.`
- Notes: `none`

### email sospetta

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### social engineering

- Status: `OK`
- Score: `70.0`
- Output: `Il social engineering usa tecniche di inganno per convincere le persone a fornire dati sensibili o credenziali.`
- Source sentence: `Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.`
- Notes: `none`

### codici temporanei

- Status: `OK`
- Score: `90.0`
- Output: `I codici temporanei sono controlli usa e getta che rafforzano l'autenticazione.`
- Source sentence: `I codici temporanei generati da app di autenticazione sono generalmente più sicuri dei codici ricevuti via SMS.`
- Notes: `none`

### account amministrativi

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### permessi minimi

- Status: `OK`
- Score: `70.0`
- Output: `I permessi minimi riducono i danni quando un programma malevolo viene eseguito.`
- Source sentence: `Limitare i permessi riduce i danni nel caso in cui un programma malevolo venga eseguito.`
- Notes: `none`

### dati personali

- Status: `OK`
- Score: `50.0`
- Output: `I dati personali devono essere protetti perché possono identificare persone, clienti o utenti.`
- Source sentence: `Possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`
- Notes: `none`

### protezione endpoint

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### aggiornamenti software

- Status: `OK`
- Score: `90.0`
- Output: `Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.`
- Source sentence: `Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza.`
- Notes: `none`

### rischio informatico

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### furto credenziali

- Status: `FAILED_NO_SAFE_SOURCE`
- Score: `-999.0`
- Output: ``
- Source sentence: ``
- Notes: `no_safe_compatible_source`

### documenti aziendali

- Status: `OK`
- Score: `90.0`
- Output: `I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati.`
- Source sentence: `Possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`
- Notes: `none`

### informazioni riservate

- Status: `OK`
- Score: `50.0`
- Output: `Le informazioni riservate devono essere protette perché possono riguardare clienti, contratti, credenziali o dati sensibili.`
- Source sentence: `Possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`
- Notes: `none`
