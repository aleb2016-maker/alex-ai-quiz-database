from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.legacy_quality_motor_registry_v1 import apply_legacy_quality_motors_v1


def main() -> int:
    payload = {
        "document_id": "test_legacy_quality_motor_registry_v1",
        "phase_name": "QUALITY_STUDY_QUIZ",
        "approved": True,
        "status": "APPROVED",
        "test_quiz": [
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
            }
        ],
        "warnings": [],
        "errors": [],
    }

    output = apply_legacy_quality_motors_v1(payload, context="phase5_registry_test")

    if not isinstance(output, dict):
        raise AssertionError("Il registry deve mantenere output dict.")

    if "test_quiz" not in output:
        raise AssertionError("Il registry ha perso test_quiz.")

    if not output["test_quiz"]:
        raise AssertionError("Il registry ha svuotato test_quiz.")

    meta = output.get("_legacy_quality_motor_registry_v1")

    if not isinstance(meta, dict):
        raise AssertionError("Metadata registry mancante.")

    if meta.get("status") not in {"ok", "partial"}:
        raise AssertionError(f"Registry status inatteso: {meta.get('status')}")

    before = meta.get("known_text_defects_before")
    after = meta.get("known_text_defects_after")

    if isinstance(before, int) and isinstance(after, int) and after > before:
        raise AssertionError(f"Registry peggiora i difetti: {before} -> {after}")

    required_motors = [
        "backend.main.pulisci_qualita_linguistica_quiz",
        "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests",
    ]

    motors = meta.get("motors", {})

    for motor_id in required_motors:
        if motor_id not in motors:
            raise AssertionError(f"Motore legacy non registrato: {motor_id}")

        status = motors[motor_id].get("status")

        if status in {"failed", "failed_import"}:
            raise AssertionError(
                f"Motore legacy non compatibile: {motor_id} | "
                f"{json.dumps(motors[motor_id], ensure_ascii=False, indent=2)}"
            )

        for target in motors[motor_id].get("targets", []):
            tb = target.get("known_text_defects_before")
            ta = target.get("known_text_defects_after")

            if isinstance(tb, int) and isinstance(ta, int) and ta > tb:
                raise AssertionError(f"Motore {motor_id} peggiora target: {tb} -> {ta}")

    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    report_path = report_dir / "legacy_quality_motor_registry_v1_report.json"
    report_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("✅ LEGACY QUALITY MOTOR REGISTRY V1 PASS")
    print(f"Report: {report_path.resolve()}")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
