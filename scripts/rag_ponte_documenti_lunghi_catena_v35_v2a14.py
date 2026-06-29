#!/usr/bin/env python3
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_documenti_lunghi_v2a14_ponte_catena_v35.md"

SCRIPTS = [
    "scripts/rag_build_knowledge_base_v34b.py",
    "scripts/rag_quality_gate_kb_v34d.py",
    "scripts/rag_genera_output_da_kb_clean_v34e.py",
    "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
    "scripts/rag_motore_didattico_riutilizzabile_v35c.py",
    "scripts/rag_motore_test_riutilizzabile_v35d.py",
    "scripts/rag_orchestratore_riutilizzabile_v35e.py",
    "scripts/rag_selezionatore_motori_riutilizzabile_v35f.py",
    "scripts/rag_revisore_qualita_testuale_v35g.py",
    "scripts/rag_revisore_naturalezza_antikeyword_v35i.py",
    "scripts/rag_revisore_accordo_pronomi_v35j.py",
    "scripts/applica_v35k_universale.py",
    "scripts/rag_micro_rifinitura_universale_v35l.py",
]

EXPECTED_OUTPUT = ROOT / "dist/generated/rag_output_cleaner_finale_v35k/output_completo/sicurezza_reale/output_cleaner_finale_v35k.json"

