#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RAG V3.5L-b
Micro-correzione universale UI:
1) deduplica badge visibili categoria/sottocategoria: "X · X" -> "X".
2) collega il selezionatore RAG V3.5K/V3.5L alle pagine principali esistenti.

Non tocca metadati JSON, id tecnici o vecchi pulsanti esistenti.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

ROOT = Path.cwd()
TEST_PAGE = ROOT / "demo-rag" / "test-selezionatore-output-v35h.html"
REPORT = ROOT / "reports" / "rag_badge_ui_e_link_main_v35l.md"

BADGE_SCRIPT_ID = "rag-v35l-badge-dedup"
BADGE_SCRIPT = r'''
<script id="rag-v35l-badge-dedup">
(function () {
  "use strict";

  function normalizzaBadgeParte(value) {
    return String(value || "")
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/\s+/g, " ")
      .trim()
      .toLowerCase();
  }

  function deduplicaBadgeTesto(testo) {
    var originale = String(testo || "").replace(/\s+/g, " ").trim();
    if (!originale || originale.indexOf(" · ") === -1) return originale;

    var parti = originale.split(" · ").map(function (p) { return p.trim(); }).filter(Boolean);
    if (parti.length !== 2) return originale;

    if (normalizzaBadgeParte(parti[0]) === normalizzaBadgeParte(parti[1])) {
      return parti[0];
    }
    return originale;
  }

  function nodoBadgePossibile(el) {
    if (!el || !el.textContent) return false;
    var testo = el.textContent.replace(/\s+/g, " ").trim();
    if (testo.indexOf(" · ") === -1) return false;
    if (testo.length > 120) return false;

    var tag = (el.tagName || "").toLowerCase();
    var cls = String(el.className || "").toLowerCase();

    return tag === "span" || tag === "button" || tag === "a" ||
      cls.indexOf("badge") >= 0 || cls.indexOf("pill") >= 0 ||
      cls.indexOf("tag") >= 0 || cls.indexOf("chip") >= 0 ||
      cls.indexOf("categoria") >= 0 || cls.indexOf("category") >= 0;
  }

  function applicaDeduplicaBadge() {
    var selettore = [
      "span", "button", "a",
      "[class*='badge']", "[class*='Badge']",
      "[class*='pill']", "[class*='Pill']",
      "[class*='tag']", "[class*='Tag']",
      "[class*='chip']", "[class*='Chip']",
      "[class*='categoria']", "[class*='Categoria']",
      "[class*='category']", "[class*='Category']"
    ].join(",");

    document.querySelectorAll(selettore).forEach(function (el) {
      if (!nodoBadgePossibile(el)) return;
      var pulito = deduplicaBadgeTesto(el.textContent);
      if (pulito && pulito !== el.textContent.replace(/\s+/g, " ").trim()) {
        el.textContent = pulito;
        el.setAttribute("data-v35l-badge-dedup", "ok");
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", applicaDeduplicaBadge);
  } else {
    applicaDeduplicaBadge();
  }

  var observer = new MutationObserver(function () {
    applicaDeduplicaBadge();
  });
  observer.observe(document.documentElement, { childList: true, subtree: true, characterData: true });
})();
</script>
'''.strip()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def inject_before_body_end(html: str, block: str) -> str:
    if "</body>" in html:
        return html.replace("</body>", block + "\n</body>", 1)
    return html.rstrip() + "\n" + block + "\n"


def patch_test_page() -> list[str]:
    logs: list[str] = []
    if not TEST_PAGE.exists():
        raise FileNotFoundError(f"Pagina test non trovata: {TEST_PAGE}")

    html = read_text(TEST_PAGE)
    original = html

    # Rimuove eventuali versioni precedenti dello stesso blocco, poi reinserisce una sola volta.
    html = re.sub(
        r"\n?\s*<script id=\"rag-v35l-badge-dedup\">.*?</script>\s*\n?",
        "\n",
        html,
        flags=re.S,
    )
    html = inject_before_body_end(html, BADGE_SCRIPT)

    # Sicurezza: non devono ricomparire vecchi path rotti/label vecchie.
    html = html.replace("output_cleaner_finale_v35k.json();", "output_cleaner_finale_v35k.json")
    html = html.replace("V3.5J", "V3.5K")

    if html != original:
        write_text(TEST_PAGE, html)
        logs.append("OK: patch UI badge universale inserita nella pagina V3.5H")
    else:
        logs.append("OK: pagina V3.5H gia aggiornata")
    return logs


