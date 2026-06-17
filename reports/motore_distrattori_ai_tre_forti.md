# Motore distrattori AI - tre distrattori forti

Regola nuova: ogni domanda deve avere una risposta corretta e tre distrattori forti.

Domande controllate: 80
Domande problematiche: 80

## Prime domande da correggere

---

### AI-AV-0008

Livello: `avanzato`

Gravità: `175`

Domanda: In una pipeline AI, perché conviene separare recupero delle informazioni, generazione e controllo finale?

Opzioni:

- A. Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore ✅
- B. Per valutare separatamente le fasi, ma senza collegare gli errori alla risposta finale
- C. Per controllare solo il recupero dei documenti ignorando la generazione
- D. Per controllare solo la generazione ignorando retrieval e verifica finale

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.33.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.318.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: contiene parole che la rendono eliminabile: solo, ignorando.
- Opzione D: troppo lontana dalla corretta, similarità 0.303.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: contiene parole che la rendono eliminabile: solo, ignorando.

Analisi distrattori:

- B: similarità `0.33`, sovrapposizione `0.0`
- C: similarità `0.318`, sovrapposizione `0.0`
- D: similarità `0.303`, sovrapposizione `0.0`

---

### AI-FAC-0201

Livello: `facile`

Gravità: `175`

Domanda: Che cosa indica, in generale, un modello di intelligenza artificiale generativa?

Opzioni:

- A. Un sistema capace di produrre nuovi contenuti, come testo, immagini o codice, partendo da dati e istruzioni. ✅
- B. Un sistema che riconosce soltanto se un'immagine appartiene a una categoria già definita.
- C. Un database che conserva esempi senza costruire risposte nuove.
- D. Un programma che esegue solo calcoli numerici impostati manualmente.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.351.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.09.
- Opzione B: contiene parole che la rendono eliminabile: soltanto.
- Opzione C: troppo lontana dalla corretta, similarità 0.212.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.235.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: contiene parole che la rendono eliminabile: solo.

Analisi distrattori:

- B: similarità `0.351`, sovrapposizione `0.09`
- C: similarità `0.212`, sovrapposizione `0.0`
- D: similarità `0.235`, sovrapposizione `0.0`

---

### AI-AV-0211

Livello: `avanzato`

Gravità: `175`

Domanda: Perché le guardrail sono importanti in un sistema AI usato da utenti finali?

Opzioni:

- A. Per limitare comportamenti rischiosi, applicare regole e gestire richieste non adatte. ✅
- B. Per aumentare il numero di parametri del modello durante l'inferenza.
- C. Per sostituire completamente la progettazione del prodotto.
- D. Per impedire qualsiasi risposta anche quando la richiesta è lecita.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.286.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.286.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: contiene parole che la rendono eliminabile: completamente.
- Opzione D: troppo lontana dalla corretta, similarità 0.316.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: contiene parole che la rendono eliminabile: qualsiasi.

Analisi distrattori:

- B: similarità `0.286`, sovrapposizione `0.0`
- C: similarità `0.286`, sovrapposizione `0.0`
- D: similarità `0.316`, sovrapposizione `0.0`

---

### AI-FAC-0001

Livello: `facile`

Gravità: `155`

Domanda: Qual è il ruolo principale di un modello linguistico di grandi dimensioni, chiamato LLM?

Opzioni:

- A. Prevedere e generare testo in base al contesto ricevuto ✅
- B. Classificare testi in categorie fisse senza produrre nuove frasi
- C. Recuperare documenti esterni senza generare una risposta autonoma
- D. Tradurre parole usando solo un dizionario statico

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.307.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.353.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.17.
- Opzione D: troppo lontana dalla corretta, similarità 0.286.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: contiene parole che la rendono eliminabile: solo.

Analisi distrattori:

- B: similarità `0.307`, sovrapposizione `0.0`
- C: similarità `0.353`, sovrapposizione `0.17`
- D: similarità `0.286`, sovrapposizione `0.0`

---

### AI-INT-0006

Livello: `intermedio`

Gravità: `155`

Domanda: Perché è utile testare un modello AI con esempi diversi da quelli usati in addestramento?

Opzioni:

