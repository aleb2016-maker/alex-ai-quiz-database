# Alex AI Quiz Database

## Demo online

La demo permette di provare il database direttamente dal browser e può essere utilizzata come supporto per la preparazione personale, test di ingresso, esercitazioni didattiche e allenamento per concorsi.

Funzioni principali:

- scelta categoria
- scelta livello
- test da più domande
- feedback immediato
- spiegazione dopo la risposta
- supporto a domande visuali di logica
## Demo web interattiva

La demo grafica permette di provare il progetto senza usare il terminale.

Funzioni disponibili nella demo:

* selezione della categoria;
* selezione del livello;
* caricamento casuale delle domande;
* risposta tramite pulsanti;
* visualizzazione immediata di risposta corretta o sbagliata;
* spiegazione dopo ogni risposta;
* supporto alle immagini per la logica visiva;
* effetto coriandoli quando la risposta è corretta.


---

## Descrizione del progetto

Sistema Python/JSON per creare, validare e costruire un database di quiz su:

* AI
* Informatica
* Matematica
* Inglese
* Logica

Il progetto è pensato come base per app di allenamento, sistemi di test personalizzati e strumenti di preparazione per prove tecniche, logiche e orientate all’AI.

---

## Obiettivo del progetto

L’obiettivo del progetto è costruire un database di quiz:

* ordinato
* controllato
* espandibile
* riutilizzabile

Il database può essere usato in:

* app Android
* app web
* simulatori di test
* sistemi di allenamento personalizzati

---

## Funzioni principali

Questo progetto permette di:

* creare domande in file JSON separati per categoria;
* validare automaticamente la struttura delle domande;
* controllare eventuali duplicati o domande troppo simili;
* controllare i percorsi delle immagini nelle domande visive;
* unire tutte le domande in un unico database finale;
* generare un report con il numero di domande per categoria e livello;
* testare una pesca casuale intelligente delle domande;
* usare spiegazioni associate alle risposte per migliorare l’apprendimento;
* controllare la qualità linguistica delle domande, delle opzioni e delle spiegazioni;
* segnalare possibili problemi di grammatica, costruzione della frase, punteggiatura e accenti;
* usare un controllo AI opzionale con Gemma 4 12B tramite Ollama per una revisione linguistica più profonda;
* generare un report Markdown con le eventuali domande da rivedere.

---

## Punti di forza

* Revisione linguistica avanzata con AI locale, senza API a pagamento.
* Controllo della qualità del testo prima della pubblicazione del database.
* Possibilità di individuare errori sottili come accenti, apostrofi, frasi poco naturali o spiegazioni poco chiare.
* Struttura modulare, facile da espandere con nuove domande e nuove categorie.
* Database finale generabile automaticamente a partire dai file JSON separati.

---

## Controllo qualità testi con AI locale

Il progetto include anche uno script opzionale per controllare la qualità linguistica dei testi usando Gemma 4 12B installato localmente tramite Ollama.

Lo script controlla:

* grammatica;
* costruzione della frase;
* punteggiatura;
* accenti;
* chiarezza delle spiegazioni;
* naturalezza delle opzioni di risposta.

Comando:

```bash
python scripts/check_text_quality_ai.py
```

Il controllo AI non modifica automaticamente i file JSON. Genera un report in:

```text
dist/text_quality_ai_report.md
```

Questo controllo è pensato come revisione profonda finale, non come controllo quotidiano, perché un modello locale da 12 miliardi di parametri può essere lento.

---

## Categorie principali

* AI
* Informatica
* Matematica
* Inglese
* Logica

---

## Sottosezioni della logica

La categoria Logica è suddivisa in:

* Logica verbale
* Ragionamento critico
* Logica numerica
* Ragionamento astratto
* Logica visiva

---

## Struttura del progetto

```text
data/
  ai.json
  informatica.json
  matematica.json
  inglese.json
  logica/
    logica_verbale.json
    ragionamento_critico.json
    logica_numerica.json
    ragionamento_astratto.json
    logica_visiva.json

scripts/
  validate_questions.py
  check_duplicates.py
  check_image_paths.py
  check_text_quality_ai.py
  generate_logica_visiva_assets.py
  build_database.py
  report_database.py
  run_all_checks.py
  test_random_picker.py

assets/
  logica_visiva/
    immagini PNG per le domande di logica visiva

dist/
  database_quiz_finale.json

demo/
  index.html
  style.css
  app.js

requirements.txt
index.html
README.md
```
