
const RAG_STOPWORDS = new Set([
  "che", "con", "per", "del", "della", "dello", "delle", "degli", "dei",
  "alla", "allo", "alle", "agli", "una", "uno", "anche", "sono", "non",
  "nel", "nella", "nelle", "negli", "questo", "questa", "questi", "queste",
  "come", "piu", "più", "viene", "essere", "può", "puo", "quindi", "tra",
  "fra", "gli", "sul", "sulla", "dai", "dal", "dalle", "ad", "ed"
]);

const OUTPUT_OPTIONS = [
  { id: "summary", label: "Riassunto", checked: true },
  { id: "tables", label: "Tabelle", checked: true },
  { id: "cards", label: "Card colorate", checked: true },
  { id: "quiz", label: "Quiz", checked: false },
  { id: "minicourse", label: "Minicorso", checked: false },
  { id: "data", label: "Dati tecnici", checked: false }
];

const DOWNLOADABLE_OUTPUTS = new Set(["summary", "tables", "cards", "data"]);

const fileInput = document.getElementById("fileInput");
const titleInput = document.getElementById("titleInput");
const generateButton = document.getElementById("generateButton");
const statusBox = document.getElementById("statusBox");
const outputBox = document.getElementById("outputBox");

if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
}

function ensureControls() {
  if (!generateButton || document.getElementById("ragControls")) return;

  const wrapper = document.createElement("section");
  wrapper.id = "ragControls";
  wrapper.className = "generation-options";
  wrapper.innerHTML = `
    <h2>Scegli cosa generare</h2>
    <p>Per la demo RAG puoi generare riassunti, tabelle, card colorate, quiz, minicorso e dati tecnici.</p>
    <div class="option-grid">
      ${OUTPUT_OPTIONS.map(option => `
        <label class="option-pill">
          <input type="checkbox" data-output-option value="${option.id}" ${option.checked ? "checked" : ""}>
          <span>${option.label}</span>
        </label>
      `).join("")}
    </div>
    <div class="ocr-box">
      <label class="option-pill ocr-pill">
        <input type="checkbox" id="useOcrToggle">
        <span>Attiva OCR per PDF scansionati e immagini</span>
      </label>
      <p class="ocr-note">L'OCR usa Tesseract.js. Se il file è una scansione o una foto, l'analisi può richiedere più tempo.</p>
    </div>
    <div class="quick-actions">
      <button type="button" id="selectAllOutputs">Seleziona tutto</button>
      <button type="button" id="clearAllOutputs">Deseleziona tutto</button>
    </div>
  `;

  generateButton.parentNode.insertBefore(wrapper, generateButton);

  document.getElementById("selectAllOutputs").addEventListener("click", () => {
    document.querySelectorAll("[data-output-option]").forEach(input => input.checked = true);
  });

  document.getElementById("clearAllOutputs").addEventListener("click", () => {
    document.querySelectorAll("[data-output-option]").forEach(input => input.checked = false);
  });

  generateButton.textContent = "Genera output selezionati";
}

ensureControls();

function getSelectedOutputs() {
  const selected = new Set();
  document.querySelectorAll("[data-output-option]:checked").forEach(input => selected.add(input.value));
  return selected;
}

function useOcrEnabled() {
  const el = document.getElementById("useOcrToggle");
  return !!(el && el.checked);
}

function fixMojibakeText(text) {
  if (!text) return text;
  const replacements = {
    "Ã¨": "è", "Ã©": "é", "Ã ": "à", "Ã²": "ò", "Ã¹": "ù", "Ã¬": "ì",
    "piÃ¹": "più", "perchÃ©": "perché", "qualitÃ ": "qualità", "vulnerabilitÃ ": "vulnerabilità",
    "puÃ²": "può", "giÃ ": "già", "Â": "", "â€™": "'", "â€œ": "“", "â€": "”", "â€“": "–"
  };
  let output = text;
  for (const [wrong, right] of Object.entries(replacements)) output = output.split(wrong).join(right);
  return output;
}

