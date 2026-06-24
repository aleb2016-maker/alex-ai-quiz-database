const sourceText = document.getElementById("sourceText");
const fileInput = document.getElementById("fileInput");
const cleanButton = document.getElementById("cleanButton");
const generateButton = document.getElementById("generateButton");
const printButton = document.getElementById("printButton");
const clearButton = document.getElementById("clearButton");

const startPageInput = document.getElementById("startPageInput");
const endPageInput = document.getElementById("endPageInput");
const chunkSizeInput = document.getElementById("chunkSizeInput");
const maxCardsInput = document.getElementById("maxCardsInput");

const stats = document.getElementById("stats");
const fileStatus = document.getElementById("fileStatus");
const output = document.getElementById("output");
const documentTitle = document.getElementById("documentTitle");
const documentSubtitle = document.getElementById("documentSubtitle");
const qualityBox = document.getElementById("qualityBox");
const summaryBox = document.getElementById("summaryBox");
const cardsBox = document.getElementById("cardsBox");
const questionsBox = document.getElementById("questionsBox");

const PDFJS_URL = "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.mjs";
const PDFJS_WORKER_URL = "https://cdn.jsdelivr.net/npm/pdfjs-dist@4.10.38/build/pdf.worker.mjs";

let pdfjsLibPromise = null;
let normalPageTitle = "Riassunto pulito";

const stopWords = new Set([
  "che", "con", "per", "una", "uno", "del", "della", "delle", "degli", "dei",
  "nel", "nella", "nelle", "sul", "sulla", "sono", "come", "anche", "più",
  "meno", "tra", "fra", "gli", "all", "alla", "alle", "dai", "dal", "dallo",
  "questo", "questa", "questi", "quelle", "quello", "essere", "avere",
  "viene", "vengono", "può", "possono", "deve", "devono", "ogni", "molto",
  "dopo", "prima", "quando", "dove", "quindi", "perché", "suo", "sua",
  "loro", "oppure", "cioè", "non", "ma", "siano", "stata", "stato",
  "tutti", "tutte", "altro", "altra", "altri", "altre", "puoi"
]);

const weakWords = new Set([
  "solo", "utile", "finale", "frasi", "frase", "pagina", "pagine", "sezioni",
  "sezione", "testo", "documento", "documenti", "domande", "domanda", "studio",
  "card", "riassunto", "riassunti", "motore", "blocchi", "blocco", "cosa",
  "parte", "parti", "materiale", "risultato", "risultati", "persona", "argomento"
]);

const badTitleWords = new Set([
  "trasformare", "leggere", "dividerlo", "dividere", "individuare", "generare",
  "mantenere", "creare", "spiegare", "studiare", "contenere", "evitare",
  "perdere", "serve", "permette", "vuole", "sensati", "esteso", "facili",
  "velocemente", "ripetitive", "importanti", "secondari", "ordinato"
]);

const accentReplacements = new Map([
  ["e'", "è"], ["E'", "È"],
  ["perche'", "perché"], ["Perche'", "Perché"],
  ["poiche'", "poiché"], ["Poiche'", "Poiché"],
  ["finche'", "finché"], ["Finche'", "Finché"],
  ["affinche'", "affinché"], ["Affinche'", "Affinché"],
  ["puo'", "può"], ["Puo'", "Può"],
  ["piu'", "più"], ["Piu'", "Più"],
  ["gia'", "già"], ["Gia'", "Già"],
  ["cosi'", "così"], ["Cosi'", "Così"],
  ["cioe'", "cioè"], ["Cioe'", "Cioè"],
  ["pero'", "però"], ["Pero'", "Però"],
  ["sara'", "sarà"], ["Sara'", "Sarà"],
  ["fara'", "farà"], ["Fara'", "Farà"],
  ["qualita'", "qualità"], ["Qualita'", "Qualità"],
  ["attivita'", "attività"], ["Attivita'", "Attività"],
  ["capacita'", "capacità"], ["Capacita'", "Capacità"],
  ["realta'", "realtà"], ["Realta'", "Realtà"],
  ["utilita'", "utilità"], ["Utilita'", "Utilità"],
  ["velocita'", "velocità"], ["Velocita'", "Velocità"],
  ["possibilita'", "possibilità"], ["Possibilita'", "Possibilità"],
  ["difficolta'", "difficoltà"], ["Difficolta'", "Difficoltà"],
  ["percio'", "perciò"], ["Percio'", "Perciò"],
  ["puo’", "può"], ["piu’", "più"], ["perche’", "perché"], ["e’", "è"]
]);

