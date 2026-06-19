#!/usr/bin/env python3
# BUILD_DATABASE_UFFICIALE_RINFORZATO
# Costruisce dist/database_quiz_finale.json SOLO dai database ufficiali.
# Non legge backup, revisioni, traduzioni o file di appoggio.

from pathlib import Path
import json
import subprocess
import sys
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
REPORTS = ROOT / "reports"

DIST.mkdir(exist_ok=True)
REPORTS.mkdir(exist_ok=True)

OUTPUT = DIST / "database_quiz_finale.json"
REPORT_MD = REPORTS / "build_database.md"
REPORT_JSON = REPORTS / "build_database.json"

OFFICIAL_FILES = [
    ("Scienze generali", "data/scienze.json"),
    ("Biologia", "data/biologia.json"),
    ("Chimica", "data/chimica.json"),
    ("Fisica", "data/fisica.json"),
    ("Fisica quantistica", "data/fisica_quantistica.json"),
    ("AI", "data/ai.json"),
    ("Informatica", "data/informatica.json"),
    ("Matematica", "data/matematica.json"),
    ("Inglese", "data/inglese.json"),
    ("Logica numerica", "data/logica/logica_numerica.json"),
    ("Logica verbale", "data/logica/logica_verbale.json"),
    ("Ragionamento astratto", "data/logica/ragionamento_astratto.json"),
    ("Ragionamento critico", "data/logica/ragionamento_critico.json"),
    ("Logica visiva", "data/logica/logica_visiva.json"),
]


def run(command):
    print("")
    print("▶️", " ".join(command))
    result = subprocess.run(command, cwd=ROOT)

    if result.returncode != 0:
        print("")
        print("❌ Build database interrotta.")
        print("Controllo fallito:", " ".join(command))
        sys.exit(result.returncode)


def load_questions(path):
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, list):
        raise ValueError(f"{path} deve contenere una lista di domande")

    return data


def get_id(item):
    return str(
        item.get("id")
        or item.get("codice")
        or item.get("question_id")
        or item.get("uid")
        or ""
    ).strip()


def get_category(item):
    return str(item.get("categoria") or item.get("category") or "").strip().lower()


def main():
    print("----- BUILD DATABASE UFFICIALE RINFORZATO -----")

    # Prima controlla i sorgenti ufficiali.
    run([sys.executable, "scripts/validatore_core_database.py"])

    all_questions = []
    counts_by_file = {}
    problems = []

    for label, relative_path in OFFICIAL_FILES:
        path = ROOT / relative_path
        print(f"Leggo sorgente ufficiale: {relative_path}")

        if not path.exists():
            problems.append(f"File mancante: {relative_path}")
            continue

        try:
            questions = load_questions(path)
        except Exception as error:
            problems.append(f"Errore in {relative_path}: {error}")
            continue

        counts_by_file[relative_path] = len(questions)
        all_questions.extend(questions)

    ids = [get_id(item) for item in all_questions]
    duplicate_ids = [
        question_id
        for question_id, count in Counter(ids).items()
        if question_id and count > 1
    ]

    if duplicate_ids:
        problems.append(
            "ID duplicati nei sorgenti ufficiali: "
            + ", ".join(sorted(duplicate_ids)[:50])
        )

    if problems:
        for problem in problems:
            print("❌", problem)
        sys.exit(1)

    OUTPUT.write_text(
        json.dumps(all_questions, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    categories = Counter(get_category(item) for item in all_questions)

    result = {
        "esito": "OK",
        "output": str(OUTPUT.relative_to(ROOT)),
        "totale_domande": len(all_questions),
        "conteggio_per_file": counts_by_file,
        "conteggio_per_categoria": dict(categories),
    }

    REPORT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Build database ufficiale rinforzato",
        "",
        f"Output: `{OUTPUT.relative_to(ROOT)}`",
        f"Totale domande: {len(all_questions)}",
        "",
        "## Conteggio per file",
        "",
    ]

    for path, count in counts_by_file.items():
        lines.append(f"- `{path}`: {count}")

    lines.extend(["", "## Conteggio per categoria", ""])

    for category, count in sorted(categories.items()):
        lines.append(f"- `{category or 'senza_categoria'}`: {count}")

    lines.extend(["", "## Esito", "", "✅ Build completata correttamente."])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("")
    print("✅ Build database completata.")
    print(f"Output: {OUTPUT}")
    print(f"Totale domande: {len(all_questions)}")
    print(f"Report: {REPORT_MD}")

    # Dopo la build controlla dist e duplicati.
    run([sys.executable, "scripts/validatore_database_finale.py"])
    run([sys.executable, "scripts/validatore_duplicati_database.py"])

    print("")
    print("✅ build_database.py rinforzato superato.")


if __name__ == "__main__":
    main()
