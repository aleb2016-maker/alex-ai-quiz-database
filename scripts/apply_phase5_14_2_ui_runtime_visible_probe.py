#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.14.2 — UI RUNTIME VISIBLE PROBE

Scopo:
- evitare uso obbligatorio della Console Chrome;
- aggiungere una guardia DOM contro HierarchyRequestError appendChild;
- aggiungere un pannello visibile in pagina che mostra:
  - connector UI caricato;
  - pulsanti agganciati;
  - funzioni motore browser trovate;
  - necessità eventuale di bridge locale backend Python.

Non modifica motori backend.
Non modifica PDF.
Non usa fallback/demo.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import List


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "demo-rag" / "test-documenti-universale.html"

DOM_GUARD = ROOT / "demo-rag" / "phase5-14-2-dom-safety-guard.js"
RUNTIME_PANEL = ROOT / "demo-rag" / "phase5-14-2-runtime-visible-panel.js"

REPORT_JSON = ROOT / "reports" / "phase5_14_2_ui_runtime_visible_probe_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_14_2_ui_runtime_visible_probe_v1.md"


@dataclass
class Report:
    phase: str
    status: str
    page: str
    dom_guard: str
    runtime_panel: str
    injected_dom_guard: bool
    injected_runtime_panel: bool
    defects: List[str]
    warnings: List[str]


DOM_GUARD_CODE = r'''/*
FASE 5.14.2 — DOM SAFETY GUARD

Evita che vecchi script di layout blocchino la pagina con:
HierarchyRequestError: appendChild - new child contains the parent.

Non genera output.
Non modifica i motori.
*/

(function () {
  "use strict";

  if (window.__phase5_14_2_dom_guard_installed__) return;
  window.__phase5_14_2_dom_guard_installed__ = true;

  const originalAppendChild = Node.prototype.appendChild;

  window.__phase5_14_2_dom_guard__ = {
    phase: "5.14.2",
    blockedAppendChild: 0,
    active: true
  };

  Node.prototype.appendChild = function phase5142SafeAppendChild(child) {
    try {
      if (
        child &&
        typeof child.contains === "function" &&
        child.contains(this)
      ) {
        window.__phase5_14_2_dom_guard__.blockedAppendChild += 1;
        console.warn(
          "[Phase 5.14.2] appendChild bloccato: il nuovo figlio contiene il parent.",
          { parent: this, child: child }
        );
        return child;
      }
    } catch (error) {
      console.warn("[Phase 5.14.2] DOM guard warning:", error);
    }

    return originalAppendChild.call(this, child);
  };

  console.log("[Phase 5.14.2] DOM safety guard attivo");
})();
'''


RUNTIME_PANEL_CODE = r'''/*
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
'''


def inject_before_first_existing_script(html: str, script_tag: str) -> tuple[str, bool]:
    if script_tag in html:
        return html, False

    first_script = html.find("<script")
    if first_script >= 0:
        return html[:first_script] + script_tag + "\n" + html[first_script:], True

    if "</body>" in html:
        return html.replace("</body>", script_tag + "\n</body>", 1), True

    return html + "\n" + script_tag + "\n", True


def inject_before_body_close(html: str, script_tag: str) -> tuple[str, bool]:
    if script_tag in html:
        return html, False

    if "</body>" in html:
        return html.replace("</body>", "  " + script_tag + "\n</body>", 1), True

    return html + "\n" + script_tag + "\n", True


def render_md(report: Report) -> str:
    lines = [
        "# FASE 5.14.2 — UI RUNTIME VISIBLE PROBE",
        "",
        f"Status: `{report.status}`",
        "",
        f"- Pagina: `{report.page}`",
        f"- DOM guard: `{report.dom_guard}`",
        f"- Runtime panel: `{report.runtime_panel}`",
        f"- DOM guard injected: `{report.injected_dom_guard}`",
        f"- Runtime panel injected: `{report.injected_runtime_panel}`",
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
        "- Questa fase evita l'uso obbligatorio della Console Chrome.",
        "- Aggiunge un pannello visibile direttamente nella pagina.",
        "- Se non trova funzioni motore browser, il passo successivo è il bridge locale backend.",
        "- Non modifica i motori backend.",
    ]

    return "\n".join(lines) + "\n"


def main() -> int:
    defects: List[str] = []
    warnings: List[str] = []

    if not PAGE.exists():
        defects.append(f"Pagina non trovata: {PAGE}")
        html = ""
        injected_guard = False
        injected_panel = False
    else:
        DOM_GUARD.write_text(DOM_GUARD_CODE, encoding="utf-8")
        RUNTIME_PANEL.write_text(RUNTIME_PANEL_CODE, encoding="utf-8")

        html = PAGE.read_text(encoding="utf-8", errors="replace")

        guard_tag = '<script src="phase5-14-2-dom-safety-guard.js"></script>'
        panel_tag = '<script src="phase5-14-2-runtime-visible-panel.js"></script>'

        html, injected_guard = inject_before_first_existing_script(html, guard_tag)
        html, injected_panel = inject_before_body_close(html, panel_tag)

        PAGE.write_text(html, encoding="utf-8")

    status = (
        "PASS - Fase 5.14.2: UI_RUNTIME_VISIBLE_PROBE_APPLIED"
        if not defects
        else "FAIL - Fase 5.14.2: UI_RUNTIME_VISIBLE_PROBE_NOT_APPLIED"
    )

    report = Report(
        phase="5.14.2",
        status=status,
        page=str(PAGE.relative_to(ROOT)),
        dom_guard=str(DOM_GUARD.relative_to(ROOT)),
        runtime_panel=str(RUNTIME_PANEL.relative_to(ROOT)),
        injected_dom_guard=injected_guard,
        injected_runtime_panel=injected_panel,
        defects=defects,
        warnings=warnings,
    )

    REPORT_JSON.write_text(json.dumps(asdict(report), ensure_ascii=False, indent=2), encoding="utf-8")
    REPORT_MD.write_text(render_md(report), encoding="utf-8")

    print(status)
    print(f"Page: {report.page}")
    print(f"DOM guard: {report.dom_guard}")
    print(f"Runtime panel: {report.runtime_panel}")
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
