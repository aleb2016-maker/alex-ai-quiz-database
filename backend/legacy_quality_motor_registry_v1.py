from __future__ import annotations

# FASE 5.4 — LEGACY QUALITY MOTOR REGISTRY V1
#
# Struttura centrale per collegare i vecchi motori qualità alla nuova pipeline.
#
# Principi:
# - non importa backup;
# - non chiama main_backup_*;
# - non riscrive i motori vecchi;
# - usa adapter input/output;
# - rifiuta automaticamente un motore se peggiora i difetti testuali noti;
# - restituisce metadata tracciabili.

import copy
import importlib
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REGISTRY_VERSION = "legacy_quality_motor_registry_v1"


@dataclass(frozen=True)
class LegacyMotorSpec:
    motor_id: str
    module_name: str
    function_name: str
    adapter_name: str
    target_kind: str
    enabled: bool = True


LEGACY_QUALITY_MOTORS: list[LegacyMotorSpec] = [

    # FASE 5.6 — READY SAFE LEGACY MOTORS V1
    # Motori emersi dalla diagnostica Fase 5.5 come READY_SAFE.
    # Sono collegati tramite adapter e restano protetti dalla guardia anti-peggioramento.
    LegacyMotorSpec(
        motor_id="scripts.rag_cleaner_finale_universale_v35k.clean_output",
        module_name="scripts.rag_cleaner_finale_universale_v35k",
        function_name="clean_output",
        adapter_name="summary_dict",
        target_kind="summary",
    ),
    LegacyMotorSpec(
        motor_id="scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions",
        module_name="scripts.rag_motore_didattico_riutilizzabile_v35c",
        function_name="refine_study_questions",
        adapter_name="cards_list",
        target_kind="study",
    ),
    LegacyMotorSpec(
        motor_id="scripts.rag_motore_test_riutilizzabile_v35d.refine_output",
        module_name="scripts.rag_motore_test_riutilizzabile_v35d",
        function_name="refine_output",
        adapter_name="summary_dict",
        target_kind="summary",
    ),
    LegacyMotorSpec(
        motor_id="scripts.rag_revisore_accordo_pronomi_v35j.improve_output",
        module_name="scripts.rag_revisore_accordo_pronomi_v35j",
        function_name="improve_output",
        adapter_name="summary_dict",
        target_kind="summary",
    ),
    LegacyMotorSpec(
        motor_id="scripts.rag_revisore_qualita_testuale_v35g.refine_output",
        module_name="scripts.rag_revisore_qualita_testuale_v35g",
        function_name="refine_output",
        adapter_name="summary_dict",
        target_kind="summary",
    ),
    LegacyMotorSpec(
        motor_id="scripts.rag_revisore_qualita_testuale_v35g.refine_study",
        module_name="scripts.rag_revisore_qualita_testuale_v35g",
        function_name="refine_study",
        adapter_name="phase5_full_output",
        target_kind="full_output",
    ),
    LegacyMotorSpec(
        motor_id="backend.main.pulisci_qualita_linguistica_quiz",
        module_name="backend.main",
        function_name="pulisci_qualita_linguistica_quiz",
        adapter_name="dict_test_quiz",
        target_kind="quiz",
    ),
    LegacyMotorSpec(
        motor_id="scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests",
        module_name="scripts.rag_motore_didattico_riutilizzabile_v35c",
        function_name="refine_tests",
        adapter_name="legacy_answers_dict",
        target_kind="quiz",
    ),
]


