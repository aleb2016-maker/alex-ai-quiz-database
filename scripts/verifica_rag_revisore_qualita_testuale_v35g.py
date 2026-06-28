#!/usr/bin/env python3
"""
Verifica RAG Revisore Qualità Testuale V3.5G.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_revisore_qualita_testuale_v35g.md"
BASE_IN = ROOT / "dist/generated/rag_selezionatore_motori_v35f"
BASE_OUT = ROOT / "dist/generated/rag_output_revisionato_qualita_v35g"

CASES = [
    ("solo_riassunto", "sicurezza_reale", "solo_riassunto/sicurezza_reale/output_selezionato_v35f.json"),
    ("solo_card", "sicurezza_reale", "solo_card/sicurezza_reale/output_selezionato_v35f.json"),
    ("solo_domande_studio", "sicurezza_reale", "solo_domande_studio/sicurezza_reale/output_selezionato_v35f.json"),
    ("solo_test", "sicurezza_reale", "solo_test/sicurezza_reale/output_selezionato_v35f.json"),
    ("output_completo", "sicurezza_reale", "output_completo/sicurezza_reale/output_selezionato_v35f.json"),
]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    risultati = []
    errori = []

    code, log = run(["python3", "scripts/verifica_rag_selezionatore_motori_riutilizzabile_v35f.py"])

    if code != 0:
        errori.append("precheck selezionatore V3.5F fallito")
        errori.append(log)
    else:
        risultati.append("OK: precheck selezionatore V3.5F")

    for case_name, doc_name, rel_input in CASES:
        src = BASE_IN / rel_input
        dst = BASE_OUT / case_name / doc_name / "output_revisionato_qualita_v35g.json"

        if not src.exists():
            errori.append(f"{case_name}: input selezionato mancante {src.relative_to(ROOT)}")
            continue

        code, log = run([
            "python3",
            "scripts/rag_revisore_qualita_testuale_v35g.py",
            "--input",
            str(src),
            "--output",
            str(dst),
        ])

        if code != 0:
            errori.append(f"{case_name}: revisore qualità fallito")
            errori.append(log)
            continue

        data = json.loads(dst.read_text(encoding="utf-8"))
        q = data.get("controlli_qualita", {}).get("qualita_testuale_v35g", {})

        if not q.get("ok"):
            errori.append(f"{case_name}: qualità testuale non OK: {q}")
            continue

        if "categorie_didattiche_v35g" not in data:
            errori.append(f"{case_name}: categorie didattiche mancanti")

        if "revisione_qualita_testuale_v35g" not in data:
            errori.append(f"{case_name}: metadati revisione qualità mancanti")

        risultati.append(
            f"OK: qualità testuale V3.5G valida per {case_name} "
            f"({q.get('testi_controllati')} testi, {q.get('categorie')} categorie)"
        )

    script_text = (ROOT / "scripts/rag_revisore_qualita_testuale_v35g.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_markers = [
        "grammatica_italiana",
        "accenti",
        "apostrofi",
        "domande_naturali",
        "spiegazioni_test",
        "categorie",
        "sottocategorie",
        "qualita_testuale_v35g",
    ]

    for marker in required_markers:
        if marker not in script_text:
            errori.append(f"marker qualità mancante nello script: {marker}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report RAG Revisore Qualità Testuale V3.5G",
        "",
        "Verifica del controllo finale su grammatica, accenti, apostrofi, spiegazioni, categorie e sottocategorie.",
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
        lines.append("ESITO: DA CORREGGERE")
    else:
        lines.append("ESITO: OK")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA RAG REVISORE QUALITÀ TESTUALE V3.5G ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
