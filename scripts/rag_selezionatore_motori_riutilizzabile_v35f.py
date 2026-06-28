#!/usr/bin/env python3
"""
RAG Selezionatore Motori Riutilizzabile V3.5F

Scopo:
decidere quali motori RAG usare in base al compito richiesto dall'utente.

Livelli già disponibili:
- V3.5B bridge motori quiz
- V3.5C motore didattico
- V3.5D motore test separato
- V3.5E orchestratore completo

Questo modulo è pensato per progetti futuri:
un'app, una pagina web o un agente può chiedere:
"voglio un test", "voglio card", "voglio PDF", "voglio solo riassunto"
e il selezionatore sceglie il flusso corretto.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]

BASE_V34E = ROOT / "dist/generated/rag_output_kb_clean_v34e/outputs"
BASE_SELECTOR = ROOT / "dist/generated/rag_selezionatore_motori_v35f"

MOTORS = {
    "output_base_v34e": {
        "script": "scripts/rag_genera_output_da_kb_clean_v34e.py",
        "ruolo": "genera output base da Knowledge Base pulita",
    },
    "bridge_quiz_v35b": {
        "script": "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
        "ruolo": "controlla test e testi nei motori qualità quiz esistenti",
    },
    "didattico_v35c": {
        "script": "scripts/rag_motore_didattico_riutilizzabile_v35c.py",
        "ruolo": "migliora card, riassunti, domande studio, fonti, tono e layout",
    },
    "test_v35d": {
        "script": "scripts/rag_motore_test_riutilizzabile_v35d.py",
        "ruolo": "gestisce test, opzioni interne/visibili, risposta corretta e mappa",
    },
    "orchestratore_v35e": {
        "script": "scripts/rag_orchestratore_riutilizzabile_v35e.py",
        "ruolo": "esegue pipeline completa e produce output finale UI/PDF/app",
    },
}


def normalizza(value: str) -> str:
    text = str(value or "").lower()
    text = text.replace("à", "a").replace("è", "e").replace("é", "e")
    text = text.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def slug(value: str) -> str:
    text = normalizza(value)
    return text.replace(" ", "_")[:80] or "compito"


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def write_json(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def classify_task(compito: str) -> dict[str, Any]:
    t = normalizza(compito)

    wants_test = any(k in t for k in [
        "test",
        "quiz",
        "verifica",
        "domande a risposta",
        "risposte multiple",
        "interattivo",
        "punteggio",
    ])

    wants_cards = any(k in t for k in [
        "card",
        "schede",
        "flashcard",
        "carte",
        "grafiche",
    ])

    wants_summary = any(k in t for k in [
        "riassunto",
        "sintesi",
        "riepilogo",
        "abstract",
    ])

    wants_study = any(k in t for k in [
        "domande studio",
        "domande di studio",
        "ripasso",
        "studiare",
        "spiegami",
    ])

    wants_export = any(k in t for k in [
        "pdf",
        "app",
        "download",
        "esporta",
        "ui",
        "pagina",
        "web",
        "pacchetto",
    ])

    wants_all = any(k in t for k in [
        "tutto",
        "completo",
        "pipeline completa",
        "tutti",
        "materiale completo",
    ])

    if wants_all or wants_export:
        return {
            "tipo": "output_completo",
            "output_richiesti": ["riassunto", "card", "test", "domande_studio", "ui_layout"],
            "motori": ["orchestratore_v35e"],
            "perche": "serve un output finale completo e già pronto per UI/PDF/app",
        }

    if wants_test and not (wants_cards or wants_summary or wants_study):
        return {
            "tipo": "solo_test",
            "output_richiesti": ["test"],
            "motori": ["bridge_quiz_v35b", "didattico_v35c", "test_v35d", "bridge_quiz_v35b"],
            "perche": "il test richiede controlli extra su opzioni, risposta corretta, duplicati e bridge quiz",
        }

    if wants_cards and not (wants_test or wants_summary or wants_study):
        return {
            "tipo": "solo_card",
            "output_richiesti": ["card", "ui_layout"],
            "motori": ["didattico_v35c"],
            "perche": "le card richiedono stile, fonti visibili e layout, non il motore test",
        }

    if wants_summary and not (wants_test or wants_cards or wants_study):
        return {
            "tipo": "solo_riassunto",
            "output_richiesti": ["riassunto"],
            "motori": ["didattico_v35c"],
            "perche": "il riassunto richiede tono didattico e pulizia, non opzioni test",
        }

    if wants_study and not (wants_test or wants_cards or wants_summary):
        return {
            "tipo": "solo_domande_studio",
            "output_richiesti": ["domande_studio"],
            "motori": ["didattico_v35c"],
            "perche": "le domande studio richiedono naturalezza e risposta guida, non distrattori quiz",
        }

    if wants_test or wants_cards or wants_summary or wants_study:
        outputs = []
        if wants_summary:
            outputs.append("riassunto")
        if wants_cards:
            outputs.extend(["card", "ui_layout"])
        if wants_test:
            outputs.append("test")
        if wants_study:
            outputs.append("domande_studio")

        motors = ["didattico_v35c"]

        if wants_test:
            motors = ["bridge_quiz_v35b", "didattico_v35c", "test_v35d", "bridge_quiz_v35b"]

        return {
            "tipo": "combinato",
            "output_richiesti": sorted(set(outputs)),
            "motori": motors,
            "perche": "il compito richiede più output; vengono scelti solo i motori necessari",
        }

    return {
        "tipo": "auto_completo_sicuro",
        "output_richiesti": ["riassunto", "card", "test", "domande_studio", "ui_layout"],
        "motori": ["orchestratore_v35e"],
        "perche": "compito non specifico: uso output completo sicuro per non perdere informazioni",
    }


def build_plan(compito: str, documento: str) -> dict[str, Any]:
    decision = classify_task(compito)

    return {
        "ok": True,
        "versione": "rag_selezionatore_motori_riutilizzabile_v35f",
        "creato_il": datetime.now().isoformat(timespec="seconds"),
        "documento": documento,
        "compito": compito,
        "decisione": decision,
        "motori_da_usare": [
            {
                "id": motor_id,
                "script": MOTORS[motor_id]["script"],
                "ruolo": MOTORS[motor_id]["ruolo"],
            }
            for motor_id in decision["motori"]
        ],
        "regole_architetturali": {
            "card_riassunti_domande_studio": "motore didattico V3.5C",
            "test": "motore test V3.5D con bridge quiz V3.5B",
            "output_completo": "orchestratore V3.5E",
        },
    }


def select_fields(data: dict[str, Any], outputs: list[str]) -> dict[str, Any]:
    selected: dict[str, Any] = {
        "versione": "rag_output_selezionato_v35f",
        "output_richiesti": outputs,
        "controlli_qualita": data.get("controlli_qualita", {}),
        "motori_riutilizzabili": data.get("motori_riutilizzabili", {}),
    }

    for field in outputs:
        if field in data:
            selected[field] = data[field]

    if "ui_layout" in outputs and "ui_layout" in data:
        selected["ui_layout"] = data["ui_layout"]

    if "orchestratore_v35e" in data:
        selected["orchestratore_v35e"] = data["orchestratore_v35e"]

    return selected


def execute_plan(plan: dict[str, Any]) -> dict[str, Any]:
    documento = plan["documento"]
    decision = plan["decisione"]
    tipo = decision["tipo"]
    outputs = decision["output_richiesti"]

    out_dir = BASE_SELECTOR / slug(tipo) / documento
    out_dir.mkdir(parents=True, exist_ok=True)

    base_v34e = BASE_V34E / documento / "rag_output_kb_clean_v34e.json"
    didactic_out = out_dir / "output_didattico_v35c.json"
    test_out = out_dir / "output_test_v35d.json"
    final_selected = out_dir / "output_selezionato_v35f.json"
    bridge_report = out_dir / "bridge_report_v35f.json"

    execution = {
        "ok": False,
        "tipo": tipo,
        "passaggi": [],
        "errori": [],
        "output_file": str(final_selected.relative_to(ROOT)),
    }

    if not base_v34e.exists():
        execution["errori"].append(f"manca output base V3.4E: {base_v34e}")
        return execution

    if "orchestratore_v35e" in decision["motori"]:
        code, log = run([
            "python3",
            "scripts/rag_orchestratore_riutilizzabile_v35e.py",
            "--docs",
            documento,
            "--skip-precheck",
        ])

        execution["passaggi"].append({
            "motore": "orchestratore_v35e",
            "ok": code == 0,
        })

        if code != 0:
            execution["errori"].append(log)
            return execution

        final_v35e = ROOT / "dist/generated/rag_output_finale_orchestrato_v35e" / documento / "rag_output_finale_v35e.json"

        if not final_v35e.exists():
            execution["errori"].append(f"output finale V3.5E mancante: {final_v35e}")
            return execution

        data = read_json(final_v35e)
        selected = select_fields(data, outputs)
        selected["piano_motori_v35f"] = plan
        write_json(final_selected, selected)

        execution["ok"] = True
        return execution

    code, log = run([
        "python3",
        "scripts/rag_motore_didattico_riutilizzabile_v35c.py",
        "--input",
        str(base_v34e),
        "--output",
        str(didactic_out),
    ])

    execution["passaggi"].append({
        "motore": "didattico_v35c",
        "ok": code == 0,
    })

    if code != 0:
        execution["errori"].append(log)
        return execution

    source_for_selection = didactic_out

    if "test_v35d" in decision["motori"]:
        code, log = run([
            "python3",
            "scripts/rag_motore_test_riutilizzabile_v35d.py",
            "--input",
            str(didactic_out),
            "--output",
            str(test_out),
        ])

        execution["passaggi"].append({
            "motore": "test_v35d",
            "ok": code == 0,
        })

        if code != 0:
            execution["errori"].append(log)
            return execution

        code, log = run([
            "python3",
            "scripts/rag_bridge_motori_qualita_esistenti_v35b.py",
            "--input",
            str(test_out),
            "--output-report-json",
            str(bridge_report),
        ])

        execution["passaggi"].append({
            "motore": "bridge_quiz_v35b",
            "ok": code == 0,
        })

        if code != 0:
            execution["errori"].append(log)
            return execution

        source_for_selection = test_out

    data = read_json(source_for_selection)
    selected = select_fields(data, outputs)
    selected["piano_motori_v35f"] = plan
    write_json(final_selected, selected)

    execution["ok"] = True
    return execution


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--compito", required=True)
    parser.add_argument("--documento", default="sicurezza_reale")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--plan-json", default="")
    args = parser.parse_args()

    plan = build_plan(args.compito, args.documento)

    if args.execute:
        plan["esecuzione"] = execute_plan(plan)

    plan_path = Path(args.plan_json) if args.plan_json else BASE_SELECTOR / "plans" / f"{slug(args.compito)}_{args.documento}.json"
    write_json(plan_path, plan)

    print("=== RAG SELEZIONATORE MOTORI RIUTILIZZABILE V3.5F ===")
    print("Compito:", args.compito)
    print("Documento:", args.documento)
    print("Tipo:", plan["decisione"]["tipo"])
    print("Output richiesti:", ", ".join(plan["decisione"]["output_richiesti"]))
    print("Motori:")
    for motor in plan["motori_da_usare"]:
        print("-", motor["id"], "->", motor["script"])

    print("Piano JSON:", plan_path.relative_to(ROOT))

    if args.execute:
        execution = plan["esecuzione"]
        print("Esecuzione OK:", execution["ok"])
        print("Output:", execution["output_file"])
        if execution["errori"]:
            print("ERRORI:")
            for e in execution["errori"]:
                print("-", e)

        return 0 if execution["ok"] else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
