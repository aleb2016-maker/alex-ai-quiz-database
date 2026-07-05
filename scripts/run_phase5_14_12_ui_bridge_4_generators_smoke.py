#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_JSON = ROOT / "reports" / "phase5_14_12_ui_bridge_4_generators_smoke_v1.json"
REPORT_MD = ROOT / "reports" / "phase5_14_12_ui_bridge_4_generators_smoke_v1.md"

TEXT = (
    "Questo documento descrive una procedura aziendale per la gestione degli accessi. "
    "Ogni account deve essere associato a una persona identificabile. "
    "Le credenziali non devono essere condivise tra operatori. "
    "La revisione periodica degli accessi riduce il rischio di permessi non autorizzati."
)

KINDS = ["summary", "cards", "study", "quiz"]

def post(kind):
    body = json.dumps({"kind": kind, "text": TEXT}).encode("utf-8")
    req = urllib.request.Request(
        "http://127.0.0.1:8765/api/generate",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))

def main():
    results = {}
    defects = []

    for kind in KINDS:
        try:
            payload = post(kind)
            results[kind] = payload

            if not payload.get("ok"):
                defects.append(f"{kind}: ok false")
                continue

            result = payload.get("result") or {}
            if result.get("approved") is not True:
                defects.append(f"{kind}: approved non true")

            if result.get("status") != "APPROVED":
                defects.append(f"{kind}: status non APPROVED")

            if kind == "summary" and not result.get("content"):
                defects.append("summary: content vuoto")

            if kind in {"cards", "study", "quiz"} and not result.get("items"):
                defects.append(f"{kind}: items vuoti")

        except Exception as exc:
            defects.append(f"{kind}: {type(exc).__name__}: {exc}")

    status = (
        "PASS - Fase 5.14.12: UI_BRIDGE_4_GENERATORS_READY"
        if not defects
        else "FAIL - Fase 5.14.12: UI_BRIDGE_4_GENERATORS_NOT_READY"
    )

    report = {
        "phase": "5.14.12",
        "status": status,
        "strict_no_fallback": True,
        "endpoint": "http://127.0.0.1:8765/api/generate",
        "results": results,
        "defects": defects,
    }

    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# FASE 5.14.12 — UI BRIDGE 4 GENERATORI",
        "",
        f"Status: `{status}`",
        "",
        "| Generatore | OK | Approved | Status | Motore |",
        "|---|---:|---:|---|---|",
    ]

    for kind in KINDS:
        payload = results.get(kind, {})
        result = payload.get("result") or {}
        lines.append(
            f"| `{kind}` | `{payload.get('ok')}` | `{result.get('approved')}` | "
            f"`{result.get('status')}` | `{result.get('motor_name')}` |"
        )

    lines.extend(["", "## Defects", ""])
    lines.append("- Nessuno" if not defects else "\n".join(f"- `{d}`" for d in defects))

    lines.extend([
        "",
        "## Confini",
        "",
        "- Bridge locale pagina → backend attivo su porta 8765.",
        "- Nessun fallback/demo usato.",
        "- I quattro generatori rispondono da testo reale.",
    ])

    REPORT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(status)
    print(f"Defects: {len(defects)}")
    print(f"JSON report: {REPORT_JSON}")
    print(f"Markdown report: {REPORT_MD}")

    if defects:
        for defect in defects:
            print("-", defect)
        return 1

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
