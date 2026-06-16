# Report qualità distrattori motori scientifici

Questo report separa i problemi qualitativi reali dagli avvisi non bloccanti sulla posizione della risposta corretta nel file sorgente.

## Riepilogo

| Motore | Domande | Problemi qualità reali | Risposta in A nel sorgente |
|---|---:|---:|---:|
| Scienze generali | 40 | 16 | 34 |
| Biologia | 40 | 0 | 40 |
| Fisica | 40 | 21 | 40 |
| Chimica | 40 | 8 | 40 |
| Fisica quantistica | 40 | 21 | 40 |

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
Domande con problemi qualità reali: **21**
Risposte corrette in A nel sorgente: **40**

Distribuzione risposta corretta nel sorgente:

```text
{'A': 40}
```

### Domande da migliorare davvero

### FIS_002 — livello: facile

**Domanda:** Che cosa succede al moto di un corpo quando agisce su di esso una forza risultante non nulla?

**Opzioni attuali:**
- A. Il corpo modifica il proprio stato di moto accelerando ✅
- B. Il corpo resta sempre fermo indipendentemente dalla forza
- C. Il corpo perde automaticamente tutta la propria massa
- D. Il corpo cambia temperatura ma non può cambiare velocità

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_008 — livello: intermedio

**Domanda:** Che cosa accade alla pressione esercitata da una forza se la stessa forza agisce su una superficie più piccola?

**Opzioni attuali:**
- A. La pressione aumenta ✅
- B. La pressione diminuisce sempre
- C. La pressione resta sempre uguale
- D. La pressione diventa automaticamente nulla

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_010 — livello: avanzato

**Domanda:** Che cosa afferma il principio di conservazione dell’energia meccanica in assenza di attriti?

**Opzioni attuali:**
- A. La somma di energia cinetica e potenziale resta costante ✅
- B. L’energia cinetica resta sempre uguale in ogni punto
- C. L’energia potenziale resta sempre uguale in ogni punto
- D. La velocità del corpo resta sempre nulla

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_012 — livello: avanzato

**Domanda:** Che cosa succede alla lunghezza d’onda di un’onda se la frequenza aumenta e la velocità di propagazione resta costante?

**Opzioni attuali:**
- A. La lunghezza d’onda diminuisce ✅
- B. La lunghezza d’onda aumenta
- C. La lunghezza d’onda resta sempre uguale
- D. La lunghezza d’onda diventa infinita

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_015 — livello: facile

**Domanda:** Che cosa fa di solito la forza di attrito tra due superfici a contatto?

**Opzioni attuali:**
- A. Si oppone al movimento relativo tra le superfici ✅
- B. Aumenta sempre la velocità senza consumo di energia
- C. Elimina completamente la massa degli oggetti
- D. Agisce solo quando gli oggetti sono nel vuoto

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_017 — livello: intermedio

**Domanda:** Perché un corpo immerso in un fluido può ricevere una spinta verso l’alto?

**Opzioni attuali:**
- A. Perché il fluido esercita una spinta di Archimede legata al volume spostato ✅
- B. Perché il corpo perde completamente la propria massa dentro il fluido
- C. Perché il fluido annulla sempre la forza di gravità
- D. Perché il corpo diventa automaticamente meno denso dell’aria

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_018 — livello: intermedio

**Domanda:** Che cosa avviene in genere a un solido quando viene riscaldato?

**Opzioni attuali:**
- A. Le sue particelle vibrano di più e il corpo tende a dilatarsi ✅
- B. Le sue particelle si fermano completamente
- C. La sua massa diventa sempre uguale a zero
- D. Il suo volume diminuisce sempre in ogni materiale

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_019 — livello: intermedio

**Domanda:** In un circuito con resistenze in serie, che cosa accade alla resistenza equivalente?

**Opzioni attuali:**
- A. È la somma delle resistenze dei singoli componenti ✅
- B. È sempre minore della resistenza più piccola
- C. È sempre uguale a zero
- D. È indipendente dal numero di resistenze

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_020 — livello: intermedio

**Domanda:** Che cosa distingue una grandezza vettoriale da una grandezza scalare?

