#!/usr/bin/env python3
"""
Benchmark Mini LLM Study Pack V2 Quality.

Controlla:
- riassunto;
- card;
- Q&A;
- test;
- domande naturali;
- titoli card puliti;
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
    "possono causare documenti",
]


BAD_TITLE_WORDS = [
    "recuperare",
    "protegge",
    "rafforza",
    "convincere",
    "fornire",
]


def load_module(root: Path):
    path = root / "mini_llm/python/runtime/mini_llm_study_pack_v2_quality.py"

    spec = importlib.util.spec_from_file_location("mini_llm_study_pack_v2_quality", path)

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
        title = str(card.get("title", ""))

        if not title:
            errors.append(f"card_{idx}_missing_title")

        low_title = title.lower()

        for bad in BAD_TITLE_WORDS:
            if bad.lower() in low_title:
                errors.append(f"card_{idx}_bad_title_word:{title}")

        if len(title.split()) > 5:
            errors.append(f"card_{idx}_title_too_long:{title}")

        if not card.get("message"):
            errors.append(f"card_{idx}_missing_message")

        if len(card.get("bullets", [])) < 3:
            errors.append(f"card_{idx}_few_bullets")

    qas = pack.get("qas", [])

    if len(qas) < 8:
        errors.append("qas_less_than_8")

    for idx, qa in enumerate(qas):
        question = str(qa.get("question", "")).strip()
        answer = str(qa.get("answer", "")).strip()

        if not question.endswith("?"):
            errors.append(f"qa_{idx}_question_no_question_mark")

        for bad in BAD_QUESTION_FRAGMENTS:
            if bad.lower() in question.lower():
                errors.append(f"qa_{idx}_bad_question:{question}")

        if len(answer.split()) < 5:
            errors.append(f"qa_{idx}_answer_too_short")

    test = pack.get("test", [])

    if len(test) < 6:
        errors.append("test_less_than_6")

    correct_indexes = []

    for idx, item in enumerate(test):
        options = item.get("options", [])
        correct_index = item.get("correct_index")
        correct_indexes.append(correct_index)

        if len(options) != 4:
            errors.append(f"test_{idx}_options_not_4")

        if len(set(options)) != len(options):
            errors.append(f"test_{idx}_duplicate_options")

        if correct_index not in [0, 1, 2, 3]:
            errors.append(f"test_{idx}_bad_correct_index")

        if options and correct_index in [0, 1, 2, 3]:
            if options[correct_index] != item.get("answer"):
                errors.append(f"test_{idx}_correct_index_mismatch")

        if not item.get("question", "").endswith("?"):
            errors.append(f"test_{idx}_question_no_question_mark")

    if len(set(correct_indexes)) < 2:
        errors.append("correct_index_not_mixed")

    if float(pack.get("elapsed_ms", 9999.0)) > 35.0:
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
        "benchmark": "mini_llm_study_pack_v2_quality",
        "status": status,
        "errors": errors,
        "total_ms": total_ms,
        "pack_elapsed_ms": pack.get("elapsed_ms"),
        "counts": pack.get("counts", {}),
        "summary": pack.get("summary", {}),
        "cards": pack.get("cards", []),
        "qas": pack.get("qas", []),
        "test": pack.get("test", []),
        "quality_checks": {
            "bad_question_fragments_blocked": BAD_QUESTION_FRAGMENTS,
            "bad_title_words_blocked": BAD_TITLE_WORDS,
            "correct_index_mixed": len(set([item.get("correct_index") for item in pack.get("test", [])])) >= 2,
        },
        "limits": [
            "Study Pack V2 structured/extractive.",
            "Non è ancora LLM neurale generativo.",
            "Migliora qualità linguistica rispetto a V1.",
            "Mantiene generazione ultra rapida.",
        ],
    }

    data_dir = root / "mini_llm/data/fast_runtime"
    report_dir = root / "mini_llm/reports"

    data_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)

    json_path = data_dir / "mini_llm_study_pack_v2_quality_benchmark.json"
    md_path = report_dir / "mini_llm_study_pack_v2_quality_benchmark.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    lines = [
        "# Mini LLM Study Pack V2 Quality Benchmark",
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
        f"- Domande test: `{pack.get('counts', {}).get('test_questions')}`",
        "",
        "## Migliorie V2",
        "",
        "- Domande più naturali in italiano.",
        "- Titoli card meno meccanici.",
        "- Risposta corretta mescolata nel test.",
        "- Quality gate contro formule brutte della V1.",
        "",
        "## Riassunto esempio",
        "",
        str(pack.get("summary", {}).get("summary", "")),
        "",
        "## Card esempio",
        "",
    ]

    for card in pack.get("cards", [])[:4]:
        lines.extend(
            [
                f"### {card.get('title')}",
                "",
                str(card.get("message", "")),
                "",
            ]
        )

    lines.extend(["## Q&A esempio", ""])

    for qa in pack.get("qas", [])[:5]:
        lines.extend(
            [
                f"**D:** {qa.get('question')}",
                "",
                f"**R:** {qa.get('answer')}",
                "",
            ]
        )

    lines.extend(["## Test esempio", ""])

    for item in pack.get("test", [])[:4]:
        lines.append(f"**Domanda:** {item.get('question')}")
        lines.append("")
        for option_index, option in enumerate(item.get("options", []), start=1):
            lines.append(f"{option_index}. {option}")
        lines.append("")
        lines.append(f"Corretto interno: `{item.get('correct_index')}`")
        lines.append("")

    lines.extend(
        [
            "## Limiti",
            "",
            "- Non è ancora LLM neurale generativo.",
            "- Usa frasi reali del documento.",
            "- Non inventa concetti fuori dal testo.",
            "- È il livello qualità veloce prima del collegamento CLI/LLM.",
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
