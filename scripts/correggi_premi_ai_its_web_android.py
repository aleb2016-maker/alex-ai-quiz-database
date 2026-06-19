from pathlib import Path
import zipfile
import tempfile
import shutil
import re
import datetime

ROOT = Path.cwd()
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
changed_files = []
warnings = []


def backup_file(path: Path):
    if path.exists():
        backup = path.with_suffix(path.suffix + f".bak_{STAMP}")
        shutil.copy2(path, backup)


def write_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    old = path.read_text(encoding="utf-8") if path.exists() else None

    if old != content:
        backup_file(path)
        path.write_text(content, encoding="utf-8")
        changed_files.append(str(path.relative_to(ROOT)))


def copy_file(src: Path, dst: Path):
    dst.parent.mkdir(parents=True, exist_ok=True)
    old = dst.read_bytes() if dst.exists() else None
    new = src.read_bytes()

    if old != new:
        backup_file(dst)
        dst.write_bytes(new)
        changed_files.append(str(dst.relative_to(ROOT)))


AI_EFFECTS_JS = r"""
(() => {
  "use strict";

  const CARD_SELECTOR = "[data-ai-its-final-reward], .ai-its-final-reward-card";
  const CONFETTI_STAGE_CLASS = "ai-its-confetti-stage";

  const state = {
    observerPausedUntil: 0,
    lastRenderedScoreKey: null
  };

  const rewardGroups = [
    {
      min: 0,
      max: 39,
      items: [
        {
          emoji: "🧭",
          title: "Allenamento utile",
          badge: "Base da rinforzare",
          message: "Questo risultato serve a capire dove lavorare. Ora il passo importante è correggere gli errori e riprovare meglio."
        },
        {
          emoji: "🔧",
          title: "Ripartenza intelligente",
          badge: "Correzione mirata",
          message: "Hai individuato una zona debole: è una buona notizia, perché adesso sai esattamente dove migliorare."
        },
        {
          emoji: "📌",
          title: "Primo passo utile",
          badge: "Fondamenta",
          message: "Il test non è perso: ti ha mostrato quali concetti vanno ricostruiti con più calma."
        },
        {
          emoji: "🧱",
          title: "Base in costruzione",
          badge: "Allenamento attivo",
          message: "Ogni errore corretto diventa una domanda più facile la prossima volta."
        },
        {
          emoji: "💡",
          title: "Errore trasformabile",
          badge: "Studio pratico",
          message: "Il punteggio è basso, ma il valore è alto se usi le spiegazioni per capire il motivo degli errori."
        },
        {
          emoji: "🚦",
          title: "Segnale chiaro",
          badge: "Riprova guidata",
          message: "Il quiz ti sta dicendo quali argomenti rallentano il percorso. Riparti da quelli."
        }
      ]
    },
    {
      min: 40,
      max: 59,
      items: [
        {
          emoji: "⚙️",
          title: "Meccanismo avviato",
          badge: "In crescita",
          message: "Hai già alcuni punti solidi. Ora devi trasformare le risposte incerte in risposte sicure."
        },
        {
          emoji: "🧩",
          title: "Pezzi da collegare",
          badge: "Quasi sufficiente",
          message: "La base c’è, ma alcuni collegamenti logici vanno resi più precisi."
        },
        {
          emoji: "📈",
          title: "Progressione visibile",
          badge: "Miglioramento",
          message: "Non sei lontano: con una revisione mirata puoi salire rapidamente."
        },
        {
          emoji: "🎯",
          title: "Obiettivo vicino",
          badge: "Precisione",
          message: "Ora serve attenzione ai dettagli: spesso la differenza è in una parola o in una condizione."
        }
      ]
    },
    {
      min: 60,
      max: 79,
      items: [
        {
          emoji: "✅",
          title: "Risultato solido",
          badge: "Buona base",
          message: "Hai superato la soglia utile. Ora punta a ridurre gli errori causati da fretta o distrattori simili."
        },
        {
          emoji: "🏗️",
          title: "Struttura buona",
          badge: "Consolidamento",
          message: "La preparazione c’è. Il prossimo salto arriva distinguendo meglio le opzioni molto vicine."
        },
        {
          emoji: "🧠",
          title: "Ragionamento attivo",
          badge: "Buon controllo",
          message: "Stai ragionando bene. Ora allena la parte più difficile: scegliere tra risposte quasi uguali."
        },
        {
          emoji: "🚀",
          title: "Salita iniziata",
          badge: "Livello buono",
          message: "Il risultato è positivo. Con qualche correzione mirata puoi entrare nella fascia alta."
        }
      ]
    },
    {
      min: 80,
      max: 94,
      items: [
        {
          emoji: "🏆",
          title: "Prestazione forte",
          badge: "Ottimo livello",
          message: "Hai gestito bene anche i distrattori. Ora lavora sulla costanza per arrivare al massimo."
        },
        {
          emoji: "🔥",
          title: "Controllo alto",
          badge: "Quasi eccellente",
          message: "Il livello è alto. Gli ultimi punti si recuperano controllando i dettagli più sottili."
        },
        {
          emoji: "💎",
          title: "Risultato brillante",
          badge: "Preparazione forte",
          message: "Hai una buona padronanza. Continua così e rendi automatico il ragionamento."
        },
        {
          emoji: "🦾",
          title: "Modalità avanzata",
          badge: "Molto buono",
          message: "Stai rispondendo con solidità. Ora il lavoro è rifinire, non ricostruire."
        }
      ]
    },
    {
      min: 95,
      max: 100,
      items: [
        {
          emoji: "🌟",
          title: "Eccellente",
          badge: "Livello massimo",
          message: "Prestazione quasi perfetta. Hai superato anche i distrattori più insidiosi."
        },
        {
          emoji: "👑",
          title: "Dominio del quiz",
          badge: "Top performance",
          message: "Risultato altissimo: ragionamento, attenzione e memoria stanno lavorando insieme."
        },
        {
          emoji: "🚀",
          title: "Prestazione da lancio",
          badge: "Eccellenza",
          message: "Hai completato il test con grande controllo. Questo è il livello da mantenere."
        },
        {
          emoji: "🏅",
          title: "Risultato elite",
          badge: "Preparazione eccellente",
          message: "Hai dimostrato precisione anche nelle risposte più simili. Ottimo lavoro."
        }
      ]
    }
  ];

  function clampNumber(value, min, max) {
    const number = Number(value);
    if (!Number.isFinite(number)) return min;
    return Math.max(min, Math.min(max, number));
  }

  function removeFinalRewardCards() {
    document.querySelectorAll(CARD_SELECTOR).forEach((card) => card.remove());
    document.body.classList.remove("ai-its-has-final-reward");
    state.lastRenderedScoreKey = null;
  }

  function resetFinalRewardUi() {
    removeFinalRewardCards();
    state.observerPausedUntil = Date.now() + 900;
  }

  function findRewardGroup(score, total) {
    const percent = total > 0 ? Math.round((score / total) * 100) : 0;
    return rewardGroups.find((group) => percent >= group.min && percent <= group.max) || rewardGroups[0];
  }

  function pickReward(score, total) {
    const group = findRewardGroup(score, total);
    const scoreKey = `${score}/${total}`;
    const storageKey = `ai-its-last-final-reward-${scoreKey}`;
    const lastTitle = sessionStorage.getItem(storageKey);

    let available = group.items.filter((item) => item.title !== lastTitle);

    if (available.length === 0) {
      available = group.items;
    }

    const reward = available[Math.floor(Math.random() * available.length)];
    sessionStorage.setItem(storageKey, reward.title);

    return reward;
  }

  function findResultTarget() {
    const selectors = [
      "[data-result]",
      "[data-quiz-result]",
      "#result",
      "#results",
      ".result",
      ".results",
      ".quiz-result",
      ".final-result",
      ".score-card",
      "main",
      "#app",
      ".app"
    ];

    for (const selector of selectors) {
      const element = document.querySelector(selector);
      if (element) return element;
    }

    return document.body;
  }

  function renderFinalReward(rawScore, rawTotal, options = {}) {
    const score = clampNumber(rawScore, 0, 999);
    const total = clampNumber(rawTotal || 10, 1, 999);
    const scoreKey = `${score}/${total}`;

    const existing = document.querySelector(CARD_SELECTOR);

    if (existing && !options.force && existing.dataset.scoreKey === scoreKey) {
      return existing;
    }

    removeFinalRewardCards();

    const reward = pickReward(score, total);
    const percent = Math.round((score / total) * 100);

    const card = document.createElement("section");
    card.className = "ai-its-final-reward-card";
    card.dataset.aiItsFinalReward = "true";
    card.dataset.scoreKey = scoreKey;

    card.innerHTML = `
      <div class="ai-its-final-reward-glow"></div>
      <div class="ai-its-final-reward-content">
        <div class="ai-its-final-reward-emoji" aria-hidden="true">${reward.emoji}</div>
        <div class="ai-its-final-reward-text">
          <p class="ai-its-final-reward-kicker">Premio finale AI ITS</p>
          <h2>${reward.title}</h2>
          <p class="ai-its-final-reward-score">${score}/${total} · ${percent}% · ${reward.badge}</p>
          <p class="ai-its-final-reward-message">${reward.message}</p>
        </div>
      </div>
    `;

    const target = options.target || findResultTarget();
    target.appendChild(card);
    document.body.classList.add("ai-its-has-final-reward");
    state.lastRenderedScoreKey = scoreKey;

    return card;
  }

  function launchConfetti(options = {}) {
    const particleCount = clampNumber(options.count || 46, 12, 120);
    const existingStage = document.querySelector("." + CONFETTI_STAGE_CLASS);

    if (existingStage) {
      existingStage.remove();
    }

    const stage = document.createElement("div");
    stage.className = CONFETTI_STAGE_CLASS;
    stage.setAttribute("aria-hidden", "true");

    const colors = [
      "#8be9fd",
      "#50fa7b",
      "#ffb86c",
      "#ff79c6",
      "#bd93f9",
      "#f1fa8c",
      "#ffffff"
    ];

    for (let index = 0; index < particleCount; index += 1) {
      const piece = document.createElement("span");
      piece.className = "ai-its-confetti-piece";

      const startX = Math.round((Math.random() - 0.5) * window.innerWidth * 0.55);
      const endX = Math.round((Math.random() - 0.5) * window.innerWidth * 1.35);
      const rise = Math.round(window.innerHeight * (0.72 + Math.random() * 0.58));
      const size = Math.round(9 + Math.random() * 13);
      const duration = Math.round(1600 + Math.random() * 950);
      const delay = Math.round(Math.random() * 220);
      const spin = Math.round((Math.random() > 0.5 ? 1 : -1) * (260 + Math.random() * 620));

      piece.style.setProperty("--start-x", `${startX}px`);
      piece.style.setProperty("--end-x", `${endX}px`);
      piece.style.setProperty("--rise", `${rise}px`);
      piece.style.setProperty("--size", `${size}px`);
      piece.style.setProperty("--duration", `${duration}ms`);
      piece.style.setProperty("--delay", `${delay}ms`);
      piece.style.setProperty("--spin", `${spin}deg`);
      piece.style.background = colors[index % colors.length];

      stage.appendChild(piece);
    }

    document.body.appendChild(stage);

    window.setTimeout(() => {
      stage.remove();
    }, 3100);
  }

  function textLooksLikeFinalResult(text) {
    return /risultato|punteggio|finale|terminato|completato|corrette|esatte|hai totalizzato|quiz finito|fine quiz/i.test(text);
  }

  function detectFinalScore() {
    const elements = Array.from(document.querySelectorAll("body *"))
      .filter((element) => {
        const text = element.textContent || "";
        return text.length > 0 && text.length < 900;
      });

    const scorePattern = /(\d{1,3})\s*\/\s*(\d{1,3})/;

    for (const element of elements) {
      const text = element.textContent || "";
      const match = text.match(scorePattern);

      if (!match) continue;

      const ancestorText = [
        text,
        element.parentElement ? element.parentElement.textContent || "" : "",
        element.closest("section, article, div") ? element.closest("section, article, div").textContent || "" : ""
      ].join(" ");

      if (!textLooksLikeFinalResult(ancestorText)) continue;

      const score = Number(match[1]);
      const total = Number(match[2]);

      if (Number.isFinite(score) && Number.isFinite(total) && total > 0 && score <= total) {
        return { score, total };
      }
    }

    return null;
  }

  function attachResetListeners() {
    document.addEventListener("click", (event) => {
      const clickable = event.target.closest("button, a, [role='button'], input[type='button'], input[type='submit']");

      if (!clickable) return;

      const text = [
        clickable.textContent || "",
        clickable.value || "",
        clickable.getAttribute("aria-label") || "",
        clickable.id || "",
        clickable.className || ""
      ].join(" ");

      if (/nuovo|genera|inizia|ricomincia|riprova|restart|start|reset|cambia materia|crea quiz/i.test(text)) {
        resetFinalRewardUi();
      }
    }, true);
  }

  function attachResultObserver() {
    const observer = new MutationObserver(() => {
      if (Date.now() < state.observerPausedUntil) return;

      window.clearTimeout(attachResultObserver.timer);
      attachResultObserver.timer = window.setTimeout(() => {
        const detected = detectFinalScore();

        if (!detected) return;

        const existing = document.querySelector(CARD_SELECTOR);
        const scoreKey = `${detected.score}/${detected.total}`;

        if (existing && existing.dataset.scoreKey === scoreKey) {
          return;
        }

        renderFinalReward(detected.score, detected.total, { force: false });
      }, 180);
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });
  }

  function exposeApi() {
    const api = {
      resetFinalRewardUi,
      removeFinalRewardCards,
      renderFinalReward,
      showFinalReward: (score, total, options = {}) => renderFinalReward(score, total, { ...options, force: true }),
      launchConfetti
    };

    window.AiItsEffects = api;
    window.AIEffects = api;

    window.showAiItsFinalReward = api.showFinalReward;
    window.showAiFinalReward = api.showFinalReward;
    window.aiItsShowFinalReward = api.showFinalReward;
    window.mostraPremioFinaleAiIts = api.showFinalReward;
    window.mostraPremioFinaleAIITS = api.showFinalReward;
    window.mostraPremioFinale = api.showFinalReward;

    window.launchAiItsConfetti = launchConfetti;
    window.launchAiConfetti = launchConfetti;
    window.avviaCoriandoliAiIts = launchConfetti;
  }

  function boot() {
    exposeApi();
    attachResetListeners();
    attachResultObserver();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
""".strip() + "\n"


