package com.alex.quizengine

import android.content.Context
import org.json.JSONArray
import org.json.JSONObject

object QuizRepository {

    fun loadFromAssets(
        context: Context,
        fileName: String = "database_quiz.json"
    ): List<QuizQuestion> {
        val jsonText = context.assets.open(fileName)
            .bufferedReader()
            .use { it.readText() }

        return parseQuestions(jsonText)
    }

    fun parseQuestions(jsonText: String): List<QuizQuestion> {
        val cleanText = jsonText.trim()

        val array = if (cleanText.startsWith("[")) {
            JSONArray(cleanText)
        } else {
            val root = JSONObject(cleanText)

            when {
                root.has("quiz") -> root.getJSONArray("quiz")
                root.has("domande") -> root.getJSONArray("domande")
                root.has("questions") -> root.getJSONArray("questions")
                else -> JSONArray()
            }
        }

        val questions = mutableListOf<QuizQuestion>()

        for (index in 0 until array.length()) {
            val item = array.getJSONObject(index)

            questions.add(
                QuizQuestion(
                    id = readText(item, "id", "Q_${index + 1}"),
                    categoria = readText(item, "categoria", "category"),
                    sottocategoria = readText(item, "sottocategoria", "subcategory"),
                    livello = readText(item, "livello", "difficulty"),
                    domanda = readText(item, "domanda", "question"),
                    opzioni = readOptions(item),
                    rispostaCorretta = readText(
                        item,
                        "risposta_corretta",
                        "correct_answer",
                        "answer"
                    ),
                    spiegazione = readText(item, "spiegazione", "explanation"),
                    distrattoreForte = readText(
                        item,
                        "distrattore_forte",
                        "strong_distractor"
                    ),
                    tags = readStringList(item.opt("tags"))
                )
            )
        }

        return questions
    }

    private fun readOptions(item: JSONObject): List<String> {
        val optionsValue = item.opt("opzioni") ?: item.opt("options")
        return readStringList(optionsValue)
    }

    private fun readText(
        item: JSONObject,
        vararg keys: String
    ): String {
        for (key in keys) {
            if (item.has(key)) {
                val value = item.optString(key, "").trim()

                if (value.isNotBlank()) {
                    return value
                }
            }
        }

        return ""
    }

    private fun readStringList(value: Any?): List<String> {
        return when (value) {
            is JSONArray -> {
                val result = mutableListOf<String>()

                for (index in 0 until value.length()) {
                    result.add(value.optString(index, "").trim())
                }

                result.filter { it.isNotBlank() }
            }

            is JSONObject -> {
                val result = mutableListOf<String>()
                val preferredKeys = listOf("A", "B", "C", "D", "a", "b", "c", "d")

                preferredKeys.forEach { key ->
                    if (value.has(key)) {
                        result.add(value.optString(key, "").trim())
                    }
                }

                result.filter { it.isNotBlank() }
            }

            else -> emptyList()
        }
    }
}
