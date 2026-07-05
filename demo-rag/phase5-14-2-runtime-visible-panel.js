/*
FASE 5.14.2 — RUNTIME VISIBLE PANEL

Mostra nella pagina lo stato reale del collegamento:
- connector 5.14.1 caricato
- pulsanti agganciati
- funzioni motore browser disponibili
- bisogno eventuale di bridge locale backend Python

Non genera fallback/demo.
*/

(function () {
  "use strict";

  const PHASE = "5.14.2";
  const PANEL_ID = "phase5-14-2-runtime-visible-panel";

  const MOTOR_NAMES = [
    "phase5GenerateSummary",
    "generaRiassunto",
    "generateSummary",
    "ragGenerateSummary",
    "generaRiassuntoUniversale",
    "generaRiassuntoDocumento",

    "phase5GenerateCards",
    "generaCard",
    "generateCards",
    "ragGenerateCards",
    "generaCardUniversali",
    "generaCardDocumento",

    "phase5GenerateQuiz",
    "generaTest",
    "generateQuiz",
    "ragGenerateQuiz",
    "generaTestDocumento",
    "generaQuizDocumento",

    "phase5GenerateStudyQuestions",
    "generaDomandeStudio",
    "generateStudyQuestions",
    "ragGenerateStudyQuestions",
    "generaDomandeStudioDocumento"
  ];

  function availableMotors() {
    return MOTOR_NAMES.filter((name) => typeof window[name] === "function");
  }

  function connectorResults() {
    const conn = window.__phase5_14_ui_buttons_connection__;
    if (!conn || !conn.results) return null;
    return conn.results;
  }

  function countConnectedButtons() {
    return document.querySelectorAll("[data-phase5-14-connected]").length;
  }

  function getInputInfo() {
    const textareas = Array.from(document.querySelectorAll("textarea"));
    const usable = textareas.filter((el) => String(el.value || "").trim().length >= 20);
    return {
      textareas: textareas.length,
      usableTextareas: usable.length
    };
  }

  function ensurePanel() {
    let panel = document.getElementById(PANEL_ID);
    if (panel) return panel;

    panel = document.createElement("section");
    panel.id = PANEL_ID;
    panel.style.margin = "18px 0";
    panel.style.padding = "18px 22px";
    panel.style.borderRadius = "18px";
    panel.style.border = "2px solid rgba(80, 255, 170, 0.45)";
    panel.style.background = "rgba(0, 80, 70, 0.22)";
    panel.style.color = "#f2fff9";
    panel.style.fontFamily = "system-ui, -apple-system, BlinkMacSystemFont, sans-serif";
    panel.style.boxShadow = "0 18px 40px rgba(0,0,0,0.25)";
    panel.style.lineHeight = "1.45";

    const main = document.querySelector("main") || document.body;
    main.insertBefore(panel, main.firstChild);

    return panel;
  }

  function render() {
    const panel = ensurePanel();
    const motors = availableMotors();
    const conn = connectorResults();
    const input = getInputInfo();
    const connectedButtons = countConnectedButtons();
    const domGuard = window.__phase5_14_2_dom_guard__;

    const connText = conn
      ? JSON.stringify(conn)
      : "connector 5.14.1 non ancora rilevato";

    const bridgeStatus = motors.length > 0
      ? "MOTORI_BROWSER_TROVATI"
      : "SERVE_BRIDGE_LOCALE_BACKEND";

    const bridgeColor = motors.length > 0 ? "#8cffc1" : "#ffd27a";

    panel.innerHTML = `
      <h2 style="margin:0 0 10px 0;">FASE ${PHASE} — Stato runtime UI</h2>
      <p><strong>Pulsanti DOM agganciati:</strong> ${connectedButtons}/4</p>
      <p><strong>Connector 5.14.1:</strong> <code>${escapeHtml(connText)}</code></p>
      <p><strong>Funzioni motore browser trovate:</strong> ${motors.length}</p>
      <p><strong>Nomi funzioni:</strong> <code>${escapeHtml(motors.join(", ") || "nessuna")}</code></p>
      <p><strong>Input testo:</strong> textarea=${input.textareas}, textarea utilizzabili=${input.usableTextareas}</p>
      <p><strong>DOM guard:</strong> ${domGuard ? "attiva, blocchi appendChild=" + domGuard.blockedAppendChild : "non rilevata"}</p>
      <p style="font-size:1.05rem;color:${bridgeColor};"><strong>Stato prossimo passo:</strong> ${bridgeStatus}</p>
      <p style="opacity:.86;margin-bottom:0;">
        Se lo stato è <strong>SERVE_BRIDGE_LOCALE_BACKEND</strong>, i pulsanti sono agganciati
        ma serve creare il ponte locale dalla pagina ai motori Python validati.
        Nessun output demo viene considerato valido.
      </p>
    `;

    window.__phase5_14_2_runtime_status__ = {
      phase: PHASE,
      connectedButtons,
      connectorResults: conn,
      availableMotors: motors,
      input,
      bridgeStatus,
      domGuard: domGuard || null
    };
  }

  function escapeHtml(text) {
    return String(text || "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function boot() {
    render();
    setTimeout(render, 500);
    setTimeout(render, 1500);
    setTimeout(render, 3000);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
