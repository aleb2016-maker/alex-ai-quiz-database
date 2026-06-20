from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def esegui(comando: list[str]) -> subprocess.CompletedProcess:
    print()
    print("▶️ " + " ".join(comando))
    return subprocess.run(
        comando,
        cwd=PROJECT_ROOT,
        text=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera quiz RAG con retry se Ollama produce JSON non valido."
    )

    parser.add_argument("argomento")
    parser.add_argument("--categoria", default="rag_generato")
    parser.add_argument("--livello", default="intermedio")
    parser.add_argument("--numero-domande", type=int, default=10)
    parser.add_argument("--output", default="dist/generated/rag_quiz_generato.json")
    parser.add_argument("--prompt-output", default="reports/rag_prompt_generazione_quiz_json.md")
    parser.add_argument("--usa-ollama", action="store_true")
    parser.add_argument("--modello", default="gemma3:4b")
    parser.add_argument("--tentativi", type=int, default=3)

    args = parser.parse_args()

    if args.tentativi <= 0:
        raise SystemExit("Il numero di tentativi deve essere maggiore di zero.")

    python = sys.executable

    ultimo_esito = 1

    for tentativo in range(1, args.tentativi + 1):
        print()
        print(f"🔁 Tentativo RAG con Ollama {tentativo}/{args.tentativi}")

        comando_generazione = [
            python,
            "scripts/rag_genera_quiz_json.py",
            args.argomento,
            "--categoria",
            args.categoria,
            "--livello",
            args.livello,
            "--numero-domande",
            str(args.numero_domande),
            "--output",
            args.output,
            "--prompt-output",
            args.prompt_output,
        ]

        if args.usa_ollama:
            comando_generazione.extend(["--usa-ollama", "--modello", args.modello])

        risultato_generazione = esegui(comando_generazione)

        if risultato_generazione.returncode != 0:
            ultimo_esito = risultato_generazione.returncode
            print("⚠️ Generazione fallita. Riprovo se restano tentativi.")
            continue

        risultato_validazione = esegui(
            [
                python,
                "scripts/rag_valida_quiz_json.py",
                args.output,
            ]
        )

        if risultato_validazione.returncode == 0:
            print()
            print("✅ JSON RAG valido generato con successo")
            return

        ultimo_esito = risultato_validazione.returncode
        print("⚠️ JSON generato non valido. Riprovo se restano tentativi.")

    print()
    print("❌ Ollama non è riuscito a generare un JSON valido dopo i tentativi disponibili.")
    print("📌 Controlla: reports/rag_validazione_quiz_json.md")
    raise SystemExit(ultimo_esito)


if __name__ == "__main__":
    main()