AI_EFFECTS_CSS = r"""
.ai-its-final-reward-card {
  position: relative;
  overflow: hidden;
  margin: 24px auto;
  max-width: 760px;
  border: 1px solid rgba(139, 233, 253, 0.35);
  border-radius: 28px;
  background:
    radial-gradient(circle at top left, rgba(139, 233, 253, 0.24), transparent 36%),
    radial-gradient(circle at bottom right, rgba(189, 147, 249, 0.24), transparent 38%),
    rgba(10, 16, 32, 0.92);
  box-shadow:
    0 18px 55px rgba(0, 0, 0, 0.45),
    0 0 42px rgba(139, 233, 253, 0.18);
  color: #ffffff;
  animation: aiRewardEnter 560ms cubic-bezier(.2, .9, .25, 1) both;
}

.ai-its-final-reward-glow {
  position: absolute;
  inset: -35%;
  background: conic-gradient(
    from 90deg,
    rgba(139, 233, 253, 0.0),
    rgba(139, 233, 253, 0.18),
    rgba(189, 147, 249, 0.18),
    rgba(255, 121, 198, 0.14),
    rgba(139, 233, 253, 0.0)
  );
  filter: blur(24px);
  opacity: 0.75;
  animation: aiRewardGlow 5.5s linear infinite;
}

.ai-its-final-reward-content {
  position: relative;
  display: flex;
  gap: 20px;
  align-items: center;
  padding: 26px;
}

.ai-its-final-reward-emoji {
  display: grid;
  place-items: center;
  flex: 0 0 auto;
  width: 78px;
  height: 78px;
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.11);
  border: 1px solid rgba(255, 255, 255, 0.20);
  font-size: 42px;
  box-shadow: inset 0 0 22px rgba(255, 255, 255, 0.08);
}

.ai-its-final-reward-text {
  position: relative;
  z-index: 1;
}

.ai-its-final-reward-kicker {
  margin: 0 0 6px;
  font-size: 0.76rem;
  letter-spacing: 0.13em;
  text-transform: uppercase;
  color: #8be9fd;
  font-weight: 800;
}

.ai-its-final-reward-card h2 {
  margin: 0;
  font-size: clamp(1.45rem, 4vw, 2.25rem);
  line-height: 1.05;
}

.ai-its-final-reward-score {
  margin: 10px 0 0;
  color: #f1fa8c;
  font-weight: 800;
}

.ai-its-final-reward-message {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.88);
  line-height: 1.5;
  font-weight: 500;
}

.ai-its-confetti-stage {
  position: fixed;
  inset: 0;
  z-index: 99999;
  pointer-events: none;
  overflow: hidden;
}

.ai-its-confetti-piece {
  position: absolute;
  left: 50%;
  bottom: -42px;
  width: var(--size);
  height: calc(var(--size) * 0.64);
  border-radius: 4px;
  opacity: 0;
  transform: translate(var(--start-x), 40px) rotate(0deg);
  animation: aiConfettiFromBottom var(--duration) cubic-bezier(.16, .78, .24, 1) var(--delay) forwards;
  box-shadow: 0 0 14px rgba(255, 255, 255, 0.28);
}

@keyframes aiConfettiFromBottom {
  0% {
    opacity: 0;
    transform: translate(var(--start-x), 42px) rotate(0deg) scale(0.88);
  }

  8% {
    opacity: 1;
  }

  76% {
    opacity: 1;
  }

  100% {
    opacity: 0;
    transform:
      translate(
        calc(var(--start-x) + var(--end-x)),
        calc(-1 * var(--rise))
      )
      rotate(var(--spin))
      scale(1.08);
  }
}

@keyframes aiRewardEnter {
  from {
    opacity: 0;
    transform: translateY(22px) scale(0.97);
  }

  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes aiRewardGlow {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .ai-its-final-reward-content {
    align-items: flex-start;
    padding: 22px;
  }

  .ai-its-final-reward-emoji {
    width: 58px;
    height: 58px;
    border-radius: 18px;
    font-size: 32px;
  }
}
""".strip() + "\n"


