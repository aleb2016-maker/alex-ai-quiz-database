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
    study: ["genera domande studio", "domande studio"]
  };

  const TITLES = {
    summary: "Riassunto",
    cards: "Card",
    quiz: "Test/Quiz",
    study: "Domande studio"
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

  async function runKind(kind) {
    const inputText = getInputText();
    const motor = findRealMotor(kind);

    if (!inputText || inputText.length < 20) {
      renderError(kind, "Nessun testo reale trovato nella pagina. Carica o incolla un documento prima di generare.");
      return;
    }

    try {
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