function stripMarkdownForAnalysis(text) {
  const lines = text.split(/\r?\n/);
  const cleaned = [];
  let insideCodeBlock = false;

  for (const rawLine of lines) {
    let line = rawLine.trim();

    if (line.startsWith("```")) {
      insideCodeBlock = !insideCodeBlock;
      continue;
    }

    if (insideCodeBlock) continue;
    if (!line) {
      cleaned.push("");
      continue;
    }

    if (line.startsWith("#")) continue;
    if (line.startsWith(">") || line.startsWith("---") || line.startsWith("***")) continue;

    line = line.replace(/^[-*+]\s+/, "");
    line = line.replace(/^\d+[.)]\s+/, "");
    line = line.replace(/\[([^\]]+)\]\([^)]+\)/g, "$1");
    line = line.replace(/`([^`]+)`/g, "$1");
    line = line.replaceAll("**", "").replaceAll("__", "").replaceAll("*", "");

    cleaned.push(line);
  }

  return cleaned.join("\n").replace(/\n{3,}/g, "\n\n").trim();
}

function cleanText(text) {
  const fixed = fixMojibakeText(text).replace(/\r\n/g, "\n").replace(/\r/g, "\n");
  const stripped = stripMarkdownForAnalysis(fixed);

  return stripped
    .split(/\n\s*\n/)
    .map(paragraph => paragraph.replace(/\n+/g, " ").replace(/[ \t]+/g, " ").trim())
    .filter(Boolean)
    .join("\n\n");
}

function splitSentences(text) {
  const compact = text.replace(/\s+/g, " ").trim();
  if (!compact) return [];

  return compact
    .split(/(?<=[.!?])\s+(?=[A-ZÀ-Ü0-9])/)
    .map(sentence => sentence.trim())
    .filter(sentence => sentence.length >= 35);
}

function tokenize(text) {
  const matches = text.toLowerCase().match(/[a-zà-öø-ÿ0-9]{3,}/g) || [];
  return matches.filter(word => !RAG_STOPWORDS.has(word) && !/^\d+$/.test(word));
}

function extractKeywords(text, limit = 24) {
  const counts = new Map();
  for (const word of tokenize(text)) counts.set(word, (counts.get(word) || 0) + 1);

  return [...counts.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(([parola, frequenza]) => ({ parola, frequenza }));
}

function scoreSentence(sentence, keywordMap) {
  const words = tokenize(sentence);
  if (!words.length) return 0;
  const baseScore = words.reduce((total, word) => total + (keywordMap.get(word) || 0), 0);
  const lengthPenalty = 1 + Math.abs(words.length - 28) / 65;
  return baseScore / lengthPenalty;
}

function makeSummary(sentences, keywords, maxSentences = 8) {
  const keywordMap = new Map(keywords.map(item => [item.parola, item.frequenza]));
  return sentences
    .map((sentence, index) => ({ sentence, index, score: scoreSentence(sentence, keywordMap) }))
    .sort((a, b) => b.score - a.score)
    .slice(0, maxSentences)
    .sort((a, b) => a.index - b.index)
    .map(item => fixMojibakeText(item.sentence));
}

function findContext(keyword, sentences) {
  const lowerKeyword = keyword.toLowerCase();
  return sentences.find(sentence => sentence.toLowerCase().includes(lowerKeyword)) || sentences[0] || "";
}

function shorten(text, limit = 220) {
  const compact = fixMojibakeText(text).replace(/\s+/g, " ").trim();
  if (compact.length <= limit) return compact;
  return compact.slice(0, limit).replace(/\s+\S*$/, "") + "...";
}

function makeConceptRows(keywords, sentences, limit = 14) {
  const maxFrequency = Math.max(...keywords.map(item => item.frequenza), 1);
  return keywords.slice(0, limit).map(item => ({
    concetto: item.parola,
    frequenza: item.frequenza,
    importanza: Math.max(1, Math.min(5, Math.ceil((item.frequenza / maxFrequency) * 5))),
    spiegazione: shorten(findContext(item.parola, sentences), 260)
  }));
}

function makeCards(rows, limit = 12) {
  return rows.slice(0, limit).map((row, index) => ({
    id: `RAG-CARD-${String(index + 1).padStart(4, "0")}`,
    fronte: `Concetto chiave: ${row.concetto}`,
    retro: row.spiegazione,
    uso: "Ripassa questo punto e prova a rispiegarlo con parole tue.",
    illustrazione: buildCardIllustration(row.concetto, index)
  }));
}

function makeQuiz(rows, limit = 10) {
  const contexts = rows.map(row => row.spiegazione);
  return rows.slice(0, limit).map((row, index) => {
    const correctAnswer = shorten(row.spiegazione, 180);
    const distractors = contexts
      .map(context => shorten(context, 180))
      .filter(context => context && context !== correctAnswer)
      .slice(0, 3);

    while (distractors.length < 3) {
      distractors.push(`Il concetto di ${row.concetto} viene citato, ma con una relazione diversa da quella corretta.`);
    }

    const correctIndex = index % 4;
    const options = [...distractors];
    options.splice(correctIndex, 0, correctAnswer);

    return {
      id: `RAG-QUIZ-${String(index + 1).padStart(4, "0")}`,
      categoria: "rag",
      livello: "intermedio",
      domanda: `Quale affermazione descrive meglio il concetto “${row.concetto}” secondo il documento?`,
      opzioni: options,
      risposta_corretta: correctAnswer,
      indice_risposta_corretta: correctIndex,
      spiegazione: `La risposta corretta riprende il modo in cui il documento collega “${row.concetto}” al contenuto principale.`
    };
  });
}

function cardPalette(index) {
  const palettes = [
    ["#6d28d9", "#0f172a", "#f5d0fe"],
    ["#0f766e", "#082f49", "#a7f3d0"],
    ["#b91c1c", "#111827", "#fecaca"],
    ["#1d4ed8", "#172554", "#bfdbfe"],
    ["#be185d", "#3b0764", "#fbcfe8"],
    ["#ea580c", "#431407", "#fed7aa"]
  ];
  return palettes[index % palettes.length];
}

function buildCardIllustration(keyword, index) {
  const [main, dark, accent] = cardPalette(index);
  const safeKeyword = escapeHtml(keyword || "Concetto");
  return `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 120" role="img" aria-label="Illustrazione ${safeKeyword}">
      <defs>
        <linearGradient id="g${index}" x1="0" y1="0" x2="1" y2="1">
          <stop offset="0%" stop-color="${main}" />
          <stop offset="100%" stop-color="${dark}" />
        </linearGradient>
      </defs>
      <rect x="0" y="0" width="220" height="120" rx="24" fill="url(#g${index})"/>
      <circle cx="42" cy="34" r="18" fill="${accent}" opacity="0.95"/>
      <rect x="28" y="60" width="164" height="14" rx="7" fill="rgba(255,255,255,0.18)"/>
      <rect x="28" y="82" width="118" height="10" rx="5" fill="rgba(255,255,255,0.14)"/>
      <path d="M156 28 L178 44 L156 60 L134 44 Z" fill="${accent}" opacity="0.9"/>
      <text x="28" y="108" font-size="13" fill="white" font-family="Arial, sans-serif">${safeKeyword}</text>
    </svg>
  `;
}

async function runImageOcr(file) {
  if (!window.Tesseract) throw new Error("OCR non disponibile. Tesseract.js non è stato caricato.");
  setStatus("OCR immagine in corso...", "info");
  const result = await Tesseract.recognize(file, "ita+eng");
  return result.data.text || "";
}

async function runPdfOcr(file) {
  if (!window.Tesseract || !window.pdfjsLib) throw new Error("OCR PDF non disponibile. Mancano Tesseract.js o PDF.js.");

  setStatus("OCR PDF in corso... Può richiedere tempo se il documento è grande.", "info");
  const buffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: buffer }).promise;
  const texts = [];

  for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
    setStatus(`OCR PDF in corso... pagina ${pageNumber} di ${pdf.numPages}`, "info");
    const page = await pdf.getPage(pageNumber);
    const viewport = page.getViewport({ scale: 1.6 });
    const canvas = document.createElement("canvas");
    const context = canvas.getContext("2d");
    canvas.width = viewport.width;
    canvas.height = viewport.height;
    await page.render({ canvasContext: context, viewport }).promise;
    const result = await Tesseract.recognize(canvas, "ita+eng");
    texts.push(result.data.text || "");
  }

  return texts.join("\n\n");
}

async function readPdfText(file) {
  if (!window.pdfjsLib) {
    throw new Error("PDF.js non disponibile. Per i PDF usa il pacchetto locale Python.");
  }

  const buffer = await file.arrayBuffer();
  const pdf = await pdfjsLib.getDocument({ data: buffer }).promise;
  const pages = [];

  for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
    const page = await pdf.getPage(pageNumber);
    const content = await page.getTextContent();
    const text = content.items.map(item => item.str).join(" ");
    pages.push(`[Pagina ${pageNumber}]\n${text}`);
  }

  return pages.join("\n\n");
}

async function readUploadedFile(file) {
  const lowerName = file.name.toLowerCase();
  const ocr = useOcrEnabled();

  if (lowerName.endsWith(".png") || lowerName.endsWith(".jpg") || lowerName.endsWith(".jpeg") || lowerName.endsWith(".webp")) {
    return runImageOcr(file);
  }

  if (lowerName.endsWith(".pdf")) {
    const extracted = await readPdfText(file);
    if (ocr || cleanText(extracted).length < 120) {
      return runPdfOcr(file);
    }
    return extracted;
  }

  return file.text();
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function downloadBlob(filename, content, mimeType = "text/plain;charset=utf-8") {
  const blob = content instanceof Blob ? content : new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

function slugify(text) {
  return String(text)
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "")
    .replace(/[^a-zA-Z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "")
    .toLowerCase() || "documento-rag";
}

function markdownTable(headers, rows) {
  const header = `| ${headers.join(" | ")} |`;
  const separator = `| ${headers.map(() => "---").join(" | ")} |`;
  const body = rows.map(row => `| ${row.map(value => String(value).replaceAll("|", "\\|")).join(" | ")} |`);
  return [header, separator, ...body].join("\n");
}

function makeSummaryMarkdown(analysis) {
  return `# Riassunto - ${analysis.titolo}\n\n` + analysis.riassunto.map((sentence, index) => `${index + 1}. ${sentence}`).join("\n") + "\n";
}

