from pathlib import Path
import json
import zipfile
import tempfile
import shutil
import datetime
import re
import sys

ROOT = Path.cwd()
DATA_PATH = ROOT / "data/logica/logica_visiva.json"
REPORT_PATH = ROOT / "reports/correzione_domande_suggerite_logica_visiva.md"
BACKUP_DIR = ROOT / "backups"

BACKUP_DIR.mkdir(exist_ok=True)
REPORT_PATH.parent.mkdir(exist_ok=True)

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
GENERIC_QUESTION = "Osserva la sequenza visiva e scegli la figura successiva."

TARGET_JSONS = [
    ROOT / "demo-ai/database_quiz.json",
    ROOT / "dist/database_quiz_finale.json",
]

TARGET_ZIPS = [
    ROOT / "downloads/pacchetto-web-ai-its-demo.zip",
    ROOT / "downloads/pacchetto-android-ai-its-finale-semplice.zip",
]

LEAK_PATTERNS = [
    "la risposta corretta",
    "deve rispettare",
    "forma resta",
    "forma aumenta",
    "forma cresce",
    "colore alterna",
    "colore resta",
    "lati aumentano",
    "aumenta il numero di lati",
    "numero di lati",
    "pallini interni",
    "quadratini interni",
    "triangoli interni",
    "triangolo interno",
    "oggetti interni",
    "resta un triangolo",
    "restano tre",
    "aumentano di uno",
    "alternano tre",
]


def get_id(item):
    if not isinstance(item, dict):
        return ""

    return str(
        item.get("id")
        or item.get("codice")
        or item.get("question_id")
        or item.get("uid")
        or ""
    )


def is_log_vis(codice):
    return codice.startswith("LOG-VIS")


def get_question_key(item):
    for key in ["domanda", "question", "testo"]:
        if key in item:
            return key

    return "domanda"


def contains_leak(text):
    lower = str(text).lower()
    return [pattern for pattern in LEAK_PATTERNS if pattern in lower]


def backup_file(path):
    backup = BACKUP_DIR / f"{path.name}.backup_prima_domande_suggerite_{STAMP}"
    shutil.copy2(path, backup)
    return backup


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def fix_source_database():
    data = load_json(DATA_PATH)
    changed_ids = []
    already_clean = []

    for item in data:
        codice = get_id(item)

        if not is_log_vis(codice):
            continue

        question_key = get_question_key(item)
        question_text = str(item.get(question_key, ""))

        leaks = contains_leak(question_text)

        if leaks:
            item[question_key] = GENERIC_QUESTION
            changed_ids.append({
                "id": codice,
                "leaks": leaks,
                "old_question": question_text,
            })
        else:
            already_clean.append(codice)

    backup = None

    if changed_ids:
        backup = backup_file(DATA_PATH)
        write_json(DATA_PATH, data)

    return data, changed_ids, already_clean, backup


def build_source_map(source_data):
    return {
        get_id(item): item
        for item in source_data
        if is_log_vis(get_id(item))
    }


def replace_questions(obj, source_by_id):
    count = 0

    if isinstance(obj, list):
        for index, item in enumerate(obj):
            codice = get_id(item)

            if codice in source_by_id:
                obj[index] = source_by_id[codice]
                count += 1
            else:
                count += replace_questions(item, source_by_id)

    elif isinstance(obj, dict):
        codice = get_id(obj)

        if codice in source_by_id:
            obj.clear()
            obj.update(source_by_id[codice])
            return 1

        for value in obj.values():
            count += replace_questions(value, source_by_id)

    return count


def propagate_json(path, source_by_id):
    if not path.exists():
        return {"path": path, "updated": 0, "status": "mancante", "backup": None}

    data = load_json(path)
    updated = replace_questions(data, source_by_id)

    backup = None

    if updated:
        backup = backup_file(path)
        write_json(path, data)

    return {"path": path, "updated": updated, "status": "ok", "backup": backup}


def propagate_zip(path, source_by_id):
    if not path.exists():
        return {
            "path": path,
            "updated": 0,
            "status": "mancante",
            "backup": None,
            "files": [],
        }

    total_updated = 0
    updated_files = []

    with tempfile.TemporaryDirectory() as tmp_name:
        tmp = Path(tmp_name)

        with zipfile.ZipFile(path, "r") as archive:
            archive.extractall(tmp)

        for json_path in tmp.rglob("*.json"):
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
            except Exception:
                continue

            updated = replace_questions(data, source_by_id)

            if updated:
                write_json(json_path, data)
                total_updated += updated
                updated_files.append(str(json_path.relative_to(tmp)))

        backup = None

        if total_updated:
            backup = backup_file(path)

            with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
                for file in tmp.rglob("*"):
                    if file.is_file():
                        archive.write(file, file.relative_to(tmp))

    return {
        "path": path,
        "updated": total_updated,
        "status": "ok",
        "backup": backup,
        "files": updated_files,
    }


source_data, changed_ids, already_clean, source_backup = fix_source_database()
source_by_id = build_source_map(source_data)

results = []

for target in TARGET_JSONS:
    results.append(propagate_json(target, source_by_id))

for target in TARGET_ZIPS:
    results.append(propagate_zip(target, source_by_id))

report = [
    "# Correzione domande suggerite Logica visiva",
    "",
    "Obiettivo: la domanda visibile non deve contenere la logica dell'esercizio.",
    "",
    "La regola può restare nei dati interni `visual_logic`, ma non deve essere mostrata nel campo `domanda`.",
    "",
    f"Domande Logica visiva ripulite: {len(changed_ids)}",
    "",
]

if source_backup:
    report.append(f"Backup source: `{source_backup.relative_to(ROOT)}`")
    report.append("")

if changed_ids:
    report.extend(["## Domande corrette", ""])

    for entry in changed_ids:
        report.append(f"- `{entry['id']}`: rimossi indizi {entry['leaks']}")

report.extend(["", "## Propagazione", ""])

for result in results:
    report.append(
        f"- `{result['path'].relative_to(ROOT)}`: {result['updated']} domande propagate"
    )

    if result.get("files"):
        for file_name in result["files"]:
            report.append(f"  - JSON interno aggiornato: `{file_name}`")

    if result.get("backup"):
        report.append(f"  - Backup: `{result['backup'].relative_to(ROOT)}`")

REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

print("✅ Correzione domande suggerite Logica visiva completata.")
print(f"Domande ripulite: {len(changed_ids)}")
for result in results:
    print(f"- {result['path'].relative_to(ROOT)}: {result['updated']} domande propagate")
print(f"Report: {REPORT_PATH}")
