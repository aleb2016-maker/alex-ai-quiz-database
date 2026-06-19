from pathlib import Path
import json
import zipfile
import tempfile
import shutil
import datetime
import re

ROOT = Path.cwd()
SOURCE_PATH = ROOT / "data/logica/logica_visiva.json"
REPORT_PATH = ROOT / "reports/propaga_logica_visiva_0019_0040.md"

STAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP_DIR = ROOT / "backups"
BACKUP_DIR.mkdir(exist_ok=True)
REPORT_PATH.parent.mkdir(exist_ok=True)

TARGET_JSONS = [
    ROOT / "demo-ai/database_quiz.json",
    ROOT / "dist/database_quiz_finale.json",
]

TARGET_ZIPS = [
    ROOT / "downloads/pacchetto-web-ai-its-demo.zip",
    ROOT / "downloads/pacchetto-android-ai-its-finale-semplice.zip",
]

ID_PATTERN = re.compile(r"LOG-VIS-(\d{4})$")


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


def is_target_id(codice):
    match = ID_PATTERN.fullmatch(codice)
    return bool(match and 19 <= int(match.group(1)) <= 40)


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path, data):
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


source_data = load_json(SOURCE_PATH)

source_by_id = {
    get_id(item): item
    for item in source_data
    if is_target_id(get_id(item))
}

if len(source_by_id) != 22:
    raise RuntimeError(
        f"Attese 22 domande LOG-VIS-0019 → LOG-VIS-0040, trovate {len(source_by_id)}"
    )


def replace_questions(obj):
    count = 0

    if isinstance(obj, list):
        for index, item in enumerate(obj):
            codice = get_id(item)

            if codice in source_by_id:
                obj[index] = source_by_id[codice]
                count += 1
            else:
                count += replace_questions(item)

    elif isinstance(obj, dict):
        codice = get_id(obj)

        if codice in source_by_id:
            obj.clear()
            obj.update(source_by_id[codice])
            return 1

        for value in obj.values():
            count += replace_questions(value)

    return count


def backup_file(path):
    backup_path = BACKUP_DIR / f"{path.name}.backup_prima_propaga_logica_visiva_{STAMP}"
    shutil.copy2(path, backup_path)
    return backup_path


def process_json_file(path):
    if not path.exists():
        return {
            "path": path,
            "updated": 0,
            "backup": None,
            "status": "mancante",
        }

    data = load_json(path)
    updated = replace_questions(data)

    backup = None
    if updated:
        backup = backup_file(path)
        write_json(path, data)

    return {
        "path": path,
        "updated": updated,
        "backup": backup,
        "status": "ok",
    }


def process_zip_file(path):
    if not path.exists():
        return {
            "path": path,
            "updated": 0,
            "files": [],
            "backup": None,
            "status": "mancante",
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

            updated = replace_questions(data)

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
        "files": updated_files,
        "backup": backup,
        "status": "ok",
    }


results = []

for target in TARGET_JSONS:
    results.append(process_json_file(target))

for target in TARGET_ZIPS:
    results.append(process_zip_file(target))


def verify_no_old_residue_in_object(obj):
    problemi = []

    if isinstance(obj, list):
        for item in obj:
            problemi.extend(verify_no_old_residue_in_object(item))

    elif isinstance(obj, dict):
        codice = get_id(obj)

        if codice in source_by_id:
            text = json.dumps(obj, ensure_ascii=False).lower()

            for phrase in [
                "cerchio/quadrato",
                "cerchio nero",
                "dopo il quadrato torna il cerchio",
                "triangolo verde con 7 lati",
            ]:
                if phrase in text:
                    problemi.append(f"{codice}: residuo '{phrase}'")

        for value in obj.values():
            problemi.extend(verify_no_old_residue_in_object(value))

    return problemi


verification_errors = []

for target in TARGET_JSONS:
    if target.exists():
        verification_errors.extend(verify_no_old_residue_in_object(load_json(target)))

for target in TARGET_ZIPS:
    if target.exists():
        with zipfile.ZipFile(target, "r") as archive:
            for name in archive.namelist():
                if not name.endswith(".json"):
                    continue

                try:
                    data = json.loads(archive.read(name).decode("utf-8"))
                except Exception:
                    continue

                verification_errors.extend(verify_no_old_residue_in_object(data))


report = [
    "# Propagazione Logica visiva LOG-VIS-0019 → LOG-VIS-0040",
    "",
    "Sono state propagate le 22 domande corrette da `data/logica/logica_visiva.json` verso demo, database finale e ZIP.",
    "",
    "## Risultati",
    "",
]

for result in results:
    relative = result["path"].relative_to(ROOT)

    report.append(f"- `{relative}`: {result['updated']} domande aggiornate")

    if result.get("files"):
        for file_name in result["files"]:
            report.append(f"  - JSON interno aggiornato: `{file_name}`")

    if result["backup"]:
        report.append(f"  - Backup: `{result['backup'].relative_to(ROOT)}`")

    if result["status"] == "mancante":
        report.append("  - Avviso: file mancante")

if verification_errors:
    report.extend(["", "## Errori verifica residui", ""])

    for error in verification_errors:
        report.append(f"- {error}")

    REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

    print("❌ Propagazione completata ma verifica residui fallita.")
    for error in verification_errors:
        print("-", error)
    raise SystemExit(1)

report.extend([
    "",
    "## Verifica",
    "",
    "✅ Nessun residuo vecchio trovato nelle domande propagate.",
    "",
])

REPORT_PATH.write_text("\n".join(report) + "\n", encoding="utf-8")

print("✅ Propagazione Logica visiva completata.")
for result in results:
    print(f"- {result['path'].relative_to(ROOT)}: {result['updated']} domande aggiornate")
print(f"Report: {REPORT_PATH}")
