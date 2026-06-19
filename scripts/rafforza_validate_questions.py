from pathlib import Path
import shutil

ROOT = Path.cwd()
SCRIPTS = ROOT / "scripts"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

VALIDATE = SCRIPTS / "validate_questions.py"
BASE = SCRIPTS / "validate_questions_base.py"
REPORT = REPORTS / "rafforza_validate_questions.md"

if not VALIDATE.exists():
    raise FileNotFoundError("scripts/validate_questions.py non trovato")

current = VALIDATE.read_text(encoding="utf-8")

if "WRAPPER_VALIDATE_QUESTIONS_CORE" in current:
    print("✅ validate_questions.py è già rafforzato.")
else:
    if not BASE.exists():
        shutil.copy2(VALIDATE, BASE)
        base_message = "Creato backup operativo `scripts/validate_questions_base.py`."
    else:
        base_message = "Backup operativo già presente `scripts/validate_questions_base.py`."

    wrapper = '''#!/usr/bin/env python3
# WRAPPER_VALIDATE_QUESTIONS_CORE
# Wrapper rinforzato:
# - esegue il validate_questions originale salvato come validate_questions_base.py
# - esegue il nuovo validatore core database
# - fallisce se uno dei controlli fallisce

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "scripts/validate_questions_base.py"],
    [sys.executable, "scripts/validatore_core_database.py"],
]


def run_command(command):
    print("")
    print("▶️", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)

    if result.returncode != 0:
        print("")
        print("❌ validate_questions rinforzato fallito.")
        print("Controllo fallito:", " ".join(command))
        sys.exit(result.returncode)


def main():
    print("----- VALIDATE QUESTIONS RINFORZATO -----")
    print("Controlli obbligatori:")
    print("- validatore originale")
    print("- validatore core database")

    for command in COMMANDS:
        run_command(command)

    print("")
    print("✅ validate_questions rinforzato superato.")


if __name__ == "__main__":
    main()
'''

    VALIDATE.write_text(wrapper, encoding="utf-8")

    REPORT.write_text(
        "\n".join([
            "# Rafforzamento validate_questions.py",
            "",
            base_message,
            "",
            "`scripts/validate_questions.py` ora è un wrapper che esegue:",
            "",
            "1. `scripts/validate_questions_base.py`",
            "2. `scripts/validatore_core_database.py`",
            "",
            "Il comando ora deve fallire se il validatore core trova errori bloccanti.",
            "",
        ])
        + "\n",
        encoding="utf-8",
    )

    print("✅ validate_questions.py rafforzato.")
    print(base_message)
    print(f"Report: {REPORT}")
