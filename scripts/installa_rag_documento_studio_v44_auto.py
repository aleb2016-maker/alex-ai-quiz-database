#!/usr/bin/env python3
from pathlib import Path
import argparse
import textwrap


def write(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"OK scritto: {path}")

HTML = r'''
<!doctype html>
<html lang="it">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>RAG Documento Studio V4.4</title>
  <link rel="stylesheet" href="/demo-rag/rag-documento-studio-v44.css">
</head>
<body>
  <main class="page-shell">
    <section class="hero">
      <p class="eyebrow">RAG DOCUMENTO STUDIO V4.4</p>
      <h1>Carica un documento e genera materiale di studio</h1>
      <p class="hero-text">Carichi TXT/PDF, il testo viene pulito automaticamente e ottieni riassunto, card colorate e risposte alle domande sul documento.</p>
    </section>

    <section class="work-panel no-pdf">
      <div class="main-actions" aria-label="Azioni principali">
        <button id="btnCaricaFile" class="big-btn file" type="button">Carica TXT/PDF</button>
        <button id="btnScaricaTxt" class="big-btn download" type="button" disabled>Scarica TXT</button>
        <button id="btnScaricaPdf" class="big-btn download" type="button" disabled>Scarica PDF</button>
      </div>

      <input id="fileInput" type="file" hidden accept=".txt,.md,.pdf,text/plain,text/markdown,application/pdf">
      <div id="statusBox" class="status-box">Pronto. Carica un file TXT/PDF oppure incolla testo: l’analisi parte automaticamente.</div>

      <label class="input-label" for="documentText">Testo documento</label>
      <textarea id="documentText" spellcheck="false" placeholder="Incolla qui un documento lungo: dopo pochi secondi verrà analizzato automaticamente..."></textarea>
    </section>

    <section id="pdfRoot" class="output-root">
      <article id="summarySection" class="output-section pdf-export-group" hidden>
        <div class="section-header">
          <p class="eyebrow">RIASSUNTO</p>
          <h2>Riassunto pulito</h2>
        </div>
        <div id="summaryOutput" class="summary-box"></div>
      </article>

      <article id="cardsSection" class="output-section pdf-export-group" hidden>
        <div class="section-header">
          <p class="eyebrow">CARD</p>
          <h2>Card colorate con disegni</h2>
        </div>
        <div id="cardsOutput" class="cards-grid"></div>
      </article>
    </section>

    <section id="qaSection" class="output-section qa-section no-pdf" hidden>
      <div class="section-header">
        <p class="eyebrow">INTERROGA IL DOCUMENTO</p>
        <h2>Fai una domanda sul testo</h2>
      </div>
      <div class="qa-controls">
        <input id="questionInput" type="text" placeholder="Esempio: perché sono importanti i backup?">
        <button id="btnInterroga" class="small-btn" type="button">Rispondi dal documento</button>
      </div>
      <div id="answerOutput" class="answer-box">Carica prima un documento, poi scrivi una domanda.</div>
    </section>
  </main>

  <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
  <script src="/runtime/web/card-graphic-engine.js"></script>
  <script src="/demo-rag/pdf-export-browser-v6.js"></script>
  <script src="/demo-rag/rag-documento-studio-v44.js"></script>
</body>
</html>
'''

