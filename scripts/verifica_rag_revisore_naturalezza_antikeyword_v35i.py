#!/usr/bin/env python3
"""
Verifica RAG Revisore Naturalezza Anti-keyword V3.5I.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_revisore_naturalezza_antikeyword_v35i.md"

BASE_RAW = ROOT / "dist/generated/rag_selezionatore_motori_v35f"
BASE_IN = ROOT / "dist/generated/rag_output_revisionato_qualita_v35g"
BASE_OUT = ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i"

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

    code, log = run(["python3", "scripts/verifica_rag_revisore_qualita_testuale_v35g.py"])

    if code != 0:
        errori.append("precheck revisore qualità V3.5G fallito")
        errori.append(log)
    else:
        risultati.append("OK: precheck revisore qualità V3.5G")

    for case_name, doc_name, raw_rel in CASES:
        src = BASE_IN / case_name / doc_name / "output_revisionato_qualita_v35g.json"
        raw = BASE_RAW / raw_rel
        dst = BASE_OUT / case_name / doc_name / "output_naturalezza_antikeyword_v35i.json"

        if not src.exists():
            errori.append(f"{case_name}: input V3.5G mancante {src.relative_to(ROOT)}")
            continue

        if not raw.exists():
            errori.append(f"{case_name}: raw input V3.5F mancante {raw.relative_to(ROOT)}")
            continue

        code, log = run([
            "python3",
            "scripts/rag_revisore_naturalezza_antikeyword_v35i.py",
            "--input",
            str(src),
            "--raw-input",
            str(raw),
            "--output",
            str(dst),
        ])

        if code != 0:
            errori.append(f"{case_name}: revisore naturalezza V3.5I fallito")
            errori.append(log)
            continue

        data = json.loads(dst.read_text(encoding="utf-8"))
        q = data.get("controlli_qualita", {}).get("naturalezza_antikeyword_v35i", {})

        if not q.get("ok"):
            errori.append(f"{case_name}: naturalezza anti-keyword non OK: {q}")
            continue

        if "revisione_naturalezza_antikeyword_v35i" not in data:
            errori.append(f"{case_name}: metadati naturalezza V3.5I mancanti")

        risultati.append(
            f"OK: naturalezza anti-keyword V3.5I valida per {case_name} "
            f"({q.get('testi_controllati')} testi)"
        )

    script_text = (ROOT / "scripts/rag_revisore_naturalezza_antikeyword_v35i.py").read_text(
        encoding="utf-8",
        errors="ignore",
    )

    required_markers = [
        "Controllo di naturalezza linguistica anti-keyword",
        "niente_liste_grezze_keyword",
        "niente_frasi_robotiche",
        "card_con_spiegazioni_naturali",
        "messaggi_chiave_utili",
        "riassunto_piu_studiabile",
        "domande_studio_umane",
        "spiegazioni_test_non_meccaniche",
    ]

    for marker in required_markers:
        if marker not in script_text:
            errori.append(f"marker naturalezza mancante: {marker}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report RAG Revisore Naturalezza Anti-keyword V3.5I",
        "",
        "Verifica del controllo di naturalezza linguistica anti-keyword.",
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

    print("=== VERIFICA RAG REVISORE NATURALEZZA ANTI-KEYWORD V3.5I ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
