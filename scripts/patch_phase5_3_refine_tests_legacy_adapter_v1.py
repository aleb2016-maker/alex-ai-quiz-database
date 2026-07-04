from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

FILES = [
    ROOT / "backend" / "phase5_live_quality_bridge_v1.py",
    ROOT / "scripts" / "patch_phase5_live_quality_bridge_v1.py",
]

TEST = ROOT / "backend" / "test_phase5_live_quality_bridge_v1.py"

START_MARKER = "# FASE 5.3.1 — ADATTATORE FORMATO TEST_QUIZ V1"
END_ANCHOR = "\ndef _apply_motor(result: Any, module_name: str, function_name: str) -> Any:\n"

NEW_ADAPTER_BLOCK = r'''
# FASE 5.3.3 — REFINE_TESTS LEGACY ADAPTER V1
# Adapter reale per usare refine_tests con il formato legacy compatibile trovato:
# legacy_answers_dict.
def _phase5_option_letter(index: int) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if 0 <= index < len(letters):
        return letters[index]
    return str(index + 1)


def _phase5_correct_text(item: dict[str, Any]) -> str:
    correct_id = item.get("correct_option_id")

    for option in item.get("opzioni", []):
        if option.get("is_correct") is True:
            return str(option.get("testo", ""))

        if correct_id and option.get("option_id") == correct_id:
            return str(option.get("testo", ""))

    return ""


def _phase5_to_legacy_answers_dict(value: Any) -> Any:
    if not isinstance(value, list):
        return value

    converted: list[dict[str, Any]] = []

    for item in value:
        if not isinstance(item, dict):
            continue

        answers = []

        for option in item.get("opzioni", []):
            if not isinstance(option, dict):
                continue

            answers.append(
                {
                    "label": option.get("option_id"),
                    "text": option.get("testo"),
                    "correct": option.get("is_correct") is True,
                }
            )

        converted.append(
            {
                "question": item.get("domanda") or item.get("question") or "",
                "answers": answers,
                "correct": item.get("correct_option_id"),
                "explanation": item.get("spiegazione") or item.get("explanation") or "",
            }
        )

    return converted


def _extract_legacy_list(value: Any) -> Any:
    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        for key in ["test_quiz", "quiz", "tests", "questions", "items", "answers", "risposte"]:
            child = value.get(key)

            if isinstance(child, list):
                return child

    return value


def _legacy_option_text(option: Any) -> str:
    if isinstance(option, str):
        return option

    if isinstance(option, dict):
        for key in ["testo", "text", "label", "value", "answer"]:
            value = option.get(key)

            if isinstance(value, str):
                return value

    return ""


def _legacy_refine_output_to_phase5(value: Any, original_value: Any) -> Any:
    extracted = _extract_legacy_list(value)

    if not isinstance(extracted, list):
        return original_value

    if not isinstance(original_value, list):
        return original_value

    normalized: list[dict[str, Any]] = []

    for index, item in enumerate(extracted):
        if not isinstance(item, dict):
            return original_value

        original_item = original_value[index] if index < len(original_value) and isinstance(original_value[index], dict) else {}

        question_text = (
            item.get("domanda")
            or item.get("question")
            or item.get("prompt")
            or original_item.get("domanda")
            or ""
        )

        raw_options = (
            item.get("opzioni")
            or item.get("options")
            or item.get("answers")
            or item.get("risposte")
            or item.get("choices")
            or []
        )

        if not isinstance(raw_options, list):
            return original_value

        correct_hint = (
            item.get("correct_option_id")
            or item.get("correct")
            or item.get("answer")
            or item.get("correct_answer")
            or original_item.get("correct_option_id")
        )

        opzioni: list[dict[str, Any]] = []

        for option_index, raw_option in enumerate(raw_options):
            option_id = _phase5_option_letter(option_index)
            option_text = _legacy_option_text(raw_option)
            is_correct = False

            if isinstance(raw_option, dict):
                raw_id = raw_option.get("option_id") or raw_option.get("id") or raw_option.get("label")

                if isinstance(raw_id, str) and raw_id:
                    option_id = raw_id

                if raw_option.get("is_correct") is True or raw_option.get("correct") is True:
                    is_correct = True

            if isinstance(correct_hint, int) and correct_hint == option_index:
                is_correct = True

            if isinstance(correct_hint, str):
                if correct_hint == option_id:
                    is_correct = True

                if option_text and correct_hint.strip() == option_text.strip():
                    is_correct = True

            if not option_text:
                return original_value

            opzioni.append(
                {
                    "option_id": option_id,
                    "testo": option_text,
                    "is_correct": is_correct,
                }
            )

        if not any(option.get("is_correct") is True for option in opzioni):
            original_correct = original_item.get("correct_option_id")

            for option in opzioni:
                if option.get("option_id") == original_correct:
                    option["is_correct"] = True

        correct_option_id = ""

        for option in opzioni:
            if option.get("is_correct") is True:
                correct_option_id = option.get("option_id", "")
                break

        normalized_item = dict(original_item)
        normalized_item["domanda"] = question_text
        normalized_item["opzioni"] = opzioni
        normalized_item["correct_option_id"] = correct_option_id
        normalized_item["spiegazione"] = item.get("spiegazione") or item.get("explanation") or original_item.get("spiegazione") or ""

        normalized.append(normalized_item)

    return normalized


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

    if motor_id == "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests" and isinstance(value, list):
        legacy_payload = _phase5_to_legacy_answers_dict(value)
        legacy_output = fn(copy.deepcopy(legacy_payload))
        return _legacy_refine_output_to_phase5(legacy_output, value)

    return fn(copy.deepcopy(value))

'''


