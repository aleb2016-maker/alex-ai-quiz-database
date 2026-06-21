/* Curriculum Card Engine - pagina test separata */

const CV_STOPWORDS = new Set([
  "alessandro", "barbarossa", "curriculum", "vitae", "pagina",
  "presso", "addetto", "telefono", "email", "indirizzo",
  "nascita", "nazionalita", "italiana", "roma", "contatti",
  "esperienza", "lavorativa", "profilo", "competenze",
  "della", "delle", "degli", "dello", "alla", "alle",
  "con", "per", "nel", "nella", "sono", "come", "anche",
  "dal", "del", "dei", "una", "uno", "che", "gli", "le",
  "il", "lo", "la", "di", "a", "e", "o", "in"
]);

const CV_THEMES = {
  curriculum: {
    badge: "Curriculum",
    palette: ["#3f1235", "#be185d", "#fbbf24"],
    icon: "badge"
  },
  digitale: {
    badge: "Digitale / AI",
    palette: ["#1e1b4b", "#8b5cf6", "#22d3ee"],
    icon: "chip"
  },
  informatica: {
    badge: "Progetti software",
    palette: ["#0b3b66", "#38bdf8", "#1e293b"],
    icon: "code"
  },
  lavoro: {
    badge: "Esperienza",
    palette: ["#422006", "#f97316", "#fde68a"],
    icon: "work"
  }
};

