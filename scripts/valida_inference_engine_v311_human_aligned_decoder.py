#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validatore Inference Engine V3.11.

Esegue:
1. Inference Engine V3.11;
2. Semantic Gate V3.8.4 SOLO sugli output V3.11;
3. report finale.

Non fa commit.
Non cancella file.
Non modifica V3.10.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd: Path) -> int:
    print("")
    print("Eseguo:", " ".join(str(x) for x in cmd))
    completed = subprocess.run(cmd, cwd=cwd)
    return completed.returncode


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    inference = root / "mini_llm/python/inference/inference_engine_v311_human_aligned_decoder.py"
    gate = root / "mini_llm/python/quality/model_semantic_gate_v384.py"
    outputs = root / "mini_llm/data/inference_v311_human_aligned_decoder/inference_engine_v311_human_aligned_decoder_outputs.json"
    manifest = root / "mini_llm/data/quality/model_semantic_gate_v384/model_semantic_gate_v384_manifest.json"
    validation_report = root / "mini_llm/reports/validazione_inference_engine_v311_human_aligned_decoder.md"

    if not inference.exists():
        print(f"ERRORE: inference non trovata: {inference}")
        return 2

    if not gate.exists():
        print(f"ERRORE: Semantic Gate V3.8.4 non trovato: {gate}")
        return 2

    code_inference = run([sys.executable, str(inference)], root)

    if not outputs.exists():
        print(f"ERRORE: output V3.11 non generato: {outputs}")
        return 2

    code_gate = run([sys.executable, str(gate), str(outputs)], root)

    gate_status = "UNKNOWN"
    gate_failed = None
    gate_total = None

    if manifest.exists():
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
            gate_status = data.get("status", "UNKNOWN")
            gate_failed = data.get("failed")
            gate_total = data.get("total_outputs_checked")
        except Exception:
            pass

    final_status = "PASS" if code_inference == 0 and code_gate == 0 and gate_status == "PASS" else "FAIL"

    lines = []
    lines.append("# Validazione Inference Engine V3.11 Human Aligned Decoder")
    lines.append("")
    lines.append(f"- Stato finale: **{final_status}**")
    lines.append(f"- Codice inference: `{code_inference}`")
    lines.append(f"- Codice semantic gate V3.8.4: `{code_gate}`")
    lines.append(f"- Semantic Gate status: `{gate_status}`")
    lines.append(f"- Output controllati dal gate: `{gate_total}`")
    lines.append(f"- Output falliti dal gate: `{gate_failed}`")
    lines.append("")
    lines.append("## File generati")
    lines.append("")
    lines.append(f"- Output inferenza: `{outputs.relative_to(root)}`")
    lines.append("- Report inferenza: `mini_llm/reports/inference_engine_v311_human_aligned_decoder_report.md`")
    lines.append("- Report gate: `mini_llm/reports/model_semantic_gate_v384_report.md`")
    lines.append("")
    lines.append("## Regola di accettazione")
    lines.append("")
    lines.append("La V3.11 è accettabile solo se:")
    lines.append("")
    lines.append("- l'inference interna è PASS;")
    lines.append("- il Semantic Gate V3.8.4 è PASS;")
    lines.append("- gli output sono buoni anche a controllo umano;")
    lines.append("- non ci sono sostituzioni cieche del soggetto;")
    lines.append("- non ci sono liste senza separatori o verbi accostati male.")
    lines.append("")
    lines.append("Se passa formalmente ma le frasi sono brutte, non va committata come motore valido.")

    validation_report.write_text("\n".join(lines), encoding="utf-8")

    print("")
    print("Report validazione:")
    print(validation_report)
    print("")
    print("\n".join(lines))

    return 0 if final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
