#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Validatore V3.15 Extended Safe Decoder.

Esegue:
1. Inference V3.15;
2. Semantic Gate V3.8.6 sugli output OK;
3. report finale.

Non fa commit.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def run(cmd, cwd: Path) -> int:
    print("")
    print("Eseguo:", " ".join(str(x) for x in cmd))
    return subprocess.run(cmd, cwd=cwd).returncode


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    inference = root / "mini_llm/python/inference/inference_engine_v315_extended_safe_decoder.py"
    gate = root / "mini_llm/python/quality/model_semantic_gate_v386.py"
    outputs = root / "mini_llm/data/inference_v315_extended_safe_decoder/inference_engine_v315_extended_safe_decoder_outputs.json"
    gate_input = root / "mini_llm/data/inference_v315_extended_safe_decoder/inference_engine_v315_extended_safe_decoder_gate_input.json"
    manifest = root / "mini_llm/data/quality/model_semantic_gate_v386/model_semantic_gate_v386_manifest.json"
    validation_report = root / "mini_llm/reports/validazione_inference_engine_v315_extended_safe_decoder.md"

    if not inference.exists():
        print(f"ERRORE: inference non trovata: {inference}")
        return 2

    if not gate.exists():
        print(f"ERRORE: gate V3.8.6 non trovato: {gate}")
        return 2

    code_inference = run([sys.executable, str(inference)], root)

    if not outputs.exists():
        print(f"ERRORE: output V3.15 non generato: {outputs}")
        return 2

    data = json.loads(outputs.read_text(encoding="utf-8"))
    ok_outputs = [row for row in data if row.get("status") == "OK" and row.get("output")]
    gate_input.write_text(json.dumps(ok_outputs, ensure_ascii=False, indent=2), encoding="utf-8")

    code_gate = run([sys.executable, str(gate), str(gate_input)], root)

    gate_status = "UNKNOWN"
    gate_failed = None
    gate_total = None

    if manifest.exists():
        gate_manifest = json.loads(manifest.read_text(encoding="utf-8"))
        gate_status = gate_manifest.get("status", "UNKNOWN")
        gate_failed = gate_manifest.get("failed")
        gate_total = gate_manifest.get("total_outputs_checked")

    total = len(data)
    ok = len(ok_outputs)
    failed_internal = total - ok

    final_status = "PASS" if code_inference == 0 and code_gate == 0 and gate_status == "PASS" else "FAIL"

    lines = []
    lines.append("# Validazione Inference Engine V3.15 Extended Safe Decoder")
    lines.append("")
    lines.append(f"- Stato finale: **{final_status}**")
    lines.append(f"- Codice inference: `{code_inference}`")
    lines.append(f"- Codice semantic gate V3.8.6: `{code_gate}`")
    lines.append(f"- Output totali: `{total}`")
    lines.append(f"- Output OK interni: `{ok}`")
    lines.append(f"- Output falliti interni: `{failed_internal}`")
    lines.append(f"- Semantic Gate status: `{gate_status}`")
    lines.append(f"- Output controllati dal gate: `{gate_total}`")
    lines.append(f"- Output falliti dal gate: `{gate_failed}`")
    lines.append("")
    lines.append("## Regola")
    lines.append("")
    lines.append("V3.15 è accettabile solo se:")
    lines.append("")
    lines.append("- produce almeno 10 output OK;")
    lines.append("- non copia identica dal corpus;")
    lines.append("- non ha score negativi marcati OK;")
    lines.append("- passa Semantic Gate V3.8.6;")
    lines.append("- gli output OK sono buoni anche a controllo umano.")

    validation_report.write_text("\n".join(lines), encoding="utf-8")

    print("")
    print("\n".join(lines))

    return 0 if final_status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
