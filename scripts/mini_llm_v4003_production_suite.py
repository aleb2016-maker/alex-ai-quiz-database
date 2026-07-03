#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

ENGINE = ROOT / "mini_llm/python/runtime/mini_llm_universal_orchestrator_v4002.py"

OUT_DIR = ROOT / "reports/mini_llm_v4003"


DOCUMENTS = [
    {
        "id": "ai_generativa",
        "path": "rag/documenti/documento_ai_generativa_test_rag.md",
        "question": "Quali rischi o limiti vengono indicati dal documento sull'intelligenza artificiale generativa?",
    },
    {
        "id": "informatica_sicurezza_rag",
        "path": "rag/documenti/documento_rag_sicurezza_informatica_aziendale.md",
        "question": "Quali sono i rischi principali e le regole operative indicate dal documento?",
    },
    {
        "id": "business_v396",
        "path": "mini_llm/data/real_tests/test_v396_current_engine/business.md",
        "question": "Quali sono i punti principali del documento business?",
    },
    {
        "id": "curriculum_v396",
        "path": "mini_llm/data/real_tests/test_v396_current_engine/curriculum.md",
        "question": "Quali competenze, esperienze o elementi importanti emergono dal curriculum?",
    },
    {
        "id": "informatics_v396",
        "path": "mini_llm/data/real_tests/test_v396_current_engine/informatics.md",
        "question": "Quali rischi o concetti informatici principali vengono descritti?",
    },
    {
        "id": "science_v396",
        "path": "mini_llm/data/real_tests/test_v396_current_engine/science.txt",
        "question": "Quali concetti scientifici principali vengono spiegati?",
    },
    {
        "id": "sport_v396",
        "path": "mini_llm/data/real_tests/test_v396_current_engine/sport.txt",
        "question": "Quali indicazioni principali emergono dal documento sportivo?",
    },
]


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def status_of(block):
    if not isinstance(block, dict):
        return "MISSING"
    return block.get("status", "MISSING")


def errors_of(block):
    if not isinstance(block, dict):
        return []
    quality = block.get("quality", {})
    if not isinstance(quality, dict):
        return []
    return quality.get("errors", [])


