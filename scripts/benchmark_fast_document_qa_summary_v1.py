#!/usr/bin/env python3
"""
Benchmark Fast Document Q&A + Summary V1.

Misura il primo runtime documentale:
- costruzione indice da testo;
- Q&A extractive su documento;
- summary extractive;
- performance su testo simulato più lungo.
"""

from __future__ import annotations

import importlib.util
import json
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
    spec = importlib.util.spec_from_file_location("fast_document_qa_summary_v1", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    module_path = root / "mini_llm/python/runtime/fast_document_qa_summary_v1.py"
    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_report = data_dir / "fast_document_qa_summary_v1_benchmark.json"
    md_report = report_dir / "fast_document_qa_summary_v1_benchmark.md"

    module = load_module(module_path)

    # Documento simulato medio: ripetizione controllata con sezioni.
    sections = []
    for idx in range(1, 61):
        sections.append(f"Sezione {idx}. {BASE_DOCUMENT}")

    document = "\\n".join(sections)

    start_build = time.perf_counter()
    engine = module.FastDocumentQASummary.from_text(document, max_words_per_chunk=90)
    build_ms = (time.perf_counter() - start_build) * 1000.0

    qa_results = []
    qa_times = []

    for question in QUESTIONS:
        result = engine.ask(question)
        qa_results.append(result)
        qa_times.append(float(result.get("elapsed_ms", 0.0)))

    start_summary = time.perf_counter()
    summary = engine.summarize(max_sentences=10)
    summary_total_ms = (time.perf_counter() - start_summary) * 1000.0

    ok_answers = [
        row for row in qa_results
        if row.get("status") == "OK" and str(row.get("answer", "")).strip()
    ]

    status = "PASS"

    if len(engine.chunks) < 10:
        status = "FAIL"

    if len(ok_answers) < 9:
        status = "FAIL"

    if summary.get("status") != "OK":
        status = "FAIL"

    if build_ms > 150.0:
        status = "FAIL"

    if qa_times and max(qa_times) > 20.0:
        status = "FAIL"

    if summary_total_ms > 30.0:
        status = "FAIL"

    metrics = {
        "benchmark": "fast_document_qa_summary_v1",
        "status": status,
        "document_chars": len(document),
        "chunks": len(engine.chunks),
        "questions_total": len(QUESTIONS),
        "answers_ok": len(ok_answers),
        "build_index_ms": build_ms,
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
            "Documento testuale simulato, non PDF reale.",
            "Q&A extractive, non generazione libera.",
            "Summary extractive, non ancora compressione progressiva 10%/1%.",
            "Indice in memoria, non ancora cache persistente per file utente.",
        ],
    }

    json_report.write_text(
        json.dumps(metrics, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Fast Document Q&A + Summary V1 Benchmark",
        "",
        f"- Stato: **{status}**",
        f"- Caratteri documento simulato: `{len(document)}`",
        f"- Chunk creati: `{len(engine.chunks)}`",
        "",
        "## Performance",
        "",
        f"- Build indice: `{build_ms:.6f}` ms",
        f"- Q&A media: `{metrics['qa_avg_ms']:.6f}` ms",
        f"- Q&A mediana: `{metrics['qa_median_ms']:.6f}` ms",
        f"- Q&A P95: `{metrics['qa_p95_ms']:.6f}` ms",
        f"- Q&A max: `{metrics['qa_max_ms']:.6f}` ms",
        f"- Summary interno: `{metrics['summary_internal_ms']:.6f}` ms",
        f"- Summary totale: `{summary_total_ms:.6f}` ms",
        "",
        "## Qualità Q&A",
        "",
        f"- Domande testate: `{len(QUESTIONS)}`",
        f"- Risposte OK: `{len(ok_answers)}`",
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
        str(summary.get("summary", "")),
        "",
        "## Limiti",
        "",
        "- Non legge ancora PDF direttamente.",
        "- Non fa OCR.",
        "- Non produce ancora riassunto 10% pagine o sinossi 1%.",
        "- Non usa ancora cache persistente per documenti caricati.",
        "",
    ])

    md_report.write_text("\\n".join(lines), encoding="utf-8")

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_report}")
    print(f"Report Markdown: {md_report}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
