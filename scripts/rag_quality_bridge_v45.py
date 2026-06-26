#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RAG Quality Bridge V4.5

Scopo:
- NON reinventare i motori qualità;
- cercare i validatori già presenti nel progetto;
- provare a richiamarli su un quiz JSON generato dal RAG;
- creare un report chiaro: trovato / mancante / passato / fallito.

Questo file è un ponte. Non sostituisce:
- validate_questions.py
- rag_valida_quiz_json.py
- rag_valida_distrattori_forti.py
- validatore_core_database.py
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional


VALIDATOR_REGISTRY = [
    {
        "name": "rag_valida_quiz_json",
        "path": "scripts/rag_valida_quiz_json.py",
        "purpose": "Validazione struttura quiz RAG JSON",
    },
    {
        "name": "rag_valida_distrattori_forti",
        "path": "scripts/rag_valida_distrattori_forti.py",
        "purpose": "Controllo qualità distrattori forti RAG",
    },
    {
        "name": "validate_questions",
        "path": "scripts/validate_questions.py",
        "purpose": "Validatore domande già esistente",
    },
    {
        "name": "validatore_core_database",
        "path": "scripts/validatore_core_database.py",
        "purpose": "Validatore core database quiz",
    },
]


COMMAND_PATTERNS = [
    ["{python}", "{script}", "{quiz}"],
    ["{python}", "{script}", "--input", "{quiz}"],
    ["{python}", "{script}", "--file", "{quiz}"],
    ["{python}", "{script}", "--json", "{quiz}"],
    ["{python}", "{script}", "--quiz", "{quiz}"],
]


QUIZ_CANDIDATE_NAMES = [
    "quiz_validato.json",
    "quiz_generato.json",
    "rag_quiz_bridge_v43.json",
    "database_quiz.json",
]


def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def find_project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def find_quiz_candidate(output_dir: Path) -> Optional[Path]:
    for name in QUIZ_CANDIDATE_NAMES:
        candidate = output_dir / name
        if candidate.exists():
            return candidate

    json_files = sorted(output_dir.glob("*.json"))
    for candidate in json_files:
        if candidate.name not in {"manifest.json", "report_qualita.json", "pipeline_report.json"}:
            return candidate

    return None


def render_command(pattern: List[str], script_path: Path, quiz_path: Path) -> List[str]:
    return [
        token.format(
            python=sys.executable,
            script=str(script_path),
            quiz=str(quiz_path),
        )
        for token in pattern
    ]


def run_validator(
    root: Path,
    validator: Dict[str, str],
    quiz_path: Path,
    timeout: int = 20,
) -> Dict[str, Any]:
    script_path = root / validator["path"]

    result: Dict[str, Any] = {
        "name": validator["name"],
        "path": validator["path"],
        "purpose": validator["purpose"],
        "exists": script_path.exists(),
        "status": "missing",
        "attempts": [],
    }

    if not script_path.exists():
        result["message"] = "Validatore non trovato: non viene inventato nulla."
        return result

    for pattern in COMMAND_PATTERNS:
        command = render_command(pattern, script_path=script_path, quiz_path=quiz_path)

        attempt: Dict[str, Any] = {
            "command": command,
            "returncode": None,
            "stdout_tail": "",
            "stderr_tail": "",
        }

        try:
            completed = subprocess.run(
                command,
                cwd=str(root),
                text=True,
                capture_output=True,
                timeout=timeout,
            )

            attempt["returncode"] = completed.returncode
            attempt["stdout_tail"] = completed.stdout[-2500:]
            attempt["stderr_tail"] = completed.stderr[-2500:]
            result["attempts"].append(attempt)

            if completed.returncode == 0:
                result["status"] = "passed"
                result["message"] = "Validatore eseguito con successo."
                return result

        except subprocess.TimeoutExpired as exc:
            attempt["returncode"] = "timeout"
            attempt["stdout_tail"] = (exc.stdout or "")[-2500:] if isinstance(exc.stdout, str) else ""
            attempt["stderr_tail"] = (exc.stderr or "")[-2500:] if isinstance(exc.stderr, str) else ""
            result["attempts"].append(attempt)

        except Exception as exc:
            attempt["returncode"] = "exception"
            attempt["stderr_tail"] = str(exc)
            result["attempts"].append(attempt)

    result["status"] = "failed"
    result["message"] = (
        "Validatore trovato ma non ha approvato il file oppure usa una CLI diversa. "
        "Il bridge lo segnala invece di aggirarlo."
    )
    return result


