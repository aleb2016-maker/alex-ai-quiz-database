#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASE 5.15B - smoke test for the single quality checked generator entrypoint.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15b_quality_checked_generators import (  # noqa: E402
    build_report,
    run_quality_checked_generator,
    save_report_files,
    save_trace_json,
)


DOCUMENTS = {
    "breve_valido": (
        "La procedura di onboarding assegna un tutor al nuovo dipendente. "
        "Il tutor presenta gli strumenti aziendali, verifica gli accessi e registra "
        "eventuali problemi entro il primo giorno. Il responsabile HR controlla che "
        "la scheda sia completa e che ogni autorizzazione abbia una motivazione. "
        "Alla fine della settimana il nuovo dipendente conferma di aver compreso "
        "le regole operative principali."
    ),
    "tecnico": (
        "Il sistema di backup usa snapshot incrementali ogni quattro ore e una "
        "replica giornaliera su storage separato. Il ripristino deve essere testato "
        "almeno una volta al mese con un campione di file critici. Se il test "
        "fallisce, il team apre un ticket critico, blocca la chiusura del controllo "
        "e ripete la procedura dopo la correzione. I log di replica vengono "
        "conservati per novanta giorni per consentire verifiche successive."
    ),
    "narrativo_discorsivo": (
        "Marta arrivò alla stazione quando il treno era già partito. Nel diario "
        "trovò una mappa disegnata da suo nonno e capì che il viaggio non riguardava "
        "la destinazione, ma la memoria della famiglia. Decise di seguire gli indizi "
        "uno alla volta, fermandosi in ogni paese citato dalle vecchie lettere. "
        "Quando raggiunse la casa vicino al lago, riconobbe il cortile descritto "
        "nei racconti d'infanzia e annotò ogni dettaglio per non perderlo."
    ),
}

GENERATORS = ["summary", "cards", "study_questions", "quiz"]


def _has_demo_input(text: str) -> bool:
    low = str(text or "").lower()
    return (
        "lorem ipsum" in low
        or "testo di esempio" in low
        or ("sicurezza informatica aziendale" in low and len(text) < 500)
    )


def _validate_case(result: Dict[str, Any], document_id: str, generator: str, input_text: str) -> List[str]:
    defects: List[str] = []
    prefix = f"{document_id}/{generator}"
    if result.get("used_entrypoint") is not True:
        defects.append(f"{prefix}: generatore non passato dall'entrypoint unico")
    if not result.get("qm_runtime_trace"):
        defects.append(f"{prefix}: qm_runtime_trace mancante")
    if result.get("all_motors_connected") is True and not result.get("qm_runtime_trace"):
        defects.append(f"{prefix}: all_motors_connected=True senza trace reale")
    if int(result.get("executed_qm_count") or 0) <= 0:
        defects.append(f"{prefix}: nessun QM eseguito")
    if result.get("raw_output_present") is not True:
        defects.append(f"{prefix}: output vuoto")
    if result.get("input_verified") is not True:
        defects.append(f"{prefix}: input reale assente o respinto")
    if _has_demo_input(input_text):
        defects.append(f"{prefix}: fallback/demo usato come input")
    return defects


def main() -> int:
    results: List[Dict[str, Any]] = []
    smoke_defects: List[str] = []

    for document_id, input_text in DOCUMENTS.items():
        for generator in GENERATORS:
            result = run_quality_checked_generator(generator, input_text)
            result["document_id"] = document_id
            results.append(result)
            smoke_defects.extend(_validate_case(result, document_id, generator, input_text))

    save_trace_json(results)
    report = build_report(results, smoke_defects)
    save_report_files(report, results)

    print(
        "FASE 5.15B smoke: "
        f"status={report['status']} "
        f"cases={len(results)} "
        f"generators_with_trace={report['generators_with_real_qm_trace']}/4"
    )

    if smoke_defects:
        print("SMOKE DEFECTS:")
        for defect in smoke_defects:
            print(f"- {defect}")
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
