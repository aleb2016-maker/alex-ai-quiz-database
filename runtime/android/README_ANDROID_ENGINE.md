# Pacchetto Android Quiz Engine

ATTENZIONE: questo pacchetto NON è un APK.

Non si installa direttamente sul telefono.
Non è una app già pronta da aprire sullo smartphone.
Se si apre con Antigravity, VS Code o un altro editor di codice è normale.

Questo pacchetto serve per Android Studio.

Contiene il database delle domande e un motore Kotlin riutilizzabile per costruire o ampliare una app quiz Android.

CONTENUTO DEL PACCHETTO

- database_quiz.json
- app/src/main/assets/database_quiz.json
- quiz_engine_android/kotlin/com/alex/quizengine/QuizQuestion.kt
- quiz_engine_android/kotlin/com/alex/quizengine/QuizRepository.kt
- quiz_engine_android/kotlin/com/alex/quizengine/QuizEngine.kt
- quiz_engine_android/kotlin/com/alex/quizengine/QuizQualityValidator.kt
- quiz_engine_android/kotlin/com/alex/quizengine/ScoreEngine.kt

COME SI USA IN ANDROID STUDIO

1. Apri Android Studio.

2. Crea una nuova app Android oppure apri una app quiz già esistente.

3. Copia questo file:

   app/src/main/assets/database_quiz.json

   dentro la tua app Android nello stesso percorso:

   app/src/main/assets/database_quiz.json

   Se la cartella assets non esiste, creala dentro app/src/main.

4. Copia i file Kotlin del motore da:

   quiz_engine_android/kotlin/com/alex/quizengine/

   dentro il codice della tua app Android.

5. Collega il motore alla grafica della tua app.

La grafica Android la devi creare tu, per esempio con Jetpack Compose.

Il motore permette di gestire:

- scelta materia
- scelta difficoltà
- scelta 10, 20 o tutte le domande
- lettura del database JSON
- controllo della risposta corretta
- calcolo punteggio
- giudizio finale
- controllo qualità delle domande

DIFFERENZA TRA PACCHETTO WEB E PACCHETTO ANDROID

Il pacchetto Web si apre subito nel browser.

Il pacchetto Android invece è materiale tecnico per sviluppatori.
Serve per costruire una vera app Android dentro Android Studio.

IN PAROLE SEMPLICI

Questo pacchetto Android è il motore più il database.
Non è la macchina completa.
Va inserito dentro Android Studio per costruire l'app quiz.