def write_markdown_report(report: Dict[str, Any], md_path: Path) -> None:
    lines: List[str] = []
    lines.append("# Report qualità RAG V4.5")
    lines.append("")
    lines.append(f"- Stato: **{report['status']}**")
    lines.append(f"- Creato: `{report['created_at']}`")
    lines.append(f"- Quiz analizzato: `{report.get('quiz_file') or 'nessun quiz trovato'}`")
    lines.append("")

    lines.append("## Regola V4.5")
    lines.append("")
    lines.append(
        "Il RAG non decide la qualità da solo. "
        "Il RAG passa dai validatori già presenti nel progetto."
    )
    lines.append("")

    lines.append("## Validatori")
    lines.append("")

    for item in report.get("validators", []):
        lines.append(f"### {item['name']}")
        lines.append("")
        lines.append(f"- Scopo: {item['purpose']}")
        lines.append(f"- File: `{item['path']}`")
        lines.append(f"- Esiste: `{item['exists']}`")
        lines.append(f"- Stato: **{item['status']}**")
        lines.append(f"- Messaggio: {item.get('message', '')}")
        lines.append("")

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def validate_quiz(
    output_dir: str | Path,
    quiz_file: str | Path | None = None,
    strict: bool = False,
) -> Dict[str, Any]:
    root = find_project_root()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if quiz_file:
        quiz_path = Path(quiz_file)
    else:
        quiz_path = find_quiz_candidate(out_dir)

    report: Dict[str, Any] = {
        "version": "V4.5",
        "module": "rag_quality_bridge_v45",
        "created_at": now_iso(),
        "output_dir": str(out_dir),
        "quiz_file": str(quiz_path) if quiz_path else None,
        "strict": strict,
        "status": "no_quiz_to_validate",
        "validators": [],
        "summary": {
            "found": 0,
            "missing": 0,
            "passed": 0,
            "failed": 0,
        },
    }

    if not quiz_path or not quiz_path.exists():
        report["message"] = (
            "Nessun quiz JSON trovato. Il bridge qualità è pronto, "
            "ma non valida output inesistenti."
        )
    else:
        for validator in VALIDATOR_REGISTRY:
            item = run_validator(root=root, validator=validator, quiz_path=quiz_path)
            report["validators"].append(item)

        for item in report["validators"]:
            if item["exists"]:
                report["summary"]["found"] += 1
            else:
                report["summary"]["missing"] += 1

            if item["status"] == "passed":
                report["summary"]["passed"] += 1
            elif item["status"] == "failed":
                report["summary"]["failed"] += 1

        if report["summary"]["found"] == 0:
            report["status"] = "no_validators_found"
            report["message"] = "Nessun validatore qualità esistente trovato."
        elif report["summary"]["failed"] > 0:
            report["status"] = "validation_failed"
            report["message"] = "Uno o più validatori esistenti non hanno approvato il quiz."
        elif report["summary"]["passed"] > 0:
            report["status"] = "passed"
            report["message"] = "Il quiz è passato attraverso almeno un validatore esistente."
        else:
            report["status"] = "validators_present_but_not_executed"
            report["message"] = "Validatori trovati, ma nessuno è stato eseguito con successo."

    json_path = out_dir / "report_qualita.json"
    md_path = out_dir / "report_qualita.md"

    json_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_markdown_report(report, md_path)

    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description="RAG Quality Bridge V4.5 - usa i validatori già esistenti."
    )
    parser.add_argument("--output", required=True, help="Cartella output RAG.")
    parser.add_argument("--quiz", default=None, help="Quiz JSON da validare.")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero se validazione fallisce.")
    args = parser.parse_args()

    report = validate_quiz(
        output_dir=args.output,
        quiz_file=args.quiz,
        strict=args.strict,
    )

    print("✅ RAG Quality Bridge V4.5 completato")
    print(f"📊 Stato: {report['status']}")
    print(f"📁 Report: {Path(args.output) / 'report_qualita.json'}")

    if args.strict and report["status"] in {
        "validation_failed",
        "no_validators_found",
        "validators_present_but_not_executed",
    }:
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
