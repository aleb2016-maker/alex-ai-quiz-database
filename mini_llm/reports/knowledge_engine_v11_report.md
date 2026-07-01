# Report Knowledge Engine V1.1

## File analizzato
/Users/alessandrobarbarossa/alex-ai-workspace/rag/documenti/documento_rag_sicurezza_informatica_aziendale.md

## Output JSON
/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v11_output.json

## Categoria documento
documento_aziendale

## Statistiche
{
  "caratteri_testo": 10458,
  "numero_unita_testuali": 122,
  "numero_parole_utili": 846,
  "numero_aree_operative": 14,
  "numero_micro_informazioni": 30,
  "numero_frasi_rilevanti": 10,
  "numero_relazioni_operative": 10,
  "numero_training_items": 10
}

## Aree operative
- password
- sicurezza informatica
- dati sensibili
- malware
- ransomware
- account
- aggiornamenti software
- allegati inattesi
- backup regolari
- privilegi amministrativi
- protezione endpoint
- codici temporanei
- autenticazione a due fattori
- reti wi-fi pubbliche

## Micro-informazioni operative
- La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.
- La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.
- Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare.
- Può dire che un account verrà bloccato, che un pacco è fermo, che bisogna verificare un pagamento o.
- L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.
- Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento.
- Un tipo particolare di malware è il ransomware.
- Risposta corretta: Perché se un servizio viene violato, la stessa password può essere provata anche su altri account.
- Per ridurre il rischio malware è importante:
- Un sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti usano password deboli, cliccano link.
- serve una protezione aggiuntiva, come password o permessi limitati?
- Lasciare attivi account non più necessari è un rischio.
- Domanda: Perché è rischioso usare la stessa password su più servizi?
- Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o.
- La sicurezza informatica ha tre obiettivi principali:
- Un password manager permette di salvare password lunghe e uniche senza doverle ricordare tutte.
- Anche se un attaccante scopre la password, deve superare anche il secondo controllo.
- Il phishing è una tecnica usata per ingannare le persone e convincerle a fornire dati sensibili, credenziali o.
- richiesta di password, codici o dati bancari;
- Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai.
- Il ransomware blocca o cifra i dati e chiede un pagamento per ripristinarli.
- Un utente non dovrebbe lavorare sempre con account amministratore se non necessario.
- Serve a recuperare informazioni in caso di errore umano, guasto, furto, cancellazione accidentale o attacco ransomware.
- Se il backup è sempre collegato allo stesso computer o alla stessa rete, un ransomware potrebbe cifrare anche.
- Questo principio riduce il danno possibile in caso di errore o compromissione di un account.
- # Documento RAG di test: Sicurezza informatica aziendale
- Cos'è la sicurezza informatica
- Una password sicura deve essere lunga, difficile da indovinare e diversa per ogni servizio.
- Una buona password dovrebbe contenere parole non ovvie, numeri, simboli e una lunghezza adeguata.
- Un esempio debole è `password123`, perché è corta, comune e facile da provare automaticamente.

## Frasi rilevanti
- La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.
- La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali.
- Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account.
- Può dire che un account verrà bloccato, che un pacco è fermo, che bisogna verificare un pagamento o che è necessario aggiornare subito una password.
- L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.
- Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili.
- Per ridurre il rischio malware è importante:
- Un tipo particolare di malware è il ransomware.
- Risposta corretta: Perché se un servizio viene violato, la stessa password può essere provata anche su altri account.
- Un sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti usano password deboli, cliccano link sospetti o condividono dati riservati senza controllo.

## Relazioni operative
- password -> account (co_presenza_in_informazione_rilevante)
- sicurezza informatica -> account (co_presenza_in_informazione_rilevante)
- password -> account (co_presenza_in_informazione_rilevante)
- password -> account (co_presenza_in_informazione_rilevante)
- password -> autenticazione a due fattori (co_presenza_in_informazione_rilevante)
- dati sensibili -> account (co_presenza_in_informazione_rilevante)
- malware -> Per ridurre il rischio malware è importante: (area_collegata_a_frase_operativa)
- malware -> ransomware (co_presenza_in_informazione_rilevante)
- password -> account (co_presenza_in_informazione_rilevante)
- password -> Un sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti usano password deboli, cliccano link. (area_collegata_a_frase_operativa)

## Dataset training iniziale
[
  {
    "input": "Riconosci la categoria operativa del documento.",
    "output": "documento_aziendale"
  },
  {
    "input": "Elenca le aree operative principali del documento.",
    "output": "password, sicurezza informatica, dati sensibili, malware, ransomware, account, aggiornamenti software, allegati inattesi, backup regolari, privilegi amministrativi, protezione endpoint, codici temporanei, autenticazione a due fattori, reti wi-fi pubbliche"
  },
  {
    "input": "Elenca le micro-informazioni operative più utili.",
    "output": "La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.; La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi.; Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare.; Può dire che un account verrà bloccato, che un pacco è fermo, che bisogna verificare un pagamento o.; L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password.; Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento.; Un tipo particolare di malware è il ransomware.; Risposta corretta: Perché se un servizio viene violato, la stessa password può essere provata anche su altri account.; Per ridurre il rischio malware è importante:; Un sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti usano password deboli, cliccano link.; serve una protezione aggiuntiva, come password o permessi limitati?; Lasciare attivi account non più necessari è un rischio."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "Può dire che un account verrà bloccato, che un pacco è fermo, che bisogna verificare un pagamento o che è necessario aggiornare subito una password."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "L'autenticazione a due fattori, spesso abbreviata in 2FA, aggiunge un secondo controllo oltre alla password."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "Una buona regola aziendale è attivare la 2FA almeno su email, strumenti cloud, account amministrativi, sistemi di pagamento e piattaforme che contengono dati sensibili."
  },
  {
    "input": "Crea una sintesi breve delle informazioni operative più importanti.",
    "output": "La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata. La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali. Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account. Può dire che un account verrà bloccato, che un pacco è fermo, che bisogna verificare un pagamento o che è necessario aggiornare subito una password."
  }
]
