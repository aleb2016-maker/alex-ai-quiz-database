from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag import RagEngine


def main() -> None:
    rag = RagEngine()
    indice = rag.crea_indice()

    Path("reports").mkdir(exist_ok=True)

    report = f"""# Report RAG

## Stato indice

- Versione: {indice.get("versione")}
- Tipo: {indice.get("tipo")}
- Documenti letti: {indice.get("documenti_letti")}
- Chunk creati: {indice.get("numero_chunk")}

## Cartella documenti

rag/documenti/

## File indice

rag/indice_rag.json

## Nota

Questo è il primo motore RAG locale e riutilizzabile del progetto.
Serve come base per generare quiz, test, mini-corsi, slide e contenuti formativi a partire da documenti caricati.
"""

    Path("reports/rag_status.md").write_text(report, encoding="utf-8")

    print("✅ Indice RAG creato correttamente")
    print(f"📄 Documenti letti: {indice.get('documenti_letti')}")
    print(f"🧩 Chunk creati: {indice.get('numero_chunk')}")
    print("📌 Report: reports/rag_status.md")


if __name__ == "__main__":
    main()
