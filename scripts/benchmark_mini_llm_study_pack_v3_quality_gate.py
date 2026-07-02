#!/usr/bin/env python3
"""
Benchmark Mini LLM Study Pack V3 Quality Gate.

Controlla:
- qualità card;
- domande naturali;
- opzioni test corte;
- test studente senza risposta corretta visibile;
- answer key separata;
- risposta corretta mescolata;
- velocità.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import time
from pathlib import Path


SAMPLE_DOCUMENT = """
# Documento aziendale di sicurezza informatica

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


BAD_QUESTION_FRAGMENTS = [
    "Che cosa protegge sicurezza",
    "Che cosa usa phishing",
    "Che cosa rafforza L'autenticazione",
    "Qual è il punto chiave su",
]


BAD_CARD_PHRASES = [
    "è un punto centrale del documento",
    "punto chiave su",
]


def load_module(root: Path):
    path = root / "mini_llm/python/runtime/mini_llm_study_pack_v3_quality_gate.py"

    spec = importlib.util.spec_from_file_location("mini_llm_study_pack_v3_quality_gate", path)

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Impossibile caricare modulo: {path}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    return module


def validate_pack(pack: dict) -> list[str]:
    errors: list[str] = []

    if pack.get("status") != "OK":
        errors.append(f"pack_status_not_ok:{pack.get('status')}")

    if pack.get("quality_errors"):
        errors.append("pack_quality_errors_present")

    summary = pack.get("summary", {})

    if summary.get("status") != "OK":
        errors.append("summary_not_ok")

    if not str(summary.get("summary", "")).strip():
        errors.append("summary_empty")

    cards = pack.get("cards", [])

    if len(cards) < 6:
        errors.append("cards_less_than_6")

    for idx, card in enumerate(cards):
        blob = json.dumps(card, ensure_ascii=False)

        if not card.get("title"):
            errors.append(f"card_{idx}_missing_title")

        if not card.get("message"):
            errors.append(f"card_{idx}_missing_message")

        if len(card.get("bullets", [])) < 3:
            errors.append(f"card_{idx}_few_bullets")

        for bad in BAD_CARD_PHRASES:
            if bad.lower() in blob.lower():
                errors.append(f"card_{idx}_bad_phrase:{bad}")

    qas = pack.get("qas", [])

    if len(qas) < 8:
        errors.append("qas_less_than_8")

    for idx, qa in enumerate(qas):
        question = str(qa.get("question", "")).strip()
        answer = str(qa.get("answer", "")).strip()

        if not question.endswith("?"):
            errors.append(f"qa_{idx}_question_no_question_mark")

        if len(question.split()) < 5:
            errors.append(f"qa_{idx}_question_too_short")

        for bad in BAD_QUESTION_FRAGMENTS:
            if bad.lower() in question.lower():
                errors.append(f"qa_{idx}_bad_question:{question}")

        if len(answer.split()) < 5:
            errors.append(f"qa_{idx}_answer_too_short")

    internal_test = pack.get("test", [])
    student_test = pack.get("student_test", [])
    answer_key = pack.get("answer_key", [])

    if len(internal_test) < 6:
        errors.append("internal_test_less_than_6")

    if len(student_test) != len(internal_test):
        errors.append("student_test_length_mismatch")

    if len(answer_key) != len(internal_test):
        errors.append("answer_key_length_mismatch")

    correct_indexes = []

    for idx, item in enumerate(internal_test):
        options = item.get("options", [])
        correct_index = item.get("correct_index")

        correct_indexes.append(correct_index)

        if len(options) != 4:
            errors.append(f"test_{idx}_options_not_4")

        if len(set(options)) != 4:
            errors.append(f"test_{idx}_duplicate_options")

        if correct_index not in [0, 1, 2, 3]:
            errors.append(f"test_{idx}_bad_correct_index")

        elif options[correct_index] != item.get("answer"):
            errors.append(f"test_{idx}_correct_index_mismatch")

        for option in options:
            if len(str(option).split()) > 18:
                errors.append(f"test_{idx}_option_too_long:{option}")

    if len(set(correct_indexes)) < 3:
        errors.append("correct_index_not_mixed_enough")

    forbidden_student_keys = {"correct_index", "answer", "explanation", "source_sentence"}

    for idx, item in enumerate(student_test):
        for key in forbidden_student_keys:
            if key in item:
                errors.append(f"student_test_{idx}_leaks_{key}")

        if len(item.get("options", [])) != 4:
            errors.append(f"student_test_{idx}_options_not_4")

    if float(pack.get("elapsed_ms", 9999.0)) > 45.0:
        errors.append("pack_generation_too_slow")

    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    module = load_module(root)

    start = time.perf_counter()
    pack = module.generate_study_pack(SAMPLE_DOCUMENT)
    total_ms = (time.perf_counter() - start) * 1000.0

    errors = validate_pack(pack)
    status = "PASS" if not errors else "FAIL"

    report = {
        "benchmark": "mini_llm_study_pack_v3_quality_gate",
        "status": status,
        "errors": errors,
        "total_ms": total_ms,
        "pack_elapsed_ms": pack.get("elapsed_ms"),
        "counts": pack.get("counts", {}),
        "summary": pack.get("summary", {}),
        "cards": pack.get("cards", []),
        "qas": pack.get("qas", []),
        "test_internal": pack.get("test", []),
        "student_test": pack.get("student_test", []),
        "answer_key": pack.get("answer_key", []),
        "quality_checks": {
            "student_test_hides_answers": True,
            "answer_key_is_separate": True,
            "options_max_words": 18,
            "correct_index_mixed_min_distinct": 3,
        },
        "limits": [
            "Study Pack V3 structured/extractive.",
            "Non è ancora LLM neurale generativo.",
            "Migliora leggibilità del test rispetto a V2.",
            "Mantiene output studente separato da answer key.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_study_pack_v3_quality_gate_benchmark.json"
    md_path = report_dir / "mini_llm_study_pack_v3_quality_gate_benchmark.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Mini LLM Study Pack V3 Quality Gate Benchmark",
        "",
        f"- Stato: **{status}**",
        f"- Errori: `{', '.join(errors) if errors else 'nessuno'}`",
        f"- Tempo totale: `{total_ms:.6f}` ms",
        f"- Tempo pack interno: `{float(pack.get('elapsed_ms', 0.0)):.6f}` ms",
        "",
        "## Output generati",
        "",
        f"- Frasi riassunto: `{pack.get('counts', {}).get('summary_sentences')}`",
        f"- Card: `{pack.get('counts', {}).get('cards')}`",
        f"- Q&A: `{pack.get('counts', {}).get('qas')}`",
        f"- Test interno: `{pack.get('counts', {}).get('test_questions')}`",
        f"- Test studente: `{pack.get('counts', {}).get('student_test_questions')}`",
        "",
        "## Migliorie V3",
        "",
        "- Opzioni test più corte.",
        "- Test studente senza risposta corretta visibile.",
        "- Answer key separata interna.",
        "- Quality gate più severo su domande, card e opzioni.",
        "",
        "## Riassunto esempio",
        "",
        str(pack.get("summary", {}).get("summary", "")),
        "",
        "## Card esempio",
        "",
    ]

    for card in pack.get("cards", [])[:3]:
        lines.extend(
            [
                f"### {card.get('title')}",
                "",
                str(card.get("message", "")),
                "",
            ]
        )

    lines.extend(["## Q&A esempio", ""])

    for qa in pack.get("qas", [])[:4]:
        lines.extend(
            [
                f"**D:** {qa.get('question')}",
                "",
                f"**R:** {qa.get('answer')}",
                "",
            ]
        )

    lines.extend(["## Test studente esempio", ""])

    for item in pack.get("student_test", [])[:3]:
        lines.append(f"**Domanda:** {item.get('question')}")
        lines.append("")
        for option_index, option in enumerate(item.get("options", []), start=1):
            lines.append(f"{option_index}. {option}")
        lines.append("")

    lines.extend(
        [
            "## Nota",
            "",
            "Il test studente non contiene `correct_index`, `answer`, `explanation` o `source_sentence`.",
            "Le risposte corrette restano nella answer key interna.",
            "",
            "## Limiti",
            "",
            "- Non è ancora LLM neurale generativo.",
            "- Usa frasi reali del documento.",
            "- Non inventa concetti fuori dal testo.",
            "- È il livello qualità prima del collegamento CLI V2.",
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
