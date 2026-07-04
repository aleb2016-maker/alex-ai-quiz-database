from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

BRIDGE = ROOT / "backend" / "phase5_live_quality_bridge_v1.py"
PATCH_GENERATOR = ROOT / "scripts" / "patch_phase5_live_quality_bridge_v1.py"

MARKER = "# FASE 5.3.1 — ADATTATORE FORMATO TEST_QUIZ V1"


HELPER_CODE = r'''

# FASE 5.3.1 — ADATTATORE FORMATO TEST_QUIZ V1
# Alcuni motori vivi, come backend.main.pulisci_qualita_linguistica_quiz,
# non accettano una lista diretta di domande, ma un dizionario.
# Questo adattatore converte temporaneamente:
#   test_quiz -> {"test_quiz": test_quiz}
# poi recupera dal risultato la lista corretta.
def _extract_adapted_quiz_value(adapted_output: Any, original_key: str, fallback: Any) -> Any:
    if adapted_output is None:
        return fallback

    if isinstance(adapted_output, list):
        return adapted_output

    if isinstance(adapted_output, dict):
        preferred_keys = [
            original_key,
            "test_quiz",
            "quiz",
            "quiz_draft",
            "test",
            "tests",
            "domande_quiz",
        ]

        for key in preferred_keys:
            value = adapted_output.get(key)
            if isinstance(value, (list, dict)):
                return value

    return adapted_output


def _call_motor_with_format_adapter(
    *,
    fn: Callable[[Any], Any],
    module_name: str,
    function_name: str,
    value: Any,
    label: str,
) -> Any:
    motor_id = f"{module_name}.{function_name}"

    # Motore vivo storico: si aspetta dict, non lista.
    if motor_id == "backend.main.pulisci_qualita_linguistica_quiz" and isinstance(value, list):
        wrapped_payload = {
            label: copy.deepcopy(value),
            "test_quiz": copy.deepcopy(value),
            "quiz": copy.deepcopy(value),
            "_phase5_3_adapter": {
                "source_label": label,
                "reason": "motor_requires_dict_not_list",
            },
        }

        adapted_output = fn(wrapped_payload)

        return _extract_adapted_quiz_value(
            adapted_output=adapted_output,
            original_key=label,
            fallback=value,
        )

    return fn(copy.deepcopy(value))
'''


OLD_CALL = '''        try:
            new_value = fn(copy.deepcopy(value))
        except Exception as exc:
            errors.append(f"{label}: {_safe_error(exc)}")
            continue
'''

NEW_CALL = '''        try:
            new_value = _call_motor_with_format_adapter(
                fn=fn,
                module_name=module_name,
                function_name=function_name,
                value=value,
                label=label,
            )
        except Exception as exc:
            errors.append(f"{label}: {_safe_error(exc)}")
            continue
'''


def patch_file(path: Path) -> bool:
    if not path.exists():
        print(f"ℹ️ File non trovato, salto: {path}")
        return False

    text = path.read_text(encoding="utf-8")

    changed = False

    if MARKER not in text:
        anchor = "\ndef _apply_motor(result: Any, module_name: str, function_name: str) -> Any:\n"

        if anchor not in text:
            raise RuntimeError(f"Anchor _apply_motor non trovato in {path}")

        text = text.replace(anchor, HELPER_CODE + anchor)
        changed = True

    if OLD_CALL in text:
        text = text.replace(OLD_CALL, NEW_CALL)
        changed = True

    if changed:
        path.write_text(text, encoding="utf-8")
        print(f"✅ Patch adattatore applicata a: {path}")
    else:
        print(f"ℹ️ Nessuna modifica necessaria: {path}")

    return changed


def main() -> int:
    if not BRIDGE.exists():
        raise FileNotFoundError(f"Bridge non trovato: {BRIDGE}")

    patch_file(BRIDGE)

    # Aggiorna anche il generatore patch, così non rigenera il bridge vecchio se rilanciato.
    patch_file(PATCH_GENERATOR)

    print("✅ FASE 5.3.1 ADATTATORE FORMATO TEST_QUIZ COMPLETATA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
