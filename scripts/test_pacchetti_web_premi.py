from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]

ZIP_FOLDERS = [
    ROOT / "downloads",
    ROOT / "dist" / "generated",
]

CONTROLLI = [
    "window.AlexFinalRewardEngine",
    "ALEX_FINAL_REWARD_CSS",
    "alex-final-reward-card",
    "installaStiliPremioFinaleAlex",
]

zip_controllati = 0
zip_web_con_premi = 0

for cartella in ZIP_FOLDERS:
    if not cartella.exists():
        continue

    for zip_path in sorted(cartella.glob("*.zip")):
        with zipfile.ZipFile(zip_path, "r") as archivio:
            file_quiz_engine = [
                nome for nome in archivio.namelist()
                if nome.endswith("quiz-engine.js")
            ]

            if not file_quiz_engine:
                continue

            zip_controllati += 1

            for nome in file_quiz_engine:
                contenuto = archivio.read(nome).decode("utf-8", errors="ignore")

                if all(controllo in contenuto for controllo in CONTROLLI):
                    zip_web_con_premi += 1
                    print(f"OK: {zip_path.name} contiene premi finali in {nome}")
                    break
            else:
                raise SystemExit(
                    f"ERRORE: {zip_path.name} ha quiz-engine.js ma non contiene il motore premi."
                )

if zip_controllati == 0:
    print("ATTENZIONE: non ho trovato pacchetti web ZIP con quiz-engine.js.")
else:
    print("")
    print(f"Pacchetti web controllati: {zip_controllati}")
    print(f"Pacchetti web con premi finali: {zip_web_con_premi}")
    print("OK: tutti i pacchetti web controllati includono il motore premi finale.")
