import json
from pathlib import Path


# Questo script crea il primo batch di espansione.
# Obiettivo: portare il database da 27 a 100 domande totali.
# Le nuove domande vengono salvate in data/espansione/batch_100.json


PERCORSO_OUTPUT = Path("data/espansione/batch_100.json")


nuove_domande = [
    # =========================
    # AI - 17 nuove domande
    # =========================

    {
        "id": "AI-FAC-0004",
        "categoria": "ai",
        "sottocategoria": "concetti_base",
        "livello": "facile",
        "domanda": "In un sistema di intelligenza artificiale, che cosa rappresentano i dati di addestramento?",
        "opzioni": [
            "Esempi usati dal modello per imparare schemi e relazioni",
            "Comandi casuali usati solo per avviare il computer",
            "File grafici usati per colorare l'interfaccia",
            "Password necessarie per accedere al modello"
        ],
        "risposta_corretta": "Esempi usati dal modello per imparare schemi e relazioni",
        "spiegazione": "I dati di addestramento sono esempi che il modello analizza per riconoscere schemi, relazioni e regolarità utili a fare previsioni o generare risposte.",
        "tags": ["ai", "training", "dati"],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0005",
        "categoria": "ai",
        "sottocategoria": "prompt",
        "livello": "facile",
        "domanda": "Quale prompt è più chiaro per chiedere a un modello AI di riassumere un testo?",
        "opzioni": [
            "Riassumi questo testo in 5 righe usando un linguaggio semplice.",
            "Fai qualcosa con questo testo.",
            "Sistema tutto e dimmi com'è.",
            "Usa l'intelligenza artificiale sul contenuto."
        ],
        "risposta_corretta": "Riassumi questo testo in 5 righe usando un linguaggio semplice.",
        "spiegazione": "Un prompt chiaro specifica il compito, il formato e il livello di linguaggio richiesto. In questo caso il modello sa che deve produrre un riassunto di 5 righe in modo semplice.",
        "tags": ["ai", "prompt", "chiarezza"],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0006",
        "categoria": "ai",
        "sottocategoria": "classificazione",
        "livello": "facile",
        "domanda": "Se un modello AI decide se una email è spam oppure no, quale tipo di attività sta svolgendo?",
        "opzioni": [
            "Classificazione",
            "Compressione video",
            "Disegno vettoriale",
            "Crittografia manuale"
        ],
        "risposta_corretta": "Classificazione",
        "spiegazione": "La classificazione consiste nell'assegnare un elemento a una categoria. In questo caso l'email viene classificata come spam oppure non spam.",
        "tags": ["ai", "classificazione", "email"],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0007",
        "categoria": "ai",
        "sottocategoria": "modelli_linguistici",
        "livello": "facile",
        "domanda": "Che cosa fa principalmente un modello linguistico?",
        "opzioni": [
            "Lavora con il linguaggio per comprendere o generare testo",
            "Aumenta fisicamente la memoria RAM del computer",
            "Trasforma sempre le immagini in file audio",
            "Sostituisce il sistema operativo del dispositivo"
        ],
        "risposta_corretta": "Lavora con il linguaggio per comprendere o generare testo",
        "spiegazione": "Un modello linguistico elabora testo: può completare frasi, rispondere a domande, riassumere contenuti o generare nuove risposte in linguaggio naturale.",
        "tags": ["ai", "llm", "linguaggio"],
        "difficolta": 1
    },
    {
        "id": "AI-FAC-0008",
        "categoria": "ai",
        "sottocategoria": "allucinazioni",
        "livello": "facile",
        "domanda": "Quando un modello AI inventa una risposta falsa ma la presenta come sicura, come viene chiamato di solito questo problema?",
        "opzioni": [
            "Allucinazione",
            "Rendering",
            "Backup",
            "Indicizzazione"
        ],
        "risposta_corretta": "Allucinazione",
        "spiegazione": "Nel contesto dell'AI, un'allucinazione è una risposta non affidabile o inventata che il modello presenta come se fosse vera.",
        "tags": ["ai", "allucinazioni", "affidabilità"],
        "difficolta": 1
    },
    {
        "id": "AI-INT-0004",
        "categoria": "ai",
        "sottocategoria": "rag",
        "livello": "intermedio",
        "domanda": "In un sistema RAG, perché si cercano documenti esterni prima di generare la risposta?",
        "opzioni": [
            "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
            "Per impedire al modello di leggere qualsiasi testo",
            "Per sostituire completamente il database con immagini",
            "Per rendere impossibile il controllo delle fonti"
        ],
        "risposta_corretta": "Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta",
        "spiegazione": "Nel RAG il modello recupera documenti rilevanti e poi genera una risposta usando quel contesto. Questo riduce il rischio di risposte generiche o inventate.",
        "tags": ["ai", "rag", "retrieval"],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0005",
        "categoria": "ai",
        "sottocategoria": "embedding",
        "livello": "intermedio",
        "domanda": "A cosa serve un embedding in molte applicazioni di intelligenza artificiale?",
        "opzioni": [
            "A rappresentare testi, immagini o dati come vettori confrontabili",
            "A cancellare automaticamente tutti i file temporanei",
            "A trasformare ogni domanda in una password",
            "A impedire la ricerca per somiglianza semantica"
        ],
        "risposta_corretta": "A rappresentare testi, immagini o dati come vettori confrontabili",
        "spiegazione": "Un embedding trasforma un contenuto in un vettore numerico. Questo permette di confrontare contenuti simili anche quando non usano le stesse parole.",
        "tags": ["ai", "embedding", "vettori"],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0006",
        "categoria": "ai",
        "sottocategoria": "valutazione",
        "livello": "intermedio",
        "domanda": "Perché è utile testare un modello AI con esempi diversi da quelli usati in addestramento?",
        "opzioni": [
            "Per verificare se il modello generalizza anche su casi nuovi",
            "Per obbligare il modello a dimenticare tutte le regole",
            "Per misurare solo la velocità della ventola",
            "Per evitare qualsiasi confronto con risultati reali"
        ],
        "risposta_corretta": "Per verificare se il modello generalizza anche su casi nuovi",
        "spiegazione": "Un modello deve funzionare anche su dati nuovi, non solo sugli esempi già visti. Per questo si usano dati di test separati dall'addestramento.",
        "tags": ["ai", "testing", "generalizzazione"],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0007",
        "categoria": "ai",
        "sottocategoria": "prompt_engineering",
        "livello": "intermedio",
        "domanda": "Quale elemento rende più controllabile la risposta di un modello AI?",
        "opzioni": [
            "Specificare ruolo, obiettivo, vincoli e formato della risposta",
            "Scrivere soltanto una parola senza contesto",
            "Chiedere al modello di indovinare il formato",
            "Mescolare più richieste incompatibili tra loro"
        ],
        "risposta_corretta": "Specificare ruolo, obiettivo, vincoli e formato della risposta",
        "spiegazione": "Un prompt strutturato riduce l'ambiguità. Indicare ruolo, obiettivo, vincoli e formato aiuta il modello a produrre una risposta più utile e coerente.",
        "tags": ["ai", "prompt", "controllo"],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0008",
        "categoria": "ai",
        "sottocategoria": "dataset",
        "livello": "intermedio",
        "domanda": "Che cosa può succedere se un dataset contiene molti esempi sbilanciati verso una sola classe?",
        "opzioni": [
            "Il modello può imparare a favorire quella classe nelle previsioni",
            "Il modello diventa automaticamente perfetto",
            "Il dataset smette di occupare memoria",
            "La rete internet viene disattivata"
        ],
        "risposta_corretta": "Il modello può imparare a favorire quella classe nelle previsioni",
        "spiegazione": "Se una classe è molto più presente delle altre, il modello può diventare sbilanciato e prevedere troppo spesso quella classe.",
        "tags": ["ai", "dataset", "bias"],
        "difficolta": 2
    },
    {
        "id": "AI-INT-0009",
        "categoria": "ai",
        "sottocategoria": "agenti",
        "livello": "intermedio",
        "domanda": "In un agente AI, che cosa rappresenta normalmente un tool?",
        "opzioni": [
            "Uno strumento esterno che l'agente può usare per compiere un'azione",
            "Un colore obbligatorio dell'interfaccia grafica",
            "Un file che impedisce ogni risposta",
            "Una password salvata dentro il prompt"
        ],
        "risposta_corretta": "Uno strumento esterno che l'agente può usare per compiere un'azione",
        "spiegazione": "Un tool è una funzione o risorsa che l'agente può usare, per esempio cercare dati, leggere un file, fare un calcolo o interrogare un'API.",
        "tags": ["ai", "agenti", "tool"],
        "difficolta": 2
    },
    {
        "id": "AI-AV-0004",
        "categoria": "ai",
        "sottocategoria": "rag",
        "livello": "avanzato",
        "domanda": "In un sistema RAG, quale problema può nascere se il recupero dei documenti seleziona testi pertinenti solo in apparenza?",
        "opzioni": [
            "Il modello può generare una risposta ben scritta ma basata su contesto non davvero rilevante",
            "Il modello smette di produrre testo e genera solo immagini",
            "Il database viene automaticamente eliminato dal disco",
            "Il prompt diventa impossibile da inviare al modello"
        ],
        "risposta_corretta": "Il modello può generare una risposta ben scritta ma basata su contesto non davvero rilevante",
        "spiegazione": "Se il retrieval recupera documenti poco adatti, il modello può usare un contesto sbagliato e produrre una risposta apparentemente convincente ma non corretta.",
        "tags": ["ai", "rag", "retrieval", "qualità"],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0005",
        "categoria": "ai",
        "sottocategoria": "valutazione",
        "livello": "avanzato",
        "domanda": "Perché valutare un modello AI solo con risposte corrette o sbagliate può essere limitante?",
        "opzioni": [
            "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
            "Perché nessun modello può mai essere valutato in alcun modo",
            "Perché il punteggio binario aumenta automaticamente la qualità",
            "Perché le risposte lunghe sono sempre corrette"
        ],
        "risposta_corretta": "Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità",
        "spiegazione": "Molti compiti AI non hanno una sola risposta esatta. Serve valutare anche chiarezza, sicurezza, coerenza, utilità e aderenza alla richiesta.",
        "tags": ["ai", "valutazione", "qualità"],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0006",
        "categoria": "ai",
        "sottocategoria": "sicurezza",
        "livello": "avanzato",
        "domanda": "Qual è il rischio principale di un prompt injection in un'applicazione AI collegata a strumenti esterni?",
        "opzioni": [
            "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
            "Il modello migliora automaticamente la sicurezza del sistema",
            "Il codice CSS della pagina viene sempre cancellato",
            "Il database JSON viene trasformato in un'immagine"
        ],
        "risposta_corretta": "Il modello può essere spinto a ignorare istruzioni originali e usare strumenti in modo non previsto",
        "spiegazione": "Una prompt injection prova a manipolare il comportamento del modello. Se il modello può usare tool esterni, il rischio aumenta perché potrebbe compiere azioni non desiderate.",
        "tags": ["ai", "sicurezza", "prompt injection"],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0007",
        "categoria": "ai",
        "sottocategoria": "fine_tuning",
        "livello": "avanzato",
        "domanda": "Quando ha più senso valutare il fine-tuning rispetto al solo prompt engineering?",
        "opzioni": [
            "Quando servono comportamenti stabili e specifici su molti esempi simili",
            "Quando basta fare una singola domanda generica",
            "Quando non esistono dati di esempio affidabili",
            "Quando si vuole evitare qualunque controllo sul risultato"
        ],
        "risposta_corretta": "Quando servono comportamenti stabili e specifici su molti esempi simili",
        "spiegazione": "Il fine-tuning può essere utile quando il modello deve seguire uno stile, un formato o un comportamento specifico in modo ripetibile su molti casi.",
        "tags": ["ai", "fine tuning", "prompt engineering"],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0008",
        "categoria": "ai",
        "sottocategoria": "architetture",
        "livello": "avanzato",
        "domanda": "In una pipeline AI, perché conviene separare recupero delle informazioni, generazione e controllo finale?",
        "opzioni": [
            "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
            "Per impedire al sistema di produrre qualsiasi output",
            "Per duplicare casualmente tutte le risposte",
            "Per sostituire il modello con un file vuoto"
        ],
        "risposta_corretta": "Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore",
        "spiegazione": "Separare le fasi aiuta a capire se un errore nasce dal retrieval, dal modello generativo o dal controllo finale. Questo rende il sistema più debuggabile.",
        "tags": ["ai", "pipeline", "architettura"],
        "difficolta": 3
    },
    {
        "id": "AI-AV-0009",
        "categoria": "ai",
        "sottocategoria": "bias",
        "livello": "avanzato",
        "domanda": "Perché un modello AI può produrre risultati distorti anche se l'algoritmo è implementato correttamente?",
        "opzioni": [
            "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
            "Perché un algoritmo corretto produce sempre risultati neutrali",
            "Perché i bias dipendono solo dal colore dello schermo",
            "Perché la distorsione è impossibile nei sistemi automatici"
        ],
        "risposta_corretta": "Perché i dati, gli obiettivi di addestramento o le metriche possono introdurre distorsioni",
        "spiegazione": "Un sistema può essere tecnicamente corretto ma imparare schemi distorti se i dati o gli obiettivi contengono squilibri o rappresentazioni non neutrali.",
        "tags": ["ai", "bias", "etica"],
        "difficolta": 3
    },

    # =========================
    # INFORMATICA - 17 nuove domande
    # =========================

    {
        "id": "INF-FAC-0004",
        "categoria": "informatica",
        "sottocategoria": "web",
        "livello": "facile",
        "domanda": "Quale linguaggio viene usato principalmente per definire la struttura di una pagina web?",
        "opzioni": ["HTML", "SQL", "Python", "JSON"],
        "risposta_corretta": "HTML",
        "spiegazione": "HTML definisce la struttura della pagina, per esempio titoli, paragrafi, immagini, link e sezioni.",
        "tags": ["web", "html", "frontend"],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0005",
        "categoria": "informatica",
        "sottocategoria": "database",
        "livello": "facile",
        "domanda": "In un database, che cosa rappresenta normalmente una tabella?",
        "opzioni": [
            "Un insieme organizzato di righe e colonne",
            "Un'immagine compressa",
            "Un cavo di rete",
            "Una password temporanea"
        ],
        "risposta_corretta": "Un insieme organizzato di righe e colonne",
        "spiegazione": "Una tabella organizza i dati in righe e colonne. Ogni riga rappresenta spesso un record, mentre le colonne rappresentano i campi.",
        "tags": ["database", "tabelle", "dati"],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0006",
        "categoria": "informatica",
        "sottocategoria": "programmazione",
        "livello": "facile",
        "domanda": "A cosa serve una variabile in programmazione?",
        "opzioni": [
            "A conservare un valore che può essere usato o modificato",
            "A spegnere automaticamente il monitor",
            "A eliminare il sistema operativo",
            "A impedire l'esecuzione del codice"
        ],
        "risposta_corretta": "A conservare un valore che può essere usato o modificato",
        "spiegazione": "Una variabile è un contenitore con un nome. Serve a salvare un valore, leggerlo e usarlo durante l'esecuzione del programma.",
        "tags": ["programmazione", "variabili", "base"],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0007",
        "categoria": "informatica",
        "sottocategoria": "internet",
        "livello": "facile",
        "domanda": "Che cosa indica normalmente un URL?",
        "opzioni": [
            "L'indirizzo di una risorsa sul web",
            "La quantità di memoria RAM disponibile",
            "Il formato interno della batteria",
            "Il nome del processore grafico"
        ],
        "risposta_corretta": "L'indirizzo di una risorsa sul web",
        "spiegazione": "Un URL identifica dove si trova una risorsa online, per esempio una pagina web, un'immagine o un file.",
        "tags": ["web", "url", "internet"],
        "difficolta": 1
    },
    {
        "id": "INF-FAC-0008",
        "categoria": "informatica",
        "sottocategoria": "file",
        "livello": "facile",
        "domanda": "Quale formato è adatto a rappresentare dati strutturati leggibili da molte applicazioni?",
        "opzioni": ["JSON", "MP3", "PNG", "MOV"],
        "risposta_corretta": "JSON",
        "spiegazione": "JSON è un formato testuale usato per rappresentare dati strutturati, come oggetti, liste, stringhe e numeri.",
        "tags": ["json", "dati", "formati"],
        "difficolta": 1
    },
    {
        "id": "INF-INT-0004",
        "categoria": "informatica",
        "sottocategoria": "api",
        "livello": "intermedio",
        "domanda": "In una richiesta HTTP, quale metodo viene usato di solito per ottenere dati senza modificarli?",
        "opzioni": ["GET", "POST", "DELETE", "PATCH"],
        "risposta_corretta": "GET",
        "spiegazione": "GET viene usato normalmente per leggere o recuperare dati. POST, PATCH e DELETE sono più legati a creazione, modifica o eliminazione di risorse.",
        "tags": ["http", "api", "backend"],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0005",
        "categoria": "informatica",
        "sottocategoria": "database",
        "livello": "intermedio",
        "domanda": "Perché si usa una chiave primaria in una tabella di database?",
        "opzioni": [
            "Per identificare in modo univoco ogni record",
            "Per colorare automaticamente le righe",
            "Per impedire qualunque ricerca",
            "Per trasformare i dati in immagini"
        ],
        "risposta_corretta": "Per identificare in modo univoco ogni record",
        "spiegazione": "La chiave primaria identifica ogni riga in modo univoco. Questo evita ambiguità quando si cercano, aggiornano o collegano record.",
        "tags": ["database", "chiave primaria", "sql"],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0006",
        "categoria": "informatica",
        "sottocategoria": "frontend",
        "livello": "intermedio",
        "domanda": "In una pagina web, qual è il ruolo principale del CSS?",
        "opzioni": [
            "Gestire l'aspetto visivo degli elementi",
            "Salvare dati in tabelle relazionali",
            "Eseguire query SQL sul server",
            "Compilare il codice macchina del processore"
        ],
        "risposta_corretta": "Gestire l'aspetto visivo degli elementi",
        "spiegazione": "CSS controlla lo stile della pagina: colori, dimensioni, layout, spaziature, bordi, animazioni e comportamento visivo responsive.",
        "tags": ["css", "frontend", "web"],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0007",
        "categoria": "informatica",
        "sottocategoria": "debug",
        "livello": "intermedio",
        "domanda": "Che cosa significa fare debug di un programma?",
        "opzioni": [
            "Individuare e correggere errori nel comportamento del codice",
            "Aumentare la luminosità dello schermo",
            "Convertire sempre il codice in un'immagine",
            "Cancellare tutti i file del progetto"
        ],
        "risposta_corretta": "Individuare e correggere errori nel comportamento del codice",
        "spiegazione": "Il debug è il processo con cui si analizza un programma, si trovano errori o comportamenti inattesi e si correggono.",
        "tags": ["debug", "programmazione", "errori"],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0008",
        "categoria": "informatica",
        "sottocategoria": "git",
        "livello": "intermedio",
        "domanda": "In Git, che cosa rappresenta un commit?",
        "opzioni": [
            "Una fotografia salvata dello stato del progetto",
            "Un virus installato nel repository",
            "Una cartella temporanea del browser",
            "Una modifica che non può essere tracciata"
        ],
        "risposta_corretta": "Una fotografia salvata dello stato del progetto",
        "spiegazione": "Un commit salva uno stato del progetto con un messaggio descrittivo. Permette di tenere traccia delle modifiche nel tempo.",
        "tags": ["git", "versionamento", "commit"],
        "difficolta": 2
    },
    {
        "id": "INF-INT-0009",
        "categoria": "informatica",
        "sottocategoria": "sicurezza",
        "livello": "intermedio",
        "domanda": "Perché è rischioso salvare password direttamente nel codice sorgente?",
        "opzioni": [
            "Perché possono finire in repository, log o copie condivise del progetto",
            "Perché il codice diventa sempre più veloce",
            "Perché il computer smette di usare la tastiera",
            "Perché le password diventano automaticamente pubblicità"
        ],
        "risposta_corretta": "Perché possono finire in repository, log o copie condivise del progetto",
        "spiegazione": "Le password nel codice possono essere esposte facilmente, soprattutto se il progetto viene caricato online. È meglio usare variabili d'ambiente o sistemi di gestione dei segreti.",
        "tags": ["sicurezza", "password", "git"],
        "difficolta": 2
    },
    {
        "id": "INF-AV-0004",
        "categoria": "informatica",
        "sottocategoria": "architettura",
        "livello": "avanzato",
        "domanda": "Perché separare frontend e backend rende spesso un'applicazione più gestibile?",
        "opzioni": [
            "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
            "Perché impedisce al backend di ricevere qualsiasi richiesta",
            "Perché elimina la necessità di testare il codice",
            "Perché trasforma automaticamente il progetto in un videogioco"
        ],
        "risposta_corretta": "Perché interfaccia, logica applicativa e dati possono evolvere con responsabilità più chiare",
        "spiegazione": "Separare frontend e backend aiuta a organizzare meglio il progetto. Il frontend gestisce l'interazione utente, mentre il backend gestisce logica, dati e API.",
        "tags": ["frontend", "backend", "architettura"],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0005",
        "categoria": "informatica",
        "sottocategoria": "api",
        "livello": "avanzato",
        "domanda": "Che cosa può indicare una risposta HTTP 401 in una API protetta?",
        "opzioni": [
            "La richiesta non è autenticata correttamente",
            "La richiesta è stata completata con successo",
            "Il server ha inviato un'immagine troppo grande",
            "Il client ha chiesto di cambiare colore alla pagina"
        ],
        "risposta_corretta": "La richiesta non è autenticata correttamente",
        "spiegazione": "Il codice 401 indica normalmente un problema di autenticazione: il client non ha fornito credenziali valide o non è autorizzato ad accedere senza login.",
        "tags": ["api", "http", "sicurezza"],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0006",
        "categoria": "informatica",
        "sottocategoria": "database",
        "livello": "avanzato",
        "domanda": "Qual è il vantaggio principale di usare un indice su una colonna molto cercata di un database?",
        "opzioni": [
            "Rendere più veloci alcune ricerche su quella colonna",
            "Rendere impossibile ogni ordinamento",
            "Trasformare la tabella in un file audio",
            "Cancellare automaticamente le righe duplicate"
        ],
        "risposta_corretta": "Rendere più veloci alcune ricerche su quella colonna",
        "spiegazione": "Un indice può accelerare le ricerche perché permette al database di trovare i record senza scorrere tutta la tabella. Ha però un costo in spazio e aggiornamenti.",
        "tags": ["database", "indice", "prestazioni"],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0007",
        "categoria": "informatica",
        "sottocategoria": "concorrenza",
        "livello": "avanzato",
        "domanda": "Perché due operazioni simultanee sullo stesso dato possono creare problemi in un'applicazione?",
        "opzioni": [
            "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
            "Perché impediscono sempre al server di accendersi",
            "Perché cancellano automaticamente il codice sorgente",
            "Perché trasformano ogni numero in testo casuale"
        ],
        "risposta_corretta": "Perché possono produrre risultati incoerenti se non vengono gestite correttamente",
        "spiegazione": "Se più operazioni modificano lo stesso dato senza controllo, si possono creare conflitti, aggiornamenti persi o stati incoerenti. Per questo si usano transazioni o meccanismi di sincronizzazione.",
        "tags": ["concorrenza", "transazioni", "backend"],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0008",
        "categoria": "informatica",
        "sottocategoria": "testing",
        "livello": "avanzato",
        "domanda": "Perché un test automatico utile deve avere un risultato atteso ben definito?",
        "opzioni": [
            "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
            "Perché il test deve cambiare casualmente a ogni esecuzione",
            "Perché il test serve solo a colorare il terminale",
            "Perché un test non dovrebbe mai verificare il risultato"
        ],
        "risposta_corretta": "Perché il test deve poter stabilire se il comportamento ottenuto è corretto o no",
        "spiegazione": "Un test automatico confronta il risultato prodotto dal codice con un risultato atteso. Senza un risultato atteso chiaro, il test non può dire se il comportamento è corretto.",
        "tags": ["testing", "qualità", "software"],
        "difficolta": 3
    },
    {
        "id": "INF-AV-0009",
        "categoria": "informatica",
        "sottocategoria": "deploy",
        "livello": "avanzato",
        "domanda": "Perché una variabile d'ambiente è utile quando si pubblica un'applicazione?",
        "opzioni": [
            "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
            "Serve solo a cambiare il font del browser",
            "Obbliga l'applicazione a funzionare senza server",
            "Trasforma ogni file JSON in una tabella SQL"
        ],
        "risposta_corretta": "Permette di separare configurazioni sensibili o diverse dal codice sorgente",
        "spiegazione": "Le variabili d'ambiente permettono di gestire dati come chiavi, URL o configurazioni senza scriverli direttamente nel codice.",
        "tags": ["deploy", "ambiente", "configurazione"],
        "difficolta": 3
    },

    # =========================
    # MATEMATICA - 17 nuove domande
    # =========================

    {
        "id": "MAT-FAC-0004",
        "categoria": "matematica",
        "sottocategoria": "frazioni",
        "livello": "facile",
        "domanda": "Quanto vale tre quarti di 80?",
        "opzioni": ["40", "50", "60", "70"],
        "risposta_corretta": "60",
        "spiegazione": "Tre quarti di 80 significa dividere 80 in 4 parti uguali e prenderne 3. Prima calcoliamo 80 / 4 = 20, poi facciamo 20 × 3 = 60.",
        "tags": ["frazioni", "calcolo", "parte_di_un_totale"],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0005",
        "categoria": "matematica",
        "sottocategoria": "proporzioni",
        "livello": "facile",
        "domanda": "Se 3 quaderni costano 6 euro, quanto costano 5 quaderni allo stesso prezzo unitario?",
        "opzioni": ["8 euro", "9 euro", "10 euro", "12 euro"],
        "risposta_corretta": "10 euro",
        "spiegazione": "Ogni quaderno costa 6 / 3 = 2 euro. Quindi 5 quaderni costano 5 × 2 = 10 euro.",
        "tags": ["proporzioni", "prezzo_unitario"],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0006",
        "categoria": "matematica",
        "sottocategoria": "aritmetica",
        "livello": "facile",
        "domanda": "Qual è il risultato di 18 + 7 × 2?",
        "opzioni": ["32", "50", "25", "36"],
        "risposta_corretta": "32",
        "spiegazione": "Prima si esegue la moltiplicazione: 7 × 2 = 14. Poi 18 + 14 = 32.",
        "tags": ["operazioni", "precedenza"],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0007",
        "categoria": "matematica",
        "sottocategoria": "frazioni",
        "livello": "facile",
        "domanda": "Quale frazione è equivalente a 1/2?",
        "opzioni": ["2/4", "2/3", "3/5", "4/6"],
        "risposta_corretta": "2/4",
        "spiegazione": "Una frazione equivalente ha lo stesso valore. 2/4 si semplifica dividendo numeratore e denominatore per 2, ottenendo 1/2.",
        "tags": ["frazioni", "equivalenza"],
        "difficolta": 1
    },
    {
        "id": "MAT-FAC-0008",
        "categoria": "matematica",
        "sottocategoria": "geometria",
        "livello": "facile",
        "domanda": "Qual è l'area di un rettangolo con base 8 cm e altezza 5 cm?",
        "opzioni": ["13 cm²", "26 cm²", "40 cm²", "80 cm²"],
        "risposta_corretta": "40 cm²",
        "spiegazione": "L'area del rettangolo si calcola con base × altezza. Quindi 8 × 5 = 40 cm².",
        "tags": ["geometria", "area", "rettangolo"],
        "difficolta": 1
    },
    {
        "id": "MAT-INT-0004",
        "categoria": "matematica",
        "sottocategoria": "equazioni",
        "livello": "intermedio",
        "domanda": "Risolvi l'equazione: 3x + 5 = 20.",
        "opzioni": ["x = 4", "x = 5", "x = 6", "x = 7"],
        "risposta_corretta": "x = 5",
        "spiegazione": "Sottrai 5 da entrambi i membri: 3x = 15. Poi dividi per 3: x = 5.",
        "tags": ["equazioni", "algebra"],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0005",
        "categoria": "matematica",
        "sottocategoria": "percentuali",
        "livello": "intermedio",
        "domanda": "Un prodotto costa 80 euro e viene scontato del 25%. Qual è il prezzo finale?",
        "opzioni": ["55 euro", "60 euro", "65 euro", "70 euro"],
        "risposta_corretta": "60 euro",
        "spiegazione": "Il 25% di 80 è 20. Il prezzo finale è 80 - 20 = 60 euro.",
        "tags": ["percentuali", "sconto"],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0006",
        "categoria": "matematica",
        "sottocategoria": "media",
        "livello": "intermedio",
        "domanda": "La media di 6, 8, 10 e 12 è:",
        "opzioni": ["8", "9", "10", "11"],
        "risposta_corretta": "9",
        "spiegazione": "Sommiamo i valori: 6 + 8 + 10 + 12 = 36. Poi dividiamo per 4 valori: 36 / 4 = 9.",
        "tags": ["media", "statistica_base"],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0007",
        "categoria": "matematica",
        "sottocategoria": "rapporti",
        "livello": "intermedio",
        "domanda": "In una classe il rapporto tra studenti assenti e presenti è 1:5. Se gli assenti sono 4, quanti sono i presenti?",
        "opzioni": ["16", "18", "20", "24"],
        "risposta_corretta": "20",
        "spiegazione": "Il rapporto 1:5 significa che per ogni assente ci sono 5 presenti. Se gli assenti sono 4, i presenti sono 4 × 5 = 20.",
        "tags": ["rapporti", "proporzioni"],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0008",
        "categoria": "matematica",
        "sottocategoria": "geometria",
        "livello": "intermedio",
        "domanda": "Un quadrato ha perimetro 36 cm. Quanto misura il suo lato?",
        "opzioni": ["6 cm", "8 cm", "9 cm", "12 cm"],
        "risposta_corretta": "9 cm",
        "spiegazione": "Il perimetro del quadrato è 4 volte il lato. Quindi il lato misura 36 / 4 = 9 cm.",
        "tags": ["geometria", "perimetro", "quadrato"],
        "difficolta": 2
    },
    {
        "id": "MAT-INT-0009",
        "categoria": "matematica",
        "sottocategoria": "probabilita",
        "livello": "intermedio",
        "domanda": "In un sacchetto ci sono 3 palline rosse e 7 blu. Qual è la probabilità di estrarre una pallina rossa?",
        "opzioni": ["3/10", "7/10", "3/7", "1/3"],
        "risposta_corretta": "3/10",
        "spiegazione": "Le palline totali sono 3 + 7 = 10. Le rosse sono 3, quindi la probabilità è 3/10.",
        "tags": ["probabilità", "frazioni"],
        "difficolta": 2
    },
    {
        "id": "MAT-AV-0004",
        "categoria": "matematica",
        "sottocategoria": "problemi",
        "livello": "avanzato",
        "domanda": "Un numero aumentato del suo 30% diventa 65. Qual era il numero iniziale?",
        "opzioni": ["45", "50", "55", "60"],
        "risposta_corretta": "50",
        "spiegazione": "Se il numero iniziale è x, dopo l'aumento del 30% diventa 1,3x. Quindi 1,3x = 65 e x = 65 / 1,3 = 50.",
        "tags": ["percentuali_inverse", "equazioni"],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0005",
        "categoria": "matematica",
        "sottocategoria": "velocita",
        "livello": "avanzato",
        "domanda": "Un treno percorre 180 km in 2 ore e 15 minuti. Qual è la sua velocità media?",
        "opzioni": ["75 km/h", "80 km/h", "85 km/h", "90 km/h"],
        "risposta_corretta": "80 km/h",
        "spiegazione": "2 ore e 15 minuti non sono 2,15 ore: i 15 minuti vanno trasformati in ore. Poiché 15 minuti sono 15/60 = 0,25 ore, il tempo totale è 2 + 0,25 = 2,25 ore. La velocità media si calcola facendo distanza / tempo, quindi 180 / 2,25 = 80 km/h.",
        "tags": ["velocità", "tempo", "problemi"],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0006",
        "categoria": "matematica",
        "sottocategoria": "algebra",
        "livello": "avanzato",
        "domanda": "Se 2x - 3 = x + 9, quale valore ha x?",
        "opzioni": ["9", "10", "11", "12"],
        "risposta_corretta": "12",
        "spiegazione": "Portiamo x a sinistra e -3 a destra: 2x - x = 9 + 3. Quindi x = 12.",
        "tags": ["algebra", "equazioni"],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0007",
        "categoria": "matematica",
        "sottocategoria": "combinazioni",
        "livello": "avanzato",
        "domanda": "Quanti codici diversi di 2 cifre si possono formare usando le cifre 1, 2, 3, 4 senza ripetizione?",
        "opzioni": ["8", "10", "12", "16"],
        "risposta_corretta": "12",
        "spiegazione": "Per la prima cifra ci sono 4 scelte. Per la seconda restano 3 scelte, perché non si può ripetere la cifra. Quindi 4 × 3 = 12 codici.",
        "tags": ["combinatoria", "conteggio"],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0008",
        "categoria": "matematica",
        "sottocategoria": "problemi",
        "livello": "avanzato",
        "domanda": "La somma di due numeri è 48 e uno è il doppio dell'altro. Qual è il numero maggiore?",
        "opzioni": ["24", "28", "32", "36"],
        "risposta_corretta": "32",
        "spiegazione": "Se il numero minore è x, il maggiore è 2x. Quindi x + 2x = 48, cioè 3x = 48. Il minore è 16 e il maggiore è 32.",
        "tags": ["problemi", "equazioni"],
        "difficolta": 3
    },
    {
        "id": "MAT-AV-0009",
        "categoria": "matematica",
        "sottocategoria": "percentuali",
        "livello": "avanzato",
        "domanda": "Un valore passa da 120 a 150. Qual è l'aumento percentuale?",
        "opzioni": ["20%", "25%", "30%", "35%"],
        "risposta_corretta": "25%",
        "spiegazione": "L'aumento è 150 - 120 = 30. La percentuale di aumento è 30 / 120 × 100 = 25%.",
        "tags": ["percentuali", "variazione"],
        "difficolta": 3
    },

    # =========================
    # INGLESE - 17 nuove domande
    # =========================

    {
        "id": "ING-FAC-0004",
        "categoria": "inglese",
        "sottocategoria": "verbo_essere",
        "livello": "facile",
        "domanda": "Quale frase inglese è corretta?",
        "opzioni": [
            "They are students.",
            "They is students.",
            "They am students.",
            "They be students."
        ],
        "risposta_corretta": "They are students.",
        "spiegazione": "La frase corretta è 'They are students' perché 'they' significa 'loro' ed è un soggetto plurale. Con i soggetti plurali come 'we' e 'they' si usa 'are'. 'Is' si usa con soggetti singolari come 'he', 'she' e 'it', mentre 'am' si usa solo con 'I'.",
        "tags": ["inglese", "to be", "grammatica"],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0005",
        "categoria": "inglese",
        "sottocategoria": "articoli",
        "livello": "facile",
        "domanda": "Completa la frase: I have ___ apple in my bag.",
        "opzioni": ["an", "a", "the", "some"],
        "risposta_corretta": "an",
        "spiegazione": "Si usa 'an' davanti a parole che iniziano con suono vocalico, come 'apple'.",
        "tags": ["inglese", "articoli", "base"],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0006",
        "categoria": "inglese",
        "sottocategoria": "lessico",
        "livello": "facile",
        "domanda": "Quale parola inglese indica il contrario di 'hot'?",
        "opzioni": ["cold", "warm", "dry", "soft"],
        "risposta_corretta": "cold",
        "spiegazione": "'Hot' significa caldo. Il contrario più diretto è 'cold', cioè freddo.",
        "tags": ["inglese", "vocabolario", "opposti"],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0007",
        "categoria": "inglese",
        "sottocategoria": "preposizioni",
        "livello": "facile",
        "domanda": "Completa la frase: The book is ___ the table.",
        "opzioni": ["on", "at", "to", "from"],
        "risposta_corretta": "on",
        "spiegazione": "Si usa 'on' quando qualcosa si trova sopra una superficie. La frase significa: il libro è sul tavolo.",
        "tags": ["inglese", "preposizioni", "base"],
        "difficolta": 1
    },
    {
        "id": "ING-FAC-0008",
        "categoria": "inglese",
        "sottocategoria": "plurali",
        "livello": "facile",
        "domanda": "Qual è il plurale corretto di 'child'?",
        "opzioni": ["children", "childs", "childes", "childrens"],
        "risposta_corretta": "children",
        "spiegazione": "'Child' ha un plurale irregolare: 'children'. Le altre forme non sono corrette.",
        "tags": ["inglese", "plurali", "irregolari"],
        "difficolta": 1
    },
    {
        "id": "ING-INT-0004",
        "categoria": "inglese",
        "sottocategoria": "past_simple",
        "livello": "intermedio",
        "domanda": "Quale frase usa correttamente il past simple?",
        "opzioni": [
            "She visited London last year.",
            "She has visited London last year.",
            "She visit London last year.",
            "She was visit London last year."
        ],
        "risposta_corretta": "She visited London last year.",
        "spiegazione": "Con un tempo passato preciso come 'last year' si usa il past simple. 'Visited' è la forma corretta del verbo regolare al passato.",
        "tags": ["inglese", "past simple", "grammatica"],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0005",
        "categoria": "inglese",
        "sottocategoria": "comparativi",
        "livello": "intermedio",
        "domanda": "Completa la frase: This exercise is ___ than the previous one.",
        "opzioni": ["more difficult", "most difficult", "difficulty", "difficultest"],
        "risposta_corretta": "more difficult",
        "spiegazione": "Per formare il comparativo di un aggettivo lungo come 'difficult' si usa 'more difficult'.",
        "tags": ["inglese", "comparativi", "aggettivi"],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0006",
        "categoria": "inglese",
        "sottocategoria": "modali",
        "livello": "intermedio",
        "domanda": "Quale frase esprime meglio un obbligo?",
        "opzioni": [
            "You must wear a helmet.",
            "You might wear a helmet.",
            "You could wear a helmet.",
            "You would wear a helmet."
        ],
        "risposta_corretta": "You must wear a helmet.",
        "spiegazione": "'Must' esprime obbligo o necessità forte. 'Might', 'could' e 'would' indicano possibilità o condizione, non obbligo.",
        "tags": ["inglese", "modali", "must"],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0007",
        "categoria": "inglese",
        "sottocategoria": "conditionals",
        "livello": "intermedio",
        "domanda": "Completa la frase: If it rains tomorrow, we ___ at home.",
        "opzioni": ["will stay", "stayed", "have stayed", "stay yesterday"],
        "risposta_corretta": "will stay",
        "spiegazione": "Nel first conditional si usa if + present simple e will + verbo base. Quindi: If it rains tomorrow, we will stay at home.",
        "tags": ["inglese", "conditionals", "future"],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0008",
        "categoria": "inglese",
        "sottocategoria": "phrasal_verbs",
        "livello": "intermedio",
        "domanda": "Nella frase 'Please turn off the light', che cosa significa 'turn off'?",
        "opzioni": ["spegnere", "accendere", "spostare", "rompere"],
        "risposta_corretta": "spegnere",
        "spiegazione": "'Turn off' significa spegnere. La frase chiede di spegnere la luce.",
        "tags": ["inglese", "phrasal verbs", "lessico"],
        "difficolta": 2
    },
    {
        "id": "ING-INT-0009",
        "categoria": "inglese",
        "sottocategoria": "comprensione",
        "livello": "intermedio",
        "domanda": "Quale frase corrisponde meglio a: 'Non vedo l'ora di iniziare il corso'?",
        "opzioni": [
            "I am looking forward to starting the course.",
            "I am looking after starting the course.",
            "I am looking for starting the course.",
            "I am looking through starting the course."
        ],
        "risposta_corretta": "I am looking forward to starting the course.",
        "spiegazione": "'Look forward to' significa non vedere l'ora di fare qualcosa. Dopo 'to' in questa espressione si usa il verbo in -ing.",
        "tags": ["inglese", "espressioni", "comprensione"],
        "difficolta": 2
    },
    {
        "id": "ING-AV-0004",
        "categoria": "inglese",
        "sottocategoria": "connettivi",
        "livello": "avanzato",
        "domanda": "Completa la frase: The system is powerful; ___, it requires careful testing before deployment.",
        "opzioni": ["however", "therefore", "because", "unless"],
        "risposta_corretta": "however",
        "spiegazione": "'However' introduce un contrasto: il sistema è potente, ma richiede comunque test accurati prima della pubblicazione.",
        "tags": ["inglese", "connettivi", "contrasto"],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0005",
        "categoria": "inglese",
        "sottocategoria": "relative_clauses",
        "livello": "avanzato",
        "domanda": "Scegli la frase corretta:",
        "opzioni": [
            "The developer who fixed the bug updated the repository.",
            "The developer which fixed the bug updated the repository.",
            "The developer what fixed the bug updated the repository.",
            "The developer where fixed the bug updated the repository."
        ],
        "risposta_corretta": "The developer who fixed the bug updated the repository.",
        "spiegazione": "Per riferirsi a una persona in una frase relativa si usa 'who'. Per questo la forma corretta è 'The developer who fixed the bug...'.",
        "tags": ["inglese", "relative clauses", "grammatica"],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0006",
        "categoria": "inglese",
        "sottocategoria": "passive_voice",
        "livello": "avanzato",
        "domanda": "Quale frase usa correttamente la forma passiva?",
        "opzioni": [
            "The report was reviewed by the team.",
            "The report reviewed by the team was.",
            "The report has review by the team.",
            "The report is reviewing by the team."
        ],
        "risposta_corretta": "The report was reviewed by the team.",
        "spiegazione": "La forma passiva corretta usa il verbo 'to be' più il participio passato: 'was reviewed'.",
        "tags": ["inglese", "passivo", "grammatica"],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0007",
        "categoria": "inglese",
        "sottocategoria": "sfumature",
        "livello": "avanzato",
        "domanda": "Quale frase esprime meglio un consiglio formale?",
        "opzioni": [
            "You should consider updating the documentation.",
            "You must maybe update the documentation.",
            "You can to update the documentation.",
            "You would updating the documentation."
        ],
        "risposta_corretta": "You should consider updating the documentation.",
        "spiegazione": "'Should consider' è una forma adatta per dare un consiglio in modo educato e relativamente formale.",
        "tags": ["inglese", "registro", "consigli"],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0008",
        "categoria": "inglese",
        "sottocategoria": "reported_speech",
        "livello": "avanzato",
        "domanda": "Quale frase trasforma correttamente 'I am working on the project' nel discorso indiretto?",
        "opzioni": [
            "He said that he was working on the project.",
            "He said that he is work on the project.",
            "He said that he working on the project.",
            "He said that he has work on the project."
        ],
        "risposta_corretta": "He said that he was working on the project.",
        "spiegazione": "Nel discorso indiretto, il present continuous 'am working' diventa spesso past continuous: 'was working'.",
        "tags": ["inglese", "reported speech", "grammatica"],
        "difficolta": 3
    },
    {
        "id": "ING-AV-0009",
        "categoria": "inglese",
        "sottocategoria": "lessico_tecnico",
        "livello": "avanzato",
        "domanda": "Nel contesto software, quale frase rende meglio 'The feature is backward compatible'?",
        "opzioni": [
            "La funzionalità è compatibile con versioni precedenti.",
            "La funzionalità funziona solo andando all'indietro.",
            "La funzionalità cancella le versioni precedenti.",
            "La funzionalità è incompatibile con il passato."
        ],
        "risposta_corretta": "La funzionalità è compatibile con versioni precedenti.",
        "spiegazione": "'Backward compatible' significa che una funzionalità mantiene compatibilità con versioni precedenti del sistema o del software.",
        "tags": ["inglese", "lessico_tecnico", "software"],
        "difficolta": 3
    },

    # =========================
    # LOGICA - 5 nuove domande
    # =========================

    {
        "id": "LOG-CRI-INT-0004",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "intermedio",
        "domanda": "Tutti i tecnici controllano i log. Alcuni tecnici documentano gli errori. Quale conclusione è sicuramente vera?",
        "opzioni": [
            "Alcune persone che documentano gli errori controllano i log",
            "Tutti quelli che controllano i log documentano errori",
            "Nessun tecnico documenta errori",
            "Chi documenta errori non controlla mai i log"
        ],
        "risposta_corretta": "Alcune persone che documentano gli errori controllano i log",
        "spiegazione": "Se alcuni tecnici documentano gli errori e tutti i tecnici controllano i log, allora quelle persone documentano errori e controllano anche i log.",
        "tags": ["sillogismi", "ragionamento_critico"],
        "difficolta": 2
    },
    {
        "id": "LOG-CRI-AV-0005",
        "categoria": "logica",
        "sottocategoria": "ragionamento_critico",
        "livello": "avanzato",
        "domanda": "Un'app è stata aggiornata e subito dopo alcuni utenti segnalano errori. Quale conclusione è più prudente?",
        "opzioni": [
            "L'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche",
            "L'aggiornamento è certamente l'unica causa possibile",
            "Gli errori non possono dipendere dall'aggiornamento",
            "Gli utenti hanno sicuramente usato l'app in modo sbagliato"
        ],
        "risposta_corretta": "L'aggiornamento potrebbe essere collegato agli errori, ma servono ulteriori verifiche",
        "spiegazione": "La vicinanza temporale suggerisce una possibile relazione, ma non dimostra da sola una causa certa. Servono log, test e confronto con altri fattori.",
        "tags": ["causalità", "ragionamento_critico", "debug"],
        "difficolta": 3
    },
    {
        "id": "LOG-AST-INT-0004",
        "categoria": "logica",
        "sottocategoria": "ragionamento_astratto",
        "livello": "intermedio",
        "domanda": "Osserva le trasformazioni: A1 → B2, C3 → D4, E5 → ?",
        "opzioni": ["F6", "E6", "F5", "G6"],
        "risposta_corretta": "F6",
        "spiegazione": "In ogni trasformazione la lettera avanza di una posizione nell'alfabeto e il numero aumenta di 1. Quindi E5 diventa F6.",
        "tags": ["trasformazioni", "lettere", "numeri"],
        "difficolta": 2
    },
    {
        "id": "LOG-VER-INT-0004",
        "categoria": "logica",
        "sottocategoria": "logica_verbale",
        "livello": "intermedio",
        "domanda": "Quale coppia mantiene meglio la relazione: seme → pianta?",
        "opzioni": [
            "bozza → documento",
            "libro → pagina",
            "porta → chiave",
            "strada → automobile"
        ],
        "risposta_corretta": "bozza → documento",
        "spiegazione": "Un seme può svilupparsi in una pianta. Allo stesso modo una bozza può svilupparsi in un documento completo.",
        "tags": ["analogie", "relazioni"],
        "difficolta": 2
    },
    {
        "id": "LOG-NUM-AV-0004",
        "categoria": "logica",
        "sottocategoria": "logica_numerica",
        "livello": "avanzato",
        "domanda": "Completa la sequenza: 5, 11, 10, 22, 21, 42, ?",
        "opzioni": ["40", "41", "43", "44"],
        "risposta_corretta": "41",
        "spiegazione": "La sequenza alterna due operazioni: ×2 + 1, poi -1. Infatti 5 × 2 + 1 = 11, 11 - 1 = 10, 10 × 2 + 2 = 22, 22 - 1 = 21, 21 × 2 = 42. Il passo successivo è 42 - 1 = 41.",
        "tags": ["sequenze", "operazioni_alternate", "logica_numerica"],
        "difficolta": 3
    }
]


def main():
    PERCORSO_OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with open(PERCORSO_OUTPUT, "w", encoding="utf-8") as file:
        json.dump(
            nuove_domande,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("File creato correttamente:")
    print(PERCORSO_OUTPUT)
    print(f"Domande create: {len(nuove_domande)}")


main()