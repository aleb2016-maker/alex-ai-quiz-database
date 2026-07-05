from __future__ import annotations

import copy
import importlib
import json
import re
import sys
import traceback
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


INSPECTION_JSON = ROOT / "reports" / "phase5_9_6_quiz_motor_compatibility_inspection_v1.json"
REPORT_JSON = ROOT / "reports" / "phase5_9_7_quiz_motor_runtime_test_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_9_7_quiz_motor_runtime_test_v1.md"


from scripts.verifica_phase5_8_quality_delta_ready_safe_motors_v1 import build_dirty_payload
from backend.phase5_quiz_true_distractor_repair_v1 import count_true_fact_distractors_v1


MECHANICAL_QUESTION_PATTERNS = [
    r"quale affermazione è supportata dal documento",
    r"quale regola o informazione emerge da",
    r"il documento dice che",
]

ROUGH_EXPLANATION_PATTERNS = [
    r"bozza",
    r"draft",
    r"macro-grezzo",
    r"non non",
    r"perchè",
    r"qual e",
]

SIDE_EFFECT_ARG_NAMES = {
    "percorso",
    "path",
    "file_path",
    "filename",
    "output_path",
}


# FASE 5.9.7.1 — RUNTIME SIDE EFFECT GUARD
# Il runtime test deve misurare i candidati, non modificare file reali.
# Questo candidato ha già scritto su data/espansione/batch_100.json e scripts/create_batch_100.py.
RUNTIME_SIDE_EFFECT_DENYLIST = {
    "scripts.improve_answer_options_100.applica_miglioramenti",
}

RUNTIME_SIDE_EFFECT_PATH_DENYLIST = {
    "scripts/improve_answer_options_100.py",
}


def normalize_text(value: Any) -> str:
    text = str(value or "").strip().lower()
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def quiz_from_payload(payload: Dict[str, Any]) -> List[Dict[str, Any]]:
    for key in ["test_quiz", "quiz_draft", "quiz", "domande_quiz", "tests"]:
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return []


def quiz_options(question: Dict[str, Any]) -> List[Dict[str, Any]]:
    value = question.get("opzioni")
    if isinstance(value, list):
        return value

    value = question.get("options")
    if isinstance(value, list):
        return value

    return []


def question_text(question: Dict[str, Any]) -> str:
    return str(question.get("domanda") or question.get("question") or "")


def explanation_text(question: Dict[str, Any]) -> str:
    return str(
        question.get("spiegazione")
        or question.get("explanation")
        or question.get("explanation_draft")
        or ""
    )


def option_text(option: Dict[str, Any]) -> str:
    return str(option.get("testo") or option.get("text") or "")


def correct_option_text(question: Dict[str, Any]) -> str:
    correct_id = question.get("correct_option_id")

    for option in quiz_options(question):
        if option.get("is_correct") is True or option.get("option_id") == correct_id:
            return option_text(option)

    return ""


def source_facts(question: Dict[str, Any]) -> List[str]:
    facts = question.get("source_facts")

    if isinstance(facts, list):
        return [str(item) for item in facts if str(item).strip()]

    return []


def count_mechanical_questions(quiz: List[Dict[str, Any]]) -> int:
    count = 0

    for question in quiz:
        text = normalize_text(question_text(question))

        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in MECHANICAL_QUESTION_PATTERNS):
            count += 1

    return count


def count_duplicate_questions(quiz: List[Dict[str, Any]]) -> int:
    texts = [
        normalize_text(question_text(question))
        for question in quiz
        if normalize_text(question_text(question))
    ]

    return len(texts) - len(set(texts))


def count_rough_explanations(quiz: List[Dict[str, Any]]) -> int:
    count = 0

    for question in quiz:
        text = normalize_text(explanation_text(question))

        if any(re.search(pattern, text, flags=re.IGNORECASE) for pattern in ROUGH_EXPLANATION_PATTERNS):
            count += 1

    return count


