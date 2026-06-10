# Alex AI Quiz Database

Sistema Python/JSON per creare, validare e costruire un database di quiz su:

- AI
- Informatica
- Matematica
- Inglese
- Logica

Il progetto è pensato come base per app di allenamento, sistemi di test personalizzati e strumenti di preparazione per prove tecniche, logiche e orientate all’AI.

---

## Obiettivo del progetto

L’obiettivo del progetto è costruire un database di quiz:

- ordinato
- controllato
- espandibile
- riutilizzabile

Il database può essere usato in:

- app Android
- app web
- simulatori di test
- sistemi di allenamento personalizzati

---

## Funzioni principali del progetto

Questo progetto permette di:

- creare domande in file JSON separati per categoria
- validare automaticamente la struttura delle domande
- controllare eventuali duplicati o domande troppo simili
- controllare i percorsi delle immagini nelle domande visive
- unire tutte le domande in un unico database finale
- generare un report con il numero di domande per categoria e livello
- testare una pesca casuale intelligente delle domande
- usare spiegazioni associate alle risposte per migliorare l’apprendimento

---

## Categorie principali

- AI
- Informatica
- Matematica
- Inglese
- Logica

---

## Sottosezioni della logica

La categoria Logica è suddivisa in:

- Logica verbale
- Ragionamento critico
- Logica numerica
- Ragionamento astratto
- Logica visiva

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