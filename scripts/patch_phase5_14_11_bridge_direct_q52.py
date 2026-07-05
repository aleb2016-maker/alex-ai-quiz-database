#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "scripts" / "run_phase5_14_3_local_backend_bridge.py"

text = BRIDGE.read_text(encoding="utf-8")

start = text.find("def build_study_quiz_result(text: str) -> Dict[str, Any]:")
end = text.find("def generate_study(text: str) -> Dict[str, Any]:", start)

if start < 0 or end < 0:
    raise SystemExit("FAIL - build_study_quiz_result non trovata")

new_block = r'''def build_study_quiz_result(text: str) -> Dict[str, Any]:
    """
    FASE 5.14.11 — DIRECT Q52 UI BRIDGE

    La UI parte da testo grezzo.
    Qui NON passiamo più da q5_extract_facts_from_gate.
    Costruiamo facts stringa e chiamiamo direttamente i builder q52 reali:
    - q52_build_quality_study_questions
    - q52_build_quality_quiz
    - q52_validate_study_questions
    - q52_validate_quiz
    """
    module = import_backend_module()

    facts: List[str] = []

    for item in make_bridge_facts_from_raw_text(text):
        if isinstance(item, dict):
            value = (
                item.get("text")
                or item.get("testo")
                or item.get("fatto")
                or item.get("fact")
                or item.get("content")
                or item.get("sentence")
            )
        else:
            value = str(item)

        value = str(value or "").strip()
        if value and value not in facts:
            facts.append(value)

    if not facts:
        facts = split_real_sentences(text)

    facts = [str(f).strip() for f in facts if str(f).strip()]

    if not facts:
        raise RuntimeError("Nessun fact stringa estratto dal testo reale UI.")

    concepts = extract_micro_concepts(text)
    pages = [1]

    Config = getattr(module, "Phase5StudyQuizConfig")
    Result = getattr(module, "Phase5QualityStudyQuizResult")

    cfg = Config(
        max_study_questions=4,
        max_quiz_questions=4,
        quiz_options_count=4,
        max_fact_chars=700,
        max_micro_concepts_per_item=5,
        require_phase4_study_quiz_not_blocked=False,
    )

    result = Result(document_id="phase5_14_ui_real_text")
    result.phase_name = "QUALITY_STUDY_QUIZ_UI_BRIDGE_Q52"

    result.domande_studio = module.q52_build_quality_study_questions(
        facts=facts,
        preferred_concepts=concepts,
        pages=pages,
        config=cfg,
    )

    result.test_quiz = module.q52_build_quality_quiz(
        facts=facts,
        preferred_concepts=concepts,
        pages=pages,
        config=cfg,
    )

    try:
        from backend.phase5_quiz_options_repair_v513d3 import repair_test_quiz_options_v513d3
    except ModuleNotFoundError:
        from phase5_quiz_options_repair_v513d3 import repair_test_quiz_options_v513d3

    result.test_quiz = repair_test_quiz_options_v513d3(result.test_quiz)

    result.errors.extend(module.q52_validate_study_questions(result.domande_studio))
    result.errors.extend(module.q52_validate_quiz(result.test_quiz, facts, cfg.quiz_options_count))

    if not result.domande_studio:
        result.errors.append("PHASE5_STUDY_QUESTIONS_EMPTY")

    if not result.test_quiz:
        result.errors.append("PHASE5_TEST_QUIZ_EMPTY")

    result.approved = not result.errors
    result.status = "APPROVED" if result.approved else "QUALITY_BLOCKED"

    result.quality_report = {
        "phase": "5.14.11",
        "bridge": "direct_q52_ui_bridge",
        "motor_path": "q52_build_quality_study_questions + q52_build_quality_quiz",
        "facts_count": len(facts),
        "concepts_count": len(concepts),
        "study_questions_count": len(result.domande_studio),
        "quiz_questions_count": len(result.test_quiz),
        "strict_no_fallback": True,
    }

    plain = to_plain(result)

    if result.errors:
        raise RuntimeError(f"Direct Q52 bridge ha prodotto errori: {result.errors}")

    return {
        "motor_name": "direct_q52_ui_bridge_v51411",
        "raw": plain,
    }


'''

text = text[:start] + new_block + text[end:]

BRIDGE.write_text(text, encoding="utf-8")
print("PASS - Fase 5.14.11: bridge study/quiz passa direttamente ai builder q52 reali")
