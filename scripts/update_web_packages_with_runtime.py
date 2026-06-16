from pathlib import Path
import zipfile
import tempfile
import shutil

ROOT = Path(__file__).resolve().parents[1]

RUNTIME_ENGINE = ROOT / "runtime" / "web" / "quiz-engine.js"

ZIP_FOLDERS = [
    ROOT / "downloads",
    ROOT / "dist" / "generated",
]

CONTROLLI_OBBLIGATORI = [
    "window.AlexFinalRewardEngine",
    "ALEX_FINAL_REWARD_CSS",
    "alex-final-reward-card",
    "installaStiliPremioFinaleAlex",
]


def controlla_runtime_engine():
    if not RUNTIME_ENGINE.exists():
        raise SystemExit(f"ERRORE: non trovo {RUNTIME_ENGINE}")

    testo = RUNTIME_ENGINE.read_text(encoding="utf-8")

    for controllo in CONTROLLI_OBBLIGATORI:
        if controllo not in testo:
            raise SystemExit(
                f"ERRORE: il runtime non contiene il blocco richiesto: {controllo}"
            )

    return testo


def aggiorna_zip(zip_path, nuovo_quiz_engine):
    with zipfile.ZipFile(zip_path, "r") as archivio:
        nomi = archivio.namelist()

        file_quiz_engine = [
            nome for nome in nomi
            if nome.endswith("quiz-engine.js")
        ]

        if not file_quiz_engine:
            print(f"SKIP senza quiz-engine.js: {zip_path}")
            return False

        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as tmp:
            temp_path = Path(tmp.name)

        with zipfile.ZipFile(zip_path, "r") as archivio_originale:
            with zipfile.ZipFile(
                temp_path,
                "w",
                compression=zipfile.ZIP_DEFLATED
            ) as archivio_nuovo:

                for elemento in archivio_originale.infolist():
                    contenuto = archivio_originale.read(elemento.filename)

                    if elemento.filename.endswith("quiz-engine.js"):
                        contenuto = nuovo_quiz_engine.encode("utf-8")
                        print(
                            f"AGGIORNATO: {zip_path.name} -> {elemento.filename}"
                        )

                    archivio_nuovo.writestr(elemento, contenuto)

        shutil.move(str(temp_path), zip_path)
        return True


def controlla_zip_aggiornato(zip_path):
    with zipfile.ZipFile(zip_path, "r") as archivio:
        nomi = archivio.namelist()

        file_quiz_engine = [
            nome for nome in nomi
            if nome.endswith("quiz-engine.js")
        ]

        if not file_quiz_engine:
            return True

        for nome in file_quiz_engine:
            contenuto = archivio.read(nome).decode("utf-8", errors="ignore")

            for controllo in CONTROLLI_OBBLIGATORI:
                if controllo not in contenuto:
                    raise SystemExit(
                        f"ERRORE: {zip_path.name} non contiene {controllo} in {nome}"
                    )

    return True


def main():
    print("----- AGGIORNO PACCHETTI WEB CON RUNTIME NUOVO -----")

    nuovo_quiz_engine = controlla_runtime_engine()

    zip_trovati = []

    for cartella in ZIP_FOLDERS:
        if cartella.exists():
            zip_trovati.extend(sorted(cartella.glob("*.zip")))

    if not zip_trovati:
        print("ATTENZIONE: non ho trovato ZIP da aggiornare.")
        return

    zip_aggiornati = 0

    for zip_path in zip_trovati:
        if aggiorna_zip(zip_path, nuovo_quiz_engine):
            zip_aggiornati += 1

    print("")
    print("----- CONTROLLO ZIP AGGIORNATI -----")

    for zip_path in zip_trovati:
        controlla_zip_aggiornato(zip_path)

    print("")
    print(f"ZIP trovati: {len(zip_trovati)}")
    print(f"ZIP web aggiornati: {zip_aggiornati}")
    print("OK: i pacchetti web esistenti ora includono il motore premi finale.")


if __name__ == "__main__":
    main()
