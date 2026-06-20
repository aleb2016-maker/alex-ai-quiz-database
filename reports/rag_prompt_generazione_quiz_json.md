Sei un generatore professionale di quiz formativi basati su documenti RAG.

Devi creare un file JSON basato SOLO sul contesto RAG fornito.

OBIETTIVO:
Generare 3 domande per un quiz riutilizzabile.

DATI QUIZ:
- argomento: sicurezza informatica aziendale
- categoria: informatica
- livello: intermedio

REGOLE OBBLIGATORIE SULLE FONTI:
- usa solo informazioni presenti nel contesto RAG
- non inventare contenuti esterni
- ogni domanda deve essere collegata al contesto recuperato
- la spiegazione deve essere coerente con il documento
- inserisci in fonte_rag il riferimento alla fonte usata, per esempio "[Fonte 1]"

REGOLE OBBLIGATORIE SULLE DOMANDE:
- crea esattamente 3 domande
- ogni domanda deve avere 4 opzioni
- 1 sola opzione deve essere corretta
- 3 opzioni devono essere distrattori forti
- non usare risposte palesemente assurde
- non usare opzioni completamente fuori tema
- non usare "tutte le precedenti" o "nessuna delle precedenti"
- non rendere la risposta corretta più lunga, più tecnica o più completa delle altre in modo evidente
- tutte le opzioni devono avere lunghezza, stile e livello tecnico simili

REGOLA FONDAMENTALE SUI 3 DISTRAttORI FORTI:
Ogni distrattore deve partire da un'idea plausibile e vicina alla risposta corretta,
ma deve diventare sbagliato per un dettaglio preciso.

NON creare distrattori come:
- affermazioni positive quando la domanda chiede un rischio
- frasi completamente scollegate dal tema
- opzioni che si eliminano subito
- opzioni ridicole o impossibili
- frasi troppo generiche

CREA invece distrattori di questo tipo:
- stesso concetto della risposta corretta, ma con una conseguenza sbagliata
- stessa premessa, ma con una limitazione errata
- stessa area tecnica, ma con un dettaglio invertito
- stessa funzione, ma applicata nel momento sbagliato
- stessa misura di sicurezza, ma con un effetto esagerato o falso

ESEMPIO DI QUALITÀ ATTESA:

Domanda:
Perché è rischioso usare la stessa password su più servizi?

Risposta corretta:
Perché se un servizio viene violato, la stessa password può essere provata anche su altri account.

Distrattore forte 1:
Perché usare la stessa password impedisce alla 2FA di generare codici temporanei.

Distrattore forte 2:
Perché una password riutilizzata viene automaticamente salvata in chiaro da tutti i siti.

Distrattore forte 3:
Perché il riutilizzo della password elimina sempre la possibilità di cambiarla in futuro.

Nota:
I tre distrattori sono vicini al tema password/account/sicurezza,
ma sono sbagliati per un dettaglio specifico.

ESEMPIO SU BACKUP:

Risposta corretta:
Il backup serve a recuperare dati dopo perdita, guasto o attacco ransomware.

Distrattore forte 1:
Il backup serve a impedire direttamente l'esecuzione di un ransomware prima dell'attacco.

Distrattore forte 2:
Il backup serve a recuperare i dati, ma solo se rimane sempre collegato alla stessa rete principale.

Distrattore forte 3:
Il backup serve a ripristinare i dati senza bisogno di verificare mai il recupero.

ESEMPIO SU PHISHING:

Risposta corretta:
Il phishing cerca di ingannare l'utente per ottenere credenziali, dati sensibili o pagamenti.

Distrattore forte 1:
Il phishing protegge le credenziali chiedendo all'utente di confermarle su un sito esterno.

Distrattore forte 2:
Il phishing si riconosce sempre solo dalla presenza di errori grammaticali evidenti.

Distrattore forte 3:
Il phishing riguarda solo allegati infetti e non può usare link o messaggi urgenti.

REGOLE SULLA SPIEGAZIONE:
- spiega perché la risposta corretta è corretta
- indica il dettaglio centrale della regola
- non limitarti a dire "le altre risposte sono sbagliate"
- non fare spiegazioni troppo brevi
- non inventare informazioni non presenti nel contesto

FORMATO JSON OBBLIGATORIO:
Restituisci solo JSON valido.
Non aggiungere markdown, commenti, testo prima o dopo.

{
  "metadati": {
    "origine": "rag",
    "argomento": "sicurezza informatica aziendale",
    "categoria": "informatica",
    "livello": "intermedio",
    "numero_domande_richieste": 3,
    "regola_distrattori": "tre_distrattori_forti_vicini"
  },
  "domande": [
    {
      "id": "RAG-0001",
      "categoria": "informatica",
      "livello": "intermedio",
      "domanda": "Testo della domanda",
      "opzioni": [
        "Risposta corretta",
        "Distrattore forte vicino 1",
        "Distrattore forte vicino 2",
        "Distrattore forte vicino 3"
      ],
      "risposta_corretta": "Risposta corretta",
      "spiegazione": "Spiegazione chiara basata sul contesto RAG.",
      "fonte_rag": "[Fonte 1]",
      "regola_distrattori": "tre_distrattori_forti_vicini"
    }
  ]
}

CONTESTO RAG:

CONTESTO RAG RECUPERATO DAI DOCUMENTI:

