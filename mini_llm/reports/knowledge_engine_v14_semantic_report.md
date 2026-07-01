# Report Knowledge Engine Semantic Repair V1.4

## Input JSON
/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v13_strict_output.json

## Output JSON
/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v14_semantic_output.json

## Categoria documento
documento_aziendale

## Statistiche
{
  "numero_aree_operative": 14,
  "numero_micro_informazioni": 24,
  "numero_frasi_rilevanti": 10,
  "numero_relazioni_operative": 3,
  "numero_training_items": 9,
  "micro_riparazioni": 2,
  "frasi_riparazioni": 0,
  "problemi_residui": 0,
  "semantic_repairs_v14": 3,
  "problemi_semantici_residui_v14": 0
}

## Aree operative
- sicurezza informatica
- password sicure
- password manager
- protezione dei dati
- dati sensibili
- autenticazione a due fattori
- codici temporanei
- account online
- account amministrativi
- phishing
- malware
- ransomware
- backup regolari
- aggiornamenti software

## Micro-informazioni
- Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.
- Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.
- Un tipo particolare di malware è il ransomware.
- La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.
- L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.
- Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza.
- Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.
- Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche quello.
- Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.
- Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati.
- Un password manager permette di salvare password lunghe e uniche senza doverle ricordare tutte.
- Il metodo migliore per gestire password sicure è usare un password manager.
- L'utente deve ricordare solo la password principale del password manager, che deve essere molto robusta.
- I dati sensibili sono informazioni che devono essere protette con particolare attenzione.
- Non tutti devono poter modificare file critici, accedere a dati sensibili o installare software.
- Il backup serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.
- I codici temporanei generati da app di autenticazione sono generalmente più sicuri dei codici ricevuti via SMS.
- Un messaggio di phishing può sembrare urgente.
- La sicurezza informatica dipende anche da comportamenti quotidiani.
- La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.
- Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account.
- Lasciare attivi account non più necessari è un rischio.
- Il principio del minimo privilegio riduce il danno possibile in caso di errore o compromissione di un account.
- Una password sicura deve essere lunga, difficile da indovinare e diversa per ogni servizio.

## Frasi rilevanti
- Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.
- Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.
- Un tipo particolare di malware è il ransomware.
- La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali.
- L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.
- Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza.
- Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.
- Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati.
- Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.
- Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche quello.

## Relazioni operative
- malware -> ransomware (relazione_operativa_pulita)
- dati sensibili -> account amministrativi (relazione_operativa_pulita)
- dati sensibili -> phishing (relazione_operativa_pulita)

## Dataset training
[
  {
    "input": "Riconosci la categoria operativa del documento.",
    "output": "documento_aziendale"
  },
  {
    "input": "Elenca le aree operative principali del documento.",
    "output": "sicurezza informatica, password sicure, password manager, protezione dei dati, dati sensibili, autenticazione a due fattori, codici temporanei, account online, account amministrativi, phishing, malware, ransomware, backup regolari, aggiornamenti software"
  },
  {
    "input": "Elenca micro-informazioni operative pulite e complete.",
    "output": "Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.; Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.; Un tipo particolare di malware è il ransomware.; La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.; L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.; Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza.; Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.; Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche quello.; Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.; Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "Un tipo particolare di malware è il ransomware."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password."
  },
  {
    "input": "Crea una sintesi operativa breve del documento.",
    "output": "Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili. Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti. Un tipo particolare di malware è il ransomware. La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali."
  }
]

## Report qualità
{
  "micro_riparazioni": [
    {
      "prima": "Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche.",
      "dopo": "Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche quello."
    },
    {
      "prima": "Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare.",
      "dopo": "Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account."
    }
  ],
  "frasi_riparazioni": [],
  "problemi_residui": [],
  "semantic_repairs_v14": [
    {
      "prima": "Il metodo migliore è usare un password manager.",
      "dopo": "Il metodo migliore per gestire password sicure è usare un password manager."
    },
    {
      "prima": "Serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.",
      "dopo": "Il backup serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware."
    },
    {
      "prima": "Questo principio riduce il danno possibile in caso di errore o compromissione di un account.",
      "dopo": "Il principio del minimo privilegio riduce il danno possibile in caso di errore o compromissione di un account."
    }
  ],
  "problemi_semantici_residui_v14": []
}
