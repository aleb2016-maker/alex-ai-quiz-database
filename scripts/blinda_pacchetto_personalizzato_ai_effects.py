from pathlib import Path
import re
import datetime

ROOT = Path.cwd()
SCRIPT_PATH = ROOT / "scripts/create_quiz_package.py"
REPORT_PATH = ROOT / "reports/blinda_pacchetto_personalizzato_ai_effects.md"

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

if not SCRIPT_PATH.exists():
    raise FileNotFoundError("Non trovo scripts/create_quiz_package.py")

testo = SCRIPT_PATH.read_text(encoding="utf-8")
backup = SCRIPT_PATH.with_suffix(SCRIPT_PATH.suffix + f".bak_{STAMP}")
backup.write_text(testo, encoding="utf-8")

# Garantisce import Path.
if "from pathlib import Path" not in testo:
    testo = "from pathlib import Path\n" + testo

helper = '''
# AI_ITS_RUNTIME_EFFECTS_START
RUNTIME_WEB_DIR = Path(__file__).resolve().parents[1] / "runtime" / "web"

def _leggi_runtime_ai_effects(nome_file):
    percorso = RUNTIME_WEB_DIR / nome_file

    if not percorso.exists():
        raise FileNotFoundError(f"Runtime effetti AI ITS non trovato: {percorso}")

    return percorso.read_text(encoding="utf-8").strip() + "\\n"
# AI_ITS_RUNTIME_EFFECTS_END

'''.lstrip()

# Rimuove eventuale helper precedente.
testo = re.sub(
    r"# AI_ITS_RUNTIME_EFFECTS_START.*?# AI_ITS_RUNTIME_EFFECTS_END\n\n",
    "",
    testo,
    flags=re.DOTALL
)

# Inserisce helper prima delle costanti effetti.
match = re.search(r"^ALEX_AI_EFFECTS_(JS|CSS)\s*=", testo, flags=re.MULTILINE)

if not match:
    raise RuntimeError("Non trovo le costanti ALEX_AI_EFFECTS_JS/CSS da aggiornare.")

testo = testo[:match.start()] + helper + testo[match.start():]

# Sostituisce le vecchie costanti incorporate con lettura diretta da runtime/web.
testo, count_js = re.subn(
    r"^ALEX_AI_EFFECTS_JS\s*=.*$",
    'ALEX_AI_EFFECTS_JS = _leggi_runtime_ai_effects("ai-effects.js")',
    testo,
    count=1,
    flags=re.MULTILINE
)

testo, count_css = re.subn(
    r"^ALEX_AI_EFFECTS_CSS\s*=.*$",
    'ALEX_AI_EFFECTS_CSS = _leggi_runtime_ai_effects("ai-effects.css")',
    testo,
    count=1,
    flags=re.MULTILINE
)

if count_js != 1:
    raise RuntimeError("Non sono riuscito a sostituire ALEX_AI_EFFECTS_JS.")

if count_css != 1:
    raise RuntimeError("Non sono riuscito a sostituire ALEX_AI_EFFECTS_CSS.")

SCRIPT_PATH.write_text(testo, encoding="utf-8")

REPORT_PATH.parent.mkdir(exist_ok=True)
REPORT_PATH.write_text(
    "\n".join([
        "# Blindatura pacchetto personalizzato AI ITS",
        "",
        "Il generatore del pacchetto personalizzato ora non usa più il vecchio codice effetti incorporato.",
        "",
        "Adesso legge sempre questi file aggiornati:",
        "",
        "- `runtime/web/ai-effects.js`",
        "- `runtime/web/ai-effects.css`",
        "",
        "Questo evita che demo online, pacchetto Web AI ITS e pacchetto personalizzato abbiano logiche premio diverse.",
        "",
        f"Backup temporaneo creato: `{backup.relative_to(ROOT)}`",
        ""
    ]),
    encoding="utf-8"
)

print("✅ Pacchetto personalizzato blindato.")
print(f"Report: {REPORT_PATH}")
print(f"Backup: {backup}")
