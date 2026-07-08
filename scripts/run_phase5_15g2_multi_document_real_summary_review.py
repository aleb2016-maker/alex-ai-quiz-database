#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.2 - diagnostica multi-documento reale summary G.2."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator  # noqa: E402
from backend.phase5_15g1_long_document_orchestrator import build_global_document_map, is_long_document  # noqa: E402
from backend.phase5_15g2_universal_long_summary_smoothing import (  # noqa: E402
    detect_document_profile,
    validate_universal_summary_quality,
)

REPORT_JSON = ROOT / "reports/phase5_15g2_multi_document_real_summary_review_v1.json"
REPORT_MD = ROOT / "reports/phase5_15g2_multi_document_real_summary_review_v1.md"

CHECKPOINT = {
    "branch": "rag-concept-app-presentabile-v3",
    "commit": "291c6c9 Aggiunge smoothing summary long-doc Fase 5.15G.2",
    "tag": "checkpoint-mini-llm-long-summary-smoothing-v515g2",
    "initial_state": "working tree clean, branch up to date with origin",
}

DOCUMENT_CANDIDATES: List[Tuple[str, str, str]] = [
    ("long_real_audit_report", "reports/audit_effetti_premi_ai_its.md", "Documento lungo reale di audit effetti/premi presente nei report."),
    ("medium_security_training_doc", "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md", "Documento medio formativo cyber-security in rag/documenti."),
    ("different_domain_ai_rag_doc", "rag/documenti/documento_ai_generativa_test_rag.md", "Documento di dominio diverso: AI generativa e RAG."),
    ("short_business_training_doc", "rag/documenti/esempio_documento_aziendale_formazione.md", "Documento breve aziendale/formazione: controllo non-long."),
    ("synthetic_long_stress_reference", "rag/documenti/test_documento_lungo_aziendale_120_pagine.txt", "Stress test lungo gia usato: sintetico, non unico documento della review."),
]

SYSTEM_NOISE = ["non contiene dati reali", "collegato alla demo", "demo", "fallback", "script", "test tecnico", "documento fixture", "fixture tecnica"]
TEMPLATE_PATTERNS = [r"\bla procedura richiede\b", r"\bogni attivit[aà] deve\b", r"\bnel contesto\b", r"\bla sezione\b", r"\bquesto passaggio\b", r"\bevita passaggi informali\b", r"\bmacro-area\b"]
GENERIC_PATTERNS = ["aspetto importante", "contenuto del documento", "passaggio operativo generico", "il documento parla di", "in generale il documento"]
TECHNICAL_TITLE_PATTERNS = [r"riferimento sezione", r"\bMAN-[A-Z]+-\d+", r"\bCTRL[-_ ]?\d+", r"\bmacro-area\b", r"^sezione\s+\d+$"]


def word_tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def word_count(text: str) -> int:
    return len(word_tokens(text))


def split_sentences(text: str) -> List[str]:
    parts = re.split(r"(?<=[.!?])\s+|\n+", str(text or ""))
    return [re.sub(r"\s+", " ", part).strip() for part in parts if word_count(part) >= 6]


def count_phrases(text: str, phrases: Iterable[str]) -> Dict[str, int]:
    low = str(text or "").lower()
    return {phrase: low.count(phrase) for phrase in phrases if low.count(phrase)}


def count_patterns(text: str, patterns: Iterable[str]) -> Dict[str, int]:
    low = str(text or "").lower()
    out: Dict[str, int] = {}
    for pattern in patterns:
        count = len(re.findall(pattern, low, flags=re.I))
        if count:
            out[pattern] = count
    return out


def repeated_sentence_patterns(text: str) -> Dict[str, int]:
    starts = []
    for sentence in split_sentences(text):
        tokens = word_tokens(sentence.lower())
        if len(tokens) >= 7:
            starts.append(" ".join(tokens[:3]))
    return {key: value for key, value in Counter(starts).most_common(16) if value > 1}


def extract_sections(summary: str) -> List[str]:
    sections = []
    for line in str(summary or "").splitlines():
        clean = re.sub(r"\s+", " ", line.strip())
        if clean and len(clean) <= 120 and not clean.endswith(".") and word_count(clean) <= 10:
            sections.append(clean)
    return sections[:40]


