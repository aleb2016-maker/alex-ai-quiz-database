#!/usr/bin/env python3
"""
Mini LLM - Current Stable Inference Engine.

Motore corrente stabile:
- versione: V3.15 Extended Safe Decoder
- checkpoint: checkpoint-mini-llm-v315-extended-safe
- commit base: 40b18cf

Questo wrapper esegue il motore stabile V3.15 senza duplicare logica.
"""

from pathlib import Path
import runpy


def main() -> None:
    root = Path(__file__).resolve().parents[3]
    target = root / "mini_llm/python/inference/inference_engine_v315_extended_safe_decoder.py"

    if not target.exists():
        raise FileNotFoundError(f"Motore stabile non trovato: {target}")

    runpy.run_path(str(target), run_name="__main__")


if __name__ == "__main__":
    main()
