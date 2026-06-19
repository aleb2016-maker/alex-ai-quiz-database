package com.alex.quizengine

import kotlin.random.Random

data class FinalReward(
    val score: Int,
    val total: Int,
    val percent: Int,
    val emoji: String,
    val title: String,
    val badge: String,
    val message: String
)

object FinalRewardEngine {

    private val lastTitleByScore = mutableMapOf<String, String>()

    private val lowRewards = listOf(
        FinalRewardTemplate("🧭", "Allenamento utile", "Base da rinforzare", "Questo risultato serve a capire dove lavorare. Ora il passo importante è correggere gli errori e riprovare meglio."),
        FinalRewardTemplate("🔧", "Ripartenza intelligente", "Correzione mirata", "Hai individuato una zona debole: è una buona notizia, perché adesso sai esattamente dove migliorare."),
        FinalRewardTemplate("📌", "Primo passo utile", "Fondamenta", "Il test non è perso: ti ha mostrato quali concetti vanno ricostruiti con più calma."),
        FinalRewardTemplate("🧱", "Base in costruzione", "Allenamento attivo", "Ogni errore corretto diventa una domanda più facile la prossima volta."),
        FinalRewardTemplate("💡", "Errore trasformabile", "Studio pratico", "Il punteggio è basso, ma il valore è alto se usi le spiegazioni per capire il motivo degli errori."),
        FinalRewardTemplate("🚦", "Segnale chiaro", "Riprova guidata", "Il quiz ti sta dicendo quali argomenti rallentano il percorso. Riparti da quelli.")
    )

    private val mediumLowRewards = listOf(
        FinalRewardTemplate("⚙️", "Meccanismo avviato", "In crescita", "Hai già alcuni punti solidi. Ora devi trasformare le risposte incerte in risposte sicure."),
        FinalRewardTemplate("🧩", "Pezzi da collegare", "Quasi sufficiente", "La base c’è, ma alcuni collegamenti logici vanno resi più precisi."),
        FinalRewardTemplate("📈", "Progressione visibile", "Miglioramento", "Non sei lontano: con una revisione mirata puoi salire rapidamente."),
        FinalRewardTemplate("🎯", "Obiettivo vicino", "Precisione", "Ora serve attenzione ai dettagli: spesso la differenza è in una parola o in una condizione.")
    )

    private val goodRewards = listOf(
        FinalRewardTemplate("✅", "Risultato solido", "Buona base", "Hai superato la soglia utile. Ora punta a ridurre gli errori causati da fretta o distrattori simili."),
        FinalRewardTemplate("🏗️", "Struttura buona", "Consolidamento", "La preparazione c’è. Il prossimo salto arriva distinguendo meglio le opzioni molto vicine."),
        FinalRewardTemplate("🧠", "Ragionamento attivo", "Buon controllo", "Stai ragionando bene. Ora allena la parte più difficile: scegliere tra risposte quasi uguali."),
        FinalRewardTemplate("🚀", "Salita iniziata", "Livello buono", "Il risultato è positivo. Con qualche correzione mirata puoi entrare nella fascia alta.")
    )

    private val highRewards = listOf(
        FinalRewardTemplate("🏆", "Prestazione forte", "Ottimo livello", "Hai gestito bene anche i distrattori. Ora lavora sulla costanza per arrivare al massimo."),
        FinalRewardTemplate("🔥", "Controllo alto", "Quasi eccellente", "Il livello è alto. Gli ultimi punti si recuperano controllando i dettagli più sottili."),
        FinalRewardTemplate("💎", "Risultato brillante", "Preparazione forte", "Hai una buona padronanza. Continua così e rendi automatico il ragionamento."),
        FinalRewardTemplate("🦾", "Modalità avanzata", "Molto buono", "Stai rispondendo con solidità. Ora il lavoro è rifinire, non ricostruire.")
    )

    private val excellentRewards = listOf(
        FinalRewardTemplate("🌟", "Eccellente", "Livello massimo", "Prestazione quasi perfetta. Hai superato anche i distrattori più insidiosi."),
        FinalRewardTemplate("👑", "Dominio del quiz", "Top performance", "Risultato altissimo: ragionamento, attenzione e memoria stanno lavorando insieme."),
        FinalRewardTemplate("🚀", "Prestazione da lancio", "Eccellenza", "Hai completato il test con grande controllo. Questo è il livello da mantenere."),
        FinalRewardTemplate("🏅", "Risultato elite", "Preparazione eccellente", "Hai dimostrato precisione anche nelle risposte più simili. Ottimo lavoro.")
    )

    fun createReward(score: Int, total: Int): FinalReward {
        val safeTotal = total.coerceAtLeast(1)
        val safeScore = score.coerceIn(0, safeTotal)
        val percent = ((safeScore.toDouble() / safeTotal.toDouble()) * 100).toInt()

        val templates = when {
            percent >= 95 -> excellentRewards
            percent >= 80 -> highRewards
            percent >= 60 -> goodRewards
            percent >= 40 -> mediumLowRewards
            else -> lowRewards
        }

        val scoreKey = "$safeScore/$safeTotal"
        val lastTitle = lastTitleByScore[scoreKey]
        val availableTemplates = templates.filter { it.title != lastTitle }.ifEmpty { templates }
        val selectedTemplate = availableTemplates.random(Random.Default)

        lastTitleByScore[scoreKey] = selectedTemplate.title

        return FinalReward(
            score = safeScore,
            total = safeTotal,
            percent = percent,
            emoji = selectedTemplate.emoji,
            title = selectedTemplate.title,
            badge = selectedTemplate.badge,
            message = selectedTemplate.message
        )
    }

    private data class FinalRewardTemplate(
        val emoji: String,
        val title: String,
        val badge: String,
        val message: String
    )
}