CSS = r'''
:root {
  color-scheme: dark;
  --bg: #07111f;
  --panel: rgba(15, 27, 46, 0.94);
  --panel2: rgba(11, 20, 35, 0.96);
  --line: rgba(157, 181, 214, 0.24);
  --text: #eef6ff;
  --muted: #a9b8cc;
  --green: #39e7b1;
  --cyan: #4ecbff;
  --yellow: #ffd166;
  --red: #ff7a7a;
  --shadow: 0 24px 70px rgba(0,0,0,.34);
}
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background:
    radial-gradient(circle at 18% 0%, rgba(57, 231, 177, 0.12), transparent 34%),
    radial-gradient(circle at 88% 6%, rgba(78, 203, 255, 0.14), transparent 34%),
    linear-gradient(180deg, #08111f 0%, #07111f 100%);
  color: var(--text);
}
.page-shell { width: min(1440px, calc(100% - 64px)); margin: 0 auto; padding: 40px 0 80px; }
.hero, .work-panel, .output-section {
  border: 1px solid var(--line);
  border-radius: 28px;
  background: linear-gradient(145deg, rgba(15,27,46,.95), rgba(8,15,28,.96));
  box-shadow: var(--shadow);
}
.hero { padding: 54px 40px; margin-bottom: 22px; }
.eyebrow { margin: 0 0 14px; color: var(--green); font-weight: 900; letter-spacing: .22em; text-transform: uppercase; font-size: 13px; }
h1 { margin: 0; max-width: 980px; font-size: clamp(44px, 6vw, 82px); line-height: .96; letter-spacing: -.055em; }
h2 { margin: 0; font-size: clamp(28px, 3vw, 44px); letter-spacing: -.035em; }
h3 { margin: 0 0 12px; font-size: 22px; }
.hero-text { margin: 26px 0 0; color: var(--muted); font-size: 22px; max-width: 960px; }
.work-panel { padding: 28px; margin-bottom: 24px; }
.main-actions {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 1fr));
  gap: 16px;
  margin-bottom: 18px;
}
.big-btn, .small-btn {
  border: 1px solid rgba(255,255,255,.16);
  border-radius: 20px;
  color: #06121e;
  font-weight: 950;
  font-size: 17px;
  padding: 20px 24px;
  cursor: pointer;
  min-height: 64px;
  box-shadow: 0 14px 34px rgba(0,0,0,.22);
}
.big-btn.file { background: linear-gradient(135deg, var(--green), var(--cyan)); }
.big-btn.download { background: linear-gradient(135deg, #6ee7ff, #37e3b0); }
.big-btn:disabled { cursor: not-allowed; opacity: .42; filter: grayscale(.4); }
.small-btn { min-height: 54px; padding: 14px 18px; background: linear-gradient(135deg, var(--green), var(--cyan)); }
.status-box {
  border: 1px solid var(--line);
  border-radius: 18px;
  background: rgba(255,255,255,.045);
  color: var(--muted);
  padding: 16px 18px;
  margin-bottom: 18px;
  font-weight: 750;
}
.status-box.ok { color: var(--green); }
.status-box.error { color: var(--red); }
.input-label { display: block; margin: 0 0 10px; color: var(--muted); font-weight: 900; }
textarea {
  width: 100%; min-height: 230px; resize: vertical;
  border: 1px solid var(--line); border-radius: 22px;
  background: rgba(2,8,18,.78); color: var(--text);
  font-size: 18px; line-height: 1.6; padding: 22px;
  outline: none;
}
.output-root { display: grid; gap: 24px; }
.output-section { padding: 34px; margin-bottom: 24px; }
.section-header { margin-bottom: 24px; }
.summary-box { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.summary-card {
  border: 1px solid var(--line); border-radius: 24px;
  background: rgba(255,255,255,.045); padding: 24px;
}
.summary-card.wide { grid-column: 1 / -1; }
.summary-card p, .summary-card li { color: #dceaff; line-height: 1.65; font-size: 17px; }
.summary-card ul { margin: 0; padding-left: 22px; }
.keyword-row { display: flex; flex-wrap: wrap; gap: 10px; }
.keyword-pill { border: 1px solid var(--line); border-radius: 999px; padding: 8px 12px; color: var(--green); background: rgba(57,231,177,.08); font-weight: 900; }
.cards-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 18px; }
.study-card {
  position: relative; overflow: hidden; min-height: 310px;
  border: 1px solid rgba(255,255,255,.16); border-radius: 30px;
  padding: 24px; background: linear-gradient(145deg, #123251, #0d1e34);
  box-shadow: 0 18px 46px rgba(0,0,0,.28);
}
.study-card::after {
  content: ""; position: absolute; right: -42px; top: -42px; width: 170px; height: 170px;
  border-radius: 45px; transform: rotate(16deg); background: rgba(255,255,255,.11);
}
.card-illustration { position: relative; z-index: 1; width: 82px; height: 82px; margin-bottom: 18px; }
.study-card h3 { position: relative; z-index: 1; font-size: 27px; line-height: 1.05; }
.study-card p { position: relative; z-index: 1; color: #e6f3ff; font-size: 17px; line-height: 1.45; margin: 0; }
.card-tag { position: relative; z-index: 1; display: inline-flex; margin-top: 18px; border-radius: 999px; padding: 7px 11px; background: rgba(255,255,255,.1); color: #cfe6ff; font-weight: 900; font-size: 13px; }
.qa-section { margin-bottom: 0; }
.qa-controls { display: grid; grid-template-columns: 1fr auto; gap: 14px; }
.qa-controls input {
  border: 1px solid var(--line); border-radius: 18px; background: rgba(2,8,18,.72);
  color: var(--text); padding: 0 18px; font-size: 17px; outline: none;
}
.answer-box {
  margin-top: 18px; border: 1px solid var(--line); border-radius: 22px;
  background: rgba(255,255,255,.045); padding: 22px; color: #dceaff;
  font-size: 17px; line-height: 1.65;
}
.answer-box strong { color: var(--green); }
.source { margin-top: 12px; color: var(--muted); font-size: 14px; }
@media (max-width: 860px) {
  .page-shell { width: min(100% - 28px, 1440px); padding-top: 20px; }
  .main-actions { grid-template-columns: 1fr; }
  .summary-box { grid-template-columns: 1fr; }
  .qa-controls { grid-template-columns: 1fr; }
}
'''