def link_block_for(href: str) -> str:
    return f'''
<!-- RAG_V35L_LINK_START -->
<section id="rag-v35l-main-link" style="margin:32px 0;padding:22px;border-radius:20px;border:1px solid rgba(80,220,170,.45);background:linear-gradient(135deg,rgba(15,35,55,.92),rgba(20,70,65,.78));box-shadow:0 12px 28px rgba(0,0,0,.22);">
  <h2 style="margin:0 0 10px;color:#eaf4ff;">Motore RAG documenti · V3.5K/V3.5L</h2>
  <p style="margin:0 0 16px;color:#c7d6ea;line-height:1.55;">Apri il selezionatore completo con riassunto, card, domande studio, test interattivo e gate qualità universale.</p>
  <a href="{href}" style="display:inline-block;padding:13px 18px;border-radius:14px;background:#0b7f6f;color:#ffffff;text-decoration:none;font-weight:800;border:1px solid rgba(255,255,255,.22);">Apri selezionatore RAG completo</a>
</section>
<!-- RAG_V35L_LINK_END -->
'''.strip()


def patch_main_page(path: Path, href: str) -> str:
    html = read_text(path)
    if "RAG_V35L_LINK_START" in html:
        return f"OK: link gia presente in {path.relative_to(ROOT)}"

    block = link_block_for(href)
    patched = inject_before_body_end(html, block)
    write_text(path, patched)
    return f"OK: link V3.5K/V3.5L aggiunto a {path.relative_to(ROOT)}"


def patch_main_pages() -> list[str]:
    logs: list[str] = []
    candidates = [
        (ROOT / "demo-rag" / "index.html", "test-selezionatore-output-v35h.html"),
        (ROOT / "demo" / "index.html", "../demo-rag/test-selezionatore-output-v35h.html"),
        (ROOT / "index.html", "demo-rag/test-selezionatore-output-v35h.html"),
    ]
    patched_any = False
    for path, href in candidates:
        if path.exists():
            logs.append(patch_main_page(path, href))
            patched_any = True
    if not patched_any:
        logs.append("AVVISO: nessuna pagina principale trovata tra demo-rag/index.html, demo/index.html, index.html")
    return logs


def run_verifier() -> tuple[int, str]:
    verifier = ROOT / "scripts" / "verifica_rag_demo_selezionatore_output_v35h.py"
    if not verifier.exists():
        return 1, "verifier mancante"
    proc = subprocess.run(
        ["python3", str(verifier)],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    return proc.returncode, proc.stdout


def main() -> int:
    logs: list[str] = []
    errors: list[str] = []

    print("=== V3.5L-B BADGE UI + COLLEGAMENTO MAIN ===")

    try:
        logs.extend(patch_test_page())
        logs.extend(patch_main_pages())
    except Exception as exc:
        errors.append(str(exc))

    # Controlli statici sulla pagina test.
    if TEST_PAGE.exists():
        html = read_text(TEST_PAGE)
        if "Ripasso guidato · ripasso guidato" in html:
            errors.append("pagina contiene ancora duplicazione statica Ripasso guidato · ripasso guidato")
        if "json();" in html:
            errors.append("pagina contiene ancora json();")
        if "V3.5J" in html:
            errors.append("pagina contiene ancora V3.5J")
        if BADGE_SCRIPT_ID not in html:
            errors.append("script badge dedup V3.5L-B non inserito")

    code, out = run_verifier()
    if code == 0 and "ESITO: OK" in out:
        logs.append("OK: verifier pagina V3.5H")
    else:
        errors.append("verifier pagina V3.5H non OK")
        logs.append(out)

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Report RAG V3.5L-B Badge UI e Collegamento Main",
        "",
        "Scopo: micro-correzione universale UI, non patch su frasi specifiche.",
        "",
        "## Regole",
        "- se un badge visibile contiene `X · X`, mostra solo `X`",
        "- se un badge contiene `X · Y` con X diverso da Y, lo lascia invariato",
        "- collega il selezionatore RAG V3.5K/V3.5L alle pagine principali esistenti senza modificare i pulsanti già presenti",
        "",
        "## Risultati",
    ]
    for log in logs:
        lines.append(f"- {log}")
    lines += ["", f"Errori totali: {len(errors)}"]
    if errors:
        lines += ["", "## Errori"] + [f"- {e}" for e in errors]
    lines += ["", "ESITO: " + ("OK" if not errors else "DA CORREGGERE")]
    write_text(REPORT, "\n".join(lines) + "\n")

    for log in logs:
        print(log)
    if errors:
        for e in errors:
            print("ERRORE:", e)

    print(f"Report: {REPORT.relative_to(ROOT)}")
    print("ESITO:", "OK" if not errors else "DA CORREGGERE")
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
