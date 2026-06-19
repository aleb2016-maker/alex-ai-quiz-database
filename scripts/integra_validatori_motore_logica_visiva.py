from pathlib import Path
import shutil
import datetime

ROOT = Path.cwd()
SCRIPTS = ROOT / "scripts"
REPORTS = ROOT / "reports"

MOTORE = SCRIPTS / "motore_qualita_logica_visiva.py"
BASE = SCRIPTS / "motore_qualita_logica_visiva_base.py"
REPORT = REPORTS / "integra_validatori_motore_logica_visiva.md"

REPORTS.mkdir(exist_ok=True)

if not MOTORE.exists():
    raise FileNotFoundError(f"Motore non trovato: {MOTORE}")

contenuto_attuale = MOTORE.read_text(encoding="utf-8")

if "WRAPPER_MOTORE_LOGICA_VISIVA" in contenuto_attuale:
    print("✅ Il motore Logica visiva risulta già integrato con i validatori.")
else:
    if not BASE.exists():
        shutil.copy2(MOTORE, BASE)
        base_action = f"Creato backup operativo: `{BASE.relative_to(ROOT)}`"
    else:
        base_action = f"Backup operativo già presente: `{BASE.relative_to(ROOT)}`"

    wrapper = '''#!/usr/bin/env python3
# WRAPPER_MOTORE_LOGICA_VISIVA
# Questo wrapper rende obbligatori i controlli aggiuntivi:
# 1. Nessuna domanda visibile deve suggerire la logica dell'esercizio.
# 2. Risposta, spiegazione e visual_logic devono essere coerenti.
# 3. Dopo questi controlli viene eseguito il motore visuale originale.

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMANDI = [
    [
        sys.executable,
        "scripts/validatore_domande_non_suggerite_logica_visiva.py",
    ],
    [
        sys.executable,
        "scripts/validatore_coerenza_logica_visiva.py",
    ],
    [
        sys.executable,
        "scripts/motore_qualita_logica_visiva_base.py",
    ],
]


def esegui_comando(comando):
    print("")
    print("▶️", " ".join(comando))
    risultato = subprocess.run(comando, cwd=ROOT)

    if risultato.returncode != 0:
        print("")
        print("❌ Motore qualità Logica visiva interrotto.")
        print("Il controllo fallito è:", " ".join(comando))
        sys.exit(risultato.returncode)


def main():
    print("----- MOTORE QUALITÀ LOGICA VISIVA INTEGRATO -----")
    print("Controlli obbligatori:")
    print("- domande non suggerite")
    print("- coerenza risposta/spiegazione/visual_logic")
    print("- qualità visuale originale")

    for comando in COMANDI:
        esegui_comando(comando)

    print("")
    print("✅ Motore qualità Logica visiva integrato superato.")


if __name__ == "__main__":
    main()
'''

    MOTORE.write_text(wrapper, encoding="utf-8")

    REPORT.write_text(
        "\n".join([
            "# Integrazione validatori nel motore Logica visiva",
            "",
            "Il file `scripts/motore_qualita_logica_visiva.py` è stato trasformato in wrapper obbligatorio.",
            "",
            base_action,
            "",
            "Ora il comando principale esegue:",
            "",
            "1. `scripts/validatore_domande_non_suggerite_logica_visiva.py`",
            "2. `scripts/validatore_coerenza_logica_visiva.py`",
            "3. `scripts/motore_qualita_logica_visiva_base.py`",
            "",
            "In questo modo il motore visuale non può più dichiarare 0 problemi ignorando:",
            "",
            "- domande che contengono già la logica dell'esercizio;",
            "- incoerenze tra risposta corretta, spiegazione e visual_logic.",
            "",
        ])
        + "\n",
        encoding="utf-8",
    )

    print("✅ Motore Logica visiva integrato con i validatori.")
    print(base_action)
    print(f"Report: {REPORT}")