function makeSummaryHtmlDocument(analysis) {
  const items = analysis.riassunto.map(sentence => `<li>${escapeHtml(sentence)}</li>`).join("\n");
  return `<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Riassunto RAG - ${escapeHtml(analysis.titolo)}</title>
<style>
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:#0f172a;color:#f8fafc}
main{max-width:920px;margin:0 auto;padding:42px 20px}
section{border:1px solid rgba(255,255,255,.14);border-radius:28px;background:rgba(15,23,42,.88);padding:30px;box-shadow:0 24px 80px rgba(0,0,0,.34)}
h1{font-size:clamp(32px,5vw,52px);line-height:1.05;margin-top:0}
li{margin:16px 0;line-height:1.65;font-size:18px}
</style></head><body><main><section><h1>Riassunto - ${escapeHtml(analysis.titolo)}</h1><ol>${items}</ol></section></main></body></html>`;
}

function makeConceptTableMarkdown(analysis) {
  const rows = analysis.tabella_concetti.map(row => [row.concetto, row.frequenza, `${row.importanza}/5`, row.spiegazione]);
  return `# Tabelle concetti - ${analysis.titolo}\n\n` + markdownTable(["Concetto", "Frequenza", "Importanza", "Spiegazione"], rows) + "\n";
}

function makeConceptTableCsv(analysis) {
  const rows = [["Concetto", "Frequenza", "Importanza", "Spiegazione"]];
  analysis.tabella_concetti.forEach(row => rows.push([row.concetto, row.frequenza, row.importanza, row.spiegazione]));
  return rows.map(row => row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(",")).join("\n");
}