const conceptRules = [
  {
    title: "Motore RAG per documenti lunghi",
    article: "il motore RAG per documenti lunghi",
    patterns: ["motore rag per documenti lunghi", "rag per documenti lunghi", "documenti lunghi"]
  },
  {
    title: "Divisione in blocchi RAG",
    article: "la divisione in blocchi RAG",
    patterns: ["divisione in blocchi", "blocchi rag", "dividere in blocchi", "blocchi sensati"]
  },
  {
    title: "Concetti principali",
    article: "i concetti principali",
    patterns: ["concetti principali", "individuare i concetti", "concetti più importanti"]
  },
  {
    title: "Parole chiave",
    article: "le parole chiave",
    patterns: ["parole chiave", "keyword"]
  },
  {
    title: "Riassunto ordinato",
    article: "un riassunto ordinato",
    patterns: ["riassunto ideale", "riassunti più ordinati", "riassunto ordinato", "riassunto", "riassunti"]
  },
  {
    title: "Card riassuntive",
    article: "le card riassuntive",
    patterns: ["card riassuntive", "card", "schede visive", "schede di ripasso"]
  },
  {
    title: "Domande studio",
    article: "le domande studio",
    patterns: ["domande studio", "domanda aiuta", "risposta nascosta"]
  },
  {
    title: "PDF finale leggibile",
    article: "un PDF finale leggibile",
    patterns: ["pdf finale", "salva il pdf", "stampa", "pdf"]
  },
  {
    title: "Contenuti facili da studiare",
    article: "i contenuti facili da studiare",
    patterns: ["contenuti facili da studiare", "facili da studiare", "studiare velocemente"]
  },
  {
    title: "Parti importanti e dettagli secondari",
    article: "le parti importanti e i dettagli secondari",
    patterns: ["parti importanti", "dettagli secondari", "sezioni ripetitive"]
  },
  {
    title: "Mini corso interattivo",
    article: "un mini corso interattivo",
    patterns: ["mini corso", "mini lezione", "corso interattivo"]
  },
  {
    title: "Caricamento PDF",
    article: "il caricamento PDF",
    patterns: ["caricamento pdf", "caricare pdf", "lettura pdf"]
  },
  {
    title: "Controllo qualità del testo",
    article: "il controllo qualità del testo",
    patterns: ["qualità del testo", "controllo qualità", "testo pulito"]
  },
  {
    title: "OCR per scansioni",
    article: "l'OCR per le scansioni",
    patterns: ["ocr", "scansioni", "pdf scansionati"]
  }
];

function setFileStatus(message, type = "") {
  fileStatus.className = `file-status ${type}`.trim();
  fileStatus.textContent = message;
}

function yieldToBrowser() {
  return new Promise(resolve => setTimeout(resolve, 0));
}

async function loadPdfJs() {
  if (!pdfjsLibPromise) {
    pdfjsLibPromise = import(PDFJS_URL).then(module => {
      module.GlobalWorkerOptions.workerSrc = PDFJS_WORKER_URL;
      return module;
    });
  }

  return pdfjsLibPromise;
}

async function extractTextFromPdf(file) {
  setFileStatus("Caricamento libreria PDF e lettura del file...", "warn");

  const pdfjsLib = await loadPdfJs();
  const arrayBuffer = await file.arrayBuffer();
  const loadingTask = pdfjsLib.getDocument({ data: arrayBuffer });
  const pdf = await loadingTask.promise;

  const totalPages = pdf.numPages;
  const startPage = Math.max(1, Number(startPageInput.value || 1));
  const requestedEnd = Number(endPageInput.value || totalPages);
  const endPage = Math.min(totalPages, Math.max(startPage, requestedEnd));

  const pageTexts = [];

  for (let pageNumber = startPage; pageNumber <= endPage; pageNumber += 1) {
    setFileStatus(
      `Estrazione testo PDF: pagina ${pageNumber} di ${endPage} ` +
      `(PDF totale: ${totalPages} pagine)...`,
      "warn"
    );

    const page = await pdf.getPage(pageNumber);
    const textContent = await page.getTextContent();

    const items = textContent.items
      .map(item => item.str)
      .filter(Boolean);

    pageTexts.push(`\n\n--- Pagina ${pageNumber} ---\n\n${items.join(" ")}`);

    if (pageNumber % 3 === 0) {
      await yieldToBrowser();
    }
  }

  const extracted = cleanText(pageTexts.join("\n\n"));

  if (extracted.length < 80) {
    throw new Error("Il PDF sembra composto da immagini/scansioni: serve OCR, non semplice estrazione testo.");
  }

  return {
    text: extracted,
    pagesRead: endPage - startPage + 1,
    totalPages,
    startPage,
    endPage
  };
}