def count_empty_explanations(quiz: List[Dict[str, Any]]) -> int:
    return sum(1 for question in quiz if not explanation_text(question).strip())


def count_correct_options_errors(quiz: List[Dict[str, Any]]) -> int:
    errors = 0

    for question in quiz:
        correct_id = question.get("correct_option_id")
        count = 0

        for option in quiz_options(question):
            if option.get("is_correct") is True or option.get("option_id") == correct_id:
                count += 1

        if count != 1:
            errors += 1

    return errors


def count_option_count_errors(quiz: List[Dict[str, Any]]) -> int:
    errors = 0

    for question in quiz:
        options = quiz_options(question)

        if len(options) != 4:
            errors += 1

    return errors


def quiz_metrics(quiz: List[Dict[str, Any]]) -> Dict[str, int]:
    return {
        "questions_count": len(quiz),
        "true_fact_distractors": count_true_fact_distractors_v1(quiz),
        "mechanical_questions": count_mechanical_questions(quiz),
        "duplicate_questions": count_duplicate_questions(quiz),
        "rough_explanations": count_rough_explanations(quiz),
        "empty_explanations": count_empty_explanations(quiz),
        "correct_options_errors": count_correct_options_errors(quiz),
        "option_count_errors": count_option_count_errors(quiz),
    }


def bad_total(metrics: Dict[str, int]) -> int:
    return (
        metrics["true_fact_distractors"]
        + metrics["mechanical_questions"]
        + metrics["duplicate_questions"]
        + metrics["rough_explanations"]
        + metrics["empty_explanations"]
        + metrics["correct_options_errors"] * 3
        + metrics["option_count_errors"] * 3
    )


def extract_quiz_candidate(value: Any) -> Optional[List[Dict[str, Any]]]:
    if isinstance(value, tuple) and value:
        return extract_quiz_candidate(value[0])

    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        # Se sembra lista domande quiz.
        if any(("question" in item or "domanda" in item) for item in value):
            return value

    if isinstance(value, dict):
        for key in ["test_quiz", "quiz_draft", "quiz", "domande_quiz", "tests"]:
            candidate = value.get(key)
            if isinstance(candidate, list):
                return extract_quiz_candidate(candidate)

        # Alcune funzioni ritornano {"domande": [...]}
        for key in ["domande", "questions"]:
            candidate = value.get(key)
            if isinstance(candidate, list):
                return extract_quiz_candidate(candidate)

    return None


def import_function(motor_id: str) -> Callable[..., Any]:
    module_name, function_name = motor_id.rsplit(".", 1)
    module = importlib.import_module(module_name)
    fn = getattr(module, function_name)

    if not callable(fn):
        raise TypeError(f"Oggetto non callable: {motor_id}")

    return fn


