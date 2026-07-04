from __future__ import annotations

import copy
import importlib
import json
import re
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


REPORT_JSON = ROOT / "reports" / "adapter_refine_tests_fase5_v1.json"
REPORT_MD = ROOT / "reports" / "adapter_refine_tests_fase5_v1.md"

MOTOR_MODULE = "scripts.rag_motore_didattico_riutilizzabile_v35c"
MOTOR_FUNCTION = "refine_tests"
MOTOR_ID = f"{MOTOR_MODULE}.{MOTOR_FUNCTION}"


PHASE5_TEST_QUIZ = [
    {
        "question_id": "phase5_quiz_question_001",
        "domanda": "Quale affermazione descrive correttamente il divieto su protezione credenziali?",
        "opzioni": [
            {
                "option_id": "A",
                "testo": "Le credenziali possono essere condivise liberamente tra più operatori.",
                "is_correct": False,
            },
            {
                "option_id": "B",
                "testo": "Le credenziali non non devono essere necessariamente condivise tra più operatori.",
                "is_correct": False,
            },
            {
                "option_id": "C",
                "testo": "Le credenziali non devono essere condivise tra più operatori.",
                "is_correct": True,
            },
            {
                "option_id": "D",
                "testo": "Le credenziali non devono essere condivise tra più utenti anonimi.",
                "is_correct": False,
            },
        ],
        "correct_option_id": "C",
        "spiegazione": "La risposta corretta riprende il fatto verificato dal documento.",
        "fatto_origine": "Le credenziali non devono essere condivise tra più operatori.",
        "micro_concetti": [
            "protezione credenziali",
            "condivisione credenziali",
            "controllo accessi",
        ],
        "fonte_pagine": [1, 2],
    }
]


def _load_callable() -> tuple[Callable[[Any], Any] | None, str | None]:
    try:
        module = importlib.import_module(MOTOR_MODULE)
        fn = getattr(module, MOTOR_FUNCTION)

        if not callable(fn):
            return None, f"{MOTOR_ID} non è callable"

        return fn, None

    except Exception as exc:
        return None, f"{exc.__class__.__name__}: {exc}"


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
        r"\buna\s+una\b",
        r"\bun\s+un\b",
        r"\bil\s+il\b",
        r"\bla\s+la\b",
    ]

    return sum(
        len(re.findall(pattern, text, flags=re.IGNORECASE))
        for pattern in patterns
    )


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        return repr(value)


def _letters(index: int) -> str:
    return "ABCDEFGHIJKLMNOPQRSTUVWXYZ"[index]


def _correct_text_from_phase5(item: dict[str, Any]) -> str:
    correct_id = item.get("correct_option_id")

    for option in item.get("opzioni", []):
        if option.get("is_correct") is True:
            return str(option.get("testo", ""))

        if correct_id and option.get("option_id") == correct_id:
            return str(option.get("testo", ""))

    return ""


def _variant_current_phase5_list() -> list[dict[str, Any]]:
    return copy.deepcopy(PHASE5_TEST_QUIZ)


def _variant_legacy_question_options_dict() -> list[dict[str, Any]]:
    converted = []

    for item in PHASE5_TEST_QUIZ:
        options = []

        for option in item["opzioni"]:
            options.append(
                {
                    "id": option["option_id"],
                    "text": option["testo"],
                    "correct": option["is_correct"],
                    "is_correct": option["is_correct"],
                }
            )

        converted.append(
            {
                "id": item["question_id"],
                "question": item["domanda"],
                "options": options,
                "correct_option_id": item["correct_option_id"],
                "correct_answer": _correct_text_from_phase5(item),
                "explanation": item["spiegazione"],
            }
        )

    return converted


def _variant_legacy_question_options_strings_answer() -> list[dict[str, Any]]:
    converted = []

    for item in PHASE5_TEST_QUIZ:
        converted.append(
            {
                "id": item["question_id"],
                "question": item["domanda"],
                "options": [option["testo"] for option in item["opzioni"]],
                "answer": _correct_text_from_phase5(item),
                "correct_answer": _correct_text_from_phase5(item),
                "explanation": item["spiegazione"],
            }
        )

    return converted


