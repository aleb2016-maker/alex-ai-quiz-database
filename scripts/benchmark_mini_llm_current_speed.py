#!/usr/bin/env python3
"""
Benchmark velocità Mini LLM current.

Misura:
- validazione del motore current stabile;
- caricamento output validati V3.15;
- risposta hot-path su prompt già validati;
- report JSON + Markdown.

Nota:
questo benchmark NON è il motore finale per domande libere.
Serve a creare una base misurabile di velocità.
"""

from __future__ import annotations

import json
import statistics
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple


def normalize(text: str) -> str:
    return " ".join(text.lower().strip().split())


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * p))
    return ordered[index]


def run_validator(root: Path) -> Tuple[int, float]:
    validator = root / "scripts/valida_inference_engine_current.py"

    if not validator.exists():
        raise FileNotFoundError(f"Validatore current non trovato: {validator}")

    start = time.perf_counter()
    result = subprocess.run(
        [sys.executable, str(validator)],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    elapsed = time.perf_counter() - start

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)

    return result.returncode, elapsed


def load_validated_outputs(root: Path) -> Tuple[Dict[str, str], float, int]:
    outputs_path = (
        root
        / "mini_llm/data/inference_v315_extended_safe_decoder/"
        / "inference_engine_v315_extended_safe_decoder_outputs.json"
    )

    if not outputs_path.exists():
        raise FileNotFoundError(f"Output V3.15 non trovato: {outputs_path}")

    start = time.perf_counter()
    data = json.loads(outputs_path.read_text(encoding="utf-8"))
    elapsed = time.perf_counter() - start

    answers: Dict[str, str] = {}

    for item in data:
        if item.get("status") != "OK":
            continue

        prompt = normalize(str(item.get("prompt", "")))
        output = str(item.get("output", "")).strip()

        if prompt and output:
            answers[prompt] = output

    return answers, elapsed, len(data)


def hot_answer(query: str, answers: Dict[str, str]) -> str:
    """
    Hot path minimale:
    risposta per prompt già validati.

    Non inventa risposta se il prompt non è presente.
    """
    return answers.get(normalize(query), "")


def benchmark_hot_path(answers: Dict[str, str], rounds: int = 2000) -> Dict[str, float]:
    prompts = list(answers.keys())

    if not prompts:
        raise RuntimeError("Nessun output OK disponibile per benchmark hot path.")

    timings_ms: List[float] = []

    for i in range(rounds):
        query = prompts[i % len(prompts)]

        start = time.perf_counter()
        output = hot_answer(query, answers)
        elapsed_ms = (time.perf_counter() - start) * 1000.0

        if not output:
            raise RuntimeError(f"Risposta vuota inattesa per prompt: {query}")

        timings_ms.append(elapsed_ms)

    return {
        "rounds": float(rounds),
        "avg_ms": statistics.mean(timings_ms),
        "median_ms": statistics.median(timings_ms),
        "p95_ms": percentile(timings_ms, 0.95),
        "max_ms": max(timings_ms),
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    report_dir = root / "mini_llm/reports"
    data_dir = root / "mini_llm/data/benchmarks"
    report_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    json_report = data_dir / "mini_llm_current_speed_benchmark.json"
    md_report = report_dir / "mini_llm_current_speed_benchmark.md"

    validator_code, validator_seconds = run_validator(root)

    answers, load_seconds, total_outputs = load_validated_outputs(root)
    hot_metrics = benchmark_hot_path(answers)

    status = "PASS" if validator_code == 0 and len(answers) >= 20 else "FAIL"

    result = {
        "benchmark": "mini_llm_current_speed",
        "status": status,
        "current_engine": "inference_engine_v315_extended_safe_decoder",
        "current_checkpoint": "checkpoint-mini-llm-current-v315-stable",
        "validator_code": validator_code,
        "validator_seconds": validator_seconds,
        "total_outputs": total_outputs,
        "ok_outputs_loaded": len(answers),
        "load_outputs_seconds": load_seconds,
        "hot_path": hot_metrics,
        "limits": [
            "Benchmark diagnostico.",
            "Misura prompt già validati, non domande libere.",
            "Non misura ancora riassunti lunghi.",
            "Non sostituisce un motore RAG completo.",
        ],
    }

    json_report.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Mini LLM Current Speed Benchmark",
        "",
        f"- Stato: **{status}**",
        "- Motore current: `inference_engine_v315_extended_safe_decoder`",
        "- Checkpoint current: `checkpoint-mini-llm-current-v315-stable`",
        "",
        "## Validazione",
        "",
        f"- Codice validatore: `{validator_code}`",
        f"- Tempo validazione current: `{validator_seconds:.4f}` secondi",
        "",
        "## Caricamento output validati",
        "",
        f"- Output totali: `{total_outputs}`",
        f"- Output OK caricati: `{len(answers)}`",
        f"- Tempo caricamento JSON: `{load_seconds:.6f}` secondi",
        "",
        "## Hot path risposte validate",
        "",
        f"- Round benchmark: `{int(hot_metrics['rounds'])}`",
        f"- Tempo medio risposta: `{hot_metrics['avg_ms']:.6f}` ms",
        f"- Mediana risposta: `{hot_metrics['median_ms']:.6f}` ms",
        f"- P95 risposta: `{hot_metrics['p95_ms']:.6f}` ms",
        f"- Max risposta: `{hot_metrics['max_ms']:.6f}` ms",
        "",
        "## Limiti",
        "",
        "- Questo benchmark misura il percorso veloce su prompt già validati.",
        "- Non misura ancora domande libere su documenti lunghi.",
        "- Non misura ancora riassunti progressivi.",
        "- Serve come base tecnica per costruire il motore veloce di domande e riassunti.",
        "",
        "## Prossimo passo tecnico",
        "",
        "Per domande libere e riassunti veloci servono:",
        "",
        "1. indicizzazione documento;",
        "2. retrieval dei chunk rilevanti;",
        "3. cache risposte;",
        "4. cache riassunti;",
        "5. benchmark separato per Q&A e riassunti.",
        "",
    ]

    md_report.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(result, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_report}")
    print(f"Report Markdown: {md_report}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
