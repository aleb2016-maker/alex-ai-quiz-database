
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
      id("output") ||
      id("risultati-generati-subito") ||
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
      /* V4.8 - flip flashcards solo nella sezione Domande studio */
      .rag-v48-study-grid {display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:20px;margin-top:24px;align-items:stretch}
      .rag-v48-flashcard {position:relative;display:block;width:100%;height:380px;min-height:380px;border:0;padding:0;border-radius:28px;background:transparent;box-shadow:none;color:#f8fafc;cursor:pointer;text-align:left;perspective:1200px;-webkit-perspective:1200px;touch-action:manipulation}
      .rag-v48-flashcard:hover,.rag-v48-flashcard:active {transform:none;filter:none;box-shadow:none}
      .rag-v48-flashcard:focus-visible {outline:3px solid #67e8f9;outline-offset:5px}
      .rag-v48-flashcard-inner {position:relative;display:block;width:100%;height:100%;transform-style:preserve-3d;-webkit-transform-style:preserve-3d;transition:transform .7s cubic-bezier(.2,.75,.22,1)}
      .rag-v48-flashcard.is-flipped .rag-v48-flashcard-inner {transform:rotateY(180deg)}
      .rag-v48-face {position:absolute;inset:0;display:flex;flex-direction:column;align-items:flex-start;width:100%;height:100%;padding:24px;box-sizing:border-box;border:1px solid rgba(148,163,184,.33);border-radius:28px;background:radial-gradient(circle at top left,rgba(49,196,255,.15),transparent 55%),linear-gradient(158deg,#344d72,#392469);box-shadow:0 16px 32px rgba(0,0,0,.28);backface-visibility:hidden;-webkit-backface-visibility:hidden;overflow:auto;overscroll-behavior:contain}
      .rag-v48-face-back {transform:rotateY(180deg);background:radial-gradient(circle at top right,rgba(20,184,166,.22),transparent 55%),linear-gradient(158deg,#173e54,#3b276d)}
      .rag-v48-flashcard .rag-v48-topic {display:inline-block;max-width:100%;padding:8px 13px;border-radius:16px;background:rgba(255,255,255,.14);font-size:.92rem;line-height:1.3;font-weight:800;overflow-wrap:anywhere}
      .rag-v48-flashcard .rag-v48-side {margin-top:18px;color:#b5f3ff;font-size:.78rem;font-weight:950;letter-spacing:.1em}
      .rag-v48-flashcard .rag-v48-content {display:block;margin:12px 0 18px;font-size:clamp(1.12rem,1.75vw,1.55rem);line-height:1.37;font-weight:850;overflow-wrap:anywhere}
      .rag-v48-flashcard .rag-v48-face-back .rag-v48-content {font-size:clamp(1.02rem,1.32vw,1.18rem);font-weight:700;line-height:1.5}
      .rag-v48-flashcard .rag-v48-hint {display:block;margin-top:auto;padding-top:14px;color:#d8eaff;font-size:.9rem;font-weight:750}
      .rag-v48-flashcard:hover .rag-v48-face {border-color:rgba(103,232,249,.65)}
      @media(max-width:980px) {.rag-v48-study-grid {grid-template-columns:repeat(2,minmax(0,1fr))}}
      @media(max-width:680px) {.rag-v48-study-grid {grid-template-columns:1fr}.rag-v48-flashcard {height:365px;min-height:365px}.rag-v48-flashcard .rag-v48-content {font-size:1.24rem}}
      @media(prefers-reduced-motion:reduce) {.rag-v48-flashcard-inner {transition:none}}
      .rag-v47-summary-part {margin:20px 0;padding:16px 18px;border:1px solid rgba(148,163,184,.22);border-radius:18px;background:rgba(255,255,255,.04)}
      .rag-v47-summary-part h3 {margin:0 0 10px;font-size:1.4rem}
      .rag-v47-summary-part p {margin:0;line-height:1.65}
      .rag-v46-panel { scroll-margin-top: 18px }
      .rag-v46-quiz { scroll-margin-top: 20px }
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
        materia: "sicurezza informatica aziendale",
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

  function concepts(text) {
    const out = [];

    if (has(text, ["sicurezza informatica", "sicurezza digitale", "sicurezza dei dati", "cybersecurity", "cyber security"])) {
      out.push(concept(
        "Sicurezza informatica aziendale",
        "protezione dati e sistemi",
        "La sicurezza informatica comprende pratiche, strumenti e comportamenti usati per proteggere dati, dispositivi, account e sistemi digitali.",
        "Quali elementi protegge la sicurezza informatica aziendale?",
        "🛡️"
      ));
    }

    if (has(text, ["email sospetta", "e-mail sospetta", "mail sospetta", "reparto it", "responsabile della sicurezza", "phishing"])) {
      out.push(concept(
        "E-mail sospette",
        "segnalazione e prevenzione",
        "Un'e-mail sospetta deve essere segnalata al reparto IT o al responsabile della sicurezza.",
        "Perché un'e-mail sospetta deve essere segnalata al reparto IT o al responsabile della sicurezza?",
        "📧"
      ));
    }

    if (has(text, ["password manager", "password"])) {
      out.push(concept(
        "Password manager",
        "gestione sicura delle credenziali",
        "Il documento indica come scelta migliore l'uso di un password manager.",
        "A cosa serve un password manager nella sicurezza informatica aziendale?",
        "🔐"
      ));
    }

    if (has(text, ["aggiornamenti", "aggiornamento", "procedura controllata"])) {
      out.push(concept(
        "Aggiornamenti controllati",
        "gestione dei sistemi",
        "Gli aggiornamenti devono essere gestiti con una procedura controllata.",
        "Perché gli aggiornamenti dei sistemi devono seguire una procedura controllata?",
        "🔄"
      ));
    }

    if (has(text, ["rischi", "controlli", "errori", "ridurre"])) {
      out.push(concept(
        "Rischi e controlli",
        "riduzione degli errori",
        "Controlli e comportamenti corretti servono a ridurre errori e rischi per dati e sistemi aziendali.",
        "In che modo controlli e comportamenti corretti riducono i rischi?",
        "⚠️"
      ));
    }

    // Per ogni altro argomento, usa soltanto frasi effettivamente presenti
    // nel documento invece di inventare concetti sulla sicurezza informatica.
    if (!out.length) {
      const segments = clean(text)
        .split(/(?:\n+|(?<=[.!?])\s+)/)
        .map(s => s.trim())
        .filter(s => s.length >= 28 && /[a-zà-ÿ]/i.test(s));
      const seen = new Set();
      for (const segment of segments) {
        const normalized = segment.toLocaleLowerCase("it").replace(/[^a-zà-ÿ0-9]/gi, "").slice(0, 100);
        if (seen.has(normalized)) continue;
        seen.add(normalized);
        const fact = segment.slice(0, 420);
        const words = fact.replace(/^[\d\s.)-]+/, "").split(/\s+/).filter(Boolean);
        const title = words.slice(0, 6).join(" ").replace(/[.,;:!?]+$/, "") || "Concetto del documento";
        out.push(concept(title, "dal documento", fact, "Quale informazione fornisce il documento su «" + title + "»?", "📚"));
        if (out.length >= 8) break;
      }
    }
    return out.slice(0, 8);
  }

  function buildMap() {
    const quality = window.RAGContentQualityV47;
    if (!quality) throw new Error("Motore di analisi V4.7 non caricato. Ricarica la pagina.");
    return quality.analyze(getText());
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
        <span class="rag-v46-pill">📄 Riassunto dal documento</span>
        <h2>Riassunto: ${esc(m.profile.materia)}</h2>
        <div id="ragV46DownloadSlot" class="rag-v46-download-slot"></div>
        <p>Argomenti analizzati: ${m.summary.length}. Le informazioni seguenti provengono dal testo incollato o caricato.</p>
        ${m.summary.map((part,i)=>`
          <article class="rag-v47-summary-part">
            <h3>${i+1}. ${esc(part.title)}</h3>
            <p>${esc(part.text)}</p>
          </article>`).join("")}
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
        <span class="rag-v46-pill">🎓 Flashcard interattive</span>
        <h2>Domande studio</h2>
        <p>Leggi la domanda, prova a rispondere e gira la carta per controllare. Clicca di nuovo per tornare alla domanda.</p>
        <div id="ragV46DownloadSlot" class="rag-v46-download-slot"></div>
        <div class="rag-v48-study-grid">
          ${m.concepts.map((c,i)=>`
            <button class="rag-v48-flashcard" type="button" data-study-flashcard data-flipped="false"
              aria-pressed="false" aria-label="Domanda ${i+1}: ${esc(c.domanda)}. Premi per vedere la risposta">
              <span class="rag-v48-flashcard-inner">
                <span class="rag-v48-face rag-v48-face-front">
                  <span class="rag-v48-topic">${esc(c.ramo)}</span>
                  <span class="rag-v48-side">DOMANDA ${i+1}</span>
                  <span class="rag-v48-content">${esc(c.domanda)}</span>
                  <span class="rag-v48-hint" aria-hidden="true">↻ Clicca per vedere la risposta</span>
                </span>
                <span class="rag-v48-face rag-v48-face-back" aria-hidden="true">
                  <span class="rag-v48-topic">${esc(c.ramo)}</span>
                  <span class="rag-v48-side">RISPOSTA ${i+1}</span>
                  <span class="rag-v48-content">${esc(c.risposta)}</span>
                  <span class="rag-v48-hint" aria-hidden="true">↶ Clicca per tornare alla domanda</span>
                </span>
              </span>
            </button>`).join("")}
        </div>
      </section>
    `;
    outputBox().querySelectorAll("[data-study-flashcard]").forEach(card => {
      card.addEventListener("click", () => {
        const flipped = card.classList.toggle("is-flipped");
        card.dataset.flipped = String(flipped);
        card.setAttribute("aria-pressed", String(flipped));
        const front = card.querySelector(".rag-v48-face-front");
        const back = card.querySelector(".rag-v48-face-back");
        if (front) front.setAttribute("aria-hidden", String(flipped));
        if (back) back.setAttribute("aria-hidden", String(!flipped));
        const active = flipped ? back : front;
        const content = active && active.querySelector(".rag-v48-content");
        const value = content ? content.textContent.trim() : "";
        card.setAttribute("aria-label", (flipped ? "Risposta: " : "Domanda: ") + value +
          (flipped ? ". Premi per tornare alla domanda" : ". Premi per vedere la risposta"));
      });
    });
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

    // Risposte alternative tratte da altri passaggi dello stesso documento:
    // pertinenti al contenuto ma non alla domanda in corso.
    const map = buildMap();
    const other = (map ? map.concepts : [])
      .filter(item => item.fatto !== c.fatto)
      .map(item => item.fatto)
      .filter(Boolean)
      .slice(0, 3);
    if (other.length >= 3) return other;
    return other.concat([
      "Il documento non fornisce alcuna informazione su questo argomento.",
      "Il passaggio riguarda esclusivamente un argomento diverso.",
      "Nessuna delle informazioni elencate è presente nel documento."
    ]).slice(0, 3);
  }

  let quiz = { domande: [], indice: 0, punti: 0, risposto: false };

  function makeQuiz(m) {
    return window.RAGContentQualityV47.makeQuiz(m);
  }

  function renderQuiz() {
    const m = needMap();
    if (!m) return;

    quiz = { domande: makeQuiz(m), indice: 0, punti: 0, risposto: false };
    if (!quiz.domande.length) {
      outputBox().innerHTML = '<section class="rag-v46-panel" role="alert"><h2>Test non generabile</h2><p>Il documento non contiene abbastanza fatti distinti per costruire quattro risposte verificabili. Aggiungi altre informazioni e riprova.</p></section>';
      finalizeOutputScroll();
      return;
    }

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
    const current = id("ragV46QuizBox");
    if (current) current.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function answer(button) {
    if (quiz.risposto) return;
    quiz.risposto = true;

    const q = quiz.domande[quiz.indice];
    const selected = button.getAttribute("data-answer") || "";
    const ok = selected === q.correct;

    if (ok) quiz.punti += 1;
    const score = id("ragV46QuizBox") && id("ragV46QuizBox").querySelector(".rag-v46-progress");
    if (score) score.textContent = "Domanda " + (quiz.indice + 1) + " di " + quiz.domande.length + " · Punteggio: " + quiz.punti + "/" + quiz.domande.length;

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
      const area = outputBox();
      area.innerHTML = '<section class="rag-v46-panel" role="status" aria-live="polite"><h2>Generazione in corso...</h2><p>Sto preparando il materiale dal testo inserito.</p></section>';
      area.scrollIntoView({ behavior: "smooth", block: "start" });
      requestAnimationFrame(() => {
        try {
          fn();
          if (area.textContent.includes("Generazione in corso...")) throw new Error("Nessun risultato prodotto.");
        } catch (error) {
          console.error("RAG: generazione non riuscita", error);
          area.innerHTML = '<section class="rag-v46-panel" role="alert"><h2>Errore durante la generazione</h2><p>' + esc(error.message || String(error)) + '</p></section>';
          area.scrollIntoView({ behavior: "smooth", block: "start" });
        }
      });
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

    // Il caricamento file non e' una generazione: non mostrare lo spinner.
    const loadButton = id("btnFile");
    if (loadButton && fileInput) {
      const clone = loadButton.cloneNode(true);
      loadButton.replaceWith(clone);
      clone.addEventListener("click", ev => {
        ev.preventDefault();
        ev.stopPropagation();
        fileInput.click();
      }, true);
    }
    replaceButton("btnRiassunto", renderSummary);
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