function makeCardsHtmlDocument(analysis) {
  const cards = analysis.cards.map((card, index) => {
    const [main, dark, accent] = cardPalette(index);
    return `
      <article class="card" style="--main:${main};--dark:${dark};--accent:${accent};">
        <div class="ill">${card.illustrazione}</div>
        <h2>${escapeHtml(card.fronte)}</h2>
        <p>${escapeHtml(card.retro)}</p>
        <small>${escapeHtml(card.uso)}</small>
      </article>`;
  }).join("\n");

  return `<!doctype html>
<html lang="it"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Card RAG - ${escapeHtml(analysis.titolo)}</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#0f172a;color:#f8fafc}
main{max-width:1120px;margin:0 auto;padding:36px 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
.card{border:1px solid rgba(255,255,255,.12);border-radius:22px;background:linear-gradient(145deg,var(--main),var(--dark));padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.28)}
.card .ill{margin-bottom:14px}.card h2{font-size:20px;margin:0 0 12px}.card p{line-height:1.55}.card small{color:#e5e7eb;font-weight:700}
</style></head><body><main><h1>Card di ripasso - ${escapeHtml(analysis.titolo)}</h1><section class="grid">${cards}</section></main></body></html>`;
}

function makeReportMarkdown(analysis) {
  return `# Report RAG - ${analysis.titolo}\n\n- Generato il: ${analysis.generato_il}\n- File originale: ${analysis.file_originale}\n- Caratteri estratti: ${analysis.statistiche.caratteri}\n- Parole utili: ${analysis.statistiche.parole}\n- Frasi analizzate: ${analysis.statistiche.frasi}\n- Parole chiave: ${analysis.statistiche.parole_chiave}\n- Card generate: ${analysis.statistiche.card}\n`;
}

function makeDownloadPackage(analysis, selectedOutputs) {
  const files = {};

  if (selectedOutputs.has("summary")) {
    files["riassunto.html"] = makeSummaryHtmlDocument(analysis);
    files["riassunto.md"] = makeSummaryMarkdown(analysis);
  }
  if (selectedOutputs.has("tables")) {
    files["tabelle_concetti.md"] = makeConceptTableMarkdown(analysis);
    files["tabelle_concetti.csv"] = makeConceptTableCsv(analysis);
  }
  if (selectedOutputs.has("cards")) {
        files["cards.json"] = JSON.stringify(analysis.cards, null, 2);
    files["ISTRUZIONI_CARD_PDF.txt"] = "Per le card usa il pulsante: Scarica card PDF stampabile sul PC. Il PDF funziona offline e si apre senza internet.";
  }
  if (selectedOutputs.has("data")) {
    files["analisi_completa.json"] = JSON.stringify(analysis, null, 2);
    files["statistiche.json"] = JSON.stringify(analysis.statistiche, null, 2);
    files["report_rag.md"] = makeReportMarkdown(analysis);
  }
  return files;
}

async function downloadSelectedZip(analysis, selectedOutputs) {
  const files = makeDownloadPackage(analysis, selectedOutputs);
  const slug = slugify(analysis.titolo);

  if (!Object.keys(files).length) {
    setStatus("Per lo ZIP seleziona almeno riassunto, tabelle, card o dati tecnici.", "error");
    return;
  }

  if (!window.JSZip) {
    downloadBlob(`${slug}-output-rag.json`, JSON.stringify(files, null, 2), "application/json;charset=utf-8");
    return;
  }

  const zip = new JSZip();
  const folder = zip.folder(`output-rag-${slug}`);
  Object.entries(files).forEach(([filename, content]) => folder.file(filename, content));
  const blob = await zip.generateAsync({ type: "blob" });
  downloadBlob(`output-rag-${slug}.zip`, blob, "application/zip");
}

function hexToRgb(hex) {
  const clean = String(hex || "#334155").replace("#", "");
  const full = clean.length === 3 ? clean.split("").map(c => c + c).join("") : clean;
  const number = parseInt(full, 16);
  return { r: (number >> 16) & 255, g: (number >> 8) & 255, b: number & 255 };
}

