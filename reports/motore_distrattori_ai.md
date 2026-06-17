# Motore distrattori AI

File controllato: `data/ai.json`

Domande controllate: 80
Domande problematiche: 74

## Prime domande da correggere

---

### AI-INT-0005

Livello: `intermedio`

Gravità: `115`

Domanda: A cosa serve un embedding in molte applicazioni di intelligenza artificiale?

Opzioni:

- A. A rappresentare testi, immagini o dati come vettori confrontabili ✅
- B. A trasformare contenuti in vettori numerici solo per conservarli come testo compresso 🎯 distrattore principale
- C. A confrontare contenuti solo quando usano le stesse parole identiche
- D. A cercare parole uguali senza rappresentare il significato dei contenuti

Similarità distrattore principale: `0.353`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.353.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.405.
- Opzione B eliminabile per parole troppo assolute: solo.
- Opzione C eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.17.

---

### AI-AV-0008

Livello: `avanzato`

Gravità: `115`

Domanda: In una pipeline AI, perché conviene separare recupero delle informazioni, generazione e controllo finale?

Opzioni:

- A. Per rendere più controllabile ogni fase e individuare meglio dove nasce un errore ✅
- B. Per valutare separatamente le fasi, ma senza collegare gli errori alla risposta finale 🎯 distrattore principale
- C. Per controllare solo il recupero dei documenti ignorando la generazione
- D. Per controllare solo la generazione ignorando retrieval e verifica finale

Similarità distrattore principale: `0.35`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.35.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.35.
- Opzione C eliminabile per parole troppo assolute: solo.
- Opzione D eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-INT-0107

Livello: `intermedio`

Gravità: `115`

Domanda: Perché conviene limitare le azioni che un agente AI può eseguire automaticamente?

Opzioni:

- A. Per ridurre il rischio che un errore o un prompt malevolo produca azioni dannose ✅
- B. Per velocizzare il flusso riducendo controlli e conferme dell'utente 🎯 distrattore principale
- C. Per impedire al modello di leggere qualsiasi istruzione dell'utente
- D. Per rendere impossibile ogni controllo umano sulle azioni dell'agente

Similarità distrattore principale: `0.327`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.327.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.391.
- Opzione C eliminabile per parole troppo assolute: qualsiasi.
- Opzione D eliminabile per parole troppo assolute: impossibile.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-FAC-0201

Livello: `facile`

Gravità: `115`

Domanda: Che cosa indica, in generale, un modello di intelligenza artificiale generativa?

Opzioni:

- A. Un sistema capace di produrre nuovi contenuti, come testo, immagini o codice, partendo da dati e istruzioni. ✅
- B. Un sistema che riconosce soltanto se un'immagine appartiene a una categoria già definita. 🎯 distrattore principale
- C. Un database che conserva esempi senza costruire risposte nuove.
- D. Un programma che esegue solo calcoli numerici impostati manualmente.

Similarità distrattore principale: `0.373`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.373.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.373.
- Opzione B eliminabile per parole troppo assolute: soltanto.
- Opzione D eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.09.

---

### AI-FAC-0211

Livello: `facile`

Gravità: `115`

Domanda: Perché la privacy è importante quando si usa un'app AI?

Opzioni:

- A. Perché i dati inseriti dall'utente possono contenere informazioni personali o sensibili. ✅
- B. Perché un modello AI non può elaborare nessun testo se non conosce il nome dell'utente. 🎯 distrattore principale
- C. Perché la privacy serve solo a rendere più colorata l'interfaccia.
- D. Perché tutti i dati personali devono essere pubblicati per migliorare il modello.

Similarità distrattore principale: `0.341`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.341.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.416.
- Opzione C eliminabile per parole troppo assolute: solo.
- Opzione D eliminabile per parole troppo assolute: tutti.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.1.

---

### AI-AV-0211

Livello: `avanzato`

Gravità: `115`

Domanda: Perché le guardrail sono importanti in un sistema AI usato da utenti finali?

Opzioni:

- A. Per limitare comportamenti rischiosi, applicare regole e gestire richieste non adatte. ✅
- B. Per aumentare il numero di parametri del modello durante l'inferenza. 🎯 distrattore principale
- C. Per sostituire completamente la progettazione del prodotto.
- D. Per impedire qualsiasi risposta anche quando la richiesta è lecita.