**Opzioni attuali:**
- A. La grandezza vettoriale ha modulo, direzione e verso ✅
- B. La grandezza vettoriale non può mai essere misurata
- C. La grandezza scalare ha sempre direzione e verso
- D. La grandezza scalare è sempre negativa

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “mai”.
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_021 — livello: avanzato

**Domanda:** Secondo la legge di Coulomb, che cosa succede alla forza elettrica se la distanza tra due cariche raddoppia?

**Opzioni attuali:**
- A. Diventa un quarto del valore iniziale ✅
- B. Diventa il doppio del valore iniziale
- C. Resta esattamente invariata
- D. Diventa sempre nulla

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_023 — livello: avanzato

**Domanda:** Che cosa accade in un fenomeno di risonanza?

**Opzioni attuali:**
- A. Un sistema oscilla con ampiezza maggiore quando viene sollecitato vicino alla sua frequenza naturale ✅
- B. Un sistema smette sempre di oscillare quando riceve energia periodica
- C. La frequenza naturale diventa sempre uguale a zero
- D. L’energia fornita viene sempre trasformata interamente in massa

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_025 — livello: facile

**Domanda:** Perché riusciamo a vedere un oggetto che non produce luce propria?

**Opzioni attuali:**
- A. Perché riflette luce che arriva ai nostri occhi ✅
- B. Perché trasforma sempre la propria massa in luce
- C. Perché emette sempre onde sonore visibili
- D. Perché assorbe tutta la luce senza rimandarne nessuna

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_026 — livello: facile

**Domanda:** Che cosa accade a una molla elastica quando viene deformata entro il suo limite elastico?

**Opzioni attuali:**
- A. Tende a tornare alla forma iniziale quando la forza viene tolta ✅
- B. Perde sempre tutta la propria massa
- C. Si trasforma definitivamente in un liquido
- D. Smette di esercitare qualunque forza

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_028 — livello: intermedio

**Domanda:** Quando un corpo è in equilibrio statico?

**Opzioni attuali:**
- A. Quando la forza risultante e il momento risultante sono nulli ✅
- B. Quando la velocità aumenta sempre in modo costante
- C. Quando agisce una sola forza non bilanciata
- D. Quando il corpo non possiede massa misurabile

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_029 — livello: intermedio

**Domanda:** Perché il suono non si propaga nel vuoto?

**Opzioni attuali:**
- A. Perché ha bisogno di un mezzo materiale che trasmetta le vibrazioni ✅
- B. Perché nel vuoto la luce assorbe tutte le onde sonore
- C. Perché nel vuoto la temperatura è sempre infinita
- D. Perché il suono è formato da particelle con massa nulla

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_031 — livello: avanzato

**Domanda:** Che cosa accade alla corrente in un circuito se la tensione resta costante e la resistenza aumenta?

**Opzioni attuali:**
- A. La corrente diminuisce ✅
- B. La corrente aumenta sempre
- C. La corrente resta identica in ogni caso
- D. La corrente diventa indipendente dalla resistenza

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_033 — livello: facile

**Domanda:** Perché l’ago di una bussola tende a orientarsi sempre in una direzione precisa?

**Opzioni attuali:**
- A. Perché interagisce con il campo magnetico terrestre ✅
- B. Perché viene attratto direttamente dalla massa della Terra
- C. Perché misura la temperatura dell’aria intorno alla bussola
- D. Perché ruota sempre nella direzione del vento più forte

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_034 — livello: facile

**Domanda:** Che cosa succede a un corpo se riceve calore?

**Opzioni attuali:**
- A. Può aumentare la temperatura o cambiare stato fisico ✅
- B. Perde sempre tutta la propria massa
- C. Smette sempre di occupare spazio
- D. Si trasforma sempre in carica elettrica

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_035 — livello: intermedio

**Domanda:** Qual è la differenza tra calore e temperatura?

**Opzioni attuali:**
- A. Il calore è energia trasferita, la temperatura indica lo stato termico del corpo ✅
- B. Il calore è una forza, la temperatura è sempre una massa
- C. Il calore si misura solo in metri, la temperatura solo in newton
- D. Il calore esiste solo nei solidi, la temperatura solo nei gas

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_036 — livello: intermedio

