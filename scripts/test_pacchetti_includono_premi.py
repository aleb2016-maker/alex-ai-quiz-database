from pathlib import Path
import zipfile
import subprocess
import sys

root = Path(__file__).resolve().parents[1]

quiz_engine = root / "runtime" / "web" / "quiz-engine.js"
final_reward_engine = root / "runtime" / "web" / "final-reward-engine.js"

for file in [quiz_engine, final_reward_engine]:
    if not file.exists():
        raise SystemExit(f"ERRORE: file mancante: {file}")

for file in [quiz_engine, final_reward_engine]:
    testo = file.read_text(encoding="utf-8")

    controlli = [
        "window.AlexFinalRewardEngine",
        "creaPremioFinale",
        "mostraPremioFinale",
        "ALEX_FINAL_REWARD_CSS",
        "installaStiliPremioFinaleAlex",
        "alex-final-reward-card",
    ]

    for controllo in controlli:
        if controllo not in testo:
            raise SystemExit(f"ERRORE: manca {controllo} in {file}")

print("OK: runtime web e motore premi sono autosufficienti.")

zip_trovati = []

for cartella in [
    root / "dist" / "generated",
    root / "downloads",
]:
    if cartella.exists():
        zip_trovati.extend(cartella.glob("*.zip"))

zip_con_motore = 0

for zip_path in zip_trovati:
    try:
        with zipfile.ZipFile(zip_path) as archivio:
            nomi = archivio.namelist()
            file_quiz_engine = [
                nome for nome in nomi
                if nome.endswith("quiz-engine.js")
            ]

            for nome in file_quiz_engine:
                contenuto = archivio.read(nome).decode("utf-8", errors="ignore")

                if (
                    "window.AlexFinalRewardEngine" in contenuto and
                    "ALEX_FINAL_REWARD_CSS" in contenuto and
                    "alex-final-reward-card" in contenuto
                ):
                    zip_con_motore += 1
                    print(f"OK ZIP con motore premi: {zip_path.name} -> {nome}")
                    break

    except zipfile.BadZipFile:
        continue

if zip_trovati and zip_con_motore == 0:
    print("ATTENZIONE: ho trovato ZIP vecchi, ma nessuno contiene ancora il motore premi.")
    print("Questo può essere normale: bisogna rigenerare i pacchetti dopo questa modifica.")
else:
    print("OK: controllo ZIP completato.")

print("OK: i prossimi pacchetti web generati useranno il quiz-engine aggiornato.")
