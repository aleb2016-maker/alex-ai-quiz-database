from __future__ import annotations

import json
from pathlib import Path
from typing import List


class ModelQualityGateV1InstallerValidator:
    """
    Validatore tecnico del gate stesso.
    Non certifica che il modello è buono.
    Certifica solo che il gate è stato installato e ha prodotto un risultato leggibile.
    """

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        script_path = root / "mini_llm" / "python" / "quality" / "model_quality_gate_v1.py"
        runner_path = root / "scripts" / "valida_model_quality_gate_v1.py"
        output_dir = root / "mini_llm" / "data" / "quality" / "model_quality_gate_v1"
        results_path = output_dir / "model_quality_gate_v1_results.json"
        manifest_path = output_dir / "model_quality_gate_v1_manifest.json"
        report_path = root / "mini_llm" / "reports" / "model_quality_gate_v1_report.md"

        for path in [script_path, runner_path]:
            if not path.exists():
                errors.append(f"File installazione mancante: {path}")

        for path in [results_path, manifest_path, report_path]:
            if not path.exists():
                errors.append(f"File output gate mancante: {path}")

        if errors:
            return errors

        try:
            results = json.loads(results_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"Risultati gate JSON non validi: {error}")
            return errors

        if results.get("versione") != "model_quality_gate_v1":
            errors.append("Versione gate errata.")

        if results.get("status") not in {"passed", "failed"}:
            errors.append("Status gate non valido.")

        rules = results.get("rules", {})

        if rules.get("forbid_fallback") is not True:
            errors.append("Regola forbid_fallback non attiva.")

        if rules.get("forbid_hardcoded") is not True:
            errors.append("Regola forbid_hardcoded non attiva.")

        if rules.get("forbid_sentence_bank") is not True:
            errors.append("Regola forbid_sentence_bank non attiva.")

        if rules.get("forbid_anchor_retrieval") is not True:
            errors.append("Regola forbid_anchor_retrieval non attiva.")

        if rules.get("require_domain") is not True:
            errors.append("Regola require_domain non attiva.")

        if not rules.get("forbid_special_tokens"):
            errors.append("Regola token speciali vietati mancante.")

        if "summary" not in results or "checks" not in results:
            errors.append("Risultati gate incompleti.")

        return errors


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione installazione Model Quality Gate V1

## Stato
{status}

## Root progetto
{root}

## Nota
Questa validazione controlla il gate, non promuove il modello.
Il gate può fallire sul modello ed essere comunque installato correttamente.

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_model_quality_gate_v1.md"

    validator = ModelQualityGateV1InstallerValidator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione installazione Model Quality Gate V1 fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione installazione Model Quality Gate V1 superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