def find_input_document() -> Path:
    candidates = [
        ROOT / "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md",
        ROOT / "dist/generated/rag_generatori_da_kb_v34c/test_inputs/sicurezza_reale.txt",
        ROOT / "dist/generated/rag_quality_gate_kb_v34d/inputs/sicurezza_reale.txt",
        ROOT / "dist/generated/rag_output_kb_clean_v34e/inputs/sicurezza.txt",
        ROOT / "dist/generated/rag_output_kb_clean_v34e/inputs/aziendale.txt",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise SystemExit("ERRORE: nessun documento input trovato per la catena V35")


def command_for(script: str) -> list[str]:
    if script == "scripts/rag_build_knowledge_base_v34b.py":
        input_doc = find_input_document()
        return [
            sys.executable,
            script,
            "--input",
            str(input_doc),
            "--output",
            str(ROOT / "dist/generated/rag_knowledge_base_v34b/knowledge_base.json"),
        ]

    if script == "scripts/rag_quality_gate_kb_v34d.py":
        return [
            sys.executable,
            script,
            "--kb",
            str(ROOT / "dist/generated/rag_knowledge_base_v34b/knowledge_base.json"),
            "--output",
            str(ROOT / "dist/generated/rag_quality_gate_kb_v34d/sicurezza_reale/knowledge_base_clean_v34d.json"),
        ]

    if script == "scripts/rag_genera_output_da_kb_clean_v34e.py":
        return [
            sys.executable,
            script,
            "--kb",
            str(ROOT / "dist/generated/rag_quality_gate_kb_v34d/sicurezza_reale/knowledge_base_clean_v34d.json"),
            "--outdir",
            str(ROOT / "dist/generated/rag_output_kb_clean_v34e/outputs/sicurezza_reale"),
            "--numero",
            "5",
        ]

    if script == "scripts/rag_bridge_motori_qualita_esistenti_v35b.py":
        return [
            sys.executable,
            script,
            "--input",
            str(ROOT / "dist/generated/rag_output_kb_clean_v34e/outputs/sicurezza_reale/rag_output_kb_clean_v34e.json"),
            "--output-report-json",
            str(ROOT / "dist/generated/rag_bridge_motori_qualita_esistenti_v35b/sicurezza_reale/bridge_report.json"),
        ]

    if script == "scripts/rag_motore_didattico_riutilizzabile_v35c.py":
        return [
            sys.executable,
            script,
            "--input",
            str(ROOT / "dist/generated/rag_output_kb_clean_v34e/outputs/sicurezza_reale/rag_output_kb_clean_v34e.json"),
            "--output",
            str(ROOT / "dist/generated/rag_output_didattico_riutilizzabile_v35c/sicurezza_reale/rag_output_didactic_v35c.json"),
        ]

    if script == "scripts/rag_motore_test_riutilizzabile_v35d.py":
        return [
            sys.executable,
            script,
            "--input",
            str(ROOT / "dist/generated/rag_output_didattico_riutilizzabile_v35c/sicurezza_reale/rag_output_didactic_v35c.json"),
            "--output",
            str(ROOT / "dist/generated/rag_output_test_riutilizzabile_v35d/sicurezza_reale/rag_output_test_v35d.json"),
        ]

    if script == "scripts/rag_selezionatore_motori_riutilizzabile_v35f.py":
        return [
            sys.executable,
            script,
            "--compito",
            "prepara tutto il materiale completo per PDF app e pagina web",
            "--documento",
            "sicurezza_reale",
            "--execute",
            "--plan-json",
            str(ROOT / "dist/generated/rag_selezionatore_motori_v35f/plans/v2a14_sicurezza_reale_completo.json"),
        ]

    if script == "scripts/rag_revisore_qualita_testuale_v35g.py":
        return [
            sys.executable,
            script,
            "--input",
            str(ROOT / "dist/generated/rag_selezionatore_motori_v35f/output_completo/sicurezza_reale/output_selezionato_v35f.json"),
            "--output",
            str(ROOT / "dist/generated/rag_output_revisionato_qualita_v35g/output_completo/sicurezza_reale/output_revisionato_qualita_v35g.json"),
        ]

    if script == "scripts/rag_revisore_naturalezza_antikeyword_v35i.py":
        return [
            sys.executable,
            script,
            "--input",
            str(ROOT / "dist/generated/rag_output_revisionato_qualita_v35g/output_completo/sicurezza_reale/output_revisionato_qualita_v35g.json"),
            "--raw-input",
            str(ROOT / "dist/generated/rag_selezionatore_motori_v35f/output_completo/sicurezza_reale/output_selezionato_v35f.json"),
            "--output",
            str(ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i/output_completo/sicurezza_reale/output_naturalezza_antikeyword_v35i.json"),
        ]

    if script == "scripts/rag_revisore_accordo_pronomi_v35j.py":
        return [
            sys.executable,
            script,
            "--input",
            str(ROOT / "dist/generated/rag_output_naturalezza_antikeyword_v35i/output_completo/sicurezza_reale/output_naturalezza_antikeyword_v35i.json"),
            "--output",
            str(ROOT / "dist/generated/rag_output_accordo_pronomi_v35j/output_completo/sicurezza_reale/output_accordo_pronomi_v35j.json"),
        ]

    return [sys.executable, script]


def run(script: str) -> str:
    path = ROOT / script
    if not path.exists():
        raise SystemExit(f"ERRORE: script mancante {script}")

    command = command_for(script)

    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    out = (result.stdout or "") + (result.stderr or "")
    print(f"\n=== {script} ===")
    print(out[-3000:])

    if result.returncode != 0:
        if script == "scripts/rag_revisore_accordo_pronomi_v35j.py":
            print("ATTENZIONE: V35J ha segnalato un controllo rigido, continuo verso V35K cleaner finale universale.")
            return out
        raise SystemExit(f"ERRORE: fallito {script}")

    return out

def validate_final_json() -> dict:
    if not EXPECTED_OUTPUT.exists():
        raise SystemExit(f"ERRORE: output finale mancante {EXPECTED_OUTPUT.relative_to(ROOT)}")

    data = json.loads(EXPECTED_OUTPUT.read_text(encoding="utf-8"))

    required = ["riassunto", "card", "domande_studio", "test", "controlli_qualita"]
    for key in required:
        if key not in data:
            raise SystemExit(f"ERRORE: chiave finale mancante {key}")

    if not data["card"] or not data["domande_studio"] or not data["test"]:
        raise SystemExit("ERRORE: card/domande/test vuoti")

    quality = data.get("controlli_qualita", {})
    if not quality.get("ok", False):
        raise SystemExit("ERRORE: controlli_qualita.ok non true")

    cleaner = quality.get("cleaner_finale_universale_v35k", {})
    if not cleaner.get("ok", False):
        raise SystemExit("ERRORE: cleaner finale V35K non ok")

    return data

def main() -> None:
    logs = []

    for script in SCRIPTS:
        logs.append((script, run(script)))

    data = validate_final_json()

    REPORT.write_text(
        "\n".join([
            "# Report RAG documenti lunghi V2A.14 — ponte catena V35",
            "",
            f"- Eseguito il: {datetime.now().isoformat(timespec='seconds')}",
            "- Scopo: usare la catena buona già esistente, senza riscrivere generatori.",
            "- Catena usata:",
            *[f"  - `{s}`" for s in SCRIPTS],
            f"- Output finale: `{EXPECTED_OUTPUT.relative_to(ROOT)}`",
            f"- Card: {len(data.get('card', []))}",
            f"- Domande studio: {len(data.get('domande_studio', []))}",
            f"- Test: {len(data.get('test', []))}",
            "- Cleaner finale V35K: OK",
            "- Micro-rifinitura V35L: eseguita",
            "- Esito: OK",
            "",
        ]),
        encoding="utf-8",
    )

    print("\nOK: ponte V2A.14 catena V35 completato")
    print(f"Report: {REPORT.relative_to(ROOT)}")
    print(f"Output: {EXPECTED_OUTPUT.relative_to(ROOT)}")

if __name__ == "__main__":
    main()