def technical_titles(sections: Iterable[str]) -> List[str]:
    bad = []
    for title in sections:
        low = title.lower()
        if any(re.search(pattern, low, flags=re.I) for pattern in TECHNICAL_TITLE_PATTERNS):
            bad.append(title)
    return bad


def first_sentence_starts(summary: str, limit: int = 5) -> List[str]:
    out = []
    for sentence in split_sentences(summary):
        out.append(" ".join(word_tokens(sentence)[:12]))
        if len(out) >= limit:
            break
    return out


def final_output(result: Dict[str, Any]) -> Dict[str, Any]:
    if isinstance(result.get("final_output"), dict):
        return result["final_output"]
    if isinstance(result.get("raw_output"), dict):
        return result["raw_output"]
    return result


def summary_text(output: Dict[str, Any]) -> str:
    return str(output.get("content") or output.get("summary_text") or output.get("summary") or output.get("text") or "")


def safe_profile(text: str, output: Dict[str, Any]) -> Dict[str, Any]:
    report = output.get("quality_report") if isinstance(output.get("quality_report"), dict) else {}
    profile = report.get("document_profile") if isinstance(report.get("document_profile"), dict) else None
    if profile:
        return profile
    try:
        return detect_document_profile(build_global_document_map(text), text[:14000])
    except Exception as exc:
        return {"tipo_testo": "profile_error", "confidence": 0.0, "error": str(exc)}


def judge(case: Dict[str, Any]) -> Tuple[str, List[str]]:
    defects: List[str] = []
    warnings: List[str] = []
    if not case["summary_words"]:
        defects.append("summary_empty")
    if not case["approved"]:
        defects.append("not_approved")
    if int(case["qm_count"] or 0) != 55:
        defects.append("qm_summary_count_not_55")
    if case["system_noise_total"] > 0:
        defects.append("system_noise_present")
    if case["placeholder_demo_fallback_total"] > 0:
        defects.append("placeholder_demo_fallback_present")
    if case["template_phrase_total"] > 0:
        defects.append("template_phrases_present")
    if case["technical_titles_count"] > 0:
        defects.append("technical_titles_present")
    if case["generic_phrase_total"] > 2:
        warnings.append("generic_phrases_present")
    if case["repeated_pattern_total"] > 8:
        warnings.append("repeated_patterns_high")
    if case["long_doc"]:
        if case["g2_runtime_flag"] is not True:
            defects.append("g2_not_active_on_long_doc")
        if case["target_10_percent_reached"] is not True:
            defects.append("target_10_percent_not_reached")
        if case["summary_words"] < 300:
            defects.append("long_summary_too_short")
    else:
        if case["g2_runtime_flag"] is True:
            defects.append("g2_active_on_non_long_doc")
        if case["summary_words"] < 30:
            warnings.append("non_long_summary_very_short")
    if defects:
        return "FAIL", defects + warnings
    if warnings:
        return "WARNING", warnings
    return "PASS", []