OLD_NO_GUARD = '''        after_json = _safe_json(new_value)
        defects_after = _count_known_text_defects(new_value)

        if parent is not None and key is not None:
            parent[key] = new_value
        else:
            result = new_value

        applied += 1

        did_change = before_json != after_json

        if did_change:
            changed += 1

        if meta is not None:
            meta["motors"][motor_id]["targets"].append(
                {
                    "target": label,
                    "changed": did_change,
                    "known_text_defects_before": defects_before,
                    "known_text_defects_after": defects_after,
                }
            )
'''


NEW_WITH_GUARD = '''        after_json = _safe_json(new_value)
        defects_after = _count_known_text_defects(new_value)

        # FASE 5.3.3 — GUARDIA ANTI-PEGGIORAMENTO
        # Un motore legacy può essere usato solo se non aumenta i difetti noti.
        guarded_rejected = False

        if defects_after > defects_before:
            guarded_rejected = True
            new_value = value
            after_json = before_json
            defects_after = defects_before

        if parent is not None and key is not None:
            parent[key] = new_value
        else:
            result = new_value

        applied += 1

        did_change = before_json != after_json

        if did_change:
            changed += 1

        if meta is not None:
            meta["motors"][motor_id]["targets"].append(
                {
                    "target": label,
                    "changed": did_change,
                    "guarded_rejected": guarded_rejected,
                    "known_text_defects_before": defects_before,
                    "known_text_defects_after": defects_after,
                }
            )
'''


TEST_OLD = '''    if not output["test_quiz"]:
        raise AssertionError("Il bridge ha svuotato test_quiz.")

    report_dir = Path("reports")
'''


TEST_NEW = '''    if not output["test_quiz"]:
        raise AssertionError("Il bridge ha svuotato test_quiz.")

    # QUALITY_NON_WORSENING_ASSERTION
    before = meta.get("known_text_defects_before")
    after = meta.get("known_text_defects_after")

    if isinstance(before, int) and isinstance(after, int) and after > before:
        raise AssertionError(f"Il bridge ha peggiorato i difetti testuali: {before} -> {after}")

    for motor_id, info in motors.items():
        for target in info.get("targets", []):
            tb = target.get("known_text_defects_before")
            ta = target.get("known_text_defects_after")

            if isinstance(tb, int) and isinstance(ta, int) and ta > tb:
                raise AssertionError(f"Il motore {motor_id} ha peggiorato il target {target.get('target')}: {tb} -> {ta}")

    report_dir = Path("reports")
'''


def patch_bridge_file(path: Path) -> bool:
    if not path.exists():
        print(f"ℹ️ File non trovato, salto: {path}")
        return False

    text = path.read_text(encoding="utf-8")
    changed = False

    start = text.find(START_MARKER)

    if start == -1:
        raise RuntimeError(f"Marker adapter 5.3.1 non trovato in {path}")

    end = text.find(END_ANCHOR, start)

    if end == -1:
        raise RuntimeError(f"Anchor _apply_motor non trovato in {path}")

    text = text[:start] + NEW_ADAPTER_BLOCK + text[end:]
    changed = True

    if OLD_NO_GUARD in text:
        text = text.replace(OLD_NO_GUARD, NEW_WITH_GUARD)
        changed = True
    elif "guarded_rejected" in text:
        print(f"ℹ️ Guardia anti-peggioramento già presente in: {path}")
    else:
        raise RuntimeError(f"Blocco guard target non trovato in {path}")

    path.write_text(text, encoding="utf-8")
    print(f"✅ Adapter refine_tests legacy applicato a: {path}")
    return changed


def patch_test_file() -> bool:
    if not TEST.exists():
        print(f"ℹ️ Test non trovato, salto: {TEST}")
        return False

    text = TEST.read_text(encoding="utf-8")

    if "QUALITY_NON_WORSENING_ASSERTION" in text:
        print("ℹ️ Test non-worsening già presente.")
        return False

    if TEST_OLD not in text:
        raise RuntimeError("Blocco test non trovato per assertion anti-peggioramento.")

    TEST.write_text(text.replace(TEST_OLD, TEST_NEW), encoding="utf-8")
    print(f"✅ Assertion anti-peggioramento aggiunta a: {TEST}")
    return True


def main() -> int:
    for path in FILES:
        patch_bridge_file(path)

    patch_test_file()

    print("✅ FASE 5.3.3 REFINE_TESTS LEGACY ADAPTER COMPLETATA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
