#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

SUITE_JSON = ROOT / "reports/mini_llm_v4005/production_suite_v4005.json"
SUITE_MD = ROOT / "reports/mini_llm_v4005/production_suite_v4005.md"
PORTFOLIO_MD = ROOT / "reports/mini_llm_v4005/portfolio_output_v4005.md"
REPORT_MD = ROOT / "reports/mini_llm_v4005/validazione_finale_v4005.md"


EXPECTED = {
    "ai_generativa": {
        "domain": "intelligenza artificiale generativa e RAG",
        "summary": "GENERATED",
        "answer": "GENERATED",
        "cards": "GENERATED",
    },
    "informatica_sicurezza_rag": {
        "domain": "sicurezza informatica",
        "summary": "GENERATED",
        "answer": "GENERATED",
        "cards": "GENERATED",
    },
    "business_v396": {
        "domain": "documento aziendale",
        "summary": "GENERATED_SHORT",
        "answer": "GENERATED_SHORT",
        "cards": "GENERATED_SHORT",
    },
    "curriculum_v396": {
        "domain": "curriculum vitae",
        "summary": "GENERATED_SHORT",
        "answer": "GENERATED_SHORT",
        "cards": "GENERATED_SHORT",
    },
    "informatics_v396": {
        "domain": "sicurezza informatica",
        "summary": "GENERATED_SHORT",
        "answer": "GENERATED_SHORT",
        "cards": "GENERATED_SHORT",
    },
    "science_v396": {
        "domain": "scientifico",
        "summary": "GENERATED_SHORT",
        "answer": "GENERATED_SHORT",
        "cards": "GENERATED_SHORT",
    },
    "sport_v396": {
        "domain": "sport e allenamento",
        "summary": "GENERATED_SHORT",
        "answer": "GENERATED_SHORT",
        "cards": "GENERATED_SHORT",
    },
}


def fail(errors, code, detail):
    errors.append(f"{code}: {detail}")


def main():
    errors = []
    warnings = []

    for p in [SUITE_JSON, SUITE_MD, PORTFOLIO_MD]:
        if not p.exists():
            fail(errors, "FILE_MANCANTE", str(p))

    if errors:
        print("VALIDATION_FAILED")
        for e in errors:
            print("-", e)
        sys.exit(1)

    data = json.loads(SUITE_JSON.read_text(encoding="utf-8"))
    by_id = {item.get("id"): item for item in data}

    if len(data) != 7:
        fail(errors, "NUMERO_DOCUMENTI_ERRATO", f"Attesi 7, trovati {len(data)}")

    for doc_id, expected in EXPECTED.items():
        item = by_id.get(doc_id)

        if not item:
            fail(errors, "DOCUMENTO_MANCANTE", doc_id)
            continue

        profile = item.get("profile", {})
        outputs = item.get("outputs", {})

        domain = profile.get("domain")
        if domain != expected["domain"]:
            fail(errors, "DOMINIO_ERRATO", f"{doc_id}: atteso {expected['domain']}, trovato {domain}")

        for key in ["summary", "answer", "cards"]:
            block = outputs.get(key, {})
            status = block.get("status")
            expected_status = expected[key]

            if status != expected_status:
                fail(errors, "STATUS_ERRATO", f"{doc_id}/{key}: atteso {expected_status}, trovato {status}")

            q_errors = block.get("errors", [])
            if q_errors:
                fail(errors, "QUALITY_ERRORS_PRESENTI", f"{doc_id}/{key}: {q_errors}")

        if outputs.get("cards", {}).get("cards_count", 0) < 1:
            fail(errors, "CARD_ASSENTI", doc_id)

        if item.get("status") != "PRODUCED":
            fail(errors, "SUITE_STATUS_NON_PRODOTTO", f"{doc_id}: {item.get('status')}")

    portfolio = PORTFOLIO_MD.read_text(encoding="utf-8")

    if "Mini LLM V400.3 - Portfolio output generati" in portfolio:
        fail(errors, "INTESTAZIONE_PORTFOLIO_VECCHIA", "Il portfolio contiene ancora V400.3")

    if "Mini LLM V400.5 - Portfolio output generati" not in portfolio:
        fail(errors, "INTESTAZIONE_PORTFOLIO_MANCANTE", "Manca intestazione V400.5")

    banned_fragments = [
        "sicurezza informatica aziendale attraverso il tema intelligenza",
        "artificiale generativa tecnologia",
        "generativa tecnologia permette",
        "qualità proporzionato ridotto",
        "proporzionato ridotto poche",
        "Riassunto: sicurezza informatica aziendale",
    ]

    for frag in banned_fragments:
        if frag.lower() in portfolio.lower():
            fail(errors, "FRAMMENTO_BRUTTO_PRESENTE", frag)

    lines = []
    lines.append("# Validazione finale Mini LLM V400.5")
    lines.append("")
    lines.append("## Esito")
    lines.append("")
    lines.append(f"- Stato: `{'FAILED' if errors else 'OK'}`")
    lines.append(f"- Documenti controllati: `{len(data)}`")
    lines.append("")
    lines.append("## Controlli eseguiti")
    lines.append("")
    lines.append("- Presenza JSON suite, Markdown suite e portfolio.")
    lines.append("- 7 documenti prodotti.")
    lines.append("- Dominio corretto per ogni documento.")
    lines.append("- Stato summary/answer/cards corretto.")
    lines.append("- Nessun errore qualità nei blocchi finali.")
    lines.append("- Almeno una card per documento.")
    lines.append("- Intestazione portfolio aggiornata a V400.5.")
    lines.append("- Assenza frammenti brutti noti.")
    lines.append("")
    lines.append("## Dettaglio documenti")
    lines.append("")

    for doc_id in EXPECTED:
        item = by_id.get(doc_id, {})
        profile = item.get("profile", {})
        outputs = item.get("outputs", {})
        lines.append(f"### {doc_id}")
        lines.append("")
        lines.append(f"- Dominio: `{profile.get('domain')}`")
        lines.append(f"- Parole: `{profile.get('input_words')}`")
        lines.append(f"- Summary: `{outputs.get('summary', {}).get('status')}`")
        lines.append(f"- Answer: `{outputs.get('answer', {}).get('status')}`")
        lines.append(f"- Cards: `{outputs.get('cards', {}).get('status')}` count `{outputs.get('cards', {}).get('cards_count')}`")
        lines.append("")

    if errors:
        lines.append("## Errori")
        lines.append("")
        for e in errors:
            lines.append(f"- {e}")
        lines.append("")

    if warnings:
        lines.append("## Warning")
        lines.append("")
        for w in warnings:
            lines.append(f"- {w}")
        lines.append("")

    REPORT_MD.write_text("\n".join(lines), encoding="utf-8")

    if errors:
        print("VALIDATION_FAILED")
        for e in errors:
            print("-", e)
        print("Report:", REPORT_MD)
        sys.exit(1)

    print("VALIDATION_OK")
    print("Report:", REPORT_MD)


if __name__ == "__main__":
    main()
