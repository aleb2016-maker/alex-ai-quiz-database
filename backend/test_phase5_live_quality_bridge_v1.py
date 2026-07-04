from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_live_quality_bridge_v1 import apply_phase5_live_quality_bridge_v1


def main() -> int:
    payload = {
        "document_id": "test_phase5_live_quality_bridge_v1",
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

    output = apply_phase5_live_quality_bridge_v1(payload)

    if not isinstance(output, dict):
        raise AssertionError("Il bridge deve mantenere un dizionario come output.")

    meta = output.get("_phase5_live_quality_bridge_v1")

    if not isinstance(meta, dict):
        raise AssertionError("Metadata _phase5_live_quality_bridge_v1 mancante.")

    if meta.get("phase") != "5.3":
        raise AssertionError("Phase metadata errato.")

    motors = meta.get("motors", {})

    required_motors = [
        "backend.main.pulisci_qualita_linguistica_quiz",
        "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_tests",
    ]

    for motor in required_motors:
        if motor not in motors:
            raise AssertionError(f"Motore non registrato: {motor}")

        status = motors[motor].get("status")

        if status in {"failed_import", "failed"}:
            raise AssertionError(
                f"Motore vivo non collegato correttamente: {motor} | "
                f"status={status} | details={json.dumps(motors[motor], ensure_ascii=False, indent=2)}"
            )

    if "test_quiz" not in output:
        raise AssertionError("Il bridge ha perso test_quiz.")

    if not output["test_quiz"]:
        raise AssertionError("Il bridge ha svuotato test_quiz.")

    # QUALITY_NON_WORSENING_ASSERTION
    before = meta.get("known_text_defects_before")
    after = meta.get("known_text_defects_after")

    if isinstance(before, int) and isinstance(after, int) and after > before:
        raise AssertionError(f"Il bridge ha peggiorato i difetti testuali: {before} -> {after}")

    for motor_id, info in motors.items():
        for target in info.get("targets", []):
            tb = target.get("known_text_defects_before")
            ta = target.get("known_text_defects_after")

            if isinstance(tb, int) and isinstance(ta, int) and ta > tb:
                raise AssertionError(f"Il motore {motor_id} ha peggiorato il target {target.get('target')}: {tb} -> {ta}")

    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)

    report_path = report_dir / "phase5_live_quality_bridge_v1_report.json"
    report_path.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print("✅ FASE 5.3 LIVE QUALITY BRIDGE V1 PASS")
    print(f"Report: {report_path.resolve()}")
    print(json.dumps(meta, ensure_ascii=False, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
