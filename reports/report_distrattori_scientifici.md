# Report qualità distrattori motori scientifici

Questo report separa i problemi qualitativi reali dagli avvisi non bloccanti sulla posizione della risposta corretta nel file sorgente.

## Riepilogo

| Motore | Domande | Problemi qualità reali | Risposta in A nel sorgente |
|---|---:|---:|---:|
| Scienze generali | 40 | 16 | 34 |
| Biologia | 40 | 0 | 40 |
| Fisica | 40 | 0 | 40 |
| Chimica | 40 | 0 | 40 |
| Fisica quantistica | 40 | 5 | 40 |

**Nota:** la risposta in A nel sorgente non è più bloccante, perché il runtime ora usa il mescolatore generale.

## Scienze generali

Domande sorgente: **40**
Domande con problemi qualità reali: **16**
Risposte corrette in A nel sorgente: **34**

Distribuzione risposta corretta nel sorgente:

```text
{'B': 3, 'A': 34, 'C': 3}
```

### Domande da migliorare davvero

### SCI_001 — livello: facile

**Domanda:** Quale organulo cellulare è principalmente responsabile della produzione di energia nella cellula?

**Opzioni attuali:**
- A. Nucleo
- B. Mitocondrio ✅
- C. Ribosoma
- D. Membrana cellulare

**Risposta corretta nel sorgente:** B

**Problemi reali:**
- Opzioni con lunghezze molto sbilanciate: una risposta può risultare troppo riconoscibile.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_005 — livello: intermedio

**Domanda:** Durante la fotosintesi, quale gas viene assorbito principalmente dalle piante?

**Opzioni attuali:**
- A. Ossigeno
- B. Azoto
- C. Anidride carbonica ✅
- D. Idrogeno

**Risposta corretta nel sorgente:** C

**Problemi reali:**
- Opzioni con lunghezze molto sbilanciate: una risposta può risultare troppo riconoscibile.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_006 — livello: intermedio

**Domanda:** Quale valore di pH indica una soluzione acida?

**Opzioni attuali:**
- A. pH uguale a 7
- B. pH maggiore di 7
- C. pH minore di 7 ✅
- D. pH sempre uguale a 14

**Risposta corretta nel sorgente:** C

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_007 — livello: intermedio

**Domanda:** Se la massa di un oggetto resta costante e la forza applicata aumenta, che cosa succede alla sua accelerazione secondo la seconda legge di Newton?

**Opzioni attuali:**
- A. Aumenta ✅
- B. Diminuisce
- C. Resta sempre nulla
- D. Diventa indipendente dalla forza

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Opzioni con lunghezze molto sbilanciate: una risposta può risultare troppo riconoscibile.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_008 — livello: intermedio

**Domanda:** Quale molecola contiene le istruzioni genetiche ereditarie degli esseri viventi?

**Opzioni attuali:**
- A. ATP
- B. DNA ✅
- C. Glucosio
- D. Emoglobina

**Risposta corretta nel sorgente:** B

**Problemi reali:**
- Opzioni con lunghezze molto sbilanciate: una risposta può risultare troppo riconoscibile.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_011 — livello: avanzato

**Domanda:** Quale affermazione descrive meglio la differenza tra massa e peso?

**Opzioni attuali:**
- A. La massa dipende dalla gravità, il peso no
- B. La massa è la quantità di materia, il peso è la forza gravitazionale su quella massa ✅
- C. Massa e peso sono sempre la stessa grandezza
- D. Il peso si misura in chilogrammi, la massa in Newton

**Risposta corretta nel sorgente:** B

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_013 — livello: facile

**Domanda:** Qual è la funzione principale della membrana cellulare?

**Opzioni attuali:**
- A. Delimita la cellula e regola gli scambi con l'esterno ✅
- B. Produce direttamente tutta l'energia della cellula
- C. Contiene sempre il DNA in tutte le cellule
- D. Trasforma il sangue in ossigeno

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_023 — livello: intermedio

**Domanda:** Una soluzione con pH minore di 7 è generalmente considerata:

**Opzioni attuali:**
- A. Acida ✅
- B. Basica
- C. Neutra
- D. Sempre salina

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_029 — livello: intermedio

**Domanda:** Perché una correlazione tra due fenomeni non dimostra automaticamente una causa?

**Opzioni attuali:**
- A. Perché due fenomeni possono variare insieme senza che uno provochi direttamente l'altro ✅
- B. Perché ogni correlazione è sempre falsa
- C. Perché la causa può essere dimostrata solo con un'opinione personale
- D. Perché i dati numerici non possono mai essere usati nella scienza

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “mai”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_031 — livello: avanzato

**Domanda:** In un moto circolare uniforme, verso dove è diretta l'accelerazione centripeta?

**Opzioni attuali:**
- A. Verso il centro della traiettoria circolare ✅
- B. Sempre nella stessa direzione della velocità istantanea
- C. Sempre verso l'esterno della traiettoria
- D. In una direzione casuale che cambia senza regola

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_033 — livello: avanzato

**Domanda:** Che cosa caratterizza la successione ecologica primaria?

**Opzioni attuali:**
- A. Inizia in un ambiente privo di suolo sviluppato, come una roccia nuda ✅
- B. Inizia sempre in una foresta matura già ricca di organismi
- C. Avviene solo quando una specie animale cambia dieta
- D. È la sostituzione immediata di tutti i predatori con erbivori

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_035 — livello: avanzato

**Domanda:** Che cosa esprime in modo semplificato il principio di indeterminazione di Heisenberg?

