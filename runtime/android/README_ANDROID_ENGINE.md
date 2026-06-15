# Motore Android Quiz

Questo pacchetto non contiene solo un file JSON.

Contiene:

- database_quiz.json
- QuizQuestion.kt
- QuizRepository.kt
- QuizEngine.kt
- QuizQualityValidator.kt
- ScoreEngine.kt

## Dove mettere i file in Android Studio

Copia:

app/src/main/assets/database_quiz.json

dentro:

app/src/main/assets/database_quiz.json

Copia i file Kotlin dentro il package della tua app, oppure mantieni:

com.alex.quizengine

## Cosa fa il motore

QuizRepository.kt
- legge il database JSON dagli assets
- trasforma il JSON in oggetti QuizQuestion

QuizEngine.kt
- filtra per categoria
- filtra per livello
- mescola le domande
- crea test da 10, 20 o tutte le domande
- controlla la risposta
- calcola il punteggio

QuizQualityValidator.kt
- controlla se ogni domanda ha 4 opzioni
- controlla se la risposta corretta è presente tra le opzioni
- controlla se categoria, livello, domanda e spiegazione sono presenti
- segnala problemi prima di avviare il quiz

ScoreEngine.kt
- calcola percentuale
- assegna giudizio finale