def build_inputs_for_candidate(
    args: List[str],
    payload: Dict[str, Any],
) -> List[Tuple[str, Tuple[Any, ...]]]:
    quiz = quiz_from_payload(payload)
    first_question = quiz[0] if quiz else {}
    options = quiz_options(first_question)
    correct = correct_option_text(first_question)

    attempts: List[Tuple[str, Tuple[Any, ...]]] = []

    # Evito funzioni che sembrano voler leggere file.
    if any(arg in SIDE_EFFECT_ARG_NAMES for arg in args):
        return []

    if len(args) == 1:
        arg = args[0]

        if arg in {"payload", "output", "output_result", "data", "dati_quiz"}:
            attempts.append(("payload", (copy.deepcopy(payload),)))

        elif arg in {"quiz", "domande", "questions", "domande_analizzate"}:
            attempts.append(("quiz", (copy.deepcopy(quiz),)))

        elif arg in {"domanda", "question"}:
            attempts.append(("question", (copy.deepcopy(first_question),)))

        elif arg in {"opzioni", "options", "opzioni_grezze"}:
            attempts.append(("options", (copy.deepcopy(options),)))

        elif arg in {"spiegazione", "explanation", "value", "testo"}:
            attempts.append(("text", (explanation_text(first_question) or question_text(first_question),)))

        else:
            attempts.append(("payload_generic", (copy.deepcopy(payload),)))
            attempts.append(("quiz_generic", (copy.deepcopy(quiz),)))
            attempts.append(("question_generic", (copy.deepcopy(first_question),)))

    elif len(args) == 2:
        a, b = args

        if {a, b} == {"indice", "domanda"}:
            if a == "indice":
                attempts.append(("index_question", (0, copy.deepcopy(first_question))))
            else:
                attempts.append(("question_index", (copy.deepcopy(first_question), 0)))

        elif {a, b} == {"opzioni", "risposta"} or {a, b} == {"options", "risposta"}:
            if a in {"opzioni", "options"}:
                attempts.append(("options_correct", (copy.deepcopy(options), correct)))
            else:
                attempts.append(("correct_options", (correct, copy.deepcopy(options))))

        elif a in {"data", "value", "output"}:
            attempts.append(("payload_original", (copy.deepcopy(payload), copy.deepcopy(payload))))

        elif a in {"domande", "domande_analizzate", "questions"}:
            attempts.append(("quiz_threshold", (copy.deepcopy(quiz), 0.75)))

        else:
            attempts.append(("payload_payload", (copy.deepcopy(payload), copy.deepcopy(payload))))
            attempts.append(("quiz_index", (copy.deepcopy(quiz), 0)))

    elif len(args) == 3:
        if args == ["nome_motore", "indice", "domanda"]:
            attempts.append(("name_index_question", ("phase5_9_7", 0, copy.deepcopy(first_question))))

        elif args == ["domande", "categoria", "sottocategoria"]:
            attempts.append(("quiz_category_subcategory", (copy.deepcopy(quiz), "cybersecurity", "accessi")))

        elif args == ["title", "correct", "idx"]:
            attempts.append(("title_correct_idx", ("Controllo accessi", correct, 0)))

        else:
            attempts.append(("quiz_category_subcategory_generic", (copy.deepcopy(quiz), "cybersecurity", "accessi")))

    return attempts


def evaluate_output(
    before_quiz: List[Dict[str, Any]],
    output: Any,
) -> Dict[str, Any]:
    candidate_quiz = extract_quiz_candidate(output)

    if candidate_quiz is None:
        return {
            "usable_quiz_output": False,
            "after_metrics": None,
            "improved": False,
            "worsened": False,
            "neutral": True,
            "bad_total_before": bad_total(quiz_metrics(before_quiz)),
            "bad_total_after": None,
            "notes": ["Output non riconosciuto come quiz riutilizzabile."],
        }

    before_metrics = quiz_metrics(before_quiz)
    after_metrics = quiz_metrics(candidate_quiz)

    before_bad = bad_total(before_metrics)
    after_bad = bad_total(after_metrics)

    improved = after_bad < before_bad
    worsened = after_bad > before_bad

    # Peggioramento strutturale sempre grave.
    if after_metrics["correct_options_errors"] > before_metrics["correct_options_errors"]:
        worsened = True

    if after_metrics["option_count_errors"] > before_metrics["option_count_errors"]:
        worsened = True

    notes: List[str] = []

    for key in [
        "true_fact_distractors",
        "mechanical_questions",
        "duplicate_questions",
        "rough_explanations",
        "empty_explanations",
    ]:
        if after_metrics[key] < before_metrics[key]:
            notes.append(f"Migliora {key}: {before_metrics[key]} -> {after_metrics[key]}")
        elif after_metrics[key] > before_metrics[key]:
            notes.append(f"Peggiora {key}: {before_metrics[key]} -> {after_metrics[key]}")

    if not notes:
        notes.append("Nessun delta misurabile sulle metriche quiz.")

    return {
        "usable_quiz_output": True,
        "after_metrics": after_metrics,
        "improved": improved and not worsened,
        "worsened": worsened,
        "neutral": not improved and not worsened,
        "bad_total_before": before_bad,
        "bad_total_after": after_bad,
        "notes": notes,
    }


