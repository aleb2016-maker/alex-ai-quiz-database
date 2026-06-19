from pathlib import Path
import shutil

ROOT = Path.cwd()
SCRIPTS = ROOT / "scripts"
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

BUILD = SCRIPTS / "build_database.py"
BUILD_BASE = SCRIPTS / "build_database_base.py"

CHECK = SCRIPTS / "check_duplicates.py"
CHECK_BASE = SCRIPTS / "check_duplicates_base.py"

REPORT = REPORTS / "rafforza_build_e_check.md"


def backup_and_wrap(path, base_path, wrapper_content, marker):
    if not path.exists():
        raise FileNotFoundError(path)

    current = path.read_text(encoding="utf-8")

    if marker in current:
        return f"`{path.relative_to(ROOT)}` era già rinforzato."

    if not base_path.exists():
        shutil.copy2(path, base_path)
        backup_msg = f"Creato backup operativo `{base_path.relative_to(ROOT)}`."
    else:
        backup_msg = f"Backup operativo già presente `{base_path.relative_to(ROOT)}`."

    path.write_text(wrapper_content, encoding="utf-8")

    return f"Rinforzato `{path.relative_to(ROOT)}`. {backup_msg}"


build_wrapper = '''#!/usr/bin/env python3
# WRAPPER_BUILD_DATABASE_RINFORZATO

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMMANDS = [
    [sys.executable, "scripts/validatore_core_database.py"],
    [sys.executable, "scripts/build_database_base.py"],
    [sys.executable, "scripts/validatore_database_finale.py"],
    [sys.executable, "scripts/validatore_duplicati_database.py"],
]


def run(command):
    print("")
    print("▶️", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)

    if result.returncode != 0:
        print("")
        print("❌ build_database rinforzato fallito.")
        print("Controllo fallito:", " ".join(command))
        sys.exit(result.returncode)


def main():
    print("----- BUILD DATABASE RINFORZATO -----")
    print("Controlli obbligatori:")
    print("- core database prima della build")
    print("- build originale")
    print("- validazione database finale")
    print("- validazione duplicati")

    for command in COMMANDS:
        run(command)

    print("")
    print("✅ build_database rinforzato superato.")


if __name__ == "__main__":
    main()
'''

check_wrapper = '''#!/usr/bin/env python3
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
'''

messages = []

messages.append(
    backup_and_wrap(
        BUILD,
        BUILD_BASE,
        build_wrapper,
        "WRAPPER_BUILD_DATABASE_RINFORZATO",
    )
)

messages.append(
    backup_and_wrap(
        CHECK,
        CHECK_BASE,
        check_wrapper,
        "WRAPPER_CHECK_DUPLICATES_RINFORZATO",
    )
)

REPORT.write_text(
    "\n".join([
        "# Rafforzamento build_database.py e check_duplicates.py",
        "",
        *[f"- {message}" for message in messages],
        "",
        "`build_database.py` ora esegue core check, build originale, validazione dist e duplicati.",
        "",
        "`check_duplicates.py` ora usa il nuovo validatore duplicati ufficiale.",
        "",
    ])
    + "\n",
    encoding="utf-8",
)

for message in messages:
    print("✅", message)

print(f"Report: {REPORT}")
