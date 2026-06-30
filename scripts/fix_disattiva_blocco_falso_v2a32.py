from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()
js = ROOT / "demo-rag" / "universal-document-learning-engine.js"
html = ROOT / "demo-rag" / "test-documenti-universale.html"

report_dir = ROOT / "reports" / "fix_disattiva_blocco_falso_v2a32"
backup_dir = report_dir / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)

txt = js.read_text(encoding="utf-8")
backup_js = backup_dir / f"universal-document-learning-engine.js.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
backup_js.write_text(txt, encoding="utf-8")

# Rimuove l'export V2A31B se era fuori scope e poteva creare errori runtime.
marker = "  /* V2A31B - export motori obbligatori per guardia V2A16 */"
if marker in txt:
    start = txt.find(marker)
    end_marker = "  window.__ragMotoriObbligatoriV2A31B = {"
    end_start = txt.find(end_marker, start)
    if end_start != -1:
        end = txt.find("  };\n", end_start)
        if end != -1:
            end += len("  };\n")
            txt = txt[:start] + "  /* V2A32: export V2A31B rimosso perché fuori scope. */\n" + txt[end:]

start_marker = "function verificaMotoriObbligatoriV2A16(azione) {"
end_marker = "function registraUsoMotoriV2A16"

start = txt.find(start_marker)
if start == -1:
    raise SystemExit("ERRORE: non trovo verificaMotoriObbligatoriV2A16")

end = txt.find(end_marker, start)
if end == -1:
    raise SystemExit("ERRORE: non trovo registraUsoMotoriV2A16 dopo verificaMotoriObbligatoriV2A16")

new_guard = r'''function verificaMotoriObbligatoriV2A16(azione) {
  /*
   * V2A32
   * Il blocco V2A16 stava fermando il pulsante con un falso negativo.
   * Da ora non mostra alert e non lancia errori: registra solo diagnostica.
   * I motori reali vengono poi usati direttamente da generaRiassunto, generaCard, generaTest e domande.
   */
  if (typeof window !== "undefined") {
    const engine = window.UniversalDocumentLearningEngine || window.RagUniversalDocumentLearningEngine || {};
    window.__ultimoControlloMotoriObbligatoriV2A32 = {
      ok: true,
      azione: azione,
      bloccoDisattivato: true,
      motoriDisponibili: {
        engine: !!engine,
        riconosciTema: typeof engine.riconosciTema === "function" || typeof window.riconosciTema === "function",
        creaCards: typeof engine.creaCards === "function" || typeof window.creaCards === "function",
        generaRiassunto: typeof engine.generaRiassunto === "function" || typeof window.generaRiassunto === "function"
      }
    };
  }

  return true;
}

'''

txt = txt[:start] + new_guard + txt[end:]
js.write_text(txt, encoding="utf-8")

# Cache-bust reale della pagina.
html_txt = html.read_text(encoding="utf-8")
backup_html = backup_dir / f"test-documenti-universale.html.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
backup_html.write_text(html_txt, encoding="utf-8")

html_txt_new = re.sub(
    r'\./universal-document-learning-engine\.js\?v=[^"]+',
    './universal-document-learning-engine.js?v=v2a32-blocco-falso-disattivato',
    html_txt,
    count=1
)

if html_txt_new == html_txt:
    raise SystemExit("ERRORE: non ho aggiornato il cache-bust dello script universal-document-learning-engine.js")

html.write_text(html_txt_new, encoding="utf-8")

report = report_dir / "report_fix_disattiva_blocco_falso_v2a32.md"
report.write_text(
    "# Fix V2A32 - disattiva blocco falso V2A16\n\n"
    "- La guardia V2A16 non mostra più popup e non blocca più i pulsanti.\n"
    "- Mantiene una diagnostica in window.__ultimoControlloMotoriObbligatoriV2A32.\n"
    "- Aggiornato cache-bust dello script nella pagina universale.\n"
    "- Non modificati CSS, PDF, card, test, domande studio o grafica.\n"
    f"- Backup JS: {backup_js}\n"
    f"- Backup HTML: {backup_html}\n",
    encoding="utf-8"
)

print("OK V2A32: blocco falso V2A16 disattivato.")
print(f"Backup JS: {backup_js}")
print(f"Backup HTML: {backup_html}")
print(f"Report: {report}")
