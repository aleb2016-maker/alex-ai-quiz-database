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

function iconSvg(icon, materia = "", concetto = "") {
  const raw = `${icon || ""} ${materia || ""} ${concetto || ""}`.toLowerCase();

  function svg(body) {
    return `<svg viewBox="0 0 96 96" aria-hidden="true" focusable="false" class="cv-inline-icon">${body}</svg>`;
  }

  if (raw.includes("profilo") || raw.includes("curriculum")) {
    return svg(`
      <rect x="18" y="22" width="46" height="32" rx="10" fill="#f9a8d4" opacity="0.95"></rect>
      <rect x="32" y="38" width="46" height="32" rx="10" fill="#f472b6" opacity="0.95"></rect>
      <circle cx="41" cy="34" r="6" fill="#ffffff"></circle>
      <path d="M30 49 c5 -10 18 -10 24 0" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round"></path>
    `);
  }

  if (raw.includes("competen")) {
    return svg(`
      <rect x="18" y="22" width="48" height="34" rx="10" fill="#a78bfa"></rect>
      <rect x="32" y="38" width="46" height="30" rx="10" fill="#7c3aed"></rect>
      <path d="M38 53 l8 8 l18 -22" fill="none" stroke="#ffffff" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"></path>
      <circle cx="40" cy="31" r="4" fill="#ffffff"></circle>
      <circle cx="52" cy="31" r="4" fill="#ffffff"></circle>
    `);
  }

  if (raw.includes("progett") || raw.includes("software") || raw.includes("app") || raw.includes("informatica")) {
    return svg(`
      <rect x="18" y="22" width="48" height="34" rx="10" fill="#7dd3fc"></rect>
      <rect x="32" y="38" width="46" height="30" rx="10" fill="#2563eb"></rect>
      <path d="M41 53 l7 -7 l7 7" fill="none" stroke="#ffffff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"></path>
      <path d="M39 32 h18 M39 40 h12" stroke="#ffffff" stroke-width="4" stroke-linecap="round"></path>
    `);
  }

  if (raw.includes("formazione") || raw.includes("studio") || raw.includes("diploma") || raw.includes("obiettivi")) {
    return svg(`
      <rect x="18" y="22" width="48" height="34" rx="10" fill="#fdba74"></rect>
      <rect x="32" y="38" width="46" height="30" rx="10" fill="#f97316"></rect>
      <path d="M48 28 l18 9 l-18 9 l-18 -9 z" fill="#ffffff"></path>
      <path d="M60 40 v8" stroke="#ffffff" stroke-width="4" stroke-linecap="round"></path>
    `);
  }

  if (raw.includes("esperienza") || raw.includes("lavoro") || raw.includes("azienda")) {
    return svg(`
      <rect x="18" y="22" width="48" height="34" rx="10" fill="#86efac"></rect>
      <rect x="32" y="38" width="46" height="30" rx="10" fill="#22c55e"></rect>
      <rect x="42" y="28" width="16" height="10" rx="3" fill="#ffffff"></rect>
      <rect x="38" y="43" width="28" height="16" rx="4" fill="#ffffff"></rect>
    `);
  }

  if (raw.includes("digitale") || raw.includes("ai") || raw.includes("prompt")) {
    return svg(`
      <rect x="26" y="24" width="44" height="48" rx="12" fill="#3b82f6"></rect>
      <path d="M39 40 h18 M39 49 h18" stroke="#ffffff" stroke-width="5" stroke-linecap="round"></path>
      <circle cx="48" cy="61" r="4" fill="#ffffff"></circle>
    `);
  }

  return svg(`
    <rect x="22" y="24" width="46" height="34" rx="10" fill="#93c5fd"></rect>
    <rect x="34" y="38" width="42" height="30" rx="10" fill="#60a5fa"></rect>
    <path d="M42 50 h20 M42 58 h12" stroke="#ffffff" stroke-width="5" stroke-linecap="round"></path>
  `);
}

function getCardBadge(card, index = 0) {
  const raw = `${card.fronte || ""} ${card.concetto || ""} ${card.materia || ""}`.toLowerCase();

  if (raw.includes("profilo")) return "Profilo";
  if (raw.includes("competenze digitali") || raw.includes("ai") || raw.includes("prompt")) return "AI / Digitale";
  if (raw.includes("competenze")) return "Competenze";
  if (raw.includes("progetti") || raw.includes("software") || raw.includes("app")) return "Progetti";
  if (raw.includes("esperienza") || raw.includes("lavoro")) return "Esperienza";
  if (raw.includes("formazione") || raw.includes("obiettivi") || raw.includes("studio")) return "Formazione";

  if (index === 0) return "Documento";
  return "Sintesi";
}

