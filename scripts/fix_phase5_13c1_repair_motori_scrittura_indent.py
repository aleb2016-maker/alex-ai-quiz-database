#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "backend" / "motori_scrittura.py"

text = TARGET.read_text(encoding="utf-8")

# 1) Rimuove i blocchi 5.13C.1 inseriti male.
#    Il problema precedente nasceva perché il blocco è stato inserito prima della parola
#    "result" ma dopo gli spazi iniziali della riga, lasciando poi result.quality_report
#    senza indentazione corretta.

patterns = [
    r'\n[ \t]*# FASE 5\.13C\.1 — STUDY QUESTIONS 51 REAL CONNECTOR(?: LOCAL SCOPE)?\n'
    r'[ \t]*from backend\.phase5_study_questions_real_connector_v513c1 import \(\n'
    r'[ \t]*build_study_questions_real_connection_report,\n'
    r'[ \t]*\)\n\n'
    r'[ \t]*study_questions_real_connection_v513c1 = build_study_questions_real_connection_report\(\n'
    r'[ \t]*result\.domande_studio,\n'
    r'[ \t]*result\.errors,\n'
    r'[ \t]*\)\n\n',

    r'\n[ \t]*# FASE 5\.13C\.1 — STUDY QUESTIONS 51 REAL CONNECTOR(?: LOCAL SCOPE)?\n'
    r'[ \t]*from backend\.phase5_study_questions_real_connector_v513c1 import \(\n'
    r'[ \t]*build_study_questions_real_connection_report,\n'
    r'[ \t]*\)\n\n',
]

for pattern in patterns:
    text = re.sub(pattern, "\n", text, flags=re.MULTILINE)

# 2) Rimuove eventuale campo duplicato già inserito nel quality_report.
text = re.sub(
    r'\n[ \t]*"study_questions_real_connection_v513c1": study_questions_real_connection_v513c1,\n',
    "\n",
    text,
)

# 3) Se result.quality_report è rimasto senza indentazione, lo corregge.
#    Dentro build_phase5_quality_study_quiz deve stare a 8 spazi.
text = re.sub(
    r'\nresult\.quality_report = \{',
    '\n        result.quality_report = {',
    text,
)

lines = text.splitlines(keepends=True)

# 4) Trova la funzione reale.
start = None
for i, line in enumerate(lines):
    if line.startswith("def build_phase5_quality_study_quiz"):
        start = i
        break

if start is None:
    raise SystemExit("FAIL - funzione build_phase5_quality_study_quiz non trovata")

end = len(lines)
for i in range(start + 1, len(lines)):
    if lines[i].startswith("def ") or lines[i].startswith("class "):
        end = i
        break

# 5) Trova il quality_report dentro quella funzione.
quality_idx = None
for i in range(start, end):
    if re.match(r'^\s*result\.quality_report = \{', lines[i]):
        quality_idx = i
        break

if quality_idx is None:
    raise SystemExit("FAIL - result.quality_report non trovato dentro build_phase5_quality_study_quiz")

quality_indent = re.match(r'^(\s*)', lines[quality_idx]).group(1)

if len(quality_indent) == 0:
    quality_indent = "        "
    lines[quality_idx] = quality_indent + lines[quality_idx].lstrip()

# 6) Inserisce il blocco corretto subito prima del quality_report.
block_marker = "FASE 5.13C.1 — STUDY QUESTIONS 51 REAL CONNECTOR LOCAL SCOPE FIXED"

function_text = "".join(lines[start:end])

if block_marker not in function_text:
    block = [
        f"{quality_indent}# {block_marker}\n",
        f"{quality_indent}from backend.phase5_study_questions_real_connector_v513c1 import (\n",
        f"{quality_indent}    build_study_questions_real_connection_report,\n",
        f"{quality_indent})\n",
        "\n",
        f"{quality_indent}study_questions_real_connection_v513c1 = build_study_questions_real_connection_report(\n",
        f"{quality_indent}    result.domande_studio,\n",
        f"{quality_indent}    result.errors,\n",
        f"{quality_indent})\n",
        "\n",
    ]

    lines = lines[:quality_idx] + block + lines[quality_idx:]
    end += len(block)

# 7) Inserisce il campo nel dizionario dopo study_questions_count.
field_already_present = any(
    '"study_questions_real_connection_v513c1"' in line
    for line in lines[start:end]
)

if not field_already_present:
    insert_after = None
    for i in range(start, end):
        if '"study_questions_count": len(result.domande_studio),' in lines[i]:
            insert_after = i
            break

    if insert_after is None:
        raise SystemExit("FAIL - campo study_questions_count non trovato nel quality_report")

    field_indent = re.match(r'^(\s*)', lines[insert_after]).group(1)
    lines.insert(
        insert_after + 1,
        f'{field_indent}"study_questions_real_connection_v513c1": study_questions_real_connection_v513c1,\n',
    )

TARGET.write_text("".join(lines), encoding="utf-8")

print("PASS - motori_scrittura.py riparato: indentazione 5.13C.1 sistemata")