FINAL_REWARD_ENGINE_KT = r"""
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
""".strip() + "\n"


AI_ITS_REWARD_EFFECTS_KT = r"""
package com.alex.quizengine

import androidx.compose.animation.core.CubicBezierEasing
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import kotlin.math.roundToInt
import kotlin.random.Random

@Composable
fun AiItsFinalRewardCard(
    score: Int,
    total: Int,
    attemptKey: Any,
    modifier: Modifier = Modifier
) {
    val reward = remember(score, total, attemptKey) {
        FinalRewardEngine.createReward(score = score, total = total)
    }

    Box(
        modifier = modifier
            .widthIn(max = 720.dp)
            .clip(RoundedCornerShape(28.dp))
            .border(
                width = 1.dp,
                color = Color(0x668BE9FD),
                shape = RoundedCornerShape(28.dp)
            )
            .background(
                Brush.linearGradient(
                    colors = listOf(
                        Color(0xFF101827),
                        Color(0xFF151B34),
                        Color(0xFF231A3D)
                    )
                )
            )
            .padding(22.dp)
    ) {
        Row(
            horizontalArrangement = Arrangement.spacedBy(18.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Box(
                modifier = Modifier
                    .size(68.dp)
                    .clip(RoundedCornerShape(22.dp))
                    .background(Color.White.copy(alpha = 0.12f)),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    text = reward.emoji,
                    fontSize = 36.sp
                )
            }

            Column(
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Text(
                    text = "Premio finale AI ITS",
                    color = Color(0xFF8BE9FD),
                    fontSize = 12.sp,
                    fontWeight = FontWeight.ExtraBold
                )

                Text(
                    text = reward.title,
                    color = Color.White,
                    fontSize = 25.sp,
                    fontWeight = FontWeight.ExtraBold
                )

                Text(
                    text = "${reward.score}/${reward.total} · ${reward.percent}% · ${reward.badge}",
                    color = Color(0xFFF1FA8C),
                    fontSize = 15.sp,
                    fontWeight = FontWeight.Bold
                )

                Text(
                    text = reward.message,
                    color = Color.White.copy(alpha = 0.88f),
                    fontSize = 15.sp,
                    lineHeight = 21.sp
                )
            }
        }
    }
}

@Composable
fun AiItsConfettiOverlay(
    visible: Boolean,
    animationKey: Any,
    modifier: Modifier = Modifier,
    particleCount: Int = 46
) {
    val particles = remember(animationKey) {
        List(particleCount.coerceIn(12, 120)) { index ->
            ConfettiParticle(
                startXFactor = Random.nextFloat() * 0.56f - 0.28f,
                endXFactor = Random.nextFloat() * 1.35f - 0.675f,
                riseFactor = 0.72f + Random.nextFloat() * 0.58f,
                size = 7f + Random.nextFloat() * 10f,
                rotation = if (Random.nextBoolean()) 360f + Random.nextFloat() * 540f else -360f - Random.nextFloat() * 540f,
                delayFactor = Random.nextFloat() * 0.16f,
                color = confettiColors[index % confettiColors.size]
            )
        }
    }

    val progress by animateFloatAsState(
        targetValue = if (visible) 1f else 0f,
        animationSpec = tween(
            durationMillis = 1850,
            easing = CubicBezierEasing(0.16f, 0.78f, 0.24f, 1f)
        ),
        label = "aiItsConfettiProgress"
    )

    if (progress <= 0f) return

    Canvas(modifier = modifier.fillMaxSize()) {
        val centerX = size.width / 2f
        val baseY = size.height + 42f

        particles.forEach { particle ->
            val localProgress = ((progress - particle.delayFactor) / (1f - particle.delayFactor))
                .coerceIn(0f, 1f)

            if (localProgress <= 0f) return@forEach

            val x = centerX +
                (particle.startXFactor * size.width) +
                (particle.endXFactor * size.width * localProgress)

            val y = baseY - (particle.riseFactor * size.height * localProgress)

            val alpha = when {
                localProgress < 0.08f -> localProgress / 0.08f
                localProgress > 0.78f -> (1f - localProgress) / 0.22f
                else -> 1f
            }.coerceIn(0f, 1f)

            rotate(
                degrees = particle.rotation * localProgress,
                pivot = Offset(x, y)
            ) {
                drawRoundRect(
                    color = particle.color.copy(alpha = alpha),
                    topLeft = Offset(x, y),
                    size = androidx.compose.ui.geometry.Size(
                        width = particle.size * 1.35f,
                        height = particle.size
                    ),
                    cornerRadius = androidx.compose.ui.geometry.CornerRadius(4f, 4f)
                )
            }
        }
    }
}

private data class ConfettiParticle(
    val startXFactor: Float,
    val endXFactor: Float,
    val riseFactor: Float,
    val size: Float,
    val rotation: Float,
    val delayFactor: Float,
    val color: Color
)

private val confettiColors = listOf(
    Color(0xFF8BE9FD),
    Color(0xFF50FA7B),
    Color(0xFFFFB86C),
    Color(0xFFFF79C6),
    Color(0xFFBD93F9),
    Color(0xFFF1FA8C),
    Color(0xFFFFFFFF)
)
""".strip() + "\n"