def run_one(doc):
    source = ROOT / doc["path"]

    result_json = OUT_DIR / f"{doc['id']}.json"

    if not source.exists():
        return {
            "id": doc["id"],
            "source": doc["path"],
            "status": "SOURCE_MISSING",
            "error": f"File mancante: {doc['path']}",
        }

    cmd = [
        sys.executable,
        str(ENGINE),
        "--input",
        doc["path"],
        "--question",
        doc["question"],
        "--out",
        str(result_json.relative_to(ROOT)),
    ]

    completed = subprocess.run(
        cmd,
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if completed.returncode != 0:
        return {
            "id": doc["id"],
            "source": doc["path"],
            "status": "ENGINE_ERROR",
            "stdout": completed.stdout,
            "stderr": completed.stderr,
        }

    data = read_json(result_json)

    summary = data.get("summary", {})
    answer = data.get("answer", {})
    cards = data.get("cards", {})
    speed = data.get("speed", {})
    profile = data.get("profile", {})

    return {
        "id": doc["id"],
        "source": doc["path"],
        "question": doc["question"],
        "json": str(result_json.relative_to(ROOT)),
        "md": str(result_json.with_suffix(".md").relative_to(ROOT)),
        "status": "PRODUCED",
        "profile": {
            "title": profile.get("title"),
            "domain": profile.get("domain"),
            "input_words": profile.get("input_words"),
            "sections": profile.get("sections"),
            "concepts": profile.get("concepts", [])[:10],
        },
        "outputs": {
            "summary": {
                "status": status_of(summary),
                "errors": errors_of(summary),
                "metrics": summary.get("quality", {}).get("metrics", {}),
            },
            "answer": {
                "status": status_of(answer),
                "errors": errors_of(answer),
                "metrics": answer.get("quality", {}).get("metrics", {}),
            },
            "cards": {
                "status": status_of(cards),
                "errors": errors_of(cards),
                "cards_count": len(cards.get("cards", [])) if isinstance(cards, dict) else 0,
            },
        },
        "speed": speed,
    }


def write_markdown(results):
    lines = []
    lines.append("# Mini LLM V400.3 - Produzione multi-documento")
    lines.append("")
    lines.append("Questo report produce output reali su più documenti già presenti nel progetto.")
    lines.append("")
    lines.append("Non modifica UI, pulsanti, PDF o grafica.")
    lines.append("")

    total = len(results)
    produced = sum(1 for r in results if r.get("status") == "PRODUCED")
    lines.append("## Sintesi")
    lines.append("")
    lines.append(f"- Documenti testati: `{total}`")
    lines.append(f"- Documenti prodotti: `{produced}`")
    lines.append("")

    lines.append("## Risultati")
    lines.append("")

    for r in results:
        lines.append(f"### {r.get('id')}")
        lines.append("")
        lines.append(f"- Source: `{r.get('source')}`")
        lines.append(f"- Status suite: `{r.get('status')}`")

        if r.get("status") != "PRODUCED":
            lines.append(f"- Errore: `{r.get('error', '')}`")
            lines.append("")
            continue

        profile = r.get("profile", {})
        outputs = r.get("outputs", {})

        lines.append(f"- Titolo: {profile.get('title')}")
        lines.append(f"- Dominio: {profile.get('domain')}")
        lines.append(f"- Parole input: `{profile.get('input_words')}`")
        lines.append(f"- Sezioni: `{profile.get('sections')}`")
        lines.append(f"- Concetti: {', '.join(profile.get('concepts', []))}")
        lines.append(f"- Summary: `{outputs.get('summary', {}).get('status')}` errori `{outputs.get('summary', {}).get('errors')}`")
        lines.append(f"- Answer: `{outputs.get('answer', {}).get('status')}` errori `{outputs.get('answer', {}).get('errors')}`")
        lines.append(f"- Cards: `{outputs.get('cards', {}).get('status')}` errori `{outputs.get('cards', {}).get('errors')}` count `{outputs.get('cards', {}).get('cards_count')}`")
        lines.append(f"- Tempo: `{r.get('speed', {}).get('elapsed_ms')}` ms")
        lines.append(f"- Output MD: `{r.get('md')}`")
        lines.append("")

    (OUT_DIR / "production_suite_v4003.md").write_text("\n".join(lines), encoding="utf-8")


def write_portfolio(results):
    lines = []
    lines.append("# Mini LLM V400.3 - Portfolio output generati")
    lines.append("")

    for r in results:
        if r.get("status") != "PRODUCED":
            continue

        md_path = ROOT / r["md"]
        lines.append(f"# Documento: {r['id']}")
        lines.append("")
        lines.append(f"Source: `{r['source']}`")
        lines.append("")

        if md_path.exists():
            lines.append(md_path.read_text(encoding="utf-8"))
        else:
            lines.append("_Markdown output mancante._")

        lines.append("\n---\n")

    (OUT_DIR / "portfolio_output_v4003.md").write_text("\n".join(lines), encoding="utf-8")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    if not ENGINE.exists():
        print(f"ENGINE_MISSING: {ENGINE}")
        sys.exit(1)

    results = []

    for doc in DOCUMENTS:
        print(f"=== PRODUCO {doc['id']} ===")
        result = run_one(doc)
        results.append(result)
        print(result.get("status"))

    summary_json = OUT_DIR / "production_suite_v4003.json"
    summary_json.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    write_markdown(results)
    write_portfolio(results)

    print("")
    print("PRODUCTION_SUITE_DONE")
    print(f"JSON: {summary_json}")
    print(f"MD: {OUT_DIR / 'production_suite_v4003.md'}")
    print(f"PORTFOLIO: {OUT_DIR / 'portfolio_output_v4003.md'}")


if __name__ == "__main__":
    main()
