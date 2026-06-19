from pathlib import Path
import zipfile
import sys

root = Path.cwd()
errors = []

def require(condition, message):
    if not condition:
        errors.append(message)

for path in [
    root / "runtime/web/ai-effects.js",
    root / "runtime/web/ai-effects.css",
    root / "demo-ai/ai-effects.js",
    root / "demo-ai/ai-effects.css",
    root / "runtime/android/FinalRewardEngine.kt",
    root / "runtime/android/AiItsRewardEffects.kt",
]:
    require(path.exists(), f"Manca {path}")

js = (root / "runtime/web/ai-effects.js").read_text(encoding="utf-8")
require("removeFinalRewardCards" in js, "Il JS non rimuove la vecchia card finale.")
require("sessionStorage" in js, "Il JS non evita la ripetizione dell'ultimo premio per lo stesso punteggio.")
require("showAiItsFinalReward" in js, "Manca API web showAiItsFinalReward.")
require("MutationObserver" in js, "Manca osservatore per rilevare risultato finale.")

web_zip = root / "downloads/pacchetto-web-ai-its-demo.zip"
if web_zip.exists():
    with zipfile.ZipFile(web_zip, "r") as archive:
        names = archive.namelist()
        require(any(name.endswith("ai-effects.js") for name in names), "Lo ZIP Web AI ITS non contiene ai-effects.js.")
        require(any(name.endswith("ai-effects.css") for name in names), "Lo ZIP Web AI ITS non contiene ai-effects.css.")
else:
    errors.append("Manca downloads/pacchetto-web-ai-its-demo.zip")

android_zip = root / "downloads/pacchetto-android-ai-its-finale-semplice.zip"
if android_zip.exists():
    with zipfile.ZipFile(android_zip, "r") as archive:
        names = archive.namelist()
        require(any(name.endswith("quizengine/FinalRewardEngine.kt") for name in names), "Lo ZIP Android non contiene quizengine/FinalRewardEngine.kt.")
        require(any(name.endswith("quizengine/AiItsRewardEffects.kt") for name in names), "Lo ZIP Android non contiene quizengine/AiItsRewardEffects.kt.")
        require(any("LEGGIMI" in name.upper() for name in names), "Lo ZIP Android non contiene il LEGGIMI.")
else:
    errors.append("Manca downloads/pacchetto-android-ai-its-finale-semplice.zip")

if errors:
    print("❌ Verifica fallita:")
    for error in errors:
        print("-", error)
    sys.exit(1)

print("✅ Verifica premi/coriandoli AI ITS superata.")
