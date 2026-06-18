import json
import shutil
import zipfile
from pathlib import Path

DEMO_AI_DIR = Path("demo-ai")
DEMO_AI_DB = Path("demo-ai/database_quiz.json")
FULL_DB = Path("dist/database_quiz_finale.json")

WEB_ZIP = Path("downloads/pacchetto-web-ai-its-demo.zip")
ANDROID_ZIP = Path("downloads/pacchetto-android-ai-its-finale-semplice.zip")

VISUAL_ASSETS_DIR = Path("assets/logica_visiva")
REPORT = Path("reports/propagazione_ai_its_download_personalizzato.md")

EXPECTED_DEMO_AI = {
    "AI": 80,
    "Informatica": 80,
    "Inglese": 80,
    "Logica": 80,
    "Logica visiva": 40,
    "Matematica": 80,
}

EXPECTED_FULL_TOTAL = 640


def load_json(path):
    if not path.exists():
        raise SystemExit(f"ERRORE: file non trovato: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def extract_questions(data):
    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["domande", "questions", "quiz", "items", "data"]:
            value = data.get(key)
            if isinstance(value, list):
                return value

    raise SystemExit("ERRORE: formato database non riconosciuto.")


def get_id(question):
    return str(question.get("id", "")).strip()


def classify_question(question):
    qid = get_id(question).upper()

    if qid.startswith("AI-"):
        return "AI"

    if qid.startswith("INF-"):
        return "Informatica"

    if qid.startswith("ING-"):
        return "Inglese"

    if qid.startswith("MAT-"):
        return "Matematica"

    if qid.startswith("LOG-VIS-"):
        return "Logica visiva"

    if (
        qid.startswith("LOG-NUM-")
        or qid.startswith("LOG-VER-")
        or qid.startswith("LOG-AST-")
        or qid.startswith("LOG-CRI-")
    ):
        return "Logica"

    return "Altro"


def count_sections(db_path):
    questions = extract_questions(load_json(db_path))

    counts = {}
    for question in questions:
        section = classify_question(question)
        counts[section] = counts.get(section, 0) + 1

    return counts, len(questions)


def assert_demo_ai_counts(db_path, label):
    counts, total = count_sections(db_path)

    errors = []

    for section, expected in EXPECTED_DEMO_AI.items():
        found = counts.get(section, 0)
        if found != expected:
            errors.append(f"{label}: {section} atteso {expected}, trovato {found}")

    expected_total = sum(EXPECTED_DEMO_AI.values())
    if total != expected_total:
        errors.append(f"{label}: totale atteso {expected_total}, trovato {total}")

    if errors:
        raise SystemExit("ERRORE CONTEGGI DEMO AI:\n" + "\n".join(errors))

    return counts, total


def assert_full_counts(db_path):
    counts, total = count_sections(db_path)

    if total != EXPECTED_FULL_TOTAL:
        raise SystemExit(
            f"ERRORE DATABASE COMPLETO: totale atteso {EXPECTED_FULL_TOTAL}, trovato {total}"
        )

    for section, expected in EXPECTED_DEMO_AI.items():
        found = counts.get(section, 0)
        if found != expected:
            raise SystemExit(
                f"ERRORE DATABASE COMPLETO: {section} atteso {expected}, trovato {found}"
            )

    return counts, total


def rebuild_web_zip():
    if not DEMO_AI_DIR.exists():
        raise SystemExit(f"ERRORE: cartella non trovata: {DEMO_AI_DIR}")

    WEB_ZIP.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(WEB_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(DEMO_AI_DIR.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(DEMO_AI_DIR))

    print(f"OK: pacchetto Web AI ITS rigenerato: {WEB_ZIP}")


def update_android_zip():
    if not ANDROID_ZIP.exists():
        raise SystemExit(f"ERRORE: pacchetto Android non trovato: {ANDROID_ZIP}")

    temp_zip = ANDROID_ZIP.with_suffix(".tmp.zip")
    database_bytes = DEMO_AI_DB.read_bytes()

    with zipfile.ZipFile(ANDROID_ZIP, "r") as old_archive:
        old_entries = old_archive.infolist()

        with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as new_archive:
            database_replaced = False

            for entry in old_entries:
                name = entry.filename

                if name.endswith("/"):
                    continue

                normalized = name.replace("\\", "/")

                is_database = normalized.endswith("database_quiz.json")
                is_visual_asset = (
                    normalized.startswith("assets/logica_visiva/")
                    or normalized.startswith("app/src/main/assets/logica_visiva/")
                    or "/assets/logica_visiva/" in normalized
                )

                if is_database:
                    new_archive.writestr(name, database_bytes)
                    database_replaced = True
                    continue

                if is_visual_asset:
                    continue

                new_archive.writestr(name, old_archive.read(entry.filename))

            if not database_replaced:
                new_archive.writestr("database_quiz.json", database_bytes)

            if VISUAL_ASSETS_DIR.exists():
                for image in sorted(VISUAL_ASSETS_DIR.rglob("*")):
                    if image.is_file():
                        new_archive.write(
                            image,
                            Path("assets/logica_visiva") / image.relative_to(VISUAL_ASSETS_DIR)
                        )

    temp_zip.replace(ANDROID_ZIP)
    print(f"OK: pacchetto Android AI ITS aggiornato: {ANDROID_ZIP}")


def update_personalized_zip_if_present():
    updated = []

    if not Path("downloads").exists():
        return updated

    candidates = []
    for pattern in ["*personalizz*.zip", "*personal*.zip"]:
        candidates.extend(Path("downloads").glob(pattern))

    candidates = sorted(set(candidates))

    for zip_path in candidates:
        temp_zip = zip_path.with_suffix(".tmp.zip")
        full_db_bytes = FULL_DB.read_bytes()
        demo_db_bytes = DEMO_AI_DB.read_bytes()

        with zipfile.ZipFile(zip_path, "r") as old_archive:
            with zipfile.ZipFile(temp_zip, "w", compression=zipfile.ZIP_DEFLATED) as new_archive:
                replaced_any = False

                for entry in old_archive.infolist():
                    name = entry.filename

                    if name.endswith("/"):
                        continue

                    normalized = name.replace("\\", "/")

                    if normalized.endswith("database_quiz_finale.json"):
                        new_archive.writestr(name, full_db_bytes)
                        replaced_any = True
                    elif normalized.endswith("database_quiz.json"):
                        new_archive.writestr(name, demo_db_bytes)
                        replaced_any = True
                    else:
                        new_archive.writestr(name, old_archive.read(entry.filename))

                if not replaced_any:
                    new_archive.writestr("dist/database_quiz_finale.json", full_db_bytes)
                    new_archive.writestr("demo-ai/database_quiz.json", demo_db_bytes)

        temp_zip.replace(zip_path)
        updated.append(zip_path)

    return updated


def verify_zip_database(zip_path, label):
    if not zip_path.exists():
        raise SystemExit(f"ERRORE: zip non trovato: {zip_path}")

    with zipfile.ZipFile(zip_path, "r") as archive:
        database_names = [
            name for name in archive.namelist()
            if name.replace("\\", "/").endswith("database_quiz.json")
        ]

        if not database_names:
            raise SystemExit(f"ERRORE: nessun database_quiz.json dentro {zip_path}")

        database_name = database_names[0]
        data = json.loads(archive.read(database_name).decode("utf-8"))

    temp_path = Path("reports") / f"_tmp_check_{label}.json"
    temp_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    counts, total = assert_demo_ai_counts(temp_path, label)
    temp_path.unlink(missing_ok=True)

    return database_name, counts, total


def write_report(demo_counts, full_counts, web_info, android_info, personalized_updated):
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Propagazione AI ITS download e pacchetto personalizzato",
        "",
        "## Destinazioni aggiornate",
        "",
        "- Demo online AI ITS: `demo-ai/database_quiz.json`",
        "- Scarica Web AI ITS: `downloads/pacchetto-web-ai-its-demo.zip`",
        "- Scarica Android AI ITS: `downloads/pacchetto-android-ai-its-finale-semplice.zip`",
        "- Crea pacchetto personalizzato: `dist/database_quiz_finale.json`",
        "",
        "## Conteggi Demo AI",
        "",
    ]

    for section, expected in EXPECTED_DEMO_AI.items():
        lines.append(f"- {section}: {demo_counts.get(section, 0)}/{expected}")

    lines.extend([
        "",
        "## Database completo",
        "",
        f"- Totale: {sum(full_counts.values())}/{EXPECTED_FULL_TOTAL}",
        "",
        "## Verifica zip",
        "",
        f"- Web zip database: `{web_info[0]}`",
        f"- Android zip database: `{android_info[0]}`",
        "",
    ])

    if personalized_updated:
        lines.append("## Zip personalizzati aggiornati")
        lines.append("")
        for path in personalized_updated:
            lines.append(f"- `{path}`")
    else:
        lines.append("## Zip personalizzati aggiornati")
        lines.append("")
        lines.append("- Nessuno zip personalizzato trovato in `downloads/`; la base resta `dist/database_quiz_finale.json`.")

    lines.extend([
        "",
        "## Esito",
        "",
        "OK: tutte le destinazioni AI ITS risultano allineate.",
        "",
    ])

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"OK: report creato: {REPORT}")


def main():
    demo_counts, demo_total = assert_demo_ai_counts(DEMO_AI_DB, "demo-ai/database_quiz.json")
    full_counts, full_total = assert_full_counts(FULL_DB)

    rebuild_web_zip()
    update_android_zip()
    personalized_updated = update_personalized_zip_if_present()

    web_info = verify_zip_database(WEB_ZIP, "web_ai_its")
    android_info = verify_zip_database(ANDROID_ZIP, "android_ai_its")

    write_report(demo_counts, full_counts, web_info, android_info, personalized_updated)

    print()
    print("===== RIEPILOGO PROPAGAZIONE =====")
    print(f"Demo AI online: {demo_total} domande")
    print(f"Database completo/personalizzato: {full_total} domande")
    print(f"Web AI ITS zip: OK")
    print(f"Android AI ITS zip: OK")

    if personalized_updated:
        print("Zip personalizzati aggiornati:")
        for path in personalized_updated:
            print(f"- {path}")
    else:
        print("Nessuno zip personalizzato separato trovato: usa dist/database_quiz_finale.json")

    print("OK: propagazione completata.")


if __name__ == "__main__":
    main()