**Domanda:** Che cosa avviene quando due corpi a temperatura diversa vengono messi a contatto?

**Opzioni attuali:**
- A. Il calore passa spontaneamente dal corpo più caldo a quello più freddo ✅
- B. Il calore passa sempre dal corpo più freddo a quello più caldo
- C. Le masse dei due corpi diventano automaticamente uguali
- D. La gravità tra i due corpi si annulla completamente

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FIS_037 — livello: intermedio

**Domanda:** Perché una leva può permettere di sollevare un carico con minore forza?

**Opzioni attuali:**
- A. Perché aumenta il braccio della forza applicata rispetto al fulcro ✅
- B. Perché elimina completamente il peso del carico
- C. Perché trasforma il carico in energia elettrica
- D. Perché annulla sempre l’attrito dell’aria

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

## Chimica

Domande sorgente: **40**
Domande con problemi qualità reali: **8**
Risposte corrette in A nel sorgente: **40**

Distribuzione risposta corretta nel sorgente:

```text
{'A': 40}
```

### Domande da migliorare davvero

### CHE_032 — livello: avanzato

**Domanda:** Che cosa indica il prodotto ionico dell’acqua in relazione a H⁺ e OH⁻?

**Opzioni attuali:**
- A. Che in acqua le concentrazioni di H⁺ e OH⁻ sono collegate da una relazione di equilibrio ✅
- B. Che ogni soluzione acquosa contiene solo ioni H⁺ e nessun altro ione
- C. Che gli ioni OH⁻ sono presenti solo nelle soluzioni completamente neutre
- D. Che il pH non dipende mai dalla concentrazione degli ioni in soluzione

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “mai”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### CHE_033 — livello: facile

**Domanda:** Che cosa avviene durante l’evaporazione di un liquido?

**Opzioni attuali:**
- A. Alcune particelle passano dallo stato liquido allo stato gassoso dalla superficie ✅
- B. Tutte le particelle diventano solide nello stesso istante
- C. Il liquido si trasforma sempre in una nuova sostanza chimica
- D. Gli atomi del liquido vengono distrutti e sostituiti

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### CHE_034 — livello: facile

**Domanda:** Che cosa descrive meglio un composto chimico?

**Opzioni attuali:**
- A. Una sostanza formata da elementi diversi uniti chimicamente in proporzioni definite ✅
- B. Una miscela casuale di sostanze che può avere qualunque composizione
- C. Un elemento puro formato da un solo tipo di atomo isolato
- D. Una soluzione che contiene sempre acqua come unico solvente

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### CHE_035 — livello: intermedio

**Domanda:** Perché un indicatore acido-base può cambiare colore in soluzioni diverse?

**Opzioni attuali:**
- A. Perché assume forme diverse a seconda del pH della soluzione ✅
- B. Perché trasforma sempre l’acido in una base forte
- C. Perché elimina tutti gli ioni presenti nella soluzione
- D. Perché misura direttamente la massa del soluto disciolto

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### CHE_036 — livello: intermedio

**Domanda:** Perché aumentare la concentrazione dei reagenti può rendere più veloce una reazione?

**Opzioni attuali:**
- A. Perché aumenta la frequenza degli urti tra particelle reagenti ✅
- B. Perché diminuisce sempre la temperatura della soluzione
- C. Perché annulla completamente l’energia di attivazione
- D. Perché trasforma i prodotti in reagenti solidi

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### CHE_038 — livello: avanzato

**Domanda:** Secondo il principio di Le Châtelier, come reagisce un sistema all’equilibrio se viene perturbato?

**Opzioni attuali:**
- A. Si sposta nel verso che tende a contrastare la perturbazione ✅
- B. Si ferma definitivamente e non può più reagire
- C. Trasforma tutti i prodotti in catalizzatori permanenti
- D. Rende sempre uguali le concentrazioni di tutte le specie

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### CHE_039 — livello: avanzato

**Domanda:** Che cosa caratterizza una soluzione tampone?