**Opzioni attuali:**
- A. Non si possono conoscere simultaneamente con precisione arbitraria posizione e quantità di moto di una particella ✅
- B. Ogni particella ha sempre posizione e velocità perfettamente misurabili
- C. La massa di una particella diventa sempre zero quando viene osservata
- D. La luce smette di propagarsi quando incontra un atomo

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_036 — livello: avanzato

**Domanda:** Che cosa fa un catalizzatore in una reazione chimica?

**Opzioni attuali:**
- A. Abbassa l'energia di attivazione e accelera la reazione senza consumarsi stabilmente ✅
- B. Aumenta sempre la quantità finale di prodotto oltre il massimo possibile
- C. Trasforma ogni reazione chimica in una reazione nucleare
- D. Elimina completamente la necessità di reagenti

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_038 — livello: avanzato

**Domanda:** Che cosa si intende per feedback negativo nell'omeostasi?

**Opzioni attuali:**
- A. Un meccanismo che riduce una variazione per riportare il sistema verso l'equilibrio ✅
- B. Un meccanismo che amplifica sempre una variazione fino al collasso del sistema
- C. Una risposta casuale senza rapporto con lo stato del corpo
- D. Una reazione che blocca definitivamente tutte le funzioni vitali

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_039 — livello: avanzato

**Domanda:** Che cosa avviene durante l'osmosi?

**Opzioni attuali:**
- A. L'acqua attraversa una membrana semipermeabile verso la soluzione più concentrata di soluti ✅
- B. I soluti attraversano sempre la membrana verso la soluzione meno concentrata
- C. L'acqua si trasforma direttamente in sale attraverso la membrana
- D. La membrana cellulare scompare per permettere il passaggio di ogni sostanza

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### SCI_040 — livello: avanzato

**Domanda:** Qual è la differenza corretta tra massa e peso?

**Opzioni attuali:**
- A. La massa misura la quantità di materia, il peso è una forza dovuta alla gravità ✅
- B. La massa e il peso sono sempre la stessa grandezza fisica
- C. Il peso misura la quantità di materia, la massa misura la temperatura
- D. La massa cambia sempre più del peso quando un corpo si sposta sulla Luna

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

## Biologia

Domande sorgente: **40**
Domande con problemi qualità reali: **0**
Risposte corrette in A nel sorgente: **40**

Distribuzione risposta corretta nel sorgente:

```text
{'A': 40}
```

Nessun problema qualitativo reale rilevato.

## Fisica

Domande sorgente: **40**
Domande con problemi qualità reali: **0**
Risposte corrette in A nel sorgente: **40**

Distribuzione risposta corretta nel sorgente:

```text
{'A': 40}
```

Nessun problema qualitativo reale rilevato.

## Chimica

Domande sorgente: **40**
Domande con problemi qualità reali: **0**
Risposte corrette in A nel sorgente: **40**

Distribuzione risposta corretta nel sorgente:

```text
{'A': 40}
```

Nessun problema qualitativo reale rilevato.

## Fisica quantistica

Domande sorgente: **40**
Domande con problemi qualità reali: **5**
Risposte corrette in A nel sorgente: **40**

Distribuzione risposta corretta nel sorgente:

```text
{'A': 40}
```

### Domande da migliorare davvero

### FQ_034 — livello: facile

**Domanda:** Perché gli spettri atomici sono formati da righe discrete?

**Opzioni attuali:**
- A. Perché gli elettroni negli atomi possono cambiare solo tra livelli energetici permessi ✅
- B. Perché gli elettroni possono avere qualsiasi energia senza limiti
- C. Perché i nuclei atomici emettono sempre suoni udibili
- D. Perché la luce visibile non contiene energia

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_035 — livello: intermedio

**Domanda:** Che cosa afferma l'ipotesi di de Broglie?

**Opzioni attuali:**
- A. Anche le particelle materiali possono avere proprietà ondulatorie ✅
- B. Solo le onde sonore possono comportarsi come particelle
- C. Gli elettroni non possono mai mostrare interferenza
- D. La luce è sempre soltanto un fenomeno meccanico classico

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “mai”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_036 — livello: intermedio

**Domanda:** Perché l'esperimento della doppia fenditura è importante in fisica quantistica?

**Opzioni attuali:**
- A. Mostra che particelle come elettroni o fotoni possono produrre figure di interferenza ✅
- B. Dimostra che gli elettroni sono sempre oggetti macroscopici visibili
- C. Dimostra che la luce non può attraversare aperture
- D. Mostra che la gravità scompare vicino a due fenditure

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_037 — livello: intermedio

**Domanda:** Che cosa significa dire che due stati quantistici interferiscono?

**Opzioni attuali:**
- A. Le loro ampiezze di probabilità si combinano, aumentando o riducendo la probabilità di certi risultati ✅
- B. Le loro masse si sommano sempre fino a diventare infinite
- C. Le particelle smettono di avere qualsiasi proprietà fisica
- D. La misura diventa impossibile in ogni situazione

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_038 — livello: avanzato

**Domanda:** Che cosa distingue uno stato puro da uno stato misto in meccanica quantistica?

**Opzioni attuali:**
- A. Uno stato puro è descritto da una singola funzione d'onda, mentre uno stato misto rappresenta una distribuzione statistica di stati ✅
- B. Uno stato puro contiene solo protoni, mentre uno stato misto contiene solo neutroni
- C. Uno stato puro è sempre macroscopico, mentre uno stato misto è sempre invisibile
- D. Uno stato misto non può mai essere descritto matematicamente

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “mai”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.