function setPdfFill(pdf, colorHex) {
  const color = hexToRgb(colorHex);
  pdf.setFillColor(color.r, color.g, color.b);
}

function setPdfDraw(pdf, colorHex) {
  const color = hexToRgb(colorHex);
  pdf.setDrawColor(color.r, color.g, color.b);
}

function pdfThemeForCard(card) {
  const subject = card.materia || "generico";
  if (window.RagCardGraphicEngine && window.RagCardGraphicEngine.themes) {
    return window.RagCardGraphicEngine.themes[subject] || window.RagCardGraphicEngine.themes.generico;
  }
  const fallbackThemes = {
    generico: { badge: "Generico", palette: ["#334155", "#64748b", "#e2e8f0"] },
    cybersecurity: { badge: "Cybersecurity", palette: ["#0f172a", "#7c3aed", "#ef4444"] },
    informatica: { badge: "Informatica", palette: ["#0b3b66", "#38bdf8", "#1e293b"] },
    ai: { badge: "AI", palette: ["#1e1b4b", "#8b5cf6", "#22d3ee"] },
    matematica: { badge: "Matematica", palette: ["#0f766e", "#22c55e", "#d9f99d"] },
    fisica: { badge: "Fisica", palette: ["#172554", "#60a5fa", "#f59e0b"] },
    chimica: { badge: "Chimica", palette: ["#14532d", "#2dd4bf", "#fb923c"] },
    biologia: { badge: "Biologia", palette: ["#166534", "#4ade80", "#93c5fd"] }
  };
  return fallbackThemes[subject] || fallbackThemes.generico;
}

function drawPdfIcon(pdf, icon, x, y, size, palette) {
  const primary = palette[0];
  const accent = palette[2];

  setPdfFill(pdf, accent);
  setPdfDraw(pdf, accent);
  pdf.setLineWidth(3);

  if (["shield", "lock-code", "badge-check", "wall"].includes(icon)) {
    pdf.triangle(x + size * 0.5, y, x + size, y + size * 0.22, x + size * 0.5, y + size, "F");
    setPdfFill(pdf, primary);
    pdf.roundedRect(x + size * 0.34, y + size * 0.48, size * 0.32, size * 0.25, 4, 4, "F");
    return;
  }

  if (icon === "backup") {
    pdf.circle(x + size * 0.38, y + size * 0.52, size * 0.22, "F");
    pdf.circle(x + size * 0.58, y + size * 0.45, size * 0.28, "F");
    pdf.circle(x + size * 0.72, y + size * 0.55, size * 0.2, "F");
    pdf.rect(x + size * 0.26, y + size * 0.55, size * 0.56, size * 0.22, "F");
    setPdfDraw(pdf, primary);
    pdf.line(x + size * 0.52, y + size * 0.7, x + size * 0.52, y + size * 0.34);
    pdf.line(x + size * 0.42, y + size * 0.45, x + size * 0.52, y + size * 0.34);
    pdf.line(x + size * 0.62, y + size * 0.45, x + size * 0.52, y + size * 0.34);
    return;
  }

  if (icon === "key") {
    pdf.circle(x + size * 0.28, y + size * 0.38, size * 0.18, "S");
    pdf.line(x + size * 0.42, y + size * 0.48, x + size * 0.9, y + size * 0.9);
    pdf.line(x + size * 0.76, y + size * 0.78, x + size * 0.95, y + size * 0.78);
    return;
  }

  if (icon === "database") {
    pdf.ellipse(x + size * 0.5, y + size * 0.22, size * 0.34, size * 0.13, "F");
    pdf.rect(x + size * 0.16, y + size * 0.22, size * 0.68, size * 0.52, "F");
    pdf.ellipse(x + size * 0.5, y + size * 0.74, size * 0.34, size * 0.13, "F");
    return;
  }

  if (["flow", "function", "api", "server", "json", "screen", "box"].includes(icon)) {
    pdf.roundedRect(x + size * 0.16, y + size * 0.18, size * 0.28, size * 0.22, 5, 5, "F");
    pdf.roundedRect(x + size * 0.58, y + size * 0.18, size * 0.28, size * 0.22, 5, 5, "F");
    pdf.roundedRect(x + size * 0.37, y + size * 0.62, size * 0.28, size * 0.22, 5, 5, "F");
    setPdfDraw(pdf, "#ffffff");
    pdf.line(x + size * 0.44, y + size * 0.3, x + size * 0.58, y + size * 0.3);
    pdf.line(x + size * 0.5, y + size * 0.4, x + size * 0.5, y + size * 0.62);
    return;
  }

  if (["chip", "network", "vectors", "prompt", "rag", "table", "training", "inference"].includes(icon)) {
    pdf.roundedRect(x + size * 0.25, y + size * 0.25, size * 0.5, size * 0.5, 8, 8, "F");
    setPdfFill(pdf, primary);
    pdf.circle(x + size * 0.4, y + size * 0.42, size * 0.04, "F");
    pdf.circle(x + size * 0.6, y + size * 0.42, size * 0.04, "F");
    pdf.circle(x + size * 0.5, y + size * 0.6, size * 0.04, "F");
    return;
  }

  if (["chart", "derivative", "integral", "formula", "percent", "fraction"].includes(icon)) {
    setPdfDraw(pdf, accent);
    pdf.line(x + size * 0.15, y + size * 0.85, x + size * 0.9, y + size * 0.85);
    pdf.line(x + size * 0.22, y + size * 0.9, x + size * 0.22, y + size * 0.15);
    pdf.line(x + size * 0.25, y + size * 0.72, x + size * 0.45, y + size * 0.5);
    pdf.line(x + size * 0.45, y + size * 0.5, x + size * 0.68, y + size * 0.58);
    pdf.line(x + size * 0.68, y + size * 0.58, x + size * 0.86, y + size * 0.28);
    return;
  }

  if (["atom", "energy", "vector", "speed", "acceleration", "circuit"].includes(icon)) {
    pdf.circle(x + size * 0.5, y + size * 0.5, size * 0.06, "F");
    pdf.ellipse(x + size * 0.5, y + size * 0.5, size * 0.42, size * 0.14, "S");
    pdf.ellipse(x + size * 0.5, y + size * 0.5, size * 0.14, size * 0.42, "S");
    return;
  }

  if (["molecule", "reaction", "bond", "flask", "beaker"].includes(icon)) {
    pdf.circle(x + size * 0.32, y + size * 0.45, size * 0.12, "F");
    pdf.circle(x + size * 0.66, y + size * 0.34, size * 0.1, "F");
    pdf.circle(x + size * 0.66, y + size * 0.7, size * 0.13, "F");
    pdf.line(x + size * 0.42, y + size * 0.43, x + size * 0.56, y + size * 0.36);
    pdf.line(x + size * 0.42, y + size * 0.5, x + size * 0.56, y + size * 0.66);
    return;
  }

  if (["dna", "cell", "protein", "organism", "leaf", "mitosis"].includes(icon)) {
    setPdfDraw(pdf, accent);
    pdf.line(x + size * 0.35, y + size * 0.12, x + size * 0.65, y + size * 0.88);
    pdf.line(x + size * 0.65, y + size * 0.12, x + size * 0.35, y + size * 0.88);
    pdf.line(x + size * 0.42, y + size * 0.3, x + size * 0.58, y + size * 0.3);
    pdf.line(x + size * 0.38, y + size * 0.5, x + size * 0.62, y + size * 0.5);
    pdf.line(x + size * 0.42, y + size * 0.7, x + size * 0.58, y + size * 0.7);
    return;
  }

  pdf.circle(x + size * 0.5, y + size * 0.5, size * 0.28, "F");
}

