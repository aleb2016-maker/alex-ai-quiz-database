# Report Knowledge Engine V1

## File analizzato
/Users/alessandrobarbarossa/alex-ai-workspace/rag/documenti/documento_rag_sicurezza_informatica_aziendale.md

## Output JSON
/Users/alessandrobarbarossa/alex-ai-workspace/mini_llm/data/output/knowledge_engine_v1_output.json

## Categoria documento
documento_aziendale

## Statistiche
{
  "caratteri_testo": 11545,
  "numero_frasi": 103,
  "numero_parole_utili": 977,
  "numero_aree_principali": 14,
  "numero_micro_informazioni": 30,
  "numero_frasi_rilevanti": 10,
  "numero_relazioni_operative": 14,
  "numero_training_items": 10
}

## Aree principali
- password
- dati
- sicurezza
- account
- backup
- usare
- utente
- software
- sistema
- sistemi
- solo
- informazioni
- rischio
- permessi

## Micro-informazioni operative
- utenti usano password deboli
- password sicure
- password sicura deve essere
- stessa password
- stessa password anche
- buona password dovrebbe contenere parole
- password manager
- password manager permette
- salvare password lunghe
- password principale
- password
- password viene comunicata
- oltre alla password
- come password
- password forte
- password inserita
- password uguale impedisce sempre
- password uguali
- password usata
- proteggere dati
- condividono dati riservati senza controllo
- dati
- contengono dati sensibili
- fornire dati sensibili
- dati bancari
- dati importanti
- decidere quali dati salvare
- dati sensibili
- dati sensibili sono informazioni
- possono includere dati personali

## Frasi rilevanti
- Per ridurre il rischio malware è importante:

- evitare software non autorizzato;
- non aprire allegati inattesi;
- aggiornare sistema operativo e applicazioni;
- usare strumenti antivirus o sistemi di protezione endpoint;
- fare backup regolari;
- limitare i privilegi amministrativi.
- La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata.
- Uso del documento per quiz e mini-corsi

Questo documento può essere usato dal motore RAG per generare domande su:

- password sicure;
- autenticazione a due fattori;
- phishing;
- malware;
- ransomware;
- backup;
- aggiornamenti software;
- protezione dei dati;
- permessi utente;
- reti Wi-Fi pubbliche;
- comportamenti corretti in azienda.
- Cos'è la sicurezza informatica

La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali.
- La sicurezza informatica ha tre obiettivi principali:

- proteggere la riservatezza dei dati;
- garantire l'integrità delle informazioni;
- mantenere disponibili servizi e strumenti quando servono.
- Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account.
- Alcuni segnali di rischio sono:

- indirizzo del mittente strano o leggermente diverso da quello ufficiale;
- link che non portano al dominio reale;
- errori grammaticali o frasi insolite;
- richiesta di password, codici o dati bancari;
- tono minaccioso o eccessivamente urgente;
- allegati inattesi.
- Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale.
- Un sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti usano password deboli, cliccano link sospetti o condividono dati riservati senza controllo.
- Malware e allegati pericolosi

Il malware è un software dannoso progettato per danneggiare sistemi, rubare informazioni, spiare attività o bloccare l'accesso ai dati.

## Relazioni operative
- password -> utenti usano password deboli (area_operativa_collegata_a_micro_informazione)
- password -> password sicure (area_operativa_collegata_a_micro_informazione)
- password -> password sicura deve essere (area_operativa_collegata_a_micro_informazione)
- dati -> proteggere dati (area_operativa_collegata_a_micro_informazione)
- dati -> condividono dati riservati senza controllo (area_operativa_collegata_a_micro_informazione)
- dati -> dati (area_operativa_collegata_a_micro_informazione)
- informazioni -> dati sensibili sono informazioni (area_operativa_collegata_a_micro_informazione)
- utenti usano password deboli -> password sicure (vicinanza_operativa)
- password sicure -> password sicura deve essere (vicinanza_operativa)
- password sicura deve essere -> stessa password (vicinanza_operativa)
- stessa password -> stessa password anche (vicinanza_operativa)
- stessa password anche -> buona password dovrebbe contenere parole (vicinanza_operativa)
- buona password dovrebbe contenere parole -> password manager (vicinanza_operativa)
- password manager -> password manager permette (vicinanza_operativa)

## Dataset training iniziale
[
  {
    "input": "Riconosci la categoria operativa del documento.",
    "output": "documento_aziendale"
  },
  {
    "input": "Elenca le aree principali del documento.",
    "output": "password, dati, sicurezza, account, backup, usare, utente, software, sistema, sistemi, solo, informazioni, rischio, permessi"
  },
  {
    "input": "Elenca le micro-informazioni operative del documento.",
    "output": "utenti usano password deboli, password sicure, password sicura deve essere, stessa password, stessa password anche, buona password dovrebbe contenere parole, password manager, password manager permette, salvare password lunghe, password principale, password, password viene comunicata, oltre alla password, come password, password forte, password inserita, password uguale impedisce sempre, password uguali, password usata, proteggere dati, condividono dati riservati senza controllo, dati, contengono dati sensibili, fornire dati sensibili, dati bancari, dati importanti, decidere quali dati salvare, dati sensibili, dati sensibili sono informazioni, possono includere dati personali"
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "Per ridurre il rischio malware è importante:\n\n- evitare software non autorizzato;\n- non aprire allegati inattesi;\n- aggiornare sistema operativo e applicazioni;\n- usare strumenti antivirus o sistemi di protezione endpoint;\n- fare backup regolari;\n- limitare i privilegi amministrativi."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "Uso del documento per quiz e mini-corsi\n\nQuesto documento può essere usato dal motore RAG per generare domande su:\n\n- password sicure;\n- autenticazione a due fattori;\n- phishing;\n- malware;\n- ransomware;\n- backup;\n- aggiornamenti software;\n- protezione dei dati;\n- permessi utente;\n- reti Wi-Fi pubbliche;\n- comportamenti corretti in azienda."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "Cos'è la sicurezza informatica\n\nLa sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "La sicurezza informatica ha tre obiettivi principali:\n\n- proteggere la riservatezza dei dati;\n- garantire l'integrità delle informazioni;\n- mantenere disponibili servizi e strumenti quando servono."
  },
  {
    "input": "Trasforma questa informazione in una frase chiara per un riassunto.",
    "output": "Usare la stessa password su più siti è rischioso: se un servizio viene violato, un attaccante può provare la stessa password anche su altri account."
  },
  {
    "input": "Crea una sintesi breve delle informazioni più importanti.",
    "output": "Per ridurre il rischio malware è importante:\n\n- evitare software non autorizzato;\n- non aprire allegati inattesi;\n- aggiornare sistema operativo e applicazioni;\n- usare strumenti antivirus o sistemi di protezione endpoint;\n- fare backup regolari;\n- limitare i privilegi amministrativi. La 2FA riduce il rischio che un account venga violato solo perché la password è stata rubata. Uso del documento per quiz e mini-corsi\n\nQuesto documento può essere usato dal motore RAG per generare domande su:\n\n- password sicure;\n- autenticazione a due fattori;\n- phishing;\n- malware;\n- ransomware;\n- backup;\n- aggiornamenti software;\n- protezione dei dati;\n- permessi utente;\n- reti Wi-Fi pubbliche;\n- comportamenti corretti in azienda."
  }
]