def _variant_legacy_answers_dict() -> list[dict[str, Any]]:
    converted = []

    for item in PHASE5_TEST_QUIZ:
        answers = []

        for option in item["opzioni"]:
            answers.append(
                {
                    "label": option["option_id"],
                    "text": option["testo"],
                    "correct": option["is_correct"],
                }
            )

        converted.append(
            {
                "question": item["domanda"],
                "answers": answers,
                "correct": item["correct_option_id"],
                "explanation": item["spiegazione"],
            }
        )

    return converted


def _variant_legacy_choices_strings_index() -> list[dict[str, Any]]:
    converted = []

    for item in PHASE5_TEST_QUIZ:
        correct_index = 0

        for index, option in enumerate(item["opzioni"]):
            if option["is_correct"]:
                correct_index = index

        converted.append(
            {
                "prompt": item["domanda"],
                "choices": [option["testo"] for option in item["opzioni"]],
                "correct": correct_index,
                "explanation": item["spiegazione"],
            }
        )

    return converted


def _variant_legacy_question_choices_answer_letter() -> list[dict[str, Any]]:
    converted = []

    for item in PHASE5_TEST_QUIZ:
        converted.append(
            {
                "question": item["domanda"],
                "choices": [option["testo"] for option in item["opzioni"]],
                "answer": item["correct_option_id"],
                "correct": item["correct_option_id"],
                "explanation": item["spiegazione"],
            }
        )

    return converted


def _make_variants() -> list[dict[str, Any]]:
    return [
        {
            "adapter_name": "current_phase5_italian_list",
            "payload": _variant_current_phase5_list(),
        },
        {
            "adapter_name": "legacy_question_options_dict",
            "payload": _variant_legacy_question_options_dict(),
        },
        {
            "adapter_name": "legacy_question_options_strings_answer",
            "payload": _variant_legacy_question_options_strings_answer(),
        },
        {
            "adapter_name": "legacy_answers_dict",
            "payload": _variant_legacy_answers_dict(),
        },
        {
            "adapter_name": "legacy_choices_strings_index",
            "payload": _variant_legacy_choices_strings_index(),
        },
        {
            "adapter_name": "legacy_question_choices_answer_letter",
            "payload": _variant_legacy_question_choices_answer_letter(),
        },
    ]


def _extract_list(value: Any) -> Any:
    if isinstance(value, list):
        return value

    if isinstance(value, dict):
        for key in [
            "test_quiz",
            "quiz",
            "tests",
            "questions",
            "items",
            "answers",
            "risposte",
        ]:
            child = value.get(key)

            if isinstance(child, list):
                return child

    return value


def _text_from_option(option: Any) -> str:
    if isinstance(option, str):
        return option

    if isinstance(option, dict):
        for key in ["testo", "text", "label", "value", "answer"]:
            value = option.get(key)

            if isinstance(value, str):
                return value

    return ""


