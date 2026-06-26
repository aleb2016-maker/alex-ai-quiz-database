(function () {
  let currentData = null;
  let pasteTimer = null;

  const $ = (id) => document.getElementById(id);

  const STOPWORDS = new Set([
    "il","lo","la","i","gli","le","un","una","uno","di","a","da","in","con","su","per","tra","fra",
    "che","e","o","ma","anche","come","più","meno","molto","nel","nella","nelle","nei","del","della",
    "delle","dei","al","alla","alle","ai","si","non","sono","essere","può","possono","deve","devono",
    "usare","fare","viene","vengono","questo","questa","questi","quelle","quelli","ogni","quando","dopo",
    "prima","sul","sulla","documento","parte","testo","cosa","quale","qual","perché","dati","account"
  ]);

  const IMPORTANT_CONCEPTS = [
    { key: "password manager", label: "Password manager", match: ["password manager", "gestore password"] },
    { key: "password", label: "Password sicure", match: ["password", "credenziali"] },
    { key: "autenticazione a due fattori", label: "Autenticazione a due fattori", match: ["2fa", "due fattori", "autenticazione a due fattori"] },
    { key: "phishing", label: "Phishing", match: ["phishing", "link sospetti", "mittente", "email"] },
    { key: "malware", label: "Malware", match: ["malware", "software dannoso", "allegati pericolosi"] },
    { key: "ransomware", label: "Ransomware", match: ["ransomware", "bloccare l'accesso", "bloccare accesso"] },
    { key: "backup", label: "Backup regolari", match: ["backup", "copie", "ripristino"] },
    { key: "aggiornamenti", label: "Aggiornamenti software", match: ["aggiornare", "aggiornamenti", "sistema operativo", "applicazioni"] },
    { key: "wifi", label: "Rete Wi‑Fi protetta", match: ["wi-fi", "wifi", "rete", "crittografia"] },
    { key: "privilegi", label: "Privilegi amministrativi", match: ["privilegi", "amministrativi", "permessi"] },
    { key: "protezione dati", label: "Protezione dei dati", match: ["proteggere dati", "protezione dei dati", "dati riservati"] }
  ];

  function setStatus(message, type = "") {
    const box = $("statusBox");
    box.textContent = message;
    box.classList.remove("ok", "error");
    if (type) box.classList.add(type);
  }

  function escapeHtml(value) {
    return String(value || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;");
  }

  function normalizeText(text) {
    return String(text || "")
      .replace(/\r\n/g, "\n")
      .replace(/\r/g, "\n")
      .replace(/[“”]/g, '"')
      .replace(/[’]/g, "'")
      .replace(/\uFFFD/g, "")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .replace(/ +([,.;:!?])/g, "$1")
      .replace(/([,.;:!?])([A-Za-zÀ-ÿ])/g, "$1 $2")
      .trim();
  }

  function tokens(text) {
    return (String(text || "").toLowerCase().match(/[a-zà-ÿ0-9]{3,}/g) || [])
      .filter((t) => !STOPWORDS.has(t) && !/^\d+$/.test(t));
  }

  function splitSentences(text) {
    return normalizeText(text)
      .split(/(?<=[.!?])\s+/)
      .map((s) => s.trim())
      .filter((s) => s.split(/\s+/).length >= 6)
      .map((s) => /[.!?]$/.test(s) ? s : s + ".");
  }

  function splitChunks(text, target = 2600) {
    const paragraphs = normalizeText(text).split(/\n+/).filter(Boolean);
    const chunks = [];
    let current = "";
    for (const paragraph of paragraphs) {
      if ((current + " " + paragraph).length > target && current) {
        chunks.push(current.trim());
        current = paragraph;
      } else {
        current += (current ? " " : "") + paragraph;
      }
    }
    if (current.trim()) chunks.push(current.trim());
    return chunks.length ? chunks : [normalizeText(text)];
  }

  function findSentenceForConcept(sentences, concept) {
    const matches = concept.match.map((m) => m.toLowerCase());
    const found = sentences.find((s) => matches.some((m) => s.toLowerCase().includes(m)));
    return found || "";
  }

  function fallbackKeywords(text, limit = 8) {
    const counts = new Map();
    tokens(text).forEach((t) => counts.set(t, (counts.get(t) || 0) + 1));
    return [...counts.entries()]
      .sort((a, b) => b[1] - a[1])
      .map(([word]) => word)
      .filter((word) => !["deve", "devono", "usare", "fare", "dati", "account", "sicurezza"].includes(word))
      .slice(0, limit);
  }

  function shortText(text, max = 210) {
    const clean = normalizeText(text);
    if (clean.length <= max) return clean;
    const cut = clean.slice(0, max);
    const lastSpace = cut.lastIndexOf(" ");
    return (lastSpace > 120 ? cut.slice(0, lastSpace) : cut).trim() + "…";
  }

  function buildSummary(sentences, keywords) {
    const keywordSet = new Set(keywords.map((k) => k.toLowerCase()));
    const scored = sentences.map((sentence) => {
      const score = tokens(sentence).filter((t) => keywordSet.has(t)).length;
      return { score, sentence };
    }).filter((item) => item.score > 0);
    scored.sort((a, b) => b.score - a.score || a.sentence.length - b.sentence.length);
    const selected = [];
    const seen = new Set();
    for (const item of scored) {
      const sig = item.sentence.toLowerCase().slice(0, 90);
      if (seen.has(sig)) continue;
      seen.add(sig);
      selected.push(item.sentence);
      if (selected.length >= 8) break;
    }
    return selected.length ? selected : sentences.slice(0, 8);
  }

  function buildDataFromText(rawText, title = "Documento di studio") {
    const text = normalizeText(rawText);
    const chunks = splitChunks(text);
    const allSentences = splitSentences(text);
    const matchedConcepts = IMPORTANT_CONCEPTS.map((concept) => ({
      ...concept,
      sentence: findSentenceForConcept(allSentences, concept)
    })).filter((concept) => concept.sentence);

    const fallback = fallbackKeywords(text, 10);
    const concepts = [...matchedConcepts];
    for (const word of fallback) {
      if (concepts.length >= 10) break;
      if (concepts.some((c) => c.key === word || c.label.toLowerCase().includes(word))) continue;
      const sentence = allSentences.find((s) => s.toLowerCase().includes(word));
      if (!sentence) continue;
      concepts.push({ key: word, label: word.charAt(0).toUpperCase() + word.slice(1), match: [word], sentence });
    }

    const keywords = [...new Set([...concepts.map((c) => c.key), ...fallback])].slice(0, 14);
    const summarySentences = buildSummary(allSentences, keywords);
    const cards = concepts.slice(0, 10).map((concept, index) => ({
      id: "card-" + String(index + 1).padStart(2, "0"),
      titolo: concept.label,
      keyword: concept.key,
      testo: shortText(concept.sentence, 230),
      frase_originale: concept.sentence,
      esempio: buildExample(concept.key),
      tags: [concept.key]
    }));

    return {
      title,
      text,
      chunks: chunks.map((chunk, index) => ({ id: "blocco-" + String(index + 1).padStart(3, "0"), text: chunk, keywords: fallbackKeywords(chunk, 10) })),
      summary: {
        idea: summarySentences[0] || "Documento analizzato.",
        points: summarySentences.slice(0, 6),
        details: summarySentences.slice(6, 9),
        keywords
      },
      cards
    };
  }

  function buildExample(keyword) {
    const k = String(keyword || "").toLowerCase();
    if (k.includes("password manager")) return "Esempio: salva password lunghe e uniche, ricordando solo la password principale.";
    if (k.includes("password")) return "Esempio: usa una password diversa per ogni servizio importante.";
    if (k.includes("fattori") || k.includes("2fa")) return "Esempio: oltre alla password, confermi l’accesso con un codice o una notifica.";
    if (k.includes("phishing")) return "Esempio: controlla mittente, link e tono del messaggio prima di cliccare.";
    if (k.includes("malware")) return "Esempio: non aprire allegati inattesi e mantieni aggiornati i sistemi.";
    if (k.includes("backup")) return "Esempio: conserva copie periodiche dei file importanti in un luogo separato.";
    if (k.includes("wifi")) return "Esempio: usa password forte e crittografia sulla rete di casa o ufficio.";
    return "Esempio: collega questo punto a un caso pratico descritto nel documento.";
  }

  function iconSvg(keyword) {
    const k = String(keyword || "").toLowerCase();
    if (k.includes("password manager")) return svgBase("manager");
    if (k.includes("password")) return svgBase("lock");
    if (k.includes("fattori") || k.includes("2fa")) return svgBase("shield");
    if (k.includes("phishing")) return svgBase("hook");
    if (k.includes("malware") || k.includes("ransomware")) return svgBase("bug");
    if (k.includes("backup")) return svgBase("cloud");
    if (k.includes("wifi")) return svgBase("wifi");
    if (k.includes("privilegi")) return svgBase("key");
    if (k.includes("dati") || k.includes("protezione")) return svgBase("database");
    return svgBase("note");
  }

  function svgBase(type) {
    const common = 'viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg"';
    const bg = '<defs><linearGradient id="g" x1="0" x2="1"><stop stop-color="#39e7b1"/><stop offset="1" stop-color="#4ecbff"/></linearGradient></defs><rect width="100" height="100" rx="28" fill="url(#g)" opacity="0.22"/>';
    const stroke = 'stroke="#eaffff" stroke-width="7" stroke-linecap="round" stroke-linejoin="round" fill="none"';
    const fill = 'fill="#39e7b1"';
    const map = {
      lock: `${bg}<rect x="26" y="43" width="48" height="34" rx="8" ${stroke}/><path d="M34 43V32c0-10 7-17 16-17s16 7 16 17v11" ${stroke}/><circle cx="50" cy="60" r="5" ${fill}/>`,
      manager: `${bg}<rect x="18" y="24" width="64" height="52" rx="12" ${stroke}/><path d="M30 40h40M30 55h28" ${stroke}/><circle cx="69" cy="57" r="7" ${fill}/>`,
      shield: `${bg}<path d="M50 15l30 12v22c0 19-12 31-30 39-18-8-30-20-30-39V27z" ${stroke}/><path d="M38 51l8 8 18-21" ${stroke}/>`,
      hook: `${bg}<path d="M66 20c-12 8-18 17-18 29v10c0 9-7 16-16 16-6 0-11-3-14-8" ${stroke}/><path d="M66 20l11 13" ${stroke}/><circle cx="32" cy="75" r="6" ${fill}/>`,
      bug: `${bg}<ellipse cx="50" cy="55" rx="21" ry="25" ${stroke}/><path d="M35 32l-9-10M65 32l9-10M25 53H13M87 53H75M29 75l-12 9M71 75l12 9" ${stroke}/><path d="M50 32v48" ${stroke}/>`,
      cloud: `${bg}<path d="M30 68h42c9 0 16-7 16-16s-7-16-16-16h-2C66 25 56 18 44 21S25 33 25 45c-8 2-13 8-13 16s8 7 18 7z" ${stroke}/><path d="M50 44v22M39 55l11-11 11 11" ${stroke}/>`,
      wifi: `${bg}<path d="M20 39c18-16 42-16 60 0M33 53c10-9 24-9 34 0M45 67c3-3 7-3 10 0" ${stroke}/><circle cx="50" cy="78" r="5" ${fill}/>`,
      key: `${bg}<circle cx="36" cy="50" r="15" ${stroke}/><path d="M51 50h31M66 50v12M76 50v-10" ${stroke}/>`,
      database: `${bg}<ellipse cx="50" cy="29" rx="27" ry="12" ${stroke}/><path d="M23 29v40c0 7 12 12 27 12s27-5 27-12V29M23 49c0 7 12 12 27 12s27-5 27-12" ${stroke}/>`,
      note: `${bg}<path d="M27 20h40l12 12v48H27z" ${stroke}/><path d="M67 20v14h14M37 46h28M37 60h22" ${stroke}/>`
    };
    return `<svg ${common}>${map[type] || map.note}</svg>`;
  }

  function renderSummary(data) {
    $("summarySection").hidden = false;
    const s = data.summary;
    $("summaryOutput").innerHTML = `
      <div class="summary-card wide">
        <h3>Idea centrale</h3>
        <p>${escapeHtml(s.idea)}</p>
      </div>
      <div class="summary-card">
        <h3>Punti principali</h3>
        <ul>${s.points.map((p) => `<li>${escapeHtml(p)}</li>`).join("")}</ul>
      </div>
      <div class="summary-card">
        <h3>Concetti chiave</h3>
        <div class="keyword-row">${s.keywords.map((k) => `<span class="keyword-pill">${escapeHtml(k)}</span>`).join("")}</div>
      </div>`;
  }

  function renderCards(data) {
    $("cardsSection").hidden = false;
    $("cardsOutput").innerHTML = data.cards.map((card) => `
      <article class="study-card">
        <div class="card-illustration">${iconSvg(card.keyword)}</div>
        <h3>${escapeHtml(card.titolo)}</h3>
        <p>${escapeHtml(card.testo)}</p>
        <span class="card-tag">${escapeHtml(card.esempio)}</span>
      </article>`).join("");
  }

  function renderAll(data) {
    currentData = data;
    renderSummary(data);
    renderCards(data);
    $("qaSection").hidden = false;
    $("btnScaricaTxt").disabled = false;
    $("btnScaricaPdf").disabled = false;
    setStatus(`Analisi completata: ${data.chunks.length} blocchi, ${data.cards.length} card, riassunto e interrogazione pronti.`, "ok");
    $("summarySection").scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function extractPdfText(file) {
    if (!window.pdfjsLib) throw new Error("Lettore PDF non caricato. Riprova o usa TXT/MD.");
    if (window.pdfjsLib.GlobalWorkerOptions) {
      window.pdfjsLib.GlobalWorkerOptions.workerSrc = "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js";
    }
    const buffer = await file.arrayBuffer();
    const pdf = await window.pdfjsLib.getDocument({ data: buffer }).promise;
    const parts = [];
    for (let pageNumber = 1; pageNumber <= pdf.numPages; pageNumber++) {
      setStatus(`Estraggo testo PDF: pagina ${pageNumber} di ${pdf.numPages}...`);
      const page = await pdf.getPage(pageNumber);
      const content = await page.getTextContent();
      const pageText = content.items.map((item) => item.str || "").join(" ");
      parts.push(`Pagina ${pageNumber}\n${pageText}`);
      await new Promise((resolve) => setTimeout(resolve, 0));
    }
    return parts.join("\n\n");
  }

  async function loadFile(file) {
    try {
      setStatus(`Carico ${file.name}...`);
      let text = "";
      if (file.type === "application/pdf" || file.name.toLowerCase().endsWith(".pdf")) {
        text = await extractPdfText(file);
      } else {
        text = await file.text();
      }
      text = normalizeText(text);
      $("documentText").value = text;
      if (text.split(/\s+/).length < 20) throw new Error("Testo troppo corto o PDF senza testo leggibile.");
      setStatus("Documento caricato. Analisi automatica in corso...");
      setTimeout(() => renderAll(buildDataFromText(text, file.name.replace(/\.[^.]+$/, ""))), 100);
    } catch (err) {
      setStatus(err.message || String(err), "error");
    }
  }

  function autoAnalyzePastedText() {
    const text = normalizeText($("documentText").value);
    if (text.split(/\s+/).length < 60) return;
    setStatus("Testo incollato rilevato. Analisi automatica in corso...");
    renderAll(buildDataFromText(text));
  }

  function scoreChunk(questionTokens, chunk) {
    const chunkTokens = new Set([...(chunk.keywords || []), ...tokens(chunk.text)]);
    let score = 0;
    questionTokens.forEach((t) => { if (chunkTokens.has(t)) score += 1; });
    return score;
  }

  function answerQuestion() {
    if (!currentData) {
      $("answerOutput").textContent = "Carica prima un documento.";
      return;
    }
    const question = normalizeText($("questionInput").value);
    if (!question) {
      $("answerOutput").textContent = "Scrivi una domanda sul documento.";
      return;
    }
    const qTokens = new Set(tokens(question));
    const ranked = currentData.chunks
      .map((chunk) => ({ chunk, score: scoreChunk(qTokens, chunk) }))
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score);

    if (!ranked.length) {
      $("answerOutput").innerHTML = "Non ho trovato una risposta abbastanza sicura nel documento caricato.";
      return;
    }

    const candidateSentences = [];
    ranked.slice(0, 3).forEach(({ chunk }) => {
      splitSentences(chunk.text).forEach((sentence) => {
        const sentenceTokens = new Set(tokens(sentence));
        let score = 0;
        qTokens.forEach((t) => { if (sentenceTokens.has(t)) score += 1; });
        if (score > 0) candidateSentences.push({ sentence, score, id: chunk.id });
      });
    });
    candidateSentences.sort((a, b) => b.score - a.score || a.sentence.length - b.sentence.length);
    const chosen = candidateSentences.slice(0, 3);
    const answer = chosen.map((item) => item.sentence).join(" ");
    const example = buildExample([...qTokens][0] || "");
    $("answerOutput").innerHTML = `
      <strong>Risposta:</strong>
      <p>${escapeHtml(answer)}</p>
      <strong>Esempio sintetico:</strong>
      <p>${escapeHtml(example)}</p>
      <div class="source">Fonte interna: ${[...new Set(chosen.map((item) => item.id))].join(", ")}</div>`;
  }

  function buildTextExport() {
    if (!currentData) return "";
    const lines = [];
    lines.push("RAG Documento Studio V4.4");
    lines.push("");
    lines.push("RIASSUNTO");
    lines.push(currentData.summary.idea);
    lines.push("");
    currentData.summary.points.forEach((p, i) => lines.push(`${i + 1}. ${p}`));
    lines.push("");
    lines.push("CARD");
    currentData.cards.forEach((card, i) => {
      lines.push(`${i + 1}. ${card.titolo}`);
      lines.push(card.testo);
      lines.push(card.esempio);
      lines.push("");
    });
    return lines.join("\n");
  }

  function downloadText() {
    if (!currentData) return;
    const blob = new Blob([buildTextExport()], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "rag-documento-studio-v44.txt";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  }

  async function downloadPdf() {
    if (!currentData) {
      setStatus("Prima carica un documento.", "error");
      return;
    }
    if (!window.AlexBrowserPdfExportV6 || !window.AlexBrowserPdfExportV6.exportSectionsToPdf) {
      setStatus("Motore PDF V6 non disponibile.", "error");
      return;
    }
    setStatus("Genero PDF pulito con motore V6...");
    await window.AlexBrowserPdfExportV6.exportSectionsToPdf({
      title: currentData.title || "RAG Documento Studio V4.4",
      filename: "rag-documento-studio-v44.pdf"
    });
    setStatus("PDF generato con motore V6.", "ok");
  }

  $("btnCaricaFile").addEventListener("click", () => $("fileInput").click());
  $("fileInput").addEventListener("change", (event) => {
    const file = event.target.files && event.target.files[0];
    if (file) loadFile(file);
  });
  $("documentText").addEventListener("input", () => {
    clearTimeout(pasteTimer);
    pasteTimer = setTimeout(autoAnalyzePastedText, 900);
  });
  $("btnScaricaTxt").addEventListener("click", downloadText);
  $("btnScaricaPdf").addEventListener("click", downloadPdf);
  $("btnInterroga").addEventListener("click", answerQuestion);
  $("questionInput").addEventListener("keydown", (event) => {
    if (event.key === "Enter") answerQuestion();
  });
})();
