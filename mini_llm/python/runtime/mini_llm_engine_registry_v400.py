#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import json
import subprocess
import datetime


ROOT = Path(__file__).resolve().parents[3]


def exists(path):
    return (ROOT / path).exists()


def git_log():
    try:
        out = subprocess.check_output(
            [
                "git",
                "log",
                "--oneline",
                "--decorate",
                "--all",
                "--grep=mini LLM",
                "--grep=mini_llm",
                "--grep=current",
                "--grep=study",
                "--grep=V3.9",
                "-n",
                "80",
            ],
            cwd=ROOT,
            text=True,
            stderr=subprocess.STDOUT,
        )
        return out.strip().splitlines()
    except Exception as exc:
        return [f"GIT_LOG_ERROR: {exc}"]


ENGINES = [
    {
        "id": "long_document_rag_v39",
        "path": "mini_llm/python/runtime/mini_llm_long_document_rag_v39.py",
        "role": "RAG documenti lunghi base",
        "decision": "RIUSARE_CON_CONTROLLI",
        "reason": "Base storica per documenti lunghi; non deve essere buttata, ma va passata da quality gate finale.",
    },
    {
        "id": "long_document_rag_v391_semantic_repair",
        "path": "mini_llm/python/runtime/mini_llm_long_document_rag_v391_semantic_repair.py",
        "role": "Riparazione semantica RAG documenti lunghi",
        "decision": "RIUSARE_CON_CONTROLLI",
        "reason": "Motore successivo al V3.9; utile per recupero/semantica, ma non basta da solo a certificare qualità output.",
    },
    {
        "id": "real_quality_gate_v392",
        "path": "mini_llm/data/fast_runtime/mini_llm_real_quality_gate_v392_validation.json",
        "role": "Quality gate reale V3.9.2",
        "decision": "RIUSARE_E_RAFFERZARE",
        "reason": "Checkpoint qualità reale già presente; va rafforzato su output visibile finale.",
    },
    {
        "id": "real_output_cleaner_v3931",
        "path": "mini_llm/data/fast_runtime/mini_llm_practical_real_test_v393_clean_validation.json",
        "role": "Pulizia output reale V3.9.3.1",
        "decision": "RIUSARE_CON_REGRESSIONI",
        "reason": "Pulizia utile, ma deve evitare di distruggere segnali di dominio nei testi corti.",
    },
    {
        "id": "universal_core_split_v394u",
        "path": "mini_llm/python/runtime/universal/mini_llm_universal_linguistic_core_v394u.py",
        "role": "Core linguistico universale separato",
        "decision": "RIUSARE",
        "reason": "Blocco universale già separato; deve diventare parte dell'orchestratore.",
    },
    {
        "id": "universal_relevance_core_v394u",
        "path": "mini_llm/python/runtime/universal/mini_llm_universal_relevance_core_v394u.py",
        "role": "Core rilevanza universale",
        "decision": "RIUSARE",
        "reason": "Serve per domanda-risposta e recupero passaggi rilevanti.",
    },
    {
        "id": "universal_question_core_v394u",
        "path": "mini_llm/python/runtime/universal/mini_llm_universal_question_core_v394u.py",
        "role": "Core domande universale",
        "decision": "RIUSARE",
        "reason": "Serve per domande studio, quiz e risposta guidata.",
    },
    {
        "id": "domain_profiles_v394u",
        "path": "mini_llm/python/runtime/domain_profiles/mini_llm_domain_profile_registry_v394u.py",
        "role": "Registro profili dominio",
        "decision": "RIUSARE",
        "reason": "Serve per riconoscere informatica, business, curriculum, scienza, sport e generico.",
    },
    {
        "id": "universal_llm_bridge_v395",
        "path": "mini_llm/python/runtime/mini_llm_universal_llm_bridge_v395.py",
        "role": "Bridge universale mini LLM",
        "decision": "RIUSARE_COME_ADAPTER",
        "reason": "Serve come ponte tra core universale e motori di generazione.",
    },
    {
        "id": "universal_current_engine_v396",
        "path": "mini_llm/python/runtime/mini_llm_universal_current_engine_v396.py",
        "role": "Current engine universale",
        "decision": "RIUSARE_COME_CUORE_CURRENT",
        "reason": "Checkpoint forte: documento reale e multi-dominio già validati; da collegare al quality gate finale.",
    },
    {
        "id": "study_pack_universal_v397",
        "path": "mini_llm/python/runtime/mini_llm_universal_study_pack_v4.py",
        "role": "Study pack universale V4",
        "decision": "RIUSARE_PER_CARD_STUDIO_DOMANDE",
        "reason": "Checkpoint V3.9.7; utile per card, domande studio e materiale didattico.",
    },
    {
        "id": "study_pack_current",
        "path": "mini_llm/python/runtime/mini_llm_study_pack_current.py",
        "role": "Study pack current",
        "decision": "RIUSARE_SE_PASSA_GATE",
        "reason": "Motore current già presente; va usato solo se il quality gate finale approva l'output.",
    },
    {
        "id": "fast_qa_summary_current",
        "path": "mini_llm/python/runtime/fast_qa_summary_current.py",
        "role": "QA/summary veloce current",
        "decision": "RIUSARE_PER_VELOCITA",
        "reason": "Serve per benchmark velocità e risposte rapide, ma deve passare dal controllo qualità.",
    },
    {
        "id": "natural_sentence_v35_family",
        "path": "mini_llm/data/inference_v31_natural/inference_engine_v31_natural_outputs.json",
        "role": "Vecchia generazione frase naturale",
        "decision": "QUARANTENA_TEST_NEGATIVO",
        "reason": "Famiglia da usare come regressione negativa: non deve più passare output grammaticalmente assurdi.",
    },
]


