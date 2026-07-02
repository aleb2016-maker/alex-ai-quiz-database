#!/usr/bin/env python3
"""
Benchmark Fast Q&A + Summary Current.

Misura:
- caricamento engine;
- risposte Q&A su domande utente simulate;
- riassunto extractive;
- soglie minime di qualità/velocità.

Codice diagnostico/stabile V1:
non sostituisce ancora un RAG completo su PDF lunghi.
"""

from __future__ import annotations

import importlib.util
import json
import statistics
import sys
import time
from pathlib import Path
from typing import List


QUESTIONS = [
    "Che cosa fa il phishing?",
    "A cosa serve un backup?",
    "Come funziona l'autenticazione a due fattori?",
    "Che cos'è il ransomware?",
    "Perché sono importanti gli aggiornamenti software?",
    "Che cosa sono i dati sensibili?",
    "Come si proteggono le credenziali rubate?",
    "Che cosa fa un password manager?",
    "Che cosa sono gli account amministrativi?",
    "Perché è pericolosa una password rubata?",
]


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * p))
    return ordered[index]


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("fast_qa_summary_current", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)

    # Necessario per dataclass/importlib su alcune versioni Python.
    sys.modules[spec.name] = module

    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    module_path = root / "mini_llm/python/runtime/fast_qa_summary_current.py"
    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_report = data_dir / "fast_qa_summary_current_benchmark.json"
    md_report = report_dir / "fast_qa_summary_current_benchmark.md"

    module = load_module(module_path)

    start_load = time.perf_counter()
    engine = module.FastQASummaryEngine.from_current_outputs(root)
    load_ms = (time.perf_counter() - start_load) * 1000.0

    qa_results = []
    qa_times = []

    for question in QUESTIONS:
        result = engine.ask(question)
        qa_results.append(result)
        qa_times.append(float(result.get("elapsed_ms", 0.0)))

    start_summary = time.perf_counter()
    summary_result = engine.summarize(max_items=8)
    summary_total_ms = (time.perf_counter() - start_summary) * 1000.0

    ok_answers = [
        row for row in qa_results
        if row.get("status") == "OK" and str(row.get("answer", "")).strip()
    ]

    status = "PASS"

    if len(engine.items) < 20:
        status = "FAIL"

    if len(ok_answers) < 8:
        status = "FAIL"

    if summary_result.get("status") != "OK":
        status = "FAIL"

    if qa_times and max(qa_times) > 10.0:
        status = "FAIL"

    if summary_total_ms > 10.0:
        status = "FAIL"

    metrics = {
        "benchmark": "fast_qa_summary_current",
        "status": status,
        "base_engine": "inference_engine_v315_extended_safe_decoder",
        "items_loaded": len(engine.items),
        "questions_total": len(QUESTIONS),
        "answers_ok": len(ok_answers),
        "load_ms": load_ms,
        "qa_avg_ms": statistics.mean(qa_times) if qa_times else 0.0,
        "qa_median_ms": statistics.median(qa_times) if qa_times else 0.0,
        "qa_p95_ms": percentile(qa_times, 0.95),
        "qa_max_ms": max(qa_times) if qa_times else 0.0,
        "summary_ms": float(summary_result.get("elapsed_ms", summary_total_ms)),
        "summary_total_ms": summary_total_ms,
        "summary_items_used": summary_result.get("items_used", 0),
        "qa_results": qa_results,
        "summary": summary_result,
        "limits": [
            "Indice in memoria su output validati current.",
            "Domande simulate, non ancora documenti utente lunghi.",
            "Riassunto extractive breve, non ancora compressione progressiva 10%/1%.",
        ],
    }

    json_report.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Fast Q&A + Summary Current Benchmark",
        "",
        f"- Stato: **{status}**",
        "- Base engine: `inference_engine_v315_extended_safe_decoder`",
        f"- Elementi indicizzati: `{len(engine.items)}`",
        "",
        "## Q&A",
        "",
        f"- Domande testate: `{len(QUESTIONS)}`",
        f"- Risposte OK: `{len(ok_answers)}`",
        f"- Load engine: `{load_ms:.6f}` ms",
        f"- Q&A media: `{metrics['qa_avg_ms']:.6f}` ms",
        f"- Q&A mediana: `{metrics['qa_median_ms']:.6f}` ms",
        f"- Q&A P95: `{metrics['qa_p95_ms']:.6f}` ms",
        f"- Q&A max: `{metrics['qa_max_ms']:.6f}` ms",
        "",
        "## Summary",
        "",
        f"- Summary status: `{summary_result.get('status')}`",
        f"- Frasi usate: `{summary_result.get('items_used')}`",
        f"- Summary time interno: `{metrics['summary_ms']:.6f}` ms",
        f"- Summary time totale: `{summary_total_ms:.6f}` ms",
        "",
        "## Esempi Q&A",
        "",
    ]

    for row in qa_results:
        lines.extend([
            f"### {row.get('question')}",
            "",
            f"- Status: `{row.get('status')}`",
            f"- Tempo: `{float(row.get('elapsed_ms', 0.0)):.6f}` ms",
            f"- Risposta: `{row.get('answer')}`",
            "",
        ])

    lines.extend([
        "## Riassunto generato",
        "",
        str(summary_result.get("summary", "")),
        "",
        "## Limiti",
        "",
        "- Questo è un motore fast Q&A/summary V1 su materiale già validato.",
        "- Non è ancora il motore RAG finale su PDF/documenti lunghi.",
        "- Non usa ancora cache persistente documentale.",
        "- Non produce ancora riassunti al 10% delle pagine o sinossi all'1%.",
        "",
    ])

    md_report.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_report}")
    print(f"Report Markdown: {md_report}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
