import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from rag import RagEngine


def main() -> None:
    if len(sys.argv) < 2:
        print('Uso: python3 scripts/rag_test_query.py "la tua domanda"')
        raise SystemExit(1)

    domanda = " ".join(sys.argv[1:])

    rag = RagEngine()
    risultati = rag.cerca(domanda, massimo_risultati=5)

    print("\n🔎 DOMANDA:")
    print(domanda)

    if not risultati:
        print("\n⚠️ Nessun risultato trovato.")
        print("Aggiungi documenti in rag/documenti/ e ricrea l'indice.")
        return

    print("\n✅ RISULTATI RAG:\n")

    for posizione, risultato in enumerate(risultati, start=1):
        print("=" * 80)
        print(f"Risultato {posizione}")
        print(f"Documento: {risultato['documento']}")
        print(f"Chunk: {risultato['numero_chunk']}")
        print(f"Punteggio: {risultato['punteggio']}")
        print("-" * 80)
        print(risultato["testo"][:900])
        print()


if __name__ == "__main__":
    main()
