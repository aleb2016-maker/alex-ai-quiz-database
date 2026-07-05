#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.13D.4 — CONNECTOR OBJECT SAFE + STRICT GATE

Ripara:
1) phase5_test_quiz_real_connector_v513d1.py:
   - valida sia dict sia dataclass/oggetti;
   - non marca più quiz_item_x_not_dict quando il quiz reale è un oggetto valido.

2) phase5_test_quiz_final_quality_gate_v513d2.py:
   - boccia se quality_report.test_quiz_real_connection_v513d1 non è PASS;
   - boccia se il connector interno contiene defects/warnings.

Non modifica UI/PDF/app.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CONNECTOR = ROOT / "backend" / "phase5_test_quiz_real_connector_v513d1.py"
GATE = ROOT / "backend" / "phase5_test_quiz_final_quality_gate_v513d2.py"


# ---------------------------------------------------------------------
# 1) Connector object-safe
# ---------------------------------------------------------------------

connector_text = CONNECTOR.read_text(encoding="utf-8")

start = connector_text.find("def _validate_quiz_shape(")
end = connector_text.find("def build_test_quiz_real_connection_report", start)

if start < 0 or end < 0:
    raise SystemExit("FAIL - funzione _validate_quiz_shape non trovata nel connector D1")

new_validate_block = r'''def _item_get(obj: Any, key: str, default: Any = None) -> Any:
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _item_text(obj: Any, *keys: str) -> str:
    for key in keys:
        value = _item_get(obj, key, None)
        if value is not None:
            return str(value or "").strip()
    return ""


def _item_list(obj: Any, *keys: str) -> List[Any]:
    for key in keys:
        value = _item_get(obj, key, None)
        if isinstance(value, list):
            return value
    return []


def _validate_quiz_shape(test_quiz: List[Any]) -> List[str]:
    defects: List[str] = []

    if not test_quiz:
        defects.append("Output reale Test/Quiz vuoto.")
        return defects

    for index, item in enumerate(test_quiz, start=1):
        # Il quiz reale può arrivare come dict dopo serializzazione
        # oppure come dataclass/oggetto dentro build_phase5_quality_study_quiz.
        if not isinstance(item, dict) and not (
            hasattr(item, "opzioni")
            or hasattr(item, "options")
            or hasattr(item, "domanda")
            or hasattr(item, "question")
        ):
            defects.append(f"quiz_item_{index}_not_supported_object")
            continue

        options = _item_list(item, "opzioni", "options")

        if len(options) != EXPECTED_OPTIONS_COUNT:
            defects.append(f"quiz_item_{index}_options_expected_4_found_{len(options)}")

        correct_option_id = _item_text(item, "correct_option_id", "risposta_corretta")
        if not correct_option_id:
            defects.append(f"quiz_item_{index}_correct_option_id_missing")

        option_ids: List[str] = []
        correct_flags = 0

        for option_index, option in enumerate(options, start=1):
            if not isinstance(option, dict) and not (
                hasattr(option, "option_id")
                or hasattr(option, "id")
                or hasattr(option, "testo")
                or hasattr(option, "text")
            ):
                defects.append(f"quiz_item_{index}_option_{option_index}_not_supported_object")
                continue

            option_id = _item_text(option, "option_id", "id")
            option_text = _item_text(option, "testo", "text")

            if not option_id:
                defects.append(f"quiz_item_{index}_option_{option_index}_id_missing")

            if not option_text:
                defects.append(f"quiz_item_{index}_option_{option_index}_text_missing")

            option_ids.append(option_id)

            if bool(_item_get(option, "is_correct", False)):
                correct_flags += 1

        if correct_option_id and correct_option_id not in option_ids:
            defects.append(f"quiz_item_{index}_correct_option_id_not_in_options:{correct_option_id}")

        if correct_flags != 1:
            defects.append(f"quiz_item_{index}_correct_flags_expected_1_found_{correct_flags}")

    return defects


'''

connector_text = connector_text[:start] + new_validate_block + connector_text[end:]
CONNECTOR.write_text(connector_text, encoding="utf-8")
print(f"PATCHED {CONNECTOR.relative_to(ROOT)}")


# ---------------------------------------------------------------------
# 2) Gate D2 strict su connector interno
# ---------------------------------------------------------------------

gate_text = GATE.read_text(encoding="utf-8")

anchor = '''    executed_ids = _as_list(real_connection.get("executed_motor_ids"))
    if len(executed_ids) != EXPECTED_ROUTE_TOTAL:
        defects.append(f"executed_motor_ids_expected_63_found_{len(executed_ids)}")
'''

replacement = '''    executed_ids = _as_list(real_connection.get("executed_motor_ids"))
    if len(executed_ids) != EXPECTED_ROUTE_TOTAL:
        defects.append(f"executed_motor_ids_expected_63_found_{len(executed_ids)}")

    connection_status = _text(real_connection.get("status"))
    if not connection_status.startswith("PASS - Fase 5.13D.1"):
        defects.append(f"test_quiz_real_connection_status_not_pass:{connection_status}")

    connection_defects = _as_list(real_connection.get("defects"))
    if connection_defects:
        defects.append(f"test_quiz_real_connection_defects_not_empty:{connection_defects}")

    connection_warnings = _as_list(real_connection.get("warnings"))
    if connection_warnings:
        defects.append(f"test_quiz_real_connection_warnings_not_empty:{connection_warnings}")
'''

if anchor in gate_text:
    gate_text = gate_text.replace(anchor, replacement, 1)
elif "test_quiz_real_connection_status_not_pass" in gate_text:
    print("Strict connector check già presente nel gate D2")
else:
    raise SystemExit("FAIL - anchor executed_ids non trovato nel gate D2")

GATE.write_text(gate_text, encoding="utf-8")
print(f"PATCHED {GATE.relative_to(ROOT)}")

print("PASS - Fix Fase 5.13D.4 applicato: connector object-safe + strict final gate")
