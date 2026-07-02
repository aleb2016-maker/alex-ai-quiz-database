#!/usr/bin/env python3
"""
Validazione Mini LLM Real Quality Gate V3.9.2.

Verifica:
- report brutto bocciato;
- report pulito accettato;
- titoli card non trattati come frasi complete.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


def load_gate(root: Path):
    path = root / "scripts/mini_llm_real_quality_gate_v392.py"

    spec = importlib.util.spec_from_file_location("mini_llm_real_quality_gate_v392", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare gate: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def build_bad_report() -> dict:
    return {
        "status": "PASS",
        "file": "bad.md",
        "diagnostics": {
            "engine": "mini_llm_long_document_rag_v391_semantic_repair",
            "sentences": 20,
        },
        "answers": [
            {
                "answer": "# Documento RAG di test: Sicurezza informatica aziendale ## Scopo del documento Questo documento è stato creato come fonte di prova."
            }
        ],
        "progressive_summary": {
            "quality_summary": "al dominio reale; - errori grammaticali o frasi insolite; - richiesta di password, codici o dati bancari.",
            "brief_summary": "Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui."
        },
        "study_pack": {
            "study_pack": {
                "summary": {
                    "summary": "Documento RAG di test: materiale di prova."
                },
                "cards": [
                    {
                        "title": "Al dominio reale - errori",
                        "message": "al dominio reale; - errori grammaticali o frasi insolite; - richiesta di password, codici o dati."
                    }
                ],
                "qas": [
                    {
                        "question": "Che cosa usa non riguarda solo gli esperti informatici: ogni persona che?",
                        "answer": "Non riguarda solo gli esperti informatici: ogni persona che usa un computer."
                    }
                ],
                "student_test": [
                    {
                        "question": "Che cosa può fare il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui un sistema RAG?",
                        "options": [
                            "al dominio reale; - errori grammaticali o frasi insolite.",
                            "Il documento non è pensato come manuale tecnico avanzato, ma come materiale formativo chiaro da cui.",
                            "Usare un computer, uno smartphone, una rete aziendale o un account online.",
                            "Contenere dati sensibili."
                        ]
                    }
                ],
            }
        },
    }


def build_good_report() -> dict:
    return {
        "status": "PASS",
        "file": "good.md",
        "diagnostics": {
            "engine": "mini_llm_long_document_rag_v391_semantic_repair",
            "sentences": 20,
        },
        "answers": [
            {
                "answer": "Il phishing usa messaggi ingannevoli per convincere le persone a fornire credenziali o dati sensibili."
            }
        ],
        "progressive_summary": {
            "quality_summary": "La sicurezza informatica protegge account, dati, dispositivi e sistemi aziendali. I backup regolari permettono di recuperare informazioni dopo errori, guasti o cancellazioni accidentali.",
            "brief_summary": "La sicurezza informatica protegge account, dati, dispositivi e sistemi aziendali. I backup regolari permettono di recuperare informazioni dopo errori, guasti o cancellazioni accidentali."
        },
        "study_pack": {
            "study_pack": {
                "summary": {
                    "summary": "La sicurezza informatica protegge account, dati, dispositivi e sistemi aziendali. I backup regolari permettono di recuperare informazioni dopo errori, guasti o cancellazioni accidentali."
                },
                "cards": [
                    {
                        "title": "Sicurezza informatica",
                        "message": "La sicurezza informatica protegge account, dati, dispositivi e sistemi aziendali."
                    },
                    {
                        "title": "Backup regolari",
                        "message": "I backup regolari permettono di recuperare informazioni dopo errori, guasti o cancellazioni accidentali."
                    }
                ],
                "qas": [
                    {
                        "question": "Che cosa usa il phishing?",
                        "answer": "Il phishing usa messaggi ingannevoli per convincere le persone a fornire credenziali o dati sensibili."
                    },
                    {
                        "question": "A cosa servono i backup regolari?",
                        "answer": "I backup regolari permettono di recuperare informazioni dopo errori, guasti o cancellazioni accidentali."
                    }
                ],
                "student_test": [
                    {
                        "question": "Che cosa usa il phishing?",
                        "options": [
                            "Messaggi ingannevoli per ottenere credenziali o dati sensibili.",
                            "Copie di sicurezza per recuperare informazioni.",
                            "Aggiornamenti software per chiudere vulnerabilità.",
                            "Procedure interne per gestire incidenti aziendali."
                        ]
                    },
                    {
                        "question": "A cosa servono i backup regolari?",
                        "options": [
                            "A recuperare informazioni dopo errori o guasti.",
                            "A ottenere credenziali tramite messaggi ingannevoli.",
                            "A classificare dati pubblici e riservati.",
                            "A segnalare anomalie nei sistemi aziendali."
                        ]
                    }
                ],
            }
        },
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    gate = load_gate(root)

    bad_result = gate.validate_report(build_bad_report())
    good_result = gate.validate_report(build_good_report())

    errors = []

    if bad_result.get("status") != "FAIL":
        errors.append("bad_report_not_rejected")

    if not bad_result.get("errors"):
        errors.append("bad_report_without_errors")

    if good_result.get("status") != "PASS":
        errors.append(f"good_report_not_pass:{good_result.get('errors')}")

    status = "PASS" if not errors else "FAIL"

    validation = {
        "validator": "valida_mini_llm_real_quality_gate_v392",
        "status": status,
        "errors": errors,
        "bad_report_status": bad_result.get("status"),
        "bad_report_errors_sample": bad_result.get("errors", [])[:20],
        "good_report_status": good_result.get("status"),
        "good_report_errors": good_result.get("errors", []),
        "limits": [
            "Valida il gate su report costruiti.",
            "Non modifica il motore generativo.",
            "Serve a impedire falsi PASS sui test reali.",
            "Titoli card validati come titoli, non come frasi.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_real_quality_gate_v392_validation.json"
    md_path = report_dir / "mini_llm_real_quality_gate_v392_validation.md"

    json_path.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Mini LLM Real Quality Gate V3.9.2",
        "",
        f"- Stato: **{status}**",
        f"- Errori validatore: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Risultati",
        "",
        f"- Report brutto bocciato: `{bad_result.get('status')}`",
        f"- Report pulito accettato: `{good_result.get('status')}`",
        "",
        "## Errori rilevati nel report brutto",
        "",
    ]

    for item in bad_result.get("errors", [])[:30]:
        lines.append(f"- `{item}`")

    lines.extend(
        [
            "",
            "## Cosa blocca",
            "",
            "- Heading Markdown dentro output.",
            "- Frammenti da elenco.",
            "- Domande innaturali.",
            "- Opzioni troncate.",
            "- Metadati del documento usati come contenuto.",
            "",
            "## Cosa non blocca più per errore",
            "",
            "- Titoli card brevi e validi come `Sicurezza informatica`.",
            "- Titoli card brevi e validi come `Backup regolari`.",
            "",
            "## Limiti",
            "",
            "- Gate diagnostico.",
            "- Non è ancora un generatore migliore.",
            "- Il prossimo step sarà collegarlo al test pratico reale come requisito obbligatorio.",
            "",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
