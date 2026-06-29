#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

COMPAT_DOC = "sicurezza_reale"

PATHS = {
    "kb_v34b": ROOT / "dist/generated/rag_knowledge_base_v34b/knowledge_base.json",
    "kb_clean_v34d": ROOT / f"dist/generated/rag_quality_gate_kb_v34d/{COMPAT_DOC}/knowledge_base_clean_v34d.json",
    "out_v34e_dir": ROOT / f"dist/generated/rag_output_kb_clean_v34e/outputs/{COMPAT_DOC}",
    "out_v34e": ROOT / f"dist/generated/rag_output_kb_clean_v34e/outputs/{COMPAT_DOC}/rag_output_kb_clean_v34e.json",
    "bridge_v35b": ROOT / f"dist/generated/rag_bridge_motori_qualita_esistenti_v35b/{COMPAT_DOC}/bridge_report.json",
    "didactic_v35c": ROOT / f"dist/generated/rag_output_didattico_riutilizzabile_v35c/{COMPAT_DOC}/rag_output_didactic_v35c.json",
    "test_v35d": ROOT / f"dist/generated/rag_output_test_riutilizzabile_v35d/{COMPAT_DOC}/rag_output_test_v35d.json",
    "plan_v35f": ROOT / "dist/generated/rag_selezionatore_motori_v35f/plans/pipeline_unica_ufficiale.json",
    "selected_v35f": ROOT / f"dist/generated/rag_selezionatore_motori_v35f/output_completo/{COMPAT_DOC}/output_selezionato_v35f.json",
    "quality_v35g": ROOT / f"dist/generated/rag_output_revisionato_qualita_v35g/output_completo/{COMPAT_DOC}/output_revisionato_qualita_v35g.json",
    "natural_v35i": ROOT / f"dist/generated/rag_output_naturalezza_antikeyword_v35i/output_completo/{COMPAT_DOC}/output_naturalezza_antikeyword_v35i.json",
    "accord_v35j": ROOT / f"dist/generated/rag_output_accordo_pronomi_v35j/output_completo/{COMPAT_DOC}/output_accordo_pronomi_v35j.json",
    "clean_v35k": ROOT / f"dist/generated/rag_output_cleaner_finale_v35k/output_completo/{COMPAT_DOC}/output_cleaner_finale_v35k.json",
}

PIPELINE = [
    "rag_build_knowledge_base_v34b.py",
    "rag_quality_gate_kb_v34d.py",
    "rag_genera_output_da_kb_clean_v34e.py",
    "rag_bridge_motori_qualita_esistenti_v35b.py",
    "rag_motore_didattico_riutilizzabile_v35c.py",
    "rag_motore_test_riutilizzabile_v35d.py",
    "rag_orchestratore_riutilizzabile_v35e.py",
    "rag_selezionatore_motori_riutilizzabile_v35f.py",
    "rag_revisore_qualita_testuale_v35g.py",
    "rag_revisore_naturalezza_antikeyword_v35i.py",
    "rag_revisore_accordo_pronomi_v35j.py",
    "applica_v35k_universale.py",
    "rag_micro_rifinitura_universale_v35l.py",
]


