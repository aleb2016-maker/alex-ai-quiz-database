from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "backend" / "legacy_quality_motor_registry_v1.py"
QUIZ_REPAIR = ROOT / "backend" / "phase5_quiz_true_distractor_repair_v1.py"

REGISTRY_MARKER = "# FASE 5.9.3 — QUIZ TRUE DISTRACTOR REPAIR REGISTRY V1"
WRAPPER_MARKER = "# FASE 5.9.3 — REGISTRY WRAPPER V1"


WRAPPER_CODE = '''

# FASE 5.9.3 — REGISTRY WRAPPER V1
# Wrapper per il registry: riceve direttamente una lista quiz e restituisce solo
# la lista riparata, senza metadata tuple. I metadata restano disponibili nei
# test separati del motore.
def repair_quiz_target_v1(quiz: Any) -> Any:
    repaired, _meta = repair_quiz_true_distractors_v1(quiz)
    return repaired
'''


REGISTRY_SPEC = '''    # FASE 5.9.3 — QUIZ TRUE DISTRACTOR REPAIR REGISTRY V1
    # Motore quiz-specifico validato separatamente in Fase 5.9.2.
    # Obiettivo: sostituire distrattori falsi che coincidono con source_facts veri.
    LegacyMotorSpec(
        motor_id="backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1",
        module_name="backend.phase5_quiz_true_distractor_repair_v1",
        function_name="repair_quiz_target_v1",
        adapter_name="quiz_list",
        target_kind="quiz",
    ),
'''


def patch_quiz_repair_wrapper() -> None:
    if not QUIZ_REPAIR.exists():
        raise FileNotFoundError(f"Motore quiz repair non trovato: {QUIZ_REPAIR}")

    text = QUIZ_REPAIR.read_text(encoding="utf-8")

    if WRAPPER_MARKER in text:
        print("ℹ️ Wrapper registry già presente nel motore quiz repair.")
        return

    text = text.rstrip() + WRAPPER_CODE + "\n"

    QUIZ_REPAIR.write_text(text, encoding="utf-8")

    print(f"✅ Wrapper registry aggiunto a: {QUIZ_REPAIR}")


def patch_registry_spec() -> None:
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Registry non trovato: {REGISTRY}")

    text = REGISTRY.read_text(encoding="utf-8")

    if REGISTRY_MARKER in text:
        print("ℹ️ Spec Fase 5.9.3 già presente nel registry.")
        return

    anchor = "LEGACY_QUALITY_MOTORS: list[LegacyMotorSpec] = [\n"

    if anchor not in text:
        raise SystemExit("Anchor LEGACY_QUALITY_MOTORS non trovato nel registry.")

    # Inserisco il riparatore quiz all'inizio della lista motori.
    # Così lavora prima dei vecchi motori quiz che finora erano no-op sui distrattori veri.
    text = text.replace(anchor, anchor + REGISTRY_SPEC, 1)

    REGISTRY.write_text(text, encoding="utf-8")

    print(f"✅ Spec quiz repair aggiunta a: {REGISTRY}")


def main() -> int:
    patch_quiz_repair_wrapper()
    patch_registry_spec()

    print("✅ PATCH FASE 5.9.3 QUIZ TRUE DISTRACTOR REPAIR REGISTRY COMPLETATA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
