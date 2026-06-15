package com.alex.quizengine

data class QuizQuestion(
    val id: String,
    val categoria: String,
    val sottocategoria: String,
    val livello: String,
    val domanda: String,
    val opzioni: List<String>,
    val rispostaCorretta: String,
    val spiegazione: String,
    val distrattoreForte: String = "",
    val tags: List<String> = emptyList()
)

data class QuizConfig(
    val categoria: String = "tutte",
    val livello: String = "tutti",
    val numeroDomande: Int = 10
)

data class AnswerResult(
    val isCorrect: Boolean,
    val selectedAnswer: String,
    val correctAnswer: String,
    val explanation: String,
    val score: Int,
    val totalAnswered: Int,
    val totalQuestions: Int
)

data class QuizSummary(
    val score: Int,
    val totalQuestions: Int,
    val percentage: Int,
    val label: String,
    val finalMessage: String
)

data class QualityIssue(
    val questionId: String,
    val severity: String,
    val message: String
)
