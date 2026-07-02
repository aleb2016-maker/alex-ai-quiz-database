#!/usr/bin/env python3
"""
Validazione Mini LLM Study Pack Current.

Controlla che:
- current punti a V3 Quality Gate;
- CLI current sia CLI V2;
- generi riassunto/card/Q&A/test;
- separi student_test e answer_key;
- non esponga risposte nel test studente;
- resti veloce.

Nota:
il campione è volutamente più ricco del primo tentativo, perché V3 richiede
abbastanza frasi utili per generare 8 Q&A di qualità.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path


SAMPLE_TEXT = """
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
La formazione del personale riduce errori, distrazioni e comportamenti rischiosi durante il lavoro quotidiano.
Le procedure di sicurezza aiutano a gestire incidenti, accessi, backup, dispositivi e comunicazioni interne.
"""


def load_current(root: Path):
    path = root / "mini_llm/python/runtime/mini_llm_study_pack_current.py"

    spec = importlib.util.spec_from_file_location("mini_llm_study_pack_current", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare current: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    module = load_current(root)

    start = time.perf_counter()
    pack = module.generate_study_pack(SAMPLE_TEXT)
    total_ms = (time.perf_counter() - start) * 1000.0

    errors = []

    current = pack.get("current", {})
    counts = pack.get("counts", {})

    if current.get("engine") != "mini_llm_study_pack_v3_quality_gate":
        errors.append("current_engine_not_v3_quality_gate")

    if current.get("cli_file") != "scripts/mini_llm_study_pack_cli_v2.py":
        errors.append("current_cli_not_v2")

    if pack.get("status") != "OK":
        errors.append(f"pack_status_not_ok:{pack.get('status')}")

    if pack.get("quality_errors"):
        errors.append("pack_quality_errors_present")

    if counts.get("summary_sentences", 0) < 8:
        errors.append("summary_less_than_8")

    if counts.get("cards", 0) < 6:
        errors.append("cards_less_than_6")

    if counts.get("qas", 0) < 8:
        errors.append("qas_less_than_8")

    if counts.get("test_questions", 0) < 6:
        errors.append("test_less_than_6")

    if counts.get("student_test_questions", 0) < 6:
        errors.append("student_test_less_than_6")

    if not pack.get("student_test"):
        errors.append("missing_student_test")

    if not pack.get("answer_key"):
        errors.append("missing_answer_key")

    student_blob = json.dumps(pack.get("student_test", []), ensure_ascii=False)

    for forbidden in ["correct_index", "answer", "explanation", "source_sentence"]:
        if forbidden in student_blob:
            errors.append(f"student_test_leaks_{forbidden}")

    if float(pack.get("elapsed_ms", 9999.0)) > 50.0:
        errors.append("pack_elapsed_too_slow")

    if total_ms > 120.0:
        errors.append("total_elapsed_too_slow")

    status = "PASS" if not errors else "FAIL"

    report = {
        "validator": "valida_mini_llm_study_pack_current",
        "status": status,
        "errors": errors,
        "total_ms": total_ms,
        "pack_elapsed_ms": pack.get("elapsed_ms"),
        "current": current,
        "counts": counts,
        "examples": {
            "first_card": pack.get("cards", [{}])[0],
            "first_qa": pack.get("qas", [{}])[0],
            "first_student_test": pack.get("student_test", [{}])[0],
            "first_answer_key": pack.get("answer_key", [{}])[0],
        },
        "limits": [
            "Current punta a V3 Quality Gate.",
            "CLI current consigliata: Study Pack CLI V2.",
            "Structured/extractive.",
            "Non ancora LLM neurale generativo.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_study_pack_current_validation.json"
    md_path = report_dir / "validazione_mini_llm_study_pack_current.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    first_card = report["examples"]["first_card"]
    first_qa = report["examples"]["first_qa"]
    first_test = report["examples"]["first_student_test"]

    lines = [
        "# Validazione Mini LLM Study Pack Current",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        f"- Tempo totale: `{total_ms:.6f}` ms",
        f"- Tempo pack: `{float(pack.get('elapsed_ms', 0.0)):.6f}` ms",
        "",
        "## Current",
        "",
        f"- Engine: `{current.get('engine')}`",
        f"- Engine file: `{current.get('engine_file')}`",
        f"- CLI file: `{current.get('cli_file')}`",
        f"- Tag: `{current.get('tag')}`",
        "",
        "## Conteggi",
        "",
        f"- Riassunto: `{counts.get('summary_sentences')}`",
        f"- Card: `{counts.get('cards')}`",
        f"- Q&A: `{counts.get('qas')}`",
        f"- Test studente: `{counts.get('student_test_questions')}`",
        "",
        "## Esempi",
        "",
        f"### Card: {first_card.get('title')}",
        "",
        str(first_card.get("message", "")),
        "",
        "### Q&A",
        "",
        f"**D:** {first_qa.get('question')}",
        "",
        f"**R:** {first_qa.get('answer')}",
        "",
        "### Test studente",
        "",
        f"**Domanda:** {first_test.get('question')}",
        "",
    ]

    for index, option in enumerate(first_test.get("options", []), start=1):
        lines.append(f"{index}. {option}")

    lines.extend(
        [
            "",
            "## Limiti",
            "",
            "- Current non è ancora LLM neurale.",
            "- È il miglior motore structured/extractive attuale.",
            "- Serve come base stabile per il prossimo sviluppo mini LLM.",
            "",
        ]
    )

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("")
    print(f"Report JSON: {json_path}")
    print(f"Report Markdown: {md_path}")

    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
