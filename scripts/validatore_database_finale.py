from pathlib import Path
import json
import sys
from collections import Counter

ROOT = Path.cwd()
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

REPORT_MD = REPORTS / "validatore_database_finale.md"
REPORT_JSON = REPORTS / "validatore_database_finale.json"

OFFICIAL_FILES = [
    "data/scienze.json",
    "data/biologia.json",
    "data/chimica.json",
    "data/fisica.json",
    "data/fisica_quantistica.json",
    "data/ai.json",
    "data/informatica.json",
    "data/matematica.json",
    "data/inglese.json",
    "data/logica/logica_numerica.json",
    "data/logica/logica_verbale.json",
    "data/logica/ragionamento_astratto.json",
    "data/logica/ragionamento_critico.json",
    "data/logica/logica_visiva.json",
]

FINAL_DB = ROOT / "dist/database_quiz_finale.json"


def load_questions(path):
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["domande", "questions", "quiz", "data"]:
            value = data.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(f"Formato database non riconosciuto: {path}")


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
    problems = []

    if not FINAL_DB.exists():
        problems.append(f"Database finale mancante: {FINAL_DB}")

    source_questions = []
    source_ids = []

    source_count_by_file = {}

    for relative_path in OFFICIAL_FILES:
        path = ROOT / relative_path

        if not path.exists():
            problems.append(f"File ufficiale mancante: {relative_path}")
            continue

        try:
            questions = load_questions(path)
        except Exception as error:
            problems.append(f"Errore lettura {relative_path}: {error}")
            continue

        source_count_by_file[relative_path] = len(questions)
        source_questions.extend(questions)
        source_ids.extend(get_id(item) for item in questions)

    final_questions = []

    if FINAL_DB.exists():
        try:
            final_questions = load_questions(FINAL_DB)
        except Exception as error:
            problems.append(f"Errore lettura database finale: {error}")

    expected_total = len(source_questions)
    final_total = len(final_questions)

    if final_total != expected_total:
        problems.append(
            f"Numero domande dist non coerente: dist={final_total}, sorgenti={expected_total}"
        )

    source_id_counter = Counter(source_ids)
    duplicate_source_ids = [
        question_id
        for question_id, count in source_id_counter.items()
        if question_id and count > 1
    ]

    if duplicate_source_ids:
        problems.append(
            "ID duplicati nei sorgenti ufficiali: "
            + ", ".join(sorted(duplicate_source_ids)[:40])
        )

    final_ids = [get_id(item) for item in final_questions]
    final_id_counter = Counter(final_ids)

    duplicate_final_ids = [
        question_id
        for question_id, count in final_id_counter.items()
        if question_id and count > 1
    ]

    if duplicate_final_ids:
        problems.append(
            "ID duplicati nel database finale: "
            + ", ".join(sorted(duplicate_final_ids)[:40])
        )

    missing_ids = sorted(set(source_ids) - set(final_ids))
    extra_ids = sorted(set(final_ids) - set(source_ids))

    if missing_ids:
        problems.append(
            "ID sorgenti mancanti nel dist: " + ", ".join(missing_ids[:40])
        )

    if extra_ids:
        problems.append(
            "ID extra nel dist non presenti nei sorgenti: " + ", ".join(extra_ids[:40])
        )

    final_categories = Counter(get_category(item) for item in final_questions)

    result = {
        "esito": "KO" if problems else "OK",
        "totale_sorgenti": expected_total,
        "totale_dist": final_total,
        "conteggio_sorgenti_per_file": source_count_by_file,
        "categorie_dist": dict(final_categories),
        "problemi": problems,
    }

    REPORT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Validatore database finale",
        "",
        f"Totale sorgenti ufficiali: {expected_total}",
        f"Totale dist/database_quiz_finale.json: {final_total}",
        "",
        "## Conteggio sorgenti",
        "",
    ]

    for path, count in source_count_by_file.items():
        lines.append(f"- `{path}`: {count}")

    lines.extend(["", "## Categorie nel database finale", ""])

    for category, count in sorted(final_categories.items()):
        lines.append(f"- `{category or 'senza_categoria'}`: {count}")

    lines.extend(["", "## Problemi", ""])

    if problems:
        for problem in problems:
            lines.append(f"- {problem}")
    else:
        lines.append("✅ Nessun problema trovato.")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    if problems:
        print("❌ Validatore database finale fallito.")
        for problem in problems:
            print("-", problem)
        print(f"Report: {REPORT_MD}")
        sys.exit(1)

    print("✅ Validatore database finale superato.")
    print(f"Sorgenti: {expected_total}")
    print(f"Dist: {final_total}")
    print(f"Report: {REPORT_MD}")


if __name__ == "__main__":
    main()