Similarità distrattore principale: `0.308`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.308.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.342.
- Opzione C eliminabile per parole troppo assolute: completamente.
- Opzione D eliminabile per parole troppo assolute: qualsiasi.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-FAC-0001

Livello: `facile`

Gravità: `100`

Domanda: Qual è il ruolo principale di un modello linguistico di grandi dimensioni, chiamato LLM?

Opzioni:

- A. Prevedere e generare testo in base al contesto ricevuto ✅
- B. Classificare testi in categorie fisse senza produrre nuove frasi 🎯 distrattore principale
- C. Recuperare documenti esterni senza generare una risposta autonoma
- D. Tradurre parole usando solo un dizionario statico

Similarità distrattore principale: `0.326`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.326.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.369.
- Opzione D eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-INT-0006

Livello: `intermedio`

Gravità: `100`

Domanda: Perché è utile testare un modello AI con esempi diversi da quelli usati in addestramento?

Opzioni:

- A. Per verificare se il modello generalizza anche su casi nuovi ✅
- B. Per confermare che il modello ricorda con precisione gli esempi usati in addestramento 🎯 distrattore principale
- C. Per scegliere automaticamente nuovi esempi da aggiungere al training set
- D. Per aumentare il numero di esempi nel dataset senza controllare le prestazioni

Similarità distrattore principale: `0.321`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.321.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.334.
- Opzione C eliminabile per parole troppo assolute: automaticamente.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.17.

---

### AI-FAC-0007

Livello: `facile`

Gravità: `100`

Domanda: Che cosa fa principalmente un modello linguistico?

Opzioni:

- A. Lavora con il linguaggio per comprendere o generare testo ✅
- B. Classifica contenuti testuali senza produrre nuove frasi 🎯 distrattore principale
- C. Recupera pagine web pertinenti senza formulare una risposta
- D. Analizza solo dati numerici organizzati in tabelle

Similarità distrattore principale: `0.303`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.303.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.338.
- Opzione D eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-FAC-0202

Livello: `facile`

Gravità: `100`

Domanda: Che cosa rappresenta un prompt quando si usa un modello linguistico?

Opzioni:

- A. L'istruzione o il testo iniziale dato al modello per guidare la risposta. ✅
- B. Il file interno che contiene tutti i pesi matematici del modello. 🎯 distrattore principale
- C. Il risultato finale generato dal modello dopo l'elaborazione.
- D. Il database esterno usato per salvare le conversazioni dell'utente.

Similarità distrattore principale: `0.346`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.346.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.413.
- Opzione B eliminabile per parole troppo assolute: tutti.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-FAC-0206

Livello: `facile`

Gravità: `100`

Domanda: Che cosa sono i token in un modello linguistico?

Opzioni:

- A. Unità di testo, come parole o parti di parole, che il modello usa per elaborare il linguaggio. ✅
- B. File immagine usati per addestrare soltanto modelli visivi. 🎯 distrattore principale
- C. Etichette numeriche che indicano esclusivamente la qualità di una risposta.
- D. Password temporanee usate per accedere a un'applicazione.

Similarità distrattore principale: `0.255`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.255.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.274.
- Opzione B eliminabile per parole troppo assolute: soltanto.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-FAC-0209

Livello: `facile`

Gravità: `100`

Domanda: A cosa servono gli embedding in molte applicazioni AI?

Opzioni:

- A. A rappresentare testi, immagini o altri dati come vettori numerici confrontabili. ✅
- B. A sostituire ogni controllo qualità sui dati prodotti dal modello. 🎯 distrattore principale
- C. A trasformare automaticamente qualsiasi modello piccolo in un modello più grande.
- D. A eliminare la necessità di salvare informazioni in memoria.

Similarità distrattore principale: `0.365`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.365.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.365.
- Opzione C eliminabile per parole troppo assolute: qualsiasi, automaticamente.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.12.

---

### AI-FAC-0210

Livello: `facile`

Gravità: `100`

Domanda: Che cosa significa fine-tuning di un modello AI?

Opzioni:

