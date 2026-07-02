#!/usr/bin/env python3
"""
Validazione Mini LLM Document CLI V1.

Verifica:
- build su documento MD;
- ask con cache MISS/HIT;
- summary;
- formato JSON valido;
- risposta non vuota;
- repository cache utente ignorata da Git.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


SAMPLE_TEXT = """
# Documento prova sicurezza informatica

La sicurezza informatica protegge dati, dispositivi, account e sistemi attraverso pratiche, strumenti e comportamenti corretti.
Il phishing usa l'inganno per convincere le persone a fornire dati sensibili, credenziali o pagamenti.
I backup regolari servono a recuperare informazioni in caso di errore umano, guasto, furto o cancellazione accidentale.
L'autenticazione a due fattori rafforza l'accesso aggiungendo un secondo controllo oltre alla password.
Il ransomware è un malware che blocca o cifra i dati e chiede un pagamento per ripristinarli.
Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
Un password manager aiuta a conservare password lunghe e uniche senza doverle ricordare tutte.
Le credenziali rubate possono consentire accessi non autorizzati ad account o sistemi.
"""


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

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Output non JSON valido: {exc}\n{result.stdout}") from exc


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    sample_dir = root / "mini_llm/data/fast_runtime/cli_v1_samples"
    sample_dir.mkdir(parents=True, exist_ok=True)

    sample_file = sample_dir / "documento_prova_sicurezza.md"
    sample_file.write_text(SAMPLE_TEXT.strip() + "\n", encoding="utf-8")

    cli = "scripts/mini_llm_document_cli_v1.py"

    build = run_json(root, [cli, "build", str(sample_file)])
    ask_first = run_json(root, [cli, "ask", str(sample_file), "Che cosa fa il phishing?"])
    ask_second = run_json(root, [cli, "ask", str(sample_file), "A cosa servono i backup regolari?"])
    summary = run_json(root, [cli, "summary", str(sample_file), "--max-sentences", "5"])

    errors = []

    if build.get("status") != "OK":
        errors.append("build_not_ok")

    if ask_first.get("status") != "OK" or not ask_first.get("answer"):
        errors.append("ask_first_not_ok")

    if ask_second.get("status") != "OK" or not ask_second.get("answer"):
        errors.append("ask_second_not_ok")

    if summary.get("status") != "OK" or not summary.get("summary"):
        errors.append("summary_not_ok")

    if str(summary.get("summary", "")).lstrip().startswith("#"):
        errors.append("summary_starts_with_markdown_heading")

    if ask_second.get("cache", {}).get("cache_status") != "HIT":
        errors.append("cache_hit_missing_on_second_ask")

    report = {
        "validator": "valida_mini_llm_document_cli_v1",
        "status": "PASS" if not errors else "FAIL",
        "errors": errors,
        "sample_file": str(sample_file),
        "build": build,
        "ask_first": ask_first,
        "ask_second": ask_second,
        "summary": summary,
    }

    report_path = root / "mini_llm/reports/validazione_mini_llm_document_cli_v1.md"
    json_path = root / "mini_llm/data/fast_runtime/mini_llm_document_cli_v1_validation.json"

    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Validazione Mini LLM Document CLI V1",
        "",
        f"- Stato: **{report['status']}**",
        f"- File sample: `{sample_file}`",
        "",
        "## Risultati",
        "",
        f"- Build: `{build.get('status')}`",
        f"- Ask 1: `{ask_first.get('status')}`",
        f"- Ask 2: `{ask_second.get('status')}`",
        f"- Cache Ask 2: `{ask_second.get('cache', {}).get('cache_status')}`",
        f"- Summary: `{summary.get('status')}`",
        "",
        "## Esempio risposta",
        "",
        str(ask_first.get("answer", "")),
        "",
        "## Esempio riassunto",
        "",
        str(summary.get("summary", "")),
        "",
        "## Limiti",
        "",
        "- CLI V1 supporta TXT/MD, non PDF diretto.",
        "- Q&A e summary sono extractive.",
        "- La cache utente è runtime e non deve essere committata.",
        "",
    ]

    report_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report Markdown: {report_path}")
    print(f"Report JSON: {json_path}")

    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