QUIZ_TARGET_KEYS = {
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

SUMMARY_TARGET_KEYS = {
    "riassunto_qualita",
    "summary",
    "riassunto",
    "summary_dict",
}

CARDS_TARGET_KEYS = {
    "card_concettuali",
    "cards",
    "cards_list",
    "flashcards",
}

STUDY_TARGET_KEYS = {
    "domande_studio",
    "study_questions",
    "study",
    "study_list",
}

FULL_OUTPUT_TARGET_KEYS = {
    "phase5_full_output",
    "full_output",
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


def count_known_text_defects_v1(value: Any) -> int:
    text = "\n".join(_walk_strings(value)).lower()

    patterns = [
        r"\bnon\s+non\b",
        r"\bcos e\b",
        r"\bqual e\b",
        r"\s+([,.!?;:])",
        r"\s{2,}",
        r"\buna\s+una\b",
        r"\bun\s+un\b",
        r"\bil\s+il\b",
        r"\bla\s+la\b",
    ]

    return sum(
        len(re.findall(pattern, text, flags=re.IGNORECASE))
        for pattern in patterns
    )




# FASE 5.7.1 — REGISTRY TARGET STRUCTURE GUARD V1
# Evita che un motore legacy cambi la struttura del target in modo da impedire
# ai motori successivi di trovare summary/cards/study/full_output.
# Inoltre preserva i metadata del registry quando un motore lavora sul full output.
def _looks_like_summary_dict(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    return bool(keys & {"titolo", "title", "paragrafi", "paragraphs", "testo_completo", "text", "summary"})


def _extract_nested_target_value(value: Any, label: str, target_kind: str) -> Any:
    if not isinstance(value, dict):
        return value

    preferred = [label]

    if target_kind == "summary":
        preferred.extend(["riassunto_qualita", "summary", "riassunto", "summary_dict"])

    elif target_kind == "cards":
        preferred.extend(["card_concettuali", "cards", "cards_list"])

    elif target_kind == "study":
        preferred.extend(["domande_studio", "study_questions", "study", "study_list", "card_concettuali", "cards"])

    elif target_kind == "quiz":
        preferred.extend(["test_quiz", "quiz", "tests", "domande_quiz"])

    for key in preferred:
        child = value.get(key)

        if isinstance(child, (dict, list, str)):
            return child

    return value


def _normalize_output_for_target_structure_v1(
    *,
    before_value: Any,
    candidate_value: Any,
    target_kind: str,
    label: str,
) -> tuple[Any, bool, str]:
    if candidate_value is None:
        return before_value, True, "none_output"

    candidate_value = _extract_nested_target_value(candidate_value, label, target_kind)

    if target_kind == "summary":
        if isinstance(before_value, dict):
            if isinstance(candidate_value, dict) and _looks_like_summary_dict(candidate_value):
                return candidate_value, False, ""

            return before_value, True, "summary_dict_structure_not_preserved"

        if isinstance(before_value, str):
            if isinstance(candidate_value, str):
                return candidate_value, False, ""

            return before_value, True, "summary_text_structure_not_preserved"

    if target_kind in {"cards", "study", "quiz"}:
        if isinstance(before_value, list):
            if isinstance(candidate_value, list):
                return candidate_value, False, ""

            return before_value, True, f"{target_kind}_list_structure_not_preserved"

        if isinstance(before_value, dict):
            if isinstance(candidate_value, dict):
                return candidate_value, False, ""

            return before_value, True, f"{target_kind}_dict_structure_not_preserved"

    if target_kind == "full_output":
        if isinstance(before_value, dict) and isinstance(candidate_value, dict):
            return candidate_value, False, ""

        return before_value, True, "full_output_structure_not_preserved"

    if type(candidate_value) is type(before_value):
        return candidate_value, False, ""

    return before_value, True, "generic_structure_not_preserved"


def _preserve_registry_meta_after_root_replace_v1(new_result: Any, previous_result: Any) -> Any:
    if not isinstance(new_result, dict) or not isinstance(previous_result, dict):
        return new_result

    previous_meta = previous_result.get("_legacy_quality_motor_registry_v1")

    if isinstance(previous_meta, dict):
        new_result["_legacy_quality_motor_registry_v1"] = previous_meta

    return new_result


def _looks_like_option_dict(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    return bool(keys & {"testo", "text", "label", "value", "is_correct", "correct"})


def _looks_like_quiz_question(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    has_question = bool(keys & {"domanda", "question", "prompt"})
    has_options = bool(keys & {"opzioni", "options", "answers", "risposte", "choices"})
    has_answer = bool(keys & {"answer", "correct_answer", "correct_option_id", "risposta", "risposta_corretta", "correct"})

    if has_question and (has_options or has_answer):
        return True

    options = value.get("opzioni") or value.get("options") or value.get("answers") or value.get("choices")

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


def _candidate_quiz_targets(payload: Any) -> list[tuple[Any, str | None, Any, str]]:
    targets: list[tuple[Any, str | None, Any, str]] = []

    if isinstance(payload, dict):
        for key, value in payload.items():
            key_norm = str(key).lower()

            if key_norm.startswith("_"):
                continue

            if key_norm in QUIZ_TARGET_KEYS and isinstance(value, (list, dict)):
                targets.append((payload, key, value, key))
                continue

            if _looks_like_quiz_list(value):
                targets.append((payload, key, value, key))

    elif isinstance(payload, list) and _looks_like_quiz_list(payload):
        targets.append((None, None, payload, "root_list"))

    return targets


def _candidate_targets_for_kind(payload: Any, target_kind: str) -> list[tuple[Any, str | None, Any, str]]:
    targets: list[tuple[Any, str | None, Any, str]] = []

    if target_kind == "quiz":
        return _candidate_quiz_targets(payload)

    if target_kind == "full_output":
        if isinstance(payload, dict):
            return [(None, None, payload, "phase5_full_output")]
        return []

    if not isinstance(payload, dict):
        return []

    if target_kind == "summary":
        keyset = SUMMARY_TARGET_KEYS
    elif target_kind == "cards":
        keyset = CARDS_TARGET_KEYS
    elif target_kind == "study":
        keyset = STUDY_TARGET_KEYS | CARDS_TARGET_KEYS
    else:
        keyset = set()

    for key, value in payload.items():
        key_norm = str(key).lower()

        if key_norm.startswith("_"):
            continue

        if key_norm in keyset and isinstance(value, (list, dict, str)):
            targets.append((payload, key, value, key))

    return targets


def _option_letter(index: int) -> str:
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    if 0 <= index < len(letters):
        return letters[index]

    return str(index + 1)


def _phase5_correct_text(item: dict[str, Any]) -> str:
    correct_id = item.get("correct_option_id")

    for option in item.get("opzioni", []):
        if not isinstance(option, dict):
            continue

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


def _extract_list(value: Any) -> Any:
    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        for key in ["test_quiz", "quiz", "tests", "questions", "items", "answers", "risposte", "domande_quiz"]:
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


def _legacy_output_to_phase5(value: Any, original_value: Any) -> Any:
    extracted = _extract_list(value)

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
            option_id = _option_letter(option_index)
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


def _call_with_adapter(
    *,
    spec: LegacyMotorSpec,
    fn: Callable[[Any], Any],
    value: Any,
    label: str,
) -> Any:
    if spec.adapter_name == "dict_test_quiz" and isinstance(value, list):
        wrapped_payload = {
            label: copy.deepcopy(value),
            "test_quiz": copy.deepcopy(value),
            "quiz": copy.deepcopy(value),
            "_legacy_quality_registry_adapter": {
                "source_label": label,
                "adapter": spec.adapter_name,
            },
        }

        adapted_output = fn(wrapped_payload)

        return _extract_adapted_quiz_value(
            adapted_output=adapted_output,
            original_key=label,
            fallback=value,
        )

    if spec.adapter_name == "legacy_answers_dict" and isinstance(value, list):
        legacy_payload = _phase5_to_legacy_answers_dict(value)
        legacy_output = fn(copy.deepcopy(legacy_payload))
        return _legacy_output_to_phase5(legacy_output, value)

    if spec.adapter_name in {"summary_dict", "cards_list", "phase5_full_output"}:
        return fn(copy.deepcopy(value))

    return fn(copy.deepcopy(value))


def _ensure_registry_meta(payload: Any) -> dict[str, Any] | None:
    if not isinstance(payload, dict):
        return None

    meta = payload.setdefault("_legacy_quality_motor_registry_v1", {})
    meta.setdefault("version", REGISTRY_VERSION)
    meta.setdefault("status", "running")
    meta.setdefault("motors", {})
    meta.setdefault("targets_count", 0)
    meta.setdefault("notes", [])

    return meta


def apply_legacy_quality_motors_v1(payload: Any, *, context: str = "generic") -> Any:
    result = copy.deepcopy(payload)
    meta = _ensure_registry_meta(result)

    if meta is not None:
        meta["context"] = context

    registry_defects_before = count_known_text_defects_v1(result)

    for spec in LEGACY_QUALITY_MOTORS:
        if not spec.enabled:
            continue

        motor_meta = {
            "status": "pending",
            "adapter_name": spec.adapter_name,
            "target_kind": spec.target_kind,
            "applied": 0,
            "changed": 0,
            "targets": [],
        }

        if meta is not None:
            meta["motors"][spec.motor_id] = motor_meta

        fn, load_error = _load_callable(spec.module_name, spec.function_name)

        if fn is None:
            motor_meta["status"] = "failed_import"
            motor_meta["error"] = load_error
            continue

        targets = _candidate_targets_for_kind(result, spec.target_kind)

        if meta is not None:
            meta["targets_count"] = len(targets)

        if not targets:
            motor_meta["status"] = "skipped_no_target"
            continue

        errors: list[str] = []

        for parent, key, value, label in targets:
            before_json = _safe_json(value)
            defects_before = count_known_text_defects_v1(value)

            try:
                new_value = _call_with_adapter(
                    spec=spec,
                    fn=fn,
                    value=value,
                    label=label,
                )
            except Exception as exc:
                errors.append(f"{label}: {_safe_error(exc)}")
                continue

            structural_rejected = False
            structural_reject_reason = ""

            if new_value is None:
                new_value = value

            new_value, structural_rejected, structural_reject_reason = _normalize_output_for_target_structure_v1(
                before_value=value,
                candidate_value=new_value,
                target_kind=spec.target_kind,
                label=label,
            )

            after_json = _safe_json(new_value)
            defects_after = count_known_text_defects_v1(new_value)

            guarded_rejected = False

            if defects_after > defects_before:
                guarded_rejected = True
                new_value = value
                after_json = before_json
                defects_after = defects_before

            if parent is not None and key is not None:
                parent[key] = new_value
            else:
                result = _preserve_registry_meta_after_root_replace_v1(new_value, result)

            motor_meta["applied"] += 1

            did_change = before_json != after_json

            if did_change:
                motor_meta["changed"] += 1

            motor_meta["targets"].append(
                {
                    "target": label,
                    "changed": did_change,
                    "guarded_rejected": guarded_rejected,
                    "structural_rejected": structural_rejected,
                    "structural_reject_reason": structural_reject_reason,
                    "known_text_defects_before": defects_before,
                    "known_text_defects_after": defects_after,
                }
            )

        if errors and motor_meta["applied"] == 0:
            motor_meta["status"] = "failed"
            motor_meta["errors"] = errors
        elif errors:
            motor_meta["status"] = "partial"
            motor_meta["errors"] = errors
        else:
            motor_meta["status"] = "ok"

        meta = _ensure_registry_meta(result)

        if meta is not None:
            meta["motors"][spec.motor_id] = motor_meta

    registry_defects_after = count_known_text_defects_v1(result)

    meta = _ensure_registry_meta(result)

    if meta is not None:
        meta["known_text_defects_before"] = registry_defects_before
        meta["known_text_defects_after"] = min(registry_defects_after, registry_defects_before)

        statuses = [
            item.get("status")
            for item in meta.get("motors", {}).values()
        ]

        if statuses and all(status == "ok" for status in statuses):
            meta["status"] = "ok"
        elif any(status in {"ok", "partial"} for status in statuses):
            meta["status"] = "partial"
        else:
            meta["status"] = "degraded"

    return result
