const RAG_STOPWORDS = new Set([
  "che", "con", "per", "del", "della", "dello", "delle", "degli", "dei",
  "alla", "allo", "alle", "agli", "una", "uno", "anche", "sono", "non",
  "nel", "nella", "nelle", "negli", "questo", "questa", "questi", "queste",
  "come", "piu", "più", "viene", "essere", "può", "puo", "quindi", "tra",
  "fra", "gli", "sul", "sulla", "dai", "dal", "dalle", "ad", "ed"
]);

const OUTPUT_OPTIONS = [
  { id: "summary", label: "Riassunto", files: ["riassunto.html", "riassunto.md"] },
  { id: "tables", label: "Tabelle", files: ["tabelle_concetti.md", "tabelle_concetti.csv"] },
  { id: "cards", label: "Card", files: ["cards.html", "cards.json"] },
  { id: "quiz", label: "Quiz", files: ["quiz_interattivo.html", "quiz.json"] },
  { id: "minicourse", label: "Minicorso", files: ["minicorso_interattivo.html"] },
  { id: "data", label: "Dati tecnici", files: ["analisi_completa.json", "statistiche.json", "report_rag.md"] }
];

const fileInput = document.getElementById("fileInput");
const titleInput = document.getElementById("titleInput");
const generateButton = document.getElementById("generateButton");
const statusBox = document.getElementById("statusBox");
const outputBox = document.getElementById("outputBox");

if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
}

function ensureGenerationOptions() {
  if (!generateButton || document.getElementById("generationOptions")) {
    return;
  }

  const box = document.createElement("section");
  box.id = "generationOptions";
  box.className = "generation-options";
  box.innerHTML = `
    <h2>Scegli cosa generare</h2>
    <p>Puoi generare tutto oppure solo riassunto, tabelle, card, quiz o minicorso.</p>
    <div class="option-grid">
      ${OUTPUT_OPTIONS.map(option => `
        <label class="option-pill">
          <input type="checkbox" data-output-option value="${option.id}" checked>
          <span>${option.label}</span>
        </label>
      `).join("")}
    </div>
    <div class="quick-actions">
      <button type="button" id="selectAllOutputs">Seleziona tutto</button>
      <button type="button" id="clearAllOutputs">Deseleziona tutto</button>
    </div>
  `;

  generateButton.parentNode.insertBefore(box, generateButton);

  document.getElementById("selectAllOutputs").addEventListener("click", () => {
    document.querySelectorAll("[data-output-option]").forEach(input => input.checked = true);
  });

  document.getElementById("clearAllOutputs").addEventListener("click", () => {
    document.querySelectorAll("[data-output-option]").forEach(input => input.checked = false);
  });

  generateButton.textContent = "Genera output selezionati";
}

ensureGenerationOptions();

function getSelectedOutputs() {
  const selected = new Set();

  document.querySelectorAll("[data-output-option]:checked").forEach(input => {
    selected.add(input.value);
  });

  return selected;
}

