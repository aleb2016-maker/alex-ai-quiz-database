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
  const m = String(materia || "").toLowerCase();
  const c = String(concetto || "").toLowerCase();
  const i = String(icon || "").toLowerCase();

  if (i === "chip" || m.includes("digitale") || c.includes("digitale") || c.includes("ai")) return "💻";
  if (i === "code" || m.includes("informatica") || c.includes("software") || c.includes("app")) return "🧩";
  if (i === "work" || m.includes("lavoro") || c.includes("lavorativa") || c.includes("colloquio")) return "💼";
  if (c.includes("formazione") || c.includes("studio") || c.includes("obiettivi")) return "🎓";
  if (c.includes("profilo") || m.includes("curriculum")) return "👤";
  return "📄";
}

function renderCard(card) {
  const theme = CV_THEMES[card.materia] || CV_THEMES.curriculum;
  const palette = Array.isArray(theme.palette) && theme.palette.length >= 3
    ? theme.palette
    : ["#1e1b4b", "#7c3aed", "#22d3ee"];

  const [primary, secondary, accent] = palette;
  const icon = iconSvg(theme.icon, card.materia || "", card.concetto || "");

  return `
    <article class="cv-card" style="--cv-primary:${primary};--cv-secondary:${secondary};--cv-accent:${accent};">
      <div class="cv-badge">${escapeHtml(theme.badge || card.materia || "Documento")}</div>
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
  const keywords = Array.isArray(result.keywords) ? result.keywords : [];

  if (!cards.length) {
    alert("Prima genera le card del documento.");
    return;
  }

  function cleanPdfText(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^\x20-\x7E]/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function esc(value) {
    return cleanPdfText(value)
      .replace(/\\/g, "\\\\")
      .replace(/\(/g, "\\(")
      .replace(/\)/g, "\\)");
  }

  function wrapText(text, maxChars) {
    const words = cleanPdfText(text).split(" ");
    const lines = [];
    let line = "";

    words.forEach(word => {
      const candidate = line ? line + " " + word : word;
      if (candidate.length > maxChars) {
        if (line) lines.push(line);
        line = word;
      } else {
        line = candidate;
      }
    });

    if (line) lines.push(line);
    return lines;
  }

  function textLinesPdf(lines, x, startY, fontSize, lineGap) {
    let y = startY;
    let out = "";
    lines.forEach(line => {
      out += "BT /F1 " + fontSize + " Tf " + x + " " + y + " Td (" + esc(line) + ") Tj ET\n";
      y -= lineGap;
    });
    return out;
  }

  function pageContentForCard(card, index) {
    const title = card.fronte || card.concetto || ("Scheda documento " + (index + 1));
    const badge = card.materia || "Documento";
    const body = card.retro || "";
    const use = card.uso || "Usa questa scheda per ripassare il contenuto.";

    let content = "";

    // sfondo pagina
    content += "q 0.96 0.97 0.99 rg 0 0 595 842 re f Q\n";

    // card colorata
    content += "q 0.34 0.08 0.24 rg 48 72 499 698 re f Q\n";
    content += "q 0.74 0.09 0.34 rg 48 72 499 230 re f Q\n";
    content += "q 0.98 0.72 0.16 rg 390 72 157 157 re f Q\n";

    // badge
    content += "q 1 1 1 rg 72 700 180 34 re f Q\n";
    content += "0 0 0 rg\n";
    content += "BT /F1 14 Tf 90 711 Td (" + esc(badge.toUpperCase()) + ") Tj ET\n";

    // titolo
    content += "1 1 1 rg\n";
    content += textLinesPdf(wrapText(title, 28), 72, 640, 27, 34);

    // corpo
    content += textLinesPdf(wrapText(body, 52).slice(0, 14), 72, 520, 16, 23);

    // uso
    content += textLinesPdf(wrapText(use, 46).slice(0, 3), 72, 170, 15, 21);

    return content;
  }

  function pageContentForCover() {
    let content = "";
    content += "q 0.96 0.97 0.99 rg 0 0 595 842 re f Q\n";
    content += "q 0.12 0.10 0.28 rg 48 72 499 698 re f Q\n";
    content += "q 0.49 0.18 0.82 rg 48 72 499 220 re f Q\n";

    content += "1 1 1 rg\n";
    content += textLinesPdf(["Card documento"], 72, 650, 34, 40);
    content += textLinesPdf(["File PDF generato dalle card selezionate."], 72, 595, 17, 24);

    if (keywords.length) {
      content += textLinesPdf(["Parole chiave estratte:"], 72, 525, 20, 28);
      content += textLinesPdf(wrapText(keywords.join("  -  "), 56).slice(0, 8), 72, 485, 15, 22);
    }

    content += textLinesPdf(["Pagine card: " + cards.length], 72, 170, 16, 24);

    return content;
  }

  function buildPdfBlob() {
    const pageStreams = [pageContentForCover(), ...cards.map(pageContentForCard)];

    const objects = [];
    objects.push("<< /Type /Catalog /Pages 2 0 R >>");

    const pageIds = pageStreams.map((_, i) => 4 + i * 2);
    objects.push("<< /Type /Pages /Kids [" + pageIds.map(id => id + " 0 R").join(" ") + "] /Count " + pageIds.length + " >>");

    objects.push("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>");

    pageStreams.forEach((stream, i) => {
      const pageObjId = 4 + i * 2;
      const contentObjId = 5 + i * 2;

      objects[pageObjId - 1] =
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 3 0 R >> >> /Contents " + contentObjId + " 0 R >>";

      objects[contentObjId - 1] =
        "<< /Length " + stream.length + " >>\nstream\n" + stream + "\nendstream";
    });

    let pdf = "%PDF-1.4\n";
    const offsets = [0];

    objects.forEach((obj, index) => {
      offsets.push(pdf.length);
      pdf += (index + 1) + " 0 obj\n" + obj + "\nendobj\n";
    });

    const xrefStart = pdf.length;
    pdf += "xref\n0 " + (objects.length + 1) + "\n";
    pdf += "0000000000 65535 f \n";

    offsets.slice(1).forEach(offset => {
      pdf += String(offset).padStart(10, "0") + " 00000 n \n";
    });

    pdf += "trailer\n<< /Size " + (objects.length + 1) + " /Root 1 0 R >>\n";
    pdf += "startxref\n" + xrefStart + "\n%%EOF";

    return new Blob([pdf], { type: "application/pdf" });
  }

  const blob = buildPdfBlob();
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = "card-documento.pdf";
  document.body.appendChild(link);
  link.click();
  link.remove();

  setTimeout(() => URL.revokeObjectURL(url), 30000);
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
