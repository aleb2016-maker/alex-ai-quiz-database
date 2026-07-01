from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class InferenceRawDiagnosticsV1Validator:
    """
    Questo validatore NON boccia il modello perché genera male.
    Boccia solo se la diagnostica non è realmente raw.

    Il modello deve poter fallire in modo visibile.
    """

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        output_dir = root / "mini_llm" / "data" / "diagnostics" / "inference_raw_diagnostics_v1"
        report_dir = root / "mini_llm" / "reports"

        outputs_path = output_dir / "inference_raw_diagnostics_v1_outputs.json"
        manifest_path = output_dir / "inference_raw_diagnostics_v1_manifest.json"
        report_path = report_dir / "inference_raw_diagnostics_v1_report.md"

        for path in [outputs_path, manifest_path, report_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        try:
            outputs = json.loads(outputs_path.read_text(encoding="utf-8"))
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"JSON non valido: {error}")
            return errors

        self._validate_manifest(manifest, outputs, errors)
        self._validate_outputs(outputs, errors)

        return errors

    def _validate_manifest(self, manifest: Dict, outputs: List[Dict], errors: List[str]) -> None:
        if manifest.get("versione") != "inference_raw_diagnostics_v1":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "diagnosed":
            errors.append("Status manifest non diagnosed.")

        settings = manifest.get("settings", {})

        required_false = [
            "fallback_enabled",
            "hardcoded_sentences_enabled",
            "sentence_bank_enabled",
            "anchor_retrieval_enabled",
            "filters_enabled",
        ]

        for key in required_false:
            if settings.get(key) is not False:
                errors.append(f"La diagnostica non è raw: {key} non è False.")

        if settings.get("generation_mode") != "raw_model_only":
            errors.append("generation_mode non è raw_model_only.")

        summary = manifest.get("summary", {})

        if summary.get("prompts_total") != len(outputs):
            errors.append("Conteggio prompt incoerente.")

        if not manifest.get("diagnostics"):
            errors.append("Diagnostica globale mancante.")

    def _validate_outputs(self, outputs: List[Dict], errors: List[str]) -> None:
        if not isinstance(outputs, list) or not outputs:
            errors.append("Output diagnostica vuoto.")
            return

        for index, item in enumerate(outputs, start=1):
            if item.get("generation_mode") != "raw_model_only":
                errors.append(f"Output {index}: generation_mode non raw.")

            if item.get("fallback_used") is not False:
                errors.append(f"Output {index}: fallback usato.")

            if item.get("hardcoded_sentence_used") is not False:
                errors.append(f"Output {index}: frase hardcoded usata.")

            if item.get("sentence_bank_used") is not False:
                errors.append(f"Output {index}: sentence bank usato.")

            if item.get("anchor_retrieval_used") is not False:
                errors.append(f"Output {index}: anchor retrieval usato.")

            if item.get("filters_used") is not False:
                errors.append(f"Output {index}: filtri usati.")

            if "generated_tokens_raw" not in item:
                errors.append(f"Output {index}: generated_tokens_raw mancante.")

            if "step_trace" not in item or not item["step_trace"]:
                errors.append(f"Output {index}: step_trace mancante.")

            if "diagnostics" not in item:
                errors.append(f"Output {index}: diagnostics mancante.")


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)
    return f"""# Validazione Inference Raw Diagnostics V1

## Stato
{status}

## Root progetto
{root}

## Regola
La validazione controlla solo che la diagnostica sia davvero raw.
Non giudica il modello come buono solo perché produce qualcosa.

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_inference_raw_diagnostics_v1.md"

    validator = InferenceRawDiagnosticsV1Validator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Inference Raw Diagnostics V1 fallita")
        print(f"Report: {report_path}")
        for error in errors[:100]:
            print("-", error)
        if len(errors) > 100:
            print(f"... altri errori: {len(errors) - 100}")
        raise SystemExit(1)

    print("OK - Validazione Inference Raw Diagnostics V1 superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
