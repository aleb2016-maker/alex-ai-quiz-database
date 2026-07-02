#!/usr/bin/env python3
"""
Mini LLM Real Quality Gate V3.9.2.

Gate diagnostico per impedire falsi PASS sui test pratici reali.

Controlla separatamente:
- testi/frasi;
- titoli card;
- domande;
- opzioni test.

Blocca:
- heading Markdown dentro output;
- frammenti da elenco tipo "al dominio reale; - ...";
- metadati del documento usati come contenuto;
- domande innaturali;
- opzioni troncate;
- frasi fuse o spezzate.

Non genera contenuto.
Non modifica il motore.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List


BAD_FRAGMENTS = [
    "# Documento",
    "## Scopo",
    "Documento RAG di test",
    "fonte di prova",
    "progetto quiz",
    "al dominio reale",
    "da cui.",
    "codici o dati.",
    "documento non è pensato come",
]


BAD_QUESTION_PATTERNS = [
    r"^Che cosa usa non riguarda",
    r"^Che cosa può fare il documento non",
    r"^Che cosa contengono una buona regola",
    r"^Quale informazione importante viene data su al dominio",
    r"^Quale informazione importante viene data su #",
    r"^Che cos'è malware e allegati pericolosi Il malware",
]


BAD_OPTION_ENDINGS = {
    "da cui",
    "codici o dati",
    "documenti interni o dati",
}


BAD_TEXT_STARTS = {
    "al", "della", "dello", "delle", "degli", "dei", "del",
    "pagina", "e", "o", "ma", "con", "per",
}


BAD_TEXT_ENDINGS = {
    "alla", "allo", "alle", "agli", "al", "a", "di", "del",
    "della", "dello", "delle", "e", "o", "ma", "che", "con",
    "per", "tra", "fra", "cui",
}


BAD_TITLE_STARTS = {
    "al", "della", "dello", "delle", "degli", "dei", "del",
    "pagina", "#",
}


def normalize(text: Any) -> str:
    return " ".join(str(text or "").replace("\u00a0", " ").strip().split())


def first_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return re.sub(r"^[\"'“”‘’(\[]+", "", words[0]).lower().strip(".,;:!?")


def last_word(text: str) -> str:
    words = normalize(text).split()

    if not words:
        return ""

    return words[-1].lower().strip(".,;:!?\"'“”‘’)]}")


def split_sentences(text: str) -> List[str]:
    return [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", normalize(text))
        if sentence.strip()
    ]


def contains_bad_fragment(text: str) -> List[str]:
    errors = []
    low = text.lower()

    for fragment in BAD_FRAGMENTS:
        if fragment.lower() in low:
            errors.append(f"bad_fragment:{fragment}")

    return errors


def check_title(title: str, label: str) -> List[str]:
    errors: List[str] = []
    value = normalize(title)

    if not value:
        errors.append(f"{label}:empty_title")
        return errors

    words = value.split()

    if len(words) < 2:
        errors.append(f"{label}:title_too_short:{value[:120]}")

    if len(words) > 8:
        errors.append(f"{label}:title_too_long:{value[:160]}")

    errors.extend([f"{label}:{err}" for err in contains_bad_fragment(value)])

    if first_word(value) in BAD_TITLE_STARTS:
        errors.append(f"{label}:bad_title_start:{value[:120]}")

    if value.endswith((".", "?", "!")):
        errors.append(f"{label}:title_has_terminal_punctuation:{value[:120]}")

    if re.search(r"[#*_`<>]", value):
        errors.append(f"{label}:title_has_markup:{value[:120]}")

    return errors


def check_statement(text: str, label: str) -> List[str]:
    errors: List[str] = []
    value = normalize(text)

    if not value:
        errors.append(f"{label}:empty")
        return errors

    errors.extend([f"{label}:{err}" for err in contains_bad_fragment(value)])

    for sentence in split_sentences(value):
        if sentence.endswith("?"):
            continue

        words = sentence.split()

        if len(words) < 6:
            errors.append(f"{label}:too_short:{sentence[:120]}")

        if len(words) > 55:
            errors.append(f"{label}:too_long:{sentence[:120]}")

        if first_word(sentence) in BAD_TEXT_STARTS:
            errors.append(f"{label}:bad_start:{sentence[:120]}")

        if last_word(sentence) in BAD_TEXT_ENDINGS:
            errors.append(f"{label}:bad_ending:{sentence[:120]}")

        if not re.search(r"[.!]$", sentence):
            errors.append(f"{label}:missing_terminal_punctuation:{sentence[:120]}")

        if re.search(r"\b(dati|credenziali|backup|informazioni|password)\s+(Il|La|I|Gli|Le|Un|Una|L')\b", sentence):
            errors.append(f"{label}:fused_sentence:{sentence[:120]}")

    return errors


def check_question(question: str, label: str) -> List[str]:
    errors: List[str] = []
    q = normalize(question)

    if not q:
        errors.append(f"{label}:empty_question")
        return errors

    if not q.endswith("?"):
        errors.append(f"{label}:missing_question_mark:{q[:120]}")

    if len(q.split()) < 5:
        errors.append(f"{label}:question_too_short:{q[:120]}")

    if len(q.split()) > 18:
        errors.append(f"{label}:question_too_long:{q[:160]}")

    for pattern in BAD_QUESTION_PATTERNS:
        if re.search(pattern, q, flags=re.IGNORECASE):
            errors.append(f"{label}:bad_question_pattern:{pattern}:{q[:160]}")

    errors.extend([f"{label}:{err}" for err in contains_bad_fragment(q)])

    if first_word(q) in {"al", "della", "pagina", "#"}:
        errors.append(f"{label}:bad_question_start:{q[:120]}")

    return errors


def check_option(option: str, label: str) -> List[str]:
    errors: List[str] = []
    value = normalize(option)

    if not value:
        errors.append(f"{label}:empty_option")
        return errors

    if len(value.split()) < 2:
        errors.append(f"{label}:option_too_short:{value[:120]}")

    if len(value.split()) > 24:
        errors.append(f"{label}:option_too_long:{value[:160]}")

    errors.extend([f"{label}:{err}" for err in contains_bad_fragment(value)])

    cleaned = value.lower().rstrip(".!?;: ")

    if any(cleaned.endswith(item) for item in BAD_OPTION_ENDINGS):
        errors.append(f"{label}:truncated_option:{value[:160]}")

    if first_word(value) in BAD_TEXT_STARTS:
        errors.append(f"{label}:bad_option_start:{value[:120]}")

    if last_word(value) in BAD_TEXT_ENDINGS:
        errors.append(f"{label}:bad_option_ending:{value[:120]}")

    if re.search(r"\b(dati|credenziali|backup|informazioni|password)\s+(Il|La|I|Gli|Le|Un|Una|L')\b", value):
        errors.append(f"{label}:fused_option:{value[:120]}")

    return errors


def validate_report(report: Dict[str, Any]) -> Dict[str, Any]:
    errors: List[str] = []

    if report.get("status") != "PASS":
        errors.append(f"input_report_not_pass:{report.get('status')}")

    diagnostics = report.get("diagnostics", {})

    if diagnostics.get("engine") != "mini_llm_long_document_rag_v391_semantic_repair":
        errors.append(f"wrong_engine:{diagnostics.get('engine')}")

    if diagnostics.get("sentences", 0) < 8:
        errors.append(f"too_few_sentences:{diagnostics.get('sentences')}")

    for index, answer in enumerate(report.get("answers", []), start=1):
        errors.extend(check_statement(str(answer.get("answer", "")), f"answer_{index}"))

    summary = report.get("progressive_summary", {})
    errors.extend(check_statement(str(summary.get("quality_summary", "")), "quality_summary"))
    errors.extend(check_statement(str(summary.get("brief_summary", "")), "brief_summary"))

    study = report.get("study_pack", {})
    pack = study.get("study_pack", {}) if isinstance(study.get("study_pack", {}), dict) else {}

    pack_summary = pack.get("summary", {})
    errors.extend(check_statement(str(pack_summary.get("summary", "")), "study_pack_summary"))

    for index, card in enumerate(pack.get("cards", []), start=1):
        errors.extend(check_title(str(card.get("title", "")), f"card_{index}_title"))
        errors.extend(check_statement(str(card.get("message", "")), f"card_{index}_message"))

    for index, qa in enumerate(pack.get("qas", []), start=1):
        errors.extend(check_question(str(qa.get("question", "")), f"qa_{index}_question"))
        errors.extend(check_statement(str(qa.get("answer", "")), f"qa_{index}_answer"))

    for index, item in enumerate(pack.get("student_test", []), start=1):
        errors.extend(check_question(str(item.get("question", "")), f"test_{index}_question"))

        options = item.get("options", [])

        if not isinstance(options, list) or len(options) != 4:
            errors.append(f"test_{index}:wrong_options_count:{len(options) if isinstance(options, list) else 'not_list'}")
            continue

        for option_index, option in enumerate(options, start=1):
            errors.extend(check_option(str(option), f"test_{index}_option_{option_index}"))

    status = "PASS" if not errors else "FAIL"

    return {
        "gate": "mini_llm_real_quality_gate_v392",
        "status": status,
        "errors": errors,
        "input_file": report.get("file"),
        "input_test_status": report.get("status"),
        "diagnostics": diagnostics,
        "limits": [
            "Gate reale su report pratico.",
            "Non genera contenuto.",
            "Blocca falsi PASS.",
            "Controlla titoli, frasi, domande e opzioni separatamente.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Valida un report pratico reale del mini LLM con gate V3.9.2."
    )

    parser.add_argument("report_json", help="Path practical_real_test_v391_report.json")
    parser.add_argument("--out", default="", help="Output JSON opzionale.")

    args = parser.parse_args()

    report_path = Path(args.report_json).expanduser().resolve()

    if not report_path.exists():
        print(
            json.dumps(
                {
                    "gate": "mini_llm_real_quality_gate_v392",
                    "status": "ERROR",
                    "error": f"Report non trovato: {report_path}",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 1

    report = json.loads(report_path.read_text(encoding="utf-8"))
    validation = validate_report(report)

    output = json.dumps(validation, ensure_ascii=False, indent=2)
    print(output)

    if args.out:
        out_path = Path(args.out).expanduser().resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output + "\n", encoding="utf-8")

    return 0 if validation.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
