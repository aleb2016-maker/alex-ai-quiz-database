#!/usr/bin/env python3
"""
Smoke test integrato Mini LLM documentale V1.

Verifica in un solo comando:
- motore current V3.15;
- CLI documentale V1;
- cache HIT;
- Q&A su documento reale temporaneo;
- summary pulito senza heading Markdown;
- tempi principali.

Questo test non crea nuove feature.
Serve a garantire che il sistema documentale resti sano dopo le patch.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path


SAMPLE_TEXT = """
# Documento integrato Mini LLM

La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.
Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.
Gli account amministrativi hanno privilegi elevati e devono essere protetti con controlli aggiuntivi.
I documenti aziendali possono contenere informazioni operative, contratti, credenziali o dati riservati.
"""


def run_command(root: Path, args: list[str], expect_json: bool = False) -> tuple[int, str, str, object | None, float]:
    start = time.perf_counter()

    result = subprocess.run(
        [sys.executable, *args],
        cwd=str(root),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    elapsed_ms = (time.perf_counter() - start) * 1000.0

    parsed = None

    if expect_json and result.returncode == 0:
        parsed = json.loads(result.stdout)

    return result.returncode, result.stdout, result.stderr, parsed, elapsed_ms


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    report_dir = root / "mini_llm/reports"
    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    json_report = data_dir / "mini_llm_documentale_integrato_v1.json"
    md_report = report_dir / "mini_llm_documentale_integrato_v1.md"

    with tempfile.TemporaryDirectory(prefix="mini_llm_doc_smoke_") as tmp:
        sample_file = Path(tmp) / "documento_integrato.md"
        sample_file.write_text(SAMPLE_TEXT.strip() + "\n", encoding="utf-8")

        current_code, current_out, current_err, _, current_ms = run_command(
            root,
            ["scripts/valida_inference_engine_current.py"],
            expect_json=False,
        )

        build_code, build_out, build_err, build_json, build_ms = run_command(
            root,
            ["scripts/mini_llm_document_cli_v1.py", "build", str(sample_file)],
            expect_json=True,
        )

        ask_code, ask_out, ask_err, ask_json, ask_ms = run_command(
            root,
            [
                "scripts/mini_llm_document_cli_v1.py",
                "ask",
                str(sample_file),
                "Che cosa fa il phishing?",
            ],
            expect_json=True,
        )

        summary_code, summary_out, summary_err, summary_json, summary_ms = run_command(
            root,
            [
                "scripts/mini_llm_document_cli_v1.py",
                "summary",
                str(sample_file),
                "--max-sentences",
                "6",
            ],
            expect_json=True,
        )

    errors: list[str] = []

    if current_code != 0:
        errors.append("current_validator_failed")

    if build_code != 0 or not build_json or build_json.get("status") != "OK":
        errors.append("build_failed")

    if ask_code != 0 or not ask_json or ask_json.get("status") != "OK" or not ask_json.get("answer"):
        errors.append("ask_failed")

    if summary_code != 0 or not summary_json or summary_json.get("status") != "OK" or not summary_json.get("summary"):
        errors.append("summary_failed")

    if ask_json and ask_json.get("cache", {}).get("cache_status") != "HIT":
        errors.append("ask_cache_not_hit")

    if summary_json and str(summary_json.get("summary", "")).lstrip().startswith("#"):
        errors.append("summary_has_markdown_heading")

    status = "PASS" if not errors else "FAIL"

    report = {
        "validator": "mini_llm_documentale_integrato_v1",
        "status": status,
        "errors": errors,
        "current_validator_ms": current_ms,
        "build_total_ms": build_ms,
        "ask_total_ms": ask_ms,
        "summary_total_ms": summary_ms,
        "build": build_json,
        "ask": ask_json,
        "summary": summary_json,
        "limits": [
            "Smoke test integrato, non benchmark completo.",
            "Usa TXT/MD tramite CLI, non PDF diretto.",
            "Q&A e summary sono extractive.",
            "Serve a verificare stabilità end-to-end.",
        ],
    }

    json_report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Mini LLM Documentale Integrato V1",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Componenti verificati",
        "",
        f"- Current validator: `{'OK' if current_code == 0 else 'FAIL'}`",
        f"- CLI build: `{build_json.get('status') if build_json else 'FAIL'}`",
        f"- CLI ask: `{ask_json.get('status') if ask_json else 'FAIL'}`",
        f"- CLI summary: `{summary_json.get('status') if summary_json else 'FAIL'}`",
        f"- Cache ask: `{ask_json.get('cache', {}).get('cache_status') if ask_json else 'N/D'}`",
        "",
        "## Tempi",
        "",
        f"- Current validator totale: `{current_ms:.6f}` ms",
        f"- Build totale: `{build_ms:.6f}` ms",
        f"- Ask totale: `{ask_ms:.6f}` ms",
        f"- Summary totale: `{summary_ms:.6f}` ms",
        "",
        "## Risposta esempio",
        "",
        str(ask_json.get("answer", "") if ask_json else ""),
        "",
        "## Riassunto esempio",
        "",
        str(summary_json.get("summary", "") if summary_json else ""),
        "",
        "## Limiti",
        "",
        "- Test integrato su documento Markdown temporaneo.",
        "- Non legge ancora PDF direttamente.",
        "- Non fa OCR.",
        "- Non applica ancora la regola riassunto 10% pagine / sinossi 1%.",
        "",
    ]

    md_report.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_report}")
    print(f"Report Markdown: {md_report}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