function downloadCardsPdf(analysis) {
  if (!analysis || !Array.isArray(analysis.cards) || !analysis.cards.length) {
    setStatus("Nessuna card da salvare in PDF.", "error");
    return;
  }

  if (!window.jspdf || !window.jspdf.jsPDF) {
    setStatus("PDF non disponibile: ricarica la pagina e riprova. Serve la libreria jsPDF.", "error");
    return;
  }

  const { jsPDF } = window.jspdf;
  const pdf = new jsPDF({ orientation: "portrait", unit: "pt", format: "a4" });
  const pageWidth = pdf.internal.pageSize.getWidth();

  const margin = 36;
  const gap = 20;
  const cardWidth = (pageWidth - margin * 2 - gap) / 2;
  const cardHeight = 330;

  analysis.cards.forEach((card, index) => {
    if (index > 0 && index % 4 === 0) {
      pdf.addPage();
    }

    const position = index % 4;
    const col = position % 2;
    const row = Math.floor(position / 2);

    const x = margin + col * (cardWidth + gap);
    const y = margin + row * (cardHeight + gap);

    const theme = pdfThemeForCard(card);
    const palette = theme.palette || ["#334155", "#64748b", "#e2e8f0"];
    const primary = palette[0];
    const secondary = palette[1];
    const accent = palette[2];

    setPdfFill(pdf, primary);
    pdf.roundedRect(x, y, cardWidth, cardHeight, 18, 18, "F");

    setPdfFill(pdf, secondary);
    pdf.roundedRect(x + 8, y + 8, cardWidth - 16, 96, 14, 14, "F");

    setPdfFill(pdf, accent);
    pdf.circle(x + cardWidth - 42, y + 48, 30, "F");

    setPdfFill(pdf, "#ffffff");
    pdf.roundedRect(x + 16, y + 16, Math.min(110, cardWidth - 32), 24, 10, 10, "F");

    setPdfDraw(pdf, accent);
    pdf.setLineWidth(1.2);
    pdf.roundedRect(x, y, cardWidth, cardHeight, 18, 18, "S");

    pdf.setTextColor(15, 23, 42);
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(9);
    pdf.text(String(theme.badge || card.materia || "Card").toUpperCase(), x + 24, y + 32, { maxWidth: cardWidth - 48 });

    drawPdfIcon(pdf, card.icona || "", x + 54, y + 42, 92, palette);

    pdf.setTextColor(255, 255, 255);
    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(15);
    const titleLines = pdf.splitTextToSize(card.fronte || "Concetto chiave", cardWidth - 34);
    pdf.text(titleLines.slice(0, 3), x + 17, y + 132);

    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10.5);
    const bodyLines = pdf.splitTextToSize(card.retro || "", cardWidth - 34);
    pdf.text(bodyLines.slice(0, 10), x + 17, y + 188);

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(9);
    const usageLines = pdf.splitTextToSize(card.uso || "Ripassa questo punto e prova a rispiegarlo con parole tue.", cardWidth - 34);
    pdf.text(usageLines.slice(0, 3), x + 17, y + cardHeight - 42);
  });

  const slug = slugify(analysis.titolo || "card-rag");
  pdf.save(`card-rag-${slug}.pdf`);
  setStatus("✅ PDF delle card scaricato. Lo trovi nella cartella Download del browser.", "success");
}

