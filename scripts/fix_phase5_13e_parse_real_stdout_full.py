#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13E.1 — FIX PARSING JSON TEST REALE

Problema:
- il runner aggregato 5.13E leggeva il JSON del test reale da real.stdout_tail;
- stdout_tail è solo la coda dell'output;
- quando il JSON è lungo, la coda può partire da un oggetto interno;
- quindi approved/status/quality_report risultavano None.

Fix:
- conserva nel report solo la coda per non appesantire il JSON finale;
- ma per il parsing usa stdout completo del comando reale.

Non modifica motori, UI, PDF o app.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_phase5_13e_final_4_generators_regression.py"

text = SCRIPT.read_text(encoding="utf-8")

old_real_block = '''    real = run_command(
        "Real study quiz test",
        [sys.executable, "backend/test_phase5_study_quiz_v1.py"],
    )
    commands.append(real)
'''

new_real_block = '''    real_completed = subprocess.run(
        [sys.executable, "backend/test_phase5_study_quiz_v1.py"],
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    real_full_stdout = real_completed.stdout
    real = CommandResult(
        label="Real study quiz test",
        command=[sys.executable, "backend/test_phase5_study_quiz_v1.py"],
        returncode=real_completed.returncode,
        stdout_tail=_tail(real_full_stdout),
    )
    commands.append(real)
'''

if old_real_block not in text:
    raise SystemExit("FAIL - blocco Real study quiz test non trovato nel runner 5.13E")

text = text.replace(old_real_block, new_real_block, 1)

old_parse = '''        source = extract_first_json_object(real.stdout_tail)
'''

new_parse = '''        source = extract_first_json_object(real_full_stdout)
'''

if old_parse not in text:
    raise SystemExit("FAIL - parse da real.stdout_tail non trovato nel runner 5.13E")

text = text.replace(old_parse, new_parse, 1)

SCRIPT.write_text(text, encoding="utf-8")

print("PASS - Fix Fase 5.13E.1 applicato: parsing JSON test reale da stdout completo")
