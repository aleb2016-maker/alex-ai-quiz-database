#!/usr/bin/env python3
"""
Verifica pagina test completo selezionatore/output RAG V3.5H.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "demo-rag/test-selezionatore-output-v35h.html"
REPORT = ROOT / "reports/rag_demo_selezionatore_output_v35h.md"

OUTPUTS = [
    ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i/solo_riassunto/sicurezza_reale/output_naturalezza_antikeyword_v35i.json",
    ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i/solo_card/sicurezza_reale/output_naturalezza_antikeyword_v35i.json",
    ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i/solo_domande_studio/sicurezza_reale/output_naturalezza_antikeyword_v35i.json",
    ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i/solo_test/sicurezza_reale/output_naturalezza_antikeyword_v35i.json",
    ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i/output_completo/sicurezza_reale/output_naturalezza_antikeyword_v35i.json",
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

    if not PAGE.exists():
        errori.append("pagina V3.5H mancante")
    else:
        risultati.append("OK: pagina V3.5H presente")

        text = PAGE.read_text(encoding="utf-8", errors="ignore")

        required = [
            "RAG V3.5H",
            "TASKS",
            "Solo riassunto",
            "Solo card",
            "Domande studio",
            "Test interattivo",
            "Completo",
            "rag_output_naturalezza_antikeyword_v35i",
            "naturalezza_antikeyword_v35i",
            "piano_motori_v35f",
            "opzioni_visibili",
            "risposta_corretta_visibile",
            "renderPlan",
            "renderQuality",
            "renderSummary",
            "renderCards",
            "renderStudy",
            "renderQuiz",
            "activateQuiz",
        ]

        for marker in required:
            if marker not in text:
                errori.append(f"pagina V3.5H: marker mancante {marker}")

        forbidden = [
            "../demo/index.html",
            "README",
            "pulsanti ufficiali",
        ]

        for marker in forbidden:
            if marker in text:
                errori.append(f"pagina V3.5H: riferimento vietato {marker}")

    for output in OUTPUTS:
        if not output.exists():
            errori.append(f"output naturalezza mancante: {output.relative_to(ROOT)}")
            continue

        data = json.loads(output.read_text(encoding="utf-8"))
        q = data.get("controlli_qualita", {}).get("naturalezza_antikeyword_v35i", {})

        if not q.get("ok"):
            errori.append(f"output naturalezza non OK: {output.relative_to(ROOT)}")
        else:
            risultati.append(
                f"OK: output naturalezza {output.relative_to(ROOT)} "
                f"({q.get('testi_controllati')} testi)"
            )

        if "piano_motori_v35f" not in data:
            errori.append(f"piano motori V3.5F mancante in {output.relative_to(ROOT)}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report Demo Selezionatore Output RAG V3.5H",
        "",
        "Verifica della pagina test completa per selezionatore motori e output V3.5I con naturalezza anti-keyword.",
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

    print("=== VERIFICA DEMO SELEZIONATORE OUTPUT V3.5H ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