function openCardsPrintDialog(analysis) {
  if (!analysis || !Array.isArray(analysis.cards) || !analysis.cards.length) {
    setStatus("Nessuna card da stampare.", "error");
    return;
  }

  const cardsHtml = makeCardsHtmlDocument(analysis);
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    setStatus("Il browser ha bloccato la finestra di stampa. Consenti i popup o usa il download PDF.", "error");
    return;
  }

  printWindow.document.open();
  printWindow.document.write(cardsHtml);
  printWindow.document.close();

  setTimeout(() => {
    printWindow.focus();
    printWindow.print();
  }, 400);
}

function renderDownloadPanel(analysis, selectedOutputs) {
  const pdfCardsButton = document.getElementById("downloadCardsPdfButton");
  if (pdfCardsButton) {
    pdfCardsButton.addEventListener("click", () => downloadCardsPdf(analysis));
  }

  const printCardsButton = document.getElementById("printCardsButton");
  if (printCardsButton) {
    printCardsButton.addEventListener("click", () => openCardsPrintDialog(analysis));
  }

  const downloadableSelected = new Set([...selectedOutputs].filter(key => DOWNLOADABLE_OUTPUTS.has(key)));
  const files = makeDownloadPackage(analysis, downloadableSelected);

  const fileButtons = Object.keys(files).map(filename => {
    return `<button type="button" class="single-download-button" data-download-file="${escapeHtml(filename)}">Scarica ${escapeHtml(filename)}</button>`;
  }).join("");

  return `
    <section class="panel">
      <h2>Scarica output</h2>
      <p>
        Il pulsante PDF delle card scarica un file stampabile sul PC. Il file si apre offline, senza internet. Lo ZIP scarica un pacchetto con gli output selezionati.
        Su Mac di solito è <strong>Download</strong>; su smartphone è nella cartella Download o File.
        Se vuoi scegliere ogni volta dove salvarli, attiva nel browser l'opzione “Chiedi dove salvare ogni file”.
      </p>
      ${selectedOutputs.has("cards") ? `
      <div class="download-grid card-pdf-actions">
        <button type="button" id="downloadCardsPdfButton">Scarica card PDF stampabile sul PC</button>
        <button type="button" id="printCardsButton">Stampa / salva card come PDF</button>
      </div>
    ` : ""}
      <div class="download-grid">
        <button type="button" id="downloadSelectedZip">Scarica ZIP con riassunti, tabelle e card selezionati</button>
        ${fileButtons}
      </div>
    </section>
  `;
}

function setStatus(message, type = "info") {
  statusBox.textContent = message;
  statusBox.className = `status ${type}`;
}

