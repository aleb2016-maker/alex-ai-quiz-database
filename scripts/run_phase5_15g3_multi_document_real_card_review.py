#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.3 - review reale multi-documento delle card long-doc."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator  # noqa: E402
from backend.phase5_15g1_long_document_orchestrator import (  # noqa: E402
    build_global_document_map,
    build_long_document_cards,
    is_long_document,
)

REPORT_JSON = ROOT / "reports/phase5_15g3_multi_document_real_card_review_v1.json"
REPORT_MD = ROOT / "reports/phase5_15g3_multi_document_real_card_review_v1.md"

REAL_DOCUMENTS: List[Tuple[str, str, str]] = [
    ("audit_effetti_premi_ai_its", "reports/audit_effetti_premi_ai_its.md", "report reale lungo"),
    ("sicurezza_informatica_aziendale", "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md", "documento cyber-security"),
    ("ai_generativa_rag", "rag/documenti/documento_ai_generativa_test_rag.md", "documento AI/RAG"),
    ("formazione_aziendale", "rag/documenti/esempio_documento_aziendale_formazione.md", "documento formazione"),
]


def word_count(text: str) -> int:
    return len(re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or "")))


def compact(text: str, limit: int = 220) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    return clean if len(clean) <= limit else clean[: limit - 3].rstrip() + "..."


def final_output(result: Dict[str, Any]) -> Dict[str, Any]:
    output = result.get("final_output")
    return output if isinstance(output, dict) else result


def duplicate_titles(items: List[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        title = str(item.get("title") or item.get("titolo") or "").strip()
        if title:
            counts[title] = counts.get(title, 0) + 1
    return {title: count for title, count in counts.items() if count > 1}


def before_metrics(text: str) -> Dict[str, Any]:
    if not is_long_document(text):
        return {"cards_count": 0, "metrics": {}}
    global_map = build_global_document_map(text)
    before = build_long_document_cards(global_map, text)
    return {"cards_count": len(before.get("items") or []), "metrics": before.get("metrics", {})}


def inspect_document(name: str, rel_path: str, doc_type: str) -> Dict[str, Any] | None:
    path = ROOT / rel_path
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8")
    long_doc = is_long_document(text)
    before = before_metrics(text)
    result = run_quality_checked_generator("cards", text)
    output = final_output(result)
    items = output.get("items") if isinstance(output.get("items"), list) else []
    quality = output.get("quality_report") if isinstance(output.get("quality_report"), dict) else {}
    metrics = quality.get("g3_card_metrics") if isinstance(quality.get("g3_card_metrics"), dict) else {}
    g3_active = quality.get("phase5_15g3_universal_long_card_quality") is True
    final_dupes = duplicate_titles(items)
    defects: List[str] = []
    if long_doc:
        if not g3_active:
            defects.append("g3_not_active")
        if result.get("approved") is not True:
            defects.append(f"approved_non_true:{result.get('approved')}")
        if int(result.get("executed_qm_count") or 0) != 60:
            defects.append(f"qm_cards_count:{result.get('executed_qm_count')}")
        if float(metrics.get("traceability_rate") or 0) < 0.8:
            defects.append("traceability_below_80_percent")
        if metrics.get("generic_title_count") or metrics.get("template_phrase_count") or metrics.get("duplicate_card_count"):
            defects.append("g3_quality_metric_non_zero")
        if final_dupes:
            defects.append("final_duplicate_titles")
    judgment = "FAIL" if defects else ("PASS" if long_doc else "WARNING")
    return {
        "name": name,
        "filepath": rel_path,
        "type": doc_type,
        "words": word_count(text),
        "long_doc": long_doc,
        "g3_active": g3_active,
        "cards_before": before["cards_count"],
        "cards_after": len(items),
        "before_metrics": before["metrics"],
        "g3_card_metrics": metrics,
        "traceability_rate": metrics.get("traceability_rate"),
        "generic_title_count": metrics.get("generic_title_count"),
        "template_phrase_count": metrics.get("template_phrase_count"),
        "duplicate_card_count": metrics.get("duplicate_card_count"),
        "average_teaching_value_score": metrics.get("average_teaching_value_score"),
        "average_specificity_score": metrics.get("average_specificity_score"),
        "diversity_score": metrics.get("diversity_score"),
        "qm_cards_count": int(result.get("executed_qm_count") or 0),
        "approved": result.get("approved"),
        "status": result.get("status"),
        "final_duplicate_titles": final_dupes,
        "examples": [
            {
                "title": item.get("title"),
                "source_sentence": compact(item.get("source_sentence") or item.get("fatto_origine")),
                "example": compact(item.get("example") or item.get("esempio")),
            }
            for item in items[:4]
        ],
        "defects": defects,
        "judgment": judgment,
    }


def write_reports(report: Dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# FASE 5.15G.3 - Multi-document real card review",
        "",
        f"Status: **{report['status']}**",
        f"Long real PASS count: `{report['long_real_pass_count']}`",
        "",
    ]
    for case in report["documents"]:
        lines.extend(
            [
                f"## {case['name']} - {case['judgment']}",
                "",
                f"- Filepath: `{case['filepath']}`",
                f"- Type: `{case['type']}`; words: `{case['words']}`; long_doc: `{case['long_doc']}`; G.3 active: `{case['g3_active']}`",
                f"- Cards before/after: `{case['cards_before']}` -> `{case['cards_after']}`; approved: `{case['approved']}`; QM cards: `{case['qm_cards_count']}`",
                f"- Metrics: traceability `{case['traceability_rate']}`, generic `{case['generic_title_count']}`, template `{case['template_phrase_count']}`, duplicate `{case['duplicate_card_count']}`, teaching `{case['average_teaching_value_score']}`, specificity `{case['average_specificity_score']}`, diversity `{case['diversity_score']}`",
                f"- Defects: `{case['defects']}`",
                "- Examples:",
            ]
        )
        for example in case["examples"]:
            lines.append(f"  - `{example['title']}` — {example['source_sentence']}")
        lines.append("")
    REPORT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main() -> int:
    documents = []
    for name, rel_path, doc_type in REAL_DOCUMENTS:
        inspected = inspect_document(name, rel_path, doc_type)
        if inspected:
            documents.append(inspected)
    long_real_pass_count = sum(1 for item in documents if item["long_doc"] and item["judgment"] == "PASS")
    fail_count = sum(1 for item in documents if item["judgment"] == "FAIL")
    status = "PASS" if long_real_pass_count >= 1 and fail_count == 0 else "FAIL"
    report = {
        "phase": "5.15G.3",
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "status": status,
        "long_real_pass_count": long_real_pass_count,
        "documents": documents,
    }
    write_reports(report)
    print(f"phase5_15g3_multi_document_real_card_review: {status}")
    print(f"json: {REPORT_JSON}")
    print(f"markdown: {REPORT_MD}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