def analyze(label: str, rel_path: str, note: str) -> Dict[str, Any]:
    path = ROOT / rel_path
    text = path.read_text(encoding="utf-8", errors="replace")
    input_words = word_count(text)
    input_chars = len(text)
    long_doc = is_long_document(text)
    result = run_quality_checked_generator("summary", text)
    output = final_output(result)
    summary = summary_text(output)
    quality_report = output.get("quality_report") if isinstance(output.get("quality_report"), dict) else {}
    profile = safe_profile(text, output)
    sections = extract_sections(summary)
    bad_titles = technical_titles(sections)
    noise = count_phrases(summary, SYSTEM_NOISE)
    templates = count_patterns(summary, TEMPLATE_PATTERNS)
    generic = count_phrases(summary, GENERIC_PATTERNS)
    repeated = repeated_sentence_patterns(summary)
    summary_words = word_count(summary)
    target_words = int(input_words * 0.10) if long_doc else None
    placeholder_demo_fallback = {key: value for key, value in noise.items() if key in {"demo", "fallback", "documento fixture", "test tecnico"}}
    case = {
        "label": label,
        "path": str(path),
        "relative_path": rel_path,
        "note": note,
        "input_chars": input_chars,
        "input_words": input_words,
        "long_doc": long_doc,
        "document_profile": profile,
        "summary_words": summary_words,
        "summary_ratio": round(summary_words / max(1, input_words), 3),
        "target_words_10_percent": target_words,
        "target_10_percent_reached": (summary_words >= target_words) if target_words else None,
        "g2_runtime_flag": quality_report.get("phase5_15g2_universal_summary_smoothing"),
        "approved": bool(result.get("approved")),
        "status": result.get("status"),
        "qm_count": int(result.get("executed_qm_count") or quality_report.get("quality_controls") or 0),
        "expected_qm_count": int(result.get("expected_qm_count") or quality_report.get("route_total") or 0),
        "system_noise": noise,
        "system_noise_total": sum(noise.values()),
        "template_phrases": templates,
        "template_phrase_total": sum(templates.values()),
        "repeated_patterns": repeated,
        "repeated_pattern_total": sum(value - 1 for value in repeated.values()),
        "technical_titles": bad_titles,
        "technical_titles_count": len(bad_titles),
        "adaptive_titles_good": bool(sections) and not bad_titles,
        "adaptive_titles_bad": bool(bad_titles),
        "sections": sections,
        "section_count": len(sections),
        "generic_phrases": generic,
        "generic_phrase_total": sum(generic.values()),
        "placeholder_demo_fallback": placeholder_demo_fallback,
        "placeholder_demo_fallback_total": sum(placeholder_demo_fallback.values()),
        "sample_titles": sections[:5],
        "sample_sentence_starts": first_sentence_starts(summary, 5),
        "g2_validation": validate_universal_summary_quality(summary, profile) if long_doc else {},
        "summary_excerpt": summary[:1600],
    }
    case["judgment"], case["defects"] = judge(case)
    return case


def available_documents() -> List[Tuple[str, str, str]]:
    selected = [item for item in DOCUMENT_CANDIDATES if (ROOT / item[1]).exists()]
    if len(selected) >= 3:
        return selected
    seen = {item[1] for item in selected}
    for base in [ROOT / "rag/documenti", ROOT / "docs", ROOT / "reports"]:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.suffix.lower() not in {".txt", ".md", ".json"}:
                continue
            rel = str(path.relative_to(ROOT))
            if rel in seen:
                continue
            try:
                if word_count(path.read_text(encoding="utf-8", errors="replace")) < 250:
                    continue
            except Exception:
                continue
            selected.append((f"auto_{len(selected)+1}", rel, "Auto-selected fallback document."))
            seen.add(rel)
            if len(selected) >= 3:
                return selected
    return selected


def global_status(cases: List[Dict[str, Any]]) -> Tuple[str, List[str]]:
    defects: List[str] = []
    warnings: List[str] = []
    if len(cases) < 3:
        defects.append("less_than_3_documents_analyzed")
    if not any(case["long_doc"] for case in cases):
        defects.append("no_long_document_analyzed")
    if not any(not case["long_doc"] for case in cases):
        warnings.append("no_medium_or_short_non_long_document_analyzed")
    severe_fails = [case["label"] for case in cases if case["judgment"] == "FAIL" and "synthetic_long_stress" not in case["label"]]
    if severe_fails:
        defects.append("fail_on_real_documents: " + ", ".join(severe_fails))
    warning_docs = [case["label"] for case in cases if case["judgment"] == "WARNING"]
    if warning_docs:
        warnings.append("warning_documents: " + ", ".join(warning_docs))
    if defects:
        return "FAIL", defects + warnings
    if warnings:
        return "WARNING", warnings
    return "PASS", []