**Opzioni attuali:**
- A. Resiste a variazioni di pH quando si aggiungono piccole quantità di acido o base ✅
- B. Mantiene sempre il pH esattamente uguale a 14
- C. Trasforma ogni acido debole in un acido forte
- D. Elimina completamente tutti gli ioni dalla soluzione

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### CHE_040 — livello: avanzato

**Domanda:** Perché in una titolazione acido-base si usa spesso un indicatore?

**Opzioni attuali:**
- A. Per individuare con un cambiamento di colore il punto vicino all’equivalenza ✅
- B. Per aumentare sempre la concentrazione dell’acido titolato
- C. Per sostituire completamente la buretta durante la misura
- D. Per impedire qualunque reazione tra acido e base

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

## Fisica quantistica

Domande sorgente: **40**
Domande con problemi qualità reali: **21**
Risposte corrette in A nel sorgente: **40**

Distribuzione risposta corretta nel sorgente:

```text
{'A': 40}
```

### Domande da migliorare davvero

### FQ_001 — livello: facile

**Domanda:** Che cosa indica, in modo generale, la parola 'quanto' in fisica quantistica?

**Opzioni attuali:**
- A. Una quantità minima e discreta di una grandezza fisica ✅
- B. Una quantità continua che può assumere qualunque valore
- C. Una forza che agisce solo sui corpi macroscopici
- D. Una particella sempre visibile a occhio nudo

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_004 — livello: facile

**Domanda:** Che cosa afferma il dualismo onda-particella?

**Opzioni attuali:**
- A. Che oggetti microscopici possono mostrare sia proprietà ondulatorie sia proprietà corpuscolari ✅
- B. Che ogni particella è sempre solo un'onda classica
- C. Che ogni onda è sempre visibile come una particella macroscopica
- D. Che onde e particelle non hanno mai alcuna relazione

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “mai”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_007 — livello: facile

**Domanda:** Che cosa significa dire che l'energia di un elettrone in un atomo è quantizzata?

**Opzioni attuali:**
- A. Che può assumere solo certi valori permessi ✅
- B. Che può assumere qualsiasi valore senza limiti
- C. Che è sempre uguale a zero
- D. Che dipende solo dalla temperatura dell'aria

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_008 — livello: facile

**Domanda:** Che cosa accade quando un elettrone passa da un livello energetico alto a uno più basso?

**Opzioni attuali:**
- A. Può emettere un fotone ✅
- B. Scompare dal nucleo
- C. Diventa un protone
- D. Perde sempre tutta la sua massa

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_009 — livello: facile

**Domanda:** Quale idea è centrale nella fisica quantistica rispetto alla misura?

**Opzioni attuali:**
- A. Il risultato di una misura può essere probabilistico ✅
- B. Ogni misura dà sempre un valore prevedibile con certezza assoluta
- C. Le misure sono possibili solo su oggetti grandi
- D. La misura elimina sempre la massa della particella

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_011 — livello: intermedio

**Domanda:** Che cosa afferma il principio di indeterminazione di Heisenberg?

**Opzioni attuali:**
- A. Non è possibile conoscere contemporaneamente con precisione arbitraria posizione e quantità di moto di una particella ✅
- B. Non è possibile misurare mai la massa di una particella
- C. Ogni particella si muove sempre lungo una traiettoria perfettamente visibile
- D. La velocità della luce cambia in base alla massa dell'osservatore

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “mai”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_013 — livello: intermedio

**Domanda:** Che cosa significa sovrapposizione quantistica?

**Opzioni attuali:**
- A. Un sistema può trovarsi in una combinazione di più stati possibili prima della misura ✅
- B. Un sistema può occupare solo uno stato classico già determinato e visibile
- C. Due oggetti macroscopici devono sempre stare nello stesso luogo
- D. Una particella perde automaticamente tutta la sua energia

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_014 — livello: intermedio

**Domanda:** Che cosa indica il termine entanglement quantistico?

**Opzioni attuali:**
- A. Una correlazione tra sistemi quantistici tale che lo stato di uno è legato allo stato dell'altro ✅
- B. Una collisione meccanica tra due pianeti
- C. Una forza che trasforma sempre un elettrone in un neutrone
- D. Una vibrazione sonora prodotta da due onde acustiche

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_017 — livello: intermedio

