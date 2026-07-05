#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = ROOT / "reports"

sys.path.insert(0, str(ROOT))

from backend.phase5_section_quality_matrix_v512g2 import (  # noqa: E402
    READY_LABEL,
    build_section_matrix,
    section_matrix_to_dict,
)


PHASE = "5.12G.2"
OUT_JSON = REPORTS_DIR / "phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12g2_section_quality_selection_matrix_with_contextual_duplicates_v1.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_reports(report: Dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.12G.2 — Section Quality Matrix con duplicati contestuali")
    lines.append("")
    lines.append(f"- Status: **{report['status']}**")
    lines.append(f"- Approved: `{report['approved']}`")
    lines.append(f"- Ready label: `{report['ready_label']}`")
    lines.append(f"- Generated at: `{report['generated_at']}`")
    lines.append(f"- Registry totale motori: `{report['registry_total_motors']}`")
    lines.append("")
    lines.append("## Gruppi rilevati")
    lines.append("")
    for key, value in report["detected_groups"].items():
        if key.endswith("_ids"):
            continue
        lines.append(f"- {key}: `{value}`")
    lines.append("")
    lines.append("## Sezioni")
    lines.append("")
    for name, section in report["sections"].items():
        lines.append(f"### `{name}`")
        lines.append("")
        lines.append(section["description"])
        lines.append("")
        lines.append(f"- Motori attivi: `{len(section['active_motor_ids'])}`")
        lines.append(f"- Conteggio atteso: `{section['expected_active_count']}`")
        lines.append("")
        for mid in section["active_motor_ids"]:
            lines.append(f"- `{mid}`")
        lines.append("")
    lines.append("## Defects")
    lines.append("")
    if report["defects"]:
        for d in report["defects"]:
            lines.append(f"- `{d}`")
    else:
        lines.append("- Nessun defect.")
    lines.append("")
    lines.append("## Warnings")
    lines.append("")
    if report["warnings"]:
        for w in report["warnings"]:
            lines.append(f"- `{w}`")
    else:
        lines.append("- Nessun warning.")
    lines.append("")
    lines.append("## Scope guard")
    lines.append("")
    for k, v in report["scope_guard"].items():
        lines.append(f"- {k}: `{v}`")
    lines.append("")
    lines.append("## Nota tecnica")
    lines.append("")
    lines.append(
        "Questa matrice aggiorna solo la selezione logica dei motori. "
        "I duplicati contestuali comuni vanno su tutte le sezioni testuali; "
        "qm_048 va solo su Domande studio e Test/Quiz."
    )
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    result = build_section_matrix()
    report = section_matrix_to_dict(result)
    report["generated_at"] = now_iso()
    report["report_files"] = {
        "json": str(OUT_JSON.relative_to(ROOT)),
        "markdown": str(OUT_MD.relative_to(ROOT)),
    }

    write_reports(report)

    if report["approved"]:
        print(f"PASS - Fase {PHASE}: {READY_LABEL}")
        print(f"Registry motori: {report['registry_total_motors']}")
        print(f"Foundation motors: {report['detected_groups']['foundation_count']}")
        print(f"Textual universal motors: {report['detected_groups']['textual_universal_count']}")
        print(f"Didactic universal motors: {report['detected_groups']['didactic_universal_count']}")
        print(f"Card/Summary/Source motors: {report['detected_groups']['card_summary_source_specific_count']}")
        print(f"Test/Quiz specific motors: {report['detected_groups']['test_quiz_specific_count']}")
        print(f"Advanced language motors: {report['detected_groups']['advanced_language_universal_count']}")
        print(f"Contextual duplicate motors: {report['detected_groups']['contextual_duplicate_universal_count']}")
        print(f"Card motors: {len(report['sections']['card']['active_motor_ids'])}")
        print(f"Summary motors: {len(report['sections']['summary']['active_motor_ids'])}")
        print(f"Study motors: {len(report['sections']['study_questions']['active_motor_ids'])}")
        print(f"Test motors: {len(report['sections']['test_quiz']['active_motor_ids'])}")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: section matrix with contextual duplicates not approved")
    print("Defects:", report["defects"])
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
