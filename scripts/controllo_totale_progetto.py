#!/usr/bin/env python3
from pathlib import Path
import json
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

REPORT_MD = REPORTS / "controllo_totale_progetto.md"
REPORT_JSON = REPORTS / "controllo_totale_progetto.json"

COMMANDS = [
    ("Validate questions rinforzato", ["scripts/validate_questions.py"]),
    ("Build database rinforzato", ["scripts/build_database.py"]),
    ("Check duplicates rinforzato", ["scripts/check_duplicates.py"]),
    ("Controllo qualità completo", ["scripts/controllo_qualita_completo.py"]),
    ("Verifica premi/coriandoli AI ITS", ["scripts/verifica_premi_ai_its_v2.py"]),
]

EXPECTED_COUNTS = {
    "demo-ai/database_quiz.json": 440,
    "demo-scienze/database_quiz.json": 200,
    "dist/database_quiz_finale.json": 640,
}

EXPECTED_ZIPS = [
    "downloads/pacchetto-web-ai-its-demo.zip",
    "downloads/pacchetto-android-ai-its-finale-semplice.zip",
    "downloads/pacchetto-web-scienze-demo.zip",
    "downloads/pacchetto-android-scienze-finale-semplice.zip",
]


def run_command(label, command):
    full_command = [sys.executable, *command]

    print("")
    print(f"===== {label} =====")
    print("Comando:", " ".join(full_command))

    result = subprocess.run(full_command, cwd=ROOT)

    return {
        "label": label,
        "command": " ".join(full_command),
        "returncode": result.returncode,
        "ok": result.returncode == 0,
    }


def load_questions(path):
    data = json.loads(path.read_text(encoding="utf-8"))

    if isinstance(data, list):
        return data

    if isinstance(data, dict):
        for key in ["domande", "questions", "quiz", "data"]:
            value = data.get(key)

            if isinstance(value, list):
                return value

    raise ValueError(f"Formato non riconosciuto: {path}")


def check_counts():
    results = []

    for relative_path, expected_count in EXPECTED_COUNTS.items():
        path = ROOT / relative_path

        if not path.exists():
            results.append({
                "file": relative_path,
                "ok": False,
                "expected": expected_count,
                "actual": None,
                "message": "file mancante",
            })
            continue

        try:
            questions = load_questions(path)
            actual_count = len(questions)
        except Exception as error:
            results.append({
                "file": relative_path,
                "ok": False,
                "expected": expected_count,
                "actual": None,
                "message": str(error),
            })
            continue

        results.append({
            "file": relative_path,
            "ok": actual_count == expected_count,
            "expected": expected_count,
            "actual": actual_count,
            "message": "OK" if actual_count == expected_count else "conteggio non coerente",
        })

    return results


def check_zips():
    results = []

    for relative_path in EXPECTED_ZIPS:
        path = ROOT / relative_path

        if not path.exists():
            results.append({
                "file": relative_path,
                "ok": False,
                "message": "zip mancante",
            })
            continue

        if not zipfile.is_zipfile(path):
            results.append({
                "file": relative_path,
                "ok": False,
                "message": "file presente ma non è uno zip valido",
            })
            continue

        try:
            with zipfile.ZipFile(path, "r") as archive:
                names = archive.namelist()
        except Exception as error:
            results.append({
                "file": relative_path,
                "ok": False,
                "message": f"zip non leggibile: {error}",
            })
            continue

        results.append({
            "file": relative_path,
            "ok": True,
            "message": f"zip valido con {len(names)} file interni",
        })

    return results


def main():
    print("----- CONTROLLO TOTALE PROGETTO -----")

    command_results = [
        run_command(label, command)
        for label, command in COMMANDS
    ]

    count_results = check_counts()
    zip_results = check_zips()

    all_ok = (
        all(item["ok"] for item in command_results)
        and all(item["ok"] for item in count_results)
        and all(item["ok"] for item in zip_results)
    )

    result = {
        "esito": "OK" if all_ok else "KO",
        "comandi": command_results,
        "conteggi": count_results,
        "zip": zip_results,
    }

    REPORT_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Controllo totale progetto",
        "",
        f"Esito: {'✅ OK' if all_ok else '❌ KO'}",
        "",
        "## Comandi",
        "",
    ]

    for item in command_results:
        status = "✅ OK" if item["ok"] else "❌ KO"
        lines.append(f"- {status} — {item['label']}")

    lines.extend(["", "## Conteggi database", ""])

    for item in count_results:
        status = "✅ OK" if item["ok"] else "❌ KO"
        lines.append(
            f"- {status} — `{item['file']}`: "
            f"{item['actual']} / attese {item['expected']} — {item['message']}"
        )

    lines.extend(["", "## Pacchetti ZIP", ""])

    for item in zip_results:
        status = "✅ OK" if item["ok"] else "❌ KO"
        lines.append(f"- {status} — `{item['file']}`: {item['message']}")

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("")
    print("===== RIEPILOGO CONTROLLO TOTALE =====")

    for item in command_results:
        print(("✅" if item["ok"] else "❌"), item["label"])

    for item in count_results:
        print(
            ("✅" if item["ok"] else "❌"),
            item["file"],
            item["actual"],
            "/",
            item["expected"],
        )

    for item in zip_results:
        print(("✅" if item["ok"] else "❌"), item["file"])

    print("")
    print(f"Report: {REPORT_MD}")

    if not all_ok:
        print("❌ Controllo totale progetto fallito.")
        sys.exit(1)

    print("✅ Controllo totale progetto superato.")


if __name__ == "__main__":
    main()