def patch_html_file(path: Path):
    html = path.read_text(encoding="utf-8")

    if "ai-effects.css" not in html:
        if re.search(r"</head>", html, flags=re.IGNORECASE):
            html = re.sub(
                r"</head>",
                '  <link rel="stylesheet" href="ai-effects.css">\n</head>',
                html,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            html = '<link rel="stylesheet" href="ai-effects.css">\n' + html

    if "ai-effects.js" not in html:
        if re.search(r"</body>", html, flags=re.IGNORECASE):
            html = re.sub(
                r"</body>",
                '  <script src="ai-effects.js"></script>\n</body>',
                html,
                count=1,
                flags=re.IGNORECASE
            )
        else:
            html = html + '\n<script src="ai-effects.js"></script>\n'

    path.write_text(html, encoding="utf-8")


def patch_web_zip(zip_path: Path):
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)
        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(tmp)

        html_files = list(tmp.rglob("*.html"))

        if not html_files:
            warnings.append(f"Nessun HTML trovato dentro {zip_path}")
            return

        for html_file in html_files:
            (html_file.parent / "ai-effects.js").write_text(AI_EFFECTS_JS, encoding="utf-8")
            (html_file.parent / "ai-effects.css").write_text(AI_EFFECTS_CSS, encoding="utf-8")
            patch_html_file(html_file)

        backup_file(zip_path)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in tmp.rglob("*"):
                if file.is_file():
                    archive.write(file, file.relative_to(tmp))

        changed_files.append(str(zip_path.relative_to(ROOT)))


