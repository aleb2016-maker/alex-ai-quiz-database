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
