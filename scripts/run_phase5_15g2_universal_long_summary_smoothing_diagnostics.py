#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Diagnostica FASE 5.15G.2 - Universal long summary thematic smoothing.

Esegue il percorso:
G.1 global map -> G.1 long summary grezzo -> G.2 smoothing -> validazione G.2.
Non modifica file, non fa commit e non passa dal Quality Manager comune.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.phase5_15g1_long_document_orchestrator import (  # noqa: E402
    build_global_document_map,
    build_long_generator_output,
    build_long_quality_summary,
    is_long_document,
)
from backend.phase5_15g2_universal_long_summary_smoothing import (  # noqa: E402
    smooth_long_summary,
    validate_universal_summary_quality,
)


def _repeat(seed: str, times: int = 95) -> str:
    return "\n\n".join(
        f"Sezione {index + 1}\n{seed} "
        f"Questa parte aggiunge dettagli progressivi, collegamenti interni e conseguenze operative numero {index + 1}."
        for index in range(times)
    )


def _fixture_documents() -> Dict[str, str]:
    return {
        "manuale_aziendale": _repeat(
            "Il processo operativo definisce responsabilita, controlli, audit, rischi e passaggi di verifica. "
            "Il responsabile controlla gli stati del workflow, registra le anomalie e coordina le decisioni."
        ),
        "dispensa_scolastica_universitaria": _repeat(
            "La lezione introduce definizioni, concetti chiave, esempi, esercizi e collegamenti teorici. "
            "Gli studenti devono collegare il capitolo ai casi applicativi e alle spiegazioni precedenti."
        ),
        "documento_tecnico": _repeat(
            "L'architettura descrive componenti, database, API, configurazioni, errori e parametri di sistema. "
            "Il modulo coordina endpoint, validazioni e condizioni di installazione."
        ),
        "documento_legale_amministrativo": _repeat(
            "Il quadro amministrativo richiama articoli, commi, obblighi, scadenze, vincoli e soggetti responsabili. "
            "L'ente verifica istanze, autorizzazioni e conseguenze della norma."
        ),
        "storia_racconto": _repeat(
            "Il racconto segue il protagonista, il conflitto, la scena centrale e l'evoluzione del personaggio. "
            "La trama collega dialoghi, svolte narrative e finale."
        ),
    }


def _diagnose(name: str, text: str) -> Dict[str, Any]:
    global_map = build_global_document_map(text)
    g1 = build_long_quality_summary(global_map, text)
    g2 = smooth_long_summary(global_map, text, g1["summary_text"])
    validation = validate_universal_summary_quality(g2["summary_text"], g2["profile"])
    routed = build_long_generator_output("summary", text)
    quality_report = routed.get("quality_report", {})
    return {
        "name": name,
        "is_long_document": is_long_document(text),
        "input_words": global_map.get("input_words"),
        "macro_blocks_count": global_map.get("macro_blocks_count"),
        "profile": g2["profile"],
        "summary_words": g2["metrics"].get("summary_words"),
        "target_words_10_percent": g2["metrics"].get("target_words_10_percent"),
        "target_10_percent_reached": g2["metrics"].get("target_10_percent_reached"),
        "theme_count": g2["metrics"].get("theme_count"),
        "validation": validation,
        "integration_flag": quality_report.get("phase5_15g2_universal_summary_smoothing"),
        "integration_profile": quality_report.get("document_profile", {}).get("tipo_testo"),
        "integration_warnings": quality_report.get("g2_warnings", []),
        "preview": g2["summary_text"][:900],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Phase 5.15G.2 long-summary smoothing diagnostics.")
    parser.add_argument("--input-file", help="Documento reale da diagnosticare.")
    parser.add_argument("--json", action="store_true", help="Stampa solo JSON.")
    args = parser.parse_args()

    if args.input_file:
        path = Path(args.input_file)
        documents = {path.name: path.read_text(encoding="utf-8", errors="replace")}
    else:
        documents = _fixture_documents()

    reports: List[Dict[str, Any]] = [_diagnose(name, text) for name, text in documents.items()]
    payload = {
        "phase": "5.15G.2",
        "diagnostics_count": len(reports),
        "all_integration_flags_true": all(report["integration_flag"] is True for report in reports),
        "all_without_system_noise": all(
            report["validation"]["metrics"]["system_noise_count"] == 0 for report in reports
        ),
        "all_targets_reached": all(report["target_10_percent_reached"] for report in reports),
        "reports": reports,
    }

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    failed = not (
        payload["all_integration_flags_true"]
        and payload["all_without_system_noise"]
        and payload["all_targets_reached"]
    )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
