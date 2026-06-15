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

data class AnswerResult(
    val isCorrect: Boolean,
    val selectedAnswer: String,
    val correctAnswer: String,
    val explanation: String,
    val score: Int,
    val totalAnswered: Int
)

data class QualityIssue(
    val questionId: String,
    val severity: String,
    val message: String
)