- A. Adattare un modello già addestrato a un compito o dominio più specifico. ✅
- B. Creare un modello da zero senza usare dati precedenti. 🎯 distrattore principale
- C. Usare il modello solo per cercare file in una cartella locale.
- D. Ridurre la dimensione del monitor usato durante l'addestramento.

Similarità distrattore principale: `0.388`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.388.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.388.
- Opzione C eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.12.

---

### AI-FAC-0212

Livello: `facile`

Gravità: `100`

Domanda: Che cosa distingue un modello supervisionato da uno non supervisionato?

Opzioni:

- A. Nel supervisionato gli esempi di addestramento hanno etichette o risposte corrette associate. ✅
- B. Nel supervisionato il modello può funzionare solo senza dati di esempio. 🎯 distrattore principale
- C. Nel non supervisionato ogni esempio contiene etichette esplicite simili a quelle del supervisionato.
- D. Nel non supervisionato il modello non può trovare strutture nei dati.

Similarità distrattore principale: `0.327`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.327.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.33.
- Opzione B eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.12.

---

### AI-INT-0201

Livello: `intermedio`

Gravità: `100`

Domanda: Qual è il vantaggio principale di una pipeline RAG rispetto a un semplice prompt senza recupero documentale?

Opzioni:

- A. Può recuperare informazioni da fonti esterne e usarle per rendere la risposta più ancorata ai dati disponibili. ✅
- B. Trasforma automaticamente il modello in un sistema addestrato da zero sul dominio aziendale. 🎯 distrattore principale
- C. Elimina ogni rischio di risposta errata anche quando le fonti sono incomplete.
- D. Sostituisce il modello linguistico con un normale motore di ricerca.

Similarità distrattore principale: `0.264`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.264.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.335.
- Opzione B eliminabile per parole troppo assolute: automaticamente.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-INT-0204

Livello: `intermedio`

Gravità: `100`

Domanda: In una ricerca semantica, perché il semplice confronto di parole chiave può essere meno efficace degli embedding?

Opzioni:

- A. Perché gli embedding possono catturare somiglianze di significato anche quando le parole usate sono diverse. ✅
- B. Perché le parole chiave leggono direttamente i pensieri dell'utente. 🎯 distrattore principale
- C. Perché gli embedding eliminano la necessità di controllare i risultati recuperati.
- D. Perché la ricerca per parole chiave funziona solo con immagini e non con testo.

Similarità distrattore principale: `0.309`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.309.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.391.
- Opzione D eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.18.

---

### AI-INT-0209

Livello: `intermedio`

Gravità: `100`

Domanda: Perché un set di valutazione separato è importante nello sviluppo di un modello AI?

Opzioni:

- A. Per misurare il comportamento del modello su esempi non usati direttamente per addestrarlo. ✅
- B. Per aggiungere automaticamente nuove etichette al dataset di training. 🎯 distrattore principale
- C. Per sostituire del tutto il controllo umano quando il dominio è delicato.
- D. Per rendere inutili metriche e analisi degli errori.

Similarità distrattore principale: `0.303`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.303.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.303.
- Opzione B eliminabile per parole troppo assolute: automaticamente.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-INT-0211

Livello: `intermedio`

Gravità: `100`

Domanda: Che cosa significa grounding in una risposta generata da un modello linguistico?

Opzioni:

- A. Collegare la risposta a informazioni verificabili o a fonti fornite al sistema. ✅
- B. Aumentare casualmente la creatività della risposta. 🎯 distrattore principale
- C. Ridurre il testo generato a una sola parola.
- D. Cancellare tutti i riferimenti ai dati usati dal sistema.

Similarità distrattore principale: `0.234`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.234.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.363.
- Opzione D eliminabile per parole troppo assolute: tutti.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-INT-0212

Livello: `intermedio`

Gravità: `100`

Domanda: Perché la quantizzazione può essere utile per eseguire modelli AI su dispositivi con risorse limitate?

Opzioni:

- A. Per ridurre la precisione numerica dei pesi e diminuire memoria o costo computazionale. ✅
- B. Per aumentare il numero di neuroni senza cambiare la memoria richiesta. 🎯 distrattore principale
- C. Per trasformare un modello linguistico in un database vettoriale.
- D. Per garantire automaticamente risposte più corrette in ogni dominio.