def find_quizengine_dir(base: Path) -> Path:
    for directory in base.rglob("quizengine"):
        if directory.is_dir():
            return directory

    directory = base / "quizengine"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


ANDROID_README_BLOCK = """
<!-- AI_ITS_EFFECTS_PATCH_START -->
<hr>
<h2>Premi finali e coriandoli AI ITS</h2>

<p>Questo pacchetto Android non è un APK già eseguibile: contiene database e file Kotlin da integrare nel progetto Android Studio.</p>

<p>Ora, oltre ai file Kotlin già presenti, devi copiare anche questi due file nella stessa cartella:</p>

<ul>
  <li><code>quizengine/FinalRewardEngine.kt</code></li>
  <li><code>quizengine/AiItsRewardEffects.kt</code></li>
</ul>

<p>Cartella Android consigliata:</p>

<pre>app/src/main/java/com/alex/quizengine/</pre>

<p><strong>Uso nel risultato finale Compose:</strong></p>

<pre>
val attemptKey = System.currentTimeMillis()

AiItsFinalRewardCard(
    score = punteggioFinale,
    total = numeroDomandeTotali,
    attemptKey = attemptKey
)

AiItsConfettiOverlay(
    visible = true,
    animationKey = attemptKey
)
</pre>

<p><strong>Nota importante:</strong> <code>attemptKey</code> deve cambiare a ogni nuovo test. In questo modo, anche con lo stesso punteggio, il premio finale può variare.</p>
<!-- AI_ITS_EFFECTS_PATCH_END -->
""".strip()