def test_candidate(item: Dict[str, Any]) -> Dict[str, Any]:
    motor_id = item.get("motor_id")
    args = item.get("signature", {}).get("args", [])

    payload = build_dirty_payload()
    before_quiz = quiz_from_payload(payload)
    before_metrics = quiz_metrics(before_quiz)

    result: Dict[str, Any] = {
        "motor_id": motor_id,
        "path": item.get("path"),
        "function_name": item.get("function_name"),
        "lineno": item.get("lineno"),
        "args": args,
        "before_metrics": before_metrics,
        "status": "NOT_RUN",
        "attempts": [],
        "best_result": None,
        "runtime_error": None,
    }

    if str(motor_id) in RUNTIME_SIDE_EFFECT_DENYLIST or str(item.get("path") or "") in RUNTIME_SIDE_EFFECT_PATH_DENYLIST:
        result["status"] = "SKIPPED_RUNTIME_SIDE_EFFECT_RISK"
        result["runtime_error"] = "Candidato saltato: rischio effetti collaterali su file reali."
        return result

    attempts = build_inputs_for_candidate(args, payload)

    if not attempts:
        result["status"] = "SKIPPED_UNSAFE_OR_UNSUPPORTED_ARGS"
        return result

    try:
        fn = import_function(str(motor_id))
    except Exception as exc:
        result["status"] = "IMPORT_ERROR"
        result["runtime_error"] = f"{type(exc).__name__}: {exc}"
        return result

    best = None

    for adapter_name, call_args in attempts:
        attempt_result: Dict[str, Any] = {
            "adapter_name": adapter_name,
            "status": "PENDING",
            "error": None,
            "evaluation": None,
        }

        try:
            output = fn(*call_args)
            evaluation = evaluate_output(before_quiz, output)
            attempt_result["status"] = "OK"
            attempt_result["evaluation"] = evaluation

            if best is None:
                best = attempt_result
            else:
                current_after = evaluation.get("bad_total_after")
                best_after = best.get("evaluation", {}).get("bad_total_after")

                if current_after is not None and (best_after is None or current_after < best_after):
                    best = attempt_result

        except Exception as exc:
            attempt_result["status"] = "ERROR"
            attempt_result["error"] = {
                "type": type(exc).__name__,
                "message": str(exc),
                "traceback_tail": traceback.format_exc(limit=2),
            }

        result["attempts"].append(attempt_result)

    result["best_result"] = best

    if best is None:
        result["status"] = "RUNTIME_ERROR"
    else:
        evaluation = best.get("evaluation") or {}

        if evaluation.get("worsened"):
            result["status"] = "WORSENED"
        elif evaluation.get("improved"):
            result["status"] = "IMPROVED"
        elif evaluation.get("usable_quiz_output"):
            result["status"] = "NEUTRAL_USABLE_OUTPUT"
        else:
            result["status"] = "NO_USABLE_OUTPUT"

    return result