- A. Per verificare se il modello generalizza anche su casi nuovi ✅
- B. Per confermare che il modello ricorda con precisione gli esempi usati in addestramento
- C. Per scegliere automaticamente nuovi esempi da aggiungere al training set
- D. Per aumentare il numero di esempi nel dataset senza controllare le prestazioni

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.306.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.17.
- Opzione C: troppo lontana dalla corretta, similarità 0.305.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.17.
- Opzione C: contiene parole che la rendono eliminabile: automaticamente.
- Opzione D: troppo lontana dalla corretta, similarità 0.311.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.306`, sovrapposizione `0.17`
- C: similarità `0.305`, sovrapposizione `0.17`
- D: similarità `0.311`, sovrapposizione `0.0`

---

### AI-FAC-0007

Livello: `facile`

Gravità: `155`

Domanda: Che cosa fa principalmente un modello linguistico?

Opzioni:

- A. Lavora con il linguaggio per comprendere o generare testo ✅
- B. Classifica contenuti testuali senza produrre nuove frasi
- C. Recupera pagine web pertinenti senza formulare una risposta
- D. Analizza solo dati numerici organizzati in tabelle

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.289.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.32.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.247.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: contiene parole che la rendono eliminabile: solo.

Analisi distrattori:

- B: similarità `0.289`, sovrapposizione `0.0`
- C: similarità `0.32`, sovrapposizione `0.0`
- D: similarità `0.247`, sovrapposizione `0.0`

---

### AI-FAC-0206

Livello: `facile`

Gravità: `155`

Domanda: Che cosa sono i token in un modello linguistico?

Opzioni:

- A. Unità di testo, come parole o parti di parole, che il modello usa per elaborare il linguaggio. ✅
- B. File immagine usati per addestrare soltanto modelli visivi.
- C. Etichette numeriche che indicano esclusivamente la qualità di una risposta.
- D. Password temporanee usate per accedere a un'applicazione.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.236.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione B: contiene parole che la rendono eliminabile: soltanto.
- Opzione C: troppo lontana dalla corretta, similarità 0.214.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.252.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.236`, sovrapposizione `0.0`
- C: similarità `0.214`, sovrapposizione `0.0`
- D: similarità `0.252`, sovrapposizione `0.0`

---

### AI-FAC-0209

Livello: `facile`

Gravità: `155`

Domanda: A cosa servono gli embedding in molte applicazioni AI?

Opzioni:

- A. A rappresentare testi, immagini o altri dati come vettori numerici confrontabili. ✅
- B. A sostituire ogni controllo qualità sui dati prodotti dal modello.
- C. A trasformare automaticamente qualsiasi modello piccolo in un modello più grande.
- D. A eliminare la necessità di salvare informazioni in memoria.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.343.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.
- Opzione C: troppo lontana dalla corretta, similarità 0.29.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: contiene parole che la rendono eliminabile: qualsiasi, automaticamente.
- Opzione D: troppo lontana dalla corretta, similarità 0.261.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.343`, sovrapposizione `0.12`
- C: similarità `0.29`, sovrapposizione `0.0`
- D: similarità `0.261`, sovrapposizione `0.0`

---

### AI-INT-0201

Livello: `intermedio`

Gravità: `155`

Domanda: Qual è il vantaggio principale di una pipeline RAG rispetto a un semplice prompt senza recupero documentale?

Opzioni:

- A. Può recuperare informazioni da fonti esterne e usarle per rendere la risposta più ancorata ai dati disponibili. ✅
- B. Trasforma automaticamente il modello in un sistema addestrato da zero sul dominio aziendale.
- C. Elimina ogni rischio di risposta errata anche quando le fonti sono incomplete.
- D. Sostituisce il modello linguistico con un normale motore di ricerca.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.249.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione B: contiene parole che la rendono eliminabile: automaticamente.
- Opzione C: troppo lontana dalla corretta, similarità 0.321.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.17.
- Opzione D: troppo lontana dalla corretta, similarità 0.201.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.249`, sovrapposizione `0.0`
- C: similarità `0.321`, sovrapposizione `0.17`
- D: similarità `0.201`, sovrapposizione `0.0`

---

### AI-INT-0209

Livello: `intermedio`

Gravità: `155`

Domanda: Perché un set di valutazione separato è importante nello sviluppo di un modello AI?

Opzioni:

- A. Per misurare il comportamento del modello su esempi non usati direttamente per addestrarlo. ✅
- B. Per aggiungere automaticamente nuove etichette al dataset di training.
- C. Per sostituire del tutto il controllo umano quando il dominio è delicato.
- D. Per rendere inutili metriche e analisi degli errori.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.281.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione B: contiene parole che la rendono eliminabile: automaticamente.
- Opzione C: troppo lontana dalla corretta, similarità 0.268.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.218.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.281`, sovrapposizione `0.0`
- C: similarità `0.268`, sovrapposizione `0.0`
- D: similarità `0.218`, sovrapposizione `0.0`

---

### AI-INT-0211

Livello: `intermedio`

Gravità: `155`

Domanda: Che cosa significa grounding in una risposta generata da un modello linguistico?

Opzioni:

- A. Collegare la risposta a informazioni verificabili o a fonti fornite al sistema. ✅
- B. Aumentare casualmente la creatività della risposta.
- C. Ridurre il testo generato a una sola parola.
- D. Cancellare tutti i riferimenti ai dati usati dal sistema.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.261.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.14.
- Opzione C: troppo lontana dalla corretta, similarità 0.232.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.34.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.14.
- Opzione D: contiene parole che la rendono eliminabile: tutti.

Analisi distrattori:

- B: similarità `0.261`, sovrapposizione `0.14`
- C: similarità `0.232`, sovrapposizione `0.0`
- D: similarità `0.34`, sovrapposizione `0.14`

---

### AI-INT-0212

Livello: `intermedio`

Gravità: `155`

Domanda: Perché la quantizzazione può essere utile per eseguire modelli AI su dispositivi con risorse limitate?

Opzioni:

- A. Per ridurre la precisione numerica dei pesi e diminuire memoria o costo computazionale. ✅
- B. Per aumentare il numero di neuroni senza cambiare la memoria richiesta.
- C. Per trasformare un modello linguistico in un database vettoriale.
- D. Per garantire automaticamente risposte più corrette in ogni dominio.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.352.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.
- Opzione C: troppo lontana dalla corretta, similarità 0.266.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.275.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: contiene parole che la rendono eliminabile: automaticamente.

Analisi distrattori:

- B: similarità `0.352`, sovrapposizione `0.12`
- C: similarità `0.266`, sovrapposizione `0.0`
- D: similarità `0.275`, sovrapposizione `0.0`

---

### AI-AV-0201

Livello: `avanzato`

Gravità: `155`

Domanda: Qual è il ruolo principale del meccanismo di attention nei Transformer?

Opzioni:

- A. Pesare l'importanza relativa di diverse parti della sequenza durante l'elaborazione. ✅
- B. Ridurre ogni input a una sola parola prima della generazione.
- C. Sostituire completamente la fase di tokenizzazione.
- D. Archiviare in modo permanente tutte le conversazioni degli utenti.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.306.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.242.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: contiene parole che la rendono eliminabile: completamente.
- Opzione D: troppo lontana dalla corretta, similarità 0.27.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.306`, sovrapposizione `0.0`
- C: similarità `0.242`, sovrapposizione `0.0`
- D: similarità `0.27`, sovrapposizione `0.0`

---

### AI-AV-0205

Livello: `avanzato`

Gravità: `155`

Domanda: Che cosa indica il catastrophic forgetting nel machine learning?

Opzioni:

- A. La perdita di prestazioni su conoscenze o compiti precedenti dopo un nuovo addestramento. ✅
- B. La capacità del modello di ricordare perfettamente tutti i dati passati.
- C. La cancellazione automatica dei file temporanei dopo l'inferenza.
- D. La riduzione della latenza causata da una cache più efficiente.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.267.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione B: contiene parole che la rendono eliminabile: tutti.
- Opzione C: troppo lontana dalla corretta, similarità 0.314.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.
- Opzione D: troppo lontana dalla corretta, similarità 0.234.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.267`, sovrapposizione `0.0`
- C: similarità `0.314`, sovrapposizione `0.12`
- D: similarità `0.234`, sovrapposizione `0.0`

---

### AI-AV-0208

Livello: `avanzato`

Gravità: `155`

Domanda: Perché un sistema multimodale deve allineare informazioni provenienti da testo e immagini?

Opzioni:

- A. Per collegare correttamente elementi visivi e descrizioni linguistiche durante il ragionamento o la generazione. ✅
- B. Per impedire al modello di usare dati testuali quando riceve un'immagine.
- C. Per trasformare ogni immagine in un file audio prima dell'analisi.
- D. Per cancellare automaticamente le parti meno colorate dell'immagine.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.237.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.197.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.266.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: contiene parole che la rendono eliminabile: automaticamente.

Analisi distrattori:

- B: similarità `0.237`, sovrapposizione `0.0`
- C: similarità `0.197`, sovrapposizione `0.0`
- D: similarità `0.266`, sovrapposizione `0.0`

---

### AI-AV-0209

Livello: `avanzato`

Gravità: `155`

Domanda: Quale compromesso è spesso necessario quando si sceglie un modello AI per un'app reale?

Opzioni:

- A. Bilanciare qualità delle risposte, latenza, costo computazionale e risorse disponibili. ✅
- B. Scegliere il modello più grande come criterio principale, senza valutare bene tempi e costi.
- C. Usare solo modelli non addestrati per evitare ogni errore.
- D. Eliminare i test perché le metriche rallentano l'applicazione.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.299.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.23.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: contiene parole che la rendono eliminabile: solo.
- Opzione D: troppo lontana dalla corretta, similarità 0.247.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.299`, sovrapposizione `0.0`
- C: similarità `0.23`, sovrapposizione `0.0`
- D: similarità `0.247`, sovrapposizione `0.0`

