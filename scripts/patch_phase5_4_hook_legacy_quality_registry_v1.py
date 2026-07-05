from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

MOTORI = ROOT / "backend" / "motori_scrittura.py"

MARKER = "# FASE 5.4 — LEGACY QUALITY MOTOR REGISTRY HOOK V1"

HOOK_CODE = r'''

# FASE 5.4 — LEGACY QUALITY MOTOR REGISTRY HOOK V1
# Collega la nuova struttura centrale dei motori legacy alla Fase 5.
# Non sostituisce i motori vecchi: li esegue tramite registry, adapter e guardia anti-peggioramento.
try:
    import functools as _phase5_4_legacy_registry_functools
    from backend.legacy_quality_motor_registry_v1 import (
        apply_legacy_quality_motors_v1 as _phase5_4_apply_legacy_quality_motors_v1,
    )

    _phase5_4_previous_build_phase5_quality_study_quiz = build_phase5_quality_study_quiz

    @_phase5_4_legacy_registry_functools.wraps(_phase5_4_previous_build_phase5_quality_study_quiz)
    def build_phase5_quality_study_quiz(*args, **kwargs):
        _phase5_4_raw_output = _phase5_4_previous_build_phase5_quality_study_quiz(*args, **kwargs)
        return _phase5_4_apply_legacy_quality_motors_v1(
            _phase5_4_raw_output,
            context="phase5_quality_study_quiz",
        )

except Exception as _phase5_4_legacy_registry_error:
    _phase5_4_legacy_registry_import_error = repr(_phase5_4_legacy_registry_error)
'''


def main() -> int:
    if not MOTORI.exists():
        raise FileNotFoundError(f"File non trovato: {MOTORI}")

    text = MOTORI.read_text(encoding="utf-8")

    if MARKER in text:
        print("ℹ️ Hook Fase 5.4 già presente: non duplico.")
        return 0

    MOTORI.write_text(text.rstrip() + "\n\n" + HOOK_CODE.strip() + "\n", encoding="utf-8")

    print(f"✅ Hook registry legacy Fase 5.4 aggiunto a: {MOTORI}")
    print("✅ PATCH FASE 5.4 LEGACY QUALITY MOTOR REGISTRY HOOK COMPLETATA")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
