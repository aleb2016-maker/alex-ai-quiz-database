#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.14.1 — UI BUTTONS REAL CONNECTOR

Scopo:
- collegare i 4 pulsanti della pagina:
  - Genera riassunto
  - Genera card
  - Genera test
  - Genera domande studio
- aggiungere un JS connector controllato;
- impedire output fallback/demo quando non esiste un motore reale;
- creare report di patch.

Non modifica motori backend.
Non modifica PDF.
Non cambia layout, salvo inserire script connector e stato tecnico.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "demo-rag" / "test-documenti-universale.html"
JS = ROOT / "demo-rag" / "phase5-14-ui-buttons-real-connector.js"
REPORT_JSON = ROOT / "reports" / "phase5_14_ui_buttons_real_connector_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_14_ui_buttons_real_connector_v1.md"


@dataclass
class PatchReport:
    phase: str
    status: str
    page: str
    js: str
    script_injected: bool
    defects: List[str]
    warnings: List[str]


JS_CODE = r'''/*
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

    if (!motor) {
      renderError(
        kind,
        "Nessuna funzione browser reale trovata per " + kind +
        ". Serve agganciare questa pagina al bridge/engine reale, non a fallback."
      );
      return;
    }

    try {
      const result = await motor.fn(inputText, {
        phase: PHASE,
        kind,
        strictNoFallback: true,
        source: "ui-button"
      });

      renderOutput(kind, result, motor.name);
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
'''


def render_md(report: PatchReport) -> str:
    lines = [
        "# FASE 5.14.1 — UI BUTTONS REAL CONNECTOR",
        "",
        f"Status: `{report.status}`",
        "",
        f"- Pagina: `{report.page}`",
        f"- JS connector: `{report.js}`",
        f"- Script injected: `{report.script_injected}`",
        "",
        "## Defects",
        "",
        "- Nessuno" if not report.defects else "\n".join(f"- `{d}`" for d in report.defects),
        "",
        "## Warnings",
        "",
        "- Nessuno" if not report.warnings else "\n".join(f"- `{w}`" for w in report.warnings),
        "",
        "## Note",
        "",
        "- Il connector aggancia i pulsanti della pagina.",
        "- Non inventa output.",
        "- Se non trova motori browser reali, blocca e mostra errore.",
        "- Nessun fallback/demo viene usato.",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    defects: List[str] = []
    warnings: List[str] = []

    if not PAGE.exists():
        defects.append(f"Pagina non trovata: {PAGE}")
    else:
        html = PAGE.read_text(encoding="utf-8", errors="replace")

        JS.write_text(JS_CODE, encoding="utf-8")

        script_tag = '<script src="phase5-14-ui-buttons-real-connector.js"></script>'

        if script_tag not in html:
            if "</body>" in html:
                html = html.replace("</body>", f"  {script_tag}\n</body>", 1)
            else:
                html += "\n" + script_tag + "\n"
            PAGE.write_text(html, encoding="utf-8")
            injected = True
        else:
            injected = False
            warnings.append("Script connector già presente nella pagina.")

    status = (
        "PASS - Fase 5.14.1: UI_BUTTONS_REAL_CONNECTOR_APPLIED"
        if not defects
        else "FAIL - Fase 5.14.1: UI_BUTTONS_REAL_CONNECTOR_NOT_APPLIED"
    )

    report = PatchReport(
        phase="5.14.1",
        status=status,
        page=str(PAGE.relative_to(ROOT)),
        js=str(JS.relative_to(ROOT)),
        script_injected=not defects,
        defects=defects,
        warnings=warnings,
    )

    REPORT_JSON.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_md(report), encoding="utf-8")

    print(status)
    print(f"Page: {report.page}")
    print(f"JS: {report.js}")
    print(f"Defects: {len(defects)}")
    print(f"Warnings: {len(warnings)}")
    print(f"JSON report: {REPORT_JSON}")
    print(f"Markdown report: {REPORT_MD}")

    if defects:
        print("Defects:")
        for defect in defects:
            print(f"- {defect}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