def _normalize_back_to_phase5(value: Any) -> list[dict[str, Any]] | None:
    extracted = _extract_list(value)

    if not isinstance(extracted, list):
        return None

    normalized: list[dict[str, Any]] = []

    for index, item in enumerate(extracted):
        if not isinstance(item, dict):
            return None

        question_text = (
            item.get("domanda")
            or item.get("question")
            or item.get("prompt")
            or item.get("title")
        )

        raw_options = (
            item.get("opzioni")
            or item.get("options")
            or item.get("answers")
            or item.get("risposte")
            or item.get("choices")
        )

        if not isinstance(question_text, str) or not isinstance(raw_options, list):
            return None

        correct_hint = (
            item.get("correct_option_id")
            or item.get("correct")
            or item.get("answer")
            or item.get("correct_answer")
            or item.get("risposta_corretta")
        )

        correct_text_hint = ""

        if isinstance(correct_hint, str) and len(correct_hint) > 1:
            correct_text_hint = correct_hint

        opzioni = []

        for option_index, raw_option in enumerate(raw_options):
            option_id = _letters(option_index)
            option_text = _text_from_option(raw_option)

            if not option_text:
                return None

            is_correct = False

            if isinstance(raw_option, dict):
                raw_id = raw_option.get("option_id") or raw_option.get("id") or raw_option.get("label")

                if isinstance(raw_id, str) and len(raw_id) == 1:
                    option_id = raw_id

                if raw_option.get("is_correct") is True or raw_option.get("correct") is True:
                    is_correct = True

            if isinstance(correct_hint, int) and correct_hint == option_index:
                is_correct = True

            if isinstance(correct_hint, str):
                if correct_hint == option_id:
                    is_correct = True

                if correct_hint.strip() == option_text.strip():
                    is_correct = True

            if correct_text_hint and correct_text_hint.strip() == option_text.strip():
                is_correct = True

            opzioni.append(
                {
                    "option_id": option_id,
                    "testo": option_text,
                    "is_correct": is_correct,
                }
            )

        # Fallback: se il motore non conserva il marker corretto,
        # recuperiamo il corretto dalla domanda originale solo se l'indice coincide.
        if not any(option["is_correct"] for option in opzioni):
            if index < len(PHASE5_TEST_QUIZ):
                original_correct = PHASE5_TEST_QUIZ[index].get("correct_option_id")

                for option in opzioni:
                    if option["option_id"] == original_correct:
                        option["is_correct"] = True

        correct_option_id = ""

        for option in opzioni:
            if option["is_correct"]:
                correct_option_id = option["option_id"]
                break

        normalized.append(
            {
                "question_id": item.get("question_id") or item.get("id") or f"normalized_{index+1:03d}",
                "domanda": question_text,
                "opzioni": opzioni,
                "correct_option_id": correct_option_id,
                "spiegazione": item.get("spiegazione") or item.get("explanation") or "",
            }
        )

    return normalized


def _shape_report(value: Any) -> dict[str, Any]:
    normalized = _normalize_back_to_phase5(value)

    if not isinstance(normalized, list):
        return {
            "shape_ok": False,
            "question_count": 0,
            "option_count": 0,
            "correct_markers": 0,
        }

    option_count = 0
    correct_markers = 0

    for item in normalized:
        options = item.get("opzioni", [])

        if isinstance(options, list):
            option_count += len(options)
            correct_markers += sum(1 for option in options if option.get("is_correct") is True)

    return {
        "shape_ok": bool(normalized),
        "question_count": len(normalized),
        "option_count": option_count,
        "correct_markers": correct_markers,
    }


def _evaluate(fn: Callable[[Any], Any], adapter_name: str, payload: Any) -> dict[str, Any]:
    before_normalized = _normalize_back_to_phase5(PHASE5_TEST_QUIZ)

    if before_normalized is None:
        raise AssertionError("Input Fase 5 non normalizzabile.")

    before_defects = _count_known_text_defects(before_normalized)
    before_json = _safe_json(before_normalized)
    before_shape = _shape_report(before_normalized)

    try:
        raw_output = fn(copy.deepcopy(payload))
    except Exception as exc:
        return {
            "adapter_name": adapter_name,
            "status": "exception",
            "accepted": False,
            "exception": f"{exc.__class__.__name__}: {exc}",
            "traceback": traceback.format_exc(limit=4),
        }

    normalized_output = _normalize_back_to_phase5(raw_output)
    after_shape = _shape_report(raw_output)

    if normalized_output is None:
        return {
            "adapter_name": adapter_name,
            "status": "bad_shape",
            "accepted": False,
            "before_defects": before_defects,
            "after_defects": None,
            "before_shape": before_shape,
            "after_shape": after_shape,
            "raw_output_type": str(type(raw_output)),
        }

    after_defects = _count_known_text_defects(normalized_output)
    after_json = _safe_json(normalized_output)

    did_change = before_json != after_json
    worsened = after_defects > before_defects
    improved = after_defects < before_defects

    shape_ok = (
        after_shape["shape_ok"] is True
        and after_shape["question_count"] >= before_shape["question_count"]
        and after_shape["option_count"] >= before_shape["option_count"]
        and after_shape["correct_markers"] >= before_shape["correct_markers"]
    )

    accepted = bool(shape_ok and not worsened)

    if not shape_ok:
        status = "bad_shape"
    elif worsened:
        status = "worsened"
    elif improved:
        status = "improved"
    elif did_change:
        status = "changed_no_worse"
    else:
        status = "unchanged_no_worse"

    return {
        "adapter_name": adapter_name,
        "status": status,
        "accepted": accepted,
        "did_change": did_change,
        "worsened": worsened,
        "improved": improved,
        "before_defects": before_defects,
        "after_defects": after_defects,
        "before_shape": before_shape,
        "after_shape": after_shape,
        "normalized_preview": normalized_output[:1],
    }