function normalizeCv(text) {
  return String(text || "")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .toLowerCase()
    .replace(/[^a-z0-9+#.\s]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function cleanCvText(text) {
  return String(text || "")
    .replace(/\[Pagina\s*\d+\]/gi, "")
    .replace(/Curriculum\s+Vitae/gi, "")
    .replace(/Alessandro\s+Barbarossa/gi, "")
    .replace(/Email\s+\S+/gi, "")
    .replace(/Telefono\s+[0-9\s+]+/gi, "")
    .replace(/Indirizzo\s+[^.]+/gi, "")
    .replace(/DATA E LUOGO DI NASCITA[^.]+/gi, "")
    .replace(/NAZIONALITA'?[^.]+/gi, "")
    .replace(/\s+/g, " ")
    .trim();
}

function hasAny(text, words) {
  const normalized = normalizeCv(text);
  return words.some(word => normalized.includes(normalizeCv(word)));
}

function extractUsefulKeywords(text, limit = 24) {
  const normalized = normalizeCv(text);

  const priority = [
    "intelligenza artificiale", "ai", "prompt", "android", "kotlin",
    "python", "javascript", "html", "css", "github", "database",
    "quiz", "app", "software", "automazioni", "creativita",
    "comunicazione", "problem solving", "lavoro di gruppo",
    "sicurezza informatica", "full stack", "frontend", "backend"
  ];

  const foundPriority = priority.filter(word => normalized.includes(normalizeCv(word)));

  const words = normalized
    .split(/\s+/)
    .filter(word => word.length >= 4)
    .filter(word => !CV_STOPWORDS.has(word))
    .filter(word => !/^\d+$/.test(word));

  const counts = new Map();

  for (const word of words) {
    counts.set(word, (counts.get(word) || 0) + 1);
  }

  const frequent = [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .map(([word]) => word)
    .filter(word => !foundPriority.includes(word));

  return [...foundPriority, ...frequent].slice(0, limit);
}

function shortText(text, max = 330) {
  const cleaned = cleanCvText(text);
  if (cleaned.length <= max) return cleaned;
  return cleaned.slice(0, max).replace(/\s+\S*$/, "") + "...";
}

function buildCurriculumCards(text) {
  const clean = cleanCvText(text);
  const cards = [];

  function addCard({title, concept, theme, conditionWords, body}) {
    if (conditionWords && !hasAny(clean, conditionWords)) return;

    cards.push({
      materia: theme,
      concetto: concept,
      fronte: title,
      retro: shortText(body || clean),
      uso: "Usa questa scheda per presentarti meglio o preparare un colloquio."
    });
  }

  addCard({
    title: "Scheda: profilo professionale",
    concept: "profilo professionale",
    theme: "curriculum",
    conditionWords: ["profilo", "creativo", "adattabile", "obiettivo", "presentazione"],
    body: clean
  });

  addCard({
    title: "Scheda: competenze trasversali",
    concept: "competenze trasversali",
    theme: "curriculum",
    conditionWords: ["creativita", "comunicazione", "pazienza", "lavoro di gruppo", "pubblico", "adattamenti"],
    body: clean
  });

  addCard({
    title: "Scheda: competenze digitali e AI",
    concept: "competenze digitali e AI",
    theme: "digitale",
    conditionWords: ["intelligenza artificiale", "ai", "prompt", "generativa", "automazioni"],
    body: clean
  });

  addCard({
    title: "Scheda: progetti software e applicazioni",
    concept: "progetti software",
    theme: "informatica",
    conditionWords: ["app", "android", "kotlin", "software", "github", "database", "quiz", "python"],
    body: clean
  });

  addCard({
    title: "Scheda: esperienza lavorativa",
    concept: "esperienza lavorativa",
    theme: "lavoro",
    conditionWords: ["esperienza", "lavoro", "mansione", "azienda", "contratto", "pulizie"],
    body: clean
  });

  addCard({
    title: "Scheda: formazione e obiettivi",
    concept: "formazione e obiettivi",
    theme: "curriculum",
    conditionWords: ["formazione", "studio", "corso", "diploma", "its", "obiettivo"],
    body: clean
  });

  if (!cards.length) {
    cards.push({
      materia: "curriculum",
      concetto: "sintesi curriculum",
      fronte: "Scheda: sintesi curriculum",
      retro: shortText(clean || "Testo curriculum non sufficiente."),
      uso: "Usa questa scheda per ricavare una presentazione sintetica."
    });
  }

  return cards.slice(0, 8);
}

function iconSvg(icon) {
  if (icon === "chip") return "▣";
  if (icon === "code") return "</>";
  if (icon === "work") return "▤";
  return "◎";
}

function renderCard(card) {
  const theme = CV_THEMES[card.materia] || CV_THEMES.curriculum;
  const [primary, secondary, accent] = theme.palette;

  return `
    <article class="cv-card" style="--cv-primary:${primary};--cv-secondary:${secondary};--cv-accent:${accent};">
      <div class="cv-badge">${theme.badge}</div>
      <div class="cv-icon">${iconSvg(theme.icon)}</div>
      <h3>${escapeHtml(card.fronte)}</h3>
      <p>${escapeHtml(card.retro)}</p>
      <small>${escapeHtml(card.uso)}</small>
    </article>
  `;
}

function escapeHtml(text) {
  return String(text || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function renderKeywords(keywords) {
  return keywords.map(word => `<span>${escapeHtml(word)}</span>`).join("");
}

function generate() {
  const text = document.getElementById("cvText").value;
  const keywords = extractUsefulKeywords(text);
  const cards = buildCurriculumCards(text);

  document.getElementById("keywordsBox").innerHTML = renderKeywords(keywords);
  document.getElementById("cardsBox").innerHTML = cards.map(renderCard).join("");
  document.getElementById("jsonBox").textContent = JSON.stringify({keywords, cards}, null, 2);

  window.__cvCardsResult = {keywords, cards};
}

function downloadJson() {
  const result = window.__cvCardsResult || {keywords: [], cards: []};
  const blob = new Blob([JSON.stringify(result, null, 2)], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "card-curriculum.json";
  link.click();
  URL.revokeObjectURL(url);
}

const example = `
Curriculum Vitae. Profilo creativo e adattabile.
Esperienza lavorativa come addetto presso azienda.
Competenze: comunicazione, pazienza, lavoro di gruppo.
Competenze digitali: intelligenza artificiale, prompt, immagini generative.
Progetti: app Android, Kotlin, Python, database quiz, GitHub.
Formazione: diploma, obiettivo corso ITS full stack e AI.
`;

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("generateCvCards").addEventListener("click", generate);
  document.getElementById("downloadJson").addEventListener("click", downloadJson);
  document.getElementById("loadExample").addEventListener("click", () => {
    document.getElementById("cvText").value = example;
    generate();
  });
});