function fixMojibakeText(text) {
  if (!text) return text;

  const replacements = {
    "Ã¨": "è",
    "Ã©": "é",
    "Ã ": "à",
    "Ã²": "ò",
    "Ã¹": "ù",
    "Ã¬": "ì",
    "piÃ¹": "più",
    "perchÃ©": "perché",
    "qualitÃ ": "qualità",
    "vulnerabilitÃ ": "vulnerabilità",
    "puÃ²": "può",
    "giÃ ": "già",
    "Â": "",
    "â€™": "'",
    "â€œ": "“",
    "â€": "”",
    "â€“": "–"
  };

  let output = text;
  for (const [wrong, right] of Object.entries(replacements)) {
    output = output.split(wrong).join(right);
  }
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

function setStatus(message, type = "info") {
  statusBox.textContent = message;
  statusBox.className = `status ${type}`;
}

function cleanText(text) {
  const fixed = fixMojibakeText(text)
    .replace(/\r\n/g, "\n")
    .replace(/\r/g, "\n");

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

  for (const word of tokenize(text)) {
    counts.set(word, (counts.get(word) || 0) + 1);
  }

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
    uso: "Ripassa questo punto e prova a rispiegarlo con parole tue."
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
  if (lowerName.endsWith(".pdf")) return readPdfText(file);
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
  const body = rows.map(row => {
    return `| ${row.map(value => String(value).replaceAll("|", "\\|")).join(" | ")} |`;
  });

  return [header, separator, ...body].join("\n");
}

function makeSummaryMarkdown(analysis) {
  return `# Riassunto - ${analysis.titolo}\n\n` +
    analysis.riassunto.map((sentence, index) => `${index + 1}. ${sentence}`).join("\n") +
    "\n";
}

function makeSummaryHtmlDocument(analysis) {
  const items = analysis.riassunto
    .map(sentence => `<li>${escapeHtml(sentence)}</li>`)
    .join("\n");

  return `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Riassunto RAG - ${escapeHtml(analysis.titolo)}</title>
<style>
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:#0f172a;color:#f8fafc}
main{max-width:920px;margin:0 auto;padding:42px 20px}
section{border:1px solid rgba(255,255,255,.14);border-radius:28px;background:rgba(15,23,42,.88);padding:30px;box-shadow:0 24px 80px rgba(0,0,0,.34)}
h1{font-size:clamp(32px,5vw,52px);line-height:1.05;margin-top:0}
li{margin:16px 0;line-height:1.65;font-size:18px}
</style>
</head>
<body>
<main>
<section>
<h1>Riassunto - ${escapeHtml(analysis.titolo)}</h1>
<ol>
${items}
</ol>
</section>
</main>
</body>
</html>`;
}

function makeConceptTableMarkdown(analysis) {
  const rows = analysis.tabella_concetti.map(row => [
    row.concetto,
    row.frequenza,
    `${row.importanza}/5`,
    row.spiegazione
  ]);

  return `# Tabelle concetti - ${analysis.titolo}\n\n` +
    markdownTable(["Concetto", "Frequenza", "Importanza", "Spiegazione"], rows) +
    "\n";
}

function makeConceptTableCsv(analysis) {
  const rows = [["Concetto", "Frequenza", "Importanza", "Spiegazione"]];

  analysis.tabella_concetti.forEach(row => {
    rows.push([row.concetto, row.frequenza, row.importanza, row.spiegazione]);
  });

  return rows.map(row => {
    return row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(",");
  }).join("\n");
}

function makeCardsHtmlDocument(analysis) {
  const cards = analysis.cards.map(card => `
    <article class="card">
      <h2>${escapeHtml(card.fronte)}</h2>
      <p>${escapeHtml(card.retro)}</p>
      <small>${escapeHtml(card.uso)}</small>
    </article>
  `).join("\n");

  return `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Card RAG - ${escapeHtml(analysis.titolo)}</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#0f172a;color:#f8fafc}
main{max-width:1100px;margin:0 auto;padding:36px 20px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:18px}
.card{border:1px solid rgba(255,255,255,.12);border-radius:22px;background:linear-gradient(145deg,rgba(124,58,237,.22),rgba(15,23,42,.94));padding:22px;box-shadow:0 20px 60px rgba(0,0,0,.28)}
.card h2{font-size:20px;margin:0 0 12px}.card p{line-height:1.55}.card small{color:#cbd5e1;font-weight:700}
</style>
</head>
<body>
<main>
<h1>Card di ripasso - ${escapeHtml(analysis.titolo)}</h1>
<section class="grid">${cards}</section>
</main>
</body>
</html>`;
}

function makeQuizHtmlDocument(analysis) {
  const quizJson = JSON.stringify(analysis.quiz);

  return `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Quiz RAG - ${escapeHtml(analysis.titolo)}</title>
<style>
body{margin:0;font-family:Arial,sans-serif;background:#111827;color:#f9fafb}
main{max-width:980px;margin:0 auto;padding:34px 20px}
.question{border:1px solid rgba(255,255,255,.12);border-radius:22px;padding:22px;margin:18px 0;background:rgba(255,255,255,.06)}
button{display:block;width:100%;margin:10px 0;padding:14px;border-radius:14px;border:1px solid rgba(255,255,255,.16);background:#1f2937;color:#fff;cursor:pointer;font-weight:800;text-align:left}
button.correct{background:#166534}button.wrong{background:#7f1d1d}.explanation{display:none;margin-top:12px;color:#d1d5db}
</style>
</head>
<body>
<main>
<h1>Quiz generato dal documento - ${escapeHtml(analysis.titolo)}</h1>
<div id="quiz"></div>
</main>
<script>
const quiz = ${quizJson};
const container = document.getElementById("quiz");
quiz.forEach((item, questionIndex) => {
  const box = document.createElement("section");
  box.className = "question";
  const title = document.createElement("h2");
  title.textContent = \`\${questionIndex + 1}. \${item.domanda}\`;
  box.appendChild(title);
  const explanation = document.createElement("p");
  explanation.className = "explanation";
  explanation.textContent = item.spiegazione;
  item.opzioni.forEach((option, optionIndex) => {
    const button = document.createElement("button");
    button.textContent = \`\${String.fromCharCode(65 + optionIndex)}. \${option}\`;
    button.addEventListener("click", () => {
      const allButtons = box.querySelectorAll("button");
      allButtons.forEach(btn => btn.disabled = true);
      if (option === item.risposta_corretta) {
        button.classList.add("correct");
      } else {
        button.classList.add("wrong");
        allButtons[item.indice_risposta_corretta].classList.add("correct");
      }
      explanation.style.display = "block";
    });
    box.appendChild(button);
  });
  box.appendChild(explanation);
  container.appendChild(box);
});
</script>
</body>
</html>`;
}

function makeMiniCourseHtmlDocument(analysis) {
  const slidesFromSummary = analysis.riassunto.slice(0, 5).map((sentence, index) => `
    <section class="slide">
      <span>Step ${index + 1}</span>
      <h2>Punto chiave</h2>
      <p>${escapeHtml(sentence)}</p>
    </section>
  `).join("\n");

  const slidesFromCards = analysis.cards.slice(0, 4).map(card => `
    <section class="slide">
      <span>Ripasso</span>
      <h2>${escapeHtml(card.fronte)}</h2>
      <p>${escapeHtml(card.retro)}</p>
    </section>
  `).join("\n");

  return `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Minicorso RAG - ${escapeHtml(analysis.titolo)}</title>
<style>
body{margin:0;background:radial-gradient(circle at top,#312e81,#020617 65%);color:#f8fafc;font-family:Arial,sans-serif}
main{max-width:1040px;margin:0 auto;padding:42px 20px}
.slide{min-height:210px;margin:22px 0;border-radius:28px;padding:30px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.16);box-shadow:0 24px 70px rgba(0,0,0,.35)}
.slide span{color:#a5b4fc;font-weight:900;text-transform:uppercase;letter-spacing:.08em}.slide h2{font-size:30px}.slide p{font-size:19px;line-height:1.6}
</style>
</head>
<body>
<main>
<h1>Minicorso interattivo generato dal documento</h1>
<p>${escapeHtml(analysis.titolo)}</p>
${slidesFromSummary}
${slidesFromCards}
</main>
</body>
</html>`;
}

function makeReportMarkdown(analysis) {
  return `# Report RAG - ${analysis.titolo}

- Generato il: ${analysis.generato_il}
- File originale: ${analysis.file_originale}
- Caratteri estratti: ${analysis.statistiche.caratteri}
- Parole utili: ${analysis.statistiche.parole}
- Frasi analizzate: ${analysis.statistiche.frasi}
- Parole chiave: ${analysis.statistiche.parole_chiave}
- Card generate: ${analysis.statistiche.card}
- Domande quiz generate: ${analysis.statistiche.quiz}
`;
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
    files["cards.html"] = makeCardsHtmlDocument(analysis);
    files["cards.json"] = JSON.stringify(analysis.cards, null, 2);
  }

  if (selectedOutputs.has("quiz")) {
    files["quiz_interattivo.html"] = makeQuizHtmlDocument(analysis);
    files["quiz.json"] = JSON.stringify(analysis.quiz, null, 2);
  }

  if (selectedOutputs.has("minicourse")) {
    files["minicorso_interattivo.html"] = makeMiniCourseHtmlDocument(analysis);
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
    setStatus("Seleziona almeno un output da scaricare.", "error");
    return;
  }

  if (!window.JSZip) {
    downloadBlob(`${slug}-output-rag.json`, JSON.stringify(files, null, 2), "application/json;charset=utf-8");
    return;
  }

  const zip = new JSZip();
  const folder = zip.folder(`output-rag-${slug}`);

  Object.entries(files).forEach(([filename, content]) => {
    folder.file(filename, content);
  });

  const blob = await zip.generateAsync({ type: "blob" });
  downloadBlob(`output-rag-${slug}.zip`, blob, "application/zip");
}

