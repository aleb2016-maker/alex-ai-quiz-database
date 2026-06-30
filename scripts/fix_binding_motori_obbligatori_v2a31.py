from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
target = ROOT / "demo-rag" / "universal-document-learning-engine.js"
report_dir = ROOT / "reports" / "fix_binding_motori_obbligatori_v2a31"
backup_dir = report_dir / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)

txt = target.read_text(encoding="utf-8")
backup = backup_dir / f"universal-document-learning-engine.js.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
backup.write_text(txt, encoding="utf-8")

marker = "/* V2A31 - binding motori obbligatori */"
if marker in txt:
    print("V2A31 già presente, nessuna modifica.")
else:
    injection = r'''
  /* V2A31 - binding motori obbligatori */
  function agganciaMotoriObbligatoriV2A31() {
    if (typeof window === "undefined") return;

    window.profiliDocumento = profiliDocumento;
    window.riconosciTema = riconosciTema;
    window.creaCards = creaCards;
    window.generaRiassunto = generaRiassunto;

    window.__ragMotoriObbligatoriV2A31 = {
      profiliDocumento: profiliDocumento,
      riconosciTema: riconosciTema,
      creaCards: creaCards,
      generaRiassunto: generaRiassunto
    };
  }

'''
    needle = '  function init() {'
    if needle not in txt:
        raise SystemExit("ERRORE: non trovo function init() in universal-document-learning-engine.js")

    txt = txt.replace(needle, injection + needle, 1)

    # Chiama il binding dentro init prima dei listener pulsanti.
    needle2 = '  function init() {\n'
    replacement2 = '  function init() {\n    agganciaMotoriObbligatoriV2A31();\n'
    txt = txt.replace(needle2, replacement2, 1)

    target.write_text(txt, encoding="utf-8")
    (report_dir / "report_fix_binding_motori_obbligatori_v2a31.md").write_text(
        "# Fix binding motori obbligatori V2A31\n\n"
        "- Agganciati a window: profiliDocumento, riconosciTema, creaCards, generaRiassunto.\n"
        "- Non modificati HTML, CSS, PDF, card, test, domande studio.\n"
        f"- Backup: {backup}\n",
        encoding="utf-8"
    )
    print("OK V2A31: binding motori obbligatori applicato.")
    print(f"Backup creato: {backup}")
