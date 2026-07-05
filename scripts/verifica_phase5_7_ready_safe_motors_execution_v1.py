from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from backend.legacy_quality_motor_registry_v1 import apply_legacy_quality_motors_v1


REPORT_JSON = ROOT / "reports" / "phase5_7_ready_safe_motors_execution_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_7_ready_safe_motors_execution_v1.md"


EXPECTED_READY_SAFE = [
    "scripts.rag_cleaner_finale_universale_v35k.clean_output",
    "scripts.rag_motore_didattico_riutilizzabile_v35c.refine_study_questions",
    "scripts.rag_motore_test_riutilizzabile_v35d.refine_output",
    "scripts.rag_revisore_accordo_pronomi_v35j.improve_output",
    "scripts.rag_revisore_qualita_testuale_v35g.refine_output",
    "scripts.rag_revisore_qualita_testuale_v35g.refine_study",
]


def build_payload() -> dict:
    return {
        "document_id": "phase5_7_ready_safe_motors_execution_v1",
        "phase_name": "QUALITY_STUDY_QUIZ",
        "approved": True,
        "status": "APPROVED",
        "riassunto_qualita": {
            "titolo": "Riassunto di qualità",
            "paragrafi": [
                "Il controllo degli accessi limita l'utilizzo dei sistemi interni  .",
                "Le credenziali non non devono essere condivise tra più operatori.",
                "La revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati.",
            ],
            "testo_completo": (
                "Il controllo degli accessi limita l'utilizzo dei sistemi interni  . "
                "Le credenziali non non devono essere condivise tra più operatori. "
                "La revisione periodica degli accessi riduce il rischio perchè evita permessi attivi non autorizzati."
            ),
            "fonte_pagine": [1, 2],
        },
        "card_concettuali": [
            {
                "card_id": "phase5_card_001",
                "titolo": "Controllo accessi",
                "contenuto_esplicativo": "Il controllo degli accessi limita l'utilizzo dei sistemi interni  .",
                "micro_concetti": ["controllo accessi", "account utente"],
                "fonte_pagine": [1, 2],
            },
            {
                "card_id": "phase5_card_002",
                "titolo": "Protezione credenziali",
                "contenuto_esplicativo": "Le credenziali non non devono essere condivise tra più operatori.",
                "micro_concetti": ["credenziali", "operatori"],
                "fonte_pagine": [1, 2],
            },
        ],
        "domande_studio": [
            {
                "question_id": "study_question_001",
                "domanda": "Perchè il controllo accessi è importante ?",
                "risposta_guida": "Il controllo degli accessi limita l'utilizzo dei sistemi interni.",
                "fonte_pagine": [1, 2],
            },
            {
                "question_id": "study_question_002",
                "domanda": "Qual e il rischio delle credenziali condivise?",
                "risposta_guida": "Le credenziali non non devono essere condivise tra più operatori.",
                "fonte_pagine": [1, 2],
            },
        ],
        "test_quiz": [
            {
                "question_id": "phase5_quiz_question_001",
                "domanda": "Quale affermazione descrive correttamente la protezione credenziali?",
                "opzioni": [
                    {
                        "option_id": "A",
                        "testo": "Le credenziali possono essere condivise liberamente tra più operatori.",
                        "is_correct": False,
                    },
                    {
                        "option_id": "B",
                        "testo": "Le credenziali non non devono essere condivise tra più operatori.",
                        "is_correct": True,
                    },
                    {
                        "option_id": "C",
                        "testo": "Le credenziali devono essere scritte in chiaro nei documenti condivisi.",
                        "is_correct": False,
                    },
                    {
                        "option_id": "D",
                        "testo": "Gli account anonimi sono sempre preferibili.",
                        "is_correct": False,
                    },
                ],
                "correct_option_id": "B",
                "spiegazione": "La risposta corretta riprende il fatto verificato dal documento.",
            }
        ],
        "warnings": [],
        "errors": [],
    }


