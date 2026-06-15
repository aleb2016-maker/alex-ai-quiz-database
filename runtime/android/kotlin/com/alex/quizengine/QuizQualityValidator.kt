package com.alex.quizengine

object QuizQualityValidator {

    fun validate(questions: List<QuizQuestion>): List<QualityIssue> {
        val issues = mutableListOf<QualityIssue>()
        val ids = mutableSetOf<String>()

        questions.forEachIndexed { index, question ->
            val questionId = question.id.ifBlank { "QUESTION_${index + 1}" }

            if (question.id.isBlank()) {
                issues.addIssue(questionId, "warning", "ID mancante.")
            }

            if (question.id.isNotBlank() && question.id in ids) {
                issues.addIssue(questionId, "error", "ID duplicato.")
            }

            ids.add(question.id)

            if (question.categoria.isBlank()) {
                issues.addIssue(questionId, "error", "Categoria mancante.")
            }

            if (question.livello.isBlank()) {
                issues.addIssue(questionId, "error", "Livello mancante.")
            }

            if (question.domanda.isBlank()) {
                issues.addIssue(questionId, "error", "Testo domanda mancante.")
            }

            if (question.opzioni.size != 4) {
                issues.addIssue(questionId, "error", "La domanda deve avere esattamente 4 opzioni.")
            }

            if (question.opzioni.distinct().size != question.opzioni.size) {
                issues.addIssue(questionId, "error", "Ci sono opzioni duplicate.")
            }

            if (question.rispostaCorretta.isBlank()) {
                issues.addIssue(questionId, "error", "Risposta corretta mancante.")
            }

            if (question.rispostaCorretta !in question.opzioni) {
                issues.addIssue(questionId, "error", "La risposta corretta non è presente tra le opzioni.")
            }

            if (question.spiegazione.isBlank()) {
                issues.addIssue(questionId, "warning", "Spiegazione mancante.")
            }

            if (question.distrattoreForte.isNotBlank() && question.distrattoreForte !in question.opzioni) {
                issues.addIssue(questionId, "warning", "Il distrattore forte non è presente tra le opzioni.")
            }
        }

        return issues
    }

    fun hasBlockingErrors(questions: List<QuizQuestion>): Boolean {
        return validate(questions).any { it.severity == "error" }
    }

    private fun MutableList<QualityIssue>.addIssue(
        questionId: String,
        severity: String,
        message: String
    ) {
        add(
            QualityIssue(
                questionId = questionId,
                severity = severity,
                message = message
            )
        )
    }
}
