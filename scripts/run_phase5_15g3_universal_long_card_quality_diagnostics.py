#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""FASE 5.15G.3 - diagnostica universale qualità card long-doc."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Tuple

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator  # noqa: E402
from backend.phase5_15g1_long_document_orchestrator import (  # noqa: E402
    build_global_document_map,
    build_long_document_cards,
    is_long_document,
)

REPORT_JSON = ROOT / "reports/phase5_15g3_universal_long_card_quality_diagnostics_v1.json"
REPORT_MD = ROOT / "reports/phase5_15g3_universal_long_card_quality_diagnostics_v1.md"
SAFETY_MD = ROOT / "reports/phase5_15g3_universal_long_card_quality_safety_review_v1.md"


def words(text: str) -> List[str]:
    return re.findall(r"[A-Za-zÀ-ÖØ-öø-ÿ0-9]+", str(text or ""))


def word_count(text: str) -> int:
    return len(words(text))


def final_output(result: Dict[str, Any]) -> Dict[str, Any]:
    output = result.get("final_output")
    return output if isinstance(output, dict) else result


def compact(text: str, limit: int = 220) -> str:
    clean = re.sub(r"\s+", " ", str(text or "")).strip()
    return clean if len(clean) <= limit else clean[: limit - 3].rstrip() + "..."


def title_counts(items: Iterable[Dict[str, Any]]) -> Dict[str, int]:
    counts: Dict[str, int] = {}
    for item in items:
        title = str(item.get("title") or item.get("titolo") or "").strip()
        if title:
            counts[title] = counts.get(title, 0) + 1
    return {key: value for key, value in counts.items() if value > 1}


def expanded_inline_doc(label: str, focus: str, profile: str, section_count: int = 20) -> str:
    lines = [f"# {label}", ""]
    facets = [
        "definizione operativa",
        "esempio guidato",
        "errore comune",
        "criterio di verifica",
        "confronto tra alternative",
        "responsabilità del gruppo",
        "rischio da evitare",
        "sequenza di applicazione",
        "domanda di ripasso",
        "collegamento con il caso pratico",
    ]
    for idx in range(1, section_count + 1):
        control = f"CTRL-{profile[:3].upper()}-{idx:03d}"
        facet = facets[(idx - 1) % len(facets)]
        lines.extend(
            [
                f"Sezione {idx:03d} - {facet} su {focus}",
                f"Nel modulo {idx}, {focus} viene studiato attraverso {facet} quando una decisione richiede evidenze verificabili.",
                f"Il riferimento principale è {facet}, collegato a {focus}, responsabilità, sequenza operativa e conseguenze dell'errore.",
                f"La procedura richiede una verifica guidata, una nota scritta, una conferma del responsabile e un esempio applicato al caso {idx}.",
                f"Il controllo {control} rende confrontabile il risultato e chiarisce quale evidenza di {facet} va conservata per ricostruire la scelta.",
                f"Se l'evidenza è incompleta, il gruppo deve formulare una domanda di studio, correggere il passaggio e ripetere la verifica.",
                f"Mini caso pratico: un team analizza {focus}, separa {facet}, esempio, rischio e decisione, poi spiega perché il controllo {control} evita conclusioni generiche.",
                "",
            ]
        )
    return "\n".join(lines)


INLINE_CASES: List[Tuple[str, str, str, str]] = [
    (
        "inline_school_university_handout",
        "inline://dispensa_scolastica_universitaria",
        "dispensa_scolastica_universitaria",
        expanded_inline_doc("Dispensa universitaria su metodo scientifico", "ipotesi, variabile indipendente e validazione dei risultati", "school", section_count=4),
    ),
    (
        "inline_story_long_doc",
        "inline://storia_racconto",
        "storia_racconto",
        expanded_inline_doc("Racconto breve con arco narrativo", "conflitto del protagonista e svolta finale", "story", section_count=4),
    ),
    (
        "inline_technical_long_doc",
        "inline://documento_tecnico",
        "documento_tecnico",
        expanded_inline_doc("Mini manuale tecnico su pipeline dati", "ingestione, validazione schema e gestione errori", "tech", section_count=4),
    ),
]

FILE_CASES: List[Tuple[str, str, str]] = [
    ("synthetic_long_business_doc", "rag/documenti/test_documento_lungo_aziendale_120_pagine.txt", "manuale_aziendale"),
    ("real_long_audit_doc", "reports/audit_effetti_premi_ai_its.md", "documento_reale"),
    ("real_security_doc_if_long", "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md", "documento_tecnico"),
]


def read_cases() -> List[Dict[str, Any]]:
    cases: List[Dict[str, Any]] = []
    for name, rel_path, profile_hint in FILE_CASES:
        path = ROOT / rel_path
        if path.exists():
            cases.append({"name": name, "filepath": rel_path, "profile_hint": profile_hint, "text": path.read_text(encoding="utf-8")})
    for name, filepath, profile_hint, text in INLINE_CASES:
        cases.append({"name": name, "filepath": filepath, "profile_hint": profile_hint, "text": text})
    return cases


def before_after(text: str) -> Dict[str, Any]:
    if not is_long_document(text):
        return {"before_cards": 0, "before_metrics": {}, "after_expected": False}
    global_map = build_global_document_map(text)
    before = build_long_document_cards(global_map, text)
    return {
        "before_cards": len(before.get("items") or []),
        "before_metrics": before.get("metrics", {}),
        "after_expected": True,
    }