def build_registry():
    registry = {
        "registry": "mini_llm_engine_registry_v400",
        "created_at": datetime.datetime.now().isoformat(timespec="seconds"),
        "purpose": "Catalogare i motori mini LLM già costruiti senza buttare il lavoro fatto.",
        "rules": [
            "Non ripartire da zero.",
            "Non buttare i motori V esistenti.",
            "Riusare i blocchi buoni.",
            "Mettere in quarantena i motori che producono output brutto.",
            "Il PASS finale deve dipendere dall'output generato, non dal file presente.",
        ],
        "engines": [],
        "git_log": git_log(),
    }

    for engine in ENGINES:
        item = dict(engine)
        item["exists"] = exists(engine["path"])
        registry["engines"].append(item)

    counts = {}
    for engine in registry["engines"]:
        decision = engine["decision"]
        counts[decision] = counts.get(decision, 0) + 1

    registry["summary"] = {
        "total_engines_registered": len(registry["engines"]),
        "existing_files": sum(1 for e in registry["engines"] if e["exists"]),
        "missing_files": sum(1 for e in registry["engines"] if not e["exists"]),
        "decisions": counts,
    }

    return registry


def write_markdown(registry, path):
    lines = []
    lines.append("# Mini LLM Engine Registry V400")
    lines.append("")
    lines.append("Questo report non crea un nuovo motore da zero.")
    lines.append("")
    lines.append("Serve a catalogare il lavoro già fatto sui motori V del mini LLM e a decidere cosa riusare, cosa rafforzare e cosa mettere in quarantena.")
    lines.append("")
    lines.append("## Regole operative")
    lines.append("")
    for rule in registry["rules"]:
        lines.append(f"- {rule}")
    lines.append("")
    lines.append("## Sintesi")
    lines.append("")
    for k, v in registry["summary"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines.append("")
    lines.append("## Motori registrati")
    lines.append("")
    for e in registry["engines"]:
        status = "PRESENTE" if e["exists"] else "MANCANTE"
        lines.append(f"### {e['id']}")
        lines.append("")
        lines.append(f"- File: `{e['path']}`")
        lines.append(f"- Stato file: `{status}`")
        lines.append(f"- Ruolo: {e['role']}")
        lines.append(f"- Decisione: `{e['decision']}`")
        lines.append(f"- Motivo: {e['reason']}")
        lines.append("")
    lines.append("## Git log rilevante")
    lines.append("")
    for row in registry["git_log"]:
        lines.append(f"- `{row}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def main():
    out_dir = ROOT / "reports" / "mini_llm_v400_registry"
    out_dir.mkdir(parents=True, exist_ok=True)

    registry = build_registry()

    json_path = out_dir / "mini_llm_engine_registry_v400.json"
    md_path = out_dir / "mini_llm_engine_registry_v400.md"

    json_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2), encoding="utf-8")
    write_markdown(registry, md_path)

    print("REGISTRY_CREATED")
    print(f"JSON: {json_path}")
    print(f"MD: {md_path}")
    print(f"Motori registrati: {registry['summary']['total_engines_registered']}")
    print(f"File presenti: {registry['summary']['existing_files']}")
    print(f"File mancanti: {registry['summary']['missing_files']}")


if __name__ == "__main__":
    main()
