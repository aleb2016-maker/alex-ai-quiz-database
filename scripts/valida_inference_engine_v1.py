from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List


class InferenceEngineV1Validator:
    """
    Validatore Inference Engine V1.

    Controlla:
    - file output presenti;
    - manifest coerente;
    - generazioni presenti;
    - nessuna generazione completamente vuota;
    - step di predizione presenti;
    - token speciali bloccati non presenti nel testo generato.
    """

    BLOCKED_TOKENS = {"<PAD>", "<BOS>", "<UNK>"}

    def validate(self, root: Path) -> List[str]:
        errors: List[str] = []

        inference_dir = root / "mini_llm" / "data" / "inference_v1"
        report_dir = root / "mini_llm" / "reports"

        outputs_path = inference_dir / "inference_engine_v1_outputs.json"
        manifest_path = inference_dir / "inference_engine_v1_manifest.json"
        report_path = report_dir / "inference_engine_v1_report.md"

        for path in [outputs_path, manifest_path, report_path]:
            if not path.exists():
                errors.append(f"File mancante: {path}")

        if errors:
            return errors

        outputs = json.loads(outputs_path.read_text(encoding="utf-8"))
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

        self._validate_manifest(manifest, outputs, errors)
        self._validate_outputs(outputs, errors)

        return errors

    def _validate_manifest(self, manifest: Dict, outputs: List[Dict], errors: List[str]) -> None:
        if manifest.get("versione") != "inference_engine_v1":
            errors.append("Versione manifest errata.")

        if manifest.get("status") != "generated":
            errors.append("Status inferenza non generated.")

        model = manifest.get("model", {})

        if model.get("vocab_size", 0) < 50:
            errors.append("Vocab size troppo piccolo nel manifest inferenza.")

        if model.get("vector_dim", 0) < 16:
            errors.append("Vector dim troppo piccola nel manifest inferenza.")

        generation = manifest.get("generation", {})

        if generation.get("max_new_tokens", 0) <= 0:
            errors.append("max_new_tokens non valido.")

        if generation.get("top_k", 0) <= 0:
            errors.append("top_k non valido.")

        summary = manifest.get("summary", {})

        if summary.get("total_generations") != len(outputs):
            errors.append("Conteggio total_generations incoerente.")

        if summary.get("non_empty_generations", 0) <= 0:
            errors.append("Nessuna generazione non vuota.")

    def _validate_outputs(self, outputs: List[Dict], errors: List[str]) -> None:
        if len(outputs) < 3:
            errors.append(f"Poche inferenze generate: {len(outputs)}")

        for index, item in enumerate(outputs):
            prompt = item.get("prompt", "")
            generated_text = item.get("generated_text", "")
            generated_tokens = item.get("generated_tokens", [])
            steps = item.get("steps", [])

            if not prompt:
                errors.append(f"Inferenza {index}: prompt vuoto.")

            if not generated_text.strip():
                errors.append(f"Inferenza {index}: testo generato vuoto.")

            if not generated_tokens:
                errors.append(f"Inferenza {index}: generated_tokens vuoto.")

            if not steps:
                errors.append(f"Inferenza {index}: steps vuoti.")

            for token in generated_tokens:
                if token in self.BLOCKED_TOKENS:
                    errors.append(f"Inferenza {index}: token bloccato generato: {token}")

            for step in steps:
                if not step.get("top_candidates"):
                    errors.append(f"Inferenza {index}: step senza top_candidates.")


def build_report(errors: List[str], root: Path) -> str:
    status = "OK" if not errors else "ERRORE"
    error_block = "Nessun errore rilevato." if not errors else "\n".join(f"- {error}" for error in errors)

    return f"""# Validazione Inference Engine V1

## Stato
{status}

## Root progetto
{root}

## Errori
{error_block}
"""


def main() -> None:
    root = Path.cwd()
    report_path = root / "mini_llm" / "reports" / "validazione_inference_engine_v1.md"

    validator = InferenceEngineV1Validator()
    errors = validator.validate(root)

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(build_report(errors, root), encoding="utf-8")

    if errors:
        print("ERRORE - Validazione Inference Engine V1 fallita")
        print(f"Report: {report_path}")

        for error in errors:
            print("-", error)

        raise SystemExit(1)

    print("OK - Validazione Inference Engine V1 superata")
    print(f"Report: {report_path}")


if __name__ == "__main__":
    main()
