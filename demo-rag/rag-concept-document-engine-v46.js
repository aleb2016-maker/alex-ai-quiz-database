
(function () {
  "use strict";

  let ragV46DownloadPanel = null;

  function id(x) { return document.getElementById(x); }

  function esc(v) {
    return String(v || "")
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;")
      .replace(/'/g, "&#039;");
  }

  function clean(v) {
    return String(v || "")
      .replace(/\r\n/g, "\n")
      .replace(/\r/g, "\n")
      .replace(/^#{1,6}\s+/gm, "")
      .replace(/^\s*[-*+]\s+/gm, "")
      .replace(/\*\*/g, "")
      .replace(/__/g, "")
      .replace(/`/g, "")
      .replace(/\[(.*?)\]\((.*?)\)/g, "$1")
      .replace(/[ \t]+/g, " ")
      .replace(/\n{3,}/g, "\n\n")
      .trim();
  }

  function has(text, words) {
    const lower = String(text || "").toLowerCase();
    return words.some(function (w) {
      return lower.includes(String(w).toLowerCase());
    });
  }

  function inputBox() {
    return id("documentoInput") ||
      id("testoDocumento") ||
      id("inputDocumento") ||
      document.querySelector("textarea");
  }

  function getText() {
    const box = inputBox();
    return clean(box ? (box.value || box.textContent || "") : "");
  }

  function setText(text) {
    const box = inputBox();
    if (!box) return;
    if ("value" in box) box.value = text;
    else box.textContent = text;
  }

  function outputBox() {
    let out =
      id("risultati-generati-subito") ||
      id("output") ||
      id("risultati") ||
      document.querySelector(".output") ||
      document.querySelector(".results");

    if (!out) {
      out = document.createElement("section");
      out.id = "risultati-generati-subito";
      const anchor = id("full-width-action-zone") || document.querySelector("main") || document.body;
      anchor.insertAdjacentElement("afterend", out);
    }

    return out;
  }

  function addStyle() {
    if (id("ragConceptV46Style")) return;

    const style = document.createElement("style");
    style.id = "ragConceptV46Style";
    style.textContent = `
      .rag-v46-panel {
        width: min(1180px, calc(100% - 48px));
        margin: 24px auto 36px auto;
        padding: 30px;
        border-radius: 30px;
        background: rgba(8,18,38,.90);
        color: #f8fafc;
        border: 1px solid rgba(148,163,184,.30);
        box-sizing: border-box;
      }
      .rag-v46-download-slot {
        margin: 12px 0 18px 0;
      }
      .rag-v46-download-slot > * {
        width: 100% !important;
        margin: 0 !important;
      }
      .rag-v46-panel h2 {
        font-size: clamp(2rem, 4vw, 3.2rem);
        margin: 10px 0 18px;
      }
      .rag-v46-panel p,
      .rag-v46-panel li {
        font-size: 1.1rem;
        line-height: 1.48;
      }
      .rag-v46-pill {
        display: inline-flex;
        padding: 9px 15px;
        border-radius: 999px;
        background: rgba(148,163,184,.26);
        font-weight: 900;
      }
      .rag-v46-grid {
        display: grid;
        grid-template-columns: repeat(3, minmax(0, 1fr));
        gap: 20px;
        margin-top: 24px;
      }
      .rag-v46-card {
        min-height: 260px;
        padding: 24px;
        border-radius: 28px;
        background:
          radial-gradient(circle at top left, rgba(49,196,255,.18), transparent 34%),
          linear-gradient(160deg, rgba(59,76,102,.96), rgba(45,26,88,.96));
        border: 1px solid rgba(148,163,184,.30);
        box-shadow: 0 16px 32px rgba(0,0,0,.28);
      }
      .rag-v46-icon {
        width: 82px;
        height: 82px;
        border-radius: 24px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.2rem;
        background: rgba(255,255,255,.12);
        margin-bottom: 18px;
      }
      .rag-v46-card h3 {
        font-size: 1.55rem;
        margin: 12px 0;
      }
      .rag-v46-answer {
        margin-top: 16px;
        padding: 16px;
        border-radius: 18px;
        background: rgba(255,255,255,.10);
        font-weight: 800;
      }
      .rag-v46-quiz {
        margin-top: 22px;
        padding: 24px;
        border-radius: 24px;
        background: linear-gradient(135deg, rgba(43,72,98,.96), rgba(83,28,122,.96));
      }
      .rag-v46-progress {
        display: inline-flex;
        padding: 10px 16px;
        border-radius: 999px;
        background: rgba(255,255,255,.14);
        font-weight: 900;
        margin-bottom: 18px;
      }
      .rag-v46-options {
        display: grid;
        gap: 14px;
        margin-top: 20px;
      }
      .rag-v46-option,
      .rag-v46-start,
      .rag-v46-next {
        border: 0;
        border-radius: 18px;
        padding: 16px 18px;
        color: #fff;
        background: rgba(255,255,255,.12);
        font-size: 1rem;
        font-weight: 900;
        text-align: left;
        cursor: pointer;
      }
      .rag-v46-start,
      .rag-v46-next {
        display: inline-flex;
        text-align: center;
        background: linear-gradient(135deg, #be123c, #9333ea);
        margin-top: 18px;
      }
      .rag-v46-option.correct { background: rgba(22,163,74,.88); }
      .rag-v46-option.wrong { background: rgba(220,38,38,.88); }
      .rag-v46-feedback {
        margin-top: 18px;
        padding: 16px;
        border-radius: 18px;
        background: rgba(255,255,255,.10);
      }
      @media (max-width: 980px) {
        .rag-v46-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      }
      @media (max-width: 680px) {
        .rag-v46-grid { grid-template-columns: 1fr; }
      }
    `;
    document.head.appendChild(style);
  }

  function profile(text) {
    if (has(text, ["sicurezza informatica", "password", "password manager", "email sospetta", "e-mail sospetta", "reparto it", "responsabile della sicurezza", "sistemi digitali", "aggiornamenti", "procedura controllata", "rischi", "controlli"])) {
      return {
        materia: "sicurezza digitale",
        contesto: "documento aziendale",
        categoria: "procedure e buone pratiche"
      };
    }

    return {
      materia: "testo caricato",
      contesto: "documento generico",
      categoria: "contenuto principale"
    };
  }

  function concept(title, ramo, fatto, domanda, icon) {
    return { title, ramo, fatto, domanda, icon };
  }

  function sentences(text) {
    return clean(text)
      .replace(/\n+/g, ". ")
      .split(/(?<=[.!?])\s+/)
      .map(function (s) { return s.trim(); })
      .filter(function (s) { return s.length >= 24; });
  }

  function evidence(text, words) {
    const found = sentences(text).find(function (sentence) {
      return has(sentence, words);
    });

    return found || "";
  }

  function concepts(text) {
    const out = [];
    const protezione = evidence(text, ["sicurezza informatica", "dati", "dispositivi", "account", "sistemi digitali"]);
    const email = evidence(text, ["email sospetta", "e-mail sospetta", "mail sospetta", "reparto it", "responsabile della sicurezza", "phishing"]);
    const password = evidence(text, ["password manager", "password", "credenziali"]);
    const aggiornamenti = evidence(text, ["aggiornamenti", "aggiornamento", "procedura controllata", "patch"]);
    const rischi = evidence(text, ["rischi", "controlli", "errori", "ridurre"]);

    if (protezione) {
      out.push(concept(
        "Protezione dati e sistemi",
        "protezione dati e sistemi",
        protezione,
        "Quali elementi protegge questa parte del documento?",
        "🛡️"
      ));
    }

    if (email) {
      out.push(concept(
        "Segnalazione email",
        "segnalazione e prevenzione",
        email,
        "Perché un'e-mail sospetta deve essere segnalata al reparto IT o al responsabile della sicurezza?",
        "📧"
      ));
    }

    if (password) {
      out.push(concept(
        "Gestione credenziali",
        "gestione sicura delle credenziali",
        password,
        "Che cosa spiega il documento sulla gestione delle credenziali?",
        "🔐"
      ));
    }

    if (aggiornamenti) {
      out.push(concept(
        "Gestione aggiornamenti",
        "gestione dei sistemi",
        aggiornamenti,
        "Perché gli aggiornamenti dei sistemi devono seguire una procedura controllata?",
        "🔄"
      ));
    }

    if (rischi) {
      out.push(concept(
        "Prevenzione rischi",
        "riduzione degli errori",
        rischi,
        "In che modo controlli e comportamenti corretti riducono i rischi?",
        "⚠️"
      ));
    }

    return out.slice(0, 6);
  }

  function buildMap() {
    const text = getText();
    if (text.length < 40) return null;

    const p = profile(text);
    const c = concepts(text);

    if (!c.length) return null;
    return { profile: p, concepts: c };
  }

  function noContent() {
    outputBox().innerHTML = `
      <section class="rag-v46-panel">
        <span class="rag-v46-pill">⚠️ Documento insufficiente</span>
        <h2>Non ci sono concetti concreti da generare</h2>
        <p>Carica un testo con contenuti reali: regole, procedure, esempi, rischi o indicazioni operative.</p>
      </section>
    `;
  }

  function needMap() {
    const m = buildMap();
    if (!m) noContent();
    return m;
  }


  function captureDownloadPanel() {
    if (ragV46DownloadPanel) return ragV46DownloadPanel;

    const candidates = Array.from(document.querySelectorAll("section, article, div"))
      .filter(function (node) {
        const txt = node.textContent || "";
        return txt.includes("Scarica materiale generato") &&
          txt.includes("Scarica PDF") &&
          !node.closest("#risultati-generati-subito");
      })
      .sort(function (a, b) {
        return (a.textContent || "").length - (b.textContent || "").length;
      });

    ragV46DownloadPanel = candidates[0] || null;
    return ragV46DownloadPanel;
  }

  function placeDownloadPanelInsideOutput() {
    const panel = ragV46DownloadPanel || captureDownloadPanel();
    const slot = document.getElementById("ragV46DownloadSlot");

    if (!panel || !slot) return;

    slot.appendChild(panel);
  }

  function finalizeOutputScroll() {
    placeDownloadPanelInsideOutput();

    const target = outputBox().querySelector(".rag-v46-panel") || outputBox();

    window.requestAnimationFrame(function () {
      window.setTimeout(function () {
        target.scrollIntoView({ behavior: "smooth", block: "start" });
      }, 80);
    });
  }

  function renderSummary() {
    const m = needMap();
    if (!m) return;

    outputBox().innerHTML = `
      <section class="rag-v46-panel" data-export-section="summary">
        
        <span class="rag-v46-pill">📄 ${esc(m.profile.contesto)}</span>
        <h2>Riassunto: ${esc(m.profile.materia)}</h2>\n        <div id="ragV46DownloadSlot" class="rag-v46-download-slot"></div>
        <p>Il documento riguarda <strong>${esc(m.profile.materia)}</strong> e contiene indicazioni pratiche su ${esc(m.profile.categoria)}.</p>
        <ol>${m.concepts.map(c => `<li><strong>${esc(c.title)}:</strong> ${esc(c.fatto)}</li>`).join("")}</ol>
      </section>
    `;
    finalizeOutputScroll();
  }

  function renderCards() {
    const m = needMap();
    if (!m) return;

    outputBox().innerHTML = `
      <section class="rag-v46-panel" data-export-section="cards">
        
        <span class="rag-v46-pill">🧩 Card concetti</span>
        <h2>Card su ${esc(m.profile.materia)}</h2>\n        <div id="ragV46DownloadSlot" class="rag-v46-download-slot"></div>
        <p>Ogni card rappresenta un concetto reale del documento.</p>
        <div class="rag-v46-grid">
          ${m.concepts.map((c, i) => `
            <article class="rag-v46-card" data-pdf-card>
              <div class="rag-v46-icon">${esc(c.icon)}</div>
              <span class="rag-v46-pill">${esc(c.ramo)}</span>
              <h3>${i + 1}. ${esc(c.title)}</h3>
              <p>${esc(c.fatto)}</p>
            </article>
          `).join("")}
        </div>
      </section>
    `;
    finalizeOutputScroll();
  }

  function renderStudy() {
    const m = needMap();
    if (!m) return;

    outputBox().innerHTML = `
      <section class="rag-v46-panel" data-export-section="study">
        
        <span class="rag-v46-pill">🎓 Domande studio</span>
        <h2>Domande studio: ${esc(m.profile.materia)}</h2>\n        <div id="ragV46DownloadSlot" class="rag-v46-download-slot"></div>
        <div class="rag-v46-grid">
          ${m.concepts.map((c, i) => `
            <article class="rag-v46-card">
              <span class="rag-v46-pill">${esc(c.ramo)}</span>
              <h3>${i + 1}. ${esc(c.domanda)}</h3>
              <div class="rag-v46-answer">${esc(c.fatto)}</div>
            </article>
          `).join("")}
        </div>
      </section>
    `;
    finalizeOutputScroll();
  }

  function shuffle(a) {
    const b = a.slice();
    for (let i = b.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [b[i], b[j]] = [b[j], b[i]];
    }
    return b;
  }

  function distractors(c) {
    const t = c.title.toLowerCase();

    if (t.includes("e-mail") || t.includes("mail")) {
      return [
        "Aprire gli allegati per controllare subito il contenuto.",
        "Inoltrarla a tutti i colleghi per chiedere un parere.",
        "Rispondere al mittente inserendo dati o credenziali aziendali."
      ];
    }

    if (t.includes("password")) {
      return [
        "Condividere la stessa password tra più colleghi.",
        "Scrivere le password in un documento non protetto.",
        "Usare password brevi perché sono più facili da ricordare."
      ];
    }

    if (t.includes("aggiornamenti")) {
      return [
        "Installare aggiornamenti a caso senza controllo.",
        "Evitare sempre gli aggiornamenti per non modificare i sistemi.",
        "Delegare gli aggiornamenti a chiunque senza responsabilità."
      ];
    }

    return [
      "Ignorare questo punto perché non produce effetti pratici.",
      "Gestirlo senza controlli, responsabilità o verifica.",
      "Rimandare ogni azione anche quando il testo indica una procedura."
    ];
  }

  let quiz = { domande: [], indice: 0, punti: 0, risposto: false };

  function makeQuiz(m) {
    return m.concepts.map(c => ({
      q: c.domanda,
      correct: c.fatto,
      options: shuffle([c.fatto].concat(distractors(c))),
      explanation: c.fatto
    }));
  }

  function renderQuiz() {
    const m = needMap();
    if (!m) return;

    quiz = { domande: makeQuiz(m), indice: 0, punti: 0, risposto: false };

    outputBox().innerHTML = `
      <section class="rag-v46-panel" data-export-section="test">
        
        <span class="rag-v46-pill">🧪 Test concetti</span>
        <h2>Test: ${esc(m.profile.materia)}</h2>\n        <div id="ragV46DownloadSlot" class="rag-v46-download-slot"></div>
        <p>Il test usa concetti reali del documento e distrattori vicini ma sbagliati.</p>
        <button id="ragV46Start" class="rag-v46-start" type="button">Inizia test</button>
        <div id="ragV46QuizBox"></div>
      </section>
    `;

    id("ragV46Start").addEventListener("click", showQuestion);
    finalizeOutputScroll();
  }

  function showQuestion() {
    const box = id("ragV46QuizBox");
    const q = quiz.domande[quiz.indice];
    const total = quiz.domande.length;
    quiz.risposto = false;

    box.innerHTML = `
      <div class="rag-v46-quiz">
        <div class="rag-v46-progress">Domanda ${quiz.indice + 1} di ${total} · Punteggio: ${quiz.punti}/${total}</div>
        <h3>${esc(q.q)}</h3>
        <div class="rag-v46-options">
          ${q.options.map((o, i) => `<button class="rag-v46-option" type="button" data-answer="${esc(o)}">${String.fromCharCode(65 + i)}. ${esc(o)}</button>`).join("")}
        </div>
        <div id="ragV46Feedback"></div>
      </div>
    `;

    document.querySelectorAll(".rag-v46-option").forEach(b => {
      b.addEventListener("click", () => answer(b));
    });
  }

  function answer(button) {
    if (quiz.risposto) return;
    quiz.risposto = true;

    const q = quiz.domande[quiz.indice];
    const selected = button.getAttribute("data-answer") || "";
    const ok = selected === q.correct;

    if (ok) quiz.punti += 1;

    document.querySelectorAll(".rag-v46-option").forEach(b => {
      const ans = b.getAttribute("data-answer") || "";
      b.disabled = true;
      if (ans === q.correct) b.classList.add("correct");
      if (b === button && !ok) b.classList.add("wrong");
    });

    const last = quiz.indice >= quiz.domande.length - 1;

    id("ragV46Feedback").innerHTML = `
      <div class="rag-v46-feedback">
        <strong>${ok ? "Corretto." : "Non corretto."}</strong>
        <p>${esc(q.explanation)}</p>
        <button id="ragV46Next" class="rag-v46-next" type="button">${last ? "Vedi risultato" : "Prossima domanda"}</button>
      </div>
    `;

    id("ragV46Next").addEventListener("click", () => {
      if (last) {
        const total = quiz.domande.length;
        const perc = Math.round((quiz.punti / total) * 100);
        id("ragV46QuizBox").innerHTML = `
          <div class="rag-v46-quiz">
            <h3>Risultato finale</h3>
            <p><strong>${quiz.punti}/${total}</strong> corrette · ${perc}%</p>
            <button id="ragV46Retry" class="rag-v46-start" type="button">Ripeti test</button>
          </div>
        `;
        id("ragV46Retry").addEventListener("click", () => {
          quiz.indice = 0;
          quiz.punti = 0;
          quiz.domande = shuffle(quiz.domande);
          showQuestion();
        });
      } else {
        quiz.indice += 1;
        showQuestion();
      }
    });
  }

  async function readFile(file) {
    if (!file) return;

    let text = "";

    if (/\.pdf$/i.test(file.name) && window.pdfjsLib) {
      const data = await file.arrayBuffer();
      const pdf = await window.pdfjsLib.getDocument({ data }).promise;
      const parts = [];

      for (let n = 1; n <= pdf.numPages; n++) {
        const page = await pdf.getPage(n);
        const content = await page.getTextContent();
        parts.push(content.items.map(x => x.str || "").join(" "));
      }

      text = parts.join("\n\n");
    } else {
      text = await file.text();
    }

    setText(clean(text));
  }

  function replaceButton(buttonId, fn) {
    const old = id(buttonId);
    if (!old) return;

    const b = old.cloneNode(true);
    old.replaceWith(b);

    b.addEventListener("click", ev => {
      ev.preventDefault();
      ev.stopPropagation();
      if (ev.stopImmediatePropagation) ev.stopImmediatePropagation();
      fn();
      return false;
    }, true);
  }

  function init() {
    addStyle();
    captureDownloadPanel();

    const fileInput = id("fileInput");

    if (fileInput) {
      fileInput.addEventListener("change", async () => {
        await readFile(fileInput.files && fileInput.files[0]);
      });
    }

    replaceButton("btnFile", () => fileInput && fileInput.click());
    replaceButton("btnCard", renderCards);
    replaceButton("btnStudio", renderStudy);
    replaceButton("btnTest", renderQuiz);

    window.ragConceptDocumentEngineV46 = {
      buildMap,
      renderSummary,
      renderCards,
      renderStudy,
      renderQuiz
    };

    console.log("OK RAG Concept Engine V4.6 attivo");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
