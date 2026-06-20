import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag import RagEngine


def main() -> None:
    if len(sys.argv) < 2:
        print('Uso: python3 scripts/rag_crea_prompt_minicorso.py "argomento"')
        raise SystemExit(1)

    argomento = " ".join(sys.argv[1:])

    rag = RagEngine()
    prompt = rag.crea_prompt_per_minicorso(
        argomento=argomento,
        numero_slide=5,
        livello="base",
    )

    Path("reports").mkdir(exist_ok=True)
    Path("reports/rag_prompt_minicorso.md").write_text(prompt, encoding="utf-8")

    print("✅ Prompt mini-corso creato con contesto RAG")
    print("📌 File: reports/rag_prompt_minicorso.md")


if __name__ == "__main__":
    main()