[Fonte 1]
Documento: rag/documenti/documento_rag_sicurezza_informatica_aziendale.md
Chunk: 1
Punteggio: 0.3737
Testo:
# Documento RAG di test: Sicurezza informatica aziendale ## Scopo del documento Questo documento è stato creato come fonte di prova per il motore RAG del progetto quiz. Può essere inserito nella cartella `rag/documenti/` per generare quiz, test e mini-corsi sulla sicurezza informatica aziendale. L'obiettivo è spiegare in modo semplice i concetti fondamentali di cybersecurity utili a dipendenti, studenti e nuovi utenti aziendali. Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG può recuperare contenuti e trasformarli in domande controllate. --- ## 1. Cos'è la sicurezza informatica La sicurezza informatica è l'insieme di pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali. Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete a

[Fonte 2]
Documento: rag/documenti/ESEMPIO_RAG_PROGETTO.md
Chunk: 1
Punteggio: 0.1364
Testo:
# Esempio documento RAG Il motore RAG del progetto serve a recuperare informazioni dai documenti caricati e a usarle come base per generare contenuti formativi. Un sistema RAG professionale può essere usato per creare quiz, test, mini-corsi, slide, percorsi aziendali, formazione interna e applicazioni educative. Nel progetto quiz, il RAG permette di generare domande partendo da materiale reale, riducendo il rischio di inventare contenuti non presenti nella fonte. Ogni domanda dovrebbe avere una risposta corretta e tre distrattori forti, plausibili e vicini alla risposta corretta. Il sistema può diventare riutilizzabile anche per applicazioni diverse dai quiz, per esempio assistenti formativi, motori di studio, generatori di corsi e strumenti aziendali.

[Fonte 3]
Documento: rag/documenti/documento_rag_sicurezza_informatica_aziendale.md
Chunk: 13
Punteggio: 0.125
Testo:
otrebbe creare una rete con un nome simile a quello di un bar, hotel o aeroporto per intercettare il traffico degli utenti. Quando si usa una rete pubblica è meglio evitare operazioni sensibili, come accesso a conti bancari, sistemi aziendali o pannelli amministrativi. Se necessario, è preferibile usare una VPN aziendale o una connessione mobile personale. Anche in casa o in ufficio la rete Wi-Fi deve essere protetta con password forte e crittografia adeguata. La password del router non dovrebbe rimanere quella predefinita se è debole o facilmente prevedibile. --- ## 11. Comportamenti corretti in azienda La sicurezza informatica dipende anche da comportamenti quotidiani. Bloccare lo schermo quando ci si allontana dalla postazione impedisce ad altre persone di usare il computer senza autorizzazione. Non lasciare documenti riservati sulla scrivania riduce il rischio di accesso non autorizz

[Fonte 4]
Documento: rag/documenti/documento_rag_sicurezza_informatica_aziendale.md
Chunk: 9
Punteggio: 0.1123
Testo:
rete, un ransomware potrebbe cifrare anche quello. Una regola utile è mantenere più copie dei dati importanti, possibilmente su supporti o servizi diversi. Non basta creare backup: bisogna anche testare il ripristino. Un backup che non può essere ripristinato correttamente non è davvero utile. In un contesto aziendale, il backup deve essere pianificato. Bisogna decidere quali dati salvare, ogni quanto salvarli, dove conservarli e chi può accedervi. --- ## 7. Aggiornamenti software Gli aggiornamenti software correggono errori, migliorano le funzioni e chiudono vulnerabilità di sicurezza. Rimandare gli aggiornamenti per troppo tempo può lasciare un sistema esposto ad attacchi già conosciuti. Un attaccante spesso sfrutta vulnerabilità note. Quando una correzione viene pubblicata, anche gli attaccanti possono studiare il problema e cercare sistemi non aggiornati. Aggiornare non significa so

[Fonte 5]
Documento: rag/documenti/documento_rag_sicurezza_informatica_aziendale.md
Chunk: 2
Punteggio: 0.1109
Testo:
dati, dispositivi, account e sistemi digitali. Non riguarda solo gli esperti informatici: ogni persona che usa un computer, uno smartphone, una rete aziendale o un account online contribuisce alla sicurezza generale. Un sistema informatico può essere tecnicamente avanzato, ma rimanere vulnerabile se gli utenti usano password deboli, cliccano link sospetti o condividono dati riservati senza controllo. La sicurezza informatica ha tre obiettivi principali: - proteggere la riservatezza dei dati; - garantire l'integrità delle informazioni; - mantenere disponibili servizi e strumenti quando servono. Riservatezza significa che solo le persone autorizzate possono accedere a certe informazioni. Integrità significa che i dati non devono essere modificati in modo non autorizzato. Disponibilità significa che sistemi, documenti e servizi devono rimanere accessibili agli utenti autorizzati. --- ## 2.

[Fonte 6]
Documento: rag/documenti/documento_rag_sicurezza_informatica_aziendale.md
Chunk: 14
Punteggio: 0.0732
Testo:
ad altre persone di usare il computer senza autorizzazione. Non lasciare documenti riservati sulla scrivania riduce il rischio di accesso non autorizzato. Un dipendente dovrebbe segnalare subito incidenti, errori o sospetti. Nascondere un clic su un link sospetto o una password inserita in un sito falso può peggiorare la situazione. Una segnalazione rapida permette all'azienda di reagire prima che il danno aumenti. La cultura della sicurezza non deve basarsi sulla paura, ma sulla responsabilità. Gli errori possono capitare, ma devono essere comunicati rapidamente. --- ## 12. Uso del documento per quiz e mini-corsi Questo documento può essere usato dal motore RAG per generare domande su: - password sicure; - autenticazione a due fattori; - phishing; - malware; - ransomware; - backup; - aggiornamenti software; - protezione dei dati; - permessi utente; - reti Wi-Fi pubbliche; - comportament