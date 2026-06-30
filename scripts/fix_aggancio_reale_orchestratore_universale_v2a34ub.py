from pathlib import Path
from datetime import datetime
import re

ROOT = Path.cwd()

universal = ROOT / "demo-rag" / "universal-document-learning-engine.js"
html = ROOT / "demo-rag" / "test-documenti-universale.html"

report_dir = ROOT / "reports" / "fix_aggancio_reale_orchestratore_universale_v2a34ub"
backup_dir = report_dir / "backups"
backup_dir.mkdir(parents=True, exist_ok=True)

ts = datetime.now().strftime("%Y%m%d_%H%M%S")

backup_universal = backup_dir / f"universal-document-learning-engine.js.{ts}.bak"
backup_html = backup_dir / f"test-documenti-universale.html.{ts}.bak"

txt = universal.read_text(encoding="utf-8")
html_txt = html.read_text(encoding="utf-8")

backup_universal.write_text(txt, encoding="utf-8")
backup_html.write_text(html_txt, encoding="utf-8")

print(f"Backup JS creato: {backup_universal}")
print(f"Backup HTML creato: {backup_html}")

if "function applicaOrchestratoreRiassuntoUniversaleV2A34U" not in txt:
    raise SystemExit("ERRORE: il ponte V2A34U non è presente nel motore principale.")

if "window.RagSummaryUniversalOrchestratorV2A34U" not in txt:
    raise SystemExit("ERRORE: il ponte V2A34U non vede il pacchetto universale su window.")

old_const = "    const sezioniFinali = miglioraSezioniRiassuntoLungoV2A33(qualita.sezioni, progressive, reportLungo, testo, profilo);"
new_let = "    let sezioniFinali = miglioraSezioniRiassuntoLungoV2A33(qualita.sezioni, progressive, reportLungo, testo, profilo);"

if old_const in txt:
    txt = txt.replace(old_const, new_let, 1)
elif new_let not in txt:
    raise SystemExit("ERRORE: non trovo la riga sezioniFinali del riassunto lungo.")

call_block = '''    /* V2A34U-B - aggancio reale orchestratore universale prima del render finale */
    sezioniFinali = applicaOrchestratoreRiassuntoUniversaleV2A34U(
      testo,
      profilo,
      reportLungo,
      progressive,
      sezioniFinali,
      qualita
    );

'''

# Controllo preciso: non basta che il nome funzione esista nella dichiarazione.
if "sezioniFinali = applicaOrchestratoreRiassuntoUniversaleV2A34U(" not in txt:
    anchor = new_let + "\n"
    if anchor not in txt:
        raise SystemExit("ERRORE: non trovo il punto esatto dove inserire la chiamata V2A34U-B.")

    txt = txt.replace(anchor, anchor + "\n" + call_block, 1)
else:
    print("Chiamata V2A34U-B già presente: non duplico.")

# Aggiunge diagnostica visibile su window subito prima del render, senza cambiare UI.
diagnostic_anchor = "    window.__ragRiassuntoLungoSezioniV2A28 = sezioniFinali;"

diagnostic_block = '''    window.__ragRiassuntoUniversaleV2A34UB = {
      attivo: true,
      sezioni: Array.isArray(sezioniFinali) ? sezioniFinali.length : 0,
      primoTitolo: Array.isArray(sezioniFinali) && sezioniFinali[0] ? sezioniFinali[0].titolo : "",
      usaOrchestratoreUniversale: true
    };
'''

if diagnostic_anchor in txt and "__ragRiassuntoUniversaleV2A34UB" not in txt:
    txt = txt.replace(diagnostic_anchor, diagnostic_block + diagnostic_anchor, 1)

universal.write_text(txt, encoding="utf-8")

# Cache-bust tecnico, nessuna modifica grafica.
html_txt = re.sub(
    r'\./universal-document-learning-engine\.js\?v=[^"]+',
    './universal-document-learning-engine.js?v=v2a34ub-aggancio-reale',
    html_txt,
    count=1
)

html_txt = re.sub(
    r'\./rag-summary-universal-orchestrator-v2a34u\.js\?v=[^"]+',
    './rag-summary-universal-orchestrator-v2a34u.js?v=v2a34ub-universal-active',
    html_txt,
    count=1
)

html.write_text(html_txt, encoding="utf-8")

report = report_dir / "report_fix_aggancio_reale_orchestratore_universale_v2a34ub.md"
report.write_text(
    "# V2A34U-B - Aggancio reale orchestratore universale\n\n"
    "Problema trovato:\n"
    "- Il pacchetto universale V2A34U era caricato nella pagina.\n"
    "- Il ponte V2A34U era presente nel motore principale.\n"
    "- Però il ponte non veniva chiamato prima del render finale del riassunto.\n"
    "- Quindi il browser continuava a mostrare il vecchio riassunto estrattivo V2A33.\n\n"
    "Correzione applicata:\n"
    "- Convertita `const sezioniFinali` in `let sezioniFinali` nel punto del riassunto lungo.\n"
    "- Inserita la chiamata reale a `applicaOrchestratoreRiassuntoUniversaleV2A34U(...)` prima di `renderizzaRiassuntoLungoV2A28(...)`.\n"
    "- Aggiunta diagnostica `window.__ragRiassuntoUniversaleV2A34UB`.\n"
    "- Aggiornato solo cache-bust tecnico degli script.\n\n"
    "Vincoli rispettati:\n"
    "- Non modificati pulsanti.\n"
    "- Non modificata interfaccia grafica.\n"
    "- Non modificati CSS.\n"
    "- Non modificati PDF.\n"
    "- Non modificati card, test o domande studio.\n"
    "- Non modificati i motori già funzionanti.\n",
    encoding="utf-8"
)

print("OK V2A34U-B: orchestratore universale agganciato davvero prima del render finale.")
print(f"Report: {report}")
