#!/usr/bin/env python3
# WRAPPER_MOTORE_LOGICA_VISIVA
# Questo wrapper rende obbligatori i controlli aggiuntivi:
# 1. Nessuna domanda visibile deve suggerire la logica dell'esercizio.
# 2. Risposta, spiegazione e visual_logic devono essere coerenti.
# 3. Dopo questi controlli viene eseguito il motore visuale originale.

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]

COMANDI = [
    [
        sys.executable,
        "scripts/validatore_domande_non_suggerite_logica_visiva.py",
    ],
    [
        sys.executable,
        "scripts/validatore_coerenza_logica_visiva.py",
    ],
    [
        sys.executable,
        "scripts/motore_qualita_logica_visiva_base.py",
    ],
]


def esegui_comando(comando):
    print("")
    print("▶️", " ".join(comando))
    risultato = subprocess.run(comando, cwd=ROOT)

    if risultato.returncode != 0:
        print("")
        print("❌ Motore qualità Logica visiva interrotto.")
        print("Il controllo fallito è:", " ".join(comando))
        sys.exit(risultato.returncode)


def main():
    print("----- MOTORE QUALITÀ LOGICA VISIVA INTEGRATO -----")
    print("Controlli obbligatori:")
    print("- domande non suggerite")
    print("- coerenza risposta/spiegazione/visual_logic")
    print("- qualità visuale originale")

    for comando in COMANDI:
        esegui_comando(comando)

    print("")
    print("✅ Motore qualità Logica visiva integrato superato.")


if __name__ == "__main__":
    main()