def slugify(value: str) -> str:
    text = str(value or "").lower()
    text = text.replace("à", "a").replace("è", "e").replace("é", "e")
    text = text.replace("ì", "i").replace("ò", "o").replace("ù", "u")
    text = re.sub(r"[^a-z0-9]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text[:80] or "documento"


def run(command: list[str], allow_fail: bool = False) -> tuple[int, str]:
    result = subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    output = (result.stdout or "") + (result.stderr or "")

    print("")
    print("=== " + " ".join(command[1:]) + " ===")
    print(output[-4000:])

    if result.returncode != 0 and not allow_fail:
        raise SystemExit(f"ERRORE: comando fallito: {' '.join(command)}")

    return result.returncode, output


def command_for(script_name: str, input_file: Path) -> tuple[list[str], bool]:
    script = f"scripts/{script_name}"

    if script_name == "rag_build_knowledge_base_v34b.py":
        return [
            sys.executable, script,
            "--input", str(input_file),
            "--output", str(PATHS["kb_v34b"]),
        ], False

    if script_name == "rag_quality_gate_kb_v34d.py":
        return [
            sys.executable, script,
            "--kb", str(PATHS["kb_v34b"]),
            "--output", str(PATHS["kb_clean_v34d"]),
        ], False

    if script_name == "rag_genera_output_da_kb_clean_v34e.py":
        return [
            sys.executable, script,
            "--kb", str(PATHS["kb_clean_v34d"]),
            "--outdir", str(PATHS["out_v34e_dir"]),
            "--numero", "5",
        ], False

    if script_name == "rag_bridge_motori_qualita_esistenti_v35b.py":
        return [
            sys.executable, script,
            "--input", str(PATHS["out_v34e"]),
            "--output-report-json", str(PATHS["bridge_v35b"]),
        ], False

    if script_name == "rag_motore_didattico_riutilizzabile_v35c.py":
        return [
            sys.executable, script,
            "--input", str(PATHS["out_v34e"]),
            "--output", str(PATHS["didactic_v35c"]),
        ], False

    if script_name == "rag_motore_test_riutilizzabile_v35d.py":
        return [
            sys.executable, script,
            "--input", str(PATHS["didactic_v35c"]),
            "--output", str(PATHS["test_v35d"]),
        ], False

    if script_name == "rag_orchestratore_riutilizzabile_v35e.py":
        return [sys.executable, script], False

    if script_name == "rag_selezionatore_motori_riutilizzabile_v35f.py":
        return [
            sys.executable, script,
            "--compito", "prepara tutto il materiale completo per PDF app e pagina web",
            "--documento", COMPAT_DOC,
            "--execute",
            "--plan-json", str(PATHS["plan_v35f"]),
        ], False

    if script_name == "rag_revisore_qualita_testuale_v35g.py":
        return [
            sys.executable, script,
            "--input", str(PATHS["selected_v35f"]),
            "--output", str(PATHS["quality_v35g"]),
        ], False

    if script_name == "rag_revisore_naturalezza_antikeyword_v35i.py":
        return [
            sys.executable, script,
            "--input", str(PATHS["quality_v35g"]),
            "--raw-input", str(PATHS["selected_v35f"]),
            "--output", str(PATHS["natural_v35i"]),
        ], False

    if script_name == "rag_revisore_accordo_pronomi_v35j.py":
        return [
            sys.executable, script,
            "--input", str(PATHS["natural_v35i"]),
            "--output", str(PATHS["accord_v35j"]),
        ], True

    if script_name == "applica_v35k_universale.py":
        return [sys.executable, script], False

    if script_name == "rag_micro_rifinitura_universale_v35l.py":
        return [sys.executable, script], False

    raise SystemExit(f"ERRORE: script non gestito: {script_name}")


def validate_output(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise SystemExit(f"ERRORE: output finale mancante: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    required = ["riassunto", "card", "domande_studio", "test", "controlli_qualita"]
    missing = [key for key in required if key not in data]
    if missing:
        raise SystemExit(f"ERRORE: chiavi finali mancanti: {missing}")

    if not data.get("riassunto"):
        raise SystemExit("ERRORE: riassunto mancante")

    if len(data.get("card", [])) < 1:
        raise SystemExit("ERRORE: card mancanti")

    if len(data.get("domande_studio", [])) < 1:
        raise SystemExit("ERRORE: domande studio mancanti")

    if len(data.get("test", [])) < 1:
        raise SystemExit("ERRORE: test mancante")

    quality = data.get("controlli_qualita", {})
    if not quality.get("ok", False):
        raise SystemExit("ERRORE: controlli_qualita.ok non true")

    cleaner = quality.get("cleaner_finale_universale_v35k", {})
    if not cleaner.get("ok", False):
        raise SystemExit("ERRORE: cleaner_finale_universale_v35k non ok")

    return data


def write_report(
    report_path: Path,
    input_file: Path,
    final_output: Path,
    public_output: Path,
    data: dict[str, Any],
    logs: list[dict[str, Any]],
) -> None:
    failed_non_blocking = [
        item for item in logs
        if item["returncode"] != 0 and item["allow_fail"]
    ]

    lines = [
        "# RAG Pipeline Unica Ufficiale",
        "",
        f"- Creato il: {datetime.now().isoformat(timespec='seconds')}",
        f"- Input: `{input_file}`",
        f"- Output finale interno V35K: `{final_output.relative_to(ROOT)}`",
        f"- Output pubblico pacchetto unico: `{public_output.relative_to(ROOT)}`",
        "",
        "## Motori collegati automaticamente",
        "",
        *[f"- `{name}`" for name in PIPELINE],
        "",
        "## Esito finale",
        "",
        f"- Riassunto presente: {bool(data.get('riassunto'))}",
        f"- Card: {len(data.get('card', []))}",
        f"- Domande studio: {len(data.get('domande_studio', []))}",
        f"- Test: {len(data.get('test', []))}",
        f"- Quality OK: {data.get('controlli_qualita', {}).get('ok')}",
        f"- Cleaner V35K OK: {data.get('controlli_qualita', {}).get('cleaner_finale_universale_v35k', {}).get('ok')}",
        "",
        "## Note architetturali",
        "",
        "- I motori restano separati solo internamente come moduli riutilizzabili.",
        "- L'uso ufficiale passa da un solo entrypoint.",
        "- Nessun collegamento manuale tra motori è richiesto all'utente.",
        "- Il lane interno `sicurezza_reale` resta solo compatibilità tecnica temporanea con la catena V35 già esistente.",
        "- L'output pubblico viene copiato nello spazio della pipeline unica con slug documento.",
        "",
    ]

    if failed_non_blocking:
        lines += [
            "## Controlli non bloccanti",
            "",
            *[
                f"- `{item['script']}` ha segnalato un controllo rigido, ma il cleaner finale V35K ha validato l'output."
                for item in failed_non_blocking
            ],
            "",
        ]

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="RAG Pipeline Unica Ufficiale")
    parser.add_argument("--input", required=True, help="Documento TXT/MD da elaborare")
    parser.add_argument("--slug", default="", help="Nome breve output")
    parser.add_argument(
        "--outdir",
        default="dist/generated/rag_pipeline_unica_ufficiale",
        help="Cartella output pubblico",
    )
    args = parser.parse_args()

    input_file = Path(args.input).expanduser()
    if not input_file.is_absolute():
        input_file = ROOT / input_file
    input_file = input_file.resolve()

    if not input_file.exists():
        raise SystemExit(f"ERRORE: input non trovato: {input_file}")

    slug = slugify(args.slug or input_file.stem)
    public_dir = ROOT / args.outdir / slug
    public_dir.mkdir(parents=True, exist_ok=True)

    logs: list[dict[str, Any]] = []

    print("=== RAG PIPELINE UNICA UFFICIALE ===")
    print(f"Input: {input_file}")
    print(f"Slug: {slug}")

    for script_name in PIPELINE:
        command, allow_fail = command_for(script_name, input_file)
        returncode, output = run(command, allow_fail=allow_fail)
        logs.append({
            "script": script_name,
            "returncode": returncode,
            "allow_fail": allow_fail,
        })

    data = validate_output(PATHS["clean_v35k"])

    public_output = public_dir / "output_finale_rag_pipeline_unica.json"
    shutil.copy2(PATHS["clean_v35k"], public_output)

    report = ROOT / "reports/rag_pipeline_unica_ufficiale.md"
    write_report(report, input_file, PATHS["clean_v35k"], public_output, data, logs)

    print("")
    print("OK: RAG Pipeline Unica Ufficiale completata")
    print(f"Output pubblico: {public_output.relative_to(ROOT)}")
    print(f"Report: {report.relative_to(ROOT)}")
    print(f"Riassunto: {bool(data.get('riassunto'))}")
    print(f"Card: {len(data.get('card', []))}")
    print(f"Domande studio: {len(data.get('domande_studio', []))}")
    print(f"Test: {len(data.get('test', []))}")
    print(f"Quality OK: {data.get('controlli_qualita', {}).get('ok')}")
    print(f"Cleaner V35K: {data.get('controlli_qualita', {}).get('cleaner_finale_universale_v35k', {}).get('ok')}")


if __name__ == "__main__":
    main()
