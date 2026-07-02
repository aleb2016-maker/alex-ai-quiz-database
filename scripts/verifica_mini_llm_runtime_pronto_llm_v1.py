#!/usr/bin/env python3
"""
Verifica Mini LLM Runtime Pronto per LLM V1.

Scopo:
- certificare che il runtime documentale è stabile prima di implementare LLM;
- controllare current, CLI, cache, PDF testuale, report PASS;
- eseguire un micro test live su TXT/MD tramite CLI;
- produrre un report di chiusura.

Questo NON implementa ancora LLM.
È un contratto di stabilità prima del prossimo blocco LLM.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SAMPLE_TEXT = """
# Documento chiusura runtime LLM

La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
"""


REQUIRED_FILES = [
    "scripts/valida_inference_engine_current.py",
    "scripts/mini_llm_document_cli_v1.py",
    "scripts/verifica_mini_llm_documentale_integrato_v1.py",
    "scripts/valida_mini_llm_document_cli_pdf_v1.py",
    "mini_llm/python/runtime/fast_document_qa_summary_v2_cache.py",
    "mini_llm/python/runtime/pdf_text_extractor_v1.py",
    "mini_llm/data/fast_runtime/fast_document_qa_summary_v2_cache_benchmark.json",
    "mini_llm/data/fast_runtime/mini_llm_document_cli_v1_validation.json",
    "mini_llm/data/fast_runtime/mini_llm_document_cli_pdf_v1_validation.json",
    "mini_llm/data/fast_runtime/mini_llm_documentale_integrato_v1.json",
    "requirements.txt",
]


PASS_REPORTS = [
    "mini_llm/data/fast_runtime/fast_document_qa_summary_v2_cache_benchmark.json",
    "mini_llm/data/fast_runtime/mini_llm_document_cli_v1_validation.json",
    "mini_llm/data/fast_runtime/mini_llm_document_cli_pdf_v1_validation.json",
    "mini_llm/data/fast_runtime/mini_llm_documentale_integrato_v1.json",
]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def run_json(root: Path, args: list[str]) -> dict:
    result = subprocess.run(
        [sys.executable, *args],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    if result.returncode != 0:
        raise RuntimeError(
            "Comando fallito:\n"
            + " ".join(args)
            + "\nSTDOUT:\n"
            + result.stdout
            + "\nSTDERR:\n"
            + result.stderr
        )

    return json.loads(result.stdout)


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    errors: list[str] = []
    checks: dict[str, object] = {}

    missing_files = []

    for rel in REQUIRED_FILES:
        path = root / rel
        if not path.exists():
            missing_files.append(rel)

    if missing_files:
        errors.append("missing_required_files")

    checks["missing_files"] = missing_files

    report_statuses = {}

    for rel in PASS_REPORTS:
        path = root / rel

        if not path.exists():
            report_statuses[rel] = "MISSING"
            errors.append(f"missing_report:{rel}")
            continue

        try:
            payload = load_json(path)
            status = payload.get("status")
            report_statuses[rel] = status

            if status != "PASS":
                errors.append(f"report_not_pass:{rel}")

        except Exception as exc:
            report_statuses[rel] = f"ERROR: {exc}"
            errors.append(f"report_unreadable:{rel}")

    checks["report_statuses"] = report_statuses

    requirements_path = root / "requirements.txt"

    if requirements_path.exists():
        req_text = requirements_path.read_text(encoding="utf-8").lower()
        checks["pypdf_in_requirements"] = "pypdf" in req_text

        if "pypdf" not in req_text:
            errors.append("pypdf_missing_in_requirements")
    else:
        checks["pypdf_in_requirements"] = False
        errors.append("requirements_missing")

    cli_path = root / "scripts/mini_llm_document_cli_v1.py"

    if cli_path.exists():
        cli_text = cli_path.read_text(encoding="utf-8")
        checks["cli_supports_pdf"] = '".pdf"' in cli_text or "PDF testuale" in cli_text

        if not checks["cli_supports_pdf"]:
            errors.append("cli_pdf_support_missing")

    live_test = {}

    try:
        with tempfile.TemporaryDirectory(prefix="mini_llm_ready_llm_") as tmp:
            sample_file = Path(tmp) / "documento_chiusura_runtime.md"
            sample_file.write_text(SAMPLE_TEXT.strip() + "\n", encoding="utf-8")

            build = run_json(
                root,
                [
                    "scripts/mini_llm_document_cli_v1.py",
                    "build",
                    str(sample_file),
                ],
            )

            ask = run_json(
                root,
                [
                    "scripts/mini_llm_document_cli_v1.py",
                    "ask",
                    str(sample_file),
                    "Che cosa fa il phishing?",
                ],
            )

            summary = run_json(
                root,
                [
                    "scripts/mini_llm_document_cli_v1.py",
                    "summary",
                    str(sample_file),
                    "--max-sentences",
                    "5",
                ],
            )

            live_test = {
                "build": build,
                "ask": ask,
                "summary": summary,
            }

            if build.get("status") != "OK":
                errors.append("live_build_not_ok")

            if ask.get("status") != "OK" or not ask.get("answer"):
                errors.append("live_ask_not_ok")

            if ask.get("cache", {}).get("cache_status") != "HIT":
                errors.append("live_ask_cache_not_hit")

            if summary.get("status") != "OK" or not summary.get("summary"):
                errors.append("live_summary_not_ok")

            if str(summary.get("summary", "")).lstrip().startswith("#"):
                errors.append("live_summary_has_markdown_heading")

    except Exception as exc:
        live_test = {"error": str(exc)}
        errors.append("live_cli_test_failed")

    status = "PASS" if not errors else "FAIL"

    readiness = {
        "validator": "verifica_mini_llm_runtime_pronto_llm_v1",
        "status": status,
        "errors": errors,
        "checks": checks,
        "live_test": live_test,
        "runtime_contract": {
            "current_engine": "inference_engine_current -> V3.15 stable",
            "document_runtime": "fast_document_qa_summary_v2_cache",
            "cli": "mini_llm_document_cli_v1",
            "supported_inputs": ["txt", "md", "markdown", "pdf_textual"],
            "cache": "cache_v2_user_docs runtime ignored by git",
            "qa_mode": "extractive",
            "summary_mode": "extractive",
            "pdf_mode": "textual/selectable PDF via pypdf",
            "ready_for_llm_layer": status == "PASS",
        },
        "limits_before_llm": [
            "Non è ancora un LLM generativo.",
            "Non usa ancora modello neurale per generare testo libero.",
            "Non gestisce ancora OCR per PDF scannerizzati.",
            "Q&A e summary sono extractive.",
            "Il prossimo blocco LLM dovrà usare questo runtime come base documentale/RAG.",
        ],
        "next_llm_step": [
            "Definire interfaccia LLM provider.",
            "Creare adapter locale/API separato.",
            "Usare retrieve/cache documentale come contesto.",
            "Aggiungere generazione controllata con qualità gate.",
            "Mantenere fallback vietati e output tracciabile.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_runtime_pronto_llm_v1.json"
    md_path = report_dir / "mini_llm_runtime_pronto_llm_v1.md"

    json_path.write_text(
        json.dumps(readiness, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Mini LLM Runtime Pronto per LLM V1",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Contratto runtime",
        "",
        "- Current engine: `inference_engine_current -> V3.15 stable`",
        "- Runtime documentale: `fast_document_qa_summary_v2_cache`",
        "- CLI: `mini_llm_document_cli_v1`",
        "- Input supportati: `TXT`, `MD`, `Markdown`, `PDF testuali/selezionabili`",
        "- Cache: `cache_v2_user_docs`, runtime ignorata da Git",
        "- Q&A: `extractive`",
        "- Summary: `extractive`",
        "- PDF: `pypdf`, solo testo selezionabile",
        "",
        "## Check principali",
        "",
        f"- File mancanti: `{', '.join(missing_files) if missing_files else 'nessuno'}`",
        f"- pypdf in requirements: `{checks.get('pypdf_in_requirements')}`",
        f"- CLI supporta PDF: `{checks.get('cli_supports_pdf')}`",
        "",
        "## Report PASS letti",
        "",
    ]

    for rel, report_status in report_statuses.items():
        lines.append(f"- `{rel}`: `{report_status}`")

    ask_answer = ""
    summary_text = ""

    if isinstance(live_test, dict):
        ask_payload = live_test.get("ask", {})
        summary_payload = live_test.get("summary", {})

        if isinstance(ask_payload, dict):
            ask_answer = str(ask_payload.get("answer", ""))

        if isinstance(summary_payload, dict):
            summary_text = str(summary_payload.get("summary", ""))

    lines.extend(
        [
            "",
            "## Micro test live",
            "",
            f"- Build: `{live_test.get('build', {}).get('status') if isinstance(live_test.get('build'), dict) else 'N/D'}`",
            f"- Ask: `{live_test.get('ask', {}).get('status') if isinstance(live_test.get('ask'), dict) else 'N/D'}`",
            f"- Cache ask: `{live_test.get('ask', {}).get('cache', {}).get('cache_status') if isinstance(live_test.get('ask'), dict) else 'N/D'}`",
            f"- Summary: `{live_test.get('summary', {}).get('status') if isinstance(live_test.get('summary'), dict) else 'N/D'}`",
            "",
            "### Risposta esempio",
            "",
            ask_answer,
            "",
            "### Riassunto esempio",
            "",
            summary_text,
            "",
            "## Limiti prima del blocco LLM",
            "",
            "- Non è ancora un LLM generativo.",
            "- Non usa ancora modello neurale per generare testo libero.",
            "- Non gestisce ancora OCR per PDF scannerizzati.",
            "- Q&A e summary sono extractive.",
            "- Il prossimo blocco LLM dovrà usare questo runtime come base documentale/RAG.",
            "",
            "## Prossimo step LLM",
            "",
            "1. Definire interfaccia LLM provider.",
            "2. Creare adapter locale/API separato.",
            "3. Usare retrieve/cache documentale come contesto.",
            "4. Aggiungere generazione controllata con quality gate.",
            "5. Mantenere fallback vietati e output tracciabile.",
            "",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(readiness, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
