# Report Knowledge Engine Quality Filter V1.2

## Input JSON
/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v11_output.json

## Documento sorgente
/Users/alessandrobarbarossa/alex-ai-workspace/rag/documenti/documento_rag_sicurezza_informatica_aziendale.md

## Output JSON
/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v12_clean_output.json

## Categoria documento
documento_aziendale

## Statistiche
{
  "numero_aree_operative": 14,
  "numero_micro_informazioni": 24,
  "numero_frasi_rilevanti": 10,
  "numero_relazioni_operative": 4,
  "numero_training_items": 9,
  "problemi_residui": 0
}

## Aree operative pulite
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

## Micro-informazioni pulite
- Un tipo particolare di malware è il ransomware.
- Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.
- Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.
- La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.
- L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.
- Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.
- Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche.
- Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.
- Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati.
- Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza.
- Un password manager permette di salvare password lunghe e uniche senza doverle ricordare tutte.
- Serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.
- Il metodo migliore è usare un password manager.
- L'utente deve ricordare solo la password principale del password manager, che deve essere molto robusta.
- I codici temporanei generati da app di autenticazione sono generalmente più sicuri dei codici ricevuti via SMS.
- Un messaggio di phishing può sembrare urgente.
- I dati sensibili sono informazioni che devono essere protette con particolare attenzione.
- Non tutti devono poter modificare file critici, accedere a dati sensibili o installare software.
- La sicurezza informatica dipende anche da comportamenti quotidiani.
- La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.
- Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare.
- Lasciare attivi account non più necessari è un rischio.
- Questo principio riduce il danno possibile in caso di errore o compromissione di un account.
- Una password sicura deve essere lunga, difficile da indovinare e diversa per ogni servizio.

## Frasi rilevanti pulite
- Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.
- Un tipo particolare di malware è il ransomware.
- Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.
- La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali.
- L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.
- Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.
- Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati.
- Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.
- Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche quello.
- Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza.

## Relazioni operative pulite
- malware -> ransomware (co_presenza_in_informazione_rilevante)
- dati sensibili -> account amministrativi (co_presenza_pulita)
- malware -> ransomware (co_presenza_pulita)
- dati sensibili -> phishing (co_presenza_pulita)

## Dataset training pulito
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
    "input": "Elenca micro-informazioni operative pulite e utilizzabili.",
    "output": "Un tipo particolare di malware è il ransomware.; Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.; Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti.; La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.; L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.; Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.; Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche.; Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.; Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati.; Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "Un tipo particolare di malware è il ransomware."
  },
  {
    "input": "Riscrivi questa informazione in forma chiara per un riassunto.",
    "output": "Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti."
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
    "output": "Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili. Un tipo particolare di malware è il ransomware. Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o pagamenti. La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali."
  }
]

## Report qualità
{
  "aree_input_v11": 14,
  "micro_input_v11": 30,
  "frasi_input_v11": 10,
  "aree_output_v12": 14,
  "micro_output_v12": 24,
  "frasi_output_v12": 10,
  "relazioni_output_v12": 4,
  "training_items_output_v12": 9,
  "problemi_residui": []
}
