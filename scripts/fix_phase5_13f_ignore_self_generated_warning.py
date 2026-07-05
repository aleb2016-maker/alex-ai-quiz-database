#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13F.1 — IGNORA WARNING SELF-GENERATED REPORT

Problema:
- il report 5.13F è PASS;
- però segnala warning perché vede i propri file appena generati come untracked.

Fix:
- se il working tree contiene solo i file 5.13F appena generati,
  non produce warning;
- se invece ci sono altri file sporchi, il warning resta.

Non modifica motori, UI, PDF o app.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase5_13f_final_presentable_pipeline_report.py"

text = SCRIPT.read_text(encoding="utf-8")

old = '''    if git.status_short:
        warnings.append(
            "Working tree non pulito al momento della generazione del report. "
            "È normale se il report appena generato non è ancora committato."
        )
'''

new = '''    if git.status_short:
        allowed_self_generated = {
            "scripts/run_phase5_13f_final_presentable_pipeline_report.py",
            "scripts/fix_phase5_13f_ignore_self_generated_warning.py",
            "reports/phase5_13f_final_presentable_pipeline_report_v1.json",
            "reports/phase5_13f_final_presentable_pipeline_report_v1.md",
        }

        unexpected_dirty_lines = []

        for raw_line in git.status_short.splitlines():
            path = raw_line[3:].strip()
            if " -> " in path:
                path = path.split(" -> ", 1)[1].strip()

            if path not in allowed_self_generated:
                unexpected_dirty_lines.append(raw_line)

        if unexpected_dirty_lines:
            warnings.append(
                "Working tree non pulito con file non previsti: "
                + "; ".join(unexpected_dirty_lines)
            )
'''

if old not in text:
    raise SystemExit("FAIL - blocco warning working tree non trovato nel report 5.13F")

text = text.replace(old, new, 1)

SCRIPT.write_text(text, encoding="utf-8")

print("PASS - Fase 5.13F.1: warning self-generated ignorato correttamente")
