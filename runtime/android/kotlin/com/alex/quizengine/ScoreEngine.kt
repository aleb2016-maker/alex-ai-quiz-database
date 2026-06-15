package com.alex.quizengine

object ScoreEngine {

    fun percentage(score: Int, total: Int): Int {
        if (total <= 0) {
            return 0
        }

        return ((score.toDouble() / total.toDouble()) * 100).toInt()
    }

    fun label(score: Int, total: Int): String {
        val percentage = percentage(score, total)

        return when {
            percentage >= 100 -> "Eccellente"
            percentage >= 95 -> "Ottimo"
            percentage >= 90 -> "Distinto"
            percentage >= 80 -> "Buono"
            percentage >= 70 -> "Discreto"
            percentage >= 60 -> "Sufficiente"
            else -> "Da migliorare"
        }
    }

    fun finalMessage(score: Int, total: Int): String {
        return "Risultato: $score/$total - ${label(score, total)}"
    }
}