function renderDownloadPanel(analysis, selectedOutputs) {
  const files = makeDownloadPackage(analysis, selectedOutputs);
  const fileButtons = Object.keys(files).map(filename => {
    return `<button type="button" class="single-download-button" data-download-file="${escapeHtml(filename)}">Scarica ${escapeHtml(filename)}</button>`;
  }).join("");

  return `
    <section class="panel">
      <h2>Scarica output</h2>
      <p>
        I file vengono scaricati nella cartella Download del browser.
        Su Mac di solito è <strong>Download</strong>; su smartphone è nella cartella Download/File.
        Per scegliere ogni volta dove salvarli, attiva l'opzione del browser “Chiedi dove salvare ogni file”.
      </p>
      <div class="download-grid">
        <button type="button" id="downloadSelectedZip">Scarica ZIP con output selezionati</button>
        ${fileButtons}
      </div>
    </section>
  `;
}

function renderOutput(analysis, selectedOutputs) {
  const sections = [];

  if (selectedOutputs.has("summary")) {
    const summaryHtml = analysis.riassunto.map(sentence => `<li>${escapeHtml(sentence)}</li>`).join("");
    sections.push(`
      <section class="panel">
        <h2>Riassunto leggibile</h2>
        <ol>${summaryHtml}</ol>
      </section>
    `);
  }

  if (selectedOutputs.has("tables")) {
    const tableHtml = analysis.tabella_concetti.map(row => `
      <tr>
        <td>${escapeHtml(row.concetto)}</td>
        <td>${row.frequenza}</td>
        <td>${row.importanza}/5</td>
        <td>${escapeHtml(row.spiegazione)}</td>
      </tr>
    `).join("");

    sections.push(`
      <section class="panel">
        <h2>Tabella concetti</h2>
        <div class="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Concetto</th>
                <th>Frequenza</th>
                <th>Importanza</th>
                <th>Spiegazione</th>
              </tr>
            </thead>
            <tbody>${tableHtml}</tbody>
          </table>
        </div>
      </section>
    `);
  }

  if (selectedOutputs.has("cards")) {
    const cardsHtml = analysis.cards.map(card => `
      <article class="mini-card">
        <h3>${escapeHtml(card.fronte)}</h3>
        <p>${escapeHtml(card.retro)}</p>
      </article>
    `).join("");

    sections.push(`
      <section class="panel">
        <h2>Card di ripasso</h2>
        <div class="cards-grid">${cardsHtml}</div>
      </section>
    `);
  }

  if (selectedOutputs.has("quiz")) {
    const quizHtml = analysis.quiz.map((item, questionIndex) => `
      <article class="quiz-card">
        <h3>${questionIndex + 1}. ${escapeHtml(item.domanda)}</h3>
        ${item.opzioni.map((option, optionIndex) => `
          <button class="quiz-option" data-correct="${option === item.risposta_corretta ? "true" : "false"}">
            ${String.fromCharCode(65 + optionIndex)}. ${escapeHtml(option)}
          </button>
        `).join("")}
        <p class="quiz-explanation">${escapeHtml(item.spiegazione)}</p>
      </article>
    `).join("");

    sections.push(`
      <section class="panel">
        <h2>Quiz interattivo</h2>
        ${quizHtml}
      </section>
    `);
  }

  if (selectedOutputs.has("minicourse")) {
    sections.push(`
      <section class="panel">
        <h2>Minicorso</h2>
        <p>Il minicorso è pronto come file scaricabile HTML.</p>
      </section>
    `);
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
    zipButton.addEventListener("click", () => downloadSelectedZip(analysis, selectedOutputs));
  }

  const files = makeDownloadPackage(analysis, selectedOutputs);
  document.querySelectorAll("[data-download-file]").forEach(button => {
    button.addEventListener("click", () => {
      const filename = button.dataset.downloadFile;
      const content = files[filename];

      if (!content) {
        setStatus(`File non trovato: ${filename}`, "error");
        return;
      }

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
    setStatus("Seleziona prima un file TXT, PDF o Markdown.", "error");
    return;
  }

  if (!selectedOutputs.size) {
    setStatus("Seleziona almeno una cosa da generare: riassunto, tabelle, card, quiz o minicorso.", "error");
    return;
  }

  try {
    setStatus("Analisi in corso. Il motore sta generando solo gli output selezionati...", "info");

    const rawText = await readUploadedFile(file);
    const cleanedText = cleanText(rawText);

    if (cleanedText.length < 120) {
      throw new Error("Testo estratto troppo corto. Il PDF potrebbe essere scansionato come immagine.");
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
    setStatus("✅ Output selezionati generati. Ora puoi scaricarli con i pulsanti sotto.", "success");
  } catch (error) {
    setStatus(`❌ ${error.message}`, "error");
  }
});
