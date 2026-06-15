<!-- ALEX-QUIZ-DASHBOARD-START -->

# 🚀 Alex AI Quiz Database

**Alex AI Quiz Database** è un motore riutilizzabile per creare quiz interattivi con:

- database domande in formato JSON
- motore Web HTML / JavaScript
- motore Android Kotlin
- controlli qualità su domande, risposte e duplicati
- pacchetti scaricabili pronti da usare

Il progetto non è solo una demo online: può essere usato anche come base tecnica per creare nuove app quiz personalizzate su qualunque argomento.

## Aree disponibili

| Area | Contenuti | Pacchetti scaricabili |
|---|---|---|
| **AI / ITS** | AI, Informatica, Logica, Logica visiva, Matematica, Inglese | [Web ZIP](https://github.com/aleb2016-maker/alex-ai-quiz-database/raw/main/downloads/pacchetto-web-ai-its-demo.zip) · [Android ZIP](https://github.com/aleb2016-maker/alex-ai-quiz-database/raw/main/downloads/pacchetto-android-ai-its-finale-semplice.zip) |
| **Scienze** | Fisica, Chimica, Biologia, Fisica Quantistica, Scienze generali | [Web ZIP](https://github.com/aleb2016-maker/alex-ai-quiz-database/raw/main/downloads/pacchetto-web-scienze-demo.zip) · [Android ZIP](https://github.com/aleb2016-maker/alex-ai-quiz-database/raw/main/downloads/pacchetto-android-finale-semplice.zip) |

## Crea un pacchetto personalizzato

Puoi generare un nuovo pacchetto scegliendo piattaforma, materia, livello e numero di domande:

[Apri il workflow GitHub Actions](https://github.com/aleb2016-maker/alex-ai-quiz-database/actions/workflows/create-quiz-package.yml)

<!-- ALEX-QUIZ-DASHBOARD-END -->


<!-- DEMO_BUTTON_START -->

<table align="center">
  <tr>
    <td align="center" width="50%">
      <a href="https://aleb2016-maker.github.io/alex-ai-quiz-database/demo/" target="_blank">
        <img
          src="https://img.shields.io/badge/%E2%96%B6%20AVVIA%20DEMO%20ONLINE%20AI%20ITS-0F766E?style=for-the-badge&logo=githubpages&logoColor=white"
          alt="Avvia demo online AI ITS"
        >
      </a>
      <br>
      <br>
      <div align="center" style="font-size: 28px;">☝️</div>
      <strong>Prova subito il quiz AI / ITS</strong>
      <br>
      <small>AI · Informatica · Logica · Logica visiva · Matematica · Inglese</small>
    </td>
    <td align="center" width="50%">
      <a href="https://aleb2016-maker.github.io/alex-ai-quiz-database/demo-scienze/" target="_blank">
        <img
          src="https://img.shields.io/badge/%F0%9F%AA%90%20AVVIA%20DEMO%20ONLINE%20SCIENZE-4F46E5?style=for-the-badge&logo=githubpages&logoColor=white"
          alt="Avvia demo online Scienze"
        >
      </a>
      <br>
      <br>
      <div align="center" style="font-size: 28px;">☝️</div>
      <strong>Prova subito il quiz sulle materie scientifiche</strong>
      <br>
      <small>Fisica · Chimica · Biologia · Fisica Quantistica · Scienze generali</small>
    </td>
  </tr>
</table>

<!-- DEMO_BUTTON_END -->


## Demo online

La demo online permette di provare il progetto direttamente dal browser, senza installare nulla.

Sono disponibili due percorsi:

- **Demo AI / ITS**: quiz su AI, Informatica, Logica, Logica visiva, Matematica e Inglese.
- **Demo Scienze**: quiz su Fisica, Chimica, Biologia, Fisica Quantistica e Scienze generali.

Funzioni principali:

- scelta categoria
- scelta livello
- domande casuali
- feedback immediato
- spiegazione dopo ogni risposta
- supporto alle domande visuali


## Descrizione del progetto

Il progetto è un sistema Python/JSON per creare, validare e distribuire quiz interattivi.

Contiene due aree principali:

- **AI / ITS**: AI, Informatica, Logica, Logica visiva, Matematica e Inglese.
- **Scienze**: Fisica, Chimica, Biologia, Fisica Quantistica e Scienze generali.

Il database può essere usato per demo online, app Android, app web, simulatori di test, allenamento personale e nuovi quiz personalizzati.

## Funzioni principali

- creazione di domande in file JSON separati per categoria;
- validazione automatica della struttura delle domande;
- controllo duplicati, domande troppo simili e opzioni duplicate;
- generazione del database finale unico;
- generazione di report per categoria e livello;
- pesca casuale intelligente delle domande;
- spiegazioni dopo ogni risposta;
- supporto a domande visuali di logica;
- pacchetti Web e Android pronti da scaricare;
- workflow GitHub per creare pacchetti personalizzati.

## Controlli qualità

Il progetto include controlli automatici per mantenere alta la qualità del database:

- struttura JSON corretta;
- risposte complete;
- opzioni non duplicate;
- domande non identiche;
- domande non troppo simili;
- controllo dei percorsi immagini;
- revisione linguistica opzionale con AI locale tramite Ollama e Gemma 4 12B.

## Categorie e sottosezioni

| Area | Categorie |
|---|---|
| **AI / ITS** | AI, Informatica, Matematica, Inglese, Logica |
| **Logica** | Logica verbale, Logica numerica, Ragionamento critico, Ragionamento astratto, Logica visiva |
| **Scienze** | Fisica, Chimica, Biologia, Fisica Quantistica, Scienze generali |


## Struttura del progetto

```text
data/
  ai.json
  biologia.json
  chimica.json
  fisica.json
  fisica_quantistica.json
  informatica.json
  inglese.json
  matematica.json
  scienze.json
  logica/
    logica_numerica.json
    logica_verbale.json
    logica_visiva.json
    ragionamento_astratto.json
    ragionamento_critico.json

demo/
  index.html
  quiz-engine.js
  database_quiz.json

demo-scienze/
  index.html
  quiz-engine.js
  database_quiz.json
  science-space-effect.css
  science-space-effect.js

downloads/
  pacchetto-web-ai-its-demo.zip
  pacchetto-android-ai-its-finale-semplice.zip
  pacchetto-web-scienze-demo.zip
  pacchetto-android-finale-semplice.zip

scripts/
  validate_questions.py
  check_duplicates.py
  build_database.py
  report_database.py
  create_quiz_package.py

dist/
  database_quiz_finale.json
```
