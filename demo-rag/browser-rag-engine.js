const RAG_STOPWORDS = new Set([
  "che", "con", "per", "del", "della", "dello", "delle", "degli", "dei",
  "alla", "allo", "alle", "agli", "una", "uno", "anche", "sono", "non",
  "nel", "nella", "nelle", "negli", "questo", "questa", "questi", "queste",
  "come", "piu", "più", "viene", "essere", "può", "puo", "quindi", "tra",
  "fra", "gli", "sul", "sulla", "dai", "dal", "dalle", "ad", "ed"
]);

const fileInput = document.getElementById("fileInput");
const titleInput = document.getElementById("titleInput");
const generateButton = document.getElementById("generateButton");
const statusBox = document.getElementById("statusBox");
const outputBox = document.getElementById("outputBox");

if (window.pdfjsLib) {
  pdfjsLib.GlobalWorkerOptions.workerSrc =
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
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

function makeIndexHtmlDocument(analysis) {
  return `<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Output RAG - ${escapeHtml(analysis.titolo)}</title>
<style>
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:#020617;color:#f8fafc}
main{max-width:1080px;margin:0 auto;padding:42px 20px 70px}
.hero{border:1px solid rgba(255,255,255,.14);border-radius:30px;background:rgba(15,23,42,.88);padding:32px;box-shadow:0 24px 80px rgba(0,0,0,.34);margin-bottom:22px}
h1{margin:0 0 12px;font-size:clamp(34px,5vw,56px);line-height:1.04}
p{color:#cbd5e1;line-height:1.6}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(235px,1fr));gap:16px}
.card{display:flex;flex-direction:column;gap:10px;padding:22px;border-radius:24px;border:1px solid rgba(255,255,255,.14);background:linear-gradient(145deg,rgba(124,58,237,.26),rgba(15,23,42,.95));color:#fff;text-decoration:none;min-height:126px}
.card strong{font-size:20px}.card span{color:#cbd5e1;font-weight:800}
</style>
</head>
<body>
<main>
<section class="hero">
<h1>Output generati dal motore RAG</h1>
<p>Documento: <strong>${escapeHtml(analysis.titolo)}</strong></p>
<p>Apri prima il riassunto leggibile, poi quiz, minicorso e card.</p>
</section>
<section class="grid">
<a class="card" href="riassunto.html"><strong>Riassunto leggibile</strong><span>riassunto.html</span></a>
<a class="card" href="quiz_interattivo.html"><strong>Quiz interattivo</strong><span>quiz_interattivo.html</span></a>
<a class="card" href="minicorso_interattivo.html"><strong>Minicorso interattivo</strong><span>minicorso_interattivo.html</span></a>
<a class="card" href="cards.html"><strong>Card di ripasso</strong><span>cards.html</span></a>
</section>
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

## File scaricabili

- index.html
- riassunto.html
- riassunto.md
- tabelle_concetti.md
- tabelle_concetti.csv
- cards.html
- cards.json
- quiz_interattivo.html
- quiz.json
- minicorso_interattivo.html
- analisi_completa.json
- statistiche.json
- report_rag.md
`;
}

function makeDownloadPackage(analysis) {
  const files = {
    "index.html": makeIndexHtmlDocument(analysis),
    "riassunto.html": makeSummaryHtmlDocument(analysis),
    "riassunto.md": makeSummaryMarkdown(analysis),
    "tabelle_concetti.md": makeConceptTableMarkdown(analysis),
    "tabelle_concetti.csv": makeConceptTableCsv(analysis),
    "cards.html": makeCardsHtmlDocument(analysis),
    "cards.json": JSON.stringify(analysis.cards, null, 2),
    "quiz_interattivo.html": makeQuizHtmlDocument(analysis),
    "quiz.json": JSON.stringify(analysis.quiz, null, 2),
    "minicorso_interattivo.html": makeMiniCourseHtmlDocument(analysis),
    "analisi_completa.json": JSON.stringify(analysis, null, 2),
    "statistiche.json": JSON.stringify(analysis.statistiche, null, 2),
    "report_rag.md": makeReportMarkdown(analysis)
  };

  return files;
}

async function downloadAllAsZip(analysis) {
  const files = makeDownloadPackage(analysis);
  const slug = slugify(analysis.titolo);

  if (!window.JSZip) {
    const fallbackName = `${slug}-pacchetto-rag.json`;
    downloadBlob(fallbackName, JSON.stringify(files, null, 2), "application/json;charset=utf-8");
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

function renderDownloadPanel(analysis) {
  return `
    <section class="panel">
      <h2>Scarica output</h2>
      <p>Puoi scaricare tutto in un unico ZIP oppure scaricare i singoli file principali.</p>
      <div class="download-grid">
        <button id="downloadZip">Scarica tutto in ZIP</button>
        <button id="downloadIndexHtml">Scarica index.html</button>
        <button id="downloadSummaryHtml">Scarica riassunto.html</button>
        <button id="downloadSummaryMd">Scarica riassunto.md</button>
        <button id="downloadTableMd">Scarica tabelle_concetti.md</button>
        <button id="downloadTableCsv">Scarica tabelle_concetti.csv</button>
        <button id="downloadCardsHtml">Scarica cards.html</button>
        <button id="downloadCardsJson">Scarica cards.json</button>
        <button id="downloadQuizHtml">Scarica quiz_interattivo.html</button>
        <button id="downloadQuizJson">Scarica quiz.json</button>
        <button id="downloadMiniCourseHtml">Scarica minicorso_interattivo.html</button>
        <button id="downloadFullJson">Scarica analisi_completa.json</button>
        <button id="downloadStatsJson">Scarica statistiche.json</button>
        <button id="downloadReportMd">Scarica report_rag.md</button>
      </div>
    </section>
  `;
}

function attachDownloadHandlers(analysis) {
  const files = makeDownloadPackage(analysis);

  const mapping = {
    downloadIndexHtml: ["index.html", "text/html;charset=utf-8"],
    downloadSummaryHtml: ["riassunto.html", "text/html;charset=utf-8"],
    downloadSummaryMd: ["riassunto.md", "text/markdown;charset=utf-8"],
    downloadTableMd: ["tabelle_concetti.md", "text/markdown;charset=utf-8"],
    downloadTableCsv: ["tabelle_concetti.csv", "text/csv;charset=utf-8"],
    downloadCardsHtml: ["cards.html", "text/html;charset=utf-8"],
    downloadCardsJson: ["cards.json", "application/json;charset=utf-8"],
    downloadQuizHtml: ["quiz_interattivo.html", "text/html;charset=utf-8"],
    downloadQuizJson: ["quiz.json", "application/json;charset=utf-8"],
    downloadMiniCourseHtml: ["minicorso_interattivo.html", "text/html;charset=utf-8"],
    downloadFullJson: ["analisi_completa.json", "application/json;charset=utf-8"],
    downloadStatsJson: ["statistiche.json", "application/json;charset=utf-8"],
    downloadReportMd: ["report_rag.md", "text/markdown;charset=utf-8"]
  };

  const zipButton = document.getElementById("downloadZip");
  if (zipButton) {
    zipButton.addEventListener("click", () => downloadAllAsZip(analysis));
  }

  Object.entries(mapping).forEach(([buttonId, [filename, mimeType]]) => {
    const button = document.getElementById(buttonId);
    if (!button) return;

    button.addEventListener("click", () => {
      downloadBlob(filename, files[filename], mimeType);
    });
  });
}

function renderOutput(analysis) {
  const summaryHtml = analysis.riassunto.map(sentence => `<li>${escapeHtml(sentence)}</li>`).join("");
  const tableHtml = analysis.tabella_concetti.map(row => `
      <tr>
        <td>${escapeHtml(row.concetto)}</td>
        <td>${row.frequenza}</td>
        <td>${row.importanza}/5</td>
        <td>${escapeHtml(row.spiegazione)}</td>
      </tr>
    `).join("");

  const cardsHtml = analysis.cards.map(card => `
      <article class="mini-card">
        <h3>${escapeHtml(card.fronte)}</h3>
        <p>${escapeHtml(card.retro)}</p>
      </article>
    `).join("");

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

  outputBox.innerHTML = `
    <section class="panel">
      <h2>Riassunto leggibile</h2>
      <ol>${summaryHtml}</ol>
    </section>

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

    <section class="panel">
      <h2>Card di ripasso</h2>
      <div class="cards-grid">${cardsHtml}</div>
    </section>

    <section class="panel">
      <h2>Quiz interattivo</h2>
      ${quizHtml}
    </section>

    ${renderDownloadPanel(analysis)}
  `;

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

  attachDownloadHandlers(analysis);
}

generateButton.addEventListener("click", async () => {
  const file = fileInput.files[0];

  if (!file) {
    setStatus("Seleziona prima un file TXT, PDF o Markdown.", "error");
    return;
  }

  try {
    setStatus("Analisi in corso. Il motore sta estraendo testo, riassunto, tabelle, card e quiz...", "info");

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

    renderOutput(analysis);
    setStatus("✅ Output generati correttamente nella demo. Puoi leggerli e scaricarli.", "success");
  } catch (error) {
    setStatus(`❌ ${error.message}`, "error");
  }
});