function fixItalianAccents(text) {
  let output = text;

  for (const [bad, good] of accentReplacements.entries()) {
    output = output.split(bad).join(good);
  }

  return output;
}

function fixAcronyms(text) {
  return text
    .replace(/\brag\b/gi, "RAG")
    .replace(/\bpdf\b/gi, "PDF")
    .replace(/\bocr\b/gi, "OCR");
}

function cleanText(text) {
  return fixItalianGrammarText(fixAcronyms(fixItalianAccents(text)))
    .replace(/\r/g, "\n")
    .replace(/[ \t]+/g, " ")
    .replace(/\n{3,}/g, "\n\n")
    .replace(/([a-zàèéìòù])-\n([a-zàèéìòù])/gi, "$1$2")
    .replace(/\n(?=[a-zàèéìòù])/gi, " ")
    .replace(/--- Pagina \d+ ---/g, match => `\n\n${match}\n\n`)
    .replace(/\s+([,.!?;:])/g, "$1")
    .replace(/([,.!?;:])([A-Za-zÀ-ÿ])/g, "$1 $2")
    .trim();
}

function splitSentences(text) {
  return cleanText(text)
    .replace(/--- Pagina \d+ ---/g, " ")
    .split(/(?<=[.!?])\s+|\n+/)
    .map(sentence => sentence.trim())
    .filter(sentence => sentence.length > 35);
}

function getWords(text) {
  return text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/)
    .filter(word => word.length > 3 && !stopWords.has(word));
}

function keywordScores(text) {
  const scores = new Map();

  for (const word of getWords(text)) {
    if (weakWords.has(word) || badTitleWords.has(word)) {
      continue;
    }

    scores.set(word, (scores.get(word) || 0) + 1);
  }

  return scores;
}

function topKeywords(text, limit = 12) {
  return [...keywordScores(text).entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, limit)
    .map(item => item[0]);
}

function getConceptRuleByTitle(title) {
  return conceptRules.find(rule => rule.title.toLowerCase() === title.toLowerCase());
}

function conceptForQuestion(title) {
  const rule = getConceptRuleByTitle(title);
  return applyPrepositionToConcept("", rule ? rule.article : addSimpleArticle(title));
}

function addSimpleArticle(title) {
  const lower = title.toLowerCase();

  if (lower.startsWith("pdf") || lower.startsWith("un pdf")) {
    return `un ${fixAcronyms(lower)}`;
  }

  if (lower.startsWith("rag")) {
    return `il ${fixAcronyms(lower)}`;
  }

  if (lower.endsWith("e") || lower.endsWith("i")) {
    return `i ${lower}`;
  }

  return `il ${lower}`;
}

function conceptIsPlural(title) {
  const rule = getConceptRuleByTitle(title);
  const article = rule ? rule.article.toLowerCase() : addSimpleArticle(title).toLowerCase();

  return article.startsWith("i ") ||
    article.startsWith("gli ") ||
    article.startsWith("le ");
}

function conceptSubject(title) {
  const rule = getConceptRuleByTitle(title);
  return applyPrepositionToConcept("", rule ? rule.article : addSimpleArticle(title));
}

function conceptWithPreposition(preposition, title) {
  const rule = getConceptRuleByTitle(title);
  const article = rule ? rule.article : addSimpleArticle(title);
  return applyPrepositionToConcept(preposition, article);
}

function applyPrepositionToConcept(preposition, articlePhrase) {
  const phrase = fixAcronyms(articlePhrase.trim());
  const lower = phrase.toLowerCase();
  const restAfter = prefix => phrase.slice(prefix.length);

  if (!preposition) {
    return phrase;
  }

  if (preposition === "su") {
    if (lower.startsWith("il ")) return `sul ${restAfter("il ")}`;
    if (lower.startsWith("lo ")) return `sullo ${restAfter("lo ")}`;
    if (lower.startsWith("la ")) return `sulla ${restAfter("la ")}`;
    if (lower.startsWith("l'")) return `sull'${restAfter("l'")}`;
    if (lower.startsWith("i ")) return `sui ${restAfter("i ")}`;
    if (lower.startsWith("gli ")) return `sugli ${restAfter("gli ")}`;
    if (lower.startsWith("le ")) return `sulle ${restAfter("le ")}`;
    return `su ${phrase}`;
  }

  if (preposition === "di") {
    if (lower.startsWith("il ")) return `del ${restAfter("il ")}`;
    if (lower.startsWith("lo ")) return `dello ${restAfter("lo ")}`;
    if (lower.startsWith("la ")) return `della ${restAfter("la ")}`;
    if (lower.startsWith("l'")) return `dell'${restAfter("l'")}`;
    if (lower.startsWith("i ")) return `dei ${restAfter("i ")}`;
    if (lower.startsWith("gli ")) return `degli ${restAfter("gli ")}`;
    if (lower.startsWith("le ")) return `delle ${restAfter("le ")}`;
    return `di ${phrase}`;
  }

  return `${preposition} ${phrase}`;
}

