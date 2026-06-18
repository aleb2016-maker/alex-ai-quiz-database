(function () {
  if (window.__alexAiItsEffectsInstalled) {
    return;
  }

  window.__alexAiItsEffectsInstalled = true;

  const rewards = {
    "10": [
      ["🚀", "Missione perfetta", "Hai chiuso il test con precisione totale. Questa è mentalità da progetto professionale."],
      ["🧠", "Prestazione eccellente", "Risposte pulite, ritmo alto e zero errori: ottimo segnale per un percorso AI ITS."],
      ["🏆", "Dominio completo", "Hai gestito il test come un sistema ben addestrato: dati chiari, decisioni corrette, risultato massimo."]
    ],
    "9": [
      ["⚡", "Quasi perfetto", "Ti manca pochissimo al massimo. La base è fortissima, ora serve solo rifinire i dettagli."],
      ["🤖", "Livello molto alto", "Hai dimostrato controllo e ragionamento. Un errore non rovina una prova così solida."],
      ["🌟", "Prestazione distinta", "Sei già in una zona alta: continua così e il 10 diventa naturale."]
    ],
    "8": [
      ["🔥", "Ottimo risultato", "Hai superato bene il test. Ora lavora sui dettagli che separano il buono dall'eccellente."],
      ["💡", "Ragionamento solido", "Il risultato mostra comprensione reale. Con un po' di revisione puoi salire ancora."],
      ["🧩", "Buona padronanza", "Le basi ci sono e si vedono. Ora punta a rendere più stabili anche le risposte difficili."]
    ],
    "7": [
      ["📈", "Buona prova", "Stai costruendo una base concreta. Rivedi gli errori e trasformali in punti forti."],
      ["🔧", "In crescita", "Il risultato è positivo. Ora serve consolidare gli argomenti dove hai esitato."],
      ["🛠️", "Base valida", "Hai materiale su cui costruire. La prossima prova può salire molto."]
    ],
    "6": [
      ["🧱", "Sufficiente", "Hai superato la soglia. Ora bisogna rendere più sicure le risposte e ridurre gli errori evitabili."],
      ["🧭", "Strada giusta", "La direzione è buona, ma serve più allenamento sui concetti chiave."],
      ["📚", "Da consolidare", "Il test è passato, ma il prossimo obiettivo è trasformare il minimo in sicurezza."]
    ],
    "low": [
      ["🔁", "Riprova strategica", "Non è una bocciatura: è una mappa degli argomenti da rinforzare."],
      ["🧪", "Test diagnostico", "Questo risultato ti dice dove intervenire. Riparti dagli errori e migliora a blocchi."],
      ["🧠", "Allenamento utile", "Ogni errore è un dato. Usalo per capire cosa rivedere prima del prossimo tentativo."]
    ]
  };

  const confettiColors = ["#4dd0ff", "#8b5cf6", "#22c55e", "#facc15", "#fb7185", "#ffffff"];

  function randomItem(items) {
    return items[Math.floor(Math.random() * items.length)];
  }

  function rewardBucket(score, total) {
    if (!total) {
      return "low";
    }

    const voto = Math.round((score / total) * 10);

    if (voto >= 10) return "10";
    if (voto >= 9) return "9";
    if (voto >= 8) return "8";
    if (voto >= 7) return "7";
    if (voto >= 6) return "6";
    return "low";
  }

  function shootConfetti() {
    const count = 46;

    for (let index = 0; index < count; index += 1) {
      const piece = document.createElement("span");
      piece.className = "alex-ai-confetti-piece";

      const spread = (Math.random() * 2 - 1) * Math.min(window.innerWidth * 0.64, 620);
      const height = -(Math.random() * 360 + 300);
      const rotation = (Math.random() * 920 - 460) + "deg";

      piece.style.left = (window.innerWidth / 2 + (Math.random() * 80 - 40)) + "px";
      piece.style.background = confettiColors[index % confettiColors.length];
      piece.style.setProperty("--alex-ai-x", spread + "px");
      piece.style.setProperty("--alex-ai-y", height + "px");
      piece.style.setProperty("--alex-ai-rot", rotation);
      piece.style.animationDelay = (Math.random() * 180) + "ms";

      document.body.appendChild(piece);

      setTimeout(function () {
        piece.remove();
      }, 2100);
    }
  }

  function extractScoreFromText(text) {
    const patterns = [
      /(?:Risultato|Punteggio|Score)[^\d]*(\d+)\s*\/\s*(\d+)/i,
      /(\d+)\s*\/\s*(\d+)\s*[-–—]\s*(?:eccellente|ottimo|distinto|buono|discreto|sufficiente|insufficiente)/i,
      /Hai totalizzato[^\d]*(\d+)\s*\/\s*(\d+)/i
    ];

    for (const pattern of patterns) {
      const match = text.match(pattern);

      if (match) {
        return {
          score: Number(match[1]),
          total: Number(match[2])
        };
      }
    }

    return null;
  }

  function rewardAlreadyShown(score, total) {
    const current = document.querySelector(".alex-ai-final-reward");

    if (!current) {
      return false;
    }

    return current.getAttribute("data-score") === score + "/" + total;
  }

  function renderReward(score, total) {
    if (rewardAlreadyShown(score, total)) {
      return;
    }

    document.querySelectorAll(".alex-ai-final-reward").forEach(function (node) {
      node.remove();
    });

    const bucket = rewardBucket(score, total);
    const reward = randomItem(rewards[bucket] || rewards.low);

    const card = document.createElement("section");
    card.className = "alex-ai-final-reward";
    card.setAttribute("data-score", score + "/" + total);

    card.innerHTML = [
      '<div class="alex-ai-final-drawing" aria-hidden="true">' + reward[0] + '</div>',
      '<div class="alex-ai-final-copy">',
      '<h3>' + reward[1] + '</h3>',
      '<p>' + reward[2] + '</p>',
      '<p class="alex-ai-final-score">Risultato: ' + score + '/' + total + '</p>',
      '</div>'
    ].join("");

    const target =
      document.querySelector("#result") ||
      document.querySelector(".result") ||
      document.querySelector(".results") ||
      document.querySelector(".quiz-result") ||
      document.querySelector("main") ||
      document.body;

    target.appendChild(card);
  }

  function scanForFinalReward() {
    const text = document.body ? document.body.innerText || "" : "";
    const score = extractScoreFromText(text);

    if (score && score.total > 0) {
      renderReward(score.score, score.total);
    }
  }

  function maybeConfettiFromClick(event) {
    const clicked =
      event.target.closest("button") ||
      event.target.closest(".option") ||
      event.target.closest(".answer") ||
      event.target.closest("[data-answer]");

    if (!clicked) {
      return;
    }

    setTimeout(function () {
      const classText = String(clicked.className || "").toLowerCase();
      const text = String(clicked.innerText || clicked.textContent || "").toLowerCase();

      const looksCorrect =
        classText.includes("correct") ||
        classText.includes("corretta") ||
        classText.includes("success") ||
        text.includes("corretto");

      const looksWrong =
        classText.includes("wrong") ||
        classText.includes("errore") ||
        classText.includes("sbagli") ||
        text.includes("sbagliato");

      if (looksCorrect && !looksWrong) {
        shootConfetti();
      }

      scanForFinalReward();
    }, 180);
  }

  document.addEventListener("click", maybeConfettiFromClick, true);

  const observer = new MutationObserver(function () {
    scanForFinalReward();
  });

  function start() {
    if (!document.body) {
      return;
    }

    observer.observe(document.body, {
      childList: true,
      subtree: true,
      characterData: true
    });

    scanForFinalReward();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", start);
  } else {
    start();
  }

  window.alexAiShootConfetti = shootConfetti;
  window.alexAiShowFinalReward = renderReward;
})();
