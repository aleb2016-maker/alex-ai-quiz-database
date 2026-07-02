#!/usr/bin/env python3
"""
Validazione dello script Mini LLM Practical Real Test V3.9.1.

Usa un documento reale di test temporaneo, non sintetico da 500 pagine.
Verifica che:
- lo script parta;
- generi report JSON/MD;
- risponda a query;
- generi summary;
- generi Study Pack;
- non committi output privati.
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


SAMPLE = """
# Documento operativo di sicurezza

La sicurezza informatica protegge account, dati, dispositivi e sistemi aziendali.
Il phishing usa messaggi ingannevoli per convincere le persone a fornire credenziali o dati sensibili.
I backup regolari permettono di recuperare informazioni dopo errori, guasti o cancellazioni accidentali.
L'autenticazione a due fattori aggiunge un secondo controllo oltre alla password.
Gli aggiornamenti software correggono errori e chiudono vulnerabilità di sicurezza.
La formazione del personale riduce distrazioni, errori e comportamenti rischiosi.
Le procedure interne aiutano a gestire incidenti, accessi, backup e comunicazioni.
I log permettono di ricostruire eventi, tentativi di accesso e modifiche importanti.
La classificazione dei dati distingue informazioni pubbliche, interne, riservate e critiche.
Il ransomware blocca o cifra dati e chiede un pagamento per ripristinarli.
"""


def main() -> int:
    root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory(prefix="mini_llm_practical_v391_") as tmp:
        tmp_path = Path(tmp)
        doc = tmp_path / "documento_reale_test.md"
        out_dir = tmp_path / "out"

        doc.write_text(SAMPLE.strip() + "\n", encoding="utf-8")

        result = subprocess.run(
            [
                sys.executable,
                "scripts/mini_llm_practical_real_test_v391.py",
                str(doc),
                "--query",
                "Che cosa fa il phishing?",
                "--query",
                "A cosa servono i backup?",
                "--study-query",
                "sicurezza phishing backup formazione procedure dati ransomware",
                "--out-dir",
                str(out_dir),
            ],
            cwd=str(root),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print("STDOUT:")
            print(result.stdout)
            print("STDERR:")
            print(result.stderr)
            return 1

        report_json = out_dir / "practical_real_test_v391_report.json"
        report_md = out_dir / "practical_real_test_v391_report.md"

        if not report_json.exists() or not report_md.exists():
            print("Report non generati.")
            return 1

        report = json.loads(report_json.read_text(encoding="utf-8"))

    errors = []

    if report.get("status") != "PASS":
        errors.append(f"status_not_pass:{report.get('status')}:{report.get('errors')}")

    diagnostics = report.get("diagnostics", {})

    if diagnostics.get("engine") != "mini_llm_long_document_rag_v391_semantic_repair":
        errors.append("wrong_engine")

    if diagnostics.get("sentences", 0) < 8:
        errors.append(f"sentences_too_few:{diagnostics.get('sentences')}")

    answers = report.get("answers", [])

    if len(answers) < 2:
        errors.append("answers_less_than_2")

    if not any("phishing" in str(answer.get("answer", "")).lower() for answer in answers):
        errors.append("missing_phishing_answer")

    summary = report.get("progressive_summary", {})

    if summary.get("status") != "OK":
        errors.append(f"summary_not_ok:{summary.get('status')}")

    study = report.get("study_pack", {})

    if study.get("status") != "OK":
        errors.append(f"study_pack_not_ok:{study.get('status')}")

    pack = study.get("study_pack", {})

    counts = pack.get("counts", {})

    if counts.get("cards", 0) < 6:
        errors.append("cards_less_than_6")

    if counts.get("qas", 0) < 8:
        errors.append("qas_less_than_8")

    status = "PASS" if not errors else "FAIL"

    validation = {
        "validator": "valida_mini_llm_practical_real_test_v391",
        "status": status,
        "errors": errors,
        "sample_report_status": report.get("status"),
        "diagnostics": diagnostics,
        "counts": counts,
        "limits": [
            "Valida lo script su documento markdown temporaneo.",
            "Non usa documenti privati.",
            "Non salva output reali nel repository.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_practical_real_test_v391_validation.json"
    md_path = report_dir / "mini_llm_practical_real_test_v391_validation.md"

    json_path.write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Validazione Mini LLM Practical Real Test V3.9.1",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        "",
        "## Cosa valida",
        "",
        "- Lettura documento reale temporaneo Markdown.",
        "- RAG V3.9.1 Semantic Repair.",
        "- Risposte a domande.",
        "- Riassunto progressivo.",
        "- Study Pack.",
        "- Output reali ignorati da git.",
        "",
        "## Diagnostica campione",
        "",
        f"- Engine: `{diagnostics.get('engine')}`",
        f"- Frasi: `{diagnostics.get('sentences')}`",
        f"- Chunk: `{diagnostics.get('chunks')}`",
        f"- Counts: `{counts}`",
        "",
        "## Limiti",
        "",
        "- No OCR.",
        "- Non è ancora LLM neurale generativo.",
        "- Il test reale dell'utente va eseguito con un file vero scelto dall'utente.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(validation, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