---

### AI-AV-0005

Livello: `avanzato`

Gravità: `150`

Domanda: Perché valutare un modello AI solo con risposte corrette o sbagliate può essere limitante?

Opzioni:

- A. Perché alcune risposte richiedono giudizi su completezza, coerenza, sicurezza e utilità ✅
- B. Perché basta valutare la completezza, senza considerare coerenza, sicurezza e utilità
- C. Perché una risposta va valutata solo in base al formato richiesto
- D. Perché una risposta va valutata solo in base alla fluidità del testo

Problemi:

- Opzione B: contiene parole che la rendono eliminabile: senza considerare.
- Opzione C: troppo lontana dalla corretta, similarità 0.304.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.11.
- Opzione C: contiene parole che la rendono eliminabile: solo.
- Opzione D: troppo lontana dalla corretta, similarità 0.332.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.11.
- Opzione D: contiene parole che la rendono eliminabile: solo.

Analisi distrattori:

- B: similarità `0.589`, sovrapposizione `0.56`
- C: similarità `0.304`, sovrapposizione `0.11`
- D: similarità `0.332`, sovrapposizione `0.11`

---

### AI-INT-0005

Livello: `intermedio`

Gravità: `150`

Domanda: A cosa serve un embedding in molte applicazioni di intelligenza artificiale?

Opzioni:

- A. A rappresentare testi, immagini o dati come vettori confrontabili ✅
- B. A trasformare contenuti in vettori numerici solo per conservarli come testo compresso
- C. A confrontare contenuti solo quando usano le stesse parole identiche
- D. A cercare parole uguali senza rappresentare il significato dei contenuti

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.336.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.17.
- Opzione B: contiene parole che la rendono eliminabile: solo.
- Opzione C: troppo lontana dalla corretta, similarità 0.262.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: contiene parole che la rendono eliminabile: solo.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.17.

Analisi distrattori:

- B: similarità `0.336`, sovrapposizione `0.17`
- C: similarità `0.262`, sovrapposizione `0.0`
- D: similarità `0.385`, sovrapposizione `0.17`

---

### AI-INT-0107

Livello: `intermedio`

Gravità: `150`

Domanda: Perché conviene limitare le azioni che un agente AI può eseguire automaticamente?

Opzioni:

- A. Per ridurre il rischio che un errore o un prompt malevolo produca azioni dannose ✅
- B. Per velocizzare il flusso riducendo controlli e conferme dell'utente
- C. Per impedire al modello di leggere qualsiasi istruzione dell'utente
- D. Per rendere impossibile ogni controllo umano sulle azioni dell'agente

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.307.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.32.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: contiene parole che la rendono eliminabile: qualsiasi.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.
- Opzione D: contiene parole che la rendono eliminabile: impossibile.

Analisi distrattori:

- B: similarità `0.307`, sovrapposizione `0.0`
- C: similarità `0.32`, sovrapposizione `0.0`
- D: similarità `0.37`, sovrapposizione `0.12`

---

### AI-AV-0204

Livello: `avanzato`

Gravità: `150`

Domanda: Qual è una differenza importante tra RLHF e DPO nell'allineamento dei modelli linguistici?

Opzioni:

