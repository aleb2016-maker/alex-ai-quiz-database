# Alex AI Quiz Database

Questo progetto contiene un sistema per creare, controllare e costruire un database JSON di domande per un'app di preparazione ai test.

Il progetto è pensato per allenarsi su:

* AI
* Informatica
* Matematica
* Inglese
* Logica

La sezione Logica è divisa in più sottocategorie, comprese domande testuali e domande visive.

---

## Obiettivo del progetto

L'obiettivo è costruire un database di quiz ordinato, controllato e riutilizzabile in un'app Android, in un'app web o in altri strumenti di allenamento.

Il sistema permette di:

* scrivere domande in file JSON separati
* controllare se i JSON sono corretti
* evitare domande duplicate o troppo simili
* controllare i percorsi delle immagini per le domande visive
* creare un unico database finale
* generare un report delle domande per categoria e livello
* testare una pesca casuale intelligente delle domande

---

## Categorie principali

* AI
* Informatica
* Matematica
* Inglese
* Logica

---

## Sottosezioni della logica

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
  build_database.py
  report_database.py
  run_all_checks.py
  test_random_picker.py

assets/
  logica_visiva/

dist/
  database_quiz_finale.json
```

---

## Formato delle domande

Ogni domanda contiene campi strutturati come:

```json
{
  "id": "AI-FAC-0001",
  "categoria": "ai",
  "sottocategoria": "llm",
  "livello": "facile",
  "domanda": "Testo della domanda",
  "opzioni": [
    "Risposta A",
    "Risposta B",
    "Risposta C",
    "Risposta D"
  ],
  "risposta_corretta": "Risposta A",
  "spiegazione": "Spiegazione della risposta corretta",
  "tags": ["tag1", "tag2"],
  "difficolta": 1
}
```

---

## Tipi di domanda supportati

Il progetto supporta due tipi di domanda:

* `testo`
* `immagine`

Le domande visive usano anche questi campi:

```json
{
  "tipo_domanda": "immagine",
  "immagine_domanda": "assets/logica_visiva/esempio_domanda.png",
  "immagini_opzioni": [
    "assets/logica_visiva/esempio_A.png",
    "assets/logica_visiva/esempio_B.png",
    "assets/logica_visiva/esempio_C.png",
    "assets/logica_visiva/esempio_D.png"
  ]
}
```

---

## Script disponibili

### Validazione struttura JSON

```bash
python scripts/validate_questions.py
```

Controlla che ogni domanda abbia i campi obbligatori, 4 opzioni, una risposta corretta valida, una categoria valida, un livello valido e una difficoltà corretta.

---

### Controllo duplicati e somiglianze

```bash
python scripts/check_duplicates.py
```

Controlla:

* domande identiche
* domande troppo simili
* opzioni duplicate nella stessa domanda

---

### Controllo percorsi immagini

```bash
python scripts/check_image_paths.py
```

Controlla se i file immagine indicati nelle domande visive esistono davvero nella cartella `assets/logica_visiva/`.

---

### Creazione database finale

```bash
python scripts/build_database.py
```

Unisce tutti i file JSON della cartella `data/` in un unico file finale.

Il database finale viene creato in:

```text
dist/database_quiz_finale.json
```

---

### Report del database

```bash
python scripts/report_database.py
```

Mostra quante domande ci sono per categoria e per livello.

---

### Test random intelligente

```bash
python scripts/test_random_picker.py
```

Simula una selezione casuale delle domande evitando di ripetere sempre le stesse.

---

## Comando principale

Per eseguire tutti i controlli principali:

```bash
python scripts/run_all_checks.py
```

Questo comando esegue:

1. controllo struttura JSON
2. controllo duplicati e somiglianze
3. controllo percorsi immagini
4. creazione database finale
5. report finale

---

## Stato attuale del database

Il database contiene attualmente:

* 27 domande totali
* 9 domande facili
* 9 domande intermedie
* 9 domande avanzate

Distribuzione per categoria:

* AI: 3 domande
* Informatica: 3 domande
* Matematica: 3 domande
* Inglese: 3 domande
* Logica: 15 domande

Distribuzione della logica:

* Logica verbale
* Ragionamento critico
* Logica numerica
* Ragionamento astratto
* Logica visiva

---

## Nota sulla logica visiva

Le domande di logica visiva sono già presenti nel JSON con i relativi percorsi immagine.

I file PNG della cartella `assets/logica_visiva/` possono essere creati o completati successivamente.

---

## Utilizzo futuro

Questo progetto può essere usato come base per:

* app Android di allenamento quiz
* app web quiz
* sistemi di test personalizzati
* generatori di quiz basati su JSON
* database di preparazione per test logici, informatici e AI

---

## Note

Il progetto è progettato per funzionare senza API a pagamento.

La parte principale è basata su:

* Python
* JSON locali
* controlli automatici
* struttura compatibile con app Android o web
