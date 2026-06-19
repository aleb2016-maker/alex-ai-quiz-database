#!/usr/bin/env python3
# WRAPPER_VALIDATE_QUESTIONS_CORE
# Validatore ufficiale rinforzato.
# Usa solo i database ufficiali e fallisce se trova problemi bloccanti reali.
# Il vecchio validatore storico è conservato in scripts/validate_questions_base.py.

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
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
    print("Controllo obbligatorio:")
    print("- validatore core database ufficiale")

    for command in COMMANDS:
        run_command(command)

    print("")
    print("✅ validate_questions rinforzato superato.")


if __name__ == "__main__":
    main()
