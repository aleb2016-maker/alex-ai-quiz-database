#!/usr/bin/env python3
"""
Verifica pagina separata output RAG KB Clean V3.4F.
Non apre browser: controlla struttura file e riferimenti corretti.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "demo-rag/test-output-kb-clean-v34f.html"
REPORT = ROOT / "reports/rag_demo_output_kb_clean_v34f.md"

REQUIRED = [
    "Output RAG da KB pulita V3.4F",
    "Carica output V3.4E locale",
    "rag_output_kb_clean_v34e.json",
    "renderSummary",
    "renderCards",
    "renderQuiz",
    "renderStudy",
    "controlli_qualita",
    "quality_gate_v34d",
    "Test interattivo",
    "Domande studio",
]

FORBIDDEN = [
    "demo/index.html",
    "README.md",
    "window.location.href='/'",
]


def main() -> int:
    risultati = []
    errori = []

    if not PAGE.exists():
      errori.append(f"Pagina mancante: {PAGE.relative_to(ROOT)}")
    else:
      text = PAGE.read_text(encoding="utf-8", errors="ignore")

      for item in REQUIRED:
          if item not in text:
              errori.append(f"Elemento richiesto mancante nella pagina: {item}")

      for item in FORBIDDEN:
          if item in text:
              errori.append(f"Riferimento vietato nella pagina separata: {item}")

      risultati.append("OK: pagina V3.4F presente")

    if not errori:
        risultati.append("OK: pagina separata visualizza riassunto/card/test/domande studio")
        risultati.append("OK: nessun riferimento vietato a main/README/pulsanti ufficiali")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Demo Output RAG KB Clean V3.4F",
        "",
        "Verifica della pagina separata per visualizzare output V3.4E.",
        "",
        "## Risultati",
    ]

    for r in risultati:
        lines.append(f"- {r}")

    lines.append("")
    lines.append(f"Errori totali: {len(errori)}")
    lines.append("")

    if errori:
        lines.append("## Errori")
        for e in errori:
            lines.append(f"- {e}")
        lines.append("")
        lines.append("ESITO: DA RIVEDERE")
    else:
        lines.append("ESITO: OK")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA DEMO OUTPUT KB CLEAN V3.4F ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA RIVEDERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
