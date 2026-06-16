from pathlib import Path
import argparse
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[1]


def esegui(nome, comando):
    print()
    print(f"===== {nome} =====")
    print("Comando:", " ".join(comando))

    risultato = subprocess.run(
        comando,
        cwd=ROOT,
    )

    if risultato.returncode == 0:
        print(f"OK: {nome}")
    else:
        print(f"ERRORE: {nome} ha restituito codice {risultato.returncode}")

    return risultato.returncode


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--strict",
        action="store_true",
        help="Modalità rigida: fallisce se trova problemi tecnici, qualità reale o errori linguistici.",
    )

    args = parser.parse_args()

    python = sys.executable

    comando_testuale = [
        python,
        "scripts/motore_qualita_generale.py",
        "--area",
        "tutto",
        "--fail-on-technical",
        "--fail-on-quality",
        "--fail-on-language",
    ]

    comando_visivo = [
        python,
        "scripts/motore_qualita_logica_visiva.py",
    ]

    if args.strict:
        comando_visivo.extend([
            "--fail-on-technical",
            "--fail-on-quality",
            "--fail-on-language",
        ])

    codici = []

    codici.append(esegui("Motore qualità testuale generale", comando_testuale))
    codici.append(esegui("Motore qualità logica visiva", comando_visivo))

    print()
    print("===== RIEPILOGO CONTROLLO QUALITÀ COMPLETO =====")

    if all(codice == 0 for codice in codici):
        print("OK: controllo qualità completo terminato.")
        print("Report principali:")
        print("- reports/motore_qualita_generale.md")
        print("- reports/motore_qualita_logica_visiva.md")
    else:
        print("ATTENZIONE: uno o più controlli hanno trovato problemi.")
        print("Apri i report generati per vedere cosa correggere.")

    if args.strict and any(codice != 0 for codice in codici):
        sys.exit(1)


if __name__ == "__main__":
    main()
