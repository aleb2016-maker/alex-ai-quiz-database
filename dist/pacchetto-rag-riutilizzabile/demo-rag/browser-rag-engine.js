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
    setStatus("✅ Output generati correttamente nella demo.", "success");
  } catch (error) {
    setStatus(`❌ ${error.message}`, "error");
  }
});
