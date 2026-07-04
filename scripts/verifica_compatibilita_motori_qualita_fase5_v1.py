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


REPORT_JSON = ROOT / "reports" / "compatibilita_motori_qualita_fase5_v1.json"
REPORT_MD = ROOT / "reports" / "compatibilita_motori_qualita_fase5_v1.md"


MOTORS = [
    {
        "motor_id": "backend.main.pulisci_qualita_linguistica_quiz",
        "module": "backend.main",
        "function": "pulisci_qualita_linguistica_quiz",
        "kind": "legacy_live_quality_motor",
    },
    {
        "motor_id": "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests",
        "module": "scripts.rag_motore_didattico_riutilizzabile_v35c",
        "function": "refine_tests",
        "kind": "legacy_live_didactic_motor",
    },
]


CANONICAL_TEST_QUIZ = [
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
        "micro_concetti": [
            "protezione credenziali",
            "condivisione credenziali",
            "controllo accessi",
        ],
        "fonte_pagine": [1, 2],
    }
]


def _load_callable(module_name: str, function_name: str) -> tuple[Callable[[Any], Any] | None, str | None]:
    try:
        module = importlib.import_module(module_name)
        fn = getattr(module, function_name)
        if not callable(fn):
            return None, f"{module_name}.{function_name} non è callable"
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
        r"\buna una\b",
        r"\bun un\b",
        r"\bil il\b",
        r"\bla la\b",
    ]

    total = 0

    for pattern in patterns:
        total += len(re.findall(pattern, text, flags=re.IGNORECASE))

    return total


def _safe_json(value: Any) -> str:
    try:
        return json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
    except Exception:
        return repr(value)


def _extract_quiz_like_output(value: Any) -> Any:
    """
    Estrae una lista quiz da output diversi.

    Serve perché i motori vecchi possono restituire:
    - direttamente una lista;
    - un dict con test_quiz;
    - un dict con quiz;
    - un dict con tests;
    - un dict con questions;
    - un dict con output annidato.
    """
    if isinstance(value, list):
        return value

    if not isinstance(value, dict):
        return value

    preferred_keys = [
        "test_quiz",
        "quiz",
        "quiz_draft",
        "tests",
        "test",
        "questions",
        "domande_quiz",
        "items",
    ]

    for key in preferred_keys:
        child = value.get(key)
        if isinstance(child, list):
            return child

    for child in value.values():
        if isinstance(child, dict):
            extracted = _extract_quiz_like_output(child)
            if isinstance(extracted, list):
                return extracted

    return value


