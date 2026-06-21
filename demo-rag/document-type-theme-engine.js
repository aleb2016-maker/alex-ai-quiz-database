/* RAG_DOCUMENT_TYPE_THEME_ENGINE */

(function () {
  if (window.__documentTypeThemeEngineInstalled) return;
  window.__documentTypeThemeEngineInstalled = true;

  const DOCUMENT_THEMES = {
    curriculum: {
      label: "Curriculum",
      palette: ["#6b1d55", "#d63384", "#ff7aa2"]
    },
    storia: {
      label: "Storia",
      palette: ["#312e81", "#7c3aed", "#facc15"]
    },
    poesia: {
      label: "Poesia",
      palette: ["#4c1d95", "#a855f7", "#f0abfc"]
    },
    aziendale: {
      label: "Documento aziendale",
      palette: ["#0f172a", "#2563eb", "#38bdf8"]
    },
    test: {
      label: "Test / quiz",
      palette: ["#7c2d12", "#ea580c", "#fdba74"]
    },
    formazione: {
      label: "Materiale formativo",
      palette: ["#064e3b", "#059669", "#6ee7b7"]
    },
    generico: {
      label: "Documento",
      palette: ["#1e1b4b", "#7c3aed", "#22d3ee"]
    }
  };

  function docNorm(text) {
    return String(text || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/[^a-z0-9+#.\s]+/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function countHits(text, words) {
    const normalized = docNorm(text);
    return words.reduce((total, word) => {
      return total + (normalized.includes(docNorm(word)) ? 1 : 0);
    }, 0);
  }

  function detectDocumentType(text) {
    const scores = {
      curriculum: countHits(text, [
        "curriculum", "vitae", "profilo", "competenze",
        "esperienza lavorativa", "diploma", "formazione",
        "addetto", "mansione", "contatti"
      ]),
      storia: countHits(text, [
        "storia", "racconto", "personaggio", "personaggi",
        "protagonista", "trama", "luogo", "avventura",
        "capitolo", "dialogo", "finale", "c era una volta"
      ]),
      poesia: countHits(text, [
        "poesia", "verso", "versi", "strofa", "rima",
        "metafora", "emozione", "poeta", "lirica",
        "immagine poetica"
      ]),
      aziendale: countHits(text, [
        "azienda", "aziendale", "procedura", "processo",
        "policy", "sicurezza", "rischio", "responsabile",
        "ruolo", "report", "controllo", "kpi"
      ]),
      test: countHits(text, [
        "test", "quiz", "domanda", "risposta", "opzione",
        "opzioni", "corretta", "punteggio", "verifica",
        "esercizio", "scelta multipla"
      ]),
      formazione: countHits(text, [
        "lezione", "corso", "modulo", "obiettivo didattico",
        "materiale formativo", "spiegazione", "esempio",
        "verifica", "apprendimento", "studente"
      ])
    };

    const best = Object.entries(scores).sort((a, b) => b[1] - a[1])[0];

    if (!best || best[1] <= 0) {
      return "generico";
    }

    return best[0];
  }

  function themeForDocument(text) {
    const type = detectDocumentType(text);
    return {
      type,
      theme: DOCUMENT_THEMES[type] || DOCUMENT_THEMES.generico
    };
  }

  window.DOCUMENT_THEMES = DOCUMENT_THEMES;
  window.detectDocumentType = detectDocumentType;
  window.themeForDocument = themeForDocument;
})();

/* RAG_DOCUMENT_TYPE_CARD_GENERATOR */
(function () {
  if (window.__documentTypeCardGeneratorInstalled) return;
  window.__documentTypeCardGeneratorInstalled = true;

  function escDoc(text) {
    return String(text || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function cleanDocText(text) {
    return String(text || "")
      .replace(/\[Pagina\s*\d+\]/gi, "")
      .replace(/Curriculum\s+Vitae/gi, "")
      .replace(/Email\s+\S+/gi, "")
      .replace(/Telefono\s+[0-9\s+]+/gi, "")
      .replace(/Indirizzo\s+[^.]+/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function shortDocText(text, max = 330) {
    const cleaned = cleanDocText(text);
    if (cleaned.length <= max) return cleaned;
    return cleaned.slice(0, max).replace(/\s+\S*$/, "") + "...";
  }

  function usefulKeywordsByType(text, type) {
    const normalized = String(text || "").toLowerCase();

    const map = {
      curriculum: [
        "profilo professionale",
        "competenze trasversali",
        "competenze digitali",
        "esperienza lavorativa",
        "formazione",
        "progetti"
      ],
      storia: [
        "trama",
        "personaggi",
        "ambientazione",
        "evento",
        "conflitto",
        "finale"
      ],
      poesia: [
        "tema",
        "emozioni",
        "versi",
        "strofe",
        "immagini poetiche",
        "messaggio"
      ],
      aziendale: [
        "processo",
        "procedura",
        "ruoli",
        "responsabilità",
        "rischi",
        "azioni operative"
      ],
      test: [
        "domanda",
        "risposta",
        "opzioni",
        "spiegazione",
        "difficoltà",
        "ripasso"
      ],
      formazione: [
        "obiettivo",
        "concetto chiave",
        "esempio",
        "esercizio",
        "verifica",
        "riepilogo"
      ],
      generico: [
        "sintesi",
        "punti importanti",
        "concetti chiave",
        "domande",
        "azioni",
        "riepilogo"
      ]
    };

    const base = map[type] || map.generico;

    const found = base.filter(word => normalized.includes(word.split(" ")[0]));

    return [...new Set([...found, ...base])].slice(0, 12);
  }

  function buildCardsForDocumentType(text) {
    const detected = window.themeForDocument
      ? window.themeForDocument(text)
      : { type: "generico", theme: { label: "Documento", palette: ["#1e1b4b", "#7c3aed", "#22d3ee"] } };

    const type = detected.type;
    const theme = detected.theme;
    const cleaned = cleanDocText(text);
    const cards = [];

    function add(title, badge, visualKind, customUse) {
      cards.push({
        materia: type,
        documentType: type,
        themeType: type,
        visualKind,
        badge,
        concetto: badge,
        fronte: title,
        retro: shortDocText(cleaned),
        uso: customUse || "Usa questa scheda per studiare, ripassare o spiegare il documento."
      });
    }

    if (type === "curriculum") {
      add("Scheda: profilo professionale", "Profilo", "profile", "Usa questa scheda per presentarti meglio.");
      add("Scheda: competenze trasversali", "Competenze", "skills", "Usa questa scheda per preparare un colloquio.");
      add("Scheda: competenze digitali e AI", "AI / Digitale", "digital", "Usa questa scheda per valorizzare le competenze tecnologiche.");
      add("Scheda: progetti software", "Progetti", "project", "Usa questa scheda per raccontare cosa sai costruire.");
      add("Scheda: esperienza lavorativa", "Esperienza", "work", "Usa questa scheda per spiegare le esperienze pratiche.");
      add("Scheda: formazione e obiettivi", "Formazione", "study", "Usa questa scheda per spiegare il percorso formativo.");
    } else if (type === "storia") {
      add("Scheda: trama principale", "Trama", "story");
      add("Scheda: personaggi", "Personaggi", "characters");
      add("Scheda: ambientazione", "Luogo", "place");
      add("Scheda: problema o conflitto", "Conflitto", "conflict");
      add("Scheda: eventi importanti", "Eventi", "events");
      add("Scheda: finale e messaggio", "Finale", "ending");
    } else if (type === "poesia") {
      add("Scheda: tema della poesia", "Tema", "poetry");
      add("Scheda: emozioni", "Emozioni", "emotion");
      add("Scheda: immagini poetiche", "Immagini", "image");
      add("Scheda: parole chiave", "Parole", "words");
      add("Scheda: ritmo e versi", "Versi", "rhythm");
      add("Scheda: messaggio", "Messaggio", "meaning");
    } else if (type === "aziendale") {
      add("Scheda: obiettivo aziendale", "Obiettivo", "business");
      add("Scheda: processo", "Processo", "process");
      add("Scheda: ruoli e responsabilità", "Ruoli", "roles");
      add("Scheda: rischi e controlli", "Rischi", "risk");
      add("Scheda: azioni operative", "Azioni", "actions");
      add("Scheda: riepilogo manageriale", "Report", "report");
    } else if (type === "test") {
      add("Scheda: argomento del test", "Argomento", "test");
      add("Scheda: domanda", "Domanda", "question");
      add("Scheda: risposta corretta", "Risposta", "answer");
      add("Scheda: spiegazione", "Spiegazione", "explain");
      add("Scheda: difficoltà", "Difficoltà", "level");
      add("Scheda: ripasso", "Ripasso", "review");
    } else if (type === "formazione") {
      add("Scheda: obiettivo della lezione", "Obiettivo", "study");
      add("Scheda: concetto chiave", "Concetto", "concept");
      add("Scheda: esempio pratico", "Esempio", "example");
      add("Scheda: esercizio", "Esercizio", "exercise");
      add("Scheda: verifica", "Verifica", "check");
      add("Scheda: riepilogo", "Riepilogo", "summary");
    } else {
      add("Scheda: sintesi documento", "Sintesi", "document");
      add("Scheda: punti importanti", "Punti", "list");
      add("Scheda: concetti chiave", "Concetti", "concept");
      add("Scheda: domande utili", "Domande", "question");
      add("Scheda: azioni possibili", "Azioni", "actions");
      add("Scheda: riepilogo finale", "Riepilogo", "summary");
    }

    return {
      documentType: type,
      theme,
      keywords: usefulKeywordsByType(text, type),
      cards
    };
  }

  function themedIcon(card) {
    const kind = card.visualKind || "document";

    function svg(body) {
      return `<svg viewBox="0 0 96 96" aria-hidden="true" focusable="false" class="cv-inline-icon">${body}</svg>`;
    }

    if (kind === "profile") {
      return svg('<rect x="18" y="22" width="46" height="32" rx="10" fill="#f9a8d4"></rect><rect x="32" y="38" width="46" height="32" rx="10" fill="#f472b6"></rect><circle cx="42" cy="34" r="6" fill="#ffffff"></circle><path d="M31 50 c5 -10 18 -10 24 0" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round"></path>');
    }

    if (kind === "skills") {
      return svg('<rect x="18" y="22" width="48" height="34" rx="10" fill="#a78bfa"></rect><rect x="32" y="38" width="46" height="30" rx="10" fill="#7c3aed"></rect><path d="M38 53 l8 8 l18 -22" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"></path>');
    }

    if (kind === "digital" || kind === "project") {
      return svg('<rect x="20" y="24" width="52" height="38" rx="10" fill="#60a5fa"></rect><rect x="30" y="36" width="44" height="30" rx="10" fill="#2563eb"></rect><path d="M40 45 h22 M40 54 h14" stroke="#ffffff" stroke-width="5" stroke-linecap="round"></path>');
    }

    if (kind === "story" || kind === "characters" || kind === "events") {
      return svg('<path d="M24 24 h30 c8 0 14 6 14 14 v34 H34 c-6 0-10-4-10-10z" fill="#facc15"></path><path d="M34 34 h22 M34 44 h18 M34 54 h14" stroke="#312e81" stroke-width="4" stroke-linecap="round"></path>');
    }

    if (kind === "poetry" || kind === "emotion" || kind === "image") {
      return svg('<path d="M48 24 c18 12 22 28 0 48 c-22-20-18-36 0-48z" fill="#f0abfc"></path><path d="M38 48 h20 M42 58 h12" stroke="#4c1d95" stroke-width="4" stroke-linecap="round"></path>');
    }

    if (kind === "business" || kind === "process" || kind === "roles" || kind === "risk") {
      return svg('<rect x="24" y="28" width="48" height="38" rx="8" fill="#38bdf8"></rect><rect x="36" y="20" width="24" height="12" rx="4" fill="#ffffff"></rect><path d="M34 42 h28 M34 52 h20" stroke="#0f172a" stroke-width="5" stroke-linecap="round"></path>');
    }

    if (kind === "test" || kind === "question" || kind === "answer") {
      return svg('<rect x="24" y="22" width="48" height="52" rx="10" fill="#fdba74"></rect><circle cx="40" cy="38" r="5" fill="#7c2d12"></circle><path d="M50 37 h10 M36 54 h24" stroke="#7c2d12" stroke-width="5" stroke-linecap="round"></path>');
    }

    if (kind === "study" || kind === "concept" || kind === "exercise") {
      return svg('<path d="M48 24 l24 12 l-24 12 l-24 -12 z" fill="#6ee7b7"></path><path d="M34 47 v10 c0 8 28 8 28 0 v-10" fill="none" stroke="#ffffff" stroke-width="5"></path>');
    }

    return svg('<rect x="22" y="24" width="46" height="34" rx="10" fill="#93c5fd"></rect><rect x="34" y="38" width="42" height="30" rx="10" fill="#60a5fa"></rect><path d="M42 50 h20 M42 58 h12" stroke="#ffffff" stroke-width="5" stroke-linecap="round"></path>');
  }

  function renderThemedDocumentCard(card, index = 0) {
    const type = card.documentType || card.themeType || card.materia || "generico";
    const theme = window.DOCUMENT_THEMES?.[type] || window.DOCUMENT_THEMES?.generico || {
      label: "Documento",
      palette: ["#1e1b4b", "#7c3aed", "#22d3ee"]
    };

    const palette = theme.palette || ["#1e1b4b", "#7c3aed", "#22d3ee"];
    const primary = palette[0];
    const secondary = palette[1];
    const accent = palette[2];

    return `
      <article class="cv-card" style="--cv-primary:${primary};--cv-secondary:${secondary};--cv-accent:${accent};">
        <div class="cv-badge">${escDoc(card.badge || theme.label || "Documento")}</div>
        <div class="cv-icon" aria-hidden="true">${themedIcon(card)}</div>
        <h3>${escDoc(card.fronte || "Scheda documento")}</h3>
        <p>${escDoc(card.retro || "")}</p>
        <small>${escDoc(card.uso || "Usa questa scheda per studiare o ripassare il documento.")}</small>
      </article>
    `;
  }

  function renderDetectedType(result) {
    const box = document.getElementById("documentTypeBox");
    if (!box) return;

    box.innerHTML = `
      <div class="detected-type-card">
        <span>Tipo documento riconosciuto</span>
        <strong>${escDoc(result.theme.label)}</strong>
        <p>Colori, badge e disegni delle card vengono scelti in base a questo tipo.</p>
      </div>
    `;
  }

  function generateThemedCards() {
    const textArea = document.getElementById("cvText");
    const keywordsBox = document.getElementById("keywordsBox");
    const cardsBox = document.getElementById("cardsBox");
    const jsonBox = document.getElementById("jsonBox");

    const text = textArea ? textArea.value.trim() : "";

    if (!text) {
      if (cardsBox) {
        cardsBox.innerHTML = '<div class="answer-error">Prima incolla un documento o premi Carica esempio.</div>';
      }
      return;
    }

    const result = buildCardsForDocumentType(text);

    window.__cvCardsResult = result;

    renderDetectedType(result);

    if (keywordsBox) {
      keywordsBox.innerHTML = result.keywords.map(word => `<span>${escDoc(word)}</span>`).join("");
    }

    if (cardsBox) {
      cardsBox.innerHTML = result.cards.map((card, index) => renderThemedDocumentCard(card, index)).join("");
    }

    if (jsonBox) {
      jsonBox.textContent = JSON.stringify(result, null, 2);
    }

    return result;
  }

  window.buildCardsForDocumentType = buildCardsForDocumentType;
  window.renderThemedDocumentCard = renderThemedDocumentCard;
  window.generateThemedCards = generateThemedCards;
  window.renderCard = renderThemedDocumentCard;
  window.generate = generateThemedCards;

  try {
    renderCard = renderThemedDocumentCard;
    generate = generateThemedCards;
  } catch (error) {}
})();