function fixItalianGrammarText(text) {
  return fixAcronyms(text)
    .replace(/\bsu il\b/gi, "sul")
    .replace(/\bsu lo\b/gi, "sullo")
    .replace(/\bsu la\b/gi, "sulla")
    .replace(/\bsu i\b/gi, "sui")
    .replace(/\bsu gli\b/gi, "sugli")
    .replace(/\bsu le\b/gi, "sulle")
    .replace(/\bdi il\b/gi, "del")
    .replace(/\bdi lo\b/gi, "dello")
    .replace(/\bdi la\b/gi, "della")
    .replace(/\bdi i\b/gi, "dei")
    .replace(/\bdi gli\b/gi, "degli")
    .replace(/\bdi le\b/gi, "delle")
    .replace(/\ba il\b/gi, "al")
    .replace(/\ba lo\b/gi, "allo")
    .replace(/\ba la\b/gi, "alla")
    .replace(/\ba i\b/gi, "ai")
    .replace(/\ba gli\b/gi, "agli")
    .replace(/\ba le\b/gi, "alle")
    .replace(/\bin il\b/gi, "nel")
    .replace(/\bin lo\b/gi, "nello")
    .replace(/\bin la\b/gi, "nella")
    .replace(/\bin i\b/gi, "nei")
    .replace(/\bin gli\b/gi, "negli")
    .replace(/\bin le\b/gi, "nelle")
    .replace(/\bLe card riassuntive è importante\b/gi, "Le card riassuntive sono importanti")
    .replace(/\bLe domande studio è importante\b/gi, "Le domande studio sono importanti")
    .replace(/\bLe parole chiave è importante\b/gi, "Le parole chiave sono importanti")
    .replace(/\bI concetti principali è importante\b/gi, "I concetti principali sono importanti")
    .replace(/\bI contenuti facili da studiare è importante\b/gi, "I contenuti facili da studiare sono importanti")
    .replace(/\s+/g, " ")
    .trim();
}

function uniqueCleanSentences(sentences, limit) {
  const selected = [];
  const seen = new Set();

  for (const sentence of sentences) {
    const cleaned = cleanSentenceForOutput(sentence);
    const words = getWords(cleaned).slice(0, 10);
    const key = words.join(" ");

    if (!cleaned || key.length < 8 || seen.has(key)) {
      continue;
    }

    seen.add(key);
    selected.push(cleaned);

    if (selected.length >= limit) {
      break;
    }
  }

  return selected;
}

function detectConceptFromSentence(sentence) {
  const lower = sentence.toLowerCase();

  for (const rule of conceptRules) {
    if (rule.patterns.some(pattern => lower.includes(pattern))) {
      return rule.title;
    }
  }

  return "";
}

function fallbackConceptFromSentence(sentence) {
  const words = getWords(sentence)
    .filter(word => !weakWords.has(word) && !badTitleWords.has(word));

  if (words.length < 2) {
    return "";
  }

  const pairs = [];

  for (let i = 0; i < words.length - 1; i += 1) {
    const pair = [words[i], words[i + 1]];

    if (pair.every(word => !weakWords.has(word) && !badTitleWords.has(word))) {
      pairs.push(pair.join(" "));
    }
  }

  if (pairs.length === 0) {
    return "";
  }

  const best = pairs.find(pair => pair.length >= 12) || pairs[0];

  return titleCase(best);
}

function topConcepts(text, limit = 14) {
  const sentences = splitSentences(text);
  const selected = [];
  const seen = new Set();

  for (const rule of conceptRules) {
    const lower = text.toLowerCase();

    if (rule.patterns.some(pattern => lower.includes(pattern))) {
      selected.push(rule.title);
      seen.add(rule.title.toLowerCase());
    }

    if (selected.length >= limit) {
      return selected;
    }
  }

  for (const sentence of sentences) {
    const concept = detectConceptFromSentence(sentence) || fallbackConceptFromSentence(sentence);

    if (!concept) {
      continue;
    }

    const key = concept.toLowerCase();

    if (seen.has(key)) {
      continue;
    }

    seen.add(key);
    selected.push(concept);

    if (selected.length >= limit) {
      break;
    }
  }

  if (selected.length < 4) {
    const keywords = topKeywords(text, 10);

    for (let i = 0; i < keywords.length - 1 && selected.length < limit; i += 2) {
      selected.push(titleCase(`${keywords[i]} ${keywords[i + 1]}`));
    }
  }

  return selected;
}

