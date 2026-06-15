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
                else -> JSONArray()
            }
        }

        val questions = mutableListOf<QuizQuestion>()

        for (index in 0 until array.length()) {
            val item = array.getJSONObject(index)

            val options = readStringList(item.opt("opzioni"))
            val tags = readStringList(item.opt("tags"))

            questions.add(
                QuizQuestion(
                    id = item.optString("id", "Q_${index + 1}"),
                    categoria = item.optString("categoria", ""),
                    sottocategoria = item.optString("sottocategoria", ""),
                    livello = item.optString("livello", ""),
                    domanda = item.optString("domanda", ""),
                    opzioni = options,
                    rispostaCorretta = item.optString("risposta_corretta", ""),
                    spiegazione = item.optString("spiegazione", ""),
                    distrattoreForte = item.optString("distrattore_forte", ""),
                    tags = tags
                )
            )
        }

        return questions
    }

    private fun readStringList(value: Any?): List<String> {
        if (value !is JSONArray) {
            return emptyList()
        }

        val result = mutableListOf<String>()

        for (index in 0 until value.length()) {
            result.add(value.optString(index, "").trim())
        }

        return result.filter { it.isNotBlank() }
    }
}