def main() -> int:
    payload = build_payload()
    output = apply_legacy_quality_motors_v1(payload, context="phase5_7_ready_safe_execution")

    meta = output.get("_legacy_quality_motor_registry_v1")

    if not isinstance(meta, dict):
        raise AssertionError("Metadata registry mancante.")

    motors = meta.get("motors", {})

    missing = []
    not_applied = []
    failed = []
    worsened = []

    for motor_id in EXPECTED_READY_SAFE:
        motor = motors.get(motor_id)

        if not isinstance(motor, dict):
            missing.append(motor_id)
            continue

        status = motor.get("status")
        applied = motor.get("applied", 0)

        if status not in {"ok", "partial"}:
            failed.append(
                {
                    "motor_id": motor_id,
                    "status": status,
                    "motor": motor,
                }
            )

        if not isinstance(applied, int) or applied <= 0:
            not_applied.append(
                {
                    "motor_id": motor_id,
                    "status": status,
                    "applied": applied,
                    "motor": motor,
                }
            )

        for target in motor.get("targets", []):
            before = target.get("known_text_defects_before")
            after = target.get("known_text_defects_after")

            if isinstance(before, int) and isinstance(after, int) and after > before:
                worsened.append(
                    {
                        "motor_id": motor_id,
                        "target": target,
                    }
                )

    registry_before = meta.get("known_text_defects_before")
    registry_after = meta.get("known_text_defects_after")

    if isinstance(registry_before, int) and isinstance(registry_after, int) and registry_after > registry_before:
        raise AssertionError(f"Registry peggiora globalmente: {registry_before} -> {registry_after}")

    report = {
        "report_name": "phase5_7_ready_safe_motors_execution_v1",
        "status": "PASS" if not missing and not not_applied and not failed and not worsened else "FAIL",
        "expected_ready_safe": EXPECTED_READY_SAFE,
        "missing": missing,
        "not_applied": not_applied,
        "failed": failed,
        "worsened": worsened,
        "registry_meta": meta,
        "notes": [
            "Verifica diagnostica: controlla che i 6 motori READY_SAFE siano presenti ed eseguiti.",
            "Non aggiunge nuovi motori.",
            "Non modifica il registry.",
            "Se un motore non è applied>0, è registrato ma non realmente eseguito sul payload.",
        ],
    }

    REPORT_JSON.parent.mkdir(parents=True, exist_ok=True)
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = []
    lines.append("# Fase 5.7 — Ready Safe Motors Execution V1\n")
    lines.append(f"- Status: `{report['status']}`")
    lines.append(f"- Registry defects: `{registry_before} -> {registry_after}`")
    lines.append("")
    lines.append("| Motore | Status | Applied | Changed | Target | Peggiora |")
    lines.append("|---|---|---:|---:|---|---|")

    for motor_id in EXPECTED_READY_SAFE:
        motor = motors.get(motor_id, {})
        targets = motor.get("targets", [])

        if not targets:
            lines.append(
                f"| `{motor_id}` | `{motor.get('status')}` | `{motor.get('applied', 0)}` | `{motor.get('changed', 0)}` |  |  |"
            )
            continue

        for target in targets:
            before = target.get("known_text_defects_before")
            after = target.get("known_text_defects_after")
            bad = isinstance(before, int) and isinstance(after, int) and after > before

            lines.append(
                f"| `{motor_id}` "
                f"| `{motor.get('status')}` "
                f"| `{motor.get('applied', 0)}` "
                f"| `{motor.get('changed', 0)}` "
                f"| `{target.get('target')}` "
                f"| {'⚠️' if bad else ''} |"
            )

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    print("✅ FASE 5.7 READY SAFE MOTORS EXECUTION V1 PASS" if report["status"] == "PASS" else "❌ FASE 5.7 FAIL")
    print(f"Report JSON: {REPORT_JSON}")
    print(f"Report MD:   {REPORT_MD}")
    print(json.dumps({
        "status": report["status"],
        "missing": missing,
        "not_applied": not_applied,
        "failed_count": len(failed),
        "worsened_count": len(worsened),
        "registry_defects": f"{registry_before} -> {registry_after}",
    }, ensure_ascii=False, indent=2))

    if report["status"] != "PASS":
        raise AssertionError("Fase 5.7 fallita: vedi report.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