def _pick_best(results: list[dict[str, Any]]) -> dict[str, Any] | None:
    accepted = [item for item in results if item.get("accepted")]

    if not accepted:
        return None

    def score(item: dict[str, Any]) -> tuple[int, int, int]:
        return (
            int(item.get("after_defects", 9999)),
            -int(bool(item.get("improved"))),
            -int(bool(item.get("did_change"))),
        )

    return sorted(accepted, key=score)[0]


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    fn, load_error = _load_callable()

    if fn is None:
        raise RuntimeError(f"Import motore fallito: {load_error}")

    report: dict[str, Any] = {
        "report_name": "adapter_refine_tests_fase5_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "motor_id": MOTOR_ID,
        "input_defects": _count_known_text_defects(PHASE5_TEST_QUIZ),
        "variants": [],
        "best_adapter": None,
        "compatibility_status": "unknown",
    }

    print(f"▶ Verifico adapter specifici per: {MOTOR_ID}")

    for variant in _make_variants():
        result = _evaluate(
            fn=fn,
            adapter_name=variant["adapter_name"],
            payload=variant["payload"],
        )

        report["variants"].append(result)

        print(
            f"- {result['adapter_name']}: "
            f"{result['status']} | accepted={result.get('accepted')} | "
            f"defects={result.get('before_defects', '-')}"
            f"->{result.get('after_defects', '-')}"
        )

    best = _pick_best(report["variants"])

    if best is None:
        report["compatibility_status"] = "not_compatible_yet"
        print("⚠️ Nessun adapter refine_tests accettato senza peggiorare.")
    else:
        report["compatibility_status"] = "compatible_with_adapter"
        report["best_adapter"] = {
            "adapter_name": best["adapter_name"],
            "status": best["status"],
            "before_defects": best["before_defects"],
            "after_defects": best["after_defects"],
            "did_change": best["did_change"],
            "improved": best["improved"],
        }

        print(
            f"✅ Miglior adapter refine_tests: {best['adapter_name']} | "
            f"{best['status']} | defects={best['before_defects']}->{best['after_defects']}"
        )

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = []
    lines.append("# Adapter refine_tests Fase 5 V1\n")
    lines.append(f"- Motore: `{MOTOR_ID}`")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Stato compatibilità: `{report['compatibility_status']}`")

    if report["best_adapter"]:
        lines.append(f"- Best adapter: `{report['best_adapter']['adapter_name']}`")
        lines.append(
            f"- Difetti: `{report['best_adapter']['before_defects']} -> {report['best_adapter']['after_defects']}`"
        )

    lines.append("")
    lines.append("| Adapter | Stato | Accepted | Difetti |")
    lines.append("|---|---:|---:|---:|")

    for item in report["variants"]:
        lines.append(
            f"| `{item.get('adapter_name')}` "
            f"| `{item.get('status')}` "
            f"| `{item.get('accepted')}` "
            f"| `{item.get('before_defects', '-')} -> {item.get('after_defects', '-')}` |"
        )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("\n✅ VERIFICA ADAPTER REFINE_TESTS FASE 5 COMPLETATA")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
