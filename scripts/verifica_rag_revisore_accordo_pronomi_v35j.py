#!/usr/bin/env python3
"""
Verifica RAG Revisore Accordo Grammaticale e Pronomi V3.5J.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_revisore_accordo_pronomi_v35j.md"
BASE_IN = ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i"
BASE_OUT = ROOT / "dist/generated/rag_output_accordo_pronomi_v35j"

CASES = [
    ("solo_riassunto", "sicurezza_reale"),
    ("solo_card", "sicurezza_reale"),
    ("solo_domande_studio", "sicurezza_reale"),
    ("solo_test", "sicurezza_reale"),
    ("output_completo", "sicurezza_reale"),
]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def main() -> int:
    risultati = []
    errori = []

    code, log = run(["python3", "scripts/verifica_rag_revisore_naturalezza_antikeyword_v35i.py"])

    if code != 0:
        errori.append("precheck naturalezza anti-keyword V3.5I fallito")
        errori.append(log)
    else:
        risultati.append("OK: precheck naturalezza anti-keyword V3.5I")

    for case_name, doc_name in CASES:
        src = BASE_IN / case_name / doc_name / "output_naturalezza_antikeyword_v35i.json"
        dst = BASE_OUT / case_name / doc_name / "output_accordo_pronomi_v35j.json"

        if not src.exists():
            errori.append(f"{case_name}: input V3.5I mancante {src.relative_to(ROOT)}")
            continue

        code, log = run([
            "python3",
            "scripts/rag_revisore_accordo_pronomi_v35j.py",
            "--input",
            str(src),
            "--output",
            str(dst),
        ])

        if code != 0:
            errori.append(f"{case_name}: revisore accordo/pronomi V3.5J fallito")
            errori.append(log)
            continue

        data = json.loads(dst.read_text(encoding="utf-8"))
        q = data.get("controlli_qualita", {}).get("accordo_pronomi_v35j", {})

        if not q.get("ok"):
            errori.append(f"{case_name}: accordo/pronomi non OK: {q}")
            continue

        if "revisione_accordo_pronomi_v35j" not in data:
            errori.append(f"{case_name}: metadati accordo/pronomi V3.5J mancanti")

        risultati.append(
            f"OK: accordo grammaticale e pronomi V3.5J valido per {case_name} "
            f"({q.get('testi_controllati')} testi)"
        )

    script_text = (ROOT / "scripts/rag_revisore_accordo_pronomi_v35j.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_markers = [
        "Controllo accordo grammaticale e pronomi",
        "genere",
        "numero",
        "articoli",
        "participi",
        "pronomi",
        "accordo_titoli_contenuti",
        "niente_viene_presentato_errato",
        "niente_senza_copiarlo_errato",
        "niente_frasi_tagliate",
        "risposte_guida_meno_meccaniche",
    ]

    for marker in required_markers:
        if marker not in script_text:
            errori.append(f"marker accordo/pronomi mancante: {marker}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report RAG Revisore Accordo Grammaticale e Pronomi V3.5J",
        "",
        "Verifica del controllo su genere, numero, articoli, participi, pronomi, frasi tagliate e risposte guida meccaniche.",
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

    print("=== VERIFICA RAG REVISORE ACCORDO PRONOMI V3.5J ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