function sentenceScore(sentence, scores, concepts) {
  const words = getWords(sentence);

  if (words.length === 0) {
    return 0;
  }

  const total = words.reduce((sum, word) => sum + (scores.get(word) || 0), 0);
  const lower = sentence.toLowerCase();
  const conceptBonus = concepts.some(concept => lower.includes(concept.toLowerCase().split(" ")[0])) ? 4 : 0;
  const lengthPenalty = sentence.length > 320 ? 0.72 : sentence.length < 70 ? 0.82 : 1;

  return ((total / Math.sqrt(words.length)) + conceptBonus) * lengthPenalty;
}

function bestSentences(text, limit) {
  const sentences = splitSentences(text);
  const scores = keywordScores(text);
  const concepts = topConcepts(text, 18);
  const seen = new Set();

  return sentences
    .map((sentence, index) => ({
      sentence,
      index,
      score: sentenceScore(sentence, scores, concepts)
    }))
    .sort((a, b) => b.score - a.score)
    .filter(item => {
      const fingerprint = getWords(item.sentence).slice(0, 8).join(" ");
      if (seen.has(fingerprint)) {
        return false;
      }

      seen.add(fingerprint);
      return true;
    })
    .slice(0, limit)
    .sort((a, b) => a.index - b.index)
    .map(item => item.sentence);
}

function chunkText(text, maxWords = 850) {
  const paragraphs = cleanText(text)
    .split(/\n{2,}/)
    .map(paragraph => paragraph.trim())
    .filter(Boolean);

  const chunks = [];
  let current = [];
  let currentWords = 0;

  for (const paragraph of paragraphs) {
    const count = paragraph.split(/\s+/).filter(Boolean).length;

    if (currentWords + count > maxWords && current.length > 0) {
      chunks.push(current.join("\n\n"));
      current = [];
      currentWords = 0;
    }

    current.push(paragraph);
    currentWords += count;
  }

  if (current.length > 0) {
    chunks.push(current.join("\n\n"));
  }

  return chunks.length > 0 ? chunks : [text];
}

function cleanSentenceForOutput(sentence) {
  return fixItalianGrammarText(
    fixAcronyms(fixItalianAccents(sentence))
      .replace(/\s+/g, " ")
      .replace(/\b(Domande studio con risposte)\s+Le domande studio/gi, "Le domande studio")
      .replace(/\b(Card riassuntive)\s+Le card riassuntive/gi, "Le card riassuntive")
      .replace(/\b(Divisione in blocchi RAG)\s+La divisione in blocchi RAG/gi, "La divisione in blocchi RAG")
      .replace(/\b(Motore RAG per documenti lunghi)\s+Il motore RAG/gi, "Il motore RAG")
      .replace(/\b(Riassunto ordinato)\s+Il riassunto/gi, "Il riassunto")
      .trim()
  );
}

function cleanAnswerForOutput(answer, concept) {
  let cleaned = cleanSentenceForOutput(answer);
  const conceptRegex = new RegExp(`^${escapeRegExp(concept)}\\s+`, "i");
  cleaned = cleaned.replace(conceptRegex, "");

  for (const rule of conceptRules) {
    const ruleRegex = new RegExp(`^${escapeRegExp(rule.title)}\\s+`, "i");
    cleaned = cleaned.replace(ruleRegex, "");
  }

  cleaned = cleaned
    .replace(/^Le card riassuntive Le card riassuntive/gi, "Le card riassuntive")
    .replace(/^La divisione in blocchi RAG La divisione in blocchi RAG/gi, "La divisione in blocchi RAG")
    .replace(/^Il motore RAG Il motore RAG/gi, "Il motore RAG")
    .replace(/^PDF finale leggibile Nel PDF/gi, "Nel PDF")
    .replace(/^Parole chiave Ogni blocco/gi, "Ogni blocco")
    .replace(/^Domande studio Le domande studio/gi, "Le domande studio")
    .replace(/^Riassunto ordinato Il riassunto/gi, "Il riassunto")
    .replace(/^Card riassuntive Le card/gi, "Le card")
    .trim();

  cleaned = fixItalianGrammarText(cleaned);

  return cleaned.charAt(0).toUpperCase() + cleaned.slice(1);
}