def main() -> int:
    if not INSPECTION_JSON.exists():
        raise FileNotFoundError(f"Report 5.9.6 non trovato: {INSPECTION_JSON}")

    inspection = json.loads(INSPECTION_JSON.read_text(encoding="utf-8"))
    candidates = inspection.get("compat_test_ready") or []

    results = [test_candidate(item) for item in candidates]

    buckets: Dict[str, List[Dict[str, Any]]] = {}

    for item in results:
        buckets.setdefault(item["status"], []).append(item)

    counts = {key: len(value) for key, value in sorted(buckets.items())}

    improved = buckets.get("IMPROVED", [])
    neutral = buckets.get("NEUTRAL_USABLE_OUTPUT", [])
    no_output = buckets.get("NO_USABLE_OUTPUT", [])
    worsened = buckets.get("WORSENED", [])
    errors = buckets.get("RUNTIME_ERROR", []) + buckets.get("IMPORT_ERROR", [])

    report = {
        "report_name": "phase5_9_7_quiz_motor_runtime_test_v1",
        "status": "PASS_DIAGNOSTIC" if not worsened else "PASS_WITH_WORSENING_CANDIDATES",
        "input_candidates": len(candidates),
        "counts": counts,
        "improved_candidates": improved,
        "neutral_usable_candidates": neutral,
        "no_usable_output_candidates": no_output,
        "worsened_candidates": worsened,
        "error_candidates": errors,
        "all_results": results,
        "recommended_next_phase": {
            "phase": "5.9.8",
            "action": "Portare a compatibilità registry solo candidati IMPROVED e senza peggioramenti.",
        },
        "notes": [
            "Runtime test controllato: non collega candidati al registry.",
            "Ogni candidato viene provato con wrapper basati sulla firma.",
            "Un candidato utile deve produrre output quiz riutilizzabile e ridurre metriche problematiche.",
            "I candidati neutri possono essere utili solo con adapter migliore, ma non vanno collegati ora.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines: List[str] = []
    lines.append("# Fase 5.9.7 — Quiz Motor Runtime Test V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Candidati runtime testati: `{len(candidates)}`")
    lines.append("")
    lines.append("## Conteggi\n")
    lines.append("| Status | Conteggio |")
    lines.append("|---|---:|")

    for key, value in counts.items():
        lines.append(f"| `{key}` | {value} |")

    lines.append("")
    lines.append("## IMPROVED\n")
    lines.append("| Motore | Adapter migliore | Bad total | Note |")
    lines.append("|---|---|---|---|")

    for item in improved:
        best = item.get("best_result") or {}
        evaluation = best.get("evaluation") or {}
        lines.append(
            f"| `{item.get('motor_id')}` "
            f"| `{best.get('adapter_name')}` "
            f"| `{evaluation.get('bad_total_before')} -> {evaluation.get('bad_total_after')}` "
            f"| {'; '.join(evaluation.get('notes') or [])} |"
        )

    lines.append("")
    lines.append("## NEUTRAL_USABLE_OUTPUT\n")
    lines.append("| Motore | Adapter migliore | Bad total | Note |")
    lines.append("|---|---|---|---|")

    for item in neutral[:30]:
        best = item.get("best_result") or {}
        evaluation = best.get("evaluation") or {}
        lines.append(
            f"| `{item.get('motor_id')}` "
            f"| `{best.get('adapter_name')}` "
            f"| `{evaluation.get('bad_total_before')} -> {evaluation.get('bad_total_after')}` "
            f"| {'; '.join(evaluation.get('notes') or [])} |"
        )

    lines.append("")
    lines.append("## NO_USABLE_OUTPUT / ERROR\n")
    lines.append("| Status | Motore | Note |")
    lines.append("|---|---|---|")

    for item in (no_output + errors)[:40]:
        best = item.get("best_result") or {}
        evaluation = best.get("evaluation") or {}
        note = "; ".join(evaluation.get("notes") or [])
        err = item.get("runtime_error") or ""
        lines.append(
            f"| `{item.get('status')}` "
            f"| `{item.get('motor_id')}` "
            f"| {note or err} |"
        )

    if worsened:
        lines.append("")
        lines.append("## WORSENED\n")
        lines.append("| Motore | Note |")
        lines.append("|---|---|")

        for item in worsened:
            best = item.get("best_result") or {}
            evaluation = best.get("evaluation") or {}
            lines.append(
                f"| `{item.get('motor_id')}` "
                f"| {'; '.join(evaluation.get('notes') or [])} |"
            )

    lines.append("")
    lines.append("## Prossimo step\n")
    lines.append("- Collegare solo candidati `IMPROVED`, se presenti.")
    lines.append("- I candidati `NEUTRAL_USABLE_OUTPUT` richiedono adapter migliore o test più specifico.")
    lines.append("- I candidati `NO_USABLE_OUTPUT` non sono collegabili direttamente.")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.9.7 QUIZ MOTOR RUNTIME TEST COMPLETATA")
    print(json.dumps(counts, ensure_ascii=False, indent=2))
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