JS = r'''
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
'''

VERIFIER = r'''
#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
html = (ROOT / "demo-rag/test-rag-documento-studio-v44.html").read_text(encoding="utf-8")
js = (ROOT / "demo-rag/rag-documento-studio-v44.js").read_text(encoding="utf-8")
css = (ROOT / "demo-rag/rag-documento-studio-v44.css").read_text(encoding="utf-8")
errors = []

def ok(msg): print("OK -", msg)
def err(msg):
    print("ERRORE -", msg)
    errors.append(msg)

for forbidden in ["Carica JSON", "Analizza testo", "Controlla output", "window.print", "btnLoadGenerated", "btnAnalyzeText", "btnQuality"]:
    if forbidden in html + js:
        err(f"testo/funzione vietata presente: {forbidden}")
    else:
        ok(f"assente: {forbidden}")

for required in ["Carica TXT/PDF", "Scarica TXT", "Scarica PDF", "INTERROGA IL DOCUMENTO"]:
    if required in html:
        ok(f"interfaccia contiene {required}")
    else:
        err(f"interfaccia manca {required}")

for required in ["loadFile(file)", "autoAnalyzePastedText", "extractPdfText", "downloadPdf", "downloadText", "answerQuestion"]:
    if required in js:
        ok(f"JS contiene {required}")
    else:
        err(f"JS manca {required}")

if "/demo-rag/pdf-export-browser-v6.js" in html and "AlexBrowserPdfExportV6.exportSectionsToPdf" in js:
    ok("PDF collegato al motore V6")
else:
    err("PDF V6 non collegato")

if "/runtime/web/card-graphic-engine.js" in html:
    ok("card engine runtime caricato")
else:
    err("card engine runtime non caricato")

for bad in ["þ", "ÿ", "\\n"]:
    if bad in html + css:
        err(f"simbolo/testo brutto nel markup: {bad}")

if errors:
    raise SystemExit(1)
print("Verifica UI auto completata.")
'''

DOC = r'''
# RAG Documento Studio V4.4 Auto Flow

Questa correzione rimuove i passaggi inutili dalla pagina:

- niente Carica JSON generato
- niente Analizza testo
- niente Controlla output
- caricamento TXT/PDF con analisi automatica
- testo incollato con analisi automatica
- output: riassunto, card, interrogazione documento
- download TXT e PDF

Il PDF resta collegato a `demo-rag/pdf-export-browser-v6.js`.
'''

REPORT = r'''
# Report RAG Documento Studio V4.4 Auto Flow

Interfaccia semplificata:

- Carica TXT/PDF
- Scarica TXT
- Scarica PDF
- Interroga documento

Analisi automatica dopo caricamento file o incolla testo.
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()

    for name in [
        "README_RAG_DOCUMENTO_STUDIO_V44_UI_FIX.md",
        "README_RAG_DOCUMENTO_STUDIO_V44.md",
        "README_RAG_DOCUMENTO_STUDIO_V44_AUTO_FLOW.md",
    ]:
        p = root / name
        if p.exists():
            p.unlink()
            print(f"OK rimosso: {p}")

    write(root / "demo-rag/test-rag-documento-studio-v44.html", HTML)
    write(root / "demo-rag/rag-documento-studio-v44.css", CSS)
    write(root / "demo-rag/rag-documento-studio-v44.js", JS)
    write(root / "scripts/verifica_rag_documento_studio_v44_auto.py", VERIFIER)
    write(root / "docs/RAG_DOCUMENTO_STUDIO_V44_AUTO_FLOW.md", DOC)
    write(root / "reports/rag_documento_studio_v44_auto_flow.md", REPORT)

    print()
    print("✅ RAG Documento Studio V4.4 Auto Flow installato")
    print("🌐 URL:")
    print("   http://localhost:8000/demo-rag/test-rag-documento-studio-v44.html")
    print("🔄 Hard refresh: Cmd + Shift + R")
    print("🧪 Verifica:")
    print("   python3 scripts/verifica_rag_documento_studio_v44_auto.py")

if __name__ == "__main__":
    main()
