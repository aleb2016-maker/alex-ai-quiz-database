import subprocess
import sys


# Questa lista contiene tutti gli script che vogliamo eseguire in ordine.
SCRIPT_DA_ESEGUIRE = [
    "scripts/validate_questions.py",
    "scripts/check_duplicates.py",
    "scripts/check_image_paths.py",
    "scripts/build_database.py",
    "scripts/report_database.py",
]


def esegui_script(percorso_script):
    # Mostra quale controllo stiamo avviando.
    print("\n" + "=" * 60)
    print(f"ESEGUO: {percorso_script}")
    print("=" * 60)

    # Esegue lo script usando lo stesso Python attivo nel terminale.
    risultato = subprocess.run(
        [sys.executable, percorso_script],
        text=True
    )

    # Se uno script fallisce, blocchiamo tutto.
    if risultato.returncode != 0:
        print(f"\nERRORE: lo script {percorso_script} non è riuscito.")
        sys.exit(1)


def main():
    print("----- AVVIO CONTROLLO COMPLETO DATABASE QUIZ -----")

    for percorso_script in SCRIPT_DA_ESEGUIRE:
        esegui_script(percorso_script)

    print("\n" + "=" * 60)
    print("TUTTI I CONTROLLI SONO STATI COMPLETATI")
    print("=" * 60)


main()