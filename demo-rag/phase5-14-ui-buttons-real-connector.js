/*
FASE 5.14.1 — UI BUTTONS REAL CONNECTOR

Collega i pulsanti della pagina ai motori browser già presenti.
Non genera fallback/demo.
Se non trova un motore reale, mostra errore tecnico.
*/

(function () {
  "use strict";

  const PHASE = "5.14.1";
  const CONNECTOR_ID = "phase5-14-ui-buttons-real-connector";

  const MOTOR_CANDIDATES = {
    summary: [
      "phase5GenerateSummary",
      "generaRiassunto",
      "generateSummary",
      "ragGenerateSummary",
      "generaRiassuntoUniversale",
      "generaRiassuntoDocumento"
    ],
    cards: [
      "phase5GenerateCards",
      "generaCard",
      "generateCards",
      "ragGenerateCards",
      "generaCardUniversali",
      "generaCardDocumento"
    ],
    quiz: [
      "phase5GenerateQuiz",
      "generaTest",
      "generateQuiz",
      "ragGenerateQuiz",
      "generaTestDocumento",
      "generaQuizDocumento"
    ],
    study: [
      "phase5GenerateStudyQuestions",
      "generaDomandeStudio",
      "generateStudyQuestions",
      "ragGenerateStudyQuestions",
      "generaDomandeStudioDocumento"
    ]
  };

  const BUTTON_LABELS = {
    summary: ["genera riassunto", "riassunto"],
    cards: ["genera card", "card"],
    quiz: ["genera test", "test", "quiz"],
    study: ["interroga documento", "interroga il documento", "genera domande studio", "domande studio"]
  };

  const TITLES = {
    summary: "Riassunto",
    cards: "Card",
    quiz: "Test/Quiz",
    study: "Interroga Documento"
  };

  function norm(text) {
    return String(text || "").toLowerCase().replace(/\s+/g, " ").trim();
  }

  function getAllClickable() {
    return Array.from(document.querySelectorAll("button, .button, .btn, [role='button'], a, div, section, article"))
      .filter((el) => norm(el.innerText || el.textContent).length > 0);
  }

  function findButton(kind) {
    const labels = BUTTON_LABELS[kind] || [];
    const clickables = getAllClickable();

    let best = null;

    for (const el of clickables) {
      const text = norm(el.innerText || el.textContent);
      if (!text) continue;

      for (const label of labels) {
        if (text === label || text.includes(label)) {
          best = el;
          break;
        }
      }

      if (best) break;
    }

    return best;
  }

  function findOutputBox() {
    const preferredIds = [
      "output",
      "risultato",
      "risultati",
      "outputFinale",
      "rag-output",
      "document-output",
      "flusso-finale",
      "final-output"
    ];

    for (const id of preferredIds) {
      const el = document.getElementById(id);
      if (el) return el;
    }

    const candidates = Array.from(document.querySelectorAll("textarea, pre, .output, .result, .results, [data-output]"));
    if (candidates.length) return candidates[candidates.length - 1];

    const box = document.createElement("section");
    box.id = "phase5-14-real-output";
    box.style.marginTop = "24px";
    box.style.padding = "22px";
    box.style.borderRadius = "18px";
    box.style.border = "1px solid rgba(255,255,255,0.22)";
    box.style.background = "rgba(15,23,42,0.72)";
    box.style.color = "#fff";
    box.style.whiteSpace = "pre-wrap";
    box.innerHTML = "<h2>Output motori collegati</h2><div data-phase5-output-body></div>";

    const main = document.querySelector("main") || document.body;
    main.appendChild(box);
    return box.querySelector("[data-phase5-output-body]") || box;
  }

  function getInputText() {
    const selectors = [
      "#testo",
      "#inputText",
      "#documentText",
      "#documento",
      "#ocrText",
      "#rawText",
      "textarea"
    ];

    for (const selector of selectors) {
      const el = document.querySelector(selector);
      if (el && typeof el.value === "string" && el.value.trim().length >= 20) {
        return el.value.trim();
      }
    }

    const editable = document.querySelector("[contenteditable='true']");
    if (editable && norm(editable.innerText).length >= 20) {
      return editable.innerText.trim();
    }

    return "";
  }

  function findRealMotor(kind) {
    const candidates = MOTOR_CANDIDATES[kind] || [];

    for (const name of candidates) {
      if (typeof window[name] === "function") {
        return { name, fn: window[name] };
      }
    }

    return null;
  }

  async function phase5LocalBackendBridgeGenerate(kind, inputText) {
    const response = await fetch("http://127.0.0.1:8765/api/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        kind,
        text: inputText,
        strictNoFallback: true,
        source: "phase5-14-ui"
      })
    });

    const payload = await response.json();

    if (!response.ok || !payload.ok) {
      throw new Error(
        "Bridge locale backend non ha prodotto output valido: " +
        (payload.error || response.status)
      );
    }

    return payload;
  }

  function renderOutput(kind, result, motorName) {
    const out = findOutputBox();
    const title = TITLES[kind] || kind;

    let body = "";

    if (typeof result === "string") {
      body = result;
    } else {
      body = JSON.stringify(result, null, 2);
    }

    out.innerHTML =
      "<h2>" + title + " — motore reale collegato</h2>" +
      "<p><strong>Fase:</strong> " + PHASE + "</p>" +
      "<p><strong>Motore browser chiamato:</strong> " + motorName + "</p>" +
      "<pre style='white-space:pre-wrap;overflow:auto;'>" +
      escapeHtml(body) +
      "</pre>";

    out.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderError(kind, message) {
    const out = findOutputBox();
    const title = TITLES[kind] || kind;

    out.innerHTML =
      "<h2>" + title + " — collegamento non completato</h2>" +
      "<p><strong>Fase:</strong> " + PHASE + "</p>" +
      "<p style='color:#ffb4b4;'><strong>Errore:</strong> " + escapeHtml(message) + "</p>" +
      "<p>Blocco intenzionale: nessun fallback/demo viene usato.</p>";

    out.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function escapeHtml(text) {
    return String(text || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }


  // ============================================================
  // FASE 5.15G.5.2 — REAL UI INTERROGA DOCUMENTO CONNECTION
  // UI reale: il vecchio pulsante Domande studio diventa Interroga Documento.
  // Collegamento reale: /api/generate con kind="interroga_documento"
  // e text JSON { document_text, user_question }.
  // Nessun fallback/demo, nessuna risposta hardcoded.
  // ============================================================

  function ensureDocumentQuestionBox() {
    let box = document.getElementById("phase5-15g52-document-question-box");
    if (box) return box;

    box = document.createElement("section");
    box.id = "phase5-15g52-document-question-box";
    box.style.margin = "18px 0";
    box.style.padding = "18px";
    box.style.borderRadius = "16px";
    box.style.border = "1px solid rgba(80,255,170,0.35)";
    box.style.background = "rgba(4,120,87,0.16)";
    box.style.color = "#eafff5";

    box.innerHTML =
      "<label for='phase5-15g52-document-question' style='display:block;font-weight:800;margin-bottom:8px;'>Interroga Documento</label>" +
      "<textarea id='phase5-15g52-document-question' rows='3' " +
      "placeholder='Scrivi una domanda sul documento caricato. Esempio: quali responsabilità vengono citate?' " +
      "style='width:100%;box-sizing:border-box;border-radius:12px;padding:12px;background:rgba(15,23,42,.92);color:#fff;border:1px solid rgba(255,255,255,.24);'></textarea>" +
      "<p style='margin:8px 0 0;font-size:.92rem;opacity:.86;'>La risposta viene presa solo dal documento. Se l’informazione non è presente, il motore lo dichiara.</p>";

    const studyButton = findButton("study");
    if (studyButton && studyButton.parentNode) {
      studyButton.parentNode.insertBefore(box, studyButton.nextSibling);
    } else {
      const main = document.querySelector("main") || document.body;
      main.insertBefore(box, main.firstChild);
    }

    return box;
  }

  function getDocumentQuestion() {
    const box = ensureDocumentQuestionBox();
    const textarea = box.querySelector("#phase5-15g52-document-question");
    return textarea && typeof textarea.value === "string" ? textarea.value.trim() : "";
  }

  function renderDocumentQAOutput(result, motorName) {
    const out = findOutputBox();
    const raw = result && (result.final_output || result.raw_output || result.output || result.result || result);
    const answer = raw && raw.answer ? String(raw.answer) : JSON.stringify(raw, null, 2);
    const status = raw && raw.status ? String(raw.status) : "";
    const confidence = raw && raw.confidence ? String(raw.confidence) : "";
    const evidence = raw && Array.isArray(raw.evidence) ? raw.evidence : [];

    let evidenceHtml = "";
    if (evidence.length) {
      evidenceHtml =
        "<h3>Passaggi usati dal documento</h3><ol>" +
        evidence.slice(0, 5).map((item) => {
          const txt = item && item.text ? item.text : String(item || "");
          return "<li>" + escapeHtml(txt) + "</li>";
        }).join("") +
        "</ol>";
    }

    out.innerHTML =
      "<h2>Interroga Documento — risposta dal documento</h2>" +
      "<p><strong>Fase:</strong> 5.15G.5.2</p>" +
      "<p><strong>Motore backend chiamato:</strong> " + escapeHtml(motorName) + "</p>" +
      (status ? "<p><strong>Status:</strong> " + escapeHtml(status) + "</p>" : "") +
      (confidence ? "<p><strong>Confidence:</strong> " + escapeHtml(confidence) + "</p>" : "") +
      "<div style='white-space:pre-wrap;font-size:1rem;line-height:1.55;'>" + escapeHtml(answer) + "</div>" +
      evidenceHtml;

    out.scrollIntoView({ behavior: "smooth", block: "start" });
  }


  async function runKind(kind) {
    const inputText = getInputText();
    const motor = findRealMotor(kind);

    if (!inputText || inputText.length < 20) {
      renderError(kind, "Nessun testo reale trovato nella pagina. Carica o incolla un documento prima di generare.");
      return;
    }

    try {
      if (kind === "study") {
        ensureDocumentQuestionBox();
        const question = getDocumentQuestion();

        if (!question || question.length < 4) {
          renderError(kind, "Scrivi una domanda sul documento prima di usare Interroga Documento.");
          return;
        }

        const bridgeInput = JSON.stringify({
          document_text: inputText,
          user_question: question
        });

        const bridgePayload = await phase5LocalBackendBridgeGenerate("interroga_documento", bridgeInput);
        renderDocumentQAOutput(bridgePayload.result || bridgePayload, "local_backend_bridge_8765_interroga_documento");
        return;
      }

      if (motor) {
        const result = await motor.fn(inputText, {
          phase: PHASE,
          kind,
          strictNoFallback: true,
          source: "ui-button"
        });

        renderOutput(kind, result, motor.name);
        return;
      }

      const bridgePayload = await phase5LocalBackendBridgeGenerate(kind, inputText);
      renderOutput(kind, bridgePayload.result, "local_backend_bridge_8765");

    } catch (error) {
      renderError(kind, error && error.stack ? error.stack : String(error));
    }
  }

  function attach(kind) {
    const btn = findButton(kind);
    if (!btn) return false;

    btn.setAttribute("data-phase5-14-connected", kind);

    if (kind === "study") {
      btn.textContent = "Interroga Documento";
      btn.setAttribute("aria-label", "Interroga Documento");
      btn.setAttribute("title", "Fai una domanda libera sul documento caricato");
      ensureDocumentQuestionBox();
    }

    btn.addEventListener("click", function (event) {
      event.preventDefault();
      event.stopPropagation();
      runKind(kind);
    }, true);

    return true;
  }

  function addStatusPanel(results) {
    const existing = document.getElementById(CONNECTOR_ID);
    if (existing) existing.remove();

    const panel = document.createElement("div");
    panel.id = CONNECTOR_ID;
    panel.style.margin = "18px 0";
    panel.style.padding = "14px 18px";
    panel.style.borderRadius = "14px";
    panel.style.border = "1px solid rgba(80,255,170,0.35)";
    panel.style.background = "rgba(0,120,90,0.18)";
    panel.style.color = "#eafff5";
    panel.style.fontWeight = "700";

    const ok = Object.values(results).filter(Boolean).length;
    panel.textContent =
      "FASE 5.14.1 — Pulsanti agganciati: " + ok + "/4. " +
      "Modalità strict: nessun fallback/demo.";

    const main = document.querySelector("main") || document.body;
    main.insertBefore(panel, main.firstChild);
  }

  function boot() {
    const results = {
      summary: attach("summary"),
      cards: attach("cards"),
      quiz: attach("quiz"),
      study: attach("study")
    };

    window.__phase5_14_ui_buttons_connection__ = {
      phase: PHASE,
      results,
      motorCandidates: MOTOR_CANDIDATES
    };

    addStatusPanel(results);

    console.log("[Phase 5.14.1] UI buttons connector ready", window.__phase5_14_ui_buttons_connection__);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
