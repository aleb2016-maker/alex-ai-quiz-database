#!/usr/bin/env python3
"""
Verifica RAG Selezionatore Motori Riutilizzabile V3.5F.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports/rag_selezionatore_motori_riutilizzabile_v35f.md"
BASE_SELECTOR = ROOT / "dist/generated/rag_selezionatore_motori_v35f"

CASES = [
    {
        "nome": "riassunto",
        "compito": "fammi solo un riassunto chiaro del documento",
        "tipo": "solo_riassunto",
        "must_include": ["didattico_v35c"],
        "must_not_include": ["test_v35d", "orchestratore_v35e"],
        "output_fields": ["riassunto"],
    },
    {
        "nome": "card",
        "compito": "crea card grafiche con fonti visibili",
        "tipo": "solo_card",
        "must_include": ["didattico_v35c"],
        "must_not_include": ["test_v35d", "orchestratore_v35e"],
        "output_fields": ["card"],
    },
    {
        "nome": "domande_studio",
        "compito": "genera domande studio naturali per ripassare",
        "tipo": "solo_domande_studio",
        "must_include": ["didattico_v35c"],
        "must_not_include": ["test_v35d", "orchestratore_v35e"],
        "output_fields": ["domande_studio"],
    },
    {
        "nome": "test",
        "compito": "genera un test interattivo con risposte multiple",
        "tipo": "solo_test",
        "must_include": ["bridge_quiz_v35b", "didattico_v35c", "test_v35d"],
        "must_not_include": ["orchestratore_v35e"],
        "output_fields": ["test"],
    },
    {
        "nome": "completo_pdf_app",
        "compito": "prepara tutto il materiale completo per PDF app e pagina web",
        "tipo": "output_completo",
        "must_include": ["orchestratore_v35e"],
        "must_not_include": [],
        "output_fields": ["riassunto", "card", "test", "domande_studio"],
    },
]


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True)
    return result.returncode, result.stdout + result.stderr


def normalizza(value: str) -> str:
    import re
    text = str(value or "").lower()
    text = text.replace("à", "a").replace("è", "e").replace("é", "e")
    text = text.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def slug(value: str) -> str:
    return normalizza(value).replace(" ", "_")[:80] or "compito"


def main() -> int:
    risultati = []
    errori = []

    code, log = run(["python3", "scripts/verifica_rag_orchestratore_riutilizzabile_v35e.py"])

    if code != 0:
        errori.append("precheck orchestratore V3.5E fallito")
        errori.append(log)
    else:
        risultati.append("OK: precheck orchestratore V3.5E")

    for case in CASES:
        plan_path = BASE_SELECTOR / "plans" / f"{slug(case['compito'])}_sicurezza_reale.json"

        code, log = run([
            "python3",
            "scripts/rag_selezionatore_motori_riutilizzabile_v35f.py",
            "--compito",
            case["compito"],
            "--documento",
            "sicurezza_reale",
            "--execute",
            "--plan-json",
            str(plan_path),
        ])

        if code != 0:
            errori.append(f"{case['nome']}: selezionatore fallito")
            errori.append(log)
            continue

        data = json.loads(plan_path.read_text(encoding="utf-8"))
        decision = data.get("decisione", {})
        motors = [m["id"] for m in data.get("motori_da_usare", [])]
        execution = data.get("esecuzione", {})

        if decision.get("tipo") != case["tipo"]:
            errori.append(f"{case['nome']}: tipo atteso {case['tipo']}, ottenuto {decision.get('tipo')}")

        for motor in case["must_include"]:
            if motor not in motors:
                errori.append(f"{case['nome']}: motore richiesto non selezionato {motor}")

        for motor in case["must_not_include"]:
            if motor in motors:
                errori.append(f"{case['nome']}: motore non necessario selezionato {motor}")

        if not execution.get("ok"):
            errori.append(f"{case['nome']}: esecuzione non OK")

        output_path = ROOT / execution.get("output_file", "")

        if not output_path.exists():
            errori.append(f"{case['nome']}: output selezionato mancante {output_path}")
            continue

        selected = json.loads(output_path.read_text(encoding="utf-8"))

        for field in case["output_fields"]:
            if field not in selected:
                errori.append(f"{case['nome']}: campo output mancante {field}")

        if "piano_motori_v35f" not in selected:
            errori.append(f"{case['nome']}: piano motori non incorporato nell'output")

        if case["nome"] in ["riassunto", "card", "domande_studio"]:
            if "test" in selected:
                errori.append(f"{case['nome']}: test presente anche se non richiesto")

        if case["nome"] == "test":
            tests = selected.get("test", []) or []
            if not tests:
                errori.append("test: lista test vuota")
            else:
                first = tests[0]
                for field in ["opzioni", "opzioni_visibili", "risposta_corretta", "risposta_corretta_visibile", "mappa_opzioni_v35d"]:
                    if field not in first:
                        errori.append(f"test: campo test mancante {field}")

        risultati.append(f"OK: selezione motori corretta per {case['nome']}")

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        "# Report RAG Selezionatore Motori Riutilizzabile V3.5F",
        "",
        "Verifica del selezionatore intelligente dei motori RAG.",
        "",
        "## Risultati",
    ]

    for r in risultati:
        lines.append(f"- {r}")

    lines.append("")
    lines.append(f"Errori totali: {len(errori)}")
    lines.append("")

    if errori:
        lines.append("## Errori")
        for e in errori:
            lines.append(f"- {e}")
        lines.append("")
        lines.append("ESITO: DA CORREGGERE")
    else:
        lines.append("ESITO: OK")

    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("=== VERIFICA RAG SELEZIONATORE MOTORI RIUTILIZZABILE V3.5F ===")
    for r in risultati:
        print(r)

    print("")
    print("Errori totali:", len(errori))
    print("Report:", REPORT.relative_to(ROOT))
    print("ESITO:", "OK" if not errori else "DA CORREGGERE")

    return 0 if not errori else 1


if __name__ == "__main__":
    raise SystemExit(main())