function escapeRegExp(text) {
  return text.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function makeOverview(sentences) {
  return uniqueCleanSentences(sentences, 4).join(" ");
}

function makeSummary(text) {
  const chunkSize = Number(chunkSizeInput.value || 850);
  const chunks = chunkText(text, chunkSize);
  const concepts = topConcepts(text, 14);
  const globalBest = bestSentences(text, 7);

  const chunkSummaries = chunks.map((chunk, index) => {
    const localBest = uniqueCleanSentences(bestSentences(chunk, 5), 3);
    const localConcept = topConcepts(chunk, 1)[0] || concepts[index] || `Parte ${index + 1}`;

    return {
      title: `Parte ${index + 1} - ${localConcept}`,
      sentences: localBest
    };
  });

  return {
    chunks,
    concepts,
    overview: makeOverview(globalBest),
    chunkSummaries
  };
}

function makeCards(text, summaryData) {
  const maxCards = Number(maxCardsInput.value || 6);
  const sentences = bestSentences(text, maxCards * 4).map(cleanSentenceForOutput);
  const cards = [];
  const usedTitles = new Set();

  for (const concept of summaryData.concepts) {
    if (cards.length >= maxCards) {
      break;
    }

    if (!concept || isBadConcept(concept)) {
      continue;
    }

    const titleKey = concept.toLowerCase();
    if (usedTitles.has(titleKey)) {
      continue;
    }

    const rawAnswer = findBestAnswerForConcept(concept, sentences) ||
      sentences[cards.length] ||
      summaryData.overview;

    const answer = cleanAnswerForOutput(rawAnswer, concept);

    usedTitles.add(titleKey);

    cards.push({
      title: `${cards.length + 1}. ${concept}`,
      text: answer,
      badge: cards.length % 3 === 0 ? "Concetto chiave" : cards.length % 3 === 1 ? "Applicazione pratica" : "Da ricordare",
      icon: makeCardIcon(cards.length)
    });
  }

  return cards;
}

function isBadConcept(concept) {
  const lower = concept.toLowerCase();
  const words = lower.split(/\s+/);

  if (words.length === 1 && weakWords.has(words[0])) {
    return true;
  }

  return words.some(word => badTitleWords.has(word)) && words.length > 2;
}

function makeCardIcon(index) {
  const icons = [
    `<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="45" fill="#dcfce7"/><path d="M38 63l14 14 31-37" fill="none" stroke="#15803d" stroke-width="10" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    `<svg viewBox="0 0 120 120" aria-hidden="true"><rect x="24" y="24" width="72" height="72" rx="18" fill="#dbeafe"/><path d="M42 42h36M42 60h36M42 78h22" stroke="#2563eb" stroke-width="8" stroke-linecap="round"/></svg>`,
    `<svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="46" fill="#fef3c7"/><path d="M60 28v36l24 14" stroke="#d97706" stroke-width="9" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>`,
    `<svg viewBox="0 0 120 120" aria-hidden="true"><path d="M60 18l43 25v34l-43 25-43-25V43z" fill="#fce7f3"/><path d="M39 62h42M60 41v42" stroke="#be185d" stroke-width="9" stroke-linecap="round"/></svg>`,
    `<svg viewBox="0 0 120 120" aria-hidden="true"><rect x="21" y="30" width="78" height="60" rx="14" fill="#ede9fe"/><path d="M38 49h44M38 64h32M38 79h20" stroke="#7c3aed" stroke-width="7" stroke-linecap="round"/></svg>`
  ];

  return icons[index % icons.length];
}

function makeStudyQuestions(text, summaryData) {
  const concepts = summaryData.concepts.slice(0, 8);
  const sentences = bestSentences(text, 24).map(cleanSentenceForOutput);
  const questions = [];
  const usedQuestions = new Set();

  for (let index = 0; index < concepts.length && questions.length < 8; index += 1) {
    const concept = concepts[index];

    if (!concept || isBadConcept(concept)) {
      continue;
    }

    const subject = conceptSubject(concept);
    const suConcept = conceptWithPreposition("su", concept);
    const diConcept = conceptWithPreposition("di", concept);
    const isPlural = conceptIsPlural(concept);
    const importantPhrase = isPlural ? "sono importanti" : "è importante";
    const usePhrase = isPlural ? "si usano" : "si usa";

    const rawAnswer = findBestAnswerForConcept(concept, sentences) || sentences[index] || summaryData.overview;
    const answer = cleanAnswerForOutput(rawAnswer, concept);

    const templates = [
      `Che cosa bisogna ricordare ${suConcept}?`,
      `Perché ${subject} ${importantPhrase} nel documento?`,
      `Come ${usePhrase} ${subject} nella pratica?`,
      `Qual è il vantaggio principale ${diConcept}?`
    ];

    const question = fixItalianGrammarText(templates[questions.length % templates.length]);
    const questionKey = question.toLowerCase();

    if (usedQuestions.has(questionKey)) {
      continue;
    }

    usedQuestions.add(questionKey);

    questions.push({
      question,
      answer
    });
  }

  return questions;
}

function findBestAnswerForConcept(concept, sentences) {
  const mainWords = concept
    .toLowerCase()
    .split(/\s+/)
    .filter(word => word.length > 3 && !weakWords.has(word));

  return sentences.find(sentence => {
    const lower = sentence.toLowerCase();
    return mainWords.some(word => lower.includes(word));
  });
}

function titleCase(text) {
  return fixAcronyms(text)
    .split(/\s+/)
    .filter(Boolean)
    .map((word, index) => {
      if (["RAG", "PDF", "OCR"].includes(word.toUpperCase())) {
        return word.toUpperCase();
      }

      const lower = word.toLowerCase();
      return index === 0 ? capitalize(lower) : lower;
    })
    .join(" ");
}

function capitalize(text) {
  if (!text) {
    return "";
  }

  return text.charAt(0).toUpperCase() + text.slice(1);
}

function estimateTitle(summaryData) {
  const concepts = summaryData.concepts.slice(0, 3);

  if (concepts.length === 0) {
    return "Riassunto intelligente";
  }

  return `Riassunto su ${concepts.join(", ")}`;
}

function qualityReport(originalText, cleanedText, summaryData, cards, questions) {
  const apostropheAccentCount = (originalText.match(/\b\w+'/g) || []).length;
  const answersForPrint = questions.length;
  const repeatedCardTitles = cards.length - new Set(cards.map(card => card.title.toLowerCase())).size;

  return {
    accentsFixed: apostropheAccentCount,
    repeatedTitles: repeatedCardTitles,
    concepts: summaryData.concepts.length,
    chunks: summaryData.chunks.length,
    cards: cards.length,
    questions: questions.length,
    answersForPrint,
    words: cleanedText.split(/\s+/).filter(Boolean).length
  };
}

function updateStats(text) {
  const cleaned = cleanText(text);
  const words = cleaned ? cleaned.split(/\s+/).filter(Boolean).length : 0;
  const chars = cleaned.length;
  const chunkSize = Number(chunkSizeInput.value || 850);
  const chunks = cleaned ? chunkText(cleaned, chunkSize).length : 0;
  const concepts = cleaned ? topConcepts(cleaned, 8).length : 0;

  stats.innerHTML = `
    <strong>Statistiche:</strong>
    ${words} parole · ${chars} caratteri · ${chunks} blocchi RAG stimati · ${concepts} concetti principali stimati
  `;
}

function renderQuality(report) {
  qualityBox.innerHTML = `
    <article class="quality-card">
      <strong>${report.words}</strong>
      <span>parole lette</span>
    </article>
    <article class="quality-card">
      <strong>${report.chunks}</strong>
      <span>blocchi RAG</span>
    </article>
    <article class="quality-card">
      <strong>${report.concepts}</strong>
      <span>concetti estratti</span>
    </article>
    <article class="quality-card">
      <strong>${report.answersForPrint}</strong>
      <span>risposte visibili nel PDF</span>
    </article>
  `;
}

function renderSummary(summaryData) {
  summaryBox.innerHTML = "";

  const globalSection = document.createElement("div");
  globalSection.className = "summary-section";
  globalSection.innerHTML = `
    <h3>Quadro generale</h3>
    <p>${summaryData.overview}</p>
  `;
  summaryBox.appendChild(globalSection);

  const conceptsSection = document.createElement("div");
  conceptsSection.className = "summary-section";
  conceptsSection.innerHTML = `
    <h3>Concetti principali</h3>
    <p>${summaryData.concepts.slice(0, 10).join(" · ")}</p>
  `;
  summaryBox.appendChild(conceptsSection);

  for (const chunkSummary of summaryData.chunkSummaries) {
    const section = document.createElement("div");
    section.className = "summary-section";

    section.innerHTML = `
      <h3>${chunkSummary.title}</h3>
      <ul>
        ${chunkSummary.sentences.map(sentence => `<li>${sentence}</li>`).join("")}
      </ul>
    `;

    summaryBox.appendChild(section);
  }
}

function renderCards(cards) {
  cardsBox.innerHTML = "";

  for (const card of cards) {
    const node = document.createElement("article");
    node.className = "study-card";

    node.innerHTML = `
      ${card.icon}
      <div class="card-badge">◆ ${card.badge}</div>
      <h3>${card.title}</h3>
      <p>${card.text}</p>
    `;

    cardsBox.appendChild(node);
  }
}

function renderQuestions(questions) {
  questionsBox.innerHTML = "";

  for (const [index, item] of questions.entries()) {
    const node = document.createElement("article");
    node.className = "question-card";

    node.innerHTML = `
      <h3>${index + 1}. ${item.question}</h3>
      <details>
        <summary>Mostra risposta suggerita</summary>
        <p>${item.answer}</p>
      </details>
      <div class="answer-for-print">
        <strong>Risposta:</strong>
        <p>${item.answer}</p>
      </div>
    `;

    questionsBox.appendChild(node);
  }
}

function generateAll() {
  const original = sourceText.value;
  const cleaned = cleanText(original);

  if (cleaned.length < 300) {
    alert("Inserisci o carica un testo più lungo: questo motore serve per documenti veri, non per poche righe.");
    return;
  }

  sourceText.value = cleaned;
  updateStats(cleaned);

  const summaryData = makeSummary(cleaned);
  const cards = makeCards(cleaned, summaryData);
  const questions = makeStudyQuestions(cleaned, summaryData);
  const report = qualityReport(original, cleaned, summaryData, cards, questions);

  documentTitle.textContent = estimateTitle(summaryData);
  documentSubtitle.textContent = `${report.words} parole · ${report.chunks} blocchi RAG · ${report.cards} card · ${report.questions} domande studio con risposte nel PDF`;

  renderQuality(report);
  renderSummary(summaryData);
  renderCards(cards);
  renderQuestions(questions);

  output.classList.remove("hidden");
  output.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function handleFile(file) {
  if (!file) {
    return;
  }

  output.classList.add("hidden");
  summaryBox.innerHTML = "";
  cardsBox.innerHTML = "";
  questionsBox.innerHTML = "";

  const fileName = file.name || "file";
  const lowerName = fileName.toLowerCase();

  try {
    if (file.type === "application/pdf" || lowerName.endsWith(".pdf")) {
      const result = await extractTextFromPdf(file);
      sourceText.value = result.text;
      updateStats(result.text);
      setFileStatus(
        `PDF caricato: ${fileName}. Pagine lette: ${result.pagesRead} ` +
        `(${result.startPage}-${result.endPage}) su ${result.totalPages}. Testo estratto correttamente.`,
        "ok"
      );
      return;
    }

    const text = await file.text();
    sourceText.value = cleanText(text);
    updateStats(sourceText.value);
    setFileStatus(`File caricato: ${fileName}. Testo pronto.`, "ok");
  } catch (error) {
    console.error(error);
    setFileStatus(`Errore lettura file: ${error.message}`, "error");
  }
}

function openCleanPrintDialog() {
  const oldTitle = document.title;
  normalPageTitle = oldTitle;

  document.title = "";

  window.addEventListener("afterprint", () => {
    document.title = normalPageTitle || "Riassunto pulito";
  }, { once: true });

  setTimeout(() => window.print(), 250);
}

fileInput.addEventListener("change", async event => {
  const file = event.target.files[0];
  await handleFile(file);
});

cleanButton.addEventListener("click", () => {
  sourceText.value = cleanText(sourceText.value);
  updateStats(sourceText.value);
  setFileStatus("Testo ripulito con motore qualità V4.2.", "ok");
});

generateButton.addEventListener("click", generateAll);

printButton.addEventListener("click", () => {
  if (output.classList.contains("hidden")) {
    generateAll();
  }

  openCleanPrintDialog();
});

clearButton.addEventListener("click", () => {
  sourceText.value = "";
  summaryBox.innerHTML = "";
  cardsBox.innerHTML = "";
  questionsBox.innerHTML = "";
  qualityBox.innerHTML = "";
  stats.innerHTML = "";
  output.classList.add("hidden");
  fileInput.value = "";
  setFileStatus("Nessun file caricato. Puoi incollare testo oppure selezionare un PDF.");
});

sourceText.addEventListener("input", () => updateStats(sourceText.value));
[startPageInput, endPageInput, chunkSizeInput, maxCardsInput].forEach(input => {
  input.addEventListener("input", () => updateStats(sourceText.value));
});