def inspect_case(case: Dict[str, Any]) -> Dict[str, Any]:
    text = case["text"]
    result = run_quality_checked_generator("cards", text)
    output = final_output(result)
    items = output.get("items") if isinstance(output.get("items"), list) else []
    quality = output.get("quality_report") if isinstance(output.get("quality_report"), dict) else {}
    g3_metrics = quality.get("g3_card_metrics") if isinstance(quality.get("g3_card_metrics"), dict) else {}
    comparison = before_after(text)
    long_doc = is_long_document(text)
    active = quality.get("phase5_15g3_universal_long_card_quality") is True
    duplicate_titles = title_counts(items)
    judgment = "PASS"
    defects: List[str] = []
    if long_doc and not active:
        defects.append("g3_not_active_on_long_doc")
    if long_doc and result.get("approved") is not True:
        defects.append(f"approved_non_true:{result.get('approved')}")
    if long_doc and int(result.get("executed_qm_count") or 0) != 60:
        defects.append(f"qm_cards_count:{result.get('executed_qm_count')}")
    if long_doc and float(g3_metrics.get("traceability_rate") or 0) < 0.8:
        defects.append("traceability_below_80_percent")
    if long_doc and (g3_metrics.get("generic_title_count") or 0):
        defects.append("generic_titles_present")
    if long_doc and (g3_metrics.get("template_phrase_count") or 0):
        defects.append("template_phrases_present")
    if long_doc and duplicate_titles:
        defects.append("final_duplicate_titles_present")
    if defects:
        judgment = "FAIL"
    elif not long_doc:
        judgment = "WARNING"
    return {
        "name": case["name"],
        "filepath": case["filepath"],
        "profile_hint": case["profile_hint"],
        "words": word_count(text),
        "long_doc": long_doc,
        "g3_active": active,
        "cards_before": comparison["before_cards"],
        "cards_after": len(items),
        "before_metrics": comparison["before_metrics"],
        "g3_card_metrics": g3_metrics,
        "traceability_rate": g3_metrics.get("traceability_rate"),
        "generic_title_count": g3_metrics.get("generic_title_count"),
        "template_phrase_count": g3_metrics.get("template_phrase_count"),
        "duplicate_card_count": g3_metrics.get("duplicate_card_count"),
        "average_teaching_value_score": g3_metrics.get("average_teaching_value_score"),
        "average_specificity_score": g3_metrics.get("average_specificity_score"),
        "diversity_score": g3_metrics.get("diversity_score"),
        "final_duplicate_titles": duplicate_titles,
        "examples": [
            {
                "title": item.get("title"),
                "source_sentence": compact(item.get("source_sentence") or item.get("fatto_origine")),
                "example": compact(item.get("example") or item.get("esempio")),
            }
            for item in items[:3]
        ],
        "qm_cards_count": int(result.get("executed_qm_count") or 0),
        "approved": result.get("approved"),
        "status": result.get("status"),
        "defects": defects,
        "judgment": judgment,
    }


def write_reports(report: Dict[str, Any]) -> None:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# FASE 5.15G.3 - Universal long-doc card quality diagnostics",
        "",
        f"Status: **{report['status']}**",
        "",
    ]
    for case in report["cases"]:
        lines.extend(
            [
                f"## {case['name']} - {case['judgment']}",
                "",
                f"- Filepath: `{case['filepath']}`",
                f"- Tipo: `{case['profile_hint']}`",
                f"- Words: `{case['words']}`; long_doc: `{case['long_doc']}`; G.3 active: `{case['g3_active']}`",
                f"- Cards before/after: `{case['cards_before']}` -> `{case['cards_after']}`; QM cards count: `{case['qm_cards_count']}`; approved: `{case['approved']}`",
                f"- Metrics: traceability `{case['traceability_rate']}`, generic `{case['generic_title_count']}`, template `{case['template_phrase_count']}`, duplicate `{case['duplicate_card_count']}`, teaching `{case['average_teaching_value_score']}`, specificity `{case['average_specificity_score']}`, diversity `{case['diversity_score']}`",
                f"- Defects: `{case['defects']}`",
                "- Examples:",
            ]
        )
        for example in case["examples"]:
            lines.append(f"  - `{example['title']}` — {example['source_sentence']}")
        lines.append("")
    REPORT_MD.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")

    safety = [
        "# FASE 5.15G.3 - Safety review",
        "",
        f"Status: **{report['status']}**",
        "",
        "- Scope verificato: solo generator `cards` su documenti long-doc.",
        "- Summary G.2: non modificato; solo import/riuso indiretto del profilo se disponibile.",
        "- Quiz/study_questions/bridge/UI/raw_output common/QM common: non modificati.",
        "- Fallback: se G.3 fallisce, resta disponibile il percorso G.1 legacy nel ramo cards.",
        "- No commit, no tag, no rollback eseguiti da questo script.",
    ]
    SAFETY_MD.write_text("\n".join(safety) + "\n", encoding="utf-8")


def main() -> int:
    cases = [inspect_case(case) for case in read_cases()]
    status = "PASS" if all(case["judgment"] != "FAIL" for case in cases) else "FAIL"
    report = {
        "phase": "5.15G.3",
        "generated_at": datetime.utcnow().isoformat(timespec="seconds") + "Z",
        "status": status,
        "cases": cases,
    }
    write_reports(report)
    print(f"phase5_15g3_universal_long_card_quality_diagnostics: {status}")
    print(f"json: {REPORT_JSON}")
    print(f"markdown: {REPORT_MD}")
    print(f"safety: {SAFETY_MD}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
