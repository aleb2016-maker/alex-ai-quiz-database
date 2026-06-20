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
        description="Pipeline completa e sicura: RAG → quiz → review → preparazione import approvati."
    )

    parser.add_argument("argomento")
    parser.add_argument("--categoria", default="rag_generato")
    parser.add_argument("--livello", default="intermedio")
    parser.add_argument("--numero-domande", type=int, default=10)
    parser.add_argument("--usa-ollama", action="store_true")
    parser.add_argument("--modello", default="gemma3:4b")
    parser.add_argument("--salta-qualita-completa", action="store_true")

    args = parser.parse_args()

    python = sys.executable

    comando_pipeline_review = [
        python,
        "scripts/rag_pipeline_sicura_quiz.py",
        args.argomento,
        "--categoria",
        args.categoria,
        "--livello",
        args.livello,
        "--numero-domande",
        str(args.numero_domande),
        "--salta-qualita-completa",
    ]

    if args.usa_ollama:
        comando_pipeline_review.extend(["--usa-ollama", "--modello", args.modello])

    esegui(comando_pipeline_review)

    esegui(
        [
            python,
            "scripts/rag_prepara_import_approvati.py",
            "--input",
            "review/rag/quiz_da_revisionare.json",
            "--output",
            "review/rag/domande_approvate_pronte_per_import.json",
            "--report",
            "reports/rag_import_approvati.md",
        ]
    )

    if not args.salta_qualita_completa:
        controllo_completo = PROJECT_ROOT / "scripts/controllo_qualita_completo.py"

        if controllo_completo.exists():
            esegui([python, "scripts/controllo_qualita_completo.py"])

    Path("reports").mkdir(exist_ok=True)

    report = f"""# Pipeline completa sicura RAG

## Stato

OK: pipeline completa eseguita.

## Flusso coperto

RAG
↓
quiz JSON temporaneo
↓
validazione
↓
review
↓
preparazione import domande approvate
↓
eventuale controllo qualità completo

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
- Review locale: review/rag/quiz_da_revisionare.json
- Preparazione import locale: review/rag/domande_approvate_pronte_per_import.json
- Report import approvati: reports/rag_import_approvati.md

## Sicurezza

La pipeline non modifica i file dentro data/.
Per scrivere davvero nei database ufficiali serve un comando esplicito separato con conferma.
"""

    Path("reports/rag_pipeline_completa_sicura.md").write_text(
        report,
        encoding="utf-8",
    )

    print()
    print("✅ Pipeline completa sicura RAG terminata")
    print("📌 Report: reports/rag_pipeline_completa_sicura.md")


if __name__ == "__main__":
    main()
