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

from backend.phase5_quality_registry_bridge_v512f1 import (  # noqa: E402
    READY_LABEL,
    build_registry_bridge,
    registry_bridge_to_dict,
)


PHASE = "5.12F.1"
OUT_JSON = REPORTS_DIR / "phase5_12f1_quality_registry_59_connected_v1.json"
OUT_MD = REPORTS_DIR / "phase5_12f1_quality_registry_59_connected_v1.md"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def write_reports(report: Dict[str, Any]) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.12F.1 — Registry 59 motori collegati")
    lines.append("")
    lines.append(f"- Status: **{report['status']}**")
    lines.append(f"- Approved: `{report['approved']}`")
    lines.append(f"- Ready label: `{report['ready_label']}`")
    lines.append(f"- Generated at: `{report['generated_at']}`")
    lines.append("")
    lines.append("## Sintesi")
    lines.append("")
    lines.append(f"- Motori precedenti pronti e collegati: `{report['previous_ready_connected_motors']}`")
    lines.append(f"- Nuovi motori linguistici avanzati collegati: `{report['new_advanced_language_repair_motors']}`")
    lines.append(f"- Totale motori pronti e collegati: `{report['total_ready_connected_motors']}`")
    lines.append("")
    lines.append("## Stato controlli atomici")
    lines.append("")
    for k, v in report["remaining_atomic_controls"].items():
        lines.append(f"- {k}: `{v}`")
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
        "Questa fase collega i 4 motori linguistici avanzati 5.12F al registry. "
        "Non modifica i 55 motori precedenti, non cambia la pipeline 5.11 e non tocca UI/PDF/CSS/app."
    )
    lines.append("")

    OUT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    result = build_registry_bridge()
    report = registry_bridge_to_dict(result)
    report["generated_at"] = now_iso()
    report["report_files"] = {
        "json": str(OUT_JSON.relative_to(ROOT)),
        "markdown": str(OUT_MD.relative_to(ROOT)),
    }

    write_reports(report)

    if report["approved"]:
        print(f"PASS - Fase {PHASE}: {READY_LABEL}")
        print(f"Motori precedenti pronti e collegati: {report['previous_ready_connected_motors']}")
        print(f"Motori linguistici avanzati collegati: {report['new_advanced_language_repair_motors']}")
        print(f"Totale motori pronti e collegati: {report['total_ready_connected_motors']}")
        print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
        print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
        return 0

    print(f"FAIL - Fase {PHASE}: registry bridge not approved")
    print("Defects:", report["defects"])
    print(f"Report JSON: {OUT_JSON.relative_to(ROOT)}")
    print(f"Report MD:   {OUT_MD.relative_to(ROOT)}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