def patch_android_readme(readme_path: Path):
    if readme_path.exists():
        text = readme_path.read_text(encoding="utf-8", errors="ignore")
    else:
        text = "<!doctype html><html><body><h1>Pacchetto Android AI ITS</h1></body></html>"

    pattern = r"<!-- AI_ITS_EFFECTS_PATCH_START -->.*?<!-- AI_ITS_EFFECTS_PATCH_END -->"

    if re.search(pattern, text, flags=re.DOTALL):
        text = re.sub(pattern, ANDROID_README_BLOCK, text, flags=re.DOTALL)
    elif re.search(r"</body>", text, flags=re.IGNORECASE):
        text = re.sub(
            r"</body>",
            ANDROID_README_BLOCK + "\n</body>",
            text,
            count=1,
            flags=re.IGNORECASE
        )
    else:
        text = text + "\n\n" + ANDROID_README_BLOCK + "\n"

    readme_path.write_text(text, encoding="utf-8")


def patch_android_zip(zip_path: Path):
    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)

        with zipfile.ZipFile(zip_path, "r") as archive:
            archive.extractall(tmp)

        quizengine_dir = find_quizengine_dir(tmp)

        (quizengine_dir / "FinalRewardEngine.kt").write_text(FINAL_REWARD_ENGINE_KT, encoding="utf-8")
        (quizengine_dir / "AiItsRewardEffects.kt").write_text(AI_ITS_REWARD_EFFECTS_KT, encoding="utf-8")

        readme_candidates = list(tmp.rglob("*LEGGIMI*.html")) + list(tmp.rglob("*README*.html"))

        if readme_candidates:
            for readme in readme_candidates:
                patch_android_readme(readme)
        else:
            patch_android_readme(tmp / "1_LEGGIMI.html")

        backup_file(zip_path)

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as archive:
            for file in tmp.rglob("*"):
                if file.is_file():
                    archive.write(file, file.relative_to(tmp))

        changed_files.append(str(zip_path.relative_to(ROOT)))