**Domanda:** Che cosa afferma il principio di esclusione di Pauli?

**Opzioni attuali:**
- A. Due fermioni identici non possono occupare lo stesso stato quantico completo ✅
- B. Due fotoni non possono mai trovarsi nello stesso luogo
- C. Ogni elettrone deve avere sempre energia infinita
- D. Ogni particella deve decadere immediatamente

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “mai”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_019 — livello: intermedio

**Domanda:** Che cosa succede alla funzione d'onda secondo l'idea del collasso durante una misura?

**Opzioni attuali:**
- A. Lo stato viene associato a uno dei risultati possibili della misura ✅
- B. La particella perde sempre tutta la massa
- C. Il sistema diventa automaticamente invisibile
- D. La funzione d'onda si trasforma sempre in calore

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_022 — livello: avanzato

**Domanda:** In meccanica quantistica, che cosa rappresenta un operatore?

**Opzioni attuali:**
- A. Un oggetto matematico associato a una grandezza fisica misurabile ✅
- B. Una particella che trasporta sempre carica elettrica positiva
- C. Una forza macroscopica che agisce solo sui liquidi
- D. Un dispositivo meccanico usato solo nei motori termici

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_024 — livello: avanzato

**Domanda:** Perché il commutatore tra due operatori è importante in meccanica quantistica?

**Opzioni attuali:**
- A. Perché indica se due grandezze possono avere valori ben definiti simultaneamente ✅
- B. Perché misura sempre la velocità della luce nel vuoto
- C. Perché trasforma automaticamente un bosone in un fermione
- D. Perché stabilisce la massa totale dell'universo

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_025 — livello: avanzato

**Domanda:** Che cosa suggeriscono le disuguaglianze di Bell quando vengono violate sperimentalmente?

**Opzioni attuali:**
- A. Che certe correlazioni quantistiche non sono spiegabili con semplici variabili nascoste locali ✅
- B. Che la fisica quantistica è sempre identica alla meccanica newtoniana
- C. Che gli elettroni non possiedono mai carica elettrica
- D. Che la luce non può mai comportarsi come particella

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.
- Possibile opzione debole/generica: contiene “mai”.
- Possibile opzione debole/generica: contiene “mai”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_027 — livello: avanzato

**Domanda:** Qual è una differenza tra fermioni e bosoni?

**Opzioni attuali:**
- A. I fermioni obbediscono al principio di esclusione di Pauli, mentre i bosoni possono condividere lo stesso stato quantico ✅
- B. I bosoni hanno sempre carica negativa, mentre i fermioni sono sempre neutri
- C. I fermioni sono solo onde sonore, mentre i bosoni sono solo pianeti
- D. I bosoni non esistono nella fisica quantistica

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_029 — livello: avanzato

**Domanda:** Nel modello quantistico dell'atomo, che cosa indicano gli orbitali?

**Opzioni attuali:**
- A. Regioni associate alla probabilità di trovare un elettrone ✅
- B. Percorsi circolari rigidi identici alle orbite dei pianeti
- C. Canali vuoti dove non può mai trovarsi un elettrone
- D. Zone del nucleo occupate solo da fotoni

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “mai”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

### FQ_033 — livello: facile

**Domanda:** Che cosa succede se un fotone ha frequenza maggiore?

**Opzioni attuali:**
- A. Ha energia maggiore ✅
- B. Ha massa a riposo maggiore
- C. Diventa automaticamente un protone
- D. Perde sempre la sua natura elettromagnetica

**Risposta corretta nel sorgente:** A

**Problemi reali:**
- Possibile opzione debole/generica: contiene “sempre”.

**Regola di revisione:**
- Ogni domanda deve avere almeno un distrattore forte: una risposta sbagliata molto vicina alla corretta, ma falsa per un dettaglio preciso.
- Evitare parole assolute come “sempre” e “mai”, se rendono il distrattore troppo eliminabile.
- Rendere le quattro opzioni simili per lunghezza, struttura e livello tecnico.

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
