from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "backend" / "legacy_quality_motor_registry_v1.py"

MARKER = "# FASE 5.6 — READY SAFE LEGACY MOTORS V1"

READY_SAFE_SPECS = '''
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
'''


def main() -> int:
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Registry non trovato: {REGISTRY}")

    text = REGISTRY.read_text(encoding="utf-8")

    if MARKER in text:
        print("ℹ️ Fase 5.6 già presente nel registry: non duplico.")
        return 0

    anchor = 'LEGACY_QUALITY_MOTORS: list[LegacyMotorSpec] = [\n'

    if anchor not in text:
        raise SystemExit("Anchor LEGACY_QUALITY_MOTORS non trovato.")

    text = text.replace(anchor, anchor + READY_SAFE_SPECS, 1)

    # Estende i target summary/study/full-output senza rompere i quiz già collegati.
    replacements = {
        '''QUIZ_TARGET_KEYS = {
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
''': '''QUIZ_TARGET_KEYS = {
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
''',
        '''def _candidate_quiz_targets(payload: Any) -> list[tuple[Any, str | None, Any, str]]:
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
''': '''def _candidate_quiz_targets(payload: Any) -> list[tuple[Any, str | None, Any, str]]:
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
''',
        '''        targets = _candidate_quiz_targets(result)
''': '''        targets = _candidate_targets_for_kind(result, spec.target_kind)
''',
        '''    return fn(copy.deepcopy(value))
''': '''    if spec.adapter_name in {"summary_dict", "cards_list", "phase5_full_output"}:
        return fn(copy.deepcopy(value))

    return fn(copy.deepcopy(value))
''',
    }

    for old, new in replacements.items():
        if old not in text:
            raise SystemExit(f"Blocco non trovato per patch 5.6:\\n{old[:120]}")

        text = text.replace(old, new, 1)

    REGISTRY.write_text(text, encoding="utf-8")

    print(f"✅ Fase 5.6 READY_SAFE motors aggiunta a: {REGISTRY}")
    print("✅ PATCH FASE 5.6 READY SAFE LEGACY MOTORS COMPLETATA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