def create_verifier_script():
    verifier = r'''
from pathlib import Path
import zipfile
import sys

root = Path.cwd()
errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

for path in [
    root / "runtime/web/ai-effects.js",
    root / "runtime/web/ai-effects.css",
    root / "demo-ai/ai-effects.js",
    root / "demo-ai/ai-effects.css",
    root / "runtime/android/FinalRewardEngine.kt",
    root / "runtime/android/AiItsRewardEffects.kt",
]:
    require(path.exists(), f"Manca {path}")

js = (root / "runtime/web/ai-effects.js").read_text(encoding="utf-8")
require("removeFinalRewardCards" in js, "Il JS non rimuove la vecchia card finale.")
require("sessionStorage" in js, "Il JS non evita la ripetizione dell'ultimo premio per lo stesso punteggio.")
require("showAiItsFinalReward" in js, "Manca API web showAiItsFinalReward.")
require("MutationObserver" in js, "Manca osservatore per rilevare risultato finale.")

web_zip = root / "downloads/pacchetto-web-ai-its-demo.zip"
if web_zip.exists():
    with zipfile.ZipFile(web_zip, "r") as archive:
        names = archive.namelist()
        require(any(name.endswith("ai-effects.js") for name in names), "Lo ZIP Web AI ITS non contiene ai-effects.js.")
        require(any(name.endswith("ai-effects.css") for name in names), "Lo ZIP Web AI ITS non contiene ai-effects.css.")
else:
    errors.append("Manca downloads/pacchetto-web-ai-its-demo.zip")

android_zip = root / "downloads/pacchetto-android-ai-its-finale-semplice.zip"
if android_zip.exists():
    with zipfile.ZipFile(android_zip, "r") as archive:
        names = archive.namelist()
        require(any(name.endswith("quizengine/FinalRewardEngine.kt") for name in names), "Lo ZIP Android non contiene quizengine/FinalRewardEngine.kt.")
        require(any(name.endswith("quizengine/AiItsRewardEffects.kt") for name in names), "Lo ZIP Android non contiene quizengine/AiItsRewardEffects.kt.")
        require(any("LEGGIMI" in name.upper() for name in names), "Lo ZIP Android non contiene il LEGGIMI.")
else:
    errors.append("Manca downloads/pacchetto-android-ai-its-finale-semplice.zip")

if errors:
    print("❌ Verifica fallita:")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("✅ Verifica premi/coriandoli AI ITS superata.")
'''
    write_text(ROOT / "scripts/verifica_premi_ai_its_v2.py", verifier.strip() + "\n")


