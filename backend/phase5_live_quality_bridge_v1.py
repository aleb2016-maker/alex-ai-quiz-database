from __future__ import annotations

# FASE 5.3 — LIVE QUALITY BRIDGE V1
#
# Bridge controllato verso motori qualità vivi:
# - backend.main.pulisci_qualita_linguistica_quiz
# - scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests
#
# Non importa backup.
# Non usa main_backup_*.
# Non riscrive motori già esistenti.
# Non deve rompere la Fase 5 se un motore fallisce.

import copy
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Callable


PHASE = "5.3"
ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


QUIZ_KEYS = {
    "quiz",
    "quizzes",
    "quiz_draft",
    "test",
    "tests",
    "test_quiz",
    "quiz_finale",
    "test_finale",
    "domande_quiz",
}


def _safe_error(exc: BaseException) -> str:
    return f"{exc.__class__.__name__}: {exc}"


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        return repr(value)


def _load_callable(module_name: str, function_name: str) -> tuple[Callable[[Any], Any] | None, str | None]:
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, function_name)

        if not callable(fn):
            return None, f"{module_name}.{function_name} non è callable"

        return fn, None

    except Exception as exc:
        return None, _safe_error(exc)


def _ensure_meta(result: Any) -> dict[str, Any] | None:
    if not isinstance(result, dict):
        return None

    meta = result.setdefault("_phase5_live_quality_bridge_v1", {})
    meta.setdefault("phase", PHASE)
    meta.setdefault("status", "running")
    meta.setdefault("motors", {})
    meta.setdefault("notes", [])

    return meta


def _walk_strings(value: Any) -> list[str]:
    found: list[str] = []

    if isinstance(value, str):
        found.append(value)

    elif isinstance(value, dict):
        for child in value.values():
            found.extend(_walk_strings(child))

    elif isinstance(value, list):
        for child in value:
            found.extend(_walk_strings(child))

    return found


def _count_known_text_defects(value: Any) -> int:
    text = "\n".join(_walk_strings(value)).lower()

    patterns = [
        r"\bnon\s+non\b",
        r"\bcos e\b",
        r"\bqual e\b",
        r"\s+([,.!?;:])",
        r"\s{2,}",
    ]

    total = 0

    for pattern in patterns:
        total += len(re.findall(pattern, text, flags=re.IGNORECASE))

    return total


def _looks_like_option_dict(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    return bool(keys & {"text", "testo", "label", "value", "is_correct", "correct"})


def _looks_like_quiz_question(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    has_question = bool(keys & {"question", "domanda", "prompt"})
    has_options = bool(keys & {"options", "opzioni", "answers", "risposte"})
    has_answer = bool(keys & {"answer", "correct_answer", "correct_option_id", "risposta", "risposta_corretta"})

    if has_question and (has_options or has_answer):
        return True

    options = value.get("options", value.get("opzioni"))

    if isinstance(options, list) and any(_looks_like_option_dict(item) for item in options):
        return True

    return False


def _looks_like_quiz_list(value: Any) -> bool:
    if not isinstance(value, list) or not value:
        return False

    dict_items = [item for item in value if isinstance(item, dict)]

    if not dict_items:
        return False

    good = sum(1 for item in dict_items if _looks_like_quiz_question(item))

    return good >= max(1, len(dict_items) // 2)


def _candidate_quiz_targets(result: Any) -> list[tuple[Any, str | None, Any, str]]:
    targets: list[tuple[Any, str | None, Any, str]] = []

    if isinstance(result, dict):
        for key, value in result.items():
            key_norm = str(key).lower()

            if key_norm.startswith("_"):
                continue

            if key_norm in QUIZ_KEYS and isinstance(value, (list, dict)):
                targets.append((result, key, value, key))
                continue

            if _looks_like_quiz_list(value):
                targets.append((result, key, value, key))

    elif isinstance(result, list) and _looks_like_quiz_list(result):
        targets.append((None, None, result, "root_list"))

    return targets




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


def _apply_motor(result: Any, module_name: str, function_name: str) -> Any:
    meta = _ensure_meta(result)
    motor_id = f"{module_name}.{function_name}"

    if meta is not None:
        meta["motors"][motor_id] = {
            "status": "pending",
            "applied": 0,
            "changed": 0,
            "targets": [],
        }

    fn, load_error = _load_callable(module_name, function_name)

    if fn is None:
        if meta is not None:
            meta["motors"][motor_id]["status"] = "failed_import"
            meta["motors"][motor_id]["error"] = load_error
        return result

    targets = _candidate_quiz_targets(result)

    if not targets:
        if meta is not None:
            meta["motors"][motor_id]["status"] = "skipped_no_quiz_target"
        return result

    applied = 0
    changed = 0
    errors: list[str] = []

    for parent, key, value, label in targets:
        before_json = _safe_json(value)
        defects_before = _count_known_text_defects(value)

        try:
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

        if new_value is None:
            new_value = value

        after_json = _safe_json(new_value)
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

    if meta is not None:
        meta["motors"][motor_id]["applied"] = applied
        meta["motors"][motor_id]["changed"] = changed

        if errors and applied == 0:
            meta["motors"][motor_id]["status"] = "failed"
            meta["motors"][motor_id]["errors"] = errors
        elif errors:
            meta["motors"][motor_id]["status"] = "partial"
            meta["motors"][motor_id]["errors"] = errors
        else:
            meta["motors"][motor_id]["status"] = "ok"

    return result


def apply_phase5_live_quality_bridge_v1(payload: Any) -> Any:
    result = copy.deepcopy(payload)

    meta = _ensure_meta(result)

    if meta is not None:
        meta["description"] = "Bridge controllato Fase 5.3 verso motori qualità vivi"
        meta["status"] = "running"

    defects_before = _count_known_text_defects(result)

    result = _apply_motor(
        result,
        "backend.main",
        "pulisci_qualita_linguistica_quiz",
    )

    result = _apply_motor(
        result,
        "scripts.rag_motore_didattico_riutilizzabile_v35c",
        "refine_tests",
    )

    defects_after = _count_known_text_defects(result)

    meta = _ensure_meta(result)

    if meta is not None:
        meta["known_text_defects_before"] = defects_before
        meta["known_text_defects_after"] = defects_after

        statuses = [
            info.get("status")
            for info in meta.get("motors", {}).values()
        ]

        if statuses and all(status == "ok" for status in statuses):
            meta["status"] = "ok"
        elif any(status in {"ok", "partial"} for status in statuses):
            meta["status"] = "partial"
        else:
            meta["status"] = "degraded"

    return result
