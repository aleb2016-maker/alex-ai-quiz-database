#!/usr/bin/env python3
"""
Validatore del motore current stabile.

Current:
- V3.15 Extended Safe Decoder
- checkpoint-mini-llm-v315-extended-safe

Esegue la validazione ufficiale V3.15 e genera anche
un report current leggibile.
"""

from pathlib import Path
import subprocess
import sys


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    validator = root / "scripts/valida_inference_engine_v315_extended_safe_decoder.py"
    source_report = root / "mini_llm/reports/validazione_inference_engine_v315_extended_safe_decoder.md"
    current_report = root / "mini_llm/reports/validazione_inference_engine_current.md"

    if not validator.exists():
        print(f"ERRORE: validatore V3.15 non trovato: {validator}")
        return 1

    result = subprocess.run([sys.executable, str(validator)], cwd=str(root))

    if source_report.exists():
        content = source_report.read_text(encoding="utf-8")
    else:
        content = "Report V3.15 non trovato."

    status = "PASS" if result.returncode == 0 else "FAIL"

    current_report.write_text(
        "\n".join([
            "# Validazione Inference Engine Current",
            "",
            f"- Stato current: **{status}**",
            "- Motore current: `inference_engine_v315_extended_safe_decoder`",
            "- Checkpoint: `checkpoint-mini-llm-v315-extended-safe`",
            "- Commit base: `40b18cf`",
            "",
            "## Report ufficiale V3.15",
            "",
            content,
            "",
        ]),
        encoding="utf-8",
    )

    print("")
    print("===== REPORT CURRENT =====")
    print(current_report.read_text(encoding="utf-8"))

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
