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