def build_markdown(payload: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# FASE 5.15G.2 - Multi-document real summary review\n")
    lines.append("## 1. Obiettivo fase")
    lines.append("Review diagnostica multi-documento del solo ramo `summary` long-doc G.2, senza modificare card, quiz, study_questions, bridge, raw_output comune o Quality Manager comune.\n")
    lines.append("## 2. Checkpoint di partenza")
    for key, value in payload["checkpoint"].items():
        lines.append(f"- {key}: `{value}`")
    lines.append("\n## 3. Documenti analizzati")
    for case in payload["documents"]:
        lines.append(f"- `{case['relative_path']}` - {case['note']}")
    lines.append("\n## 4. Tabella risultati per documento")
    lines.append("| Documento | Long-doc | Profilo | Input parole | Summary parole | Ratio | Target 10% | G.2 runtime | QM | Rumore | Template | Ripetizioni | Titoli tecnici | Esito |")
    lines.append("| --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for case in payload["documents"]:
        profile = case.get("document_profile") or {}
        row = [
            f"`{case['label']}`", str(case["long_doc"]), str(profile.get("tipo_testo", "")), str(case["input_words"]),
            str(case["summary_words"]), str(case["summary_ratio"]), str(case["target_10_percent_reached"]),
            str(case["g2_runtime_flag"]), str(case["qm_count"]), str(case["system_noise_total"]),
            str(case["template_phrase_total"]), str(case["repeated_pattern_total"]), str(case["technical_titles_count"]), case["judgment"],
        ]
        lines.append("| " + " | ".join(row) + " |")
    lines.append("\n## 5. Confronto sintetico con G.2 precedente")
    lines.append("La fase precedente aveva validato G.2 soprattutto sullo stress test lungo aziendale sintetico. Questa review estende il controllo a documenti reali/operativi presenti nel repository, includendo almeno un long-doc, documenti medi/non-long e un dominio diverso.\n")
    lines.append("## 6. Difetti trovati")
    any_defect = False
    for case in payload["documents"]:
        if case["defects"]:
            any_defect = True
            lines.append(f"- `{case['label']}`: {', '.join(case['defects'])}")
    if not any_defect:
        lines.append("- Nessun difetto bloccante rilevato nei documenti analizzati.")
    lines.append("\n## 7. Eventuali correzioni fatte")
    lines.append("- Nessuna correzione runtime applicata da questa diagnostica. Sono stati creati solo script/report diagnostici.\n")
    lines.append("## 8. Verifiche finali")
    for item in payload.get("verification_notes", []):
        lines.append(f"- {item}")
    lines.append("\n## 9. Esito finale")
    lines.append(f"**{payload['global_status']}**")
    for issue in payload.get("global_issues", []):
        lines.append(f"- {issue}")
    lines.append("\n## 10. Prossimo step consigliato")
    lines.append("Passare alla review qualita card solo se la WARNING, se presente, e' considerata non bloccante." if payload["global_status"] in {"PASS", "WARNING"} else "Non passare alle card: correggere prima i FAIL summary G.2.")
    lines.append("\n## Dettagli per documento")
    for case in payload["documents"]:
        lines.append(f"### {case['label']}")
        lines.append(f"- Path: `{case['relative_path']}`")
        lines.append(f"- Sezioni: {case['section_count']} -> {', '.join(case['sections'][:10])}")
        lines.append(f"- Sample titoli: {', '.join(case['sample_titles'])}")
        lines.append(f"- Prime frasi: {json.dumps(case['sample_sentence_starts'], ensure_ascii=False)}")
        lines.append(f"- Difetti: {', '.join(case['defects']) if case['defects'] else 'nessuno'}\n")
    return "\n".join(lines) + "\n"


def main() -> int:
    cases = [analyze(label, rel_path, note) for label, rel_path, note in available_documents()]
    status, issues = global_status(cases)
    payload = {
        "phase": "5.15G.2",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "checkpoint": CHECKPOINT,
        "scope": "summary_long_doc_g2_multi_document_review_only",
        "documents_count": len(cases),
        "global_status": status,
        "global_issues": issues,
        "documents": cases,
        "verification_notes": [
            "Script diagnostico multi-documento eseguito.",
            "Le diagnostiche py_compile, G.2 universale e G.1 regressiva vanno eseguite dopo questo script come da prompt.",
        ],
    }
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    REPORT_MD.write_text(build_markdown(payload), encoding="utf-8")
    print(f"FASE 5.15G.2 multi-document review: status={status}")
    for case in cases:
        print(f"- {case['label']}: {case['judgment']} long={case['long_doc']} words={case['input_words']} summary={case['summary_words']} g2={case['g2_runtime_flag']} qm={case['qm_count']} noise={case['system_noise_total']} template={case['template_phrase_total']}")
    print(f"report_json={REPORT_JSON}")
    print(f"report_md={REPORT_MD}")
    return 0 if status in {"PASS", "WARNING"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
