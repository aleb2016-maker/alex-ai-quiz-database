/* NODE_BROWSER_COMPAT_FIX */
if (typeof window === "undefined") {
  globalThis.window = globalThis;
}

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



/* RAG_FAST_THEMED_CARDS_FIX */
(function () {
  if (window.__ragFastThemedCardsFixInstalled) return;
  window.__ragFastThemedCardsFixInstalled = true;

  function fastClean(text) {
    return String(text || "")
      .replace(/\[Pagina\s*\d+\]/gi, "")
      .replace(/Curriculum\s+Vitae/gi, "")
      .replace(/Email\s+\S+/gi, "")
      .replace(/Telefono\s+[0-9\s+]+/gi, "")
      .replace(/Indirizzo\s+[^.]+/gi, "")
      .replace(/\s+/g, " ")
      .trim();
  }

  function fastShort(text, max = 300) {
    const cleaned = fastClean(text);
    if (cleaned.length <= max) return cleaned;
    return cleaned.slice(0, max).replace(/\s+\S*$/, "") + "...";
  }

  function maxCardsForText(text) {
    const length = fastClean(text).length;

    if (length < 420) return 4;
    if (length < 900) return 5;
    return 6;
  }

  function hasFast(text, words) {
    const t = String(text || "").toLowerCase();
    return words.some(word => t.includes(String(word).toLowerCase()));
  }

  function variedPalette(type, index) {
    const palettes = {
      curriculum: [
        ["#6b1d55", "#d63384", "#ff7aa2"],
        ["#5b1f6e", "#8b5cf6", "#a78bfa"],
        ["#0f4c81", "#2563eb", "#60a5fa"],
        ["#14532d", "#16a34a", "#86efac"],
        ["#7a3b00", "#ea580c", "#fdba74"],
        ["#7c2d12", "#dc2626", "#fb7185"]
      ],
      storia: [
        ["#312e81", "#7c3aed", "#facc15"],
        ["#4c1d95", "#a855f7", "#f0abfc"],
        ["#78350f", "#d97706", "#fde68a"]
      ],
      poesia: [
        ["#4c1d95", "#a855f7", "#f0abfc"],
        ["#831843", "#db2777", "#f9a8d4"],
        ["#1e1b4b", "#6366f1", "#c4b5fd"]
      ],
      aziendale: [
        ["#0f172a", "#2563eb", "#38bdf8"],
        ["#164e63", "#0891b2", "#67e8f9"],
        ["#1e3a8a", "#3b82f6", "#93c5fd"]
      ],
      test: [
        ["#7c2d12", "#ea580c", "#fdba74"],
        ["#78350f", "#d97706", "#facc15"],
        ["#991b1b", "#ef4444", "#fca5a5"]
      ],
      formazione: [
        ["#064e3b", "#059669", "#6ee7b7"],
        ["#14532d", "#16a34a", "#86efac"],
        ["#1e3a8a", "#2563eb", "#93c5fd"]
      ],
      generico: [
        ["#1e1b4b", "#7c3aed", "#22d3ee"],
        ["#0f172a", "#2563eb", "#38bdf8"],
        ["#3f1235", "#be185d", "#fbbf24"]
      ]
    };

    const list = palettes[type] || palettes.generico;
    return list[index % list.length];
  }

  function buildCardsForDocumentTypeFast(text) {
    const detected = window.themeForDocument
      ? window.themeForDocument(text)
      : { type: "generico", theme: { label: "Documento", palette: ["#1e1b4b", "#7c3aed", "#22d3ee"] } };

    const type = detected.type;
    const theme = detected.theme;
    const cleaned = fastClean(text);
    const limit = maxCardsForText(cleaned);
    const cards = [];

    function add(title, badge, visualKind, words, customUse) {
      if (words && words.length && !hasFast(cleaned, words)) return;

      cards.push({
        materia: type,
        documentType: type,
        themeType: type,
        visualKind,
        badge,
        concetto: badge,
        fronte: title,
        retro: fastShort(cleaned),
        uso: customUse || "Usa questa scheda per studiare, ripassare o spiegare il documento."
      });
    }

    if (type === "curriculum") {
      add("Scheda: profilo professionale", "Profilo", "profile", ["profilo", "creativo", "adattabile"], "Usa questa scheda per presentarti meglio.");
      add("Scheda: competenze trasversali", "Competenze", "skills", ["competenze", "comunicazione", "pazienza", "lavoro di gruppo"], "Usa questa scheda per preparare un colloquio.");
      add("Scheda: competenze digitali e AI", "AI / Digitale", "digital", ["intelligenza artificiale", "ai", "prompt", "android", "kotlin", "python", "github"], "Usa questa scheda per valorizzare le competenze tecnologiche.");
      add("Scheda: progetti software", "Progetti", "project", ["progetti", "app", "software", "github", "database", "quiz"], "Usa questa scheda per raccontare cosa sai costruire.");
      add("Scheda: esperienza lavorativa", "Esperienza", "work", ["esperienza", "lavoro", "addetto", "azienda", "mansione"], "Usa questa scheda per spiegare le esperienze pratiche.");
      add("Scheda: formazione e obiettivi", "Formazione", "study", ["formazione", "diploma", "corso", "its", "obiettivo"], "Usa questa scheda per spiegare il percorso formativo.");
    } else if (type === "storia") {
      add("Scheda: trama principale", "Trama", "story", ["storia", "trama", "racconto"]);
      add("Scheda: personaggi", "Personaggi", "characters", ["personaggio", "personaggi", "protagonista"]);
      add("Scheda: ambientazione", "Luogo", "place", ["luogo", "ambientazione", "città", "bosco", "casa"]);
      add("Scheda: eventi importanti", "Eventi", "events", ["evento", "succede", "avventura"]);
      add("Scheda: finale e messaggio", "Finale", "ending", ["finale", "messaggio"]);
    } else if (type === "poesia") {
      add("Scheda: tema della poesia", "Tema", "poetry", ["tema", "poesia"]);
      add("Scheda: emozioni", "Emozioni", "emotion", ["emozione", "sentimento", "tristezza", "gioia"]);
      add("Scheda: immagini poetiche", "Immagini", "image", ["immagine", "metafora", "simbolo"]);
      add("Scheda: ritmo e versi", "Versi", "rhythm", ["verso", "versi", "strofa", "rima"]);
    } else if (type === "aziendale") {
      add("Scheda: obiettivo aziendale", "Obiettivo", "business", ["obiettivo", "azienda", "aziendale"]);
      add("Scheda: processo", "Processo", "process", ["processo", "procedura"]);
      add("Scheda: ruoli e responsabilità", "Ruoli", "roles", ["ruolo", "responsabile", "responsabilità"]);
      add("Scheda: rischi e controlli", "Rischi", "risk", ["rischio", "controllo", "sicurezza"]);
      add("Scheda: azioni operative", "Azioni", "actions", ["azione", "azioni", "operativo"]);
    } else if (type === "test") {
      add("Scheda: argomento del test", "Argomento", "test", ["test", "quiz"]);
      add("Scheda: domanda", "Domanda", "question", ["domanda"]);
      add("Scheda: risposta corretta", "Risposta", "answer", ["risposta", "corretta"]);
      add("Scheda: spiegazione", "Spiegazione", "explain", ["spiegazione"]);
    } else if (type === "formazione") {
      add("Scheda: obiettivo della lezione", "Obiettivo", "study", ["obiettivo", "lezione", "corso"]);
      add("Scheda: concetto chiave", "Concetto", "concept", ["concetto", "regola"]);
      add("Scheda: esempio pratico", "Esempio", "example", ["esempio"]);
      add("Scheda: verifica", "Verifica", "check", ["verifica", "esercizio"]);
      add("Scheda: riepilogo", "Riepilogo", "summary", ["riepilogo", "sintesi"]);
    } else {
      add("Scheda: sintesi documento", "Sintesi", "document", []);
      add("Scheda: punti importanti", "Punti", "list", []);
      add("Scheda: concetti chiave", "Concetti", "concept", []);
      add("Scheda: domande utili", "Domande", "question", []);
    }

    if (!cards.length) {
      cards.push({
        materia: type,
        documentType: type,
        themeType: type,
        visualKind: "document",
        badge: theme.label || "Documento",
        concetto: "Sintesi",
        fronte: "Scheda: sintesi documento",
        retro: fastShort(cleaned),
        uso: "Usa questa scheda per ripassare il documento."
      });
    }

    return {
      documentType: type,
      theme,
      keywords: window.extractUsefulKeywords ? window.extractUsefulKeywords(text, 10) : [],
      cards: cards.slice(0, limit)
    };
  }

  function renderThemedDocumentCardFast(card, index = 0) {
    const type = card.documentType || card.themeType || card.materia || "generico";
    const palette = variedPalette(type, index);
    const primary = palette[0];
    const secondary = palette[1];
    const accent = palette[2];

    const icon = window.themedIcon
      ? window.themedIcon(card, index)
      : (typeof themedIcon === "function" ? themedIcon(card, index) : "");

    return `
      <article class="cv-card" style="--cv-primary:${primary};--cv-secondary:${secondary};--cv-accent:${accent};">
        <div class="cv-badge">${String(card.badge || "Documento").replaceAll("<", "&lt;").replaceAll(">", "&gt;")}</div>
        <div class="cv-icon" aria-hidden="true">${icon}</div>
        <h3>${String(card.fronte || "Scheda documento").replaceAll("<", "&lt;").replaceAll(">", "&gt;")}</h3>
        <p>${String(card.retro || "").replaceAll("<", "&lt;").replaceAll(">", "&gt;")}</p>
        <small>${String(card.uso || "Usa questa scheda per studiare o ripassare.").replaceAll("<", "&lt;").replaceAll(">", "&gt;")}</small>
      </article>
    `;
  }

  function generateThemedCardsFast() {
    const textArea = document.getElementById("cvText");
    const keywordsBox = document.getElementById("keywordsBox");
    const cardsBox = document.getElementById("cardsBox");
    const jsonBox = document.getElementById("jsonBox");
    const typeBox = document.getElementById("documentTypeBox");

    const text = textArea ? textArea.value.trim() : "";

    if (!text) {
      if (cardsBox) cardsBox.innerHTML = '<div class="answer-error">Prima incolla un documento o premi Carica esempio.</div>';
      return;
    }

    const result = buildCardsForDocumentTypeFast(text);
    window.__cvCardsResult = result;

    if (typeBox) {
      typeBox.innerHTML = `
        <div class="detected-type-card">
          <span>Tipo documento riconosciuto</span>
          <strong>${result.theme.label}</strong>
          <p>Card generate: ${result.cards.length}. Il numero viene ridotto automaticamente sui documenti corti.</p>
        </div>
      `;
    }

    if (keywordsBox) {
      keywordsBox.innerHTML = "";
    }

    if (cardsBox) {
      cardsBox.innerHTML = result.cards.map((card, index) => renderThemedDocumentCardFast(card, index)).join("");
    }

    if (jsonBox) {
      jsonBox.textContent = JSON.stringify(result, null, 2);
    }

    return result;
  }

  window.buildCardsForDocumentType = buildCardsForDocumentTypeFast;
  window.renderThemedDocumentCard = renderThemedDocumentCardFast;
  window.renderCard = renderThemedDocumentCardFast;
  window.generateThemedCards = generateThemedCardsFast;
  window.generate = generateThemedCardsFast;

  try {
    buildCardsForDocumentType = buildCardsForDocumentTypeFast;
    renderThemedDocumentCard = renderThemedDocumentCardFast;
    renderCard = renderThemedDocumentCardFast;
    generateThemedCards = generateThemedCardsFast;
    generate = generateThemedCardsFast;
  } catch (error) {}
})();



