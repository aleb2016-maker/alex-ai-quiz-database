#!/usr/bin/env python3
"""
Benchmark Fast Document Q&A + Summary V2 Cache.

Misura:
- prima indicizzazione documento, cache MISS;
- ricaricamento cache, cache HIT;
- Q&A su engine ricaricato;
- summary su engine ricaricato.

Codice diagnostico/stabile V2.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
import statistics
import sys
import time
from pathlib import Path
from typing import List


BASE_DOCUMENT = """
La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.
Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.
Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi.
I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati.
"""

QUESTIONS = [
    "Che cosa fa il phishing?",
    "A cosa servono i backup regolari?",
    "Come funziona l'autenticazione a due fattori?",
    "Che cos'è il ransomware?",
    "Perché sono importanti gli aggiornamenti software?",
    "Che cosa fa un password manager?",
    "Cosa possono causare le credenziali rubate?",
    "Che cosa sono gli account amministrativi?",
    "Che cosa possono contenere i documenti aziendali?",
    "Che cosa protegge la sicurezza informatica?",
]


def percentile(values: List[float], p: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    index = int(round((len(ordered) - 1) * p))
    return ordered[index]


def load_module(path: Path):
    spec = importlib.util.spec_from_file_location("fast_document_qa_summary_v2_cache", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    module_path = root / "mini_llm/python/runtime/fast_document_qa_summary_v2_cache.py"
    cache_dir = root / "mini_llm/data/fast_runtime/cache_v2_benchmark"
    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_report = data_dir / "fast_document_qa_summary_v2_cache_benchmark.json"
    md_report = report_dir / "fast_document_qa_summary_v2_cache_benchmark.md"

    if cache_dir.exists():
        shutil.rmtree(cache_dir)

    module = load_module(module_path)

    sections = []
    for idx in range(1, 101):
        sections.append(f"Sezione {idx}. {BASE_DOCUMENT}")

    document = "\\n".join(sections)

    engine_miss, miss_info = module.FastDocumentQASummaryCache.from_text_with_cache(
        document,
        cache_dir,
        max_words_per_chunk=90,
    )

    engine_hit, hit_info = module.FastDocumentQASummaryCache.from_text_with_cache(
        document,
        cache_dir,
        max_words_per_chunk=90,
    )

    qa_results = []
    qa_times = []

    for question in QUESTIONS:
        row = engine_hit.ask(question)
        qa_results.append(row)
        qa_times.append(float(row.get("elapsed_ms", 0.0)))

    start_summary = time.perf_counter()
    summary = engine_hit.summarize(max_sentences=10)
    summary_total_ms = (time.perf_counter() - start_summary) * 1000.0

    ok_answers = [
        row for row in qa_results
        if row.get("status") == "OK" and str(row.get("answer", "")).strip()
    ]

    status = "PASS"

    if miss_info.get("cache_status") != "MISS_BUILT":
        status = "FAIL"

    if hit_info.get("cache_status") != "HIT":
        status = "FAIL"

    if len(engine_hit.chunks) < 100:
        status = "FAIL"

    if len(ok_answers) < 9:
        status = "FAIL"

    if summary.get("status") != "OK":
        status = "FAIL"

    if float(hit_info.get("elapsed_ms", 9999.0)) > float(miss_info.get("elapsed_ms", 0.0)) * 1.2:
        status = "FAIL"

    if qa_times and max(qa_times) > 20.0:
        status = "FAIL"

    if summary_total_ms > 40.0:
        status = "FAIL"

    metrics = {
        "benchmark": "fast_document_qa_summary_v2_cache",
        "status": status,
        "document_chars": len(document),
        "chunks": len(engine_hit.chunks),
        "cache_miss": miss_info,
        "cache_hit": hit_info,
        "questions_total": len(QUESTIONS),
        "answers_ok": len(ok_answers),
        "qa_avg_ms": statistics.mean(qa_times) if qa_times else 0.0,
        "qa_median_ms": statistics.median(qa_times) if qa_times else 0.0,
        "qa_p95_ms": percentile(qa_times, 0.95),
        "qa_max_ms": max(qa_times) if qa_times else 0.0,
        "summary_internal_ms": float(summary.get("elapsed_ms", 0.0)),
        "summary_total_ms": summary_total_ms,
        "summary_sentences_used": summary.get("sentences_used", 0),
        "qa_results": qa_results,
        "summary": summary,
        "limits": [
            "Cache persistente su testo, non ancora PDF.",
            "Q&A extractive.",
            "Summary extractive.",
            "Non ancora riassunto progressivo 10%/1%.",
        ],
    }

    json_report.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Fast Document Q&A + Summary V2 Cache Benchmark",
        "",
        f"- Stato: **{status}**",
        f"- Caratteri documento simulato: `{len(document)}`",
        f"- Chunk creati: `{len(engine_hit.chunks)}`",
        "",
        "## Cache",
        "",
        f"- Primo caricamento: `{miss_info.get('cache_status')}`",
        f"- Tempo primo caricamento: `{float(miss_info.get('elapsed_ms', 0.0)):.6f}` ms",
        f"- Secondo caricamento: `{hit_info.get('cache_status')}`",
        f"- Tempo cache hit: `{float(hit_info.get('elapsed_ms', 0.0)):.6f}` ms",
        "",
        "## Q&A",
        "",
        f"- Domande testate: `{len(QUESTIONS)}`",
        f"- Risposte OK: `{len(ok_answers)}`",
        f"- Q&A media: `{metrics['qa_avg_ms']:.6f}` ms",
        f"- Q&A mediana: `{metrics['qa_median_ms']:.6f}` ms",
        f"- Q&A P95: `{metrics['qa_p95_ms']:.6f}` ms",
        f"- Q&A max: `{metrics['qa_max_ms']:.6f}` ms",
        "",
        "## Summary",
        "",
        f"- Summary status: `{summary.get('status')}`",
        f"- Frasi usate: `{summary.get('sentences_used')}`",
        f"- Summary interno: `{metrics['summary_internal_ms']:.6f}` ms",
        f"- Summary totale: `{summary_total_ms:.6f}` ms",
        "",
        "## Limiti",
        "",
        "- Non legge ancora PDF direttamente.",
        "- Non fa OCR.",
        "- Q&A e summary sono ancora extractive.",
        "- Non applica ancora la regola riassunto 10% pagine / sinossi 1%.",
        "",
    ]

    md_report.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_report}")
    print(f"Report Markdown: {md_report}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
