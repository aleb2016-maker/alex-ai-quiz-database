from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

REGISTRY = ROOT / "backend" / "legacy_quality_motor_registry_v1.py"
CLEANER = ROOT / "backend" / "phase5_universal_text_cleaner_summary_cards_v1.py"

MARKER = "# FASE 5.10.1 — UNIVERSAL TEXT CLEANER SUMMARY/CARDS REGISTRY V1"

MOTOR_ID = "backend.phase5_universal_text_cleaner_summary_cards_v1.universal_text_cleaner_summary_cards_payload_target_v1"


REGISTRY_SPEC = '''    # FASE 5.10.1 — UNIVERSAL TEXT CLEANER SUMMARY/CARDS REGISTRY V1
    # Motore validato separatamente in Fase 5.10.
    # Pulisce riassunto e card da pattern brutti residui senza toccare quiz/study.
    LegacyMotorSpec(
        motor_id="backend.phase5_universal_text_cleaner_summary_cards_v1.universal_text_cleaner_summary_cards_payload_target_v1",
        module_name="backend.phase5_universal_text_cleaner_summary_cards_v1",
        function_name="universal_text_cleaner_summary_cards_payload_target_v1",
        adapter_name="payload",
        target_kind="full_output",
    ),
'''


def patch_registry() -> None:
    if not REGISTRY.exists():
        raise FileNotFoundError(f"Registry non trovato: {REGISTRY}")

    if not CLEANER.exists():
        raise FileNotFoundError(f"Cleaner summary/cards non trovato: {CLEANER}")

    text = REGISTRY.read_text(encoding="utf-8")

    if MARKER in text or MOTOR_ID in text:
        print("ℹ️ Cleaner summary/cards già presente nel registry.")
        return

    anchor = "LEGACY_QUALITY_MOTORS: list[LegacyMotorSpec] = ["

    if anchor not in text:
        raise SystemExit("Lista LEGACY_QUALITY_MOTORS non trovata.")

    list_start = text.find(anchor)
    list_end = text.find("\n]", list_start)

    if list_end == -1:
        raise SystemExit("Fine lista LEGACY_QUALITY_MOTORS non trovata.")

    # Inserimento come rifinitura finale.
    text = text[:list_end] + REGISTRY_SPEC + text[list_end:]

    REGISTRY.write_text(text, encoding="utf-8")

    print(f"✅ Cleaner summary/cards aggiunto al registry: {REGISTRY}")


def main() -> int:
    patch_registry()
    print("✅ PATCH FASE 5.10.1 COMPLETATA")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