/* NODE_EXPORT_COMPAT_FIX */
if (typeof module !== "undefined" && module.exports) {
  module.exports = {
    DOCUMENT_THEMES: globalThis.DOCUMENT_THEMES,
    detectDocumentType: globalThis.detectDocumentType,
    themeForDocument: globalThis.themeForDocument,
    buildCardsForDocumentType: globalThis.buildCardsForDocumentType,
    generateThemedCardPlan: globalThis.generateThemedCardPlan,
    generateThemedCards: globalThis.generateThemedCards,
    DocumentTypeThemeEngine: globalThis.DocumentTypeThemeEngine
  };
}



/* RAG_RICH_BRANCH_CARD_RENDERER_V1 */
(function () {
  if (window.__ragRichBranchCardRendererV1Installed) return;
  window.__ragRichBranchCardRendererV1Installed = true;

  const BRANCH_VISUALS = {
    curriculum_vitae: {
      defaultPalette: ["#7f1d5a", "#c026d3", "#fb7185"],
      branches: {
        profilo_personale: {
          badge: "Profilo",
          visual: "profile",
          palette: ["#6b1d55", "#d63384", "#ff7aa2"]
        },
        esperienza_lavorativa: {
          badge: "Esperienza",
          visual: "work",
          palette: ["#14532d", "#16a34a", "#86efac"]
        },
        formazione: {
          badge: "Formazione",
          visual: "study",
          palette: ["#7a3b00", "#ea580c", "#fdba74"]
        },
        competenze_tecniche: {
          badge: "Tecniche",
          visual: "code",
          palette: ["#0f4c81", "#2563eb", "#60a5fa"]
        },
        competenze_trasversali: {
          badge: "Soft skill",
          visual: "skills",
          palette: ["#5b1f6e", "#8b5cf6", "#a78bfa"]
        },
        progetti: {
          badge: "Progetti",
          visual: "project",
          palette: ["#155e75", "#0891b2", "#67e8f9"]
        },
        obiettivi_professionali: {
          badge: "Obiettivi",
          visual: "target",
          palette: ["#7c2d12", "#dc2626", "#fb7185"]
        },
        contatti: {
          badge: "Contatti",
          visual: "contact",
          palette: ["#374151", "#64748b", "#cbd5e1"]
        }
      }
    },

    documenti_personali: {
      defaultPalette: ["#0f766e", "#14b8a6", "#60a5fa"],
      branches: {
        presentazione_personale: {
          badge: "Persona",
          visual: "personal",
          palette: ["#0f766e", "#14b8a6", "#99f6e4"]
        },
        autobiografia: {
          badge: "Percorso",
          visual: "timeline",
          palette: ["#1e3a8a", "#3b82f6", "#93c5fd"]
        },
        diario_note: {
          badge: "Diario",
          visual: "notebook",
          palette: ["#713f12", "#ca8a04", "#fde68a"]
        },
        obiettivi_personali: {
          badge: "Obiettivi",
          visual: "target",
          palette: ["#7c2d12", "#ea580c", "#fdba74"]
        },
        interessi_e_passioni: {
          badge: "Passioni",
          visual: "heart",
          palette: ["#831843", "#db2777", "#f9a8d4"]
        }
      }
    },

    documenti_aziendali: {
      defaultPalette: ["#1e3a8a", "#2563eb", "#38bdf8"],
      branches: {
        report_analisi: {
          badge: "Report",
          visual: "chart",
          palette: ["#0f172a", "#2563eb", "#38bdf8"]
        },
        procedure: {
          badge: "Procedura",
          visual: "workflow",
          palette: ["#164e63", "#0891b2", "#67e8f9"]
        },
        regolamenti_policy: {
          badge: "Policy",
          visual: "shield",
          palette: ["#1e293b", "#475569", "#cbd5e1"]
        },
        sicurezza: {
          badge: "Sicurezza",
          visual: "lock",
          palette: ["#7f1d1d", "#dc2626", "#fca5a5"]
        },
        riunioni_team: {
          badge: "Team",
          visual: "team",
          palette: ["#312e81", "#6366f1", "#a5b4fc"]
        },
        piano_operativo: {
          badge: "Piano",
          visual: "roadmap",
          palette: ["#064e3b", "#059669", "#6ee7b7"]
        }
      }
    },

    storie: {
      defaultPalette: ["#92400e", "#f59e0b", "#f97316"],
      branches: {
        racconto_breve: {
          badge: "Racconto",
          visual: "book",
          palette: ["#78350f", "#d97706", "#fde68a"]
        },
        avventura: {
          badge: "Avventura",
          visual: "map",
          palette: ["#14532d", "#16a34a", "#86efac"]
        },
        favola: {
          badge: "Favola",
          visual: "castle",
          palette: ["#581c87", "#a855f7", "#e9d5ff"]
        },
        racconto_realistico: {
          badge: "Realistico",
          visual: "city",
          palette: ["#1e3a8a", "#3b82f6", "#bfdbfe"]
        },
        racconto_fantastico: {
          badge: "Fantasy",
          visual: "portal",
          palette: ["#4c1d95", "#7c3aed", "#c4b5fd"]
        }
      }
    },

    poesie: {
      defaultPalette: ["#6d28d9", "#8b5cf6", "#c084fc"],
      branches: {
        poesia_amore: {
          badge: "Amore",
          visual: "heart",
          palette: ["#831843", "#db2777", "#f9a8d4"]
        },
        poesia_riflessiva: {
          badge: "Riflessione",
          visual: "moon",
          palette: ["#1e1b4b", "#6366f1", "#c4b5fd"]
        },
        poesia_natura: {
          badge: "Natura",
          visual: "nature",
          palette: ["#14532d", "#22c55e", "#bbf7d0"]
        },
        poesia_malinconica: {
          badge: "Malinconia",
          visual: "rain",
          palette: ["#334155", "#64748b", "#cbd5e1"]
        },
        poesia_motivazionale: {
          badge: "Speranza",
          visual: "sunrise",
          palette: ["#7c2d12", "#f97316", "#fde68a"]
        }
      }
    },

    allenamento: {
      defaultPalette: ["#166534", "#22c55e", "#86efac"],
      branches: {
        allenamento_generale: {
          badge: "Allenamento",
          visual: "fitness",
          palette: ["#166534", "#22c55e", "#86efac"]
        },
        forza: {
          badge: "Forza",
          visual: "dumbbell",
          palette: ["#7f1d1d", "#dc2626", "#fca5a5"]
        },
        mobilita: {
          badge: "Mobilità",
          visual: "mobility",
          palette: ["#0f766e", "#14b8a6", "#99f6e4"]
        },
        camminata_cardio: {
          badge: "Camminata",
          visual: "walk",
          palette: ["#0f4c81", "#2563eb", "#60a5fa"]
        },
        respirazione: {
          badge: "Respiro",
          visual: "breath",
          palette: ["#312e81", "#6366f1", "#c4b5fd"]
        },
        stretching: {
          badge: "Stretching",
          visual: "stretch",
          palette: ["#7a3b00", "#ea580c", "#fdba74"]
        },
        benessere_over: {
          badge: "Benessere",
          visual: "wellness",
          palette: ["#064e3b", "#059669", "#6ee7b7"]
        }
      }
    },

    tempo_libero_progetti: {
      defaultPalette: ["#0f172a", "#7c3aed", "#38bdf8"],
      branches: {
        hobby_creativi: {
          badge: "Creatività",
          visual: "brush",
          palette: ["#7f1d5a", "#c026d3", "#f0abfc"]
        },
        viaggi: {
          badge: "Viaggi",
          visual: "travel",
          palette: ["#0f766e", "#14b8a6", "#99f6e4"]
        },
        lettura_cinema_musica: {
          badge: "Cultura",
          visual: "media",
          palette: ["#1e1b4b", "#6366f1", "#c4b5fd"]
        },
        sport_svago: {
          badge: "Sport",
          visual: "ball",
          palette: ["#166534", "#22c55e", "#86efac"]
        },
        fotografia: {
          badge: "Foto",
          visual: "camera",
          palette: ["#334155", "#64748b", "#e2e8f0"]
        },
        progetti_personali: {
          badge: "Idee",
          visual: "idea",
          palette: ["#7c2d12", "#f97316", "#fde68a"]
        }
      }
    }
  };

  function safeText(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function normalize(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .toLowerCase()
      .replace(/\s+/g, " ")
      .trim();
  }

  function makeSnippet(text, sentences) {
    const usable = Array.isArray(sentences) && sentences.length
      ? sentences.join(". ")
      : String(text || "");

    const cleaned = usable
      .replace(/\[Pagina\s*\d+\]/gi, "")
      .replace(/Curriculum\s+Vitae/gi, "")
      .replace(/\S+@\S+\.\S+/g, "")
      .replace(/Telefono\s+[0-9\s+]+/gi, "")
      .replace(/\s+/g, " ")
      .trim();

    if (cleaned.length <= 300) return cleaned;
    return cleaned.slice(0, 300).replace(/\s+\S*$/, "") + "...";
  }

  function svgWrap(body) {
    return `<svg viewBox="0 0 180 120" aria-hidden="true" focusable="false" class="cv-scene-svg">${body}</svg>`;
  }

  function richVisual(kind) {
    const k = kind || "document";

    if (k === "profile") {
      return svgWrap(`
        <rect x="22" y="18" width="76" height="58" rx="16" fill="rgba(255,255,255,.24)"/>
        <rect x="74" y="42" width="80" height="58" rx="18" fill="rgba(255,255,255,.16)"/>
        <circle cx="60" cy="43" r="12" fill="#fff"/>
        <path d="M38 66c9-20 35-20 44 0" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
        <path d="M96 62h34M96 77h44" stroke="#fff" stroke-width="7" stroke-linecap="round" opacity=".85"/>
      `);
    }

    if (k === "work") {
      return svgWrap(`
        <rect x="38" y="40" width="104" height="58" rx="14" fill="rgba(255,255,255,.20)"/>
        <rect x="72" y="26" width="36" height="18" rx="7" fill="#fff"/>
        <path d="M48 62h84M48 80h54" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
        <circle cx="128" cy="82" r="10" fill="#fff" opacity=".85"/>
      `);
    }

    if (k === "study") {
      return svgWrap(`
        <path d="M90 22l62 28-62 28-62-28z" fill="rgba(255,255,255,.28)"/>
        <path d="M54 68v18c0 18 72 18 72 0V68" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>
        <path d="M132 56v26" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
      `);
    }

    if (k === "code" || k === "project") {
      return svgWrap(`
        <rect x="24" y="24" width="132" height="78" rx="18" fill="rgba(255,255,255,.20)"/>
        <path d="M55 53l-20 16 20 16M125 53l20 16-20 16" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"/>
        <path d="M82 88l18-40" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
      `);
    }

    if (k === "skills") {
      return svgWrap(`
        <circle cx="90" cy="60" r="32" fill="rgba(255,255,255,.18)"/>
        <path d="M68 62l15 15 34-40" fill="none" stroke="#fff" stroke-width="11" stroke-linecap="round" stroke-linejoin="round"/>
        <circle cx="42" cy="34" r="8" fill="#fff"/><circle cx="138" cy="34" r="8" fill="#fff"/>
        <circle cx="42" cy="92" r="8" fill="#fff"/><circle cx="138" cy="92" r="8" fill="#fff"/>
      `);
    }

    if (k === "target") {
      return svgWrap(`
        <circle cx="82" cy="64" r="42" fill="none" stroke="rgba(255,255,255,.35)" stroke-width="10"/>
        <circle cx="82" cy="64" r="24" fill="none" stroke="#fff" stroke-width="8"/>
        <circle cx="82" cy="64" r="8" fill="#fff"/>
        <path d="M106 42l38-22M132 18h16v16" stroke="#fff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/>
      `);
    }

    if (k === "book") {
      return svgWrap(`
        <path d="M30 28h50c12 0 20 8 20 20v54H50c-12 0-20-8-20-20z" fill="rgba(255,255,255,.20)"/>
        <path d="M100 48c0-12 8-20 20-20h30v74h-50z" fill="rgba(255,255,255,.14)"/>
        <path d="M50 50h32M50 66h28M118 50h20M118 66h24" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
      `);
    }

    if (k === "map" || k === "travel") {
      return svgWrap(`
        <path d="M34 34l36-12 40 12 36-12v70l-36 12-40-12-36 12z" fill="rgba(255,255,255,.20)"/>
        <path d="M70 22v70M110 34v70" stroke="#fff" stroke-width="6" opacity=".9"/>
        <path d="M58 70c18-24 44 22 64-8" fill="none" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
      `);
    }

    if (k === "castle" || k === "portal") {
      return svgWrap(`
        <rect x="42" y="48" width="96" height="52" rx="8" fill="rgba(255,255,255,.18)"/>
        <rect x="54" y="28" width="22" height="34" rx="6" fill="#fff" opacity=".85"/>
        <rect x="104" y="28" width="22" height="34" rx="6" fill="#fff" opacity=".85"/>
        <path d="M74 100V76c0-18 32-18 32 0v24" fill="rgba(255,255,255,.36)"/>
      `);
    }

    if (k === "heart") {
      return svgWrap(`
        <path d="M90 98S36 66 36 36c0-15 18-25 32-10l22 22 22-22c14-15 32-5 32 10 0 30-54 62-54 62z" fill="rgba(255,255,255,.30)"/>
        <path d="M65 64h50" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
      `);
    }

    if (k === "moon" || k === "rain") {
      return svgWrap(`
        <path d="M100 22c-24 8-38 38-26 60 12 24 42 30 62 14-10 14-28 24-48 24-34 0-62-26-62-58 0-28 21-52 50-58 8-2 16-1 24 2z" fill="rgba(255,255,255,.28)"/>
        <path d="M120 42l10 10M42 86l8 12M58 96l8 12" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
      `);
    }

    if (k === "nature" || k === "sunrise") {
      return svgWrap(`
        <circle cx="122" cy="38" r="22" fill="rgba(255,255,255,.34)"/>
        <path d="M20 98c28-34 52-34 80 0 20-24 40-24 60 0z" fill="rgba(255,255,255,.24)"/>
        <path d="M42 92c18-26 38-26 58 0" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
      `);
    }

    if (k === "chart") {
      return svgWrap(`
        <rect x="28" y="26" width="124" height="76" rx="16" fill="rgba(255,255,255,.16)"/>
        <rect x="50" y="70" width="16" height="22" rx="4" fill="#fff"/>
        <rect x="82" y="54" width="16" height="38" rx="4" fill="#fff" opacity=".85"/>
        <rect x="114" y="40" width="16" height="52" rx="4" fill="#fff" opacity=".7"/>
        <path d="M46 44c22 10 38-10 56-2 14 6 22 0 34-12" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
      `);
    }

    if (k === "workflow" || k === "roadmap") {
      return svgWrap(`
        <rect x="24" y="28" width="38" height="30" rx="10" fill="#fff" opacity=".9"/>
        <rect x="72" y="66" width="38" height="30" rx="10" fill="#fff" opacity=".7"/>
        <rect x="120" y="28" width="38" height="30" rx="10" fill="#fff" opacity=".9"/>
        <path d="M62 43h26c10 0 10 38 20 38h12M110 81c10 0 10-38 20-38" fill="none" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
      `);
    }

    if (k === "shield" || k === "lock") {
      return svgWrap(`
        <path d="M90 18l52 20v30c0 34-24 50-52 60-28-10-52-26-52-60V38z" fill="rgba(255,255,255,.20)"/>
        <rect x="66" y="58" width="48" height="38" rx="10" fill="#fff" opacity=".9"/>
        <path d="M76 58V46c0-18 28-18 28 0v12" fill="none" stroke="#fff" stroke-width="8" stroke-linecap="round"/>
      `);
    }

    if (k === "fitness") {
      return svgWrap(`
        <circle cx="90" cy="26" r="14" fill="#fff" opacity=".95"/>
        <path d="M70 48c16-12 28-12 42 0M72 50l-20 22M108 50l22 22M80 72l-14 28M100 72l20 28" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>
        <path d="M36 88h108" stroke="rgba(255,255,255,.35)" stroke-width="8" stroke-linecap="round"/>
      `);
    }

    if (k === "dumbbell") {
      return svgWrap(`
        <path d="M45 60h90" stroke="#fff" stroke-width="12" stroke-linecap="round"/>
        <rect x="22" y="42" width="18" height="36" rx="6" fill="#fff" opacity=".9"/>
        <rect x="42" y="36" width="16" height="48" rx="6" fill="#fff" opacity=".65"/>
        <rect x="140" y="42" width="18" height="36" rx="6" fill="#fff" opacity=".9"/>
        <rect x="122" y="36" width="16" height="48" rx="6" fill="#fff" opacity=".65"/>
      `);
    }

    if (k === "breath") {
      return svgWrap(`
        <path d="M70 70c-26 0-34-34-10-46 18-9 30 9 30 28 0-19 12-37 30-28 24 12 16 46-10 46" fill="rgba(255,255,255,.18)"/>
        <path d="M44 88c26-16 66-16 92 0M54 100c20-10 52-10 72 0" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
      `);
    }

    if (k === "walk" || k === "stretch" || k === "mobility" || k === "wellness") {
      return svgWrap(`
        <circle cx="86" cy="24" r="12" fill="#fff"/>
        <path d="M82 40l-20 24M82 42l28 16M64 66l-18 34M82 64l28 34" fill="none" stroke="#fff" stroke-width="9" stroke-linecap="round"/>
        <path d="M120 98c14-18 24-18 38 0" fill="none" stroke="rgba(255,255,255,.45)" stroke-width="7" stroke-linecap="round"/>
      `);
    }

    if (k === "camera") {
      return svgWrap(`
        <rect x="36" y="38" width="108" height="62" rx="16" fill="rgba(255,255,255,.20)"/>
        <rect x="62" y="24" width="36" height="20" rx="8" fill="#fff" opacity=".8"/>
        <circle cx="90" cy="70" r="22" fill="none" stroke="#fff" stroke-width="9"/>
        <circle cx="126" cy="52" r="6" fill="#fff"/>
      `);
    }

    if (k === "media") {
      return svgWrap(`
        <rect x="30" y="32" width="50" height="62" rx="10" fill="rgba(255,255,255,.20)"/>
        <path d="M92 34l48 26-48 26z" fill="#fff" opacity=".85"/>
        <path d="M42 48h24M42 62h20M42 76h24" stroke="#fff" stroke-width="6" stroke-linecap="round"/>
      `);
    }

    if (k === "brush" || k === "idea") {
      return svgWrap(`
        <path d="M64 78c-20 4-28 14-30 28 16-2 26-10 30-30z" fill="#fff" opacity=".85"/>
        <path d="M72 70l50-50c8-8 22 6 14 14L86 84z" fill="rgba(255,255,255,.25)" stroke="#fff" stroke-width="6" stroke-linejoin="round"/>
        <circle cx="122" cy="30" r="8" fill="#fff"/>
      `);
    }

    return svgWrap(`
      <rect x="32" y="28" width="82" height="58" rx="16" fill="rgba(255,255,255,.20)"/>
      <rect x="66" y="50" width="72" height="46" rx="16" fill="rgba(255,255,255,.14)"/>
      <path d="M50 52h42M50 68h30M82 74h36" stroke="#fff" stroke-width="7" stroke-linecap="round"/>
    `);
  }

  function findSentencesForBranch(rawText, subbranch) {
    const sentences = String(rawText || "")
      .split(/[\n\.!?;:]+/)
      .map((sentence) => sentence.trim())
      .filter((sentence) => sentence.length >= 18);

    const keywords = Array.isArray(subbranch.keywords) ? subbranch.keywords : [];

    const matching = sentences.filter((sentence) => {
      const s = normalize(sentence);
      return keywords.some((keyword) => s.includes(normalize(keyword)));
    });

    return matching.length ? matching : sentences.slice(0, 2);
  }

  function buildRichThemedCards(rawText) {
    const engine = window.DocumentTypeThemeEngine;

    if (!engine || !engine.buildDocumentThemeProfile) {
      return null;
    }

    const profile = engine.buildDocumentThemeProfile(rawText);
    const branchConfig = BRANCH_VISUALS[profile.document_type_id] || BRANCH_VISUALS.documenti_personali;
    const cardLimit = profile.recommended_card_count || 3;

    const branches = Array.isArray(profile.detected_subbranches)
      ? profile.detected_subbranches.slice(0, cardLimit)
      : [];

    const cards = branches.map((branch, index) => {
      const branchVisual = branchConfig.branches[branch.id] || {};
      const sentences = findSentencesForBranch(rawText, branch);
      const palette = branchVisual.palette || branchConfig.defaultPalette || profile.theme_colors;

      return {
        materia: profile.document_type_id,
        documentType: profile.document_type_id,
        themeType: profile.document_type_id,
        branchId: branch.id,
        visualKind: branchVisual.visual || "document",
        badge: branchVisual.badge || branch.label || profile.badge_default,
        concetto: branch.label,
        fronte: `Scheda: ${String(branch.label || profile.document_type_label).toLowerCase()}`,
        retro: makeSnippet(rawText, sentences),
        uso: usageForDocumentType(profile.document_type_id),
        palette,
        imageHints: branch.image_hints || profile.image_hints || []
      };
    });

    if (!cards.length) {
      cards.push({
        materia: profile.document_type_id,
        documentType: profile.document_type_id,
        themeType: profile.document_type_id,
        branchId: "sintesi",
        visualKind: "document",
        badge: profile.badge_default,
        concetto: profile.document_type_label,
        fronte: `Scheda: ${profile.document_type_label.toLowerCase()}`,
        retro: makeSnippet(rawText, profile.useful_sentences || []),
        uso: usageForDocumentType(profile.document_type_id),
        palette: branchConfig.defaultPalette || profile.theme_colors,
        imageHints: profile.image_hints || []
      });
    }

    return {
      documentType: profile.document_type_id,
      theme: {
        label: profile.document_type_label,
        palette: profile.theme_colors,
        style: profile.theme_style
      },
      profile,
      keywords: profile.strong_keywords || [],
      cards
    };
  }

  function usageForDocumentType(type) {
    const map = {
      curriculum_vitae: "Usa questa scheda per presentarti meglio o preparare un colloquio.",
      documenti_personali: "Usa questa scheda per organizzare e chiarire le informazioni personali.",
      documenti_aziendali: "Usa questa scheda per spiegare processo, ruolo o decisione aziendale.",
      storie: "Usa questa scheda per ricordare trama, personaggi o messaggio della storia.",
      poesie: "Usa questa scheda per interpretare immagini, emozioni e significato della poesia.",
      allenamento: "Usa questa scheda come promemoria pratico del programma di allenamento.",
      tempo_libero_progetti: "Usa questa scheda per raccontare hobby, idee o progetti personali."
    };

    return map[type] || "Usa questa scheda per studiare, ripassare o spiegare il documento.";
  }

  function renderRichThemeCard(card, index = 0) {
    const palette = Array.isArray(card.palette) && card.palette.length >= 3
      ? card.palette
      : ["#1e1b4b", "#7c3aed", "#22d3ee"];

    const [primary, secondary, accent] = palette;
    const visual = richVisual(card.visualKind);

    return `
      <article class="cv-card rich-theme-card" style="--cv-primary:${primary};--cv-secondary:${secondary};--cv-accent:${accent};">
        <div class="cv-badge">${safeText(card.badge || "Documento")}</div>
        <div class="cv-hero-visual" aria-hidden="true">${visual}</div>
        <h3>${safeText(card.fronte || "Scheda documento")}</h3>
        <p>${safeText(card.retro || "")}</p>
        <small>${safeText(card.uso || "Usa questa scheda per ripassare il documento.")}</small>
      </article>
    `;
  }

  function renderThemeProfileBox(result) {
    const box = document.getElementById("documentTypeBox");
    if (!box || !result || !result.profile) return;

    const subbranches = (result.profile.detected_subbranches || [])
      .map((branch) => branch.label)
      .slice(0, 4)
      .join(", ");

    box.innerHTML = `
      <div class="detected-type-card">
        <span>Tipo documento riconosciuto</span>
        <strong>${safeText(result.theme.label)}</strong>
        <p>Sotto-rami: ${safeText(subbranches || "sintesi generale")}.</p>
        <p>Card generate: ${result.cards.length}. Il numero cambia in base alla quantità di testo utile.</p>
      </div>
    `;
  }

  function generateRichThemeCards() {
    const textArea = document.getElementById("cvText");
    const keywordsBox = document.getElementById("keywordsBox");
    const cardsBox = document.getElementById("cardsBox");
    const jsonBox = document.getElementById("jsonBox");

    const rawText = textArea ? textArea.value.trim() : "";

    if (!rawText) {
      if (cardsBox) {
        cardsBox.innerHTML = '<div class="answer-error">Prima carica o incolla un documento.</div>';
      }
      return;
    }

    const result = buildRichThemedCards(rawText);

    if (!result) {
      if (cardsBox) {
        cardsBox.innerHTML = '<div class="answer-error">Motore temi documento non disponibile.</div>';
      }
      return;
    }

    window.__cvCardsResult = result;

    renderThemeProfileBox(result);

    if (keywordsBox) {
      keywordsBox.innerHTML = (result.keywords || [])
        .slice(0, 12)
        .map((keyword) => `<span>${safeText(keyword)}</span>`)
        .join("");
    }

    if (cardsBox) {
      cardsBox.innerHTML = result.cards
        .map((card, index) => renderRichThemeCard(card, index))
        .join("");
    }

    if (jsonBox) {
      jsonBox.textContent = JSON.stringify(result, null, 2);
    }

    return result;
  }

  window.BRANCH_VISUALS = BRANCH_VISUALS;
  window.buildRichThemedCards = buildRichThemedCards;
  window.renderRichThemeCard = renderRichThemeCard;
  window.generateRichThemeCards = generateRichThemeCards;

  window.renderCard = renderRichThemeCard;
  window.generate = generateRichThemeCards;

  try {
    renderCard = renderRichThemeCard;
    generate = generateRichThemeCards;
  } catch (error) {}
})();
