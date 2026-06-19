#!/usr/bin/env python3
# WRAPPER_CHECK_DUPLICATES_RINFORZATO

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "scripts/validatore_duplicati_database.py"],
]


def run(command):
    print("")
    print("▶️", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)

    if result.returncode != 0:
        print("")
        print("❌ check_duplicates rinforzato fallito.")
        print("Controllo fallito:", " ".join(command))
        sys.exit(result.returncode)


def main():
    print("----- CHECK DUPLICATES RINFORZATO -----")
    print("Controllo ufficiale:")
    print("- validatore duplicati database")

    for command in COMMANDS:
        run(command)

    print("")
    print("✅ check_duplicates rinforzato superato.")


if __name__ == "__main__":
    main()
