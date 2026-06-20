Sei un motore di riparazione per quiz generati da RAG.

Devi correggere SOLO i distrattori deboli del quiz JSON.

CICLO DI RIPARAZIONE: 2

PROBLEMI RILEVATI DAL VALIDATORE:
- Domanda 1: opzione A: distrattore troppo lontano dalla risposta corretta (similarità 0.06).
- Domanda 1: opzione C: distrattore troppo lontano dalla risposta corretta (similarità 0.05).
- Domanda 1: almeno due distrattori sembrano troppo lontani: la risposta corretta potrebbe essere individuabile per eliminazione.
- Domanda 3: opzione A: distrattore troppo lontano dalla risposta corretta (similarità 0.06).
- Domanda 3: opzione D: distrattore troppo lontano dalla risposta corretta (similarità 0.00).
- Domanda 3: opzione D: sembra generica o fuori tema (semplificare).
- Domanda 3: almeno due distrattori sembrano troppo lontani: la risposta corretta potrebbe essere individuabile per eliminazione.
- Domanda 3: opzione A: distrattore poco collegato al testo della domanda.
- Domanda 3: opzione C: distrattore poco collegato al testo della domanda.
- Domanda 3: opzione D: distrattore poco collegato al testo della domanda.

REGOLE OBBLIGATORIE:
- restituisci solo JSON valido
- mantieni la struttura con `metadati` e `domande`
- mantieni lo stesso numero di domande
- non cancellare domande
- non aggiungere domande
- non cambiare categoria
- non cambiare livello
- non cambiare fonte_rag
- non cambiare il testo della risposta corretta
- la risposta corretta deve restare tra le 4 opzioni
- puoi riscrivere i 3 distrattori
- puoi migliorare la spiegazione se serve
- ogni domanda deve avere 1 risposta corretta e 3 distrattori forti

COME DEVONO ESSERE I DISTRAttORI FORTI:
- vicini alla risposta corretta
- stesso argomento tecnico
- stessa area concettuale
- plausibili
- sbagliati per un dettaglio preciso
- non assurdi
- non generici
- non fuori tema
- non troppo brevi rispetto alla risposta corretta
- non facilmente eliminabili

ESEMPIO:

Risposta corretta:
Il backup serve a recuperare dati dopo perdita, guasto o ransomware.

Distrattore debole:
Per velocizzare il computer.

Distrattore forte:
Il backup serve a recuperare dati dopo un ransomware, ma solo se rimane sempre collegato alla rete principale.

Il secondo è forte perché parla ancora di backup e ransomware, ma contiene un dettaglio sbagliato.

QUIZ DA RIPARARE:

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
      "domanda": "Qual è la principale ragione per cui l'uso di una singola password su più account rappresenta un rischio significativo per la sicurezza aziendale?",
      "opzioni": [
        "Perché le password lunghe sono sempre più vulnerabili agli attacchi brute-force.",
        "Perché una compromissione di un account può consentire a un attaccante di accedere a tutti gli altri account dello stesso utente.",
        "Perché l'utilizzo della stessa password semplifica il processo di autenticazione e riduce la necessità di password complesse.",
        "Perché le password condivise tra diversi account vengono automaticamente memorizzate in chiaro da tutti i siti."
      ],
      "risposta_corretta": "Perché una compromissione di un account può consentire a un attaccante di accedere a tutti gli altri account dello stesso utente.",
      "spiegazione": "Il documento sottolinea che il rischio principale risiede nel fatto che, se un account viene violato, l'attaccante può utilizzare la stessa password per ottenere accesso ad altri account associati allo stesso utente. Questo è un errore comune che espone l’azienda a rischi elevati.",
      "fonte_rag": "[Fonte 1]",
      "regola_distrattori": "tre_distrattori_forti_vicini"
    },
    {
      "id": "RAG-0002",
      "categoria": "informatica",
      "livello": "intermedio",
      "domanda": "Quale delle seguenti affermazioni descrive meglio lo scopo di un backup aziendale?",
      "opzioni": [
        "Un backup serve solo a ripristinare i dati in caso di attacco ransomware.",
        "Un backup serve a garantire che tutti i dati siano sempre disponibili, indipendentemente dall'hardware o dal software utilizzati.",
        "Un backup serve a recuperare dati dopo perdita, guasto o attacco ransomware.",
        "Un backup serve ad eliminare automaticamente tutti i file obsoleti per ottimizzare lo spazio di archiviazione."
      ],
      "risposta_corretta": "Un backup serve a recuperare dati dopo perdita, guasto o attacco ransomware.",
      "spiegazione": "Il documento spiega chiaramente che il backup ha lo scopo di recuperare i dati in seguito a eventi dannosi come perdite, guasti hardware o attacchi ransomware.",
      "fonte_rag": "[Fonte 3]",
      "regola_distrattori": "tre_distrattori_forti_vicini"
    },
    {
      "id": "RAG-0003",
      "categoria": "informatica",
      "livello": "intermedio",
      "domanda": "Perché è importante che le reti Wi-Fi aziendali siano protette con password robuste e crittografia?",
      "opzioni": [
        "Per evitare il rallentamento della rete a causa di un elevato numero di dispositivi connessi.",
        "Per prevenire l'accesso non autorizzato alla rete, proteggendo la riservatezza dei dati e la sicurezza degli utenti.",
        "Per garantire che tutti i dispositivi connessi alla rete abbiano accesso alle stesse risorse.",
        "Per semplificare il processo di connettività per i nuovi dipendenti."
      ],
      "risposta_corretta": "Per prevenire l'accesso non autorizzato alla rete, proteggendo la riservatezza dei dati e la sicurezza degli utenti.",
      "spiegazione": "Il documento afferma che l’utilizzo di password robuste e crittografia è essenziale per prevenire l'accesso non autorizzato alla rete, garantendo così la riservatezza dei dati e la sicurezza degli utenti.",
      "fonte_rag": "[Fonte 3]",
      "regola_distrattori": "tre_distrattori_forti_vicini"
    }
  ]
}