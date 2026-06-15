package com.alex.quizengine

class QuizEngine(
    private val allQuestions: List<QuizQuestion>
) {
    private var activeQuestions: List<QuizQuestion> = emptyList()
    private var currentIndex: Int = 0
    private var score: Int = 0
    private var answeredCount: Int = 0
    private val selectedAnswers: MutableMap<String, String> = mutableMapOf()

    fun startQuiz(config: QuizConfig = QuizConfig()): List<QuizQuestion> {
        return startQuiz(
            categoria = config.categoria,
            livello = config.livello,
            numeroDomande = config.numeroDomande
        )
    }

    fun startQuiz(
        categoria: String = "tutte",
        livello: String = "tutti",
        numeroDomande: Int = 10
    ): List<QuizQuestion> {
        val filteredQuestions = allQuestions
            .filter { categoryMatches(it, categoria) }
            .filter { levelMatches(it, livello) }
            .shuffled()

        activeQuestions = if (numeroDomande <= 0) {
            filteredQuestions
        } else {
            filteredQuestions.take(numeroDomande)
        }

        currentIndex = 0
        score = 0
        answeredCount = 0
        selectedAnswers.clear()

        return activeQuestions
    }

    fun currentQuestion(): QuizQuestion? {
        return activeQuestions.getOrNull(currentIndex)
    }

    fun answer(selectedAnswer: String): AnswerResult {
        val question = currentQuestion()
            ?: throw IllegalStateException("Nessuna domanda attiva.")

        if (selectedAnswer !in question.opzioni) {
            throw IllegalArgumentException("La risposta selezionata non è tra le opzioni della domanda.")
        }

        val answerKey = question.id.ifBlank { "QUESTION_$currentIndex" }

        if (selectedAnswers.containsKey(answerKey)) {
            throw IllegalStateException("Questa domanda ha già ricevuto una risposta.")
        }

        val isCorrect = selectedAnswer == question.rispostaCorretta

        if (isCorrect) {
            score += 1
        }

        answeredCount += 1
        selectedAnswers[answerKey] = selectedAnswer

        return AnswerResult(
            isCorrect = isCorrect,
            selectedAnswer = selectedAnswer,
            correctAnswer = question.rispostaCorretta,
            explanation = question.spiegazione,
            score = score,
            totalAnswered = answeredCount,
            totalQuestions = activeQuestions.size
        )
    }

    fun moveNext(): QuizQuestion? {
        if (hasNext()) {
            currentIndex += 1
        }

        return currentQuestion()
    }

    fun hasNext(): Boolean {
        return currentIndex < activeQuestions.size - 1
    }

    fun isFinished(): Boolean {
        return activeQuestions.isNotEmpty() && answeredCount >= activeQuestions.size
    }

    fun totalQuestions(): Int {
        return activeQuestions.size
    }

    fun currentScore(): Int {
        return score
    }

    fun answeredQuestions(): Int {
        return answeredCount
    }

    fun progressText(): String {
        if (activeQuestions.isEmpty()) {
            return "0/0"
        }

        return "${currentIndex + 1}/${activeQuestions.size}"
    }

    fun summary(): QuizSummary {
        val total = activeQuestions.size
        val percentage = ScoreEngine.percentage(score, total)
        val label = ScoreEngine.label(score, total)

        return QuizSummary(
            score = score,
            totalQuestions = total,
            percentage = percentage,
            label = label,
            finalMessage = ScoreEngine.finalMessage(score, total)
        )
    }

    fun availableCategories(): List<String> {
        return allQuestions
            .map { it.categoria }
            .filter { it.isNotBlank() }
            .distinct()
            .sorted()
    }

    fun availableLevels(): List<String> {
        return allQuestions
            .map { it.livello }
            .filter { it.isNotBlank() }
            .distinct()
            .sorted()
    }

    private fun categoryMatches(question: QuizQuestion, categoria: String): Boolean {
        val selectedCategory = slug(categoria)

        if (selectedCategory == "tutte") {
            return true
        }

        val questionCategory = slug(question.categoria)
        val questionSubcategory = slug(question.sottocategoria)
        val questionTags = question.tags.map { slug(it) }

        if (
            selectedCategory == questionCategory ||
            selectedCategory == questionSubcategory ||
            selectedCategory in questionTags
        ) {
            return true
        }

        return when (selectedCategory) {
            "fisica" -> questionSubcategory.contains("fisica") ||
                questionTags.any { it.contains("fisica") }

            "chimica" -> questionSubcategory.contains("chimica") ||
                questionTags.any { it.contains("chimica") }

            "biologia" -> questionSubcategory.contains("biologia") ||
                questionTags.any { it.contains("biologia") }

            else -> false
        }
    }

    private fun levelMatches(question: QuizQuestion, livello: String): Boolean {
        val selectedLevel = slug(livello)

        if (selectedLevel == "tutti") {
            return true
        }

        return slug(question.livello) == selectedLevel
    }

    private fun slug(text: String): String {
        return text
            .trim()
            .lowercase()
            .replace("à", "a")
            .replace("è", "e")
            .replace("é", "e")
            .replace("ì", "i")
            .replace("ò", "o")
            .replace("ù", "u")
            .replace(" ", "_")
            .replace("-", "_")
    }
}
