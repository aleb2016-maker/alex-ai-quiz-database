package com.alex.quizengine

class QuizEngine(
    private val allQuestions: List<QuizQuestion>
) {
    private var activeQuestions: List<QuizQuestion> = emptyList()
    private var currentIndex: Int = 0
    private var score: Int = 0
    private var answeredCount: Int = 0

    fun startQuiz(
        categoria: String = "tutte",
        livello: String = "tutti",
        numeroDomande: Int = 10
    ): List<QuizQuestion> {
        val filtered = allQuestions
            .filter { categoryMatches(it, categoria) }
            .filter { levelMatches(it, livello) }
            .shuffled()

        activeQuestions = if (numeroDomande <= 0) {
            filtered
        } else {
            filtered.take(numeroDomande)
        }

        currentIndex = 0
        score = 0
        answeredCount = 0

        return activeQuestions
    }

    fun currentQuestion(): QuizQuestion? {
        return activeQuestions.getOrNull(currentIndex)
    }

    fun answer(selectedAnswer: String): AnswerResult {
        val question = currentQuestion()
            ?: throw IllegalStateException("Nessuna domanda attiva.")

        val isCorrect = selectedAnswer == question.rispostaCorretta

        if (isCorrect) {
            score += 1
        }

        answeredCount += 1

        return AnswerResult(
            isCorrect = isCorrect,
            selectedAnswer = selectedAnswer,
            correctAnswer = question.rispostaCorretta,
            explanation = question.spiegazione,
            score = score,
            totalAnswered = answeredCount
        )
    }

    fun moveNext(): QuizQuestion? {
        currentIndex += 1
        return currentQuestion()
    }

    fun hasNext(): Boolean {
        return currentIndex < activeQuestions.size - 1
    }

    fun totalQuestions(): Int {
        return activeQuestions.size
    }

    fun currentScore(): Int {
        return score
    }

    fun progressText(): String {
        if (activeQuestions.isEmpty()) {
            return "0/0"
        }

        return "${currentIndex + 1}/${activeQuestions.size}"
    }

    private fun categoryMatches(question: QuizQuestion, categoria: String): Boolean {
        val selected = slug(categoria)

        if (selected == "tutte") {
            return true
        }

        val category = slug(question.categoria)
        val subcategory = slug(question.sottocategoria)
        val tags = question.tags.map { slug(it) }

        if (selected == category || selected == subcategory || selected in tags) {
            return true
        }

        if (selected == "fisica") {
            return subcategory.contains("fisica") || tags.any { it.contains("fisica") }
        }

        if (selected == "chimica") {
            return subcategory.contains("chimica") || tags.any { it.contains("chimica") }
        }

        if (selected == "biologia") {
            return subcategory.contains("biologia") || tags.any { it.contains("biologia") }
        }

        return false
    }

    private fun levelMatches(question: QuizQuestion, livello: String): Boolean {
        return livello == "tutti" || question.livello == livello
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
