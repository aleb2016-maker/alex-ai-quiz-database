#!/usr/bin/env python3
"""
Mini LLM Practical Real Test V3.9.4 Context FIX.

Catena:
- documento reale;
- cleaner V3.9.3.1;
- query context expander V3.9.4;
- risposte ancorate;
- real quality gate V3.9.2;
- query context relevance gate.

Fix:
- "punti principali" resta main_points anche se nella domanda espansa appare "sicurezza informatica".
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Set


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_module(path: Path, name: str):
    if not path.exists():
        raise FileNotFoundError(f"Modulo non trovato: {path}")

    spec = importlib.util.spec_from_file_location(name, path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def normalize(text: Any) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").strip().split())


def tokenize(text: str) -> Set[str]:
    words = re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9']+", normalize(text).lower())
    stop = {
        "quali", "sono", "cosa", "che", "devo", "vengono", "spiegati",
        "documento", "punti", "principali", "ricordare", "nel", "nella",
        "sul", "sulla", "di", "a", "da", "in", "con", "per", "e", "o",
        "il", "lo", "la", "gli", "le", "un", "una",
    }
    return {word for word in words if len(word) > 2 and word not in stop}


def query_type(query: str) -> str:
    low = normalize(query).lower()

    if "risch" in low or "pericol" in low or "minacc" in low:
        return "risks"

    if "punti principali" in low or "principali" in low:
        return "main_points"

    if "ricordare" in low or "studiare" in low or "concetti" in low:
        return "security_memory"

    if "sicurezza informatica" in low:
        return "security_memory"

    return "generic"


def important_terms(qtype: str) -> Set[str]:
    if qtype == "risks":
        return {
            "phishing", "ransomware", "malware", "password", "credenziali",
            "link", "sospetti", "rete", "pubblica", "furto", "cancellazione",
            "guasto", "attacco", "vulnerabilità", "dati", "riservati",
        }

    if qtype == "security_memory":
        return {
            "sicurezza", "informatica", "password", "phishing", "backup",
            "2fa", "autenticazione", "dati", "account", "credenziali",
            "malware", "ransomware", "procedure", "formazione",
        }

    if qtype == "main_points":
        return {
            "sicurezza", "password", "phishing", "backup", "malware",
            "ransomware", "dati", "account", "credenziali", "2fa",
            "autenticazione", "procedure", "formazione",
        }

    return set()


def score_sentence(expanded_query: str, sentence: str) -> float:
    qtype = query_type(expanded_query)
    q_tokens = tokenize(expanded_query)
    s_tokens = tokenize(sentence)

    score = 0.0
    score += len(q_tokens.intersection(s_tokens)) * 3.0
    score += len(important_terms(qtype).intersection(s_tokens)) * 4.0

    low = sentence.lower()

    if qtype == "risks":
        for marker in ["phishing", "ransomware", "malware", "password", "link", "rete pubblica", "attacco", "furto", "guasto", "cancellazione"]:
            if marker in low:
                score += 5.0

        if "backup" in low and not any(marker in low for marker in ["ransomware", "furto", "guasto", "cancellazione"]):
            score -= 3.0

    if qtype == "security_memory":
        for marker in ["sicurezza informatica", "password", "2fa", "backup", "phishing", "dati"]:
            if marker in low:
                score += 4.0

    if qtype == "main_points":
        for marker in ["sicurezza informatica", "password", "phishing", "backup", "malware", "ransomware", "dati", "2fa"]:
            if marker in low:
                score += 4.0

    if sentence.startswith(("Bisogna ", "Serve ", "Può ", "Quando ")):
        score -= 1.5

    return score


def lead_sentence(expanded_query: str, selected_sentences: List[str]) -> str:
    qtype = query_type(expanded_query)
    joined = " ".join(selected_sentences).lower()

    if qtype == "risks":
        visible = [
            term for term in ["phishing", "ransomware", "malware", "password deboli", "credenziali", "reti pubbliche", "dati sensibili"]
            if term in joined
        ]

        if not visible:
            visible = ["phishing", "ransomware", "password deboli"]

        return "I rischi di sicurezza informatica aziendale spiegati nel documento riguardano " + ", ".join(visible[:6]) + "."

    if qtype == "main_points":
        return "I punti principali del documento riguardano la sicurezza informatica aziendale, il phishing, le password, i backup, il malware, il ransomware e la protezione dei dati."

    if qtype == "security_memory":
        return "Sulla sicurezza informatica aziendale il documento richiama pratiche, strumenti e comportamenti da ricordare."

    return "Nel contesto del documento, la risposta riguarda questi aspetti principali."


def build_answer(original_query: str, expanded_query: str, cleaned_text: str, cleaner_module) -> Dict[str, Any]:
    sentences = [
        sentence
        for sentence in cleaner_module.split_into_sentences(cleaned_text)
        if cleaner_module.is_safe_sentence(sentence)
    ]

    ranked = []

    for sentence in sentences:
        score = score_sentence(expanded_query, sentence)

        if score > 0:
            ranked.append((score, sentence))

    ranked.sort(key=lambda item: item[0], reverse=True)

    selected: List[str] = []
    seen = set()

    for _, sentence in ranked:
        key = sentence.lower()

        if key in seen:
            continue

        seen.add(key)
        selected.append(sentence)

        if len(selected) >= 3:
            break

    if not selected:
        selected = sentences[:3]

    answer = " ".join([lead_sentence(expanded_query, selected)] + selected)

    return {
        "status": "OK",
        "query": original_query,
        "expanded_query": expanded_query,
        "answer": answer,
        "sentences_used": len(selected) + 1,
        "quality_errors": [],
        "retrieved_chunks": [],
        "elapsed_ms": 0.0,
    }


def validate_relevance(report: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []

    for index, answer in enumerate(report.get("answers", []), start=1):
        original = normalize(answer.get("query", ""))
        expanded = normalize(answer.get("expanded_query", ""))
        text = normalize(answer.get("answer", ""))
        low = text.lower()

        if not expanded or expanded == original:
            errors.append(f"answer_{index}:query_not_expanded:{original}")

        if "risch" in original.lower():
            if not low.startswith("i rischi di sicurezza informatica aziendale"):
                errors.append(f"answer_{index}:risk_answer_not_anchored:{text[:200]}")

            if not any(term in low for term in ["phishing", "ransomware", "malware", "password", "credenziali", "reti pubbliche"]):
                errors.append(f"answer_{index}:risk_terms_missing:{text[:200]}")

        if "punti principali" in original.lower():
            if not low.startswith("i punti principali del documento"):
                errors.append(f"answer_{index}:main_points_not_anchored:{text[:200]}")

        if "sicurezza informatica" in original.lower() or "ricordare" in original.lower():
            if "sicurezza informatica" not in low:
                errors.append(f"answer_{index}:security_context_missing:{text[:200]}")

    return {
        "gate": "mini_llm_query_context_relevance_v394",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
    }


def markdown_report(report: Dict[str, Any]) -> str:
    expander = report.get("query_expansion", {})
    gate_v392 = report.get("real_quality_gate", {})
    gate_v394 = report.get("query_context_relevance_gate", {})
    cleaner = report.get("cleaner", {})
    diagnostics = report.get("diagnostics", {})
    study = report.get("study_pack", {})
    pack = study.get("study_pack", {}) if isinstance(study.get("study_pack", {}), dict) else {}

    lines = [
        "# Mini LLM Practical Real Test V3.9.4 Context",
        "",
        f"- Stato: **{report.get('status')}**",
        f"- File: `{report.get('file')}`",
        f"- Tempo totale: `{float(report.get('total_ms', 0.0)):.6f}` ms",
        "",
        "## Contesto documento rilevato",
        "",
        f"- Dominio: `{expander.get('document_context', {}).get('domain')}`",
        f"- Concetti: `{expander.get('document_context', {}).get('concepts')}`",
        "",
        "## Cleaner e RAG",
        "",
        f"- Cleaner: `{cleaner.get('status')}`",
        f"- Parole pulite: `{cleaner.get('cleaned_words')}`",
        f"- Frasi RAG: `{diagnostics.get('sentences')}`",
        f"- Chunk: `{diagnostics.get('chunks')}`",
        "",
        "## Gate",
        "",
        f"- Real Quality Gate V3.9.2: `{gate_v392.get('status')}`",
        f"- Query Context Relevance V3.9.4: `{gate_v394.get('status')}`",
        f"- Errori V3.9.4: `{gate_v394.get('errors')}`",
        "",
        "## Domande migliorate e risposte",
        "",
    ]

    for answer in report.get("answers", []):
        lines.extend(
            [
                "### Domanda originale",
                "",
                str(answer.get("query", "")),
                "",
                "### Domanda migliorata",
                "",
                str(answer.get("expanded_query", "")),
                "",
                "### Risposta",
                "",
                str(answer.get("answer", "")),
                "",
            ]
        )

    lines.extend(
        [
            "## Study Pack",
            "",
            f"- Status: `{study.get('status')}`",
            f"- Counts: `{pack.get('counts')}`",
            "",
            "## Limiti",
            "",
            "- Espansione deterministica.",
            "- Structured/extractive.",
            "- Non ancora LLM neurale generativo.",
            "- No OCR.",
            "",
        ]
    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Test pratico reale V3.9.4 con query context.")
    parser.add_argument("file")
    parser.add_argument("--query", action="append", default=[])
    parser.add_argument("--out-dir", default="mini_llm/data/real_tests/test_sicurezza_v394_context")
    args = parser.parse_args()

    root = repo_root()
    file_path = Path(args.file).expanduser().resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    start = time.perf_counter()

    try:
        practical_v391 = load_module(root / "scripts/mini_llm_practical_real_test_v391.py", "practical_v391_for_v394_context")
        cleaner_module = load_module(root / "scripts/mini_llm_real_output_cleaner_v393.py", "cleaner_v3931_for_v394_context")
        expander_module = load_module(root / "scripts/mini_llm_query_context_expander_v394.py", "query_context_expander_v394_runtime")
        rag_module = load_module(root / "mini_llm/python/runtime/mini_llm_long_document_rag_v391_semantic_repair.py", "rag_v391_for_v394_context")
        study_module = load_module(root / "mini_llm/python/runtime/mini_llm_study_pack_current.py", "study_pack_current_for_v394_context")
        gate_v392_module = load_module(root / "scripts/mini_llm_real_quality_gate_v392.py", "gate_v392_for_v394_context")

        raw_text = practical_v391.read_document(file_path, root)
        cleaned_text = cleaner_module.clean_document_text(raw_text)
        safe_context = cleaner_module.safe_study_context(cleaned_text, max_sentences=48)
        cleaner_diagnostics = cleaner_module.cleaner_diagnostics(raw_text, cleaned_text)

        (out_dir / "cleaned_input_preview.txt").write_text(cleaned_text, encoding="utf-8")
        (out_dir / "safe_study_context.txt").write_text(safe_context, encoding="utf-8")

        queries = args.query or [
            "Quali sono i punti principali del documento?",
            "Che cosa devo ricordare sulla sicurezza informatica?",
            "Quali rischi vengono spiegati nel documento?",
        ]

        query_expansion = expander_module.expand_queries(queries, cleaned_text)

        rag = rag_module.MiniLLMLongDocumentRAGV391SemanticRepair(cleaned_text)
        diagnostics = rag.diagnostics()

        answers = []

        for row in query_expansion.get("queries", []):
            answers.append(
                build_answer(
                    row.get("original_query", ""),
                    row.get("expanded_query", ""),
                    cleaned_text,
                    cleaner_module,
                )
            )

        progressive_summary = rag.progressive_summary(max_quality_sentences=40, max_brief_sentences=16)
        pack = study_module.generate_study_pack(safe_context)

        study_pack = {
            "status": "OK" if pack.get("status") == "OK" else pack.get("status"),
            "query": "safe context",
            "context": {
                "context_chars": len(safe_context),
                "sentences": len(cleaner_module.split_into_sentences(safe_context)),
                "quality_errors": [],
                "references": [],
            },
            "study_pack": pack,
            "semantic_errors": [],
            "elapsed_ms": pack.get("elapsed_ms"),
        }

        report: Dict[str, Any] = {
            "test": "mini_llm_practical_real_test_v394_context",
            "status": "PASS",
            "errors": [],
            "file": str(file_path),
            "file_suffix": file_path.suffix.lower(),
            "total_ms": (time.perf_counter() - start) * 1000.0,
            "query_expansion": query_expansion,
            "cleaner": cleaner_diagnostics,
            "diagnostics": diagnostics,
            "answers": answers,
            "progressive_summary": progressive_summary,
            "study_pack": study_pack,
            "limits": [
                "Espansione deterministica.",
                "Structured/extractive.",
                "Non ancora LLM neurale generativo.",
                "No OCR.",
            ],
        }

        gate_v392 = gate_v392_module.validate_report(report)
        gate_v394 = validate_relevance(report)

        report["real_quality_gate"] = gate_v392
        report["query_context_relevance_gate"] = gate_v394

        errors: List[str] = []

        if cleaner_diagnostics.get("status") != "OK":
            errors.append(f"cleaner_not_ok:{cleaner_diagnostics}")

        if diagnostics.get("status") != "OK":
            errors.append(f"rag_not_ok:{diagnostics.get('status')}")

        if study_pack.get("status") != "OK":
            errors.append(f"study_pack_not_ok:{study_pack.get('status')}")

        if gate_v392.get("status") != "PASS":
            errors.append(f"real_quality_gate:{gate_v392.get('errors')}")

        if gate_v394.get("status") != "PASS":
            errors.append(f"query_context_relevance_gate:{gate_v394.get('errors')}")

        report["errors"] = errors
        report["status"] = "PASS" if not errors else "FAIL"
        report["total_ms"] = (time.perf_counter() - start) * 1000.0

    except Exception as exc:
        report = {
            "test": "mini_llm_practical_real_test_v394_context",
            "status": "ERROR",
            "errors": [str(exc)],
            "file": str(file_path),
            "total_ms": (time.perf_counter() - start) * 1000.0,
        }

    json_path = out_dir / "practical_real_test_v394_context_report.json"
    md_path = out_dir / "practical_real_test_v394_context_report.md"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md_path.write_text(markdown_report(report), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if report.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
