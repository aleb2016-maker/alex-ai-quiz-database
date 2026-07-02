#!/usr/bin/env python3
"""
Benchmark Mini LLM Long Document RAG V3.9.

Corretto:
- niente IndexError se lo Study Pack fallisce;
- contesto RAG più vario;
- report scritto sempre;
- commit solo se PASS.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path


def safe_first(items):
    if isinstance(items, list) and items:
        return items[0]
    return {}


def load_module(root: Path):
    path = root / "mini_llm/python/runtime/mini_llm_long_document_rag_v39.py"

    spec = importlib.util.spec_from_file_location("mini_llm_long_document_rag_v39", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def build_synthetic_500_pages() -> str:
    pages = []

    for page in range(1, 501):
        topic = page % 10

        if topic in {0, 1, 2}:
            paragraph = (
                f"[PAGE {page}] "
                f"La sicurezza informatica della pagina {page} protegge dati, dispositivi, account e sistemi aziendali. "
                f"Il phishing della pagina {page} usa l'inganno per convincere le persone a fornire credenziali, dati sensibili o pagamenti. "
                f"L'autenticazione a due fattori della pagina {page} rafforza l'accesso con un secondo controllo oltre alla password. "
                f"Le credenziali rubate della pagina {page} possono consentire accessi non autorizzati ad account e sistemi. "
                f"Gli account amministrativi della pagina {page} hanno privilegi elevati e richiedono controlli aggiuntivi. "
            )
        elif topic in {3, 4, 5}:
            paragraph = (
                f"[PAGE {page}] "
                f"I backup regolari della pagina {page} servono a recuperare informazioni dopo errori, guasti, furti o cancellazioni accidentali. "
                f"Il ransomware della pagina {page} blocca o cifra dati e chiede un pagamento per ripristinarli. "
                f"Gli aggiornamenti software della pagina {page} correggono errori e chiudono vulnerabilità di sicurezza. "
                f"Le procedure di ripristino della pagina {page} aiutano a ridurre tempi di fermo e perdita di dati. "
                f"I registri di backup della pagina {page} permettono di controllare esito, frequenza e integrità delle copie. "
            )
        elif topic in {6, 7}:
            paragraph = (
                f"[PAGE {page}] "
                f"La formazione del personale della pagina {page} riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano. "
                f"Le procedure di sicurezza della pagina {page} aiutano a gestire incidenti, accessi, backup, dispositivi e comunicazioni interne. "
                f"I documenti aziendali della pagina {page} possono contenere informazioni operative, contratti, credenziali o dati riservati. "
                f"Le policy interne della pagina {page} definiscono responsabilità, controlli e comportamenti accettabili. "
                f"La comunicazione interna della pagina {page} aiuta a segnalare anomalie e incidenti in modo tempestivo. "
            )
        else:
            paragraph = (
                f"[PAGE {page}] "
                f"Il monitoraggio della pagina {page} osserva eventi, accessi, errori e comportamenti anomali nei sistemi. "
                f"I log della pagina {page} aiutano a ricostruire incidenti, tentativi di accesso e modifiche importanti. "
                f"La classificazione dei dati della pagina {page} distingue informazioni pubbliche, interne, riservate e critiche. "
                f"La gestione dei dispositivi della pagina {page} controlla aggiornamenti, configurazioni, autorizzazioni e protezioni. "
                f"La revisione periodica della pagina {page} migliora processi, controlli e misure tecniche. "
            )

        pages.append(paragraph)

    return "\n".join(pages)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    module = load_module(root)

    synthetic_text = build_synthetic_500_pages()

    start = time.perf_counter()

    rag = module.MiniLLMLongDocumentRAGV39(
        synthetic_text,
        words_per_page=120,
        max_words_per_chunk=160,
        overlap_words=25,
    )

    diagnostics = rag.diagnostics()

    retrieval = rag.retrieve(
        "sicurezza phishing credenziali account backup ransomware aggiornamenti formazione procedure documenti policy monitoraggio log classificazione dispositivi revisione",
        top_k=40,
    )

    answer = rag.answer_query(
        "Che cosa fa il phishing?",
        top_k=12,
        max_sentences=5,
    )

    progressive_summary = rag.progressive_summary(
        max_quality_sentences=100,
        max_brief_sentences=24,
    )

    study_pack = rag.study_pack_from_query(
        "sicurezza phishing credenziali account backup ransomware aggiornamenti formazione procedure documenti policy monitoraggio log classificazione dispositivi revisione",
        top_k=40,
        max_chars=24000,
    )

    total_ms = (time.perf_counter() - start) * 1000.0

    study_pack_inner = study_pack.get("study_pack", {}) if isinstance(study_pack, dict) else {}
    pack_counts = study_pack_inner.get("counts", {}) if isinstance(study_pack_inner, dict) else {}

    errors = []

    if diagnostics.get("engine") != "mini_llm_long_document_rag_v39":
        errors.append("engine_name_wrong")

    lineage = diagnostics.get("lineage", {})

    if lineage.get("semantic_quality_line") != "V3.8/V3.8.6":
        errors.append("lineage_missing_v38")

    if lineage.get("current_engine") != "V3.15 stable current":
        errors.append("lineage_missing_v315")

    if diagnostics.get("status") != "OK":
        errors.append("diagnostics_not_ok")

    if diagnostics.get("pages") != 500:
        errors.append(f"page_count_not_500:{diagnostics.get('pages')}")

    if diagnostics.get("chunks", 0) < 200:
        errors.append(f"chunks_too_few:{diagnostics.get('chunks')}")

    targets = diagnostics.get("compression_targets", {})

    if targets.get("quality_summary_pages_10_percent") != 50:
        errors.append(f"quality_target_not_50:{targets.get('quality_summary_pages_10_percent')}")

    if targets.get("brief_summary_pages_1_percent") != 5:
        errors.append(f"brief_target_not_5:{targets.get('brief_summary_pages_1_percent')}")

    if len(retrieval) < 20:
        errors.append("retrieval_less_than_20")

    if answer.get("status") != "OK":
        errors.append(f"answer_not_ok:{answer.get('status')}")

    if "phishing" not in str(answer.get("answer", "")).lower():
        errors.append("answer_missing_phishing")

    if progressive_summary.get("status") != "OK":
        errors.append(f"summary_not_ok:{progressive_summary.get('status')}")

    if progressive_summary.get("quality_sentences", 0) < 20:
        errors.append("quality_summary_too_short_for_available_unique_content")

    if progressive_summary.get("brief_sentences", 0) < 10:
        errors.append("brief_summary_too_short_for_benchmark")

    if study_pack.get("status") != "OK":
        errors.append(f"study_pack_not_ok:{study_pack.get('status')}")

    if pack_counts.get("cards", 0) < 6:
        errors.append("study_pack_cards_less_than_6")

    if pack_counts.get("qas", 0) < 8:
        errors.append("study_pack_qas_less_than_8")

    if pack_counts.get("student_test_questions", 0) < 6:
        errors.append("study_pack_student_test_less_than_6")

    if total_ms > 5000.0:
        errors.append(f"total_too_slow:{total_ms}")

    status = "PASS" if not errors else "FAIL"

    report = {
        "benchmark": "mini_llm_long_document_rag_v39",
        "status": status,
        "errors": errors,
        "total_ms": total_ms,
        "diagnostics": diagnostics,
        "retrieval_sample": [
            {
                "chunk_id": item.chunk_id,
                "page_start": item.page_start,
                "page_end": item.page_end,
                "score": item.score,
            }
            for item in retrieval[:8]
        ],
        "answer": answer,
        "progressive_summary": {
            "status": progressive_summary.get("status"),
            "targets": progressive_summary.get("targets"),
            "quality_sentences": progressive_summary.get("quality_sentences"),
            "brief_sentences": progressive_summary.get("brief_sentences"),
            "elapsed_ms": progressive_summary.get("elapsed_ms"),
            "quality_preview": str(progressive_summary.get("quality_summary", ""))[:1200],
            "brief_preview": str(progressive_summary.get("brief_summary", ""))[:800],
        },
        "study_pack": {
            "status": study_pack.get("status"),
            "elapsed_ms": study_pack.get("elapsed_ms"),
            "context": study_pack.get("context"),
            "counts": pack_counts,
            "quality_errors": study_pack_inner.get("quality_errors", []),
            "first_card": safe_first(study_pack_inner.get("cards", [])),
            "first_qa": safe_first(study_pack_inner.get("qas", [])),
            "first_student_test": safe_first(study_pack_inner.get("student_test", [])),
        },
        "limits": [
            "V3.9 valida 500 pagine simulate.",
            "RAG e summary sono extractive/structured.",
            "Non ancora LLM neurale generativo.",
            "Non ancora OCR.",
            "Il prossimo step dovrà migliorare riassunto progressivo multi-pass e output lungo reale.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_long_document_rag_v39_benchmark.json"
    md_path = report_dir / "mini_llm_long_document_rag_v39_benchmark.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Mini LLM Long Document RAG V3.9 Benchmark",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        f"- Tempo totale: `{total_ms:.6f}` ms",
        "",
        "## Linea di continuità",
        "",
        "- V3.8/V3.8.6: qualità semantica e gate.",
        "- V3.15: current stabile.",
        "- Study Pack Current V3: output controllato.",
        "- Output Modes V1: selezione output.",
        "- Long Document RAG V3.9: documenti lunghi.",
        "",
        "## Documento lungo simulato",
        "",
        f"- Pagine: `{diagnostics.get('pages')}`",
        f"- Parole: `{diagnostics.get('words')}`",
        f"- Chunk: `{diagnostics.get('chunks')}`",
        f"- Build index: `{float(diagnostics.get('build_ms', 0.0)):.6f}` ms",
        "",
        "## Target compressione",
        "",
        f"- Riassunto qualità 10%: `{targets.get('quality_summary_pages_10_percent')}` pagine equivalenti",
        f"- Sintesi breve 1%: `{targets.get('brief_summary_pages_1_percent')}` pagine equivalenti",
        "",
        "## Retrieval/Q&A",
        "",
        f"- Answer status: `{answer.get('status')}`",
        f"- Frasi risposta: `{answer.get('sentences_used')}`",
        "",
        "### Risposta esempio",
        "",
        str(answer.get("answer", ""))[:1500],
        "",
        "## Riassunto progressivo",
        "",
        f"- Stato: `{progressive_summary.get('status')}`",
        f"- Frasi quality benchmark: `{progressive_summary.get('quality_sentences')}`",
        f"- Frasi brief benchmark: `{progressive_summary.get('brief_sentences')}`",
        f"- Tempo: `{float(progressive_summary.get('elapsed_ms', 0.0)):.6f}` ms",
        "",
        "### Quality preview",
        "",
        str(progressive_summary.get("quality_summary", ""))[:1600],
        "",
        "### Brief preview",
        "",
        str(progressive_summary.get("brief_summary", ""))[:1000],
        "",
        "## Study Pack da contesto RAG",
        "",
        f"- Status: `{study_pack.get('status')}`",
        f"- Conteggi: `{pack_counts}`",
        f"- Quality errors: `{study_pack_inner.get('quality_errors', [])}`",
        "",
        "## Limiti",
        "",
        "- V3.9 valida la struttura lunga su 500 pagine simulate.",
        "- Non è ancora LLM neurale generativo.",
        "- Non è ancora OCR.",
        "- Non genera ancora materialmente 50 pagine complete nel report.",
        "- Il prossimo blocco dovrà migliorare il riassunto progressivo multi-pass.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
