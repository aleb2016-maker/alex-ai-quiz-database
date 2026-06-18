from pathlib import Path
import importlib.util
import json
import shutil
import zipfile

REPORT = Path("reports/verifica_effetti_ai_its.md")
TMP = Path("reports/_tmp_verifica_effetti_ai_its")

ERRORI = []

def errore(msg):
    ERRORI.append(msg)

def assert_file_contains(path, texts):
    if not path.exists():
        errore(f"File mancante: {path}")
        return

    data = path.read_text(encoding="utf-8", errors="ignore")

    for text in texts:
        if text not in data:
            errore(f"`{path}` non contiene `{text}`")

def check_demo_ai():
    assert_file_contains(Path("demo-ai/index.html"), ["ai-effects.css", "ai-effects.js"])
    assert_file_contains(Path("demo-ai/ai-effects.js"), ["alexAiShootConfetti", "alexAiShowFinalReward"])
    assert_file_contains(Path("demo-ai/ai-effects.css"), ["alex-ai-confetti-piece", "alex-ai-final-reward"])

def check_create_package_simulation():
    if TMP.exists():
        shutil.rmtree(TMP)

    TMP.mkdir(parents=True, exist_ok=True)

    (TMP / "index.html").write_text(
        """<!DOCTYPE html><html><head><title>Quiz AI</title></head><body><h1>Quiz AI</h1></body></html>""",
        encoding="utf-8"
    )

    domande_ai = [
        {
            "id": f"AI-FAC-TEST-{i:04d}",
            "categoria": "ai",
            "livello": "facile",
            "domanda": "Domanda AI di test",
            "opzioni": ["A", "B", "C", "D"],
            "risposta_corretta": "A",
            "spiegazione": "Test."
        }
        for i in range(1, 11)
    ]

    (TMP / "database_quiz.json").write_text(
        json.dumps(domande_ai, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    spec = importlib.util.spec_from_file_location("create_quiz_package_test", "scripts/create_quiz_package.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    if not hasattr(module, "scrivi_effetti_web_ai_its"):
        errore("scripts/create_quiz_package.py non contiene scrivi_effetti_web_ai_its.")
        return

    module.scrivi_effetti_web_ai_its(TMP)

    assert_file_contains(TMP / "index.html", ["ai-effects.css", "ai-effects.js"])
    assert_file_contains(TMP / "ai-effects.js", ["alexAiShootConfetti", "alexAiShowFinalReward"])
    assert_file_contains(TMP / "ai-effects.css", ["alex-ai-confetti-piece", "alex-ai-final-reward"])

def check_web_ai_zip():
    path = Path("downloads/pacchetto-web-ai-its-demo.zip")

    if not path.exists():
        errore(f"Zip web AI mancante: {path}")
        return

    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        joined = "\n".join(names)

        if "ai-effects.js" not in joined:
            errore("Zip web AI non contiene ai-effects.js.")

        if "ai-effects.css" not in joined:
            errore("Zip web AI non contiene ai-effects.css.")

        js_files = [name for name in names if name.endswith("ai-effects.js")]

        if js_files:
            js = archive.read(js_files[0]).decode("utf-8", errors="ignore")

            for text in ["alexAiShootConfetti", "alexAiShowFinalReward"]:
                if text not in js:
                    errore(f"Zip web AI: ai-effects.js non contiene {text}")

def check_android_ai_zip():
    path = Path("downloads/pacchetto-android-ai-its-finale-semplice.zip")

    if not path.exists():
        errore(f"Zip Android AI mancante: {path}")
        return

    with zipfile.ZipFile(path, "r") as archive:
        names = archive.namelist()
        reward_files = [name for name in names if name.endswith("FinalRewardEngine.kt")]

        if not reward_files:
            errore("Zip Android AI non contiene FinalRewardEngine.kt.")
            return

        content = archive.read(reward_files[0]).decode("utf-8", errors="ignore")

        for text in ["FinalRewardEngine", "confettiForCorrectAnswer", "rewardFor"]:
            if text not in content:
                errore(f"FinalRewardEngine.kt non contiene {text}")

def main():
    check_demo_ai()
    check_create_package_simulation()
    check_web_ai_zip()
    check_android_ai_zip()

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    if ERRORI:
        REPORT.write_text(
            "# Verifica effetti AI ITS\n\nESITO: ERRORE\n\n" +
            "\n".join(f"- {e}" for e in ERRORI),
            encoding="utf-8"
        )

        print("ERRORE: effetti AI ITS non completi.")
        for e in ERRORI:
            print("-", e)
        raise SystemExit(1)

    REPORT.write_text(
        "# Verifica effetti AI ITS\n\n"
        "ESITO: OK\n\n"
        "- Demo AI contiene ai-effects.css/js.\n"
        "- Pacchetto web AI contiene ai-effects.css/js.\n"
        "- Pacchetto personalizzato AI simulato riceve ai-effects.css/js.\n"
        "- Pacchetto Android AI contiene FinalRewardEngine.kt.\n",
        encoding="utf-8"
    )

    print("OK: effetti AI ITS presenti nella demo AI.")
    print("OK: effetti AI ITS presenti nel pacchetto web AI.")
    print("OK: pacchetto personalizzato AI simulato riceve gli effetti.")
    print("OK: pacchetto Android AI contiene FinalRewardEngine.kt.")

if __name__ == "__main__":
    main()
