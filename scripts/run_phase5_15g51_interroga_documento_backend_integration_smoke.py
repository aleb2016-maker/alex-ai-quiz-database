#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

REPORT_JSON = REPORTS / "phase5_15g51_interroga_documento_backend_integration_smoke_v1.json"
REPORT_MD = REPORTS / "phase5_15g51_interroga_documento_backend_integration_smoke_v1.md"


def _import_runner():
    try:
        from backend.phase5_15b_quality_checked_generators import run_quality_checked_generator
    except Exception:
        import sys
        sys.path.insert(0, str(ROOT / "backend"))
        from phase5_15b_quality_checked_generators import run_quality_checked_generator
    return run_quality_checked_generator


def _user_visible_text(result: dict) -> str:
    """Controlla solo testo utente visibile, non chiavi tecniche JSON.

    Il primo smoke falliva perché cercava parole come 'fallback'
    anche dentro chiavi metriche tipo fallback_demo_count=0.
    """
    raw = result.get("final_output") or result.get("raw_output") or result.get("output") or {}
    chunks = []

    if isinstance(raw, dict):
        chunks.append(str(raw.get("answer") or ""))
        chunks.append(str(raw.get("question") or ""))
        for ev in raw.get("evidence") or []:
            if isinstance(ev, dict):
                chunks.append(str(ev.get("text") or ""))
            else:
                chunks.append(str(ev))
    else:
        chunks.append(str(raw))

    return "\n".join(chunks)


def main() -> int:
    run_quality_checked_generator = _import_runner()

    document_text = (
        "Documento di sicurezza informatica aziendale. "
        "Le responsabilità sono assegnate al responsabile IT e ai referenti di reparto. "
        "Le verifiche trimestrali controllano backup, accessi e continuità operativa. "
        "La formazione degli utenti riduce errori operativi e migliora la qualità delle procedure."
    )

    cases = [
        {
            "name": "json_answered",
            "generator": "interroga_documento",
            "payload": {
                "document_text": document_text,
                "user_question": "Quali responsabilità vengono citate nel documento?"
            },
            "expected_status": "ANSWERED",
        },
        {
            "name": "json_not_found",
            "generator": "ask_document",
            "payload": {
                "document_text": document_text,
                "user_question": "Qual è il prezzo del petrolio indicato nel documento?"
            },
            "expected_status": "NOT_FOUND_IN_DOCUMENT",
        },
        {
            "name": "marker_answered",
            "generator": "domanda_documento",
            "payload_text": (
                "DOMANDA: Quali verifiche vengono indicate?\n"
                "DOCUMENTO: " + document_text
            ),
            "expected_status": "ANSWERED",
        },
    ]

    forbidden_visible_phrases = [
        "risposta corretta",
        "opzione corretta",
        "quiz generato",
        "domanda di test",
        "raw_output",
        "quality manager",
    ]

    results = []
    defects = []

    for case in cases:
        if "payload_text" in case:
            input_text = case["payload_text"]
        else:
            input_text = json.dumps(case["payload"], ensure_ascii=False)

        result = run_quality_checked_generator(case["generator"], input_text)
        raw = result.get("final_output") or result.get("raw_output") or {}
        visible = _user_visible_text(result)
        status = result.get("status")

        case_defects = []

        if status != case["expected_status"]:
            case_defects.append(f"status_atteso_{case['expected_status']}_ottenuto_{status}")

        if result.get("generator") != "ask_document":
            case_defects.append("generator_non_normalizzato_ask_document")

        if result.get("generator_label") != "Interroga Documento":
            case_defects.append("label_non_interroga_documento")

        if not result.get("approved"):
            case_defects.append("approved_false")

        low_visible = visible.lower()
        for bad in forbidden_visible_phrases:
            if bad in low_visible:
                case_defects.append(f"contaminazione_visibile_{bad.replace(' ', '_')}")

        if isinstance(raw, dict):
            answer = str(raw.get("answer") or "")
            evidence = raw.get("evidence") or []

            if case["expected_status"] == "ANSWERED":
                if not evidence:
                    case_defects.append("answered_senza_evidence")
                if len(answer.split()) < 5:
                    case_defects.append("answered_troppo_corto")
                if raw.get("not_found"):
                    case_defects.append("not_found_errato_su_domanda_presente")

            if case["expected_status"] == "NOT_FOUND_IN_DOCUMENT":
                if not raw.get("not_found"):
                    case_defects.append("not_found_false_su_domanda_fuori_documento")
                if evidence:
                    case_defects.append("not_found_con_evidence_non_attesa")

        results.append({
            "name": case["name"],
            "generator": case["generator"],
            "expected_status": case["expected_status"],
            "status": status,
            "approved": bool(result.get("approved")),
            "defects": case_defects,
        })

        defects.extend([f"{case['name']}: {d}" for d in case_defects])

    status_final = "PASS" if not defects else "FAIL"

    report = {
        "phase": "5.15G.5.1",
        "name": "Interroga Documento backend integration smoke",
        "status": status_final,
        "defects": defects,
        "cases": results,
        "checks": {
            "visible_text_only_scan": True,
            "backend_aliases": ["ask_document", "interroga_documento", "domanda_documento"],
            "study_questions_removed": False,
            "ui_connected": False,
            "quality_manager_common_modified": False,
        },
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Fase 5.15G.5.1 - Interroga Documento backend integration smoke",
        "",
        f"Esito: **{status_final}**",
        "",
        "## Casi",
    ]
    for item in results:
        lines.append(
            f"- {item['name']}: generator `{item['generator']}`, "
            f"atteso `{item['expected_status']}`, ottenuto `{item['status']}`, "
            f"approved `{item['approved']}`, defects `{item['defects']}`"
        )

    lines.extend([
        "",
        "## Scope",
        "- Study Questions non eliminate.",
        "- UI non collegata in questa fase.",
        "- Integrazione limitata al backend quality generator.",
        "- Il motore usato è `phase5_15g5_document_qa_engine.run_interroga_documento`.",
        "- Lo smoke controlla solo testo utente visibile, non chiavi tecniche JSON.",
    ])

    if defects:
        lines.extend(["", "## Difetti", *[f"- {d}" for d in defects]])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"phase5_15g51_interroga_documento_backend_integration_smoke: {status_final}")
    print(f"json: {REPORT_JSON}")
    print(f"markdown: {REPORT_MD}")

    return 0 if status_final == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
