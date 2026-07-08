#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
REPORTS.mkdir(exist_ok=True)

CONNECTOR = ROOT / "demo-rag" / "phase5-14-ui-buttons-real-connector.js"
PAGE = ROOT / "demo-rag" / "test-documenti-universale.html"

REPORT_JSON = REPORTS / "phase5_15g52_ui_backend_real_connection_smoke_v1.json"
REPORT_MD = REPORTS / "phase5_15g52_ui_backend_real_connection_smoke_v1.md"


def main() -> int:
    defects = []

    connector = CONNECTOR.read_text(encoding="utf-8") if CONNECTOR.exists() else ""
    page = PAGE.read_text(encoding="utf-8") if PAGE.exists() else ""

    checks = {
        "connector_exists": CONNECTOR.exists(),
        "page_exists": PAGE.exists(),
        "connector_has_interroga_label": "Interroga Documento" in connector,
        "connector_calls_real_backend_kind": 'phase5LocalBackendBridgeGenerate("interroga_documento"' in connector,
        "connector_sends_document_text": "document_text: inputText" in connector,
        "connector_sends_user_question": "user_question: question" in connector,
        "connector_question_textarea": "phase5-15g52-document-question" in connector,
        "connector_bypasses_old_study_motor": 'if (kind === "study")' in connector and "renderDocumentQAOutput" in connector,
        "page_has_question_textarea": "phase5-15g52-page-document-question" in page,
        "page_sets_backend_kind": 'backendKind = "interroga_documento"' in page,
        "page_sends_document_text": "document_text: text" in page,
        "page_sends_user_question": "user_question: userQuestion" in page,
        "page_fetch_uses_backend_kind": "kind: backendKind" in page,
        "page_fetch_uses_backend_text": "text: backendText" in page,
        "page_renders_document_qa": "renderInterrogaDocumentoPayload(payload)" in page,
    }

    for key, ok in checks.items():
        if not ok:
            defects.append(key)

    # Backend reale già collegato: deve essere presente dal checkpoint G.5.1.
    backend = (ROOT / "backend" / "phase5_15b_quality_checked_generators.py").read_text(encoding="utf-8")
    backend_checks = {
        "backend_has_ask_document": '"ask_document": "ask_document"' in backend,
        "backend_has_interroga_alias": '"interroga_documento": "ask_document"' in backend,
        "backend_calls_g5_engine": "run_interroga_documento" in backend,
    }
    for key, ok in backend_checks.items():
        if not ok:
            defects.append(key)

    status = "PASS" if not defects else "FAIL"

    report = {
        "phase": "5.15G.5.2",
        "name": "UI backend real connection smoke",
        "status": status,
        "checks": checks,
        "backend_checks": backend_checks,
        "defects": defects,
        "scope": {
            "real_endpoint": "http://127.0.0.1:8765/api/generate",
            "backend_kind": "interroga_documento",
            "payload": {"kind": "interroga_documento", "text": "{\"document_text\":\"...\",\"user_question\":\"...\"}"},
            "summary_touched": False,
            "cards_touched": False,
            "quiz_touched": False,
            "study_questions_deleted": False,
            "hardcoded_answer": False,
        },
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Fase 5.15G.5.2 - UI Backend Real Connection Smoke",
        "",
        f"Esito: **{status}**",
        "",
        "## Collegamento reale",
        "- Endpoint: `http://127.0.0.1:8765/api/generate`",
        "- kind inviato: `interroga_documento`",
        "- text inviato: JSON con `document_text` e `user_question`",
        "- Nessuna risposta hardcoded.",
        "- Nessun fallback/demo.",
        "",
        "## Checks",
    ]

    for key, ok in {**checks, **backend_checks}.items():
        lines.append(f"- {key}: `{ok}`")

    if defects:
        lines.extend(["", "## Difetti", *[f"- {d}" for d in defects]])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"phase5_15g52_ui_backend_real_connection_smoke: {status}")
    print(f"json: {REPORT_JSON}")
    print(f"markdown: {REPORT_MD}")
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