function renderCard(card, index = 0) {
  const theme = CV_THEMES[card.materia] || CV_THEMES.curriculum;

  let palette = Array.isArray(theme.palette) && theme.palette.length >= 3
    ? [...theme.palette]
    : ["#1e1b4b", "#7c3aed", "#22d3ee"];

  const raw = `${card.fronte || ""} ${card.concetto || ""} ${card.materia || ""}`.toLowerCase();

  if (raw.includes("profilo")) {
    palette = index % 2 === 0
      ? ["#6b1d55", "#d63384", "#ff7aa2"]
      : ["#7a1f5c", "#c026d3", "#fb7185"];
  } else if (raw.includes("competen")) {
    palette = index % 2 === 0
      ? ["#5b1f6e", "#8b5cf6", "#a78bfa"]
      : ["#432dd7", "#7c3aed", "#60a5fa"];
  } else if (raw.includes("progett") || raw.includes("software")) {
    palette = index % 2 === 0
      ? ["#0f4c81", "#2563eb", "#60a5fa"]
      : ["#155e75", "#0891b2", "#67e8f9"];
  } else if (raw.includes("formazione") || raw.includes("obiettivi")) {
    palette = index % 2 === 0
      ? ["#7a3b00", "#ea580c", "#fdba74"]
      : ["#92400e", "#f97316", "#fbbf24"];
  } else if (raw.includes("esperienza") || raw.includes("lavoro")) {
    palette = index % 2 === 0
      ? ["#14532d", "#16a34a", "#86efac"]
      : ["#166534", "#22c55e", "#4ade80"];
  }

  const [primary, secondary, accent] = palette;
  const icon = iconSvg(theme.icon, card.materia || "", card.concetto || "");
  const badge = getCardBadge(card, index);

  return `
    <article class="cv-card" style="--cv-primary:${primary};--cv-secondary:${secondary};--cv-accent:${accent};">
      <div class="cv-badge">${escapeHtml(badge)}</div>
      <div class="cv-icon" aria-hidden="true">${icon}</div>
      <h3>${escapeHtml(card.fronte || "Scheda documento")}</h3>
      <p>${escapeHtml(card.retro || "")}</p>
      <small>${escapeHtml(card.uso || "Usa questa scheda per ripassare il contenuto.")}</small>
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


function downloadPdfFile() {
  const result = window.__cvCardsResult || { keywords: [], cards: [] };
  const cards = Array.isArray(result.cards) ? result.cards : [];

  if (!cards.length) {
    alert("Prima genera le card del documento.");
    return;
  }

  const styleUrl = new URL("style.css", window.location.href).href;
  const cardsHtml = cards.map((card, index) => renderCard(card, index)).join("");

  const printHtml = `
<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Card documento PDF</title>
<link rel="stylesheet" href="${styleUrl}">
<style>
  * {
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
    box-sizing: border-box;
  }

  html,
  body {
    margin: 0 !important;
    padding: 0 !important;
    background: #f4f6fb !important;
  }

  .pdf-card-page {
    width: 210mm;
    min-height: 297mm;
    padding: 14mm;
    display: flex;
    align-items: center;
    justify-content: center;
    page-break-after: always;
    break-after: page;
    background: #f4f6fb !important;
  }

  .pdf-card-page:last-child {
    page-break-after: auto;
    break-after: auto;
  }

  .pdf-card-page .cv-card {
    width: 100% !important;
    max-width: 165mm !important;
    min-height: 245mm !important;
    margin: 0 auto !important;
    border-radius: 32px !important;
    padding: 24mm 18mm 18mm !important;
  }

  .pdf-card-page .cv-badge {
    font-size: 13px !important;
    padding: 9px 16px !important;
  }

  .pdf-card-page .cv-icon {
    width: 38mm !important;
    height: 38mm !important;
    font-size: 42px !important;
    margin: 24mm 0 18mm !important;
  }

  .pdf-card-page .cv-card h3 {
    font-size: 34px !important;
    line-height: 1.12 !important;
    margin-bottom: 12mm !important;
  }

  .pdf-card-page .cv-card p {
    font-size: 20px !important;
    line-height: 1.48 !important;
  }

  .pdf-card-page .cv-card small {
    display: block !important;
    margin-top: 16mm !important;
    font-size: 18px !important;
    line-height: 1.3 !important;
    font-weight: 900 !important;
  }

  
  .pdf-card-page .cv-card {
    box-shadow: none !important;
    transform: none !important;
  }

  .pdf-card-page .cv-card::before,
  .pdf-card-page .cv-card::after {
    opacity: .14 !important;
  }

  .pdf-card-page .cv-inline-icon {
    width: 60px !important;
    height: 60px !important;
  }

  @page {
    size: A4;
    margin: 0;
  }

  @media print {
    body {
      background: #f4f6fb !important;
    }

    .pdf-card-page {
      page-break-after: always;
      break-after: page;
    }

    .pdf-card-page:last-child {
      page-break-after: auto;
      break-after: auto;
    }
  }
</style>
</head>
<body>
  ${cards.map((card, index) => `
    <section class="pdf-card-page">
      ${renderCard(card, index)}
    </section>
  `).join("")}

  <script>
    window.addEventListener("load", function () {
      setTimeout(function () {
        window.print();
      }, 700);
    });
  </script>
</body>
</html>`;

  const printWindow = window.open("", "_blank");

  if (!printWindow) {
    alert("Il browser ha bloccato l'apertura della finestra PDF. Consenti i popup per questa pagina.");
    return;
  }

  printWindow.document.open();
  printWindow.document.write(printHtml);
  printWindow.document.close();
}


function downloadJson() {
  const result = window.__cvCardsResult || {keywords: [], cards: []};
  const blob = new Blob([JSON.stringify(result, null, 2)], {type: "application/json"});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "card-documento.json";
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
  document.getElementById("downloadPdf").addEventListener("click", downloadPdfFile);
  document.getElementById("downloadJson").addEventListener("click", downloadJson);
  document.getElementById("loadExample").addEventListener("click", () => {
    document.getElementById("cvText").value = example;
    generate();
  });
});
