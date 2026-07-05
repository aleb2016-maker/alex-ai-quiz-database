from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "backend" / "legacy_quality_motor_registry_v1.py"
ADAPTER = ROOT / "backend" / "phase5_universal_quiz_quality_adapter_v1.py"

REGISTRY_MARKER = "# FASE 5.9.9 — UNIVERSAL QUIZ QUALITY ADAPTER REGISTRY V1"


REGISTRY_SPEC = '''    # FASE 5.9.9 — UNIVERSAL QUIZ QUALITY ADAPTER REGISTRY V1
    # Motore universale quiz validato separatamente in Fase 5.9.8.
    # Obiettivo: migliorare distrattori veri, domande meccaniche,
    # ripetitività e spiegazioni grezze preservando la risposta corretta.
    LegacyMotorSpec(
        motor_id="backend.phase5_universal_quiz_quality_adapter_v1.universal_quiz_quality_target_v1",
        module_name="backend.phase5_universal_quiz_quality_adapter_v1",
        function_name="universal_quiz_quality_target_v1",
        adapter_name="quiz_list",
        target_kind="quiz",
    ),
'''


def patch_registry() -> None:
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Registry non trovato: {REGISTRY}")

    if not ADAPTER.exists():
        raise FileNotFoundError(f"Adapter universale non trovato: {ADAPTER}")

    text = REGISTRY.read_text(encoding="utf-8")

    if REGISTRY_MARKER in text:
        print("ℹ️ Spec Fase 5.9.9 già presente nel registry.")
        return

    repair_spec_id = 'motor_id="backend.phase5_quiz_true_distractor_repair_v1.repair_quiz_target_v1"'

    if repair_spec_id not in text:
        raise SystemExit("Spec riparatore distrattori veri non trovata: non inserisco alla cieca.")

    # Inserisco il motore universale subito dopo il riparatore distrattori veri.
    # Così il primo motore azzera i distrattori veri e il secondo rifinisce
    # domande/spiegazioni senza dover duplicare il lavoro.
    insert_pos = text.find(repair_spec_id)

    next_spec_pos = text.find("    LegacyMotorSpec(", insert_pos + len(repair_spec_id))

    if next_spec_pos == -1:
        anchor = "LEGACY_QUALITY_MOTORS: list[LegacyMotorSpec] = [\n"

        if anchor not in text:
            raise SystemExit("Anchor lista motori non trovato.")

        text = text.replace(anchor, anchor + REGISTRY_SPEC, 1)

    else:
        text = text[:next_spec_pos] + REGISTRY_SPEC + text[next_spec_pos:]

    REGISTRY.write_text(text, encoding="utf-8")

    print(f"✅ Universal Quiz Quality Adapter aggiunto al registry: {REGISTRY}")


def main() -> int:
    patch_registry()
    print("✅ PATCH FASE 5.9.9 COMPLETATA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
