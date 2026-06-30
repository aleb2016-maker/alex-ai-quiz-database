from pathlib import Path
from datetime import datetime

ROOT = Path.cwd()
target = ROOT / "demo-rag" / "universal-document-learning-engine.js"

report_dir = ROOT / "reports" / "fix_binding_motori_obbligatori_v2a31b"
backup_dir = report_dir / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)

txt = target.read_text(encoding="utf-8")

backup = backup_dir / f"universal-document-learning-engine.js.{datetime.now().strftime('%Y%m%d_%H%M%S')}.bak"
backup.write_text(txt, encoding="utf-8")

marker = "/* V2A31B - export motori obbligatori per guardia V2A16 */"

if marker in txt:
    print("V2A31B già presente, nessuna modifica.")
else:
    needle = "  window.registraUsoMotoriV2A16 = registraUsoMotoriV2A16;"
    if needle not in txt:
        raise SystemExit("ERRORE: non trovo il punto sicuro window.registraUsoMotoriV2A16")

    injection = '''
  /* V2A31B - export motori obbligatori per guardia V2A16 */
  window.profiliDocumento = profiliDocumento;
  window.riconosciTema = riconosciTema;
  window.creaCards = creaCards;
  window.generaRiassunto = generaRiassunto;

  window.__ragMotoriObbligatoriV2A31B = {
    profiliDocumento: profiliDocumento,
    riconosciTema: riconosciTema,
    creaCards: creaCards,
    generaRiassunto: generaRiassunto
  };
'''

    txt = txt.replace(needle, needle + "\n" + injection, 1)

    target.write_text(txt, encoding="utf-8")

    report = report_dir / "report_fix_binding_motori_obbligatori_v2a31b.md"
    report.write_text(
        "# Fix binding motori obbligatori V2A31B\n\n"
        "- Agganciati a window: profiliDocumento, riconosciTema, creaCards, generaRiassunto.\n"
        "- Fix applicato dopo window.registraUsoMotoriV2A16.\n"
        "- Non modificati HTML, CSS, PDF, card, test, domande studio.\n"
        f"- Backup: {backup}\n",
        encoding="utf-8"
    )

    print("OK V2A31B: binding motori obbligatori applicato.")
    print(f"Backup creato: {backup}")
    print(f"Report scritto: {report}")