- A. RLHF usa un processo con modello di ricompensa e ottimizzazione tramite rinforzo, mentre DPO ottimizza direttamente su preferenze confrontate. ✅
- B. DPO richiede un modello di ricompensa separato più complesso, mentre RLHF ottimizza direttamente le preferenze.
- C. RLHF funziona solo con modelli piccoli, mentre DPO funziona solo con database SQL.
- D. DPO elimina la necessità di dati di preferenza umana o sintetica.

Problemi:

- Opzione C: troppo lontana dalla corretta, similarità 0.341.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.21.
- Opzione C: contiene parole che la rendono eliminabile: solo.
- Opzione D: troppo lontana dalla corretta, similarità 0.227.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.07.
- Opzione D: troppo corta rispetto alla corretta, 64 caratteri contro 140.
- La corretta spicca per lunghezza. Lunghezze: [140, 109, 80, 64].

Analisi distrattori:

- B: similarità `0.575`, sovrapposizione `0.57`
- C: similarità `0.341`, sovrapposizione `0.21`
- D: similarità `0.227`, sovrapposizione `0.07`

---

### AI-AV-0207

Livello: `avanzato`

Gravità: `150`

Domanda: Che cosa può causare il context poisoning in un'applicazione basata su LLM?

Opzioni:

- A. L'inserimento nel contesto di informazioni fuorvianti che influenzano negativamente le risposte successive. ✅
- B. La riduzione della temperatura a un valore più basso durante la generazione.
- C. La conversione degli input testuali in token numerici.
- D. L'uso di un monitor con risoluzione non adatta all'interfaccia.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.227.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.206.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo corta rispetto alla corretta, 53 caratteri contro 106.
- Opzione D: troppo lontana dalla corretta, similarità 0.238.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.227`, sovrapposizione `0.0`
- C: similarità `0.206`, sovrapposizione `0.0`
- D: similarità `0.238`, sovrapposizione `0.0`

---

### AI-AV-0003

Livello: `avanzato`

Gravità: `135`

Domanda: A cosa serve principalmente un sistema RAG in un'applicazione AI?

Opzioni:

- A. A recuperare informazioni da fonti esterne e usarle per generare risposte più fondate ✅
- B. A riaddestrare il modello sui documenti recuperati prima di ogni risposta
- C. A cercare documenti simili senza passarli al modello durante la generazione
- D. A sostituire il ragionamento del modello con una semplice ricerca per parole chiave

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.278.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.325.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.329.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.278`, sovrapposizione `0.0`
- C: similarità `0.325`, sovrapposizione `0.0`
- D: similarità `0.329`, sovrapposizione `0.0`

---

### AI-INT-0004

Livello: `intermedio`

Gravità: `135`

Domanda: In un sistema RAG, perché si cercano documenti esterni prima di generare la risposta?

Opzioni:

- A. Per fornire al modello informazioni aggiornate o specifiche su cui basare la risposta ✅
- B. Per trovare testi semanticamente simili alla domanda, anche se poi non vengono usati come contesto
- C. Per archiviare i documenti recuperati senza inserirli nel prompt
- D. Per confrontare la domanda con esempi simili senza generare una risposta

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.306.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.24.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.317.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.

Analisi distrattori:

- B: similarità `0.306`, sovrapposizione `0.0`
- C: similarità `0.24`, sovrapposizione `0.0`
- D: similarità `0.317`, sovrapposizione `0.12`

---

### AI-FAC-0006

Livello: `facile`

Gravità: `135`

Domanda: Se un modello AI decide se una email è spam oppure no, quale tipo di attività sta svolgendo?

Opzioni:

- A. Classificazione ✅
- B. Clustering
- C. Regressione
- D. Stima di un valore numerico

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.273.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.308.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.178.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.273`, sovrapposizione `0.0`
- C: similarità `0.308`, sovrapposizione `0.0`
- D: similarità `0.178`, sovrapposizione `0.0`

---

### AI-FAC-0008

Livello: `facile`

Gravità: `135`

Domanda: Quando un modello AI inventa una risposta falsa ma la presenta come sicura, come viene chiamato di solito questo problema?

Opzioni:

- A. Allucinazione ✅
- B. Bias del dataset
- C. Overfitting
- D. Errore di classificazione

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.259.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.228.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.251.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.259`, sovrapposizione `0.0`
- C: similarità `0.228`, sovrapposizione `0.0`
- D: similarità `0.251`, sovrapposizione `0.0`

