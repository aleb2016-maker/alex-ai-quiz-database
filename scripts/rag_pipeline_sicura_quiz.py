from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def esegui(comando: list[str]) -> None:
    print()
    print("▶️ " + " ".join(comando))
    subprocess.run(
        comando,
        cwd=PROJECT_ROOT,
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Esegue la pipeline sicura RAG → quiz JSON → review."
    )

    parser.add_argument("argomento")
    parser.add_argument("--categoria", default="rag_generato")
    parser.add_argument("--livello", default="intermedio")
    parser.add_argument("--numero-domande", type=int, default=10)
    parser.add_argument("--usa-ollama", action="store_true")
    parser.add_argument("--modello", default="gemma3:4b")
    parser.add_argument("--salta-qualita-completa", action="store_true")

    args = parser.parse_args()

    if args.numero_domande <= 0:
        raise SystemExit("Il numero di domande deve essere maggiore di zero.")

    python = sys.executable

    esegui([python, "scripts/rag_build_index.py"])

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
    ]

    if args.usa_ollama:
        comando_generazione.extend(["--usa-ollama", "--modello", args.modello])

    esegui(comando_generazione)

    esegui(
        [
            python,
            "scripts/rag_valida_quiz_json.py",
            "dist/generated/rag_quiz_generato.json",
        ]
    )

    esegui(
        [
            python,
            "scripts/rag_prepara_review_quiz.py",
            "--input",
            "dist/generated/rag_quiz_generato.json",
            "--output",
            "review/rag/quiz_da_revisionare.json",
            "--report",
            "reports/rag_review_quiz.md",
        ]
    )

    if not args.salta_qualita_completa:
        controllo_completo = PROJECT_ROOT / "scripts/controllo_qualita_completo.py"

        if controllo_completo.exists():
            esegui([python, "scripts/controllo_qualita_completo.py"])

    Path("reports").mkdir(exist_ok=True)

    report = f"""# Pipeline sicura RAG → Quiz → Review

## Stato

OK: pipeline completata.

## Argomento

{args.argomento}

## Categoria

{args.categoria}

## Livello

{args.livello}

## Numero domande richieste

{args.numero_domande}

## Modalità generazione

{"Ollama locale" if args.usa_ollama else "Modalità sicura senza modello AI"}

## Output principali

- Prompt generazione: reports/rag_prompt_generazione_quiz_json.md
- JSON temporaneo locale: dist/generated/rag_quiz_generato.json
- Report validazione: reports/rag_validazione_quiz_json.md
- Report review: reports/rag_review_quiz.md
- File review locale: review/rag/quiz_da_revisionare.json

## Regola di sicurezza

La pipeline non modifica i database ufficiali dentro data/.
"""

    Path("reports/rag_pipeline_sicura_quiz.md").write_text(
        report,
        encoding="utf-8",
    )

    print()
    print("✅ Pipeline sicura RAG completata")
    print("📌 Report: reports/rag_pipeline_sicura_quiz.md")


if __name__ == "__main__":
    main()