# 1. Runtime Web
write_text(ROOT / "runtime/web/ai-effects.js", AI_EFFECTS_JS)
write_text(ROOT / "runtime/web/ai-effects.css", AI_EFFECTS_CSS)

# 2. Demo AI online
copy_file(ROOT / "runtime/web/ai-effects.js", ROOT / "demo-ai/ai-effects.js")
copy_file(ROOT / "runtime/web/ai-effects.css", ROOT / "demo-ai/ai-effects.css")

demo_index = ROOT / "demo-ai/index.html"
if demo_index.exists():
    backup_file(demo_index)
    patch_html_file(demo_index)
    changed_files.append(str(demo_index.relative_to(ROOT)))
else:
    warnings.append("Non trovato demo-ai/index.html")

# 3. Android runtime source
write_text(ROOT / "runtime/android/FinalRewardEngine.kt", FINAL_REWARD_ENGINE_KT)
write_text(ROOT / "runtime/android/AiItsRewardEffects.kt", AI_ITS_REWARD_EFFECTS_KT)

# 4. Patch ZIP Web AI ITS
web_zip = ROOT / "downloads/pacchetto-web-ai-its-demo.zip"
if web_zip.exists():
    patch_web_zip(web_zip)
else:
    warnings.append("Non trovato downloads/pacchetto-web-ai-its-demo.zip")

# 5. Patch ZIP Android AI ITS
android_zip = ROOT / "downloads/pacchetto-android-ai-its-finale-semplice.zip"
if android_zip.exists():
    patch_android_zip(android_zip)
else:
    warnings.append("Non trovato downloads/pacchetto-android-ai-its-finale-semplice.zip")

# 6. Verifier
create_verifier_script()

report = [
    "# Correzione premi AI ITS Web/Android",
    "",
    "## Modifiche applicate",
    "",
    "- Web: la vecchia card finale viene rimossa quando parte un nuovo quiz.",
    "- Web: a fine quiz viene generato un nuovo premio anche se il punteggio è identico.",
    "- Web: il premio evita di ripetere subito lo stesso titolo per lo stesso punteggio.",
    "- Web: coriandoli più ampi, fluidi e generati dal basso.",
    "- Demo AI: aggiornati `demo-ai/ai-effects.js` e `demo-ai/ai-effects.css`.",
    "- ZIP Web AI ITS: aggiornati `ai-effects.js`, `ai-effects.css` e riferimenti HTML.",
    "- Android: aggiunti `FinalRewardEngine.kt` e `AiItsRewardEffects.kt` dentro `quizengine/` nello ZIP.",
    "- Android: aggiornato il LEGGIMI con istruzioni reali di integrazione Compose.",
    "",
    "## File modificati",
    ""
]

if changed_files:
    for file in sorted(set(changed_files)):
        report.append(f"- `{file}`")
else:
    report.append("- Nessun file modificato.")

if warnings:
    report.extend(["", "## Avvisi", ""])
    for warning in warnings:
        report.append(f"- {warning}")

report_path = REPORTS / "correzione_premi_ai_its_web_android.md"
report_path.write_text("\n".join(report) + "\n", encoding="utf-8")

print("✅ Correzione completata.")
print(f"Report: {report_path}")
if warnings:
    print("⚠️ Avvisi:")
    for warning in warnings:
        print("-", warning)