Similarità distrattore principale: `0.374`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.374.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.374.
- Opzione D eliminabile per parole troppo assolute: automaticamente.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.12.

---

### AI-INT-0213

Livello: `intermedio`

Gravità: `100`

Domanda: Che cosa può indicare una bassa precisione in un classificatore?

Opzioni:

- A. Molti elementi previsti come positivi dal modello sono in realtà negativi. ✅
- B. Il modello produce pochissimi risultati positivi. 🎯 distrattore principale
- C. Il dataset contiene solo esempi senza etichetta.
- D. Il modello è stato addestrato esclusivamente su immagini ad alta risoluzione.

Similarità distrattore principale: `0.322`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.322.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.351.
- Opzione C eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.12.

---

### AI-AV-0201

Livello: `avanzato`

Gravità: `100`

Domanda: Qual è il ruolo principale del meccanismo di attention nei Transformer?

Opzioni:

- A. Pesare l'importanza relativa di diverse parti della sequenza durante l'elaborazione. ✅
- B. Ridurre ogni input a una sola parola prima della generazione. 🎯 distrattore principale
- C. Sostituire completamente la fase di tokenizzazione.
- D. Archiviare in modo permanente tutte le conversazioni degli utenti.

Similarità distrattore principale: `0.333`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.333.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.333.
- Opzione C eliminabile per parole troppo assolute: completamente.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-AV-0205

Livello: `avanzato`

Gravità: `100`

Domanda: Che cosa indica il catastrophic forgetting nel machine learning?

Opzioni:

- A. La perdita di prestazioni su conoscenze o compiti precedenti dopo un nuovo addestramento. ✅
- B. La capacità del modello di ricordare perfettamente tutti i dati passati. 🎯 distrattore principale
- C. La cancellazione automatica dei file temporanei dopo l'inferenza.
- D. La riduzione della latenza causata da una cache più efficiente.

Similarità distrattore principale: `0.286`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.286.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.333.
- Opzione B eliminabile per parole troppo assolute: tutti.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-AV-0208

Livello: `avanzato`

Gravità: `100`

Domanda: Perché un sistema multimodale deve allineare informazioni provenienti da testo e immagini?

Opzioni:

- A. Per collegare correttamente elementi visivi e descrizioni linguistiche durante il ragionamento o la generazione. ✅
- B. Per impedire al modello di usare dati testuali quando riceve un'immagine. 🎯 distrattore principale
- C. Per trasformare ogni immagine in un file audio prima dell'analisi.
- D. Per cancellare automaticamente le parti meno colorate dell'immagine.

Similarità distrattore principale: `0.256`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.256.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.29.
- Opzione D eliminabile per parole troppo assolute: automaticamente.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-AV-0209

Livello: `avanzato`

Gravità: `100`

Domanda: Quale compromesso è spesso necessario quando si sceglie un modello AI per un'app reale?

Opzioni:

- A. Bilanciare qualità delle risposte, latenza, costo computazionale e risorse disponibili. ✅
- B. Scegliere il modello più grande come criterio principale, senza valutare bene tempi e costi. 🎯 distrattore principale
- C. Usare solo modelli non addestrati per evitare ogni errore.
- D. Eliminare i test perché le metriche rallentano l'applicazione.

Similarità distrattore principale: `0.319`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.319.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.319.
- Opzione C eliminabile per parole troppo assolute: solo.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.

---

### AI-AV-0003

Livello: `avanzato`

Gravità: `85`

Domanda: A cosa serve principalmente un sistema RAG in un'applicazione AI?

Opzioni:

- A. A recuperare informazioni da fonti esterne e usarle per generare risposte più fondate ✅
- B. A riaddestrare il modello sui documenti recuperati prima di ogni risposta 🎯 distrattore principale
- C. A cercare documenti simili senza passarli al modello durante la generazione
- D. A sostituire il ragionamento del modello con una semplice ricerca per parole chiave

Similarità distrattore principale: `0.293`

Problemi:

- Distrattore principale B troppo lontano dalla corretta. Similarità: 0.293.
- Nessun distrattore è davvero vicino alla risposta corretta. Migliore similarità: 0.348.
- Il distrattore principale condivide pochi concetti chiave con la corretta. Sovrapposizione: 0.0.
