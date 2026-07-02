# Inference Engine V3.11 Human Aligned Decoder Report

- Engine: `inference_engine_v311_human_aligned_decoder`
- Generation mode: `human_aligned_semantic_decoder_v311`
- Corpus sentences: **1333**
- Prompt testati: **8**
- OK interni: **8**
- Falliti interni: **0**

## Regole

- Nessun fallback.
- Nessuna sentence bank.
- Nessuna anchored memory.
- Nessuna frase finale hardcoded.
- Source alignment obbligatorio prima della ricostruzione.
- Vietata sostituzione cieca del soggetto su frasi di altro dominio.
- Validazione finale obbligatoria: Semantic Gate V3.8.4.
- Evita sorgenti operative numerate e sostituzioni cieche del soggetto.
- Preserva congiunzioni e separatori importanti nelle liste.

## Output

### password

- Status: `OK`
- Score: `35.0`
- Output: `La password deve essere protetta perché può esporre un account se viene rubata.`
- Copied from corpus: `False`
- Source sentence: `La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.`
- Notes: `none`

### password sicure

- Status: `OK`
- Score: `43.0`
- Output: `Le password sicure richiedono una gestione attenta e possono essere organizzate con un password manager.`
- Copied from corpus: `False`
- Source sentence: `Il metodo migliore per gestire password sicure è usare un password manager.`
- Notes: `none`

### sicurezza informatica

- Status: `OK`
- Score: `65.0`
- Output: `La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.`
- Copied from corpus: `False`
- Source sentence: `La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.`
- Notes: `none`

### backup regolari

- Status: `OK`
- Score: `51.0`
- Output: `I backup regolari servono a recuperare informazioni in caso di errore umano.`
- Copied from corpus: `False`
- Source sentence: `Il backup serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.`
- Notes: `none`

### phishing

- Status: `OK`
- Score: `47.0`
- Output: `Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili.`
- Copied from corpus: `False`
- Source sentence: `Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.`
- Notes: `none`

### dati sensibili

- Status: `OK`
- Score: `43.0`
- Output: `I dati sensibili possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`
- Copied from corpus: `False`
- Source sentence: `Possono includere dati personali, informazioni economiche, documenti aziendali, contratti, credenziali, dati sanitari o informazioni riservate sui clienti.`
- Notes: `none`

### autenticazione a due fattori

- Status: `OK`
- Score: `57.0`
- Output: `L'autenticazione a due fattori aggiunge un secondo controllo oltre alla password.`
- Copied from corpus: `False`
- Source sentence: `L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.`
- Notes: `none`

### attacco ransomware

- Status: `OK`
- Score: `39.0`
- Output: `Un attacco ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.`
- Copied from corpus: `False`
- Source sentence: `Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.`
- Notes: `none`