function renderOutput(analysis, selectedOutputs) {
  const sections = [];

  if (selectedOutputs.has("summary")) {
    const summaryHtml = analysis.riassunto.map(sentence => `<li>${escapeHtml(sentence)}</li>`).join("");
    sections.push(`<section class="panel"><h2>Riassunto leggibile</h2><ol>${summaryHtml}</ol></section>`);
  }

  if (selectedOutputs.has("tables")) {
    const tableHtml = analysis.tabella_concetti.map(row => `
      <tr><td>${escapeHtml(row.concetto)}</td><td>${row.frequenza}</td><td>${row.importanza}/5</td><td>${escapeHtml(row.spiegazione)}</td></tr>`).join("");
    sections.push(`
      <section class="panel"><h2>Tabella concetti</h2><div class="table-wrap"><table><thead><tr><th>Concetto</th><th>Frequenza</th><th>Importanza</th><th>Spiegazione</th></tr></thead><tbody>${tableHtml}</tbody></table></div></section>
    `);
  }

  if (selectedOutputs.has("cards")) {
    const cardsHtml = analysis.cards.map((card, index) => {
      const [main, dark, accent] = cardPalette(index);
      return `<article class="mini-card" style="background:linear-gradient(145deg, ${main}, ${dark});border-color:${accent};"><div class="mini-card-ill">${card.illustrazione}</div><h3>${escapeHtml(card.fronte)}</h3><p>${escapeHtml(card.retro)}</p></article>`;
    }).join("");
    sections.push(`<section class="panel"><h2>Card colorate di ripasso</h2><div class="cards-grid">${cardsHtml}</div></section>`);
  }

  if (selectedOutputs.has("quiz")) {
    const quizHtml = analysis.quiz.map((item, questionIndex) => `
      <article class="quiz-card">
        <h3>${questionIndex + 1}. ${escapeHtml(item.domanda)}</h3>
        ${item.opzioni.map((option, optionIndex) => `
          <button class="quiz-option" data-correct="${option === item.risposta_corretta ? "true" : "false"}">${String.fromCharCode(65 + optionIndex)}. ${escapeHtml(option)}</button>
        `).join("")}
        <p class="quiz-explanation">${escapeHtml(item.spiegazione)}</p>
      </article>`).join("");
    sections.push(`<section class="panel"><h2>Quiz interattivo</h2>${quizHtml}</section>`);
  }

  if (selectedOutputs.has("minicourse")) {
    sections.push(`<section class="panel"><h2>Minicorso</h2><p>Il minicorso viene generato come contenuto riassuntivo e può essere aggiunto dopo, se vuoi, anche come file HTML dedicato.</p></section>`);
  }

  sections.push(renderDownloadPanel(analysis, selectedOutputs));
  outputBox.innerHTML = sections.join("");

  document.querySelectorAll(".quiz-option").forEach(button => {
    button.addEventListener("click", () => {
      const box = button.closest(".quiz-card");
      const buttons = box.querySelectorAll(".quiz-option");
      buttons.forEach(item => {
        item.disabled = true;
        if (item.dataset.correct === "true") item.classList.add("correct");
      });
      if (button.dataset.correct !== "true") button.classList.add("wrong");
      box.querySelector(".quiz-explanation").style.display = "block";
    });
  });

  const zipButton = document.getElementById("downloadSelectedZip");
  if (zipButton) {
    zipButton.addEventListener("click", () => {
      const downloadableSelected = new Set([...selectedOutputs].filter(key => DOWNLOADABLE_OUTPUTS.has(key)));
      downloadSelectedZip(analysis, downloadableSelected);
    });
  }

  const downloadableSelected = new Set([...selectedOutputs].filter(key => DOWNLOADABLE_OUTPUTS.has(key)));
  const files = makeDownloadPackage(analysis, downloadableSelected);
  document.querySelectorAll("[data-download-file]").forEach(button => {
    button.addEventListener("click", () => {
      const filename = button.dataset.downloadFile;
      const content = files[filename];
      if (!content) return;

      let mimeType = "text/plain;charset=utf-8";
      if (filename.endsWith(".html")) mimeType = "text/html;charset=utf-8";
      if (filename.endsWith(".json")) mimeType = "application/json;charset=utf-8";
      if (filename.endsWith(".csv")) mimeType = "text/csv;charset=utf-8";
      if (filename.endsWith(".md")) mimeType = "text/markdown;charset=utf-8";
      downloadBlob(filename, content, mimeType);
    });
  });
}

generateButton.addEventListener("click", async () => {
  const file = fileInput.files[0];
  const selectedOutputs = getSelectedOutputs();

  if (!file) {
    setStatus("Seleziona prima un file TXT, PDF, Markdown o immagine.", "error");
    return;
  }

  if (!selectedOutputs.size) {
    setStatus("Seleziona almeno una cosa da generare: riassunto, tabelle, card, quiz o minicorso.", "error");
    return;
  }

  try {
    setStatus("Analisi in corso. Il motore sta generando gli output selezionati...", "info");
    const rawText = await readUploadedFile(file);
    const cleanedText = cleanText(rawText);

    if (cleanedText.length < 120) {
      throw new Error("Testo estratto troppo corto. Se il documento è una scansione, attiva l'OCR.");
    }

    const title = titleInput.value.trim() || file.name.replace(/\.[^.]+$/, "");
    const sentences = splitSentences(cleanedText);
    const keywords = extractKeywords(cleanedText);
    const summary = makeSummary(sentences, keywords, 8);
    const rows = makeConceptRows(keywords, sentences);
    const cards = makeCards(rows);
    const quiz = makeQuiz(rows);

    const analysis = {
      titolo: title,
      file_originale: file.name,
      generato_il: new Date().toISOString(),
      statistiche: {
        caratteri: cleanedText.length,
        parole: tokenize(cleanedText).length,
        frasi: sentences.length,
        parole_chiave: keywords.length,
        card: cards.length,
        quiz: quiz.length
      },
      parole_chiave: keywords,
      riassunto: summary,
      tabella_concetti: rows,
      cards,
      quiz
    };

    renderOutput(analysis, selectedOutputs);
    setStatus("✅ Output generati. Ora puoi leggerli e scaricare riassunti, tabelle e card sul tuo dispositivo.", "success");
  } catch (error) {
    setStatus(`❌ ${error.message}`, "error");
  }
});
