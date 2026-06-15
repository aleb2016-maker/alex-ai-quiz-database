package com.alex.quizengine

object QuizQualityValidator {

    fun validate(questions: List<QuizQuestion>): List<QualityIssue> {
        val issues = mutableListOf<QualityIssue>()
        val ids = mutableSetOf<String>()

        if (questions.isEmpty()) {
            issues.add(
                QualityIssue(
                    questionId = "DATABASE",
                    severity = "error",
                    message = "Il database non contiene domande."
                )
            )

            return issues
        }

        questions.forEachIndexed { index, question ->
            val questionId = question.id.ifBlank { "QUESTION_${index + 1}" }

            if (question.id.isBlank()) {
                issues.addIssue(questionId, "warning", "ID mancante.")
            }

            if (question.id.isNotBlank() && question.id in ids) {
                issues.addIssue(questionId, "error", "ID duplicato.")
            }

            if (question.id.isNotBlank()) {
                ids.add(question.id)
            }

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

            if (question.opzioni.any { it.isBlank() }) {
                issues.addIssue(questionId, "error", "Una o più opzioni sono vuote.")
            }

            if (question.opzioni.distinct().size != question.opzioni.size) {
                issues.addIssue(questionId, "error", "Ci sono opzioni duplicate.")
            }

            if (question.rispostaCorretta.isBlank()) {
                issues.addIssue(questionId, "error", "Risposta corretta mancante.")
            }

            if (
                question.rispostaCorretta.isNotBlank() &&
                question.rispostaCorretta !in question.opzioni
            ) {
                issues.addIssue(
                    questionId,
                    "error",
                    "La risposta corretta non è presente tra le opzioni."
                )
            }

            if (question.spiegazione.isBlank()) {
                issues.addIssue(questionId, "warning", "Spiegazione mancante.")
            }

            if (question.distrattoreForte.isBlank()) {
                issues.addIssue(questionId, "warning", "Distrattore forte non indicato.")
            }

            if (
                question.distrattoreForte.isNotBlank() &&
                question.distrattoreForte !in question.opzioni
            ) {
                issues.addIssue(
                    questionId,
                    "warning",
                    "Il distrattore forte non è presente tra le opzioni."
                )
            }
        }

        return issues
    }

    fun blockingErrors(questions: List<QuizQuestion>): List<QualityIssue> {
        return validate(questions).filter { it.severity == "error" }
    }

    fun hasBlockingErrors(questions: List<QuizQuestion>): Boolean {
        return blockingErrors(questions).isNotEmpty()
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