---

### AI-FAC-0207

Livello: `facile`

Gravità: `135`

Domanda: Che cosa significa inferenza in un modello AI già addestrato?

Opzioni:

- A. Usare il modello per produrre una previsione o una risposta su un nuovo input. ✅
- B. Aggiungere manualmente tutte le regole che il modello dovrà seguire.
- C. Cancellare i pesi del modello prima dell'utilizzo.
- D. Preparare il dataset prima della fase di addestramento.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.316.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.14.
- Opzione C: troppo lontana dalla corretta, similarità 0.287.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.14.
- Opzione D: troppo lontana dalla corretta, similarità 0.258.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.316`, sovrapposizione `0.14`
- C: similarità `0.287`, sovrapposizione `0.14`
- D: similarità `0.258`, sovrapposizione `0.0`

---

### AI-FAC-0208

Livello: `facile`

Gravità: `135`

Domanda: Che cosa si intende per allucinazione di un modello linguistico?

Opzioni:

- A. Una risposta plausibile nella forma ma non corretta o non supportata dai dati. ✅
- B. Una risposta presentata come verificata da fonti esterne affidabili.
- C. Una traduzione letterale prodotta senza cambiare il significato.
- D. Una compressione tecnica dei parametri del modello.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.359.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.
- Opzione C: troppo lontana dalla corretta, similarità 0.279.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.191.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.359`, sovrapposizione `0.12`
- C: similarità `0.279`, sovrapposizione `0.0`
- D: similarità `0.191`, sovrapposizione `0.0`

---

### AI-FAC-0212

Livello: `facile`

Gravità: `135`

Domanda: Che cosa distingue un modello supervisionato da uno non supervisionato?

Opzioni:

- A. Nel supervisionato gli esempi di addestramento hanno etichette o risposte corrette associate. ✅
- B. Nel supervisionato il modello può funzionare solo senza dati di esempio.
- C. Nel non supervisionato ogni esempio contiene etichette esplicite simili a quelle del supervisionato.
- D. Nel non supervisionato il modello non può trovare strutture nei dati.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.309.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.
- Opzione B: contiene parole che la rendono eliminabile: solo.
- Opzione C: troppo lontana dalla corretta, similarità 0.312.
- Opzione D: troppo lontana dalla corretta, similarità 0.311.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.

Analisi distrattori:

- B: similarità `0.309`, sovrapposizione `0.12`
- C: similarità `0.312`, sovrapposizione `0.25`
- D: similarità `0.311`, sovrapposizione `0.12`

---

### AI-INT-0202

Livello: `intermedio`

Gravità: `135`

Domanda: Perché un database vettoriale è utile in un sistema basato su embedding?

Opzioni:

- A. Per cercare elementi semanticamente simili usando vettori numerici. ✅
- B. Per salvare esclusivamente immagini in formato compresso.
- C. Per convertire un modello linguistico in un foglio di calcolo.
- D. Per sostituire la fase di progettazione dei prompt.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.33.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione C: troppo lontana dalla corretta, similarità 0.334.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.26.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.33`, sovrapposizione `0.0`
- C: similarità `0.334`, sovrapposizione `0.0`
- D: similarità `0.26`, sovrapposizione `0.0`

---

### AI-INT-0206

Livello: `intermedio`

Gravità: `135`

Domanda: Che cosa si intende per prompt injection?

Opzioni:

- A. Un tentativo di inserire istruzioni malevole o fuorvianti nel testo dato al modello. ✅
- B. Una tecnica di compressione che riduce il numero di parametri del modello.
- C. Un metodo per caricare immagini dentro un database relazionale.
- D. Un sistema per rendere più veloce la connessione internet dell'app.

Problemi:

- Opzione B: troppo lontana dalla corretta, similarità 0.332.
- Opzione B: condivide pochi concetti chiave con la corretta, sovrapposizione 0.12.
- Opzione C: troppo lontana dalla corretta, similarità 0.26.
- Opzione C: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.
- Opzione D: troppo lontana dalla corretta, similarità 0.258.
- Opzione D: condivide pochi concetti chiave con la corretta, sovrapposizione 0.0.

Analisi distrattori:

- B: similarità `0.332`, sovrapposizione `0.12`
- C: similarità `0.26`, sovrapposizione `0.0`
- D: similarità `0.258`, sovrapposizione `0.0`