def _is_option_dict(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    return bool(keys & {"testo", "text", "label", "value", "is_correct", "correct"})


def _is_question_dict(value: Any) -> bool:
    if not isinstance(value, dict):
        return False

    keys = {str(k).lower() for k in value.keys()}

    has_question = bool(keys & {"domanda", "question", "prompt", "title"})
    has_options = bool(keys & {"opzioni", "options", "answers", "risposte"})
    has_answer = bool(keys & {"correct_option_id", "answer", "correct_answer", "risposta_corretta"})

    if has_question and (has_options or has_answer):
        return True

    options = value.get("opzioni", value.get("options"))

    if isinstance(options, list) and any(_is_option_dict(item) for item in options):
        return True

    return False


def _quiz_shape_report(value: Any) -> dict[str, Any]:
    extracted = _extract_quiz_like_output(value)

    if not isinstance(extracted, list):
        return {
            "is_quiz_list": False,
            "question_count": 0,
            "option_count": 0,
            "correct_markers": 0,
        }

    question_items = [item for item in extracted if isinstance(item, dict)]
    valid_questions = [item for item in question_items if _is_question_dict(item)]

    option_count = 0
    correct_markers = 0

    for question in valid_questions:
        options = question.get("opzioni", question.get("options", []))

        if isinstance(options, list):
            option_count += len(options)

            for option in options:
                if isinstance(option, dict) and option.get("is_correct") is True:
                    correct_markers += 1

    return {
        "is_quiz_list": bool(valid_questions),
        "question_count": len(valid_questions),
        "option_count": option_count,
        "correct_markers": correct_markers,
    }


def _make_candidate_payloads(test_quiz: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Formati provati per rendere compatibili i motori vecchi.

    direct_list:
      passa la lista pura.

    dict_test_quiz:
      formato nuovo Fase 5.

    dict_quiz:
      formato generico quiz.

    dict_legacy_questions:
      formato vecchio generico con questions.

    dict_full_phase5_output:
      simula output completo della Fase 5.
    """
    return [
        {
            "adapter_name": "direct_list",
            "payload": copy.deepcopy(test_quiz),
        },
        {
            "adapter_name": "dict_test_quiz",
            "payload": {
                "test_quiz": copy.deepcopy(test_quiz),
            },
        },
        {
            "adapter_name": "dict_quiz",
            "payload": {
                "quiz": copy.deepcopy(test_quiz),
            },
        },
        {
            "adapter_name": "dict_tests",
            "payload": {
                "tests": copy.deepcopy(test_quiz),
            },
        },
        {
            "adapter_name": "dict_legacy_questions",
            "payload": {
                "questions": copy.deepcopy(test_quiz),
            },
        },
        {
            "adapter_name": "dict_full_phase5_output",
            "payload": {
                "document_id": "compatibilita_motori_qualita_fase5_v1",
                "phase_name": "QUALITY_STUDY_QUIZ",
                "approved": True,
                "status": "APPROVED",
                "test_quiz": copy.deepcopy(test_quiz),
                "quiz": copy.deepcopy(test_quiz),
                "warnings": [],
                "errors": [],
            },
        },
    ]


def _evaluate_candidate(
    *,
    fn: Callable[[Any], Any],
    motor_id: str,
    adapter_name: str,
    payload: Any,
    original_quiz: list[dict[str, Any]],
) -> dict[str, Any]:
    before_defects = _count_known_text_defects(original_quiz)
    before_shape = _quiz_shape_report(original_quiz)

    before_json = _safe_json(original_quiz)

    try:
        raw_output = fn(copy.deepcopy(payload))
        exception = None
    except Exception as exc:
        return {
            "adapter_name": adapter_name,
            "status": "exception",
            "exception": f"{exc.__class__.__name__}: {exc}",
            "traceback": traceback.format_exc(limit=3),
            "accepted": False,
        }

    extracted_output = _extract_quiz_like_output(raw_output)

    after_defects = _count_known_text_defects(extracted_output)
    after_shape = _quiz_shape_report(extracted_output)
    after_json = _safe_json(extracted_output)

    shape_ok = (
        after_shape["is_quiz_list"] is True
        and after_shape["question_count"] >= before_shape["question_count"]
        and after_shape["option_count"] >= before_shape["option_count"]
        and after_shape["correct_markers"] >= before_shape["correct_markers"]
    )

    did_change = before_json != after_json
    worsened = after_defects > before_defects
    improved = after_defects < before_defects

    accepted = bool(shape_ok and not worsened)

    status = "accepted"

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
        "improved": improved,
        "worsened": worsened,
        "before_defects": before_defects,
        "after_defects": after_defects,
        "before_shape": before_shape,
        "after_shape": after_shape,
        "output_preview": extracted_output[:1] if isinstance(extracted_output, list) else str(type(extracted_output)),
    }


def _pick_best_candidate(candidates: list[dict[str, Any]]) -> dict[str, Any] | None:
    accepted = [item for item in candidates if item.get("accepted")]

    if not accepted:
        return None

    def score(item: dict[str, Any]) -> tuple[int, int, int]:
        after_defects = int(item.get("after_defects", 9999))
        did_change = 1 if item.get("did_change") else 0
        improved = 1 if item.get("improved") else 0

        # Priorità:
        # 1. meno difetti;
        # 2. se migliora, meglio;
        # 3. se cambia senza peggiorare, meglio di niente.
        return (
            after_defects,
            -improved,
            -did_change,
        )

    return sorted(accepted, key=score)[0]


def main() -> int:
    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)

    report: dict[str, Any] = {
        "report_name": "compatibilita_motori_qualita_fase5_v1",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "root": str(ROOT),
        "input_defects": _count_known_text_defects(CANONICAL_TEST_QUIZ),
        "input_shape": _quiz_shape_report(CANONICAL_TEST_QUIZ),
        "motors": [],
    }

    for motor in MOTORS:
        motor_id = motor["motor_id"]
        print(f"\n▶ Verifico motore: {motor_id}")

        fn, load_error = _load_callable(motor["module"], motor["function"])

        motor_report: dict[str, Any] = {
            **motor,
            "load_status": "ok" if fn else "failed_import",
            "load_error": load_error,
            "candidates": [],
            "best_adapter": None,
            "compatibility_status": "failed_import" if not fn else "unknown",
        }

        if fn is None:
            print(f"  ❌ Import fallito: {load_error}")
            report["motors"].append(motor_report)
            continue

        for candidate in _make_candidate_payloads(CANONICAL_TEST_QUIZ):
            result = _evaluate_candidate(
                fn=fn,
                motor_id=motor_id,
                adapter_name=candidate["adapter_name"],
                payload=candidate["payload"],
                original_quiz=CANONICAL_TEST_QUIZ,
            )

            motor_report["candidates"].append(result)

            print(
                f"  - {result['adapter_name']}: "
                f"{result['status']} | accepted={result.get('accepted')} | "
                f"defects={result.get('before_defects', '-')}"
                f"->{result.get('after_defects', '-')}"
            )

        best = _pick_best_candidate(motor_report["candidates"])

        if best is None:
            motor_report["compatibility_status"] = "not_compatible_yet"
            print("  ⚠️ Nessun adapter accettato senza peggiorare.")
        else:
            motor_report["compatibility_status"] = "compatible_with_adapter"
            motor_report["best_adapter"] = {
                "adapter_name": best["adapter_name"],
                "status": best["status"],
                "before_defects": best["before_defects"],
                "after_defects": best["after_defects"],
                "did_change": best["did_change"],
                "improved": best["improved"],
            }

            print(
                f"  ✅ Miglior adapter: {best['adapter_name']} | "
                f"{best['status']} | defects={best['before_defects']}->{best['after_defects']}"
            )

        report["motors"].append(motor_report)

    REPORT_JSON.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines: list[str] = []
    lines.append("# Compatibilità motori qualità Fase 5 V1\n")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Difetti input: `{report['input_defects']}`")
    lines.append(f"- Shape input: `{report['input_shape']}`")
    lines.append("")

    for motor in report["motors"]:
        lines.append(f"## {motor['motor_id']}")
        lines.append("")
        lines.append(f"- Import: `{motor['load_status']}`")
        lines.append(f"- Stato compatibilità: `{motor['compatibility_status']}`")

        if motor.get("best_adapter"):
            lines.append(f"- Best adapter: `{motor['best_adapter']['adapter_name']}`")
            lines.append(
                f"- Difetti: `{motor['best_adapter']['before_defects']} -> {motor['best_adapter']['after_defects']}`"
            )

        lines.append("")
        lines.append("| Adapter | Stato | Accepted | Difetti |")
        lines.append("|---|---:|---:|---:|")

        for candidate in motor.get("candidates", []):
            lines.append(
                f"| `{candidate.get('adapter_name')}` "
                f"| `{candidate.get('status')}` "
                f"| `{candidate.get('accepted')}` "
                f"| `{candidate.get('before_defects', '-')} -> {candidate.get('after_defects', '-')}` |"
            )

        lines.append("")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("\n✅ VERIFICA COMPATIBILITÀ MOTORI QUALITÀ FASE 5 COMPLETATA")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
