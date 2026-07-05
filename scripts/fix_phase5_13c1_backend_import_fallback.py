#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]

MOTORI = ROOT / "backend" / "motori_scrittura.py"
CONNECTOR = ROOT / "backend" / "phase5_study_questions_real_connector_v513c1.py"

# ---------------------------------------------------------------------
# 1) Fix dentro motori_scrittura.py
# ---------------------------------------------------------------------

text = MOTORI.read_text(encoding="utf-8")

old_import = """        from backend.phase5_study_questions_real_connector_v513c1 import (
            build_study_questions_real_connection_report,
        )
"""

new_import = """        try:
            from backend.phase5_study_questions_real_connector_v513c1 import (
                build_study_questions_real_connection_report,
            )
        except ModuleNotFoundError:
            from phase5_study_questions_real_connector_v513c1 import (
                build_study_questions_real_connection_report,
            )
"""

if old_import in text:
    text = text.replace(old_import, new_import, 1)
elif "from phase5_study_questions_real_connector_v513c1 import" in text:
    print("Import fallback già presente in motori_scrittura.py")
else:
    raise SystemExit("FAIL - import connector 5.13C.1 non trovato in motori_scrittura.py")

MOTORI.write_text(text, encoding="utf-8")


# ---------------------------------------------------------------------
# 2) Fix dentro phase5_study_questions_real_connector_v513c1.py
#    Anche questo modulo deve funzionare sia come package backend.*
#    sia come modulo locale quando viene richiamato da backend/test_*.py.
# ---------------------------------------------------------------------

text = CONNECTOR.read_text(encoding="utf-8")

old_load = """def _load_canonical_route() -> Any:
    from backend.phase5_study_questions_route_materializer_v513c01 import run_and_write

    return run_and_write()
"""

new_load = """def _load_canonical_route() -> Any:
    try:
        from backend.phase5_study_questions_route_materializer_v513c01 import run_and_write
    except ModuleNotFoundError:
        from phase5_study_questions_route_materializer_v513c01 import run_and_write

    return run_and_write()
"""

if old_load in text:
    text = text.replace(old_load, new_load, 1)
elif "from phase5_study_questions_route_materializer_v513c01 import run_and_write" in text:
    print("Import fallback già presente nel connector")
else:
    raise SystemExit("FAIL - _load_canonical_route non trovato nel connector 5.13C.1")

CONNECTOR.write_text(text, encoding="utf-8")

print("PASS - Fix import fallback Fase 5.13C.1 applicato")
