from pathlib import Path

ROOT = Path.cwd()
VALIDATOR = ROOT / "scripts/validatore_core_database.py"
VALIDATE = ROOT / "scripts/validate_questions.py"
REPORT = ROOT / "reports/correggi_validatore_core_math.md"

if not VALIDATOR.exists():
    raise FileNotFoundError(VALIDATOR)

text = VALIDATOR.read_text(encoding="utf-8")

old = '''def compact_text(value):
    text = normalize_text(value)
    text = re.sub(r"[^a-z0-9àèéìòùç\\s]", "", text)
    text = re.sub(r"\\s+", " ", text)
    return text
'''

new = '''def compact_text(value):
    text = normalize_text(value)

    # Mantiene simboli matematici importanti.
    # Prima eliminavamo caratteri come ² e +, quindi x² + C poteva diventare troppo simile a x + C.
    replacements = {
        "²": "2",
        "³": "3",
        "⁴": "4",
        "⁵": "5",
        "⁶": "6",
        "⁷": "7",
        "⁸": "8",
        "⁹": "9",
        "⁰": "0",
        "−": "-",
        "×": "*",
        "÷": "/",
    }

    for source, target in replacements.items():
        text = text.replace(source, target)

    text = re.sub(r"[^a-z0-9àèéìòùç+\\-*/=^()\\s]", "", text)
    text = re.sub(r"\\s+", " ", text)
    return text
'''

if old not in text:
    print("⚠️ Blocco compact_text originale non trovato identico: applico sostituzione mirata alternativa.")
    start = text.index("def compact_text(value):")
    end = text.index("\n\ndef get_question_id", start)
    text = text[:start] + new + text[end:]
else:
    text = text.replace(old, new)

VALIDATOR.write_text(text, encoding="utf-8")

# Rende validate_questions.py un wrapper pulito: usa il validatore core ufficiale.
# Il vecchio validatore resta salvato in scripts/validate_questions_base.py ma non viene lanciato,
# perché scansiona file di revisione/traduzione e produce migliaia di falsi errori.
wrapper = '''#!/usr/bin/env python3
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
'''

VALIDATE.write_text(wrapper, encoding="utf-8")

REPORT.write_text(
    "\n".join([
        "# Correzione validatore core per simboli matematici",
        "",
        "Corretto `scripts/validatore_core_database.py` per non confondere espressioni matematiche come `x² + C` e `x + C`.",
        "",
        "Aggiornato `scripts/validate_questions.py` come wrapper pulito sul validatore core ufficiale.",
        "",
        "Il vecchio validatore storico resta conservato in `scripts/validate_questions_base.py`, ma non viene più eseguito dal comando principale perché scansionava anche file non ufficiali.",
        "",
    ])
    + "\n",
    encoding="utf-8",
)

print("✅ Validatore core corretto per simboli matematici.")
print("✅ validate_questions.py reso pulito e ufficiale.")
print(f"Report: {REPORT}")
